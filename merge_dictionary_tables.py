import datetime
import pymongo
import psycopg2
import json
from bson import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal

# TODO: merging the postgresql data
# TODO: handling self referencing tables - big trouble


def is_id_column(column_name, pattern, patterns=None):
    if patterns is None:
        patterns = [pattern + "id", pattern + "_id"]
    return column_name.lower() in patterns


def create_meged_table_name(from_table, to_table):
    return from_table + "__" + to_table


def check_if_is_a_dictionary_table(columns_info):
    num_of_regular_columns = 0

    for cols in columns_info:
        if cols["constraints"] is not None \
                and cols["constraints"] != []:
            if "PRIMARY KEY" not in cols["constraints"] \
                    and "FOREIGN KEY" not in cols["constraints"]:
                num_of_regular_columns += 1
        else:
            num_of_regular_columns += 1
    return num_of_regular_columns == 1


def create_db(cursor, db, schema, relationships):
    handle_merging_tables_relationships(schema, relationships)
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


def handle_merging_tables_relationships(schema, relationships, merged_tables=set()):
    # Process one-to-one relationships first
    for relation in relationships:
        if relation["from"] in merged_tables or relation["to"] in merged_tables:
            continue
        if relation.get("type") == "one-to-one":
            merge_one_to_one(schema, relationships, relation, merged_tables)
            
    # Process many-to-one relationships afterwards
    for relation in relationships:
        if relation["from"] in merged_tables or relation["to"] in merged_tables:
            continue
        if relation.get("type") == "many-to-one" and \
              (relation.get("from") != relation.get("to")): # self referencing tables do not count here
            merge_many_to_one(schema, relationships, relation, merged_tables)


def merge_many_to_one(schema, relationships, relation, merged_tables):
    is_a_dictionary_table = check_if_is_a_dictionary_table(schema[relation["to"]])

    if is_a_dictionary_table:
        print("\nmany-to-one merging (dictionary table - " + relation["from"] +"): - contents from: " + relation["to"] + " go inside: " + relation["from"] + "\n")
        fix_schema_details(
            schema,
            relationships,
            relation["from"],
            relation["to"]
        )
        merged_tables.add(relation["to"])
        merged_tables.add(relation["from"])
        # merged_tables.add(create_meged_table_name(relation["from"], relation["to"]))
        
        #   recursive call - if a table 'relation["to"]' was merged into table 'relation["from"]',
        #   then 'relation["to"]' table ceases to exist, so we can skip it, and the table
        #   'relation["from"]' does not meet the criteria for further evaluation anymore,
        #   so we can skip it as well
        handle_merging_tables_relationships(schema, relationships, merged_tables)
    else:
        is_a_dictionary_table = check_if_is_a_dictionary_table(schema[relation["from"]])
        if is_a_dictionary_table:
            print("\nE: many-to-one merging (dictionary table - " + relation["from"] +"): - contents from: " + relation["from"] + " go inside: " + relation["to"] + "\n")
            fix_schema_details(
                schema,
                relationships,
                relation["to"],
                relation["from"]
            )
            merged_tables.add(relation["to"])
            merged_tables.add(relation["from"])
            # merged_tables.add(create_meged_table_name(relation["from"], relation["to"]))
            handle_merging_tables_relationships(schema, relationships, merged_tables)


def merge_one_to_one(schema, relationships, relation, merged_tables):
    print("\none-to-one merging: - contents from: " + relation["to"] + " go inside: " + relation["from"] + "\n")
    fix_schema_details(
        schema,
        relationships,
        relation["from"],
        relation["to"]
    )
    merged_tables.add(relation["to"])
    merged_tables.add(relation["from"])
    # merged_tables.add(create_meged_table_name(relation["from"], relation["to"]))
    handle_merging_tables_relationships(schema, relationships, merged_tables)


