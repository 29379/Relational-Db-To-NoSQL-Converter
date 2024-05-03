use serde::Deserialize;

use std::path::Path;
pub mod stop;

#[derive(Deserialize)]
pub struct Record {
    route_id: String,
    agency_id: usize,
    route_short_name: String,
    route_long_name: String,
    route_desc: String,
    route_type: usize,
    route_type2_id: usize,
    valid_from: String,
    valid_until: String,
}

pub fn get_collections() {
    let stop_id = stop::get_stop_id();
    let mut route_stop: Vec<(usize, String, usize, usize)> = Vec::new();
    //(id, route_id, stop_id, current_stop_in_route)
    let mut id_count = 0usize;

    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/routes.txt");
    csv::Reader::from_path(path)
        .unwrap()
        .deserialize::<Record>()
        .for_each(|record_result| match record_result {
            Ok(record) => record
                .route_desc
                .split(" - ")
                .enumerate()
                .for_each(|(i, stop_name)| {
                    id_count = id_count +1;
                    let current_id = id_count;
                    route_stop.push((current_id, record.route_id.clone(),match stop_id.get(stop_name){
                        Some(stop_id) => *stop_id,
                        None => {
                            println!("Nie ma takiego klucza dla przystanku: {}",stop_name);
                        0
                        }
                    },i))
                }),
            Err(e) => println!("{}", e),
        });
    println!("{:?}",route_stop);
}
