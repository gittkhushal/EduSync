"""
database.py — SQLite setup for EduSync
Creates all tables and seeds sample data on first run
"""

import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), 'edusync.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c    = conn.cursor()

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

    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT    UNIQUE NOT NULL,
        name TEXT    NOT NULL,
        credits INTEGER DEFAULT 4
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        roll       INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        conducted  INTEGER NOT NULL DEFAULT 0,
        attended   INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS assignments (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id   INTEGER NOT NULL,
        title        TEXT    NOT NULL,
        description  TEXT,
        days_left    INTEGER NOT NULL DEFAULT 7,
        max_marks    INTEGER DEFAULT 10,
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )''')

    # Per-student submission tracking
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        roll          INTEGER NOT NULL,
        submitted_at  TEXT    DEFAULT (datetime('now')),
        remarks       TEXT,
        UNIQUE(assignment_id, roll),
        FOREIGN KEY (assignment_id) REFERENCES assignments(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS materials (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        title      TEXT    NOT NULL,
        type       TEXT    DEFAULT 'Notes',
        url        TEXT    DEFAULT '#',
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS notices (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        title   TEXT NOT NULL,
        content TEXT,
        date    TEXT DEFAULT (date('now'))
    )''')

    conn.commit()

    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        _seed(c)
        conn.commit()

    conn.close()

STUDENT_NAMES = [
    'Khushal Nagpure', 'Arjun Munde', 'Shreyas Nalavade', 'Aryan Narkhede',
    'Priya Deshmukh', 'Rahul Joshi', 'Sneha Kulkarni', 'Amit Shah',
    'Pooja Mehta', 'Rohan Pawar', 'Neha Gupta', 'Vikram Singh',
    'Ananya Rao', 'Siddharth Nair', 'Divya Iyer', 'Karan Malhotra',
    'Tanvi Bhatt', 'Harsh Verma', 'Riya Saxena', 'Aditya Kumar',
    'Meera Patel', 'Nikhil Sharma', 'Shweta Reddy', 'Varun Bose',
    'Ishaan Chakraborty', 'Pallavi Mishra', 'Tejas Deshpande', 'Sonal Chavan',
    'Gaurav Yadav', 'Ankita Tiwari', 'Parth Sawant', 'Ruchi Kadam',
    'Omkar Lokhande', 'Swati Jadhav', 'Mayur Gaikwad', 'Nikita More',
    'Pratik Shinde', 'Ashwini Kale', 'Sumit Bhosale', 'Kajal Patil',
    'Yash Wagh', 'Priyanka Salve', 'Deepak Fulari', 'Manasi Thorat',
    'Akshay Kharat', 'Rutuja Mhaske', 'Vishal Bansode', 'Komal Jadhav',
    'Tushar Nimbalkar', 'Snehal Dhole',
]

def _seed(c):
    c.execute(
        "INSERT INTO users (username,password,role,name,roll,dept,year) VALUES (?,?,?,?,?,?,?)",
        ('teacher', '123', 'teacher', 'Prof. Sharma', None, 'Computer Engineering', None)
    )

    student_rows = []
    for i, name in enumerate(STUDENT_NAMES):
        roll  = 1001 + i
        if i == 0:
            uname = 'khushal'
        elif i == 2:
            uname = 'shreyas'
        else:
            uname = f'student{i+1}'
        student_rows.append((uname, '123', 'student', name, roll, 'Computer Engineering', 2))

    c.executemany(
        "INSERT INTO users (username,password,role,name,roll,dept,year) VALUES (?,?,?,?,?,?,?)",
        student_rows
    )

    c.executemany("INSERT INTO subjects (code,name,credits) VALUES (?,?,?)", [
        ('AIDS301', 'Advanced Data Structures',        4),
        ('AIDS302', 'Design & Analysis of Algorithms', 4),
        ('AIDS303', 'Database Management Systems',     3),
        ('AIDS304', 'Operating Systems',               3),
        ('AIDS305', 'Computer Networks',               3),
        ('AIDS306', 'Machine Learning',                4),
    ])

    random.seed(42)
    attendance_rows = []
    for i in range(50):
        roll = 1001 + i
        for subj_id in range(1, 7):
            conducted = random.randint(28, 42)
            min_pct   = 0.60 if random.random() < 0.15 else 0.75
            attended  = random.randint(int(conducted * min_pct), conducted)
            attendance_rows.append((roll, subj_id, conducted, attended))

    c.executemany(
        "INSERT INTO attendance (roll,subject_id,conducted,attended) VALUES (?,?,?,?)",
        attendance_rows
    )

    c.executemany(
        "INSERT INTO assignments (subject_id,title,description,days_left,max_marks) VALUES (?,?,?,?,?)",
        [
            (1, 'AVL Tree Implementation',   'Implement AVL tree with all rotations in C++',        1, 10),
            (2, 'Dijkstra Algorithm',         'Implement shortest path on a weighted graph',          3, 15),
            (3, 'ER Diagram — Library DB',    'Design ER diagram for library management system',      5, 10),
            (4, 'Process Scheduling Report',  'Compare FCFS, SJF, Round Robin with examples',        2, 10),
            (5, 'Socket Programming Lab',     'TCP client-server chat application in Python',         7, 20),
            (6, 'ML Mini Project Proposal',   'Submit 1-page proposal for your ML project idea',      4, 10),
        ]
    )

    c.executemany("INSERT INTO materials (subject_id,title,type) VALUES (?,?,?)", [
        (1, 'AVL Trees — Lecture Notes Unit 1',   'Notes'),
        (1, 'Red-Black Trees Explained',           'Notes'),
        (1, 'Heap & Huffman Coding',               'Notes'),
        (2, 'Dynamic Programming Cheatsheet',      'Notes'),
        (2, 'Graph Algorithms Reference',          'PDF'),
        (3, 'SQL Query Practice Set',              'Assignment'),
        (3, 'Normalization 1NF to BCNF',           'Notes'),
        (4, 'Process Management — OS Notes',       'Notes'),
        (5, 'TCP/IP Model Summary',                'Notes'),
        (6, 'Supervised vs Unsupervised Learning', 'Notes'),
        (6, 'Python Scikit-Learn Tutorial',        'PDF'),
    ])

    c.executemany("INSERT INTO notices (title,content) VALUES (?,?)", [
        ('Mid-Sem Exam Schedule Released',  'Mid-semester examinations from 28th April. Check the timetable on the portal.'),
        ('EduSync Platform Launched',       'EduSync now merges VIERP + VOLP into one unified portal. Report bugs to admin.'),
        ('Project Submission Deadline',     'Course project submissions due on 25th April. Upload on EduSync.'),
        ('Attendance Warning',              'Students with attendance below 75% will receive a warning letter.'),
    ])
