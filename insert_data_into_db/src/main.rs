fn main() {
    let trips = include_str!("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/trips.txt");
    

    let mut trips_iter = trips.split("\n");

    trips_iter.next();
    trips_iter
        .for_each(|line| {
            let headsign = line
            .split(",")
            .nth(3)
            .unwrap();

            println!("{}",headsign);

            });
}
