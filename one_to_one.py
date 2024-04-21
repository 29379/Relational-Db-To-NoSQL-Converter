import pymongo
import json
import datetime

# one-to-one
def create_db():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["czy_dojade"]

    with open("schema_details.json", "r") as file:
        schema = json.load(file)

    for collection_name, columns in schema.items():
        if collection_name not in ["databasechangelog", "databasechangeloglock"]:
            collection = db[collection_name]
            indexes = []

            document = {}

            for column in columns:
                column_name = column["column_name"]
                data_type = column["data_type"]
                if "constraint_type" in column:
                    if column["constraint_type"] == "PRIMARY KEY":
                        index_name = f"{collection_name}_{column_name}_index"
                        indexes.append(([(column_name, pymongo.ASCENDING)], index_name))
                    elif column["constraint_type"] == "FOREIGN KEY":
                        # foreign keys 
                        index_name = f"{collection_name}_{column_name}_fk_index"
                        indexes.append(([(column_name, pymongo.ASCENDING)], index_name))
                
                # example data generation
                if data_type == "character varying":
                    document[column_name] = "example_text"[:column.get("max_length", len("example_text"))]
                elif data_type == "bigint":
                    document[column_name] = 123456789012345
                elif data_type == "boolean":
                    document[column_name] = True
                elif data_type == "double precision":
                    document[column_name] = 123.456
                elif data_type == "timestamp without time zone":
                    document[column_name] = datetime.datetime.now()

            if indexes:
                collection.create_indexes([pymongo.IndexModel(fields, name=name) 
                for fields, name in indexes])
            
            collection.insert_one(document)

def main():
    create_db()

if __name__ == "__main__":
    main()
