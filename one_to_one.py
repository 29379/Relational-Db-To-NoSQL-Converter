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


def create_db(cursor, db, schema):
    # populate with data
    for collection_name, columns_info in schema.items():
        collection = db[collection_name]
        column_names = [col["column_name"] for col in columns_info]
        data_from_pg = fetch_data_from_postgres(cursor, collection_name, column_names)

        for row in data_from_pg:
            document = {
                col["column_name"]: convert_to_compatible_types(row[idx])
                for idx, col in enumerate(columns_info)
            }
            document["_id"] = ObjectId()
            collection.insert_one(document)


def verify_and_clean_foreign_keys(db, schema):
    suffixes = ["id", "_id"]

    for collection_name, fields in schema.items():
        collection = db[collection_name]
        foreign_keys = [
            field["column_name"]
            for field in fields
            if "FOREIGN KEY" in field["constraints"]
        ]

        for document in collection.find():
            updates = {}
            for key in foreign_keys:
                if key in document:

                    ref_collection_names = [
                        key.rstrip(suffix).lower() for suffix in suffixes
                    ]

                    if not any(
                        ref_collection_name in schema
                        for ref_collection_name in ref_collection_names
                    ):
                        updates[key] = ""

            if updates:
                collection.update_one({"_id": document["_id"]}, {"$unset": updates})


def handle_relationships(db, relationships, rel_choice):
    # relationships between collections
    for relation in relationships:
        from_collection = db[relation["from"]]
        to_collection = db[relation["to"]]
        column_key = relation.get("column", relation.get("foreign_key"))

        for document in from_collection.find():
            related_document_id = None
            for key in [
                relation["to"] + "id",
                relation["to"] + "_id",
                relation["to"] + "_ID",
                relation["to"].title() + "id",
                relation["to"].title() + "_id",
                relation["to"].title() + "_ID",
                relation["to"].capitalize() + "_ID",
                relation["to"].capitalize() + "_ID",
                relation["to"].capitalize() + "_ID",
            ]:
                if key in document:
                    related_document_id = document[key]
                    break

            if related_document_id:
                # using the object itself
                related_document = to_collection.find_one({"id": related_document_id})
                if related_document:
                    if rel_choice == "ReferencingType.id":
                        related_document = ObjectId(related_document["_id"])
                    from_collection.update_one(
                        {"_id": document["_id"]},
                        {"$set": {column_key: related_document}},
                    )


def one_to_one(conn, db, rel_choice):
    cursor = conn.cursor()
    with open("resources/schema_details.json", "r") as file:
        schema = json.load(file)
        relationships = schema.pop("relationships", [])

    create_db(cursor, db, schema)
    verify_and_clean_foreign_keys(db, schema)
    handle_relationships(db, relationships, rel_choice)
    cursor.close()
