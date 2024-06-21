
pub mod route_stop;
pub mod route_types;
pub mod routes;
pub mod trips;

fn main() {
    let (trip, trip_headsign) = trips::get_collections();
    let route = routes::get_route();

    //print Trip
    println!("id,direction_id,route_id,vechicle_id,trip_destination");
    trip.iter().for_each(|entry| {
        println!("{},{},{},{}",entry.0, entry.1,entry.2,entry.3);
    });

    //Print trip_destination
    println!("id,trip_headsign");
    trip_headsign.iter().for_each(|entry| {
        println!("{},{}",entry.1,entry.0);
    });


    // Print route_stop
    println!("id,route_id,stop_id,current_stop_in_route");
    let (route_stop, schedule_stop_time) = route_stop::get_route_stop(trips::trip_vec_to_hash_map(trip.clone()));
    route_stop.iter().for_each(|(key,value)|{
     println!("{},{},{},{}",value.0,key.0, key.1, value.1);
    });
    
    // Print schedule_stop_time
    println!("id,route_id,stop_id,current_stop_in_route");
 //   let (route_stop, schedule_stop_time) = route_stop::get_route_stop(trips::trip_vec_to_hash_map(trip.clone()));
   // trip.iter().for_each(|entry| {
     //   println!("{},{},{},{}",entry.0, entry.1,entry.2,entry.3);
 //   });

    // Print route
    println!("id, route_type");
    route.iter().for_each(|entry| {
        println!("{},{}",entry.0,entry.1);
    });


    //Print route_type
    let route_type = route_types::get_route_types();
    println!("id,type");
    route_type.iter().for_each(|entry| println!("{},{}",entry.0,entry.1));
}
