use serde::Deserialize;
use std::collections::HashMap;
use std::path::Path;

#[derive(Deserialize)]
pub struct Record {
    trip_id: String,
    arrival_time: String,
    departure_time: String,
    stop_id: usize,
    stop_sequence: u8,
    #[allow(dead_code)]
    pickup_type: usize,
    #[allow(dead_code)]
    drop_off_type: usize,
}

pub fn get_route_stop(trip: HashMap<String, (u8, String, u8, usize)>) -> (HashMap<(String, usize), (usize, u8)>, Vec<(usize, String, String, usize, usize, String)>){
    let mut route_stop: HashMap<(String, usize), (usize, u8)> = HashMap::new();
    // (route_id, stop_id), (id, current_stop_in_route)
    let mut schedule_stop_time: Vec<(usize, String, String, usize, usize, String)> = Vec::new();
    // IM NOT SURE IF ITS ALL       //id , arr, departure, stop_id, route_stop_id, trip_id

    let mut route_stop_id_counter = 0usize;
    let mut schedule_stop_time_id = 0usize;
    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/stop_times.txt");
    let mut reader = csv::Reader::from_path(path).unwrap();
    let default_var = (0u8, "0".to_string(), 0u8, 0usize);
    reader
        .deserialize::<Record>()
        .for_each(|record_result| match record_result {
            Ok(record) => {
                let route_id = &trip
                    .get(&record.trip_id)
                    .unwrap_or_else(|| {
                        println!("Nie ma takiego trip_id!!!");
                        &default_var
                    })
                    .1;

                schedule_stop_time.push((
                    {
                        schedule_stop_time_id = schedule_stop_time_id + 1;
                        schedule_stop_time_id
                    }, //id
                    record.arrival_time,
                    record.departure_time,
                    record.stop_id,
                    {
                        route_stop
                            .entry((route_id.to_string(), record.stop_id))
                            .or_insert_with(|| {
                                (
                                    {
                                        route_stop_id_counter = route_stop_id_counter + 1;
                                        route_stop_id_counter
                                    },
                                    record.stop_sequence,
                                )
                            })
                            .0
                    },
                    record.trip_id,
                ))
            }
            Err(e) => println!("Erorr {}", e),
        });
    (route_stop,schedule_stop_time)
    //   route_stop
}
