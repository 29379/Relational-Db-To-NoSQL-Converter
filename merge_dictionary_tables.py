import datetime
import pymongo
import psycopg2
import json
import copy
from bson import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal
from collections import defaultdict


# TODO: map the keys inside all the other tables, not only the base one


class ForeignKeyMappingTuple:
    def __init__(self, disappearing_table_key, expanding_table_key):
        self.disappearing_table_key = disappearing_table_key
        self.expanding_table_key = expanding_table_key

    def __iter__(self):
        yield self.disappearing_table_key
        yield self.expanding_table_key


class ForeignKeyInfo:
    def __init__(self, table_from, index_of_attribute, table_to):
        self.table_from = table_from
        self.index_of_attribute = index_of_attribute
        self.table_to = table_to


def get_column_index(table, column_name, schema):
    for i, col in enumerate(schema[table]):
        if col["column_name"] == column_name:
            return i
    return None


def find_base_table(merged_table, merged_data):
    base_table = None
    for table_name in merged_data:
        if merged_table.startswith(table_name):
            base_table = table_name
            break
    return base_table


def check_if_a_part_of_merged_table(name, merged_table_names):
    for table_name in merged_table_names:
        if name in table_name:
            return True
        split = table_name.split("__")
        if name in split:
            return True
    return False


def update_foreign_keys(schema_after, schema_before, relationships_before, relationships_after, merged_data, foreign_key_mapping):
    merged_table_names = []
    merged_table_relationship_info = []
    tables_before_relationship_info = []

    #   gather info from schema_after
    for collection_name, fields in schema_after.items():
        split = collection_name.split("__")
        if len(split) != 1 and not is_a_junction_table(collection_name, relationships_after):
            merged_table_names.append(collection_name)
    for collection_name, fields in schema_after.items():
        for field_id, field in enumerate(fields):
            if "FOREIGN KEY" in field.get("constraints", []) and check_if_a_part_of_merged_table(field.get("foreign_table"), merged_table_names):
                merged_table_relationship_info.append(ForeignKeyInfo(collection_name, field_id, field.get("foreign_table")))
    
    #   gather info from schema_before
    for collection_name, fields in schema_before.items():
        if not check_if_a_part_of_merged_table(collection_name, merged_table_names):
            continue
        for field_id, field in enumerate(fields):
            if "FOREIGN KEY" in field.get("constraints", []) and check_if_a_part_of_merged_table(field.get("foreign_table"), merged_table_names):
                tables_before_relationship_info.append(ForeignKeyInfo(collection_name, field_id, field.get("foreign_table")))
    
    #   go through merged_data
    for collection_name, rows in merged_data.items():
        if collection_name not in merged_table_names:
            continue
        split_table_name = collection_name.split("__")
        
        #   REMEMBER TO USE - merged_table_names, merged_table_relationship_info, tables_before_relationship_info
        #TODO: update foreign_key_mapping here - for example for 'report'
        path = find_the_mapping_path(collection_name, split_table_name, foreign_key_mapping)    #TODO: fix
        find_the_mapping_keys(path, foreign_key_mapping, merged_data)   #TODO: fix
        

def find_the_mapping_path(table_name, split_table_name, foreign_key_mapping, path=[]):
    if table_name == split_table_name[0]:
        path.append((table_name, split_table_name[0]))
        return path
    for table_from, connections in foreign_key_mapping.items():
        for table_to, _ in connections.items():
            if table_to == table_name:
                path.append((table_from, table_to))
                return find_the_mapping_path(table_from, split_table_name, foreign_key_mapping, path)
    return path

def find_the_mapping_keys(path, foreign_key_mapping, merged_data):
    keys = []
    for i, step in enumerate(path):
        table_from, table_to = step
        mapping = foreign_key_mapping[table_from][table_to]
        for disappearing_key, expanding_key in mapping:
            if i == 0:
                keys.append((disappearing_key, expanding_key))
            else:
                pass

    # for i in range(1, len(split_table_name)):
    #     if split_table_name[i] in foreign_key_mapping:
    #         path.append((split_table_name[i - 1], split_table_name[i]))
    #     else:
    #         for table_from, tables_to in foreign_key_mapping.items():
    #             for table_to, mappings in tables_to.items():
    #                 if table_to == split_table_name[i]:
    #                     path.append((table_from, table_to))
    # return path
    

