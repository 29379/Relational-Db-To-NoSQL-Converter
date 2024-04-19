import pymongo
import json
import datetime

# trying to use embedding and referencing based on foreign key relationships
# creates a single document for each column, directly embedding or referencing other documents
def infer_rules(schema):
    embedding_rules = {}
    reference_rules = {}

    # look for foreign keys
    for table, columns in schema.items():
        if table not in ["databasechangelog", "databasechangeloglock"]:
            for column in columns:
                # embed if there are few foreign key relations, otherwise reference
                if "constraint_type" in column and column["constraint_type"] == "FOREIGN KEY":
                    referenced_table = column['foreign_table']

                    # check the count of foreign key relations to this table                
                    if len(schema[referenced_table]) <= 5: # probably need to find better way to determine
                        if table not in embedding_rules:
                            embedding_rules[table] = []
                        embedding_rules[table].append(column["column_name"])

                    else:
                        if table not in reference_rules:
                            reference_rules[table] = []
                        reference_rules[table].append(column["column_name"])

    return embedding_rules, reference_rules

def create_db():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["czy_dojade"]

    with open("schema_details.json", "r") as file:
        schema = json.load(file)

    embedding_rules, reference_rules = infer_rules(schema)

    for collection_name, columns in schema.items():
        collection = db[collection_name]
        for column in columns:
            column_name = column['column_name']
            data_type = column.get('data_type', '')

            # example data generation
            example_value = None
            if data_type == "character varying":
                example_value = "example_text"[:column.get("max_length", len("example_text"))]
            elif data_type == "bigint":
                example_value = 123
            elif data_type == "boolean":
                example_value = True
            elif data_type == "double precision":
                example_value = 123.456
            elif data_type == "timestamp without time zone":
                example_value = datetime.datetime.now()
            
            # handle embedding
            if column_name in embedding_rules.get(collection_name, []):
                if 'foreign_table' in column:
                    embedded_documents = list(db[column['foreign_table']].find())
                    for doc in embedded_documents:
                        document = {**column, 'embedded_data': doc, column_name: example_value}
                        collection.insert_one(document)

            # handle referencing
            elif column_name in reference_rules.get(collection_name, []):
                if 'foreign_table' in column:
                    # reference by ids
                    referenced_documents = list(db[column['foreign_table']].find({}, {'_id': 1}))
                    document = {**column, 'references': referenced_documents, column_name: example_value}
                    collection.insert_one(document)
            else:
                # other types of data
                document = {column_name: example_value}
                collection.insert_one(document)

            # create indexes for primary and foreign keys
            if "constraint_type" in column:
                index_name = f"{collection_name}_{column_name}_index"
                if column["constraint_type"] == "PRIMARY KEY":
                    collection.create_index([(column_name, pymongo.ASCENDING)], name=index_name)
                elif column["constraint_type"] == "FOREIGN KEY":
                    collection.create_index([(column_name, pymongo.ASCENDING)], name=index_name + "_fk")

def main():
    create_db()

if __name__ == "__main__":
    main()
