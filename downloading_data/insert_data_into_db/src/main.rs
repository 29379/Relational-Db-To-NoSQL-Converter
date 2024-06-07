
pub mod route_stop;
pub mod route_types;
pub mod routes;
pub mod trips;

fn main() {
    //let (trip, trip_headsign) = trips::get_collections();
    //let (route_stop, schedule_stop_time) = route_stop::get_route_stop(trips::trip_vec_to_hash_map(trip.clone()));
    //route_stop.iter().for_each(|(key,value)|{
    //  println!("{},{},{},{}",value.0,key.0, key.1, value.1);
    //})
    let route_type = route_types::get_route_types();
    println!("id,type");
    route_type.iter().for_each(|entry| println!("{},{}",entry.0,entry.1));
}
