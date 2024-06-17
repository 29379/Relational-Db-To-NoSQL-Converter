def get_starting_ids(foreign_key_mapping, current_table):
    starting_ids = set()
    for key, value in foreign_key_mapping.items():
        if current_table in value:
            for pair in value[current_table]:
                starting_ids.add(pair[1])
    return list(starting_ids)


def find_chain(foreign_key_mapping, current_table, merged_table_name):
    chain = [current_table]
    while True:
        found = False
        for key, value in foreign_key_mapping.items():
            if current_table in value:
                chain.append(key)
                current_table = key
                found = True
                break
        if not found or current_table == merged_table_name.split('__')[0]:
            break
    # chain.reverse()
    return chain

def build_resolution(foreign_key_mapping, postgres_data, current_table, merged_table_name):
    chain = find_chain(foreign_key_mapping, current_table, merged_table_name)
    starting_ids = get_starting_ids(foreign_key_mapping, current_table)

    resolved_ids = {}
    for start_id in starting_ids:
        current_id = start_id
        
        for i in range(1, len(chain)):
            table = chain[i]
            previous_table = chain[i - 1]
            next_id = None
            
            for fk_pair in foreign_key_mapping[table].get(previous_table, []):
                if fk_pair[1] == current_id:
                    next_id = fk_pair[0]
                    break
            
            if next_id is not None:
                current_id = next_id
            else:
                break
        
        resolved_ids[start_id] = current_id
    
    return resolved_ids

# Example usage
foreign_key_mapping = {
    "live_stop_time": {
        "schedule_stop_time": [[1,0], [2,1], [3,4]]
    },
    "accident": {
        "trip": [[13,10], [14,11], [15,12]]
    },
    "trip": {
        "route": [[10,7], [11,8], [12,9]],
        "trip_destination": [[10,1], [11,2], [12,3]]
    },
    "route": {
        "route_type": [[7,4], [8,5], [9,6]]
    }
}

postgres_data = {
    "accident": [
        [13, 'accident_1', 10], [14, 'accident_2', 11], [15, 'accident_3', 12]
    ],
    "trip": [
        [10, 'trip_0', 7], [11, 'trip_1', 8], [12, 'trip_4', 9]
    ],
    "route": [
        [7, 'route_0', 4], [8, 'route_1', 5], [9, 'route_4', 6]
    ],
    "route_type": [
        [4, 'type_0'], [5, 'type_1'], [6, 'type_4']
    ],
    "trip_destination": [
        [1, 'destination_0', 10], [2, 'destination_1', 11], [3, 'destination_4', 11]
    ]
}

current_table = 'route'
merged_table_name = 'accident__trip__route__route_type__trip_destination'

resolution = build_resolution(foreign_key_mapping, postgres_data, current_table, merged_table_name)
print(resolution)

[
    ({'accident': 10},{'trip_destination': 1}),
    ({'accident': 11},{'trip_destination': 2}),
    ({'accident': 12},{'trip_destination': 3})
]