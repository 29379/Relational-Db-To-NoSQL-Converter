use serde::Deserialize;

use std::path::Path;


#[derive(Deserialize)]
pub struct Record{
    route_id: String,
    agency_id: usize,
    route_short_name: String,
    route_long_name: String,
    route_desc: String,
    route_type: usize,
    route_type2_id: usize,
    valid_from: String,
    valid_until: String

}

pub fn get_collections(){
    let route_stop:Vec<(usize,String,usize,usize)> = Vec::new();
                    //(id, route_id, stop_id, current_stop_in_route)

    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/routes.txt");
    csv::Reader::from_path(path)
        .unwrap()
        .deserialize::<Record>()
        .for_each(|record_result| match record_result {
            Ok(record) => {
            
            },
            Err(e) => println!("{}",e),
        })


}
