"""
app.py — EduSync v3: Unified College Portal
Merges VIERP (ERP) + VOLP (LMS) into one system
"""

from __future__ import annotations
from flask import (Flask, render_template, request,
                   redirect, url_for, session, flash, jsonify)
from functools import wraps
from database import get_db, init_db
from ds import AVLTree, FibonacciHeap, Trie, SkipList, SegmentTree, UnionFind

app = Flask(__name__)
app.secret_key = 'edusync_secret_v3'

init_db()

# ── In-memory DS state ─────────────────────────────────────────
avl_tree     : AVLTree       = AVLTree()
avl_root                     = None
material_trie: Trie          = Trie()
fib_heap     : FibonacciHeap = FibonacciHeap()
skip_list    : SkipList      = SkipList()
seg_tree     : SegmentTree | None = None
attn_data    : list[float]   = []
uf           : UnionFind     = UnionFind(4)

def _build_ds():
    global avl_root, seg_tree, attn_data
    db = get_db()

    for row in db.execute(
        "SELECT roll, name, dept, year FROM users WHERE role='student'"
    ):
        if row['roll']:
            avl_root = avl_tree.insert(
                avl_root, row['roll'], row['name'],
                row['dept'] or 'CE', row['year'] or 2
            )

    for row in db.execute(
        "SELECT m.title, s.name AS subj FROM materials m "
        "JOIN subjects s ON m.subject_id = s.id"
    ):
        material_trie.insert(row['title'], row['title'])
        material_trie.insert(row['subj'],  row['subj'])

    for row in db.execute(
        "SELECT a.title, a.days_left, s.code "
        "FROM assignments a JOIN subjects s ON a.subject_id = s.id"
    ):
        fib_heap.insert(row['days_left'], row['title'], row['code'])

    for row in db.execute(
        "SELECT roll, conducted, attended FROM attendance"
    ):
        if row['conducted'] > 0:
            pct = round(row['attended'] / row['conducted'] * 100, 1)
            skip_list.insert(row['roll'], pct)

    rows = db.execute(
        "SELECT conducted, attended FROM attendance "
        "WHERE roll=1001 ORDER BY subject_id"
    ).fetchall()
    attn_data = [
        round(r['attended'] / r['conducted'] * 100)
        for r in rows if r['conducted'] > 0
    ]
    seg_tree = SegmentTree(attn_data)

    uf.union(0, 1)
    uf.union(2, 3)
    db.close()

_build_ds()


# ── Auth helpers ───────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner

def teacher_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if session.get('role') != 'teacher':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner


# ── Auth Routes ────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for(
            'teacher_dashboard' if session['role'] == 'teacher'
            else 'dashboard'
        ))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username', '').strip()
        passw = request.form.get('password', '').strip()
        db    = get_db()
        user  = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (uname, passw)
        ).fetchone()
        db.close()

        if user:
            session.update({
                'user':     dict(user),
                'username': user['username'],
                'role':     user['role'],
                'name':     user['name'],
                'roll':     user['roll'],
            })
            return redirect(url_for(
                'teacher_dashboard' if user['role'] == 'teacher'
                else 'dashboard'
            ))
        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── Student Routes ─────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    db   = get_db()
    roll = session.get('roll', 1001)

    attn_rows = db.execute(
        "SELECT conducted, attended FROM attendance WHERE roll=?", (roll,)
    ).fetchall()

    total_c = sum(r['conducted'] for r in attn_rows)
    total_a = sum(r['attended']  for r in attn_rows)
    avg_att = round(total_a / total_c * 100, 1) if total_c else 0

    # Count pending for THIS student
    all_assignments = db.execute("SELECT id FROM assignments").fetchall()
    submitted_ids   = {
        r['assignment_id'] for r in db.execute(
            "SELECT assignment_id FROM submissions WHERE roll=?", (roll,)
        ).fetchall()
    }
    pending = sum(1 for a in all_assignments if a['id'] not in submitted_ids)

    notices = db.execute(
        "SELECT * FROM notices ORDER BY id DESC LIMIT 3"
    ).fetchall()

    total_subjects = db.execute(
        "SELECT COUNT(*) AS c FROM subjects"
    ).fetchone()['c']

    seg_avg = (seg_tree.range_average(0, 2)
               if seg_tree and len(attn_data) >= 3
               else avg_att)

    db.close()

    return render_template('dashboard.html',
        name                = session.get('name', 'Student'),
        avg_attendance      = avg_att,
        pending_assignments = pending,
        total_subjects      = total_subjects,
        notices             = notices,
        seg_avg             = seg_avg,
    )

