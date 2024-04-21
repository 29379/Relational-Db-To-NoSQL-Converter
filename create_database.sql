CREATE TABLE Route (
  id            varchar(50) NOT NULL, 
  route_type_id int8 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Vehicle (
  id             BIGSERIAL NOT NULL, 
  curr_latitude  numeric(9, 6) NOT NULL, 
  curr_longitude numeric(9, 6) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Stop (
  id        SERIAL NOT NULL, 
  code      int4 NOT NULL, 
  name      varchar(255) NOT NULL, 
  latitude  numeric(9, 6) NOT NULL, 
  longitude numeric(9, 6) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE App_user (
  id            BIGSERIAL NOT NULL, 
  first_name    varchar(50) NOT NULL, 
  last_name     varchar(50) NOT NULL, 
  email         varchar(320) NOT NULL, 
  hash_password varchar(50) NOT NULL, 
  subscriber    bool NOT NULL, 
  role          varchar(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Report (
  id             SERIAL NOT NULL, 
  description    varchar(500), 
  time_of_report time(7) NOT NULL, 
  accident_id    int8 NOT NULL, 
  user_id        int8 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Trip (
  id         varchar(50) NOT NULL, 
  route_id   varchar(50) NOT NULL, 
  vehicle_id int8 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Schedule_stop_time (
  id                       SERIAL NOT NULL, 
  scheduled_arrival_time   time(7) NOT NULL, 
  scheduled_departure_time time(7) NOT NULL, 
  stop_id                  int4 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Route_type (
  id   BIGSERIAL NOT NULL, 
  type varchar(50) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Route_User (
  id       int8 NOT NULL, 
  route_id varchar(50) NOT NULL, 
  user_id  int8 NOT NULL, 
  PRIMARY KEY (id, 
  route_id, 
  user_id));
CREATE TABLE Accident (
  id               BIGSERIAL NOT NULL, 
  time_of_accident date NOT NULL, 
  acc_latitude     numeric(19, 0) NOT NULL, 
  acc_longitude    numeric(19, 0) NOT NULL, 
  is_verified      bool NOT NULL, 
  trip_id          varchar(50) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Route_Stop (
  id                 int8 NOT NULL, 
  Routeid            varchar(50) NOT NULL, 
  Stopid             int4 NOT NULL, 
  currentStopInRoute int4 NOT NULL, 
  PRIMARY KEY (id, 
  Routeid, 
  Stopid));
CREATE TABLE Live_stop_time (
  id                   BIGSERIAL NOT NULL, 
  arrival_delay        time(7) NOT NULL, 
  departure_delay      time(7) NOT NULL, 
  Schedule_stop_timeid int4 NOT NULL, 
  Tripid               varchar(50) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Trip_destination (
  id            BIGSERIAL NOT NULL, 
  trip_headsign varchar(100) NOT NULL, 
  direction_id  bool NOT NULL, 
  Tripid        varchar(50) NOT NULL, 
  PRIMARY KEY (id));
ALTER TABLE Report ADD CONSTRAINT FKReport266742 FOREIGN KEY (user_id) REFERENCES App_user (id);
ALTER TABLE Trip ADD CONSTRAINT FKTrip189169 FOREIGN KEY (route_id) REFERENCES Route (id);
ALTER TABLE Schedule_stop_time ADD CONSTRAINT FKSchedule_s655533 FOREIGN KEY (stop_id) REFERENCES Stop (id);
ALTER TABLE Trip ADD CONSTRAINT FKTrip694384 FOREIGN KEY (vehicle_id) REFERENCES Vehicle (id);
ALTER TABLE Route ADD CONSTRAINT FKRoute294582 FOREIGN KEY (route_type_id) REFERENCES Route_type (id);
ALTER TABLE Route_User ADD CONSTRAINT FKRoute_User99971 FOREIGN KEY (route_id) REFERENCES Route (id);
ALTER TABLE Route_User ADD CONSTRAINT FKRoute_User284284 FOREIGN KEY (user_id) REFERENCES App_user (id);
ALTER TABLE Report ADD CONSTRAINT FKReport31188 FOREIGN KEY (accident_id) REFERENCES Accident (id);
ALTER TABLE Accident ADD CONSTRAINT FKAccident397259 FOREIGN KEY (trip_id) REFERENCES Trip (id);
ALTER TABLE Route_Stop ADD CONSTRAINT FKRoute_Stop727755 FOREIGN KEY (Routeid) REFERENCES Route (id);
ALTER TABLE Route_Stop ADD CONSTRAINT FKRoute_Stop627197 FOREIGN KEY (Stopid) REFERENCES Stop (id);
ALTER TABLE Live_stop_time ADD CONSTRAINT FKLive_stop_851340 FOREIGN KEY (Schedule_stop_timeid) REFERENCES Schedule_stop_time (id);
ALTER TABLE Live_stop_time ADD CONSTRAINT FKLive_stop_667281 FOREIGN KEY (Tripid) REFERENCES Trip (id);
ALTER TABLE Trip_destination ADD CONSTRAINT FKTrip_desti667765 FOREIGN KEY (Tripid) REFERENCES Trip (id);
