INSERT INTO Route_type (id, type) VALUES
(1, 'Local'), (2, 'Regional'), (3, 'Express'), (4, 'Interstate'), (5, 'International'),
(6, 'City'), (7, 'Suburban'), (8, 'Rural'), (9, 'Night'), (10, 'Special');

INSERT INTO Vehicle (id, curr_latitude, curr_longitude) VALUES
(1,34.052235, -118.243683), (2, 34.052236, -118.243684), (3, 34.052237, -118.243685),
(4, 34.052238, -118.243686), (5, 34.052239, -118.243687), (6, 34.052240, -118.243688),
(7, 34.052241, -118.243689), (8, 34.052242, -118.243690), (9, 34.052243, -118.243691),
(10, 34.052244, -118.243692);

INSERT INTO Stop (id, code, name, latitude, longitude) VALUES
(1, 101, 'Stop 1', 34.052235, -118.243683), (2, 102, 'Stop 2', 34.052236, -118.243684),
(3, 103, 'Stop 3', 34.052237, -118.243685), (4, 104, 'Stop 4', 34.052238, -118.243686),
(5, 105, 'Stop 5', 34.052239, -118.243687), (6, 106, 'Stop 6', 34.052240, -118.243688),
(7, 107, 'Stop 7', 34.052241, -118.243689), (8, 108, 'Stop 8', 34.052242, -118.243690),
(9, 109, 'Stop 9', 34.052243, -118.243691), (10, 110, 'Stop 10', 34.052244, -118.243692);

INSERT INTO Route (id, Route_typeid) VALUES
('R001', 1), ('R002', 2), ('R003', 1), ('R004', 2), ('R005', 1),
('R006', 2), ('R007', 1), ('R008', 2), ('R009', 1), ('R010', 2);

INSERT INTO Route_Stop (id, Routeid, Stopid, currentStopInRoute) VALUES
(1, 'R001', 1, 1), (2, 'R002', 2, 2), (3, 'R003', 3, 3), (4, 'R004', 4, 4),
(5, 'R005', 5, 1), (6, 'R006', 6, 2), (7, 'R007', 7, 3), (8, 'R008', 8, 4),
(9, 'R009', 9, 1), (10, 'R010', 10, 2);

INSERT INTO App_user (id, first_name, last_name, email, hash_password, subscriber, role) VALUES
(1, 'John', 'Doe', 'john.doe@example.com', 'hash1', TRUE, 'user'), 
(2, 'Jane', 'Doe', 'jane.doe@example.com', 'hash2', FALSE, 'admin'),
(3, 'Jim', 'Beam', 'jim.beam@example.com', 'hash3', TRUE, 'user'), 
(4, 'Jack', 'Daniels', 'jack.daniels@example.com', 'hash4', FALSE, 'admin'),
(5, 'Josie', 'Wales', 'josie.wales@example.com', 'hash5', TRUE, 'user'),
(6, 'Jill', 'Valentine', 'jill.valentine@example.com', 'hash6', FALSE, 'admin'),
(7, 'Jake', 'Sully', 'jake.sully@example.com', 'hash7', TRUE, 'user'), 
(8, 'Jessica', 'Jones', 'jessica.jones@example.com', 'hash8', FALSE, 'admin'),
(9, 'Jerry', 'Smith', 'jerry.smith@example.com', 'hash9', TRUE, 'user'), 
(10, 'Janet', 'Snakehole', 'janet.snakehole@example.com', 'hash10', FALSE, 'admin');

INSERT INTO Trip_destination (id, trip_headsign) VALUES
(1, 'Downtown'), (2, 'Uptown'),
(3, 'Eastside'), (4, 'Westside'),
(5, 'North End'), (6, 'South Corner'),
(7, 'Central Station'), (8, 'City Limits'),
(9, 'Suburb'), (10, 'Outer Zone');