def fix_schema_details(schema, relationships, cardinality_one, cardinality_many):
    #   cardinality_one    -    route      |  trip_destination
    #   cardinality_many   -    route_type |  trip
    relations_tmp = []
    merged_table_name = create_meged_table_name(cardinality_one, cardinality_many)
    junction_tables = {}

    #   modifying relationships
    for relation in relationships:
        if relation["from"] == cardinality_many:
            if relation["to"] != cardinality_one:   # self referencing tables left the chat but noone has to know
                relation["from"] = merged_table_name
                relations_tmp.append(relation)
        elif relation["to"] == cardinality_many:
            if relation["from"] == cardinality_one:
                pass
            else:
                relation["to"] = merged_table_name
                relations_tmp.append(relation)    
        else:
            relations_tmp.append(relation)
    relationships[:] = relations_tmp

    #   modifying schema
    if cardinality_many in schema and cardinality_one in schema:
        cardinality_many_schema_accumulator = schema.pop(cardinality_many)
        primary_key_column = None
        fk_many_to_one_merging_column = None
        filtered_columns = []

        # finding primary key and foreign key to 'cardinality_one' table
        # (used when the dictionary table is on the 'many' side of the relationship)
        for column in cardinality_many_schema_accumulator:
            if "constraints" in column \
                    and column["constraints"] != []:
                if "PRIMARY KEY" in column["constraints"]:
                    primary_key_column = column
                    if fk_many_to_one_merging_column is not None:
                        break
                else:
                    if "FOREIGN KEY" in column["constraints"] \
                            and cardinality_one == column["foreign_table"]:
                        fk_many_to_one_merging_column = column
                        if primary_key_column is not None:
                            break
                
        # keeping all the columns from 'cardinality_one' table that are not a foreign key to 'cardinality_many' table
        for column in schema[cardinality_one]:
            if not ("FOREIGN KEY" in column.get("constraints") \
                    and cardinality_many == column.get("foreign_table")):
                filtered_columns.append(column)
        schema[cardinality_one] = filtered_columns

        # merging the tables
        for column in cardinality_many_schema_accumulator:
            if column != primary_key_column and column != fk_many_to_one_merging_column:
                schema[cardinality_one].append(column)
        schema[merged_table_name] = schema.pop(cardinality_one)

    # renaming junction tables in relationships
    for relation in relationships:
        if "junction_table" in relation:
            old_name = relation["junction_table"]
            if cardinality_many in relation["junction_table"]:
                relation["junction_table"] = relation["junction_table"].replace(cardinality_many, merged_table_name)
                relation["from"] = relation["from"].replace(cardinality_many, merged_table_name)
            elif cardinality_one in relation["junction_table"]:
                relation["junction_table"] = relation["junction_table"].replace(cardinality_one, merged_table_name)
                relation["from"] = relation["from"].replace(cardinality_one, merged_table_name)
            junction_tables[old_name] = relation["junction_table"]

    # renaming junction tables in schema
    for old_name, new_name in junction_tables.items():
        schema[new_name] = schema.pop(old_name)

    # renaming everything
    rename_merged_table(schema, cardinality_one, cardinality_many, merged_table_name)
    rename_merged_table(relationships, cardinality_one, cardinality_many, merged_table_name)

    with open('after.json', 'w') as after_file:
        json.dump(
            {"schema": schema, 
             "relationships": relationships},
             after_file, 
             indent=4
        )


def rename_merged_table(obj, old_name_f, old_name_t, new_name):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and (value == old_name_f or value == old_name_t):
                obj[key] = new_name
            elif isinstance(value, str) and is_id_column(value, old_name_f):
                obj[key] = value.replace(old_name_f, new_name)
            elif isinstance(value, str) and is_id_column(value, old_name_t):
                obj[key] = value.replace(old_name_t, new_name)
            else:
                rename_merged_table(value, old_name_f, old_name_t, new_name)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str) and (item == old_name_f or item == old_name_t):
                obj[i] = new_name
            elif isinstance(item, str) and is_id_column(item, old_name_f):
                obj[i] = item.replace(old_name_f, new_name)
            elif isinstance(item, str) and is_id_column(item, old_name_t):
                obj[i] = item.replace(old_name_t, new_name)
            else:
                rename_merged_table(item, old_name_f, old_name_t, new_name)


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
