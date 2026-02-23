-- ============================================================
-- EduVision Database Schema
-- Student Academic Performance and Skills Management System
-- ============================================================

-- ============================================================
-- 1. STUDENT MASTER TABLE
-- ============================================================
CREATE TABLE students (
    prn VARCHAR(12) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- ============================================================
-- 2. 12TH GRADE MARKS
-- ============================================================
CREATE TABLE marks_12th (
    prn VARCHAR(12) PRIMARY KEY,
    physics INT NOT NULL,
    chemistry INT NOT NULL,
    mathematics INT NOT NULL,
    english INT NOT NULL,
    computer_science INT NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

-- ============================================================
-- 3. SEMESTER GRADES (SEM1 - SEM6)
-- ============================================================
CREATE TABLE sem1 (
    prn VARCHAR(12) PRIMARY KEY,
    systems_mechanical_engineering INT NOT NULL,
    basic_electrical_engineering INT NOT NULL,
    engineering_mathematics_1 INT NOT NULL,
    engineering_chemistry INT NOT NULL,
    programming_problem_solving INT NOT NULL,
    sgpa DECIMAL(3,2) NOT NULL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

CREATE TABLE sem2 (
    prn VARCHAR(12) PRIMARY KEY,
    engineering_mechanics INT NOT NULL,
    engineering_graphics INT NOT NULL,
    basic_electronics_engineering INT NOT NULL,
    engineering_physics INT NOT NULL,
    engineering_mathematics_2 INT NOT NULL,
    sgpa DECIMAL(3,2) NOT NULL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

CREATE TABLE sem3 (
    prn VARCHAR(12) PRIMARY KEY,
    discrete_mathematics INT NOT NULL,
    data_structures INT NOT NULL,
    object_oriented_programming INT NOT NULL,
    computer_graphics INT NOT NULL,
    operating_systems INT NOT NULL,
    sgpa DECIMAL(3,2) NOT NULL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

CREATE TABLE sem4 (
    prn VARCHAR(12) PRIMARY KEY,
    data_structures_algorithms INT NOT NULL,
    software_engineering INT NOT NULL,
    statistics INT NOT NULL,
    internet_of_things INT NOT NULL,
    management_information_system INT NOT NULL,
    sgpa DECIMAL(3,2) NOT NULL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

CREATE TABLE sem5 (
    prn VARCHAR(12) PRIMARY KEY,
    artificial_intelligence INT NOT NULL,
    database_management_systems INT NOT NULL,
    web_technology INT NOT NULL,
    pattern_recognition INT NOT NULL,
    computer_networks INT NOT NULL,
    sgpa DECIMAL(3,2) NOT NULL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

CREATE TABLE sem6 (
    prn VARCHAR(12) PRIMARY KEY,
    cyber_security INT NOT NULL,
    data_science INT NOT NULL,
    artificial_neural_networks INT NOT NULL,
    cloud_computing INT NOT NULL,
    sgpa DECIMAL(3,2) NOT NULL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);
-- ============================================================
-- 4. STUDENT SKILLS
-- ============================================================
CREATE TABLE student_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prn VARCHAR(12) NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (prn) REFERENCES students(prn)
);

-- ============================================================
-- DATA INSERTION
-- ============================================================

-- Insert Student Records
INSERT INTO students VALUES
('72309101A', 'Ayaan Mehta'),
('72309102B', 'Ishika Rao'),
('72309103C', 'Rudra Sharma'),
('72309104D', 'Zoya Khan'),
('72309105E', 'Vivaan Patil'),
('72309106F', 'Anvi Nair'),
('72309107G', 'Kabir Singh'),
('72309108H', 'Meher Joshi'),
('72309109J', 'Dev Malviya'),
('72309110K', 'Tanya Kapoor'),
('72309111L', 'Arnav Das'),
('72309112M', 'Sara Thomas'),
('72309113N', 'Yuvraj Kulkarni'),
('72309114P', 'Ritika Iyer'),
('72309115Q', 'Harsh Verma'),
('72309116R', 'Manya Bhatia'),
('72309117S', 'Neil Gupta'),
('72309118T', 'Kavya Sethi'),
('72309119U', 'Rehan Ali'),
('72309120V', 'Simran Gill');

-- Insert 12th Grade Marks
INSERT INTO marks_12th VALUES
('72309101A', 78, 81, 75, 80, 82, 79.2),
('72309102B', 88, 84, 90, 86, 91, 87.8),
('72309103C', 67, 72, 70, 74, 69, 70.4),
('72309104D', 92, 89, 94, 90, 93, 91.6),
('72309105E', 74, 70, 72, 76, 71, 72.6),
('72309106F', 85, 87, 83, 88, 86, 85.8),
('72309107G', 69, 65, 68, 70, 67, 67.8),
('72309108H', 90, 92, 88, 91, 89, 90.0),
('72309109J', 76, 79, 74, 78, 80, 77.4),
('72309110K', 82, 85, 84, 83, 86, 84.0),
('72309111L', 71, 73, 69, 72, 74, 71.8),
('72309112M', 95, 93, 96, 94, 97, 95.0),
('72309113N', 64, 66, 68, 65, 67, 66.0),
('72309114P', 87, 89, 85, 88, 90, 87.8),
('72309115Q', 77, 75, 79, 76, 78, 77.0),
('72309116R', 83, 81, 82, 84, 80, 82.0),
('72309117S', 68, 70, 72, 69, 71, 70.0),
('72309118T', 91, 90, 89, 92, 93, 91.0),
('72309119U', 73, 74, 76, 72, 75, 74.0),
('72309120V', 86, 88, 87, 85, 89, 87.0);

-- Insert Semester 1 Grades
INSERT INTO sem1 VALUES
('72309101A', 70, 72, 75, 74, 78, 7.2),
('72309102B', 85, 88, 90, 86, 87, 8.8),
('72309103C', 65, 68, 70, 69, 72, 6.8),
('72309104D', 92, 91, 94, 93, 95, 9.4),
('72309105E', 72, 70, 73, 71, 74, 7.1),
('72309106F', 84, 83, 85, 86, 82, 8.5),
('72309107G', 66, 65, 68, 67, 69, 6.6),
('72309108H', 91, 90, 89, 92, 88, 9.1),
('72309109J', 75, 77, 74, 76, 78, 7.6),
('72309110K', 80, 82, 83, 81, 84, 8.2),
('72309111L', 69, 71, 70, 72, 73, 7.0),
('72309112M', 95, 94, 96, 97, 93, 9.6),
('72309113N', 63, 65, 66, 64, 67, 6.4),
('72309114P', 87, 88, 85, 89, 86, 8.8),
('72309115Q', 76, 74, 78, 77, 79, 7.7),
('72309116R', 82, 83, 81, 84, 80, 8.2),
('72309117S', 68, 69, 70, 67, 71, 6.9),
('72309118T', 92, 91, 90, 93, 94, 9.3),
('72309119U', 73, 74, 72, 75, 76, 7.4),
('72309120V', 86, 87, 85, 88, 89, 8.7);

-- Insert Semester 2 Grades
INSERT INTO sem2 VALUES
('72309101A', 72, 70, 74, 73, 75, 7.3),
('72309102B', 88, 86, 87, 85, 90, 8.7),
('72309103C', 67, 66, 69, 68, 70, 6.7),
('72309104D', 93, 92, 94, 91, 95, 9.3),
('72309105E', 71, 73, 72, 70, 74, 7.2),
('72309106F', 85, 84, 83, 86, 82, 8.4),
('72309107G', 65, 67, 66, 68, 69, 6.6),
('72309108H', 90, 91, 89, 92, 88, 9.1),
('72309109J', 76, 75, 78, 77, 79, 7.7),
('72309110K', 81, 82, 80, 83, 84, 8.2),
('72309111L', 70, 72, 71, 73, 74, 7.1),
('72309112M', 96, 95, 94, 97, 93, 9.6),
('72309113N', 64, 66, 65, 67, 68, 6.5),
('72309114P', 88, 87, 89, 86, 90, 8.8),
('72309115Q', 77, 79, 76, 78, 75, 7.7),
('72309116R', 83, 81, 82, 84, 80, 8.2),
('72309117S', 69, 68, 70, 71, 72, 7.0),
('72309118T', 91, 90, 92, 93, 94, 9.2),
('72309119U', 74, 73, 75, 72, 76, 7.4),
('72309120V', 87, 86, 88, 89, 85, 8.7);

-- Insert Semester 3 Grades
INSERT INTO sem3 VALUES
('72309101A', 75, 74, 78, 76, 77, 7.6),
('72309102B', 89, 87, 90, 88, 86, 8.9),
('72309103C', 68, 70, 69, 67, 71, 6.9),
('72309104D', 94, 93, 95, 92, 91, 9.3),
('72309105E', 72, 73, 71, 74, 75, 7.3),
('72309106F', 86, 85, 84, 83, 82, 8.4),
('72309107G', 66, 67, 65, 68, 69, 6.7),
('72309108H', 92, 91, 90, 89, 88, 9.0),
('72309109J', 77, 78, 76, 75, 79, 7.7),
('72309110K', 82, 83, 81, 80, 84, 8.2),
('72309111L', 71, 70, 72, 73, 74, 7.2),
('72309112M', 97, 96, 95, 94, 93, 9.7),
('72309113N', 65, 64, 66, 67, 68, 6.6),
('72309114P', 88, 89, 87, 86, 90, 8.8),
('72309115Q', 79, 78, 77, 76, 75, 7.8),
('72309116R', 84, 83, 82, 81, 80, 8.3),
('72309117S', 70, 69, 71, 72, 73, 7.1),
('72309118T', 93, 92, 91, 94, 95, 9.4),
('72309119U', 75, 74, 73, 76, 77, 7.5),
('72309120V', 88, 87, 86, 85, 89, 8.7);

-- Insert Semester 4 Grades
INSERT INTO sem4 VALUES
('72309101A', 74, 73, 75, 72, 76, 7.4),
('72309102B', 88, 87, 89, 86, 90, 8.8),
('72309103C', 69, 68, 70, 67, 71, 6.8),
('72309104D', 95, 94, 93, 92, 91, 9.3),
('72309105E', 73, 72, 74, 71, 75, 7.3),
('72309106F', 85, 84, 83, 82, 81, 8.3),
('72309107G', 67, 66, 65, 68, 69, 6.6),
('72309108H', 91, 90, 92, 89, 88, 9.0),
('72309109J', 78, 77, 76, 75, 79, 7.7),
('72309110K', 83, 82, 81, 84, 80, 8.2),
('72309111L', 72, 71, 70, 73, 74, 7.2),
('72309112M', 96, 95, 94, 97, 93, 9.6),
('72309113N', 66, 65, 64, 67, 68, 6.5),
('72309114P', 89, 88, 87, 86, 90, 8.8),
('72309115Q', 78, 79, 77, 76, 75, 7.8),
('72309116R', 84, 83, 82, 81, 80, 8.3),
('72309117S', 71, 70, 69, 72, 73, 7.0),
('72309118T', 92, 91, 90, 93, 94, 9.2),
('72309119U', 76, 75, 74, 73, 77, 7.5),
('72309120V', 87, 86, 85, 88, 89, 8.7);

-- Insert Student Skills
INSERT INTO student_skills (prn, skill_name) VALUES
-- High Performers
('72309101A', 'C++'),
('72309101A', 'Python'),
('72309101A', 'Data Structures'),
('72309101A', 'OOP'),
('72309101A', 'SQL'),
('72309101A', 'Git'),
('72309102B', 'Java'),
('72309102B', 'Python'),
('72309102B', 'Data Structures'),
('72309102B', 'SQL'),
('72309102B', 'HTML'),
('72309102B', 'Git'),
('72309110K', 'C++'),
('72309110K', 'Python'),
('72309110K', 'Data Structures'),
('72309110K', 'React'),
('72309110K', 'SQL'),
('72309118T', 'Python'),
('72309118T', 'Data Structures'),
('72309118T', 'OOP'),
('72309118T', 'SQL'),
-- Average Performers
('72309103C', 'C'),
('72309103C', 'C++'),
('72309103C', 'Data Structures'),
('72309104D', 'Java'),
('72309104D', 'OOP'),
('72309104D', 'SQL'),
('72309105E', 'C++'),
('72309105E', 'Python'),
('72309106F', 'Python'),
('72309106F', 'HTML'),
('72309106F', 'CSS'),
('72309107G', 'C'),
('72309107G', 'C++'),
('72309111L', 'Java'),
('72309111L', 'SQL'),
('72309112M', 'Python'),
('72309112M', 'Data Structures'),
('72309114P', 'C++'),
('72309114P', 'OOP'),
('72309115Q', 'Python'),
-- Lower Performers
('72309108H', 'C'),
('72309108H', 'HTML'),
('72309109J', 'C'),
('72309113N', 'HTML'),
('72309116R', 'C'),
('72309116R', 'SQL'),
('72309117S', 'C++'),
('72309119U', 'C'),
('72309120V', 'Java');

-- ============================================================
-- SAMPLE QUERY - Student Academic Overview
-- ============================================================
-- SELECT
--     s.prn,
--     s.name,
--     m.percentage AS '12th_percentage',
--     sem1.sgpa AS sem1_sgpa,
--     sem2.sgpa AS sem2_sgpa,
--     sem3.sgpa AS sem3_sgpa,
--     sem4.sgpa AS sem4_sgpa,
--     GROUP_CONCAT(ss.skill_name) AS skills
-- FROM students s
-- LEFT JOIN marks_12th m USING(prn)
-- LEFT JOIN sem1 USING(prn)
-- LEFT JOIN sem2 USING(prn)
-- LEFT JOIN sem3 USING(prn)
-- LEFT JOIN sem4 USING(prn)
-- LEFT JOIN student_skills ss USING(prn)
-- GROUP BY s.prn, s.name
-- ORDER BY m.percentage DESC;
