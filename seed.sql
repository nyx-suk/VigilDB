USE fir_db;

SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE investigation;
TRUNCATE TABLE evidence;
TRUNCATE TABLE accused;
TRUNCATE TABLE fir;
TRUNCATE TABLE complainant;
TRUNCATE TABLE officer;
TRUNCATE TABLE station;
SET FOREIGN_KEY_CHECKS=1;

-- 1. Populate 'station' (7 rows)
INSERT INTO station (station_id, name, district, address, phone, jurisdiction_area, established_year)
VALUES
(1, 'Cubbon Park PS', 'Bengaluru Urban', 'Kasturba Rd, Shantala Nagar, Ashok Nagar, Bengaluru, Karnataka 560001', '+918022942581', 'Cubbon Park and surrounding areas', 1982),
(2, 'Yelahanka PS', 'Bengaluru Urban', 'BB Road, Yelahanka, Bengaluru, Karnataka 560064', '+918022942582', 'Yelahanka Old Town, Yelahanka New Town', 1995),
(3, 'Jayanagar PS', 'Bengaluru Urban', '4th Block, Jayanagar, Bengaluru, Karnataka 560011', '+918022942583', 'Jayanagar 1st to 9th Blocks', 1990),
(4, 'Koramangala PS', 'Bengaluru Urban', '80 Feet Road, 6th Block, Koramangala, Bengaluru, Karnataka 560095', '+918022942584', 'Koramangala 1st to 8th Blocks', 1985),
(5, 'Whitefield PS', 'Bengaluru Urban', 'Whitefield Main Rd, Inner Circle, Whitefield, Bengaluru, Karnataka 560066', '+918022942585', 'Whitefield, ITPL, Kadugodi', 2002),
(6, 'Belagavi Town PS', 'Belagavi', 'Khade Bazar, Belagavi, Karnataka 590001', '+918312405233', 'Belagavi market and city center', 1988),
(7, 'Mysuru City PS', 'Mysuru', 'Devaraja Double Rd, Devaraja Mohalla, Mysuru, Karnataka 570001', '+918212418100', 'Mysuru Palace and surrounding business district', 2008);

-- 2. Populate 'officer' (8 rows)
INSERT INTO officer (officer_id, station_id, name, badge_number, `rank`, contact, email, join_date)
VALUES
(1, 1, 'Karthik Gowda', 'KA-001', 'Inspector', '9845012341', 'karthik.gowda@karnatakapolice.gov.in', '2008-04-12'),
(2, 2, 'Manjunath Patil', 'KA-002', 'SI', '9845012342', 'manjunath.patil@karnatakapolice.gov.in', '2012-08-19'),
(3, 3, 'Ravi Shankar', 'KA-003', 'ASI', '9845012343', 'ravi.shankar@karnatakapolice.gov.in', '2010-11-05'),
(4, 4, 'Priya Shenoy', 'KA-004', 'DSP', '9845012344', 'priya.shadow@karnatakapolice.gov.in', '2005-02-14'),
(5, 5, 'Srinivas Rao', 'KA-005', 'Head Constable', '9845012345', 'srinivas.rao@karnatakapolice.gov.in', '2015-05-20'),
(6, 6, 'Basavaraj Bommai', 'KA-006', 'Constable', '9845012346', 'basavaraj.b@karnatakapolice.gov.in', '2020-09-01'),
(7, 7, 'Vijay Raghavendra', 'KA-007', 'Inspector', '9845012347', 'vijay.r@karnatakapolice.gov.in', '2011-03-25'),
(8, 1, 'Anusha Hegde', 'KA-008', 'SI', '9845012348', 'anusha.hegde@karnatakapolice.gov.in', '2018-07-30');

UPDATE officer SET password_hash = SHA2('password123', 256), role = 'admin'  WHERE badge_number = 'KA-001';
UPDATE officer SET password_hash = SHA2('password123', 256), role = 'officer' WHERE badge_number != 'KA-001';