@app.route('/attendance')
@login_required
def attendance():
    db   = get_db()
    roll = session.get('roll', 1001)

    rows = db.execute('''
        SELECT s.code, s.name, a.conducted, a.attended
        FROM   attendance a
        JOIN   subjects   s ON a.subject_id = s.id
        WHERE  a.roll = ?
        ORDER  BY s.id
    ''', (roll,)).fetchall()

    subjects = []
    for r in rows:
        pct    = round(r['attended'] / r['conducted'] * 100, 1) if r['conducted'] else 0
        needed = 0
        if pct < 75 and r['conducted'] > 0:
            needed = max(0, int((0.75 * r['conducted'] - r['attended']) / 0.25))
        subjects.append({
            'code':      r['code'],
            'name':      r['name'],
            'conducted': r['conducted'],
            'attended':  r['attended'],
            'pct':       pct,
            'needed':    needed,
            'status':    'safe' if pct >= 75 else 'danger',
        })

    db.close()
    return render_template('attendance.html', subjects=subjects)

@app.route('/assignments')
@login_required
def assignments():
    db   = get_db()
    roll = session.get('roll', 1001)

    rows = db.execute('''
        SELECT a.id, a.title, a.description, a.days_left, a.max_marks,
               s.code, s.name AS subject_name
        FROM   assignments a
        JOIN   subjects    s ON a.subject_id = s.id
        ORDER  BY a.days_left ASC
    ''').fetchall()

    submitted_ids = {
        r['assignment_id'] for r in db.execute(
            "SELECT assignment_id FROM submissions WHERE roll=?", (roll,)
        ).fetchall()
    }
    db.close()

    assignment_list = []
    for r in rows:
        d = dict(r)
        d['submitted'] = r['id'] in submitted_ids
        assignment_list.append(d)

    return render_template('assignments.html',
        assignments   = assignment_list,
        submitted_ids = submitted_ids,
    )

@app.route('/assignments/submit/<int:aid>', methods=['POST'])
@login_required
def submit_assignment(aid: int):
    roll    = session.get('roll', 1001)
    remarks = request.form.get('remarks', '').strip()
    db      = get_db()
    try:
        db.execute(
            "INSERT OR IGNORE INTO submissions (assignment_id, roll, remarks) VALUES (?,?,?)",
            (aid, roll, remarks)
        )
        db.commit()
        flash('Assignment submitted successfully! ✅', 'success')
    except Exception as e:
        flash(f'Error submitting assignment: {e}', 'danger')
    finally:
        db.close()
    return redirect(url_for('assignments'))

@app.route('/materials', methods=['GET', 'POST'])
@login_required
def materials():
    db    = get_db()
    query = request.form.get('query', '').strip() if request.method == 'POST' else ''

    if query:
        _ = material_trie.search_prefix(query)
        rows = db.execute('''
            SELECT m.id, m.title, m.type, s.code, s.name AS subject_name
            FROM   materials m
            JOIN   subjects  s ON m.subject_id = s.id
            WHERE  LOWER(m.title) LIKE ? OR LOWER(s.name) LIKE ?
            ORDER  BY m.subject_id
        ''', (f'%{query.lower()}%', f'%{query.lower()}%')).fetchall()
    else:
        rows = db.execute('''
            SELECT m.id, m.title, m.type, s.code, s.name AS subject_name
            FROM   materials m
            JOIN   subjects  s ON m.subject_id = s.id
            ORDER  BY m.subject_id
        ''').fetchall()

    db.close()
    return render_template('materials.html',
        results = [dict(r) for r in rows],
        query   = query,
    )

@app.route('/student_search')
@login_required
def student_search():
    roll_str = request.args.get('roll', '').strip()
    found    = None
    if roll_str.isdigit():
        found = avl_tree.search(avl_root, int(roll_str))

    all_students = avl_tree.inorder(avl_root)
    return render_template('student_search.html',
        found=found, roll=roll_str, all_students=all_students)




# ── JSON API Endpoints ─────────────────────────────────────────

@app.route('/api/search')
@login_required
def api_search():
    q    = request.args.get('q', '').strip()
    hits = material_trie.search_prefix(q) if q else []
    return jsonify(hits)

@app.route('/api/assignments')
@login_required
def api_assignments():
    return jsonify(fib_heap.get_all_sorted())

@app.route('/api/attendance_alert')
@login_required
def api_attendance_alert():
    db   = get_db()
    roll = session.get('roll', 1001)
    rows = db.execute(
        "SELECT conducted, attended FROM attendance WHERE roll=?", (roll,)
    ).fetchall()
    db.close()
    low = sum(
        1 for r in rows
        if r['conducted'] > 0
        and round(r['attended'] / r['conducted'] * 100, 1) < 75
    )
    return jsonify({'low_attendance_count': low})


# ── Teacher Routes ─────────────────────────────────────────────

