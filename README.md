# EduVision AI

EduVision is an academic analytics system that tracks student performance using PRN-based records and generates improvement guidance.

## Student Portal (Implemented)

Student-side pages are built with Tailwind + vanilla JS and are separated by route:
- `frontend/student/dashboard.html`
- `frontend/student/progress.html`
- `frontend/student/reports.html`
- `frontend/student/improvement.html`

The pages fetch live data from the backend API (not hardcoded values).

## Backend API

Backend entrypoint:
- `backend/app.py`

Main features:
- Connects to local MySQL DB (`localhost`) using environment variables
- Reads schema tables from `db.sql`:
  - `students`
  - `marks_12th`
  - `sem1` to `sem6`
  - `student_skills`
- Builds student dashboard/progress/report payloads from DB records
- Calls Gemini API (server-side key) for improvement recommendations
- Falls back to rule-based recommendations if Gemini key/call is unavailable
- Optional strict mode: set `GEMINI_REQUIRED=true` to fail the endpoint if Gemini does not respond

## Environment Setup

1. Copy `.env.example` to `.env`
2. Fill:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`
   - `DB_SSL_CA` (keep empty for localhost)
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL` (default `gemini-1.5-flash`)

3. Import schema/data into local MySQL:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS eduvision_ai;"
mysql -u root -p eduvision_ai < db.sql
```

## Run Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start backend:
```bash
python backend/app.py
```

3. Start frontend static server:
```bash
python -m http.server 5500 --directory frontend
```

4. Open:
- `http://127.0.0.1:5500`

5. Enter:
- PRN (example: `72309101A`)
- API Base URL (default: `http://127.0.0.1:5000/api`)

6. Verify health before opening student pages:
```bash
curl http://127.0.0.1:5000/api/health
```

## Student API Endpoints

- `GET /api/health`
- `GET /api/student/<prn>/dashboard`
- `GET /api/student/<prn>/progress`
- `GET /api/student/<prn>/reports`
- `GET /api/student/<prn>/improvement`
