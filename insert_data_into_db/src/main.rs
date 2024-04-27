use std::path::Path;


fn main() {
    let path = Path::new("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/trips.txt");
    let path_test = Path::new("../../source_data");

    println!("{}",path_test.exists());
 //let trips = include_bytes!("../../source_data/OtwartyWroclaw_rozklad_jazdy_GTFS/trips.txt");
    let mut reader = csv::Reader::from_path(path).unwrap();

    reader.records().for_each(|record| {
        println!("{:?}",record);
    })

    
}
