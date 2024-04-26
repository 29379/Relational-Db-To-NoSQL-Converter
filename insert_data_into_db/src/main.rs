use std::collections::HashMap;

fn main() {
    let trips = include_str!("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/trips.txt");
    
    let mut headsigns: HashMap<&str,usize> = HashMap::new();
    let mut latest_key = 0;
    let mut trips_iter = trips.split("\n");

    trips_iter.next();
    trips_iter
        .for_each(|line| {
            let headsign = line
            .split(",")
            .nth(3)
            .unwrap();

            println!("{}",headsign);
            headsigns
                .entry(headsign)
                .or_insert_with(|| {
                    latest_key = latest_key + 1;
                    latest_key
                });

            });
    print!("{:?}",headsigns)
}