"""
3   loop through merged_data table by table (only tables saved as 'table_from' in the 1.2.1 step)
        (if one table_from has multiple table_to's, then do them back to back in order how they were saved in the 1.2.1 step)
    3.1     split the table name
    3.2     is table_to saved in 1.2.1 the first element in the split table name?
        3.2.1   if yes, skip the iteration
        3.2.2   if not - find the 'path' to the beginning of the split table name by recurrently examining foreign_key_mapping
                for example: i have 'trip_destination' - it is one of the values for a key 'trip', so i go to 'trip' and check if 
                it is the first value in split_table name - it is not, so it must be a value for something else
                it happens that it is one of the values for 'accident' so that I know it is the end of the path
                I need to save the path, so that later I will know, that I have to do this:
                    *finding_path_pseudocode:
                        - find trip_destination as a value to trip key - to a path list append: (trip, trip_destination)
                        - go to where 'trip' is the value and not the key (accident > trip) - to a path list append: (accident, trip)
                        - accident is the first part of split_table_name, so that is all
                    *finding_keys_pseudocode:
                        - using previously found path, in a loop, save a list of keys:
                            -- using the path go through foreign_key_mapping to find your way all the way to the first table in split_table_name
                                --- save two values: the original, and the last value in the path
                
    3.3    execute finding_keys_pseudocode
    3.4    go through all rows and based on what was saved while executing finding_keys_pseudocode, save the values to the right table in merged_data
"""
    # for table, rows in merged_data.items():
    #     split_table_name = table.split("__")
    #     for row in rows:
    #         for i, value in enumerate(row):
    #             if i == 0:
    #                 continue
    #             if split_table_name[i] in foreign_key_mapping:
    #                 for table_from, tables_to in foreign_key_mapping[split_table_name[i]].items():
    #                     for table_to, mappings in tables_to.items():
    #                         if table_to == split_table_name[i - 1]:
    #                             if value in mappings:
    #                                 row[i] = mappings[value]
    #                             else:
    #                                 print("Foreign key not found in mapping: " + str(value))
    #             else:
    #                 for table_from, tables_to in foreign_key_mapping.items():
    #                     for table_to, mappings in tables_to.items():
    #                         if table_to == split_table_name[i]:
    #                             if value in mappings:
    #                                 row[i] = mappings[value]
    #                             else:
    #                                 print("Foreign key not found in mapping: " + str(value))

#   -------- ----- ------ ----- - ------

    # for table, fields in schema_before.items():
    #     for field in fields:
    #         if "FOREIGN KEY" in field.get("constraints", []):
    #             foreign_table = field["foreign_table"]

    #             is_in_fk_mapping = False
    #             if foreign_table in foreign_key_mapping:
    #                 is_in_fk_mapping = True
    #             else:
    #                 for k, v in foreign_key_mapping:
    #                     if foreign_table in v:
    #                         is_in_fk_mapping = True
    #                         break
                
    #             if is_in_fk_mapping:
    #                 column_index = get_column_index(table, field["column_name"], schema_before)
    #                 if column_index is not None:
    #                     for row in postgres_data[table]:
    #                         foreign_key = row[column_index]
    #                         if foreign_key in foreign_key_mapping[foreign_table]:
    #                             row[column_index] = foreign_key_mapping[foreign_table][foreign_key]
    #                         else:
    #                             print("Foreign key not found in mapping: " + str(foreign_key))



def replace_names(value, old_name, new_name):
    if value == old_name:
        return new_name
    elif value == f"{old_name}id":
        return f"{new_name}id"
    elif value == f"{old_name}_id":
        return f"{new_name}_id"
    return value


def verify_and_clean_foreign_keys(relationships, schema):
    valid_ones = {}
    sus_ones = {}

    for collection_name, fields in schema.items():
        foreign_keys = [
            (collection_name, field)
            for field in fields
            if "FOREIGN KEY" in field["constraints"]
        ]
        for name, fields in foreign_keys:
            
            if (name, fields["foreign_table"]) not in valid_ones:
                valid_ones[(name, fields["foreign_table"])] = []
            if fields["column_name"] == fields["foreign_table"] + "id" or fields["column_name"] == fields["foreign_table"] + "_id":
                valid_ones[(name, fields["foreign_table"])].append(fields["column_name"])
            else:
                if (name, fields["foreign_table"]) not in sus_ones:
                    sus_ones[(name, fields["foreign_table"])] = []
                sus_ones[(name, fields["foreign_table"])].append(fields["column_name"])

    # clean up schema
    fields_to_remove = []
    visited = set()
    for key, value in sus_ones.items():
        if key in valid_ones:
            for collection_name, fields in schema.items():
                if collection_name == key[0]:
                    for field in fields:
                        if field["column_name"] in value:
                            fields_to_remove.append((collection_name, field))
        # print("SUS ONES: " + key + " - " + str(value))
    for collection_name, field in fields_to_remove:
        schema[collection_name].remove(field)
    fields_to_remove.clear()

    # clean up relationships
    for key, value in sus_ones.items():
        if key in valid_ones:
            for rel in relationships:
                tmp = tuple((k, v) for k, v in rel.items() if k != "foreign_column")
                if tmp not in visited:
                    visited.add(tmp)
                else:
                    fields_to_remove.append(rel)
                    continue
                if rel["from"] == key[0] and rel["to"] == key[1]:
                    if rel["column"] in value:
                        fields_to_remove.append(rel)
                    
    for field in fields_to_remove:
        relationships.remove(field)



