import datetime
import pymongo
import psycopg2
import json
from bson import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal

def fetch_data_from_postgres(cursor, table_name, columns):
    # fetch data from PostgreSQL
    sql = f"SELECT {', '.join(columns)} FROM {table_name}"
    cursor.execute(sql)
    return cursor.fetchall()

def convert_to_compatible_types(value):
    # convert data to MongoDB compatible type
    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return datetime.datetime(year=value.year, month=value.month, day=value.day)
    elif isinstance(value, datetime.time):
        return str(value)
    elif isinstance(value, Decimal):
        return Decimal128(value)
    return value

def create_db(cursor, db, schema, relationships):
    # populate with data
    for collection_name, columns_info in schema.items():
        collection = db[collection_name]
        column_names = [col["column_name"] for col in columns_info]
        data_from_pg = fetch_data_from_postgres(cursor, collection_name, column_names)

        for row in data_from_pg:
            document = {col["column_name"]: convert_to_compatible_types(row[idx]) for idx, col in enumerate(columns_info)}
            document = handle_relationships(collection_name, document, relationships, db)
            collection.insert_one(document)

def handle_relationships(collection_name, document, relationships, db):
    # relationships between collections
    for relation in relationships:
        if relation['from'] == collection_name:
            related_collection = relation['to']
            related_id_keys = [related_collection + 'id', related_collection + '_id']  # Check both keys
            for related_id_key in related_id_keys:
                if related_id_key in document:
                    # related document
                    related_document = db[related_collection].find_one({'id': document[related_id_key]})
                    if related_document:
                        # if found replace id with ObjectId or Object

                        # ObjectId
                        # document[related_id_key] = ObjectId(related_document['_id'])

                        # Object
                        document[related_collection] = related_document
                    else:
                        # if not found, delete id field
                        document.pop(related_id_key)
                    break 
    return document



def main():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["zbd_czy_dojade"]
    conn = psycopg2.connect(
        dbname='zbd_czy_dojade',
        user='postgres',
        password='123456',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()

    with open("schema_details.json", "r") as file:
        schema = json.load(file)
        relationships = schema.pop("relationships", [])

    create_db(cursor, db, schema, relationships)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
