import os
import sqlite3
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from ml_models.predictor import AcademicPredictor

app = Flask(__name__, static_folder=".", template_folder=".")
DB_PATH = "eduvision.db"

# Initialize ML Predictor
predictor = AcademicPredictor()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite DB schema and populates from dataset if empty."""
    conn = get_db()
    cursor = conn.cursor()
    
    with open("db.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    
    # Check if student table has data
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    
    if count == 0:
        dataset_path = os.path.join("datasets", "student_academic_dataset.csv")
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            for _, row in df.iterrows():
                email = f"{row['prn'].lower()}@dypiet.edu.in"
                cursor.execute("""
                    INSERT OR IGNORE INTO students (prn, name, department, email, ssc_perc, hsc_perc)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (row['prn'], row['name'], row['department'], email, row['ssc_perc'], row['hsc_perc']))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO academic_records 
                    (prn, sem1_sgpa, sem2_sgpa, sem3_sgpa, sem4_sgpa, sem5_sgpa, sem6_sgpa, 
                     attendance_perc, dsa_score, dbms_score, ml_score, cn_score, project_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['prn'], row['sem1_sgpa'], row['sem2_sgpa'], row['sem3_sgpa'],
                    row['sem4_sgpa'], row['sem5_sgpa'], row['sem6_sgpa'], row['attendance_perc'],
                    row['dsa_score'], row['dbms_score'], row['ml_score'], row['cn_score'], row['project_score']
                ))
                
                # Seed default certifications
                if row['certifications_count'] > 0:
                    cursor.execute("""
                        INSERT INTO certifications (prn, title, issuer, issue_date, status, faculty_comment)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        row['prn'], 
                        "AWS Certified Cloud Practitioner", 
                        "Amazon Web Services", 
                        "2025-11-15", 
                        "Verified & Approved", 
                        "Verified by Prof. Deshmukh"
                    ))
                    if row['certifications_count'] > 2:
                        cursor.execute("""
                            INSERT INTO certifications (prn, title, issuer, issue_date, status, faculty_comment)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            row['prn'], 
                            "Machine Learning Specialization", 
                            "DeepLearning.AI / Coursera", 
                            "2026-02-10", 
                            "Verified & Approved", 
                            "Verified by Prof. Deshmukh"
                        ))
            conn.commit()
            print("Successfully populated database from CSV dataset!")
    conn.close()

# Routes
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

@app.route("/api/students", methods=["GET"])
def get_students():
    query = request.args.get("q", "").strip().lower()
    conn = get_db()
    cursor = conn.cursor()
    
    if query:
        cursor.execute("""
            SELECT s.prn, s.name, s.department, a.sem6_sgpa, a.attendance_perc
            FROM students s
            JOIN academic_records a ON s.prn = a.prn
            WHERE LOWER(s.prn) LIKE ? OR LOWER(s.name) LIKE ? OR LOWER(s.department) LIKE ?
            LIMIT 20
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    else:
        cursor.execute("""
            SELECT s.prn, s.name, s.department, a.sem6_sgpa, a.attendance_perc
            FROM students s
            JOIN academic_records a ON s.prn = a.prn
            ORDER BY s.prn ASC
            LIMIT 30
        """)
        
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "count": len(students), "students": students})

@app.route("/api/student/<prn>", methods=["GET"])
def get_student_details(prn):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, a.sem1_sgpa, a.sem2_sgpa, a.sem3_sgpa, a.sem4_sgpa, a.sem5_sgpa, a.sem6_sgpa,
               a.attendance_perc, a.dsa_score, a.dbms_score, a.ml_score, a.cn_score, a.project_score
        FROM students s
        JOIN academic_records a ON s.prn = a.prn
        WHERE s.prn = ?
    """, (prn,))
    
    student_row = cursor.fetchone()
    if not student_row:
        conn.close()
        return jsonify({"success": False, "error": f"Student with PRN '{prn}' not found."}), 404
        
    student_data = dict(student_row)
    
    # Calculate CGPA
    sgpas = [student_data[f"sem{i}_sgpa"] for i in range(1, 7) if student_data.get(f"sem{i}_sgpa") is not None]
    student_data["cgpa"] = round(sum(sgpas) / len(sgpas), 2) if sgpas else 0.0
    
    # Get certifications
    cursor.execute("SELECT * FROM certifications WHERE prn = ? ORDER BY id DESC", (prn,))
    student_data["certifications"] = [dict(c) for c in cursor.fetchall()]
    student_data["certifications_count"] = len(student_data["certifications"])
    
    # ML & AI prediction analysis
    analysis = predictor.predict_performance(student_data)
    student_data["ai_analysis"] = analysis
    
    conn.close()
    return jsonify({"success": True, "student": student_data})

