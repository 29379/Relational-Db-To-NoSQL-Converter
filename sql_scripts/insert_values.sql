-- Insert values script for testing purpose
INSERT INTO Route_type (type) VALUES
('Local'), ('Regional'), ('Express'), ('Interstate'), ('International'),
('City'), ('Suburban'), ('Rural'), ('Night'), ('Special');

INSERT INTO Vehicle (curr_latitude, curr_longitude) VALUES
(34.052235, -118.243683), (34.052236, -118.243684), (34.052237, -118.243685),
(34.052238, -118.243686), (34.052239, -118.243687), (34.052240, -118.243688),
(34.052241, -118.243689), (34.052242, -118.243690), (34.052243, -118.243691),
(34.052244, -118.243692);

INSERT INTO Stop (code, name, latitude, longitude) VALUES
(101, 'Stop 1', 34.052235, -118.243683), (102, 'Stop 2', 34.052236, -118.243684),
(103, 'Stop 3', 34.052237, -118.243685), (104, 'Stop 4', 34.052238, -118.243686),
(105, 'Stop 5', 34.052239, -118.243687), (106, 'Stop 6', 34.052240, -118.243688),
(107, 'Stop 7', 34.052241, -118.243689), (108, 'Stop 8', 34.052242, -118.243690),
(109, 'Stop 9', 34.052243, -118.243691), (110, 'Stop 10', 34.052244, -118.243692);

INSERT INTO Route (id, route_typeid) VALUES
('R001', 1), ('R002', 2), ('R003', 1), ('R004', 2), ('R005', 1),
('R006', 2), ('R007', 1), ('R008', 2), ('R009', 1), ('R010', 2);

INSERT INTO App_user (first_name, last_name, email, hash_password, subscriber, role) VALUES
('John', 'Doe', 'john.doe@example.com', 'hash1', TRUE, 'user'), 
('Jane', 'Doe', 'jane.doe@example.com', 'hash2', FALSE, 'admin'),
('Jim', 'Beam', 'jim.beam@example.com', 'hash3', TRUE, 'user'), 
('Jack', 'Daniels', 'jack.daniels@example.com', 'hash4', FALSE, 'admin'),
('Josie', 'Wales', 'josie.wales@example.com', 'hash5', TRUE, 'user'),
('Jill', 'Valentine', 'jill.valentine@example.com', 'hash6', FALSE, 'admin'),
('Jake', 'Sully', 'jake.sully@example.com', 'hash7', TRUE, 'user'), 
('Jessica', 'Jones', 'jessica.jones@example.com', 'hash8', FALSE, 'admin'),
('Jerry', 'Smith', 'jerry.smith@example.com', 'hash9', TRUE, 'user'), 
('Janet', 'Snakehole', 'janet.snakehole@example.com', 'hash10', FALSE, 'admin');

INSERT INTO Trip (id, direction_id, routeid, vehicleid) VALUES
('T001', FALSE, 'R001', 1), ('T002', FALSE, 'R002', 2), ('T003', TRUE, 'R003', 3), ('T004', TRUE, 'R004', 4), 
('T005', TRUE, 'R005', 5), ('T006', FALSE, 'R006', 6), ('T007', TRUE, 'R007', 7), ('T008', FALSE, 'R008', 8),
('T009', TRUE, 'R009', 9), ('T010', FALSE, 'R010', 10);

INSERT INTO Accident (time_of_accident, acc_latitude, acc_longitude, is_verified, tripid) VALUES
('2023-01-01', 34.052235, -118.243683, TRUE, 'T001'), ('2023-01-02', 34.052236, -118.243684, FALSE, 'T002'),
('2023-01-03', 34.052237, -118.243685, TRUE, 'T003'), ('2023-01-04', 34.052238, -118.243686, FALSE, 'T004'),
('2023-01-05', 34.052239, -118.243687, TRUE, 'T005'), ('2023-01-06', 34.052240, -118.243688, FALSE, 'T006'),
('2023-01-07', 34.052241, -118.243689, TRUE, 'T007'), ('2023-01-08', 34.052242, -118.243690, FALSE, 'T008'),
('2023-01-09', 34.052243, -118.243691, TRUE, 'T009'), ('2023-01-10', 34.052244, -118.243692, FALSE, 'T010');

INSERT INTO Report (description, time_of_report, Accidentid, App_userid) VALUES
('Minor scratch', '12:00:00', 1, 1), ('Major crash', '13:00:00', 2, 2),
('Fender bender', '14:00:00', 3, 3), ('Oil leak', '15:00:00', 4, 4),
('Tire burst', '16:00:00', 5, 5), ('Windshield crack', '17:00:00', 6, 6),
('Headlight broken', '18:00:00', 7, 7), ('Rear end collision', '19:00:00', 8, 8),
('Stolen vehicle report', '20:00:00', 9, 9), ('Vandalism', '21:00:00', 10, 10);

INSERT INTO Route_App_user (id, Routeid, App_userid) VALUES
(1, 'R001', 1), (2, 'R002', 2), (3, 'R003', 3), (4, 'R004', 4), 
(5, 'R005', 5), (6, 'R006', 6), (7, 'R007', 7), (8, 'R008', 8),
(9, 'R009', 9), (10, 'R010', 10);

INSERT INTO Schedule_stop_time (scheduled_arrival_time, scheduled_departure_time, Stopid) VALUES
('08:00:00', '08:05:00', 1), ('08:10:00', '08:15:00', 2),
('08:20:00', '08:25:00', 3), ('08:30:00', '08:35:00', 4),
('08:40:00', '08:45:00', 5), ('08:50:00', '08:55:00', 6),
('09:00:00', '09:05:00', 7), ('09:10:00', '09:15:00', 8),
('09:20:00', '09:25:00', 9), ('09:30:00', '09:35:00', 10);

INSERT INTO Live_stop_time (arrival_delay, departure_delay, Schedule_stop_timeid, Tripid) VALUES
('00:05:00', '00:10:00', 1, 'T001'), ('00:03:00', '00:07:00', 2, 'T002'),
('00:06:00', '00:09:00', 3, 'T003'), ('00:04:00', '00:08:00', 4, 'T004'),
('00:02:00', '00:05:00', 5, 'T005'), ('00:03:00', '00:07:00', 6, 'T006'),
('00:04:00', '00:06:00', 7, 'T007'), ('00:05:00', '00:10:00', 8, 'T008'),
('00:03:00', '00:07:00', 9, 'T009'), ('00:05:00', '00:08:00', 10, 'T010');

INSERT INTO Route_Stop (id, Routeid, Stopid, currentStopInRoute) VALUES
(1, 'R001', 1, 1), (2, 'R002', 2, 2), (3, 'R003', 3, 3), (4, 'R004', 4, 4),
(5, 'R005', 5, 1), (6, 'R006', 6, 2), (7, 'R007', 7, 3), (8, 'R008', 8, 4),
(9, 'R009', 9, 1), (10, 'R010', 10, 2);

INSERT INTO Trip_destination (trip_headsign, Tripid) VALUES
('Downtown', 'T001'), ('Uptown', 'T002'),
('Eastside', 'T003'), ('Westside', 'T004'),
('North End', 'T005'), ('South Corner', 'T006'),
('Central Station', 'T007'), ('City Limits', 'T008'),
('Suburb', 'T009'), ('Outer Zone', 'T010');