def find_first_foreign_key(split_table_name, foreign_keys, current_table_index):
    for element in split_table_name[current_table_index:]:
        if element in foreign_keys:
            return element
    return None


def backtrack_looking_for_a_mapping(current_table, foreign_key_mapping):
    for table_from, tables_to in foreign_key_mapping.items():
        for table_to, mappings in tables_to.items():
            if table_to == current_table:
                return table_from
    return None


def find_mapping_name(schema, current_table_schema, split_table_name, current_table, foreign_key_mapping):
    if current_table not in split_table_name:
        return None
    foreign_keys = []
    
    for column_info in current_table_schema:
        if "FOREIGN KEY" in column_info["constraints"] and column_info["foreign_table"] in split_table_name:
            foreign_keys.append(column_info["foreign_table"])
    if len(foreign_keys) == 0:
        return backtrack_looking_for_a_mapping(current_table, foreign_key_mapping)
    return None
    # return find_first_foreign_key(split_table_name, foreign_keys, split_table_name.index(current_table))


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


def find_max_row_number(postgres_data):
    length = 0
    for _, rows in postgres_data.items():
        length += len(rows)
    return length
    

def clip_row_list_size(list_to_clip):
    index = len(list_to_clip) - 1
    while index >= 0 and not list_to_clip[index]:
        index -= 1
    return list_to_clip[:index + 1]


def is_a_junction_table(split_name, relationships_after):
    for relation in relationships_after:
        if "junction_table" in relation:
            if relation["junction_table"] == split_name:
                return True
    return False


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


def keep_track_of_junction_table_names(junction_table, next_old_name, next_new_name):
    changed = False
    for old_name, new_name in junction_table.items():
        if new_name == next_old_name or new_name == next_new_name:
            junction_table[old_name] = next_new_name
            changed = True
    if not changed:
        junction_table[next_old_name] = next_new_name


def split_junction_table(last_part_of_table_name, schema_before):
    parts = last_part_of_table_name.split('_')
    n = len(parts)

    for i in range(n):
        first_part = '_'.join(parts[:n - i])
        second_part = '_'.join(parts[n - i:])
        if second_part in schema_before and first_part in schema_before:
            return (first_part, second_part)
    return (None, None)
    

def add_data_from_unchanged_junction_table(old_name, postgres_data):
    table_data = postgres_data[old_name]
    rows_to_save = []
    for row in table_data:
        rows_to_save.append(row)
    return rows_to_save


def find_what_to_add_from_foreign_table(schema, table_merged_into_another_name, split_table_name):
    indicies_to_add = []
    for i, table_merged_into_another_name in enumerate(schema[table_merged_into_another_name]):
        if "PRIMARY KEY" in table_merged_into_another_name["constraints"]:
            pass
        elif "FOREIGN KEY" in table_merged_into_another_name["constraints"] and \
                table_merged_into_another_name["foreign_table"] in split_table_name:
            pass
        else:
            indicies_to_add.append(i)
    return indicies_to_add


def find_the_right_row_in_foreign_table(table_data, indicies_to_add, row_id):
    if indicies_to_add is None or len(indicies_to_add) == 0:
        return None
    data = []
    for row in table_data:
        if row[0] == row_id:
            for i in indicies_to_add:
                data.append(row[i])
            return data
    return None


def find_base_name(table_name_part_in_order, foreign_key_indexes):
    for key, value in foreign_key_indexes.items():
        for name, index in value:
            if name == table_name_part_in_order:
                return key
    return None


