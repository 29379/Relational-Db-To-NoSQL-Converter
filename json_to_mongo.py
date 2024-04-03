import pymongo
import json

def create_db():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["czy_dojade"]

    with open("schema_details.json", "r") as file:
        schema = json.load(file)

    for collection_name, columns in schema.items():
        if collection_name != "databasechangelog" and collection_name != "databasechangeloglock":
            collection = db[collection_name]
            indexes = []

            for column in columns:
                column_name = column["column_name"]
                data_type = column["data_type"]
                if "constraint_type" in column and column["constraint_type"] in ["PRIMARY KEY", "FOREIGN KEY"]:
                    index_name = f"{collection_name}_{column_name}_index"
                    indexes.append((index_name, pymongo.ASCENDING))
                # if "max_length" in column:
                #     index_name = f"{collection_name}_{column_name}_index_m_length"
                #     if not any(index_name == index["name"] for index in collection.list_indexes()):
                #         collection.create_index([(column_name, pymongo.TEXT)], name=index_name, default_language='english')
            if indexes:
                collection.create_index(indexes)
                # existing_indexes = set((index_info["name"], index_info["key"]) for index_info in collection.list_indexes())
                # new_index_set = set((index[0], [(index[1][0][0], index[1][0][1])]) for index in indexes)
                # if not existing_indexes.intersection(new_index_set):
                #     collection.create_index(indexes)

def main():
    create_db()

if __name__ == "__main__":
    main()