INSERT INTO Trip (id, direction_id, Routeid, Vehicleid, Trip_destinationid) VALUES
('T001', FALSE, 'R001', 1, 1), ('T002', FALSE, 'R002', 2, 2), 
('T003', TRUE, 'R003', 3, 3), ('T004', TRUE, 'R004', 4, 4),
('T005', TRUE, 'R005', 5, 5), ('T006', FALSE, 'R006', 6, 6), 
('T007', TRUE, 'R007', 7, 7), ('T008', FALSE, 'R008', 8, 8),
('T009', TRUE, 'R009', 9, 9), ('T010', FALSE, 'R010', 10, 10);

INSERT INTO Accident (id, time_of_accident, acc_latitude, acc_longitude, is_verified, Tripid) VALUES
(1, '2023-01-01', 34.052235, -118.243683, TRUE, 'T001'), (2, '2023-01-02', 34.052236, -118.243684, FALSE, 'T002'),
(3, '2023-01-03', 34.052237, -118.243685, TRUE, 'T003'), (4, '2023-01-04', 34.052238, -118.243686, FALSE, 'T004'),
(5, '2023-01-05', 34.052239, -118.243687, TRUE, 'T005'), (6, '2023-01-06', 34.052240, -118.243688, FALSE, 'T006'),
(7, '2023-01-07', 34.052241, -118.243689, TRUE, 'T007'), (8, '2023-01-08', 34.052242, -118.243690, FALSE, 'T008'),
(9, '2023-01-09', 34.052243, -118.243691, TRUE, 'T009'), (10, '2023-01-10', 34.052244, -118.243692, FALSE, 'T010');

INSERT INTO Report (id, description, time_of_report, Accidentid, App_userid) VALUES
(1, 'Minor scratch', '12:00:00', 1, 1), (2, 'Major crash', '13:00:00', 2, 2),
(3, 'Fender bender', '14:00:00', 3, 3), (4, 'Oil leak', '15:00:00', 4, 4),
(5, 'Tire burst', '16:00:00', 5, 5), (6, 'Windshield crack', '17:00:00', 6, 6),
(7, 'Headlight broken', '18:00:00', 7, 7), (8, 'Rear end collision', '19:00:00', 8, 8),
(9, 'Stolen vehicle report', '20:00:00', 9, 9), (10, 'Vandalism', '21:00:00', 10, 10);

INSERT INTO Schedule_stop_time (id, scheduled_arrival_time, scheduled_departure_time, Route_Stopid, Route_StopRouteid, Route_StopStopid) VALUES
(1, '08:00:00', '08:05:00', 1, 'R001', 1), (2, '08:10:00', '08:15:00', 2, 'R002', 2),
(3, '08:20:00', '08:25:00', 3, 'R003', 3), (4, '08:30:00', '08:35:00', 4, 'R004', 4),
(5, '08:40:00', '08:45:00', 5, 'R005', 5), (6, '08:50:00', '08:55:00', 6, 'R006', 6),
(7, '09:00:00', '09:05:00', 7, 'R007', 7), (8, '09:10:00', '09:15:00', 8, 'R008', 8),
(9, '09:20:00', '09:25:00', 9, 'R009', 9), (10, '09:30:00', '09:35:00', 10, 'R010', 10);

INSERT INTO Live_stop_time (id, arrival_delay, departure_delay, Schedule_stop_timeid) VALUES
(1, '00:05:00', '00:10:00', 1), (2, '00:03:00', '00:07:00', 2),
(3, '00:06:00', '00:09:00', 3), (4, '00:04:00', '00:08:00', 4),
(5, '00:02:00', '00:05:00', 5), (6, '00:03:00', '00:07:00', 6),
(7, '00:04:00', '00:06:00', 7), (8, '00:05:00', '00:10:00', 8),
(9, '00:03:00', '00:07:00', 9), (10, '00:05:00', '00:08:00', 10);

INSERT INTO Route_App_user (id, Routeid, App_userid) VALUES
(1, 'R001', 1), (2, 'R002', 2), (3, 'R003', 3), (4, 'R004', 4), 
(5, 'R005', 5), (6, 'R006', 6), (7, 'R007', 7), (8, 'R008', 8),
(9, 'R009', 9), (10, 'R010', 10);