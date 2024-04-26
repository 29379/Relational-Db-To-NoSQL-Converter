CREATE TABLE Route (
  id           varchar(50) NOT NULL, 
  Route_typeid int8 NOT NULL, 
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
  Accidentid     int8 NOT NULL, 
  App_userid     int8 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Trip (
  id        varchar(50) NOT NULL, 
  Routeid   varchar(50) NOT NULL, 
  Vehicleid int8 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Schedule_stop_time (
  id                       SERIAL NOT NULL, 
  scheduled_arrival_time   time(7) NOT NULL, 
  scheduled_departure_time time(7) NOT NULL, 
  Stopid                   int4 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Route_type (
  id   BIGSERIAL NOT NULL, 
  type varchar(50) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Accident (
  id               BIGSERIAL NOT NULL, 
  time_of_accident date NOT NULL, 
  acc_latitude     numeric(19, 0) NOT NULL, 
  acc_longitude    numeric(19, 0) NOT NULL, 
  is_verified      bool NOT NULL, 
  Tripid           varchar(50) UNIQUE, 
  PRIMARY KEY (id));
CREATE TABLE Live_stop_time (
  id                   BIGSERIAL NOT NULL, 
  arrival_delay        time(7) NOT NULL, 
  departure_delay      time(7) NOT NULL, 
  Tripid               varchar(50) NOT NULL, 
  Schedule_stop_timeid int4 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Trip_destination (
  id            BIGSERIAL NOT NULL, 
  trip_headsign varchar(100) NOT NULL, 
  direction_id  bool NOT NULL, 
  Tripid        varchar(50) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Route_App_user (
  id         int8 NOT NULL, 
  Routeid    varchar(50) NOT NULL, 
  App_userid int8 NOT NULL, 
  PRIMARY KEY (id, 
  Routeid, 
  App_userid));
CREATE TABLE Route_Stop (
  id                 int8 NOT NULL, 
  Routeid            varchar(50) NOT NULL, 
  Stopid             int4 NOT NULL, 
  currentStopInRoute int4 NOT NULL, 
  PRIMARY KEY (id, 
  Routeid, 
  Stopid));
ALTER TABLE Route ADD CONSTRAINT FKRoute555549 FOREIGN KEY (Route_typeid) REFERENCES Route_type (id);
ALTER TABLE Route_App_user ADD CONSTRAINT FKRoute_App_250216 FOREIGN KEY (Routeid) REFERENCES Route (id);
ALTER TABLE Route_App_user ADD CONSTRAINT FKRoute_App_73733 FOREIGN KEY (App_userid) REFERENCES App_user (id);
ALTER TABLE Route_Stop ADD CONSTRAINT FKRoute_Stop727755 FOREIGN KEY (Routeid) REFERENCES Route (id);
ALTER TABLE Route_Stop ADD CONSTRAINT FKRoute_Stop627197 FOREIGN KEY (Stopid) REFERENCES Stop (id);
ALTER TABLE Trip ADD CONSTRAINT FKTrip896381 FOREIGN KEY (Routeid) REFERENCES Route (id);
ALTER TABLE Trip_destination ADD CONSTRAINT FKTrip_desti667765 FOREIGN KEY (Tripid) REFERENCES Trip (id);
ALTER TABLE Trip ADD CONSTRAINT FKTrip176192 FOREIGN KEY (Vehicleid) REFERENCES Vehicle (id);
ALTER TABLE Accident ADD CONSTRAINT FKAccident429604 FOREIGN KEY (Tripid) REFERENCES Trip (id);
ALTER TABLE Live_stop_time ADD CONSTRAINT FKLive_stop_667281 FOREIGN KEY (Tripid) REFERENCES Trip (id);
ALTER TABLE Live_stop_time ADD CONSTRAINT FKLive_stop_851340 FOREIGN KEY (Schedule_stop_timeid) REFERENCES Schedule_stop_time (id);
ALTER TABLE Schedule_stop_time ADD CONSTRAINT FKSchedule_s521500 FOREIGN KEY (Stopid) REFERENCES Stop (id);
ALTER TABLE Report ADD CONSTRAINT FKReport668870 FOREIGN KEY (Accidentid) REFERENCES Accident (id);
ALTER TABLE Report ADD CONSTRAINT FKReport344463 FOREIGN KEY (App_userid) REFERENCES App_user (id);
