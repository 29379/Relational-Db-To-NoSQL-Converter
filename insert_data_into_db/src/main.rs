use std::{collections::HashMap, path::Path, usize};


fn main() {
    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/trips.txt");
    let mut reader = csv::Reader::from_path(path).unwrap();
    let mut trip_heads:HashMap<&str, usize> = HashMap::new();

    reader.records().for_each(|record_result| {
        match record_result {
            Ok(record) =>{
                println!("{:?}",record.get(3).unwrap());
            },
            Err(e) => println!("{}",e),
        }
    })

    
}
