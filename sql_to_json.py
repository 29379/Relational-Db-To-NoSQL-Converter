import psycopg2
import json

def get_schema_details(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)
    schema_details = {}
    for row in cursor.fetchall():
        table_name, column_name, data_type = row
        if table_name not in schema_details:
            schema_details[table_name] = []
        schema_details[table_name].append({
            'column_name': column_name,
            'data_type': data_type
        })

     # Fetch foreign key constraints
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
        WHERE tc.constraint_type = 'FOREIGN KEY';
    """)

    for row in cursor.fetchall():
        table_name, column_name, foreign_table_name, foreign_column_name = row
        schema_details[table_name].append({
            'column_name': column_name,
            'data_type': 'FOREIGN KEY',
            'foreign_table': foreign_table_name,
            'foreign_column': foreign_column_name
        })

    return schema_details

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname='czy_dojade',
        user='postgres',
        password='asdlkj000',
        host='localhost',
        port='5432'
    )

    # Get schema details
    schema_details = get_schema_details(conn)

    # Save schema details to JSON
    save_to_json(schema_details, 'schema_details.json')

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
