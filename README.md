# EduSync v3 — Unified College Portal

> VIERP + VOLP merged into one system.

EduSync is a college management portal for Vishwakarma Institute of Technology, Pune.
It combines the ERP (student records, attendance) and LMS (assignments, materials) into one platform.

---

## Features

**For Students**
- View subject-wise attendance with safe/danger status
- See all assignments with deadlines and submit them directly from the portal
- Browse and search study materials
- Look up any student by roll number
- View project group assignments

**For Teachers**
- Add and delete assignments (students see them immediately)
- Add study materials per subject
- View submission counts per assignment
- Drill into any assignment to see who has submitted and who is still pending
- Student overview with per-student submission progress

---

## Quick Start

### Linux / macOS
```bash
./setup.sh
python app.py
```

### Windows
```bat
setup_windows.bat
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## Default Credentials

| Role    | Username  | Password |
|---------|-----------|----------|
| Student | student   | 123      |
| Teacher | teacher   | 123      |

There are 50 student accounts: `student`, `student2`, `student3`, ... `student50`, all with password `123`.

---

## Project Structure

```
EduSync_v3/
├── app.py              # Main Flask application
├── database.py         # SQLite setup and seed data
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css       # Stylesheet
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── attendance.html
│   ├── assignments.html
│   ├── submissions.html
│   ├── materials.html
│   ├── student_search.html
│   ├── groups.html
│   └── teacher.html
├── ds/                 # Data structure backends (Python)
└── ds_cpp/             # Data structure backends (C++)
```

---

## Database Tables

| Table       | Purpose                              |
|-------------|--------------------------------------|
| users       | Students and teachers                |
| subjects    | 6 subjects for CE Semester 4         |
| attendance  | Per-student per-subject records      |
| assignments | Assignments added by teacher         |
| submissions | Per-student submission tracking      |
| materials   | Study materials per subject          |
| notices     | Notice board entries                 |
