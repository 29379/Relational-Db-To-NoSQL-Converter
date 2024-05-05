use serde::Deserialize;

use std::{collections::HashMap, path::Path};
pub mod stop;

#[derive(Deserialize)]
pub struct Record {
    route_id: String,
    #[allow(dead_code)]
    agency_id: usize,
    #[allow(dead_code)]
    route_short_name: String,
    #[allow(dead_code)]
    route_long_name: String,
    route_desc: String,
    route_type: usize,
    #[allow(dead_code)]
    route_type2_id: usize,
    #[allow(dead_code)]
    valid_from: String,
    #[allow(dead_code)]
    valid_until: String,
}
//                              route, route_Stop, stop
pub fn get_collections() -> (Vec<(String, usize)>,Vec<(usize, String, usize, usize)>,Vec<(usize, usize, String, f64, f64)>){
    let mut stops_id = stop::get_stop_id();
    let mut last_stop_id = get_last_id(&stops_id);
    let mut route_stop: Vec<(usize, String, usize, usize)> = Vec::new();
    //(id, route_id, stop_id, current_stop_in_route)
    let mut id_route_stop = 0usize;

    let mut route: Vec<(String, usize)> = Vec::new();

    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/routes.txt");
    csv::Reader::from_path(path)
        .unwrap()
        .deserialize::<Record>()
        .for_each(|record_result| match record_result {
            Ok(record) => {
                route.push((record.route_id.clone(), record.route_type));
                record
                    .route_desc
                    .split(" - ")
                    .enumerate()
                    .for_each(|(i, stop_name)| {
                        id_route_stop = id_route_stop + 1;
                        let current_id = id_route_stop;
                        route_stop.push((
                            current_id,
                            record.route_id.clone(),
                            stops_id
                                .entry((*stop_name).to_string())
                                .or_insert_with(|| {
                                    last_stop_id = last_stop_id + 1;
                                    last_stop_id
                                })
                                .clone(),
                            i,
                        ))
                    })
            }
            Err(e) => println!("{}", e),
        });
    (route,route_stop,stop::create_stop(stops_id))
}

fn get_last_id(hash_map: &HashMap<String, usize>) -> usize {
    hash_map.values().max().unwrap().clone()
}
