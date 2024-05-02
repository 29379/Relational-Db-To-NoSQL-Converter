use std::collections::HashMap;

pub mod trips;
pub mod stop;
pub mod routes;

fn main() {
    //trips::print_collection();
    println!("{:?}",stop::get_stop_id())
}
