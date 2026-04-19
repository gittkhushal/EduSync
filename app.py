"""
app.py — EduSync: Unified College Portal
Merges VIERP (ERP) + VOLP (LMS) into one system

Data Structures Used (per syllabus):
  Unit 1 — AVL Tree     : Student records (O log n search)
  Unit 2 — Fibonacci Heap: Assignment priority queue
  Unit 3 — Trie         : Material prefix search
  Unit 4 — Skip List    : Attendance storage
  Unit 5 — Segment Tree : Attendance range queries
  Unit 6 — Union-Find   : Student project group management
"""

from flask import (Flask, render_template, request,
                   redirect, url_for, session, flash)
from database import get_db, init_db
from ds.avl  import AVLTree
from ds.trie import Trie, SkipList, SegmentTree, UnionFind
from ds.heap import FibonacciHeap, AssignmentHeap

# ── App setup ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'edusync_secret_2024'   # Required for session

# ── Initialise database ────────────────────────────────────
init_db()

# ── Build in-memory data structures on startup ─────────────

# Unit 1: AVL Tree — load all students
avl_tree = AVLTree()
avl_root = None

# Unit 3: Trie — load all materials
material_trie = Trie()

# Unit 2: Fibonacci Heap — load all assignments
fib_heap = FibonacciHeap()

# Unit 4: Skip List — attendance records
skip_list = SkipList()

# Populate from DB
with app.app_context():
    db = get_db()

    # AVL Tree — insert students
    for row in db.execute("SELECT roll, name, dept, year FROM users WHERE role='student'"):
        if row['roll']:
            avl_root = avl_tree.insert(avl_root, row['roll'], row['name'],
                                       row['dept'] or 'CE', row['year'] or 2)

    # Trie — insert materials
    for row in db.execute("SELECT m.title, s.name AS subj FROM materials m JOIN subjects s ON m.subject_id=s.id"):
        material_trie.insert(row['title'], row['title'])
        material_trie.insert(row['subj'], row['subj'])

    # Fibonacci Heap — insert assignments
    for row in db.execute("SELECT a.title, a.days_left, s.code FROM assignments a JOIN subjects s ON a.subject_id=s.id"):
        fib_heap.insert(row['days_left'], row['title'], row['code'])

    # Skip List — attendance
    for row in db.execute("SELECT roll, conducted, attended FROM attendance"):
        if row['conducted'] > 0:
            pct = round(row['attended'] / row['conducted'] * 100, 1)
            skip_list.insert(row['roll'], pct)

    db.close()

# Unit 5: Segment Tree — attendance percentages
with app.app_context():
    db = get_db()
    rows = db.execute(
        "SELECT conducted, attended FROM attendance WHERE roll=1001 ORDER BY subject_id"
    ).fetchall()
    attn_data = [round(r['attended']/r['conducted']*100) for r in rows if r['conducted'] > 0]
    seg_tree  = SegmentTree(attn_data)
    db.close()

# Unit 6: Union-Find — project groups (demo with 4 students)
uf     = UnionFind(4)
uf.union(0, 1)   # Khushal + Arjun in one group
uf.union(2, 3)   # Shreyas + Aryan in another group


# ══════════════════════════════════════════════════════════
#  Authentication Routes
# ══════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Redirect to dashboard if logged in, else login"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        db   = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        db.close()

        if user:
            # Store user info in session
            session['user']     = dict(user)
            session['username'] = user['username']
            session['role']     = user['role']
            session['name']     = user['name']
            session['roll']     = user['roll']

            if user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html',
                                   error="Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ══════════════════════════════════════════════════════════
#  Student Routes
# ══════════════════════════════════════════════════════════

def student_required(f):
    """Decorator to protect student routes"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard — VIERP-style module grid"""
    db      = get_db()
    roll    = session.get('roll', 1001)

    # Summary stats
    attn_rows = db.execute(
        "SELECT conducted, attended FROM attendance WHERE roll=?", (roll,)
    ).fetchall()

    total_conducted = sum(r['conducted'] for r in attn_rows)
    total_attended  = sum(r['attended']  for r in attn_rows)
    avg_attendance  = round(total_attended / total_conducted * 100, 1) if total_conducted else 0

    pending_assignments = db.execute(
        "SELECT COUNT(*) as cnt FROM assignments WHERE submitted=0"
    ).fetchone()['cnt']

    notices = db.execute(
        "SELECT * FROM notices ORDER BY id DESC LIMIT 3"
    ).fetchall()

    total_subjects = db.execute("SELECT COUNT(*) as cnt FROM subjects").fetchone()['cnt']

    db.close()

    # Segment Tree query: average attendance first 3 subjects
    seg_avg = seg_tree.range_average(0, 2) if len(attn_data) >= 3 else avg_attendance

    return render_template('dashboard.html',
        name               = session.get('name', 'Student'),
        avg_attendance     = avg_attendance,
        pending_assignments= pending_assignments,
        total_subjects     = total_subjects,
        notices            = notices,
        seg_avg            = seg_avg,
    )

@app.route('/attendance')
@student_required
def attendance():
    """Attendance page with subject-wise breakdown"""
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
            # How many more to attend to reach 75%?
            # (attended + x) / (conducted + x) = 0.75
            needed = max(0, int((0.75 * r['conducted'] - r['attended']) / 0.25))

        subjects.append({
            'code':      r['code'],
            'name':      r['name'],
            'conducted': r['conducted'],
            'attended':  r['attended'],
            'pct':       pct,
            'needed':    needed,
            'status':    'safe' if pct >= 75 else 'danger'
        })

    db.close()

    # Skip List demo — lookup this student's avg
    skip_pct = skip_list.search(roll)

    return render_template('attendance.html',
        subjects  = subjects,
        skip_pct  = skip_pct,
    )

