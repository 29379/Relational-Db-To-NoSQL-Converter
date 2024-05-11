import datetime
import pymongo
import psycopg2
import json
from bson import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal
import sys


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


def handle_relationships(db, relationships, rel_choice):
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
                    if rel_choice == "1":
                        related_document = ObjectId(related_document["_id"])
                    from_collection.update_one(
                        {"_id": document["_id"]},
                        {"$set": {column_key: related_document}},
                    )


def handle_many_to_many_relations(db, relationships):
    # group relationships by junction table
    relation_groups = {}
    for relation in relationships:
        if relation["type"] == "many-to-many":
            key = relation["junction_table"]
            if key not in relation_groups:
                relation_groups[key] = []
            relation_groups[key].append(relation)

    for junction, rels in relation_groups.items():
        if len(rels) == 2:
            from_collection = db[junction]
            to_collections = [rels[0]["to"], rels[1]["to"]]

            # user decides embedding direction
            choice = prompt_user_for_embedding_direction(junction, to_collections)

            junction_records = from_collection.find()

            for record in junction_records:
                embed_in = to_collections[choice - 1]
                other_index = 1 if choice - 1 == 0 else 0
                embed_id = record[rels[choice - 1]["column"]]
                other_id = record[rels[other_index]["column"]]

                embed_collection = db[embed_in]
                other_collection = db[to_collections[other_index]]

                other_document = other_collection.find_one({"id": other_id})
                if other_document:
                    embed_collection.update_one(
                        {"id": embed_id},
                        {"$addToSet": {junction: other_document}},
                        upsert=True,
                    )


def prompt_user_for_embedding_direction(from_collection_name, to_collection_names):
    # get user to decide
    print(
        f"For the many-to-many relationship between {from_collection_name} and {to_collection_names[0]} / {to_collection_names[1]}:"
    )
    print(
        f"1. Embed {from_collection_name} details in {to_collection_names[0]} documents."
    )
    print(
        f"2. Embed {from_collection_name} details in {to_collection_names[1]} documents."
    )
    choice = input("Enter your choice (1 or 2): ")
    while choice not in ["1", "2"]:
        print("Invalid choice. Please enter 1 or 2.")
        choice = input("Enter your choice (1 or 2): ")
    return int(choice)


def drop_junction_tables(db, relationships):
    for relation in relationships:
        if relation["type"] == "many-to-many":
            db[relation["junction_table"]].drop()


# def main():
#     client = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = client["zbd_czy_dojade"]
#     conn = psycopg2.connect(
#         dbname="zbd_czy_dojade",
#         user="postgres",
#         password="123456",
#         host="localhost",
#         port="5432",
#     )
#     cursor = conn.cursor()

#     with open("schema_details.json", "r") as file:
#         schema = json.load(file)
#         relationships = schema.pop("relationships", [])

#     create_db(cursor, db, schema)
#     handle_relationships(db, [r for r in relationships if r["type"] != "many-to-many"])
#     handle_many_to_many_relations(db, relationships)
#     drop_junction_tables(db, relationships)

#     cursor.close()
#     conn.close()


# if __name__ == "__main__":
#     main()


def many_to_many(conn, db, rel_choice):
    cursor = conn.cursor()

    with open("schema_details.json", "r") as file:
        schema = json.load(file)
        relationships = schema.pop("relationships", [])

    create_db(cursor, db, schema)
    handle_relationships(
        db, [r for r in relationships if r["type"] != "many-to-many"], rel_choice
    )
    handle_many_to_many_relations(db, relationships)
    drop_junction_tables(db, relationships)

    cursor.close()