def cleanup_junction_table_names(schema, relationships):
    with open("resources/schema_after.json", "r") as file:
        data = json.load(file)
    junction_tables = data.get('junction_tables', {})   # key - old name, value - new name

    updated_relationships = []
    for relation in relationships:
        updated_rel = {}
        for key, value in relation.items():
            if isinstance(value, str):
                for old_name, new_name in junction_tables.items():
                    value = replace_names(value, old_name, new_name)
            updated_rel[key] = value
        updated_relationships.append(updated_rel)
    updated_relationships

    for _, fields in schema.items():
        for field in fields:
            for key, value in field.items():
                if isinstance(value, str):
                    for old_name, new_name in junction_tables.items():
                        field[key] = replace_names(value, old_name, new_name)

    with open('resources/schema_after.json', 'w') as after_file:
        json.dump(
            {
                "schema": schema, 
                "relationships": updated_relationships,
                "junction_tables": junction_tables
            }, 
            after_file, 
            indent=4
        )


def handle_merging_tables_relationships(schema, relationships, merged_tables=set(), junction_tables={}):
    # Process one-to-one relationships first
    for relation in relationships:
        if relation["from"] in merged_tables or relation["to"] in merged_tables:
            continue
        if relation.get("type") == "one-to-one" and \
                relation.get("to") not in junction_tables and \
                relation.get("from") not in junction_tables: # self referencing tables do not count here
            merge_one_to_one(schema, relationships, relation, merged_tables, junction_tables)
            
    # Process many-to-one relationships afterwards
    for relation in relationships:
        if relation["from"] in merged_tables or relation["to"] in merged_tables:
            continue
        if relation.get("type") == "many-to-one" and \
                relation.get("to") not in junction_tables and \
                (relation.get("from") != relation.get("to")): # self referencing tables do not count here
            merge_many_to_one(schema, relationships, relation, merged_tables, junction_tables)

    


def merge_many_to_one(schema, relationships, relation, merged_tables, junction_tables):
    is_a_dictionary_table = check_if_is_a_dictionary_table(schema[relation["to"]])

    if is_a_dictionary_table:
        print("\nmany-to-one merging (dictionary table - " + relation["from"] +"): - contents from: " + relation["to"] + " go inside: " + relation["from"] + "\n")
        fix_schema_details(
            schema,
            relationships,
            relation["from"],
            relation["to"],
            junction_tables
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
                relation["from"],
                junction_tables
            )
            merged_tables.add(relation["to"])
            merged_tables.add(relation["from"])
            # merged_tables.add(create_meged_table_name(relation["from"], relation["to"]))
            handle_merging_tables_relationships(schema, relationships, merged_tables)


def merge_one_to_one(schema, relationships, relation, merged_tables, junction_tables):
    print("\none-to-one merging: - contents from: " + relation["to"] + " go inside: " + relation["from"] + "\n")
    fix_schema_details(
        schema,
        relationships,
        relation["from"],
        relation["to"],
        junction_tables
    )
    merged_tables.add(relation["to"])
    merged_tables.add(relation["from"])
    # merged_tables.add(create_meged_table_name(relation["from"], relation["to"]))
    handle_merging_tables_relationships(schema, relationships, merged_tables)


def fix_schema_details(schema, relationships, cardinality_one, cardinality_many, old_to_new_junction_tables):
    #   cardinality_one    -    route      |  trip_destination
    #   cardinality_many   -    route_type |  trip
    relations_tmp = []
    merged_table_name = create_meged_table_name(cardinality_one, cardinality_many)
    junction_tables = {}    # key - old name, value - new name

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
            keep_track_of_junction_table_names(old_to_new_junction_tables, old_name, relation["junction_table"])

    for old_name, new_name in junction_tables.items():
        schema[new_name] = schema.pop(old_name)

    # renaming everything
    rename_merged_table(schema, cardinality_one, cardinality_many, merged_table_name)
    rename_merged_table(relationships, cardinality_one, cardinality_many, merged_table_name)

    with open('resources/schema_after.json', 'w') as after_file:
        json.dump(
            {"schema": schema, 
             "relationships": relationships,
             "junction_tables": old_to_new_junction_tables
             },
             after_file, 
             indent=4
        )


