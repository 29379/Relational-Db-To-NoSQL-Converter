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


def handle_relationships(db, relationships):
    # relationships between collections
    for relation in relationships:
        from_collection = db[relation["from"]]
        to_collection = db[relation["to"]]
        column_key = relation.get("column", relation.get("foreign_key"))

        for document in from_collection.find():
            related_document_id = None
            for key in [relation["to"] + "id", relation["to"] + "_id"]:
                if key in document:
                    related_document_id = document[key]
                    break

            if related_document_id:
                related_document = to_collection.find_one({"id": related_document_id})
                if related_document:
                    from_collection.update_one(
                        {"_id": document["_id"]},
                        {"$set": {column_key: related_document}},
                    )


def handle_many_to_many_relations(db, relationships):
    for relation in relationships:
        if relation["type"] == "many-to-many":
            junction_collection = db[relation["junction_table"]]
            from_collection = db[relation["from"]]
            to_collection = db[relation["to"]]

            junction_records = junction_collection.find()

            for record in junction_records:
                from_id = record[relation["column"]]
                to_id = record[relation["foreign_key_to"]]

                to_document = to_collection.find_one({"id": from_id})

                if to_document:
                    embedded_to_document = {
                        k: v for k, v in to_document.items() if k != "_id"
                    }

                    from_collection.update_one(
                        {"id": to_id},
                        {"$addToSet": {relation["to"]: embedded_to_document}},
                        upsert=True,
                    )

                    from_document = from_collection.find_one({"id": to_id})

                    if from_document:
                        embedded_from_document = {
                            k: v for k, v in from_document.items() if k != "_id"
                        }

                        to_collection.update_one(
                            {"id": from_id},
                            {"$addToSet": {relation["from"]: embedded_from_document}},
                            upsert=True,
                        )


def drop_junction_tables(db, relationships):
    for relation in relationships:
        if relation["type"] == "many-to-many":
            db[relation["junction_table"]].drop()


def main():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["zbd_czy_dojade"]
    conn = psycopg2.connect(
        dbname="zbd_czy_dojade",
        user="postgres",
        password="123456",
        host="localhost",
        port="5432",
    )
    cursor = conn.cursor()

    with open("schema_details.json", "r") as file:
        schema = json.load(file)
        relationships = schema.pop("relationships", [])

    create_db(cursor, db, schema)
    handle_relationships(db, [r for r in relationships if r["type"] != "many-to-many"])
    handle_many_to_many_relations(db, relationships)
    drop_junction_tables(db, relationships)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