@app.route('/assignments')
@student_required
def assignments():
    """Assignments sorted by Fibonacci Heap (nearest deadline first)"""
    db = get_db()

    rows = db.execute('''
        SELECT a.id, a.title, a.description, a.days_left, a.max_marks, a.submitted,
               s.code, s.name as subject_name
        FROM   assignments a
        JOIN   subjects    s ON a.subject_id = s.id
        ORDER  BY a.days_left ASC
    ''').fetchall()

    assignments_list = [dict(r) for r in rows]
    db.close()

    # Fibonacci Heap sorted list
    fib_sorted = fib_heap.get_all_sorted()

    return render_template('assignments.html',
        assignments = assignments_list,
        fib_sorted  = fib_sorted,
    )

@app.route('/materials', methods=['GET', 'POST'])
@student_required
def materials():
    """Study materials with Trie-powered search"""
    db      = get_db()
    results = []
    query   = ''

    if request.method == 'POST':
        query   = request.form.get('query', '').strip()
        # Trie prefix search
        trie_hits = material_trie.search_prefix(query)
        titles    = [h['data'] for h in trie_hits]

        rows = db.execute('''
            SELECT m.id, m.title, m.type, s.code, s.name as subject_name
            FROM   materials m
            JOIN   subjects  s ON m.subject_id = s.id
            WHERE  LOWER(m.title) LIKE ?
            ORDER  BY m.subject_id
        ''', ('%' + query.lower() + '%',)).fetchall()
        results = [dict(r) for r in rows]
    else:
        rows = db.execute('''
            SELECT m.id, m.title, m.type, s.code, s.name as subject_name
            FROM   materials m
            JOIN   subjects  s ON m.subject_id = s.id
            ORDER  BY m.subject_id
        ''').fetchall()
        results = [dict(r) for r in rows]

    db.close()
    return render_template('materials.html', results=results, query=query)

@app.route('/student_search', methods=['GET'])
@student_required
def student_search():
    """Search student by roll — AVL Tree O(log n)"""
    roll_str = request.args.get('roll', '').strip()
    found    = None
    if roll_str.isdigit():
        node = avl_tree.search(avl_root, int(roll_str))
        if node:
            found = {'roll': node.roll, 'name': node.name,
                     'dept': node.dept, 'year': node.year}
    all_students = avl_tree.inorder(avl_root)
    return render_template('student_search.html',
        found=found, roll=roll_str, all_students=all_students)

@app.route('/groups')
@student_required
def groups():
    """Project groups using Union-Find"""
    labels = ['Khushal', 'Arjun', 'Shreyas', 'Aryan']
    group_list = uf.get_groups(labels)
    return render_template('groups.html', groups=group_list)


# ══════════════════════════════════════════════════════════
#  Teacher Routes
# ══════════════════════════════════════════════════════════

@app.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    db = get_db()
    total_students   = db.execute("SELECT COUNT(*) as c FROM users WHERE role='student'").fetchone()['c']
    total_assignments= db.execute("SELECT COUNT(*) as c FROM assignments").fetchone()['c']
    total_materials  = db.execute("SELECT COUNT(*) as c FROM materials").fetchone()['c']
    subjects         = db.execute("SELECT * FROM subjects").fetchall()
    assignments      = db.execute('''
        SELECT a.*, s.name as subject_name FROM assignments a
        JOIN subjects s ON a.subject_id=s.id ORDER BY a.days_left
    ''').fetchall()
    db.close()

    return render_template('teacher.html',
        name             = session.get('name', 'Teacher'),
        total_students   = total_students,
        total_assignments= total_assignments,
        total_materials  = total_materials,
        subjects         = subjects,
        assignments      = assignments,
    )

@app.route('/teacher/add_assignment', methods=['POST'])
def add_assignment():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    subject_id  = request.form.get('subject_id')
    title       = request.form.get('title')
    description = request.form.get('description', '')
    days_left   = request.form.get('days_left', 7)

    db = get_db()
    db.execute(
        "INSERT INTO assignments (subject_id,title,description,days_left) VALUES (?,?,?,?)",
        (subject_id, title, description, days_left)
    )
    db.commit()
    db.close()

    # Also push to Fibonacci Heap
    subj = get_db().execute("SELECT code FROM subjects WHERE id=?", (subject_id,)).fetchone()
    code = subj['code'] if subj else ''
    fib_heap.insert(int(days_left), title, code)

    return redirect(url_for('teacher_dashboard'))

@app.route('/teacher/add_material', methods=['POST'])
def add_material():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    subject_id = request.form.get('subject_id')
    title      = request.form.get('title')
    mat_type   = request.form.get('type', 'Notes')

    db = get_db()
    db.execute(
        "INSERT INTO materials (subject_id,title,type) VALUES (?,?,?)",
        (subject_id, title, mat_type)
    )
    db.commit()
    db.close()

    # Insert into Trie
    material_trie.insert(title, title)

    return redirect(url_for('teacher_dashboard'))


# ══════════════════════════════════════════════════════════
#  Run
# ══════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True)