@app.route("/api/certifications", methods=["POST"])
def add_certification():
    data = request.json or {}
    prn = data.get("prn")
    title = data.get("title")
    issuer = data.get("issuer")
    issue_date = data.get("issue_date", "2026-07-31")
    
    if not prn or not title or not issuer:
        return jsonify({"success": False, "error": "PRN, Title, and Issuer are required."}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO certifications (prn, title, issuer, issue_date, status)
        VALUES (?, ?, ?, ?, 'Pending Verification')
    """, (prn, title, issuer, issue_date))
    
    cursor.execute("""
        INSERT INTO faculty_approvals (prn, item_type, title, status)
        VALUES (?, 'Certification', ?, 'Pending')
    """, (prn, title))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Certification submitted successfully for faculty verification!"})

@app.route("/api/faculty/approvals", methods=["GET"])
def get_pending_approvals():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, c.prn, s.name, s.department, c.title, c.issuer, c.issue_date, c.status
        FROM certifications c
        JOIN students s ON c.prn = s.prn
        ORDER BY c.id DESC
    """)
    
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "approvals": items})

@app.route("/api/faculty/approve", methods=["POST"])
def approve_item():
    data = request.json or {}
    cert_id = data.get("cert_id")
    status = data.get("status", "Verified & Approved")
    comment = data.get("comment", "Verified by Faculty")
    
    if not cert_id:
        return jsonify({"success": False, "error": "cert_id is required."}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE certifications
        SET status = ?, faculty_comment = ?
        WHERE id = ?
    """, (status, comment, cert_id))
    
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Certification updated to '{status}'."})

@app.route("/api/department/stats", methods=["GET"])
def get_department_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.department,
               COUNT(s.prn) as total_students,
               ROUND(AVG(a.sem6_sgpa), 2) as avg_sem6_sgpa,
               ROUND(AVG(a.attendance_perc), 1) as avg_attendance,
               ROUND(AVG(a.project_score), 1) as avg_project
        FROM students s
        JOIN academic_records a ON s.prn = a.prn
        GROUP BY s.department
    """)
    
    dept_stats = [dict(row) for row in cursor.fetchall()]
    
    # Get top performers
    cursor.execute("""
        SELECT s.prn, s.name, s.department, a.sem6_sgpa
        FROM students s
        JOIN academic_records a ON s.prn = a.prn
        ORDER BY a.sem6_sgpa DESC
        LIMIT 5
    """)
    top_performers = [dict(row) for row in cursor.fetchall()]
    
    # Get at-risk count
    cursor.execute("""
        SELECT COUNT(*) as risk_count
        FROM academic_records
        WHERE sem6_sgpa < 6.5 OR attendance_perc < 72.0
    """)
    risk_count = cursor.fetchone()["risk_count"]
    
    conn.close()
    return jsonify({
        "success": True,
        "departments": dept_stats,
        "top_performers": top_performers,
        "at_risk_count": risk_count
    })

if __name__ == "__main__":
    init_db()
    print("EduVision AI REST API starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
