import psycopg2
import json


def get_constraints(cursor):
    primary_keys = {}
    unique_keys = {}
    foreign_keys = {}

    cursor.execute(
        """
        SELECT kcu.table_name, kcu.column_name
        FROM information_schema.key_column_usage AS kcu
        JOIN information_schema.table_constraints AS tc
            ON kcu.table_schema = tc.table_schema
                AND kcu.table_name = tc.table_name
                AND kcu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
            AND kcu.table_schema = 'public'
    """
    )
    for table_name, column_name in cursor.fetchall():
        if table_name not in primary_keys:
            primary_keys[table_name] = []
        primary_keys[table_name].append(column_name)

    cursor.execute(
        """
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
    """
    )
    for table_name, column_name in cursor.fetchall():
        if table_name not in unique_keys:
            unique_keys[table_name] = []
        unique_keys[table_name].append(column_name)

    cursor.execute(
        """
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
    """
    )
    for row in cursor.fetchall():
        table_name, column_name, foreign_table_name, foreign_column_name = row
        if table_name not in foreign_keys:
            foreign_keys[table_name] = []
        foreign_keys[table_name].append(
            {
                "column_name": column_name,
                "foreign_table_name": foreign_table_name,
                "foreign_column_name": foreign_column_name,
            }
        )

    return primary_keys, unique_keys, foreign_keys


def identify_junction_tables(foreign_keys, primary_keys, cursor):
    junction_tables = {}
    for table, fks in foreign_keys.items():
        if len(fks) > 1:
            fk_columns = [
                fk for fk in fks if fk["column_name"] in primary_keys.get(table, [])
            ]
            if len(fk_columns) == len(fks):
                linked_tables = set(fk["foreign_table_name"] for fk in fks)
                junction_tables[table] = {
                    "linked_tables": list(linked_tables),
                    "fk_columns": fk_columns,
                }
    return junction_tables


def get_relationships(cursor, primary_keys, unique_keys, junction_tables):
    # relationships
    cursor.execute(
        """
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
    """
    )

    relationships = {}
    for (
        table_name,
        column_name,
        foreign_table_name,
        foreign_column_name,
        constraint_name,
    ) in cursor.fetchall():
        if table_name in junction_tables:
            for linked_table in junction_tables[table_name]["linked_tables"]:
                if linked_table != foreign_table_name:
                    foreign_key_info = next(
                        (
                            fk
                            for fk in junction_tables[table_name]["fk_columns"]
                            if fk["foreign_table_name"] == linked_table
                        ),
                        None,
                    )
                    relationships.setdefault(table_name, []).append(
                        {
                            "junction_table": table_name,
                            "from": table_name,
                            "to": linked_table,
                            "type": "many-to-many",
                            "column": (
                                foreign_key_info["column_name"]
                                if foreign_key_info
                                else "unknown"
                            ),
                            "foreign_key_to": (
                                foreign_key_info["foreign_column_name"]
                                if foreign_key_info
                                else "unknown"
                            ),
                        }
                    )
        else:
            if column_name in unique_keys.get(table_name, []):
                relationship_type = "one-to-one"
            else:
                relationship_type = "many-to-one"

            relationships.setdefault(table_name, []).append(
                {
                    "from": table_name,
                    "to": foreign_table_name,
                    "type": relationship_type,
                    "column": column_name,
                    "foreign_table": foreign_table_name,
                    "foreign_column": foreign_column_name,
                    "foreign_key": column_name,
                }
            )

    return relationships


def get_schema_details(connection):
    cursor = connection.cursor()

    primary_keys, unique_keys, foreign_keys = get_constraints(cursor)
    junction_tables = identify_junction_tables(foreign_keys, primary_keys, cursor)
    relationships = get_relationships(
        cursor, primary_keys, unique_keys, junction_tables
    )

    cursor.execute(
        """
        SELECT c.table_name, c.column_name, c.data_type, c.character_maximum_length,
               string_agg(tc.constraint_type, ',') FILTER (WHERE tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')) AS constraint_types,
               c.ordinal_position
        FROM information_schema.columns c
        LEFT JOIN information_schema.key_column_usage AS kcu ON c.column_name = kcu.column_name AND c.table_name = kcu.table_name
        LEFT JOIN information_schema.table_constraints AS tc ON kcu.table_schema = tc.table_schema AND kcu.table_name = tc.table_name AND kcu.constraint_name = tc.constraint_name
        WHERE c.table_schema = 'public'
        GROUP BY c.table_name, c.column_name, c.data_type, c.character_maximum_length, c.ordinal_position
        ORDER BY c.table_name, c.ordinal_position;
    """
    )

    schema_details = {}

    for row in cursor.fetchall():
        (
            table_name,
            column_name,
            data_type,
            character_maximum_length,
            constraint_types,
            ordinal_position,
        ) = row
        constraint_types_list = constraint_types.split(",") if constraint_types else []

        column_details = {
            "column_name": column_name,
            "data_type": data_type,
            "constraints": constraint_types_list,
        }

        if data_type == "character varying" and character_maximum_length:
            column_details["max_length"] = character_maximum_length

        schema_details.setdefault(table_name, []).append(column_details)

    for table_name in schema_details:
        for column in schema_details[table_name]:
            for fk in foreign_keys.get(table_name, []):
                if column["column_name"] == fk["column_name"]:
                    column["foreign_table"] = fk["foreign_table_name"]
                    column["foreign_column"] = fk["foreign_column_name"]
                    if "FOREIGN KEY" not in column["constraints"]:
                        column["constraints"].append("FOREIGN KEY")

    relationship_summary = [
        rel for rel_list in relationships.values() for rel in rel_list
    ]

    schema_details["relationships"] = relationship_summary

    cursor.close()
    return schema_details


def save_to_json(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)


def save_to_json(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)


def main():
    conn = psycopg2.connect(
        dbname='zbd_czy_dojade',
        user='postgres',
        password='asdlkj000',
        host='localhost',
        port='5432'
    )

#     schema_details = get_schema_details(conn)
#     save_to_json(schema_details, "resources/schema_details.json")
#     conn.close()


# if __name__ == "__main__":
#     main()


def sql_to_json(conn):
    schema_details = get_schema_details(conn)
    save_to_json(schema_details, "resources/schema_details.json")
