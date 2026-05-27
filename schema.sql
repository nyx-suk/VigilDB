CREATE DATABASE IF NOT EXISTS fir_db;
USE fir_db;
SET FOREIGN_KEY_CHECKS=1;

DROP VIEW IF EXISTS open_firs;
DROP TABLE IF EXISTS investigation;
DROP TABLE IF EXISTS evidence;
DROP TABLE IF EXISTS accused;
DROP TABLE IF EXISTS fir;
DROP TABLE IF EXISTS complainant;
DROP TABLE IF EXISTS officer;
DROP TABLE IF EXISTS station;

CREATE TABLE station (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    jurisdiction_area VARCHAR(150),
    established_year INT
) ENGINE=InnoDB;

CREATE TABLE officer (
    officer_id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    badge_number VARCHAR(30) NOT NULL UNIQUE,
    `rank` VARCHAR(50) NOT NULL,
    contact VARCHAR(15),
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('admin','officer') DEFAULT 'officer',
    join_date DATE,
    CONSTRAINT fk_officer_station FOREIGN KEY (station_id) REFERENCES station(station_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE complainant (
    complainant_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    id_proof_type ENUM('Aadhaar', 'PAN', 'Passport', 'VoterID') NOT NULL,
    id_proof_number VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE fir (
    fir_id INT AUTO_INCREMENT PRIMARY KEY,
    complainant_id INT NOT NULL,
    officer_id INT NOT NULL,
    station_id INT NOT NULL,
    crime_type VARCHAR(150) NOT NULL,
    incident_date DATETIME NOT NULL,
    incident_location VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('Open', 'Under Investigation', 'Closed', 'Chargesheeted') NOT NULL DEFAULT 'Open',
    filing_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_fir_complainant FOREIGN KEY (complainant_id) REFERENCES complainant(complainant_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_fir_officer FOREIGN KEY (officer_id) REFERENCES officer(officer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_fir_station FOREIGN KEY (station_id) REFERENCES station(station_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE accused (
    accused_id INT AUTO_INCREMENT PRIMARY KEY,
    fir_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    dob DATE,
    address VARCHAR(255),
    contact VARCHAR(15),
    prior_record ENUM('Yes', 'No', 'Unknown') NOT NULL DEFAULT 'Unknown',
    arrest_status ENUM('At Large', 'Arrested', 'Released on Bail') NOT NULL DEFAULT 'At Large',
    CONSTRAINT fk_accused_fir FOREIGN KEY (fir_id) REFERENCES fir(fir_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE evidence (
    evidence_id INT AUTO_INCREMENT PRIMARY KEY,
    fir_id INT NOT NULL,
    collected_by INT NOT NULL,
    type ENUM('Physical', 'Digital', 'Witness Statement', 'Forensic', 'Document') NOT NULL,
    description TEXT NOT NULL,
    collected_date DATE NOT NULL,
    storage_location VARCHAR(100),
    status ENUM('Active', 'Submitted to Court', 'Disposed') NOT NULL DEFAULT 'Active',
    CONSTRAINT fk_evidence_fir FOREIGN KEY (fir_id) REFERENCES fir(fir_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_evidence_officer FOREIGN KEY (collected_by) REFERENCES officer(officer_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE investigation (
    investigation_id INT AUTO_INCREMENT PRIMARY KEY,
    fir_id INT NOT NULL,
    officer_id INT NOT NULL,
    log_date DATETIME NOT NULL,
    remarks TEXT NOT NULL,
    next_action VARCHAR(255),
    next_hearing_date DATE DEFAULT NULL,
    outcome ENUM('Pending', 'Solved', 'Unsolved', 'Referred') NOT NULL DEFAULT 'Pending',
    CONSTRAINT fk_investigation_fir FOREIGN KEY (fir_id) REFERENCES fir(fir_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_investigation_officer FOREIGN KEY (officer_id) REFERENCES officer(officer_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE VIEW open_firs AS
SELECT 
    f.fir_id,
    f.crime_type,
    f.incident_date,
    f.incident_location,
    f.status,
    f.filing_date,
    c.name AS complainant_name,
    c.phone AS complainant_phone,
    o.name AS officer_name,
    o.badge_number AS officer_badge,
    s.name AS station_name,
    s.district AS station_district
FROM fir f
JOIN complainant c ON f.complainant_id = c.complainant_id
JOIN officer o ON f.officer_id = o.officer_id
JOIN station s ON f.station_id = s.station_id
WHERE f.status IN ('Open', 'Under Investigation');

DELIMITER $$
CREATE TRIGGER fir_status_log
AFTER UPDATE ON fir
FOR EACH ROW
BEGIN
    IF NEW.status <> OLD.status THEN
        INSERT INTO investigation (
            fir_id, 
            officer_id, 
            log_date, 
            remarks, 
            next_action, 
            next_hearing_date, 
            outcome
        ) VALUES (
            NEW.fir_id, 
            NEW.officer_id, 
            NOW(), 
            CONCAT('Status changed from ', OLD.status, ' to ', NEW.status), 
            'Follow-up investigation as per status change', 
            NULL, 
            'Pending'
        );
    END IF;
END$$
DELIMITER ;
