"""
database.py — SQLite setup for EduSync
Creates all tables and seeds sample data on first run
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'edusync.db')

def get_db():
    """Open database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # Dict-like rows
    return conn

def init_db():
    """Create tables and seed data if DB doesn't exist"""
    conn = get_db()
    c    = conn.cursor()

    # ── Users table (students + teachers) ──────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT    UNIQUE NOT NULL,
        password TEXT    NOT NULL,
        role     TEXT    NOT NULL DEFAULT 'student',
        name     TEXT    NOT NULL,
        roll     INTEGER,
        dept     TEXT    DEFAULT 'Computer Engineering',
        year     INTEGER DEFAULT 2
    )''')

    # ── Subjects ────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT    UNIQUE NOT NULL,
        name TEXT    NOT NULL,
        credits INTEGER DEFAULT 4
    )''')

    # ── Attendance ──────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        roll       INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        conducted  INTEGER NOT NULL DEFAULT 0,
        attended   INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )''')

    # ── Assignments ─────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS assignments (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id   INTEGER NOT NULL,
        title        TEXT    NOT NULL,
        description  TEXT,
        days_left    INTEGER NOT NULL DEFAULT 7,
        max_marks    INTEGER DEFAULT 10,
        submitted    INTEGER DEFAULT 0,
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )''')

    # ── Study Materials ─────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS materials (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        title      TEXT    NOT NULL,
        type       TEXT    DEFAULT 'Notes',
        url        TEXT    DEFAULT '#',
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )''')

    # ── Notices ─────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS notices (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        title   TEXT NOT NULL,
        content TEXT,
        date    TEXT DEFAULT (date('now'))
    )''')

    conn.commit()

    # ── Seed data (only if empty) ───────────────────────────
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        _seed(c)
        conn.commit()

    conn.close()

def _seed(c):
    """Insert sample data so project has realistic content"""

    # Users
    c.executemany("INSERT INTO users (username,password,role,name,roll,dept,year) VALUES (?,?,?,?,?,?,?)", [
        ('student',  '123',   'student', 'Khushal Patil',   1001, 'Computer Engineering', 2),
        ('student2', '123',   'student', 'Arjun Munde',     1002, 'Computer Engineering', 2),
        ('student3', '123',   'student', 'Shreyas Nalavade',1003, 'Computer Engineering', 2),
        ('student4', '123',   'student', 'Aryan Narkhede',  1004, 'Computer Engineering', 2),
        ('teacher',  '123',   'teacher', 'Prof. Sharma',    None, 'Computer Engineering', None),
    ])

    # Subjects
    c.executemany("INSERT INTO subjects (code,name,credits) VALUES (?,?,?)", [
        ('AIDS301', 'Advanced Data Structures',   4),
        ('AIDS302', 'Design & Analysis of Algorithms', 4),
        ('AIDS303', 'Database Management Systems',3),
        ('AIDS304', 'Operating Systems',          3),
        ('AIDS305', 'Computer Networks',          3),
        ('AIDS306', 'Machine Learning',           4),
    ])

    # Attendance for student roll 1001
    c.executemany("INSERT INTO attendance (roll,subject_id,conducted,attended) VALUES (?,?,?,?)", [
        (1001, 1, 40, 34),  # AIDS301 — 85%
        (1001, 2, 35, 28),  # AIDS302 — 80%
        (1001, 3, 30, 27),  # AIDS303 — 90%
        (1001, 4, 38, 27),  # AIDS304 — 71% ← below 75
        (1001, 5, 32, 26),  # AIDS305 — 81%
        (1001, 6, 28, 22),  # AIDS306 — 78%
    ])

    # Assignments
    c.executemany("INSERT INTO assignments (subject_id,title,description,days_left,max_marks) VALUES (?,?,?,?,?)", [
        (1, 'AVL Tree Implementation',    'Implement AVL tree with all rotations',         1, 10),
        (2, 'Dijkstra Algorithm',         'Implement shortest path on weighted graph',      3, 15),
        (3, 'ER Diagram — Library DB',    'Design ER diagram for library management',       5, 10),
        (4, 'Process Scheduling Report',  'Compare FCFS, SJF, Round Robin with examples',  2, 10),
        (5, 'Socket Programming Lab',     'TCP client-server chat application in Python',   7, 20),
        (6, 'ML Mini Project Proposal',   'Submit 1-page proposal for ML project',          4, 10),
    ])

    # Materials
    c.executemany("INSERT INTO materials (subject_id,title,type) VALUES (?,?,?)", [
        (1, 'AVL Trees — Lecture Notes Unit 1',    'Notes'),
        (1, 'Red-Black Trees Explained',            'Notes'),
        (1, 'Heap & Huffman Coding',                'Notes'),
        (2, 'Dynamic Programming Cheatsheet',       'Notes'),
        (2, 'Graph Algorithms Reference',           'PDF'),
        (3, 'SQL Query Practice Set',               'Assignment'),
        (3, 'Normalization 1NF to BCNF',            'Notes'),
        (4, 'Process Management — OS Notes',        'Notes'),
        (5, 'TCP/IP Model Summary',                 'Notes'),
        (6, 'Supervised vs Unsupervised Learning',  'Notes'),
        (6, 'Python Scikit-Learn Tutorial',         'PDF'),
    ])

    # Notices
    c.executemany("INSERT INTO notices (title,content) VALUES (?,?)", [
        ('Mid-Sem Exam Schedule Released',  'Mid-semester examinations will be held from 28th April. Check timetable on VIERP.'),
        ('EduSync Platform Launched',       'EduSync now merges VIERP + VOLP into one portal. Report bugs to admin.'),
        ('Project Submission Deadline',     'Course project submissions due on 25th April. Upload on EduSync.'),
        ('Attendance Warning',              'Students with attendance below 75% will receive a warning letter.'),
    ])
