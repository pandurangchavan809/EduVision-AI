-- EduVision AI Database Schema
-- Compatible with MySQL and SQLite

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prn VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    ssc_perc REAL,
    hsc_perc REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS academic_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prn VARCHAR(20) UNIQUE NOT NULL,
    sem1_sgpa REAL,
    sem2_sgpa REAL,
    sem3_sgpa REAL,
    sem4_sgpa REAL,
    sem5_sgpa REAL,
    sem6_sgpa REAL,
    attendance_perc REAL,
    dsa_score INTEGER,
    dbms_score INTEGER,
    ml_score INTEGER,
    cn_score INTEGER,
    project_score REAL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

CREATE TABLE IF NOT EXISTS certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prn VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    issuer VARCHAR(100) NOT NULL,
    issue_date VARCHAR(20),
    status VARCHAR(50) DEFAULT 'Pending Verification',
    faculty_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

CREATE TABLE IF NOT EXISTS faculty_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prn VARCHAR(20) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    faculty_name VARCHAR(100) DEFAULT 'Prof. S. K. Deshmukh',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
