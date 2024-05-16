-- ALTER TABLE Route DROP CONSTRAINT FKRoute555549;
-- ALTER TABLE Route_App_user DROP CONSTRAINT FKRoute_App_250216;
-- ALTER TABLE Route_App_user DROP CONSTRAINT FKRoute_App_73733;
-- ALTER TABLE Route_Stop DROP CONSTRAINT FKRoute_Stop727755;
-- ALTER TABLE Route_Stop DROP CONSTRAINT FKRoute_Stop627197;
-- ALTER TABLE Trip DROP CONSTRAINT FKTrip896381;
-- ALTER TABLE Trip DROP CONSTRAINT FKTrip176192;
-- ALTER TABLE Accident DROP CONSTRAINT FKAccident429604;
-- ALTER TABLE Schedule_stop_time DROP CONSTRAINT FKSchedule_s521500;
-- ALTER TABLE Report DROP CONSTRAINT FKReport668870;
-- ALTER TABLE Report DROP CONSTRAINT FKReport344463;
-- ALTER TABLE Trip DROP CONSTRAINT FKTrip238194;
-- ALTER TABLE Live_stop_time DROP CONSTRAINT FKLive_stop_851340;
-- ALTER TABLE Schedule_stop_time DROP CONSTRAINT FKSchedule_s257229;
DROP TABLE IF EXISTS Route CASCADE;
DROP TABLE IF EXISTS Vehicle CASCADE;
DROP TABLE IF EXISTS Stop CASCADE;
DROP TABLE IF EXISTS App_user CASCADE;
DROP TABLE IF EXISTS Report CASCADE;
DROP TABLE IF EXISTS Trip CASCADE;
DROP TABLE IF EXISTS Schedule_stop_time CASCADE;
DROP TABLE IF EXISTS Route_type CASCADE;
DROP TABLE IF EXISTS Accident CASCADE;
DROP TABLE IF EXISTS Live_stop_time CASCADE;
DROP TABLE IF EXISTS Trip_destination CASCADE;
DROP TABLE IF EXISTS Route_App_user CASCADE;
DROP TABLE IF EXISTS Route_Stop CASCADE;
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
  id        BIGSERIAL NOT NULL, 
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
  id             BIGSERIAL NOT NULL, 
  description    varchar(500), 
  time_of_report time(7) NOT NULL, 
  Accidentid     int8 NOT NULL, 
  App_userid     int8 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Trip (
  id                 varchar(50) NOT NULL, 
  direction_id       bool NOT NULL, 
  Routeid            varchar(50) NOT NULL, 
  Vehicleid          int8 NOT NULL, 
  Trip_destinationid int8 NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE Schedule_stop_time (
  id                       BIGSERIAL NOT NULL, 
  scheduled_arrival_time   time(7) NOT NULL, 
  scheduled_departure_time time(7) NOT NULL, 
  Stopid                   int8 NOT NULL, 
  Route_Stopid             int8 NOT NULL, 
  Route_StopRouteid        varchar(50) NOT NULL, 
  Route_StopStopid         int8 NOT NULL, 
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
  arrival_delay        time(7), 
  departure_delay      time(7), 
  Schedule_stop_timeid int8 NOT NULL UNIQUE, 
  PRIMARY KEY (id));
CREATE TABLE Trip_destination (
  id            BIGSERIAL NOT NULL, 
  trip_headsign varchar(100) NOT NULL, 
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
  Stopid             int8 NOT NULL, 
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
ALTER TABLE Trip ADD CONSTRAINT FKTrip176192 FOREIGN KEY (Vehicleid) REFERENCES Vehicle (id);
ALTER TABLE Accident ADD CONSTRAINT FKAccident429604 FOREIGN KEY (Tripid) REFERENCES Trip (id);
ALTER TABLE Schedule_stop_time ADD CONSTRAINT FKSchedule_s521500 FOREIGN KEY (Stopid) REFERENCES Stop (id);
ALTER TABLE Report ADD CONSTRAINT FKReport668870 FOREIGN KEY (Accidentid) REFERENCES Accident (id);
ALTER TABLE Report ADD CONSTRAINT FKReport344463 FOREIGN KEY (App_userid) REFERENCES App_user (id);
ALTER TABLE Trip ADD CONSTRAINT FKTrip238194 FOREIGN KEY (Trip_destinationid) REFERENCES Trip_destination (id);
ALTER TABLE Live_stop_time ADD CONSTRAINT FKLive_stop_851340 FOREIGN KEY (Schedule_stop_timeid) REFERENCES Schedule_stop_time (id);
ALTER TABLE Schedule_stop_time ADD CONSTRAINT FKSchedule_s257229 FOREIGN KEY (Route_Stopid, Route_StopRouteid, Route_StopStopid) REFERENCES Route_Stop (id, Routeid, Stopid);
