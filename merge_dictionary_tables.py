import datetime
import pymongo
import psycopg2
import json
from bson import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal


def create_db(cursor, db, schema, relationships):
    # populate with data
    for collection_name, columns_info in schema.items():
        collection = db[collection_name]
        column_names = [col["column_name"] for col in columns_info]

        handle_merging_tables_relationships(cursor, schema, relationships)

        data_from_pg = fetch_data_from_postgres(cursor, collection_name, column_names)

        for row in data_from_pg:
            document = {
                col["column_name"]: convert_to_compatible_types(row[idx])
                for idx, col in enumerate(columns_info)
            }
            document["_id"] = ObjectId()
            collection.insert_one(document)


def handle_merging_tables_relationships(cursor, schema, relationships, merged_tables=set()):
    for relation in relationships:
        if relation["from"] in merged_tables or relation["to"] in merged_tables:
            continue
        for label, value in relation.items():
            if label == "type" and value == "many-to-one":
                num = evaluate_if_dictionary_table(schema[relation["to"]])
                # print("From: " + relation["from"] + " To: " + relation["to"] + " Num: " + str(num))
                if num <= 1:
                    fix_schema_details(
                        schema,
                        relationships,
                        relation["from"],
                        relation["to"]
                    )
                    merged_tables.add(relation["to"])
                    #   recursive call - if a table 'relation["to"]' was merged into table 'relation["from"]',
                    #   then 'relation["to"]' table ceases to exist, so we can skip it, and the table
                    #   'relation["from"]' does not meet the criteria for further evaluation anymore,
                    #   so we can skip it as well
                    handle_merging_tables_relationships(cursor, schema, relationships, merged_tables)


def evaluate_if_dictionary_table(columns_info):
    num_of_columns = len(columns_info)
    for cols in columns_info:
        for label, info in cols.items():
            if label == "constraints" and info is not None and info != []:
                for constraint in info:
                    if "KEY" in constraint:
                        num_of_columns -= 1
                        break
    return num_of_columns


def fix_schema_details(schema, relationships, from_t, to_t):
    print(schema)
    for relation in relationships:
        if relation["from"] == to_t:
            relation["from"] = from_t
        elif relation["to"] == to_t:
            relation["to"] = from_t
    if to_t in schema and from_t in schema:
        to_t_accumulator = schema.pop(to_t)
        primary_key_column = None

        for column in to_t_accumulator:
            if column["constraints"] is not None and column["constraints"] != []:
                if "PRIMARY KEY" in column["constraints"]:
                    primary_key_column = column
                    break
        for column in to_t_accumulator:
            if column != primary_key_column:
                schema[from_t].append(column)
    print("\n- - - - - - - - - -\n")
    print(schema)


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


def handle_relationships(db, relationships):
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
                    from_collection.update_one(
                        {"_id": document["_id"]},
                        {"$set": {column_key: related_document}},
                    )

                # using the id
                # from_collection.update_one(
                #         {"_id": document["_id"]},
                #         {"$set": {column_key: related_document_id}},
                #     )    

                # using the object id
                # related_document = to_collection.find_one({"id": related_document_id})
                # if related_document_id and related_document is not None and related_document["_id"]:
                #     from_collection.update_one(
                #         {"_id": document["_id"]},
                #         {"$set": {column_key: related_document.get("_id")}},
                #     )


def main():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["zbd_czy_dojade"]
    conn = psycopg2.connect(
        dbname='zbd_czy_dojade',
        user='postgres',
        password='asdlkj000',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()

    with open("schema_details.json", "r") as file:
        schema = json.load(file)
        relationships = schema.pop("relationships", [])

    create_db(cursor, db, schema, relationships)
    handle_relationships(db, relationships)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
