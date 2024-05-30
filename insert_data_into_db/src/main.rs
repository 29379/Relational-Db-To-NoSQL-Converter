use std::collections::HashMap;

pub mod trips;
pub mod routes;
pub mod route_types;
pub mod route_stop;
fn main() {
    let (trip, trip_headsign) = trips::get_collections();
    let (route_stop,schedule_stop_time) = route_stop::get_route_stop(trips::trip_vec_to_hash_map(trip));

    //route_stop.iter().for_each(|(key,value)|{
      //  println!("{},{},{},{}",value.0,key.0, key.1, value.1);
    //})

    schedule_stop_time.iter().for_each(|element| println!("{},{},{},{},{},{}", element.0, element.1, element.2, element.3, element.4, element.5));

}