@app.route('/teacher')
@teacher_required
def teacher_dashboard():
    db = get_db()
    total_students    = db.execute("SELECT COUNT(*) AS c FROM users WHERE role='student'").fetchone()['c']
    total_assignments = db.execute("SELECT COUNT(*) AS c FROM assignments").fetchone()['c']
    total_materials   = db.execute("SELECT COUNT(*) AS c FROM materials").fetchone()['c']
    subjects          = db.execute("SELECT * FROM subjects").fetchall()

    assignments = db.execute('''
        SELECT a.id, a.title, a.description, a.days_left, a.max_marks,
               s.name AS subject_name, s.code
        FROM assignments a JOIN subjects s ON a.subject_id = s.id
        ORDER BY a.days_left
    ''').fetchall()

    # Submission count per assignment
    submission_counts = {}
    for row in db.execute(
        "SELECT assignment_id, COUNT(*) AS cnt FROM submissions GROUP BY assignment_id"
    ).fetchall():
        submission_counts[row['assignment_id']] = row['cnt']

    students = db.execute(
        "SELECT roll, name, dept, year FROM users WHERE role='student' ORDER BY roll"
    ).fetchall()

    # Per-student: which assignments submitted
    all_assignment_ids = [a['id'] for a in assignments]
    student_submissions = {}
    for row in db.execute("SELECT roll, assignment_id FROM submissions").fetchall():
        student_submissions.setdefault(row['roll'], set()).add(row['assignment_id'])

    db.close()

    assignment_list = []
    for a in assignments:
        d = dict(a)
        d['submission_count'] = submission_counts.get(a['id'], 0)
        assignment_list.append(d)

    student_list = []
    for s in students:
        submitted = len(student_submissions.get(s['roll'], set()))
        student_list.append({
            'roll':      s['roll'],
            'name':      s['name'],
            'dept':      s['dept'],
            'year':      s['year'],
            'submitted': submitted,
            'total':     total_assignments,
        })

    return render_template('teacher.html',
        name              = session.get('name', 'Teacher'),
        total_students    = total_students,
        total_assignments = total_assignments,
        total_materials   = total_materials,
        subjects          = subjects,
        assignments       = assignment_list,
        students          = student_list,
    )

@app.route('/teacher/submissions/<int:aid>')
@teacher_required
def view_submissions(aid: int):
    db  = get_db()
    assignment = db.execute(
        "SELECT a.*, s.name AS subject_name FROM assignments a "
        "JOIN subjects s ON a.subject_id = s.id WHERE a.id=?", (aid,)
    ).fetchone()

    submissions = db.execute('''
        SELECT u.name, u.roll, sub.submitted_at, sub.remarks
        FROM   submissions sub
        JOIN   users u ON u.roll = sub.roll
        WHERE  sub.assignment_id = ?
        ORDER  BY sub.submitted_at DESC
    ''', (aid,)).fetchall()

    # Students who haven't submitted
    all_students = db.execute(
        "SELECT roll, name FROM users WHERE role='student' ORDER BY roll"
    ).fetchall()
    submitted_rolls = {r['roll'] for r in submissions}
    pending_students = [s for s in all_students if s['roll'] not in submitted_rolls]

    db.close()
    return render_template('submissions.html',
        assignment       = dict(assignment),
        submissions      = [dict(r) for r in submissions],
        pending_students = [dict(s) for s in pending_students],
    )

@app.route('/teacher/add_assignment', methods=['POST'])
@teacher_required
def add_assignment():
    subject_id  = request.form.get('subject_id')
    title       = request.form.get('title', '').strip()
    description = request.form.get('description', '')
    days_left   = int(request.form.get('days_left', 7))

    if not title:
        flash('Title is required.', 'danger')
        return redirect(url_for('teacher_dashboard'))

    db = get_db()
    db.execute(
        "INSERT INTO assignments (subject_id,title,description,days_left) VALUES (?,?,?,?)",
        (subject_id, title, description, days_left)
    )
    db.commit()
    subj = db.execute("SELECT code FROM subjects WHERE id=?", (subject_id,)).fetchone()
    db.close()

    code = subj['code'] if subj else ''
    fib_heap.insert(days_left, title, code)
    flash(f'Assignment "{title}" added successfully! Students can now see and submit it.', 'success')
    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/delete_assignment/<int:aid>', methods=['POST'])
@teacher_required
def delete_assignment(aid: int):
    db = get_db()
    db.execute("DELETE FROM submissions WHERE assignment_id=?", (aid,))
    db.execute("DELETE FROM assignments WHERE id=?", (aid,))
    db.commit()
    db.close()
    flash('Assignment deleted.', 'info')
    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/attendance', methods=['GET'])
