import json
import os
import re
from collections import OrderedDict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple

import pymysql
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
STUDENT_DIR = FRONTEND_DIR / "student"

SEMESTER_SUBJECTS: "OrderedDict[str, List[str]]" = OrderedDict(
    [
        (
            "sem1",
            [
                "systems_mechanical_engineering",
                "basic_electrical_engineering",
                "engineering_mathematics_1",
                "engineering_chemistry",
                "programming_problem_solving",
            ],
        ),
        (
            "sem2",
            [
                "engineering_mechanics",
                "engineering_graphics",
                "basic_electronics_engineering",
                "engineering_physics",
                "engineering_mathematics_2",
            ],
        ),
        (
            "sem3",
            [
                "discrete_mathematics",
                "data_structures",
                "object_oriented_programming",
                "computer_graphics",
                "operating_systems",
            ],
        ),
        (
            "sem4",
            [
                "data_structures_algorithms",
                "software_engineering",
                "statistics",
                "internet_of_things",
                "management_information_system",
            ],
        ),
        (
            "sem5",
            [
                "artificial_intelligence",
                "database_management_systems",
                "web_technology",
                "pattern_recognition",
                "computer_networks",
            ],
        ),
        (
            "sem6",
            [
                "cyber_security",
                "data_science",
                "artificial_neural_networks",
                "cloud_computing",
            ],
        ),
    ]
)


class StudentNotFoundError(Exception):
    def __init__(self, prn: str, suggestions: Optional[List[Dict[str, str]]] = None):
        super().__init__("Student not found")
        self.prn = prn
        self.suggestions = suggestions or []


def db_name() -> str:
    return os.getenv("DB_NAME", "eduvision_ai")


def db_config() -> Dict[str, Any]:
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": db_name(),
        "charset": "utf8mb4",
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
        "read_timeout": int(os.getenv("DB_READ_TIMEOUT", "20")),
        "write_timeout": int(os.getenv("DB_WRITE_TIMEOUT", "20")),
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
    }


def get_connection() -> pymysql.connections.Connection:
    cfg = db_config()
    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca:
        cfg["ssl"] = {"ca": ssl_ca}
    return pymysql.connect(**cfg)


def normalize_prn(prn: str) -> str:
    return prn.strip().upper()


def format_subject_name(raw: str) -> str:
    return raw.replace("_", " ").title()


def score_to_grade(score: Optional[float]) -> str:
    if score is None:
        return "-"
    if score >= 90:
        return "A+"
    if score >= 85:
        return "A"
    if score >= 80:
        return "B+"
    if score >= 75:
        return "B"
    if score >= 70:
        return "C+"
    if score >= 60:
        return "C"
    return "D"


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    return float(value)


