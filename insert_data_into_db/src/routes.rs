pub struct Test {}

pub fn print_collection() {
    use crate::HashMap;
    use std::path::Path;

    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/trips.txt");
    let mut reader = csv::Reader::from_path(path).unwrap();
    let mut trip_heads: HashMap<String, (usize, usize)> = HashMap::new();
    // HashMap< Trip_heasign, (id, direction_id)>

    let mut trip_heads_count = 0;

    reader
        .records()
        .for_each(|record_result| match record_result {
            Ok(record) => {
                trip_heads
                    .entry(record.get(3).unwrap().to_string())
                    .or_insert_with(|| {
                        let count: usize = {
                            trip_heads_count = trip_heads_count + 1;
                            trip_heads_count
                        };
                        (count, record.get(4).unwrap().parse::<usize>().unwrap())
                    });
            }
            Err(e) => println!("{}", e),
        });
    print!("Collection : {:?}", trip_heads);
}
