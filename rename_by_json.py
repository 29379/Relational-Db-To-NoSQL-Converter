def rename_fields_recursive(document, changes):
    updates = {}
    for old_field, new_field in changes.items():
        if old_field in document:
            updates[new_field] = document.pop(old_field)
    for key, value in document.items():
        if isinstance(value, dict):
            document[key] = rename_fields_recursive(value, changes)
        elif isinstance(value, list):
            document[key] = [
                (
                    rename_fields_recursive(item, changes)
                    if isinstance(item, dict)
                    else item
                )
                for item in value
            ]
    document.update(updates)
    return document


def apply_changes_to_database(db, changes):
    for collection_name, changes_list in changes.items():
        collection = db[collection_name]
        changes_dict = {change["old"]: change["new"] for change in changes_list}

        for document in collection.find():
            updated_document = rename_fields_recursive(document, changes_dict)
            collection.replace_one({"_id": document["_id"]}, updated_document)

        for other_collection_name in db.list_collection_names():
            if other_collection_name != collection_name:
                other_collection = db[other_collection_name]
                for document in other_collection.find():
                    updated_document = rename_fields_recursive(document, changes_dict)
                    other_collection.replace_one(
                        {"_id": document["_id"]}, updated_document
                    )