def table_exists(cursor: pymysql.cursors.Cursor, table_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        """,
        (db_name(), table_name),
    )
    row = cursor.fetchone()
    return bool(row and row["cnt"])


def fetch_student_base(cursor: pymysql.cursors.Cursor, prn: str) -> Optional[Dict[str, Any]]:
    cursor.execute(
        """
        SELECT
            s.prn,
            s.name,
            m.physics,
            m.chemistry,
            m.mathematics,
            m.english,
            m.computer_science,
            m.percentage AS twelfth_percentage
        FROM students s
        LEFT JOIN marks_12th m ON s.prn = m.prn
        WHERE s.prn = %s
        """,
        (prn,),
    )
    return cursor.fetchone()


def fetch_prn_suggestions(
    cursor: pymysql.cursors.Cursor, prn: str, limit: int = 5
) -> List[Dict[str, str]]:
    prefix = prn[: max(3, len(prn) - 1)]
    cursor.execute(
        """
        SELECT prn, name
        FROM students
        WHERE prn LIKE %s
        ORDER BY prn
        LIMIT %s
        """,
        (f"{prefix}%", limit),
    )
    rows = cursor.fetchall()
    if rows:
        return [{"prn": row["prn"], "name": row["name"]} for row in rows]

    cursor.execute(
        """
        SELECT prn, name
        FROM students
        ORDER BY prn
        LIMIT %s
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    return [{"prn": row["prn"], "name": row["name"]} for row in rows]


def fetch_skills(cursor: pymysql.cursors.Cursor, prn: str) -> List[str]:
    if not table_exists(cursor, "student_skills"):
        return []
    cursor.execute(
        "SELECT skill_name FROM student_skills WHERE prn = %s ORDER BY skill_name ASC",
        (prn,),
    )
    return [row["skill_name"] for row in cursor.fetchall()]


def fetch_semester_data(cursor: pymysql.cursors.Cursor, prn: str) -> List[Dict[str, Any]]:
    semester_rows: List[Dict[str, Any]] = []
    for sem_table, subject_columns in SEMESTER_SUBJECTS.items():
        if not table_exists(cursor, sem_table):
            continue
        cursor.execute(f"SELECT * FROM {sem_table} WHERE prn = %s", (prn,))
        row = cursor.fetchone()
        if not row:
            continue

        subjects = []
        for column in subject_columns:
            if column in row and row[column] is not None:
                score = int(row[column])
                subjects.append(
                    {
                        "key": column,
                        "subject": format_subject_name(column),
                        "score": score,
                        "grade": score_to_grade(score),
                    }
                )

        semester_rows.append(
            {
                "table": sem_table,
                "semester": sem_table.replace("sem", "Semester "),
                "sgpa": safe_float(row.get("sgpa")),
                "subjects": subjects,
            }
        )

    return semester_rows


def rank_for_semester(
    cursor: pymysql.cursors.Cursor, sem_table: Optional[str], sgpa: Optional[float]
) -> Tuple[Optional[int], Optional[int]]:
    if sem_table is None or sgpa is None or not table_exists(cursor, sem_table):
        return None, None

    cursor.execute(f"SELECT COUNT(*) AS cnt FROM {sem_table} WHERE sgpa > %s", (sgpa,))
    higher = cursor.fetchone()["cnt"]
    cursor.execute(f"SELECT COUNT(*) AS cnt FROM {sem_table}")
    total = cursor.fetchone()["cnt"]
    return int(higher) + 1, int(total)


def compute_subject_average(subjects: List[Dict[str, Any]]) -> Optional[float]:
    scores = [item["score"] for item in subjects if item.get("score") is not None]
    return round(mean(scores), 2) if scores else None


def derive_focus_areas(subjects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not subjects:
        return []

    weakest = sorted(subjects, key=lambda item: item["score"])[:2]
    focus_areas = []
    for item in weakest:
        current = item["score"]
        target = min(current + 8, 95)
        gap = target - current
        priority = "high" if current < 75 else "medium"
        focus_areas.append(
            {
                "subject": item["subject"],
                "current_score": current,
                "target_score": target,
                "gap": gap,
                "priority": priority,
                "reason": "Low recent semester score compared to peer benchmark.",
            }
        )
    return focus_areas


def fallback_improvement_payload(
    student_name: str,
    focus_areas: List[Dict[str, Any]],
    skills: List[str],
) -> Dict[str, Any]:
    if not focus_areas:
        return {
            "summary": f"{student_name} is currently performing consistently across available records.",
            "focus_areas": [],
            "recommendations": [
                {
                    "title": "Weekly Revision Loop",
                    "action": "Review one completed topic every weekend and solve 10 mixed questions.",
                    "duration": "1.5 hours/week",
                    "difficulty": "easy",
                    "priority": "medium",
                }
            ],
            "six_week_plan": [
                {
                    "week_range": "Week 1-2",
                    "goal": "Establish revision routine",
                    "tasks": [
                        "Create a topic tracker",
                        "Schedule fixed revision slots",
                        "Submit one mock test",
                    ],
                }
            ],
            "source": "fallback",
        }

    primary = focus_areas[0]
    secondary = focus_areas[1] if len(focus_areas) > 1 else focus_areas[0]

    return {
        "summary": (
            f"Focus on {primary['subject']} first, then reinforce {secondary['subject']} to improve SGPA momentum."
        ),
        "focus_areas": focus_areas,
        "recommendations": [
            {
                "title": f"Targeted Practice: {primary['subject']}",
                "action": f"Solve at least 20 high-weight questions in {primary['subject']} every week.",
                "duration": "2 hours/week",
                "difficulty": "medium",
                "priority": "high",
            },
            {
                "title": f"Peer Session: {secondary['subject']}",
                "action": f"Join a study session for {secondary['subject']} and review errors after each test.",
                "duration": "1.5 hours/week",
                "difficulty": "easy",
                "priority": "medium",
            },
            {
                "title": "Skill Alignment",
                "action": (
                    "Use existing strengths to support weak subjects. "
                    f"Current skills: {', '.join(skills[:5]) if skills else 'No skills listed'}."
                ),
                "duration": "45 minutes/week",
                "difficulty": "easy",
                "priority": "medium",
            },
        ],
        "six_week_plan": [
            {
                "week_range": "Week 1-2",
                "goal": f"Stabilize {primary['subject']} foundation",
                "tasks": [
                    "Identify weak units from recent assessments",
                    "Finish one concept recap notebook",
                    "Attempt one timed quiz set",
                ],
            },
            {
                "week_range": "Week 3-4",
                "goal": f"Strengthen {secondary['subject']}",
                "tasks": [
                    "Practice mixed-difficulty questions",
                    "Track mistakes and recurring concepts",
                    "Review progress with mentor/faculty",
                ],
            },
            {
                "week_range": "Week 5-6",
                "goal": "Consolidate both focus subjects",
                "tasks": [
                    "Take one full mock assessment",
                    "Revise all weak topics",
                    "Set next-cycle score targets",
                ],
            },
        ],
        "source": "fallback",
    }


def extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def fetch_gemini_recommendations(
    student_name: str,
    prn: str,
    twelfth_percentage: Optional[float],
    semesters: List[Dict[str, Any]],
    skills: List[str],
    focus_areas: List[Dict[str, Any]],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None, "GEMINI_API_KEY is not configured."

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_name}:generateContent?key={api_key}"
    )

    semester_snapshot = [
        {
            "semester": item["semester"],
            "sgpa": item["sgpa"],
            "subjects": [
                {"subject": subject["subject"], "score": subject["score"]}
                for subject in item["subjects"]
            ],
        }
        for item in semesters
    ]

    prompt = f"""
You are an academic mentor assistant for EduVision.
Use only the student data below and create a realistic improvement plan.

Student name: {student_name}
PRN: {prn}
12th percentage: {twelfth_percentage}
Semesters: {json.dumps(semester_snapshot)}
Skills: {json.dumps(skills)}
Focus areas: {json.dumps(focus_areas)}

Respond strictly in JSON with this schema:
{{
  "summary": "string",
  "focus_areas": [
    {{
      "subject": "string",
      "current_score": number,
      "target_score": number,
      "gap": number,
      "priority": "high|medium|low",
      "reason": "string"
    }}
  ],
  "recommendations": [
    {{
      "title": "string",
      "action": "string",
      "duration": "string",
      "difficulty": "easy|medium|hard",
      "priority": "high|medium|low"
    }}
  ],
  "six_week_plan": [
    {{
      "week_range": "Week 1-2",
      "goal": "string",
      "tasks": ["string", "string"]
    }}
  ]
}}
"""

    try:
        response = requests.post(
            endpoint,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1200,
                    "responseMimeType": "application/json",
                },
            },
            timeout=25,
        )
        response.raise_for_status()
        payload = response.json()
        text = (
            payload.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        parsed = extract_json_block(text)
        if not parsed:
            return None, "Gemini response could not be parsed as JSON."
        parsed["source"] = "gemini"
        return parsed, None
    except Exception as exc:
        return None, str(exc)


def load_student_context(prn: str) -> Dict[str, Any]:
    normalized_prn = normalize_prn(prn)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            student = fetch_student_base(cursor, normalized_prn)
            if not student:
                raise StudentNotFoundError(
                    prn=normalized_prn,
                    suggestions=fetch_prn_suggestions(cursor, normalized_prn),
                )

            semesters = fetch_semester_data(cursor, normalized_prn)
            skills = fetch_skills(cursor, normalized_prn)
            latest = semesters[-1] if semesters else None
            previous = semesters[-2] if len(semesters) > 1 else None
            rank, class_size = rank_for_semester(
                cursor,
                latest["table"] if latest else None,
                latest["sgpa"] if latest else None,
            )

            return {
                "student": student,
                "semesters": semesters,
                "skills": skills,
                "latest": latest,
                "previous": previous,
                "rank": rank,
                "class_size": class_size,
            }


@app.get("/api/health")
def health() -> Any:
    status = {
        "ok": True,
        "service": "eduvision-student-api",
        "database": "disconnected",
        "db_name": db_name(),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
    }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS ok")
                row = cursor.fetchone()
                status["database"] = "connected" if row and row.get("ok") == 1 else "unknown"
    except Exception as exc:
        status["ok"] = False
        status["database"] = "error"
        status["details"] = str(exc)
        return jsonify(status), 503

    return jsonify(status)


@app.get("/api/students")
def students_list() -> Any:
    try:
        limit = int(os.getenv("STUDENT_LIST_LIMIT", "50"))
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT prn, name
                    FROM students
                    ORDER BY prn
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()
        return jsonify({"students": rows, "count": len(rows)})
    except Exception as exc:
        return jsonify({"error": "Unable to load student list", "details": str(exc)}), 500


@app.get("/")
def frontend_home() -> Any:
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/index.html")
def frontend_index() -> Any:
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/student/<path:filename>")
def frontend_student(filename: str) -> Any:
    return send_from_directory(STUDENT_DIR, filename)


@app.get("/api/student/<prn>/dashboard")
def student_dashboard(prn: str) -> Any:
    try:
        context = load_student_context(prn)
        student = context["student"]
        latest = context["latest"]
        previous = context["previous"]
        semesters = context["semesters"]
        skills = context["skills"]

        latest_subjects = latest["subjects"] if latest else []
        average_subject_score = compute_subject_average(latest_subjects)
        current_sgpa = latest["sgpa"] if latest else None
        previous_sgpa = previous["sgpa"] if previous else None
        sgpa_change = (
            round(current_sgpa - previous_sgpa, 2)
            if current_sgpa is not None and previous_sgpa is not None
            else None
        )

        recent_grades = sorted(
            latest_subjects,
            key=lambda item: item["score"],
            reverse=True,
        )

        insights = []
        if sgpa_change is not None:
            if sgpa_change > 0:
                insights.append("SGPA trend is improving compared to previous semester.")
            elif sgpa_change < 0:
                insights.append("SGPA dipped from previous semester; focus on weak subjects.")
            else:
                insights.append("SGPA is stable across the last two semesters.")
        if average_subject_score is not None:
            insights.append(f"Current semester subject average is {average_subject_score}%.")
        if skills:
            insights.append(f"Recorded technical skills: {', '.join(skills[:6])}.")

        return jsonify(
            {
                "student": {"prn": student["prn"], "name": student["name"]},
                "metrics": {
                    "current_sgpa": current_sgpa,
                    "sgpa_change": sgpa_change,
                    "twelfth_percentage": safe_float(student.get("twelfth_percentage")),
                    "average_subject_score": average_subject_score,
                    "class_rank": context["rank"],
                    "class_size": context["class_size"],
                    "skills_count": len(skills),
                },
                "progress": [
                    {"semester": row["semester"], "sgpa": row["sgpa"]} for row in semesters
                ],
                "recent_grades": recent_grades,
                "skills": skills,
                "insights": insights,
            }
        )
    except StudentNotFoundError as exc:
        return (
            jsonify(
                {
                    "error": "Student not found",
                    "prn": exc.prn,
                    "hint": "Use exact PRN from students table.",
                    "suggestions": exc.suggestions,
                }
            ),
            404,
        )
    except Exception as exc:
        return jsonify({"error": "Unable to load dashboard", "details": str(exc)}), 500


@app.get("/api/student/<prn>/progress")
def student_progress(prn: str) -> Any:
    try:
        context = load_student_context(prn)
        student = context["student"]
        latest = context["latest"]
        semesters = context["semesters"]
        skills = context["skills"]

        subjects = []
        for item in (latest["subjects"] if latest else []):
            score = item["score"]
            status = "strong" if score >= 85 else "stable" if score >= 70 else "needs_focus"
            target = min(score + 5, 95)
            subjects.append(
                {
                    **item,
                    "status": status,
                    "target_score": target,
                    "delta_to_target": target - score,
                }
            )

        twelfth_pairs = [
            ("Physics", student.get("physics")),
            ("Chemistry", student.get("chemistry")),
            ("Mathematics", student.get("mathematics")),
            ("English", student.get("english")),
            ("Computer Science", student.get("computer_science")),
        ]
        filtered_pairs = [(label, int(score)) for label, score in twelfth_pairs if score is not None]

        goals = []
        for item in sorted(subjects, key=lambda x: x["score"])[:3]:
            status = "on_track" if item["score"] >= 80 else "needs_focus"
            goals.append(
                {
                    "title": f"Improve {item['subject']}",
                    "current_score": item["score"],
                    "target_score": item["target_score"],
                    "status": status,
                }
            )

        return jsonify(
            {
                "student": {"prn": student["prn"], "name": student["name"]},
                "current_semester": latest["semester"] if latest else None,
                "subjects": subjects,
                "sgpa_trend": [
                    {"semester": row["semester"], "sgpa": row["sgpa"]} for row in semesters
                ],
                "twelfth_radar": {
                    "labels": [item[0] for item in filtered_pairs],
                    "scores": [item[1] for item in filtered_pairs],
                },
                "skills": skills,
                "goals": goals,
            }
        )
    except StudentNotFoundError as exc:
        return (
            jsonify(
                {
                    "error": "Student not found",
                    "prn": exc.prn,
                    "hint": "Use exact PRN from students table.",
                    "suggestions": exc.suggestions,
                }
            ),
            404,
        )
    except Exception as exc:
        return jsonify({"error": "Unable to load progress", "details": str(exc)}), 500


@app.get("/api/student/<prn>/reports")
def student_reports(prn: str) -> Any:
    try:
        context = load_student_context(prn)
        student = context["student"]
        semesters = context["semesters"]
        latest = context["latest"]
        sgpa_values = [item["sgpa"] for item in semesters if item.get("sgpa") is not None]

        reports = [
            {
                "semester": item["semester"],
                "sgpa": item["sgpa"],
                "subjects": item["subjects"],
            }
            for item in semesters
        ]

        return jsonify(
            {
                "student": {"prn": student["prn"], "name": student["name"]},
                "summary": {
                    "twelfth_percentage": safe_float(student.get("twelfth_percentage")),
                    "current_sgpa": latest["sgpa"] if latest else None,
                    "class_rank": context["rank"],
                    "class_size": context["class_size"],
                    "semesters_completed": len(semesters),
                    "overall_cgpa": round(mean(sgpa_values), 2) if sgpa_values else None,
                },
                "reports": reports,
            }
        )
    except StudentNotFoundError as exc:
        return (
            jsonify(
                {
                    "error": "Student not found",
                    "prn": exc.prn,
                    "hint": "Use exact PRN from students table.",
                    "suggestions": exc.suggestions,
                }
            ),
            404,
        )
    except Exception as exc:
        return jsonify({"error": "Unable to load reports", "details": str(exc)}), 500


@app.get("/api/student/<prn>/improvement")
def student_improvement(prn: str) -> Any:
    try:
        context = load_student_context(prn)
        student = context["student"]
        latest = context["latest"]
        semesters = context["semesters"]
        skills = context["skills"]

        latest_subjects = latest["subjects"] if latest else []
        focus_areas = derive_focus_areas(latest_subjects)

        gemini_payload, gemini_error = fetch_gemini_recommendations(
            student_name=student["name"],
            prn=student["prn"],
            twelfth_percentage=safe_float(student.get("twelfth_percentage")),
            semesters=semesters,
            skills=skills,
            focus_areas=focus_areas,
        )

        gemini_required = os.getenv("GEMINI_REQUIRED", "false").lower() == "true"
        if gemini_required and not gemini_payload:
            return (
                jsonify(
                    {
                        "error": "Gemini response is required but generation failed.",
                        "details": gemini_error or "Unknown Gemini error",
                    }
                ),
                502,
            )

        payload = gemini_payload or fallback_improvement_payload(
            student_name=student["name"],
            focus_areas=focus_areas,
            skills=skills,
        )

        payload["student"] = {"prn": student["prn"], "name": student["name"]}
        payload["ai_status"] = "gemini_success" if gemini_payload else "gemini_fallback"
        payload["gemini_configured"] = bool(os.getenv("GEMINI_API_KEY", "").strip())
        if gemini_error:
            payload["ai_error"] = gemini_error
        payload["sgpa_trend"] = [
            {"semester": item["semester"], "sgpa": item["sgpa"]} for item in semesters
        ]
        payload["recommendations_started"] = len(payload.get("recommendations", []))
        payload["skills_count"] = len(skills)

        return jsonify(payload)
    except StudentNotFoundError as exc:
        return (
            jsonify(
                {
                    "error": "Student not found",
                    "prn": exc.prn,
                    "hint": "Use exact PRN from students table.",
                    "suggestions": exc.suggestions,
                }
            ),
            404,
        )
    except Exception as exc:
        return jsonify({"error": "Unable to load improvement plan", "details": str(exc)}), 500


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