@teacher_required
def teacher_attendance():
    db = get_db()
    students = db.execute(
        "SELECT roll, name FROM users WHERE role='student' ORDER BY roll"
    ).fetchall()
    subjects = db.execute("SELECT * FROM subjects ORDER BY id").fetchall()

    selected_subject = request.args.get('subject_id', type=int)
    selected_date    = request.args.get('date', '')

    records = []
    if selected_subject:
        for s in students:
            row = db.execute(
                "SELECT conducted, attended FROM attendance WHERE roll=? AND subject_id=?",
                (s['roll'], selected_subject)
            ).fetchone()
            records.append({
                'roll':      s['roll'],
                'name':      s['name'],
                'conducted': row['conducted'] if row else 0,
                'attended':  row['attended']  if row else 0,
            })
    db.close()
    return render_template('teacher_attendance.html',
        students         = [dict(s) for s in students],
        subjects         = [dict(s) for s in subjects],
        selected_subject = selected_subject,
        selected_date    = selected_date,
        records          = records,
    )


@app.route('/teacher/attendance/mark', methods=['POST'])
@teacher_required
def mark_attendance():
    subject_id = int(request.form.get('subject_id'))
    db = get_db()
    students = db.execute(
        "SELECT roll FROM users WHERE role='student'"
    ).fetchall()

    for s in students:
        roll   = s['roll']
        status = request.form.get(f'status_{roll}', 'absent')

        existing = db.execute(
            "SELECT id FROM attendance WHERE roll=? AND subject_id=?",
            (roll, subject_id)
        ).fetchone()

        if existing:
            if status == 'present':
                db.execute(
                    "UPDATE attendance SET conducted=conducted+1, attended=attended+1 WHERE roll=? AND subject_id=?",
                    (roll, subject_id)
                )
            else:
                db.execute(
                    "UPDATE attendance SET conducted=conducted+1 WHERE roll=? AND subject_id=?",
                    (roll, subject_id)
                )
        else:
            attended = 1 if status == 'present' else 0
            db.execute(
                "INSERT INTO attendance (roll, subject_id, conducted, attended) VALUES (?,?,1,?)",
                (roll, subject_id, attended)
            )

    db.commit()
    db.close()

    # rebuild segment tree
    global seg_tree, attn_data
    db2 = get_db()
    rows = db2.execute(
        "SELECT conducted, attended FROM attendance WHERE roll=1001 ORDER BY subject_id"
    ).fetchall()
    attn_data = [round(r['attended']/r['conducted']*100) for r in rows if r['conducted'] > 0]
    seg_tree  = SegmentTree(attn_data)
    db2.close()

    flash('Attendance marked successfully! ✅', 'success')
    return redirect(url_for('teacher_attendance', subject_id=subject_id))


@app.route('/teacher/add_material', methods=['POST'])
@teacher_required
def add_material():
    subject_id = request.form.get('subject_id')
    title      = request.form.get('title', '').strip()
    mat_type   = request.form.get('type', 'Notes')

    if not title:
        flash('Title is required.', 'danger')
        return redirect(url_for('teacher_dashboard'))

    db = get_db()
    db.execute(
        "INSERT INTO materials (subject_id,title,type) VALUES (?,?,?)",
        (subject_id, title, mat_type)
    )
    db.commit()
    db.close()

    material_trie.insert(title, title)
    flash(f'Material "{title}" added successfully!', 'success')
    return redirect(url_for('teacher_dashboard'))


@app.route('/api/ds_info')
@login_required
def api_ds_info():
    info = {
        'attendance': {
            'name':  'Segment Tree',
            'icon':  '🌲',
            'desc':  'Your attendance percentages are stored in a Segment Tree, enabling instant range queries — e.g. "average attendance across subjects 1–4" in O(log n) time.',
            'complexity': 'Query: O(log n) · Build: O(n)',
        },
        'assignments': {
            'name':  'Fibonacci Heap',
            'icon':  '🔢',
            'desc':  'Assignments are prioritised using a Fibonacci Heap so the one with the nearest deadline always surfaces first — extract-min runs in O(log n) amortised.',
            'complexity': 'Insert: O(1) · Extract-min: O(log n)',
        },
        'materials': {
            'name':  'Trie (Prefix Tree)',
            'icon':  '🔤',
            'desc':  'The search bar on Materials uses a Trie for real-time prefix matching. Every keystroke traverses the tree in O(k) — where k is the length of your query.',
            'complexity': 'Search: O(k) · Insert: O(k)',
        },
        'student_search': {
            'name':  'AVL Tree',
            'icon':  '⚖️',
            'desc':  'All student records are indexed in a self-balancing AVL Tree keyed by roll number, guaranteeing O(log n) search regardless of how many students are enrolled.',
            'complexity': 'Search/Insert/Delete: O(log n)',
        },
    }
    return jsonify(info)


# ── Run ────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
