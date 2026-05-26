USE fir_db;

-- 1. Populate 'station' (7 rows)
INSERT INTO station (station_id, name, district, address, phone, jurisdiction_area, established_year)
VALUES
(1, 'Koramangala Police Station', 'Bangalore Urban', '80 Feet Road, 6th Block, Koramangala, Bengaluru, Karnataka 560095', '+918022942586', 'Koramangala 1st to 8th Blocks', 1985),
(2, 'Shivaji Nagar Police Station', 'Pune', 'Shivajinagar, Pune, Maharashtra 411005', '+912025501122', 'Shivajinagar, FC Road, JM Road', 1972),
(3, 'Bandra Police Station', 'Mumbai Suburban', 'Hill Road, Bandra West, Mumbai, Maharashtra 400050', '+912226421555', 'Bandra West, Khar, Pali Hill', 1960),
(4, 'Indiranagar Police Station', 'Bangalore Urban', '100 Feet Road, Indiranagar, Bengaluru, Karnataka 560038', '+918022942589', 'Indiranagar, HAL 2nd Stage, Domlur', 1999),
(5, 'Andheri Police Station', 'Mumbai Suburban', 'S.V. Road, Andheri West, Mumbai, Maharashtra 400058', '+912226282345', 'Andheri West, Versova, Lokhandwala', 1980),
(6, 'Jayanagar Police Station', 'Bangalore Urban', '4th Block, Jayanagar, Bengaluru, Karnataka 560011', '+918022942582', 'Jayanagar 1st to 9th Blocks', 1990),
(7, 'Sadashiv Peth Police Station', 'Pune', 'Sadashiv Peth, Pune, Maharashtra 411030', '+912024451133', 'Sadashiv Peth, Alka Talkies Chowk', 1995);

-- 2. Populate 'officer' (7 rows)
INSERT INTO officer (officer_id, station_id, name, badge_number, `rank`, contact, email, join_date)
VALUES
(1, 1, 'Inspector Rajesh Kumar', 'KA-KA101', 'Inspector', '9845012345', 'rajesh.kumar@karnatakapolice.gov.in', '2010-06-15'),
(2, 2, 'Sub-Inspector Amit Patil', 'MH-PN202', 'Sub-Inspector', '9822098765', 'amit.patil@mahapolice.gov.in', '2015-08-01'),
(3, 3, 'Assistant Inspector Sachin Kadam', 'MH-MB303', 'Assistant Police Inspector', '9819076543', 'sachin.kadam@mahapolice.gov.in', '2012-04-10'),
(4, 4, 'Inspector Sunita Deshmukh', 'KA-KA104', 'Inspector', '9900012345', 'sunita.d@karnatakapolice.gov.in', '2008-11-20'),
(5, 5, 'Sub-Inspector Vijay Salaskar', 'MH-MB305', 'Sub-Inspector', '9867012345', 'vijay.salaskar@mahapolice.gov.in', '2018-02-14'),
(6, 6, 'Inspector Anil Kumble', 'KA-KA106', 'Inspector', '9448098765', 'anil.kumble@karnatakapolice.gov.in', '2005-05-05'),
(7, 7, 'Sub-Inspector Priya Sharma', 'MH-PN207', 'Sub-Inspector', '9503012345', 'priya.sharma@mahapolice.gov.in', '2020-01-10');

-- 3. Populate 'complainant' (7 rows)
INSERT INTO complainant (complainant_id, name, phone, address, dob, id_proof_type, id_proof_number)
VALUES
(1, 'Aarav Mehta', '9833012345', 'A-404, Sea Breeze Apartments, Bandra West, Mumbai', '1988-04-12', 'Aadhaar', '987654321012'),
(2, 'Neha Kulkarni', '9823098765', 'Flat 12, Swapnali Residency, Sadashiv Peth, Pune', '1995-10-22', 'PAN', 'ABCDE1234F'),
(3, 'Rohan Murthy', '9901054321', '102, Maple Woods, Koramangala 3rd Block, Bengaluru', '1991-07-05', 'Passport', 'Z1234567'),
(4, 'Priya Nair', '9880012345', '45, 2nd Main, Indiranagar, Bengaluru', '1993-01-30', 'VoterID', 'XYZ9876543'),
(5, 'Aditya Joshi', '9892012345', 'Flat 8B, Gokul Dham, Andheri West, Mumbai', '1985-09-18', 'Aadhaar', '112233445566'),
(6, 'Sneha Gawde', '9702098765', 'House No. 89, Shivaji Nagar, Pune', '1990-12-05', 'PAN', 'EFGHI5678J'),
(7, 'Vikram Shenoy', '9449012345', '304, 5th Cross, Jayanagar 4th Block, Bengaluru', '1980-03-25', 'Aadhaar', '778899001122');

