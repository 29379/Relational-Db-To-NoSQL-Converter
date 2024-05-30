use std::collections::HashMap;

use serde::Deserialize;

#[derive(Deserialize)]
pub struct Record {
    route_id: String,
    #[allow(dead_code)]
    service_id: u8,
    trip_id: String,
    trip_headsign: String,
    direction_id: u8,
    #[allow(dead_code)]
    shape_id: usize,
    #[allow(dead_code)]
    brigade_id: u8,
    vehicle_id: u8,
    #[allow(dead_code)]
    variant_id: usize,
}

pub fn get_collections() -> (Vec<(String, u8, String, u8, usize)>, HashMap<String, usize>) {
    use std::path::Path;

    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/trips.txt");
    let mut reader = csv::Reader::from_path(path).unwrap();
    let mut trip_destination: HashMap<String, usize> = HashMap::new();
    // trip_destination HashMap< Trip_heasign, id>
    //
    let mut trip: Vec<(String, u8, String, u8, usize)> = Vec::new();
    //trip Vec<(id,direction_id,Route_Id,vechicle_id,trip_destination_id)

    let mut trip_heads_count = 0;

    reader
        .deserialize::<Record>()
        .for_each(|record_result| match record_result {
            Ok(record) => {
                let trip_destiantion_id = trip_destination
                    .entry(record.trip_headsign)
                    .or_insert_with(|| {
                        let count: usize = {
                            trip_heads_count = trip_heads_count + 1;
                            trip_heads_count
                        };
                        count
                    });
                trip.push((
                    record.trip_id,
                    record.direction_id,
                    record.route_id,
                    record.vehicle_id,
                    trip_destiantion_id.clone(),
                ))
            }
            Err(e) => println!("{}", e),
        });
    (trip,trip_destination)
}

pub fn trip_vec_to_hash_map(
    trip: Vec<(String, u8, String, u8, usize)>,
) -> HashMap<String, (u8, String, u8, usize)> {
    let map: HashMap<String, (u8, String, u8, usize)> = HashMap::from_iter(trip
        .into_iter()
        .map(|trip_entry| {
        (
            trip_entry.0,
            (trip_entry.1, trip_entry.2, trip_entry.3, trip_entry.4),
        )
    }));
    map
}