def create_db(cursor, db, schema_before, relationships_before):
    verify_and_clean_foreign_keys(relationships_before, schema_before)
    cloned_schema_before = copy.deepcopy(schema_before)
    
    handle_merging_tables_relationships(schema_before, relationships_before)
    cleanup_junction_table_names(schema_before, relationships_before)
    
    with open("resources/schema_after.json", "r") as file:
        data = json.load(file)
    schema_after = data.get('schema', {})
    relationships_after = data.get('relationships', {})
    junction_tables = data.get('junction_tables', {})

    postgres_data = {}
    merged_data = {}

    # fetch data from postgres
    for collection_name, columns_info in cloned_schema_before.items():
        column_names = [col["column_name"] for col in columns_info]
        single_table_data_from_pg = fetch_data_from_postgres(cursor, collection_name, column_names)
        postgres_data[collection_name] = single_table_data_from_pg
    

    # handle the tables
    foreign_key_mapping = defaultdict(lambda: defaultdict(list))
    for collection_name, columns_info in schema_after.items():
        split_table_name = collection_name.split("__")

        # unchanged table
        if len(split_table_name) == 1 and split_table_name[0] in schema_after:
            merged_data[collection_name] = postgres_data[split_table_name[0]]

        # junction table
        elif split_table_name[-1] not in cloned_schema_before:
            for old_name, new_name in junction_tables.items():
                if new_name == collection_name:
                    merged_data[collection_name] = add_data_from_unchanged_junction_table(old_name, postgres_data)
        
        # merged table
        else:
            # key - table name, value: list of indicies that should be added to row
            indicies_to_add = defaultdict(list)    
            # list of rows to save - list of lists, which will then be converted to list of tuples as in postgres_data
            rows_to_save = [[] for _ in range(find_max_row_number(postgres_data))]

            foreign_key_indexes = {}   
            handled_tables = set()
            
            for table_part_index, table_name_part_in_order in enumerate(split_table_name):
                foreign_key_indexes[table_name_part_in_order] = []
                previous_table_part_name = split_table_name[table_part_index - 1] if table_part_index > 0 else None

                if table_name_part_in_order in cloned_schema_before and \
                        table_name_part_in_order in postgres_data: 
                    
                    for column_index, column in enumerate(cloned_schema_before[table_name_part_in_order]):
                        if table_part_index == 0 and column["column_name"] == "id":
                            indicies_to_add[table_name_part_in_order].append(column_index)  # primary key of merged table
                        elif "FOREIGN KEY" in column["constraints"] and column["foreign_table"] in split_table_name:
                            # i should add it sommewhere around here somehow, then use it to find an appropriate row, and then remove it
                            foreign_key_indexes[table_name_part_in_order].append((column["foreign_table"], column_index))
                            # pass    # foreign key to a table that was merged into the current one - i handle it in the next iteration of the outer loop through split_table_name
                        
                        elif table_part_index != 0 and column["column_name"] == "id":
                            pass    # literally pass, that is a primary key of a table, that was merged into the current one
                        
                        else:   # base case - regular column or foreign key to some other table
                            indicies_to_add[table_name_part_in_order].append(column_index)


                    name_to_find_mapping = previous_table_part_name if previous_table_part_name is not None else table_name_part_in_order

                    # #   if i don't find it, it means that the relationship is inverted and i'll have to handle it differently
                    # is_inverted_relationship = True
                    # if table_name_part_in_order != split_table_name[0]:
                    #     for rel_from, out in foreign_key_mapping.items():
                    #         for rel_out, keys in out.items():
                    #             if rel_out == table_name_part_in_order:
                    #                 is_inverted_relationship = False
                    #                 break

                    #   i have to go through the relationships manually and add mapping of keys to foreign_key_mapping
                    # mapping_to_table = None
                    # mapping_to_table_index = None
                    # if is_inverted_relationship:
                    #     # mapping_to_table = None
                    #     # mapping_to_table_index = None
                    #     for column_index, column in enumerate(cloned_schema_before[table_name_part_in_order]):
                    #         if "FOREIGN KEY" in column["constraints"] and column["foreign_table"] in split_table_name:
                    #             mapping_to_table = column["column_name"]
                    #             mapping_to_table_index = column_index
                    #             break
                                
                    #     if mapping_to_table_index is not None:
                    #         for row_index, row in enumerate(postgres_data[table_name_part_in_order]):
                    #             foreign_key_mapping[table_name_part_in_order][mapping_to_table].append(
                    #                 ForeignKeyMappingTuple(
                    #                     row[mapping_to_table_index],
                    #                     row[0] #row_index
                    #                 )
                    #             )

                    if table_name_part_in_order == 'trip_destination':
                        pass
                    real_mapping_name = find_mapping_name(cloned_schema_before, cloned_schema_before[table_name_part_in_order], split_table_name, table_name_part_in_order, foreign_key_mapping) or name_to_find_mapping
                    
                    for row_index, row in enumerate(postgres_data[table_name_part_in_order]):
                        if real_mapping_name in handled_tables and table_name_part_in_order in handled_tables:
                            continue
                        tmp_base_table_values = []

                        if table_name_part_in_order == split_table_name[0]:
                            for i in indicies_to_add[table_name_part_in_order]:
                                tmp_base_table_values.append(row[i])
                            for fk_table, fk_col_index in foreign_key_indexes[table_name_part_in_order]:
                                foreign_key_mapping[table_name_part_in_order][fk_table].append(
                                    ForeignKeyMappingTuple(
                                        row[fk_col_index],
                                        row_index
                                    )
                                )
                            
                        else:   
                            if real_mapping_name is not None:
                                for fk_table, index_mapping in foreign_key_mapping[real_mapping_name].items():
                                    present_id = row[0]
                                    # for disappearing_id, expanding_id in index_mapping:
                                    #     if disappearing_id == present_id and expanding_id:
                                    #         row_to_add = find_the_right_row_in_foreign_table(
                                    #             postgres_data[fk_table],
                                    #             find_what_to_add_from_foreign_table(cloned_schema_before, fk_table, split_table_name),
                                    #             disappearing_id
                                    #         )
                                    #         if row_to_add is not None:
                                    #             tmp_base_table_values.extend(row_to_add)
                                    #         break
                                    row_to_add = find_the_right_row_in_foreign_table(
                                        postgres_data[fk_table],
                                        find_what_to_add_from_foreign_table(cloned_schema_before, fk_table, split_table_name),
                                        present_id
                                    )
                                    if row_to_add is not None:
                                        tmp_base_table_values.extend(row_to_add)

                                for fk_table, fk_col_index in foreign_key_indexes[table_name_part_in_order]:
                                    foreign_key_mapping[table_name_part_in_order][fk_table].append(
                                        ForeignKeyMappingTuple(
                                            row[fk_col_index],
                                            row[0] #row_index
                                        )
                                    )

                            # foreign_key_values[table_name_part_in_order].append(
                            #     row[foreign_key_indexes[table_name_part_in_order]]
                            # )
                        
                        if all(element is not None for element in tmp_base_table_values):
                            rows_to_save[row_index] += tmp_base_table_values   
                    
                handled_tables.add(table_name_part_in_order)
                    

            rows_to_save = clip_row_list_size(rows_to_save)
            for i in range(len(rows_to_save)):
                rows_to_save[i] = tuple(rows_to_save[i])
            merged_data[collection_name] = rows_to_save
    

    update_foreign_keys(schema_after, cloned_schema_before, relationships_before, relationships_after, merged_data, foreign_key_mapping)
    print("MERGED DATA: ")
    for x, y in merged_data.items():
        print(x + " - " + str(len(y)))
        for i in y:
            print(i)
        print("\n\n\n")

    #   insert data into MongoDB
    for collection_name, columns_info in schema_after.items():
        collection = db[collection_name]
        column_names = [col["column_name"] for col in columns_info]
        data = merged_data[collection_name]

        for row in data:
            document = {
                col["column_name"]: convert_to_compatible_types(row[idx]) # tuple index out of range for 'accident__trip__route__route_type__trip_destination'
                for idx, col in enumerate(columns_info)
            }
            document["_id"] = ObjectId()
            collection.insert_one(document)

    return relationships_after


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
    print("HANDLE RELATIONSHIPS")
    for relation in relationships:
        from_collection = db[relation["from"]]
        to_collection = db[relation["to"]]
        column_key = relation.get("column", relation.get("foreign_key"))

        print("\nRELATION: from " + str(relation["from"]) + " to " + str(relation["to"]) + " column_key: " + str(column_key))

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
                print("KEY: " + key)
                if key in document:
                    print("KEY FOUND - " + str(document[key]))
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

    with open("resources/schema_details.json", "r") as file:
        schema_before = json.load(file)
        relationships_before = schema_before.pop("relationships", [])

    relationships_after = create_db(
        cursor, db,
        schema_before,
        relationships_before
    )
    handle_relationships(db, relationships_after)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()

def merging_tables(conn, db, rel_choice):
    cursor = conn.cursor()

    with open("resources/schema_details.json", "r") as file:
        schema_before = json.load(file)
        relationships_before = schema_before.pop("relationships", [])

    relationships_after = create_db(
        cursor, db,
        schema_before,
        relationships_before
    )
    handle_relationships(db, relationships_after)

    cursor.close()
