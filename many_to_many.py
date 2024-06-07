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
            for key in [relation["to"] + "id", relation["to"] + "_id"]:
                if key in document:
                    related_document_id = document[key]
                    break

            if related_document_id:
                related_document = to_collection.find_one({"id": related_document_id})
                if related_document:
                    if rel_choice == "ReferencingType.id":
                        related_document = ObjectId(related_document["_id"])
                    from_collection.update_one(
                        {"_id": document["_id"]},
                        {"$set": {column_key: related_document}},
                    )


def findUserChoices(db, relationships):
    relation_groups = {}
    choices = []
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
            choices.append({"junction": junction, "tables": to_collections})

    return choices


def handle_many_to_many_relations(db, relationships, user_choices, rel_choice):
    for choice in user_choices:
        junction = choice["junction"]
        embed_in = choice["table"]

        relationship_data = [
            rel for rel in relationships if rel.get("junction_table") == junction
        ]

        embed_collection = db[embed_in]
        other_rel = [rel for rel in relationship_data if rel["to"] != embed_in][0]
        other_collection = db[other_rel["from"]]

        junction_records = db[junction].find()
        for record in junction_records:
            for i, item in enumerate(relationship_data):
                if embed_in in relationship_data[i]["to"]:
                    embed_name = relationship_data[i]["from"]
                    id_to_remove = relationship_data[i]["column"]
                    embed_id = record[id_to_remove]
                    other_id = record["_id"]

            other_document = other_collection.find_one({"_id": other_id})

            if rel_choice != "ReferencingType.id":
                embed_id = embed_id["_id"]

            if other_document:
                update_result = embed_collection.update_one(
                    {"_id": embed_id},
                    [
                        {
                            "$set": {
                                embed_name: {
                                    "$arrayToObject": {
                                        "$filter": {
                                            "input": {"$objectToArray": other_document},
                                            "as": "field",
                                            "cond": {
                                                "$ne": ["$$field.k", id_to_remove]
                                            },
                                        }
                                    }
                                }
                            }
                        }
                    ],
                    upsert=True,
                )


def drop_junction_tables(db, relationships):
    for relation in relationships:
        if relation["type"] == "many-to-many":
            db[relation["junction_table"]].drop()


def many_to_many(conn, db, rel_choice, user_choices):
    cursor = conn.cursor()

    with open("resources/schema_details.json", "r") as file:
        schema = json.load(file)
        relationships = schema.pop("relationships", [])

    create_db(cursor, db, schema)
    verify_and_clean_foreign_keys(db, schema)
    handle_relationships(db, relationships, rel_choice)
    handle_many_to_many_relations(db, relationships, user_choices, rel_choice)
    # FIXME: we are dropping here junction tables. comment if needed
    drop_junction_tables(db, relationships)

    cursor.close()


def findUserPromptChoices(conn, db):
    choices = []
    cursor = conn.cursor()

    with open("schema_details.json", "r") as file:
        schema = json.load(file)
        relationships = schema.pop("relationships", [])

    choices = findUserChoices(db, relationships)

    cursor.close()

    return choices
