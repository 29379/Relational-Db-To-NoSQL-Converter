import psycopg2
import json

def get_constraints(cursor):
    primary_keys = {}
    unique_keys = {}
    foreign_keys = {}

    cursor.execute("""
        SELECT kcu.table_name, kcu.column_name
        FROM information_schema.key_column_usage AS kcu
        JOIN information_schema.table_constraints AS tc
            ON kcu.table_schema = tc.table_schema
                AND kcu.table_name = tc.table_name
                AND kcu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
            AND kcu.table_schema = 'public'
    """)
    for table_name, column_name in cursor.fetchall():
        if table_name not in primary_keys:
            primary_keys[table_name] = []
        primary_keys[table_name].append(column_name)

    cursor.execute("""
        SELECT kcu.table_name, kcu.column_name
        FROM information_schema.key_column_usage AS kcu
        JOIN information_schema.table_constraints AS tc
            ON kcu.table_schema = tc.table_schema
                AND kcu.table_name = tc.table_name
                AND kcu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'UNIQUE'
            AND kcu.table_schema = 'public'
            AND kcu.column_name NOT IN (SELECT column_name FROM information_schema.key_column_usage WHERE table_schema = 'public' 
                AND constraint_name IN (SELECT constraint_name FROM information_schema.table_constraints WHERE constraint_type = 'PRIMARY KEY'))
    """)
    for table_name, column_name in cursor.fetchall():
        if table_name not in unique_keys:
            unique_keys[table_name] = []
        unique_keys[table_name].append(column_name)

    cursor.execute("""
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public';
    """)
    for row in cursor.fetchall():
        table_name, column_name, foreign_table_name, foreign_column_name = row
        if table_name not in foreign_keys:
            foreign_keys[table_name] = []
        foreign_keys[table_name].append({
            'column_name': column_name,
            'foreign_table_name': foreign_table_name,
            'foreign_column_name': foreign_column_name
        })

    return primary_keys, unique_keys, foreign_keys


def identify_junction_tables(foreign_keys, primary_keys, cursor):
    junction_tables = {}
    for table, fks in foreign_keys.items():
        linked_tables = set(fk['foreign_table_name'] for fk in fks)

        # ensure the table links to two or more distinct tables
        if len(linked_tables) > 1:
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
            """, (table,))
            all_columns = set(row[0] for row in cursor.fetchall())
            fk_columns = set(fk['column_name'] for fk in fks)
            primary_key_columns = set(primary_keys.get(table, []))

            # check if primary key columns include all foreign key columns
            if fk_columns <= primary_key_columns:
                junction_tables[table] = list(linked_tables)

    return junction_tables


def get_relationships(cursor, primary_keys, unique_keys, junction_tables):
    # relationships
    cursor.execute("""
        SELECT
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name, 
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
        FROM 
            information_schema.table_constraints AS tc
        JOIN 
            information_schema.key_column_usage AS kcu 
            ON tc.constraint_name = kcu.constraint_name
        JOIN 
            information_schema.constraint_column_usage AS ccu 
            ON ccu.constraint_name = tc.constraint_name
        WHERE 
            tc.constraint_type = 'FOREIGN KEY' AND 
            tc.table_schema = 'public'
    """)

    relationships = {}
    for table_name, column_name, foreign_table_name, foreign_column_name, constraint_name in cursor.fetchall():
        if column_name in unique_keys.get(table_name, []):
            relationship_type = 'one-to-one'
        elif table_name not in junction_tables:
            relationship_type = 'many-to-one'
        else:
            relationship_type = 'many-to-many'

        if table_name not in relationships:
            relationships[table_name] = []

        relationships[table_name].append({
            'column': column_name,
            'foreign_table': foreign_table_name,
            'foreign_column': foreign_column_name,
            'relationship_type': relationship_type
        })

    return relationships

    
def get_schema_details(connection):
    cursor = connection.cursor()

    primary_keys, unique_keys, foreign_keys = get_constraints(cursor)
    junction_tables = identify_junction_tables(foreign_keys, primary_keys, cursor)
    relationship_data = get_relationships(cursor, primary_keys, unique_keys, junction_tables)

    # get details about each tables columns
    cursor.execute("""
        SELECT c.table_name, c.column_name, c.data_type, 
               c.character_maximum_length,
               array_agg(tc.constraint_type) FILTER (WHERE tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')) AS constraint_types,
               c.ordinal_position
        FROM information_schema.columns c
        LEFT JOIN information_schema.key_column_usage AS kcu
            ON c.column_name = kcu.column_name
                AND c.table_name = kcu.table_name
        LEFT JOIN information_schema.table_constraints AS tc
            ON kcu.table_schema = tc.table_schema
                AND kcu.table_name = tc.table_name
                AND kcu.constraint_name = tc.constraint_name
        WHERE c.table_schema = 'public'
        GROUP BY c.table_name, c.column_name, c.data_type, c.character_maximum_length, c.ordinal_position
        ORDER BY c.table_name, c.ordinal_position;
    """)

    schema_details = {}

    # column details
    for row in cursor.fetchall():
        table_name, column_name, data_type, character_maximum_length, constraint_types, ordinal_position = row
        if constraint_types is None:
            constraint_types = []

        if table_name not in schema_details:
            schema_details[table_name] = []

        column_details = {
            'column_name': column_name,
            'data_type': data_type
        }

        if data_type == 'character varying' and character_maximum_length is not None:
            column_details['max_length'] = character_maximum_length

        if 'PRIMARY KEY' in constraint_types:
            column_details['constraint_type'] = 'PRIMARY KEY'
        elif 'UNIQUE' in constraint_types:
            column_details['constraint_type'] = 'UNIQUE'

        schema_details[table_name].append(column_details)
    
    # foreign keys
    for table_name in schema_details:
        for column in schema_details[table_name]:
            for fk in foreign_keys.get(table_name, []):
                if column['column_name'] == fk['column_name']:
                    column.update({
                        'foreign_table': fk['foreign_table_name'],
                        'foreign_column': fk['foreign_column_name'],
                        'constraint_type': 'FOREIGN KEY'
                    })

    # adding relations
    relationship_summary = []
    for table, rels in relationship_data.items():
        for rel in rels:
            relationship_detail = {
                'from': table,
                'to': rel['foreign_table'],
                'type': rel['relationship_type']
            }
            relationship_summary.append(relationship_detail)


    schema_details['relationships'] = relationship_summary

    cursor.close()
    return dict(schema_details)


def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    conn = psycopg2.connect(
        dbname='zbd_czy_dojade',
        user='postgres',
        password='123456',
        host='localhost',
        port='5432'
    )

    schema_details = get_schema_details(conn)
    save_to_json(schema_details, 'schema_details.json')
    conn.close()

if __name__ == "__main__":
    main()
