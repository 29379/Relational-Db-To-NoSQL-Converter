use serde::Deserialize;

#[derive(Deserialize)]
pub struct Record {
    route_id: u8,
    route_type_name: String,
}

pub fn get_route_types() -> Vec<(u8, String)> {
    use std::path::Path;

    let mut route_types: Vec<(u8, String)> = Vec::new();
    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/route_types.txt");
    let mut reader = csv::Reader::from_path(path).unwrap();

    reader
        .deserialize::<Record>()
        .for_each(|record_result| match record_result {
            Ok(record) => {
                route_types.push((record.route_id, record.route_type_name));
            }
            Err(e) => println!("Erorr {}", e),
        });
    route_types
}