-- 3. Populate 'complainant' (8 rows)
INSERT INTO complainant (complainant_id, name, phone, address, dob, id_proof_type, id_proof_number)
VALUES
(1, 'Rahul Dravid', '9880011111', '12, 3rd Main, Indiranagar, Bengaluru', '1973-01-11', 'Passport', 'Z1122334'),
(2, 'Sudha Murthy', '9880022222', 'Flat 101, Heritage Apts, Jayanagar, Bengaluru', '1950-08-19', 'Aadhaar', '123456789012'),
(3, 'Anil Kumble', '9880033333', '234, 5th Cross, Sadashivashnagar, Bengaluru', '1970-10-17', 'PAN', 'ABCDE1234A'),
(4, 'Ramesh Aravind', '9880044444', '45, Orchid Meadows, Whitefield, Bengaluru', '1964-09-10', 'VoterID', 'KA03123456'),
(5, 'Puneeth Rajkumar', '9880055555', 'House 7, Sadashivanagar, Bengaluru', '1975-03-17', 'Aadhaar', '987654321098'),
(6, 'Shreya Ghoshal', '9880066666', 'A-501, Prestige Lakeside, Mysuru', '1984-03-12', 'Passport', 'K5566778'),
(7, 'Devi Prasad', '9880077777', '15, Palace Road, Mysuru', '1979-05-24', 'PAN', 'XYZP9876Q'),
(8, 'Meera Jaswanth', '9880088888', '32, 2nd Cross, Malleshwaram, Bengaluru', '1992-11-08', 'VoterID', 'KA04765432');

-- 4. Populate 'fir' (8 rows)
INSERT INTO fir (fir_id, complainant_id, officer_id, station_id, crime_type, incident_date, incident_location, description, status, filing_date)
VALUES
(1, 1, 1, 1, 'IPC 302 - Murder', '2023-08-15 22:30:00', 'Near Lalbagh Gate, Bengaluru', 'Victim assaulted with a blunt object behind Lalbagh Gate; declared dead upon arrival at hospital.', 'Under Investigation', '2023-08-15 23:45:00'),
(2, 2, 2, 2, 'IPC 379 - Theft', '2023-10-05 14:15:00', 'Yelahanka New Town Bus Stand, Bengaluru', 'Gold chain snatched from complainant\'s neck by two unidentified riders on a motorcycle.', 'Open', '2023-10-05 15:30:00'),
(3, 3, 3, 3, 'IPC 376 - Sexual Assault', '2023-12-01 23:00:00', 'Dark alley near Jayanagar 4th Block, Bengaluru', 'Assault and harassment of a working professional returning home; physical evidence collected.', 'Under Investigation', '2023-12-02 01:15:00'),
(4, 4, 4, 4, 'IPC 420 - Fraud', '2024-01-20 11:00:00', 'Koramangala 3rd Block, Bengaluru', 'Online phishing scam where complainant was duped of INR 10 Lakhs using spoofed bank caller ID.', 'Closed', '2024-01-20 14:30:00'),
(5, 5, 5, 5, 'IPC 498A - Domestic Violence', '2024-03-14 09:00:00', 'Whitefield Prestige Apartments, Bengaluru', 'Harassment and demand for dowry by husband and in-laws, leading to physical abuse.', 'Chargesheeted', '2024-03-14 11:00:00'),
(6, 6, 6, 6, 'IPC 363 - Kidnapping', '2024-04-18 16:30:00', 'Outside Government School, Belagavi', 'A 10-year-old child reported missing; CCTV shows a red hatchback taking the child away.', 'Open', '2024-04-18 18:00:00'),
(7, 7, 7, 7, 'IPC 307 - Attempt to Murder', '2024-05-02 21:45:00', 'Near Mysuru Palace North Gate, Mysuru', 'Street altercation escalated into stab wounds inflicted on the victim with a pocket knife.', 'Closed', '2024-05-02 23:00:00'),
(8, 8, 8, 1, 'IPC 406 - Criminal Breach of Trust', '2024-02-28 15:00:00', 'Cubbon Park Road, Bengaluru', 'Business partner embezzled company funds amounting to INR 25 Lakhs through unauthorized self-transfers.', 'Chargesheeted', '2024-02-28 17:30:00');