-- 4. Populate 'fir' (7 rows)
INSERT INTO fir (fir_id, complainant_id, officer_id, station_id, crime_type, incident_date, incident_location, description, status, filing_date)
VALUES
(1, 1, 3, 3, 'IPC 379 - Theft', '2026-05-10 14:30:00', 'Bandra Carter Road Promenade', 'Complainants mobile phone and wallet snatched by two motorcycle-borne riders.', 'Open', '2026-05-10 16:00:00'),
(2, 2, 7, 7, 'IPC 302 - Murder', '2026-05-12 23:15:00', 'Sadashiv Peth Lane 3 near temple', 'A shopkeeper was assaulted with a sharp weapon, resulting in his death.', 'Under Investigation', '2026-05-13 01:30:00'),
(3, 3, 1, 1, 'IPC 420 - Cheating', '2026-05-01 10:00:00', 'Online Banking / Koramangala', 'Complainant was duped of INR 5 Lakhs via a phishing phone call impersonating bank officials.', 'Closed', '2026-05-05 11:15:00'),
(4, 4, 4, 4, 'IPC 392 - Robbery', '2026-05-15 20:45:00', 'Indiranagar 12th Main Road', 'Two suspects intercepted complainant and robbed gold chain at knifepoint.', 'Chargesheeted', '2026-05-15 22:00:00'),
(5, 5, 5, 5, 'IPC 354 - Assault on Woman', '2026-05-18 22:00:00', 'Andheri West Metro Station Exit', 'Verbal harassment and physical assault on complainant by a known suspect while returning home.', 'Under Investigation', '2026-05-19 09:30:00'),
(6, 6, 2, 2, 'IPC 384 - Extortion', '2026-05-20 11:00:00', 'Shivaji Nagar Market Area', 'Local goons demanded haftah weekly payment from shop owners and threatened violence.', 'Open', '2026-05-20 14:00:00'),
(7, 7, 6, 6, 'IPC 279 - Rash Driving', '2026-05-22 17:30:00', 'Jayanagar 4th Block Signal', 'An overspeeding SUV rammed into complainant\'s parked sedan, causing massive damage.', 'Closed', '2026-05-22 18:30:00');

-- 5. Populate 'accused' (7 rows)
INSERT INTO accused (accused_id, fir_id, name, dob, address, contact, prior_record, arrest_status)
VALUES
(1, 1, 'Ramesh Shinde', '1998-02-14', 'Slums near Bandra Reclamation, Mumbai', '9819998877', 'Yes', 'At Large'),
(2, 2, 'Suresh Patil', '1990-08-20', 'Pune Cantonment Area, Pune', '9822334455', 'Yes', 'Arrested'),
(3, 3, 'Vicky Malhotra', '1992-12-05', 'Unknown / Cyber Cell Tracing Required', NULL, 'Unknown', 'At Large'),
(4, 4, 'Jagdish Tiwari', '1995-05-16', 'Koramangala Transit Camp, Bengaluru', '9900112233', 'No', 'Arrested'),
(5, 5, 'Sameer Deshmukh', '1987-11-03', 'Andheri East, Mumbai', '9867112233', 'No', 'Released on Bail'),
(6, 6, 'Kiran Balu Thorat', '1993-04-22', 'Shivaji Nagar, Pune', '9503445566', 'Yes', 'Arrested'),
(7, 7, 'Rahul Gupte', '2001-09-09', 'JP Nagar 2nd Phase, Bengaluru', '9448332211', 'No', 'Released on Bail');

-- 6. Populate 'evidence' (7 rows)
INSERT INTO evidence (evidence_id, fir_id, collected_by, type, description, collected_date, storage_location, status)
VALUES
(1, 1, 3, 'Digital', 'CCTV Footage from Carter Road coffee shop showing suspects vehicle plate.', '2026-05-11', 'Locker Room A, Bandra PS', 'Active'),
(2, 2, 7, 'Forensic', 'Fingerprints and blood samples extracted from the crime scene weapon.', '2026-05-13', 'State Forensic Lab, Pune', 'Active'),
(3, 3, 1, 'Document', 'Bank account statements and call records log of fraudulent transaction.', '2026-05-06', 'Cyber Cell File Cabinet B3', 'Submitted to Court'),
(4, 4, 4, 'Physical', 'Serrated steel knife recovered from the arrest site of the suspect.', '2026-05-16', 'Evidence Vault, Indiranagar PS', 'Active'),
(5, 5, 5, 'Witness Statement', 'Written and signed witness statement of the security guard present at metro exit.', '2026-05-19', 'Case File 354/2026', 'Active'),
(6, 6, 2, 'Digital', 'Audio recording of the extortion threat received on the complainant\'s mobile.', '2026-05-21', 'Secured Server, Shivaji Nagar PS', 'Active'),
(7, 7, 6, 'Physical', 'Paint scrapings and dashboard camera video showing SUV license plate.', '2026-05-22', 'Evidence Vault, Jayanagar PS', 'Disposed');

-- 7. Populate 'investigation' (7 rows)
INSERT INTO investigation (investigation_id, fir_id, officer_id, log_date, remarks, next_action, next_hearing_date, outcome)
VALUES
(1, 1, 3, '2026-05-11 10:00:00', 'Preliminary site inspection completed. Informants alerted in the area.', 'Analyze CCTV footage', '2026-06-05', 'Pending'),
(2, 2, 7, '2026-05-13 14:00:00', 'Autopsy report received. Cause of death confirmed as sharp weapon injuries.', 'Interrogate suspect Suresh Patil', '2026-06-10', 'Pending'),
(3, 3, 1, '2026-05-08 16:30:00', 'Funds trace led to dummy account in another state. Account frozen. Recovery process completed.', 'File closure report', '2026-05-15', 'Solved'),
(4, 4, 4, '2026-05-17 11:00:00', 'Stolen gold chain recovered from local pawn broker who identified the suspect.', 'Prepare chargesheet for submission', '2026-06-20', 'Solved'),
(5, 5, 5, '2026-05-20 12:00:00', 'Suspect surrendered and was released on bail by court order. Statement recorded.', 'File final chargesheet', '2026-07-01', 'Pending'),
(6, 6, 2, '2026-05-22 09:30:00', 'Suspect Kiran Thorat arrested. Admitted to intimidation and named accomplice.', 'Apprehend the accomplice', '2026-06-12', 'Pending'),
(7, 7, 6, '2026-05-23 15:00:00', 'Accused paid full compensation to complainant for damages. Matter settled out of court.', 'Case closed formally', '2026-05-24', 'Solved');
