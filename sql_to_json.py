import psycopg2
import json

def get_schema_details(connection):
    cursor = connection.cursor()

    # Fetch table details
    cursor.execute("""
        SELECT c.table_name, c.column_name, c.data_type, c.character_maximum_length,
            CASE WHEN EXISTS (
                    SELECT 1
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND kcu.table_name = c.table_name
                        AND kcu.column_name = c.column_name
            ) THEN 'PRIMARY KEY' END AS constraint_type
        FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        ORDER BY c.table_name, c.ordinal_position;
    """)

    schema_details = {}
    for row in cursor.fetchall():
        table_name, column_name, data_type, character_maximum_length, constraint_type = row
        if table_name not in schema_details:
            schema_details[table_name] = []

        column_details = {
            'column_name': column_name,
            'data_type': data_type
        }

        if data_type == 'character varying':
            column_details['max_length'] = character_maximum_length
            
            column_details['constraint_type'] = constraint_type
            
        schema_details[table_name].append(column_details)

     # Fetch foreign key constraints
    cursor.execute("""
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            fc.data_type AS foreign_column_data_type
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
            JOIN information_schema.columns AS fc
                ON ccu.column_name = fc.column_name
                    AND ccu.table_name = fc.table_name
                    AND ccu.table_schema = fc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY';
    """)

    for row in cursor.fetchall():
        table_name, column_name, foreign_table_name, foreign_column_name, foreign_column_data_type = row
        
        for column in schema_details[table_name]:  # If column found, update not to duplicate
            if column['column_name'] == column_name:
                column.update({
                    'constraint_type': 'FOREIGN KEY',
                    'foreign_table': foreign_table_name,
                    'foreign_column': foreign_column_name
                })
                break
        else:  # If column not found, add new
            schema_details[table_name].append({
                'column_name': column_name,
                'data_type': foreign_column_data_type,
                'constraint_type': 'FOREIGN KEY',
                'foreign_table': foreign_table_name,
                'foreign_column': foreign_column_name
            })

    return schema_details

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    conn = psycopg2.connect(
        dbname='zbd_czy_dojade',
        user='postgres',
        password='asdlkj000',
        host='localhost',
        port='5432'
    )

    schema_details = get_schema_details(conn)
    save_to_json(schema_details, 'schema_details.json')
    conn.close()

if __name__ == "__main__":
    main()
