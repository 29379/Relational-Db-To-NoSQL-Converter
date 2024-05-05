use serde::Deserialize;
use std::collections::HashMap;
use std::path::Path;

#[derive(Deserialize)]
pub struct Record {
    stop_id: usize,
    #[allow(dead_code)]
    stop_code: usize,
    stop_name: String,
    #[allow(dead_code)]
    stop_lat: f64,
    #[allow(dead_code)]
    stop_lon: f64,
}

pub fn get_stop_id() -> HashMap<String, usize> {
    let mut stop_id: HashMap<String, usize> = HashMap::new();

    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/stops.txt");
    csv::Reader::from_path(path)
        .unwrap()
        .deserialize::<Record>()
        .for_each(|record_result| match record_result {
            Ok(record) => {
                stop_id.insert(record.stop_name, record.stop_id);
            }
            Err(e) => println!("{}", e),
        });
    stop_id
}

pub fn create_stop(mut stops: HashMap<String, usize>) -> Vec<(usize, usize, String, f64, f64)> {
    let mut stop: Vec<(usize, usize, String, f64, f64)> = Vec::new();

    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/stops.txt");
    csv::Reader::from_path(path)
        .unwrap()
        .deserialize::<Record>()
        .for_each(|record_result| match record_result {
            Ok(record) => stop.push((
                match stops.remove_entry(&record.stop_name) {
                    Some((_key, value)) => value,
                    None => {
                        println!("Nie ma takiego klucza");
                        0
                    }
                },
                record.stop_code,
                record.stop_name,
                record.stop_lat,
                record.stop_lon
            )),
            Err(e) => println!("{}", e),
        });
    stop
}