-- 5. Populate 'accused' (8 rows)
INSERT INTO accused (accused_id, fir_id, name, dob, address, contact, prior_record, arrest_status)
VALUES
(1, 1, 'Kiran Kumar alias Kulla', '1990-05-15', 'Slums near Kalasipalya, Bengaluru', '9844098761', 'Yes', 'Arrested'),
(2, 2, 'Ramesh Babu', '1995-11-20', 'Neelasandra, Bengaluru', '9844098762', 'No', 'At Large'),
(3, 3, 'Satish Reddy', '1988-03-10', 'HSR Layout, Bengaluru', '9844098763', 'Yes', 'Arrested'),
(4, 4, 'Sanjay Dutt', '1982-08-14', 'Cyber Cell investigation ongoing', NULL, 'Unknown', 'At Large'),
(5, 5, 'Dinesh Karthik', '1986-06-01', 'Prestige Apartments, Whitefield, Bengaluru', '9844098765', 'No', 'Released on Bail'),
(6, 6, 'Guru Prasad', '1993-12-25', 'Khasbag, Belagavi', '9844098766', 'Yes', 'At Large'),
(7, 7, 'Nikhil Gowda', '1997-04-18', 'Mysuru Outer Ring Road, Mysuru', '9844098767', 'No', 'Released on Bail'),
(8, 8, 'Vikram Aditya', '1979-07-02', 'Jayanagar 9th Block, Bengaluru', '9844098768', 'Unknown', 'Arrested');

-- 6. Populate 'evidence' (8 rows)
INSERT INTO evidence (evidence_id, fir_id, collected_by, type, description, collected_date, storage_location, status)
VALUES
(1, 1, 1, 'Physical', 'Blood-stained cricket bat recovered from the bushes near Lalbagh Gate.', '2023-08-16', 'Cubbon Park PS Locker Room A', 'Active'),
(2, 2, 2, 'Digital', 'CCTV footage from Yelahanka main road traffic signal showing the suspect vehicle.', '2023-10-06', 'Secure Server Rack B', 'Active'),
(3, 3, 3, 'Forensic', 'DNA swabs and fingernail scrapings of the suspect recovered from victim clothes.', '2023-12-02', 'State Forensic Laboratory, Bengaluru', 'Active'),
(4, 4, 4, 'Document', 'Bank statements showing transfer of INR 10 Lakhs to the fraudulent shell account.', '2024-01-22', 'Cyber Crime Vault 1', 'Submitted to Court'),
(5, 5, 5, 'Witness Statement', 'Signed witness statement of neighbor who heard altercation and shouting.', '2024-03-15', 'Whitefield PS Case File Box 2', 'Submitted to Court'),
(6, 6, 6, 'Digital', 'Kidnapping ransom call recording obtained from complainant\'s phone tapping.', '2024-04-19', 'Digital Evidence Locker D', 'Active'),
(7, 7, 7, 'Physical', 'Blood-stained pocket knife with 4-inch blade recovered from the spot.', '2024-05-03', 'Mysuru PS Safe Box 4', 'Disposed'),
(8, 8, 8, 'Document', 'Audit ledger showing forged signatures on company checkbook registers.', '2024-03-01', 'Cubbon Park PS Filing Cabinet C1', 'Active');

-- 7. Populate 'investigation' (8 rows)
INSERT INTO investigation (investigation_id, fir_id, officer_id, log_date, remarks, next_action, next_hearing_date, outcome)
VALUES
(1, 1, 1, '2023-08-16 10:30:00', 'Primary suspect Kiran Kumar apprehended. Underwent interrogation.', 'Await forensic report on recovered bat', '2023-09-15', 'Pending'),
(2, 2, 2, '2023-10-07 11:00:00', 'Informants deployed in local market area to identify the motorcycle license plate.', 'Conduct local area patrolling and surveillance', NULL, 'Pending'),
(3, 3, 3, '2023-12-03 14:00:00', 'Forensic DNA matching completed successfully with the accused Satish Reddy.', 'File preliminary chargesheet in court', '2024-01-10', 'Pending'),
(4, 4, 4, '2024-01-25 16:00:00', 'Scam funds traced to a mule account. Funds frozen and full amount recovered.', 'Case closed and final report submitted', NULL, 'Solved'),
(5, 5, 5, '2024-03-20 12:30:00', 'Accused husband surrendered under court pressure. Released on bail.', 'Prepare final chargesheet under 498A', NULL, 'Solved'),
(6, 6, 6, '2024-04-20 09:30:00', 'CCTV footage tracked red hatchback to Outer Ring Road toll plaza.', 'Dispatch recovery team to coordinated location', NULL, 'Pending'),
(7, 7, 7, '2024-05-05 15:00:00', 'Altercation resolved outside court with written apology and medical expense compensation.', 'Submit case compromise petition to magistrate', NULL, 'Solved'),
(8, 8, 8, '2024-03-05 10:00:00', 'Audit reports confirmed self-transfers by business partner. Fraud verified.', 'Submit formal chargesheet for IPC 406', '2024-04-20', 'Solved');
