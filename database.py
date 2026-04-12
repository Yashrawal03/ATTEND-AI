import sqlite3
import hashlib
from datetime import datetime

DB = "attendance.db"

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        theme TEXT DEFAULT 'dark'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT DEFAULT 'Present',
        subject TEXT DEFAULT 'General'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT DEFAULT 'info',
        is_read INTEGER DEFAULT 0,
        created_at TEXT
    )""")

    # Default teacher account
    c.execute("SELECT id FROM users WHERE id='teacher1'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?,?,?,?,?)",
                  ('teacher1','Prof. Kumar',hash_pw('teacher123'),'teacher','dark'))

    conn.commit()
    conn.close()
    print("[DB] Initialized successfully")

# ── AUTH ────────────────────────────────────────────
def login_user(user_id, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,name,role,theme FROM users WHERE id=? AND password=?",
              (user_id, hash_pw(password)))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def change_password(user_id, old_pw, new_pw):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE id=? AND password=?",
              (user_id, hash_pw(old_pw)))
    if not c.fetchone():
        conn.close()
        return False
    c.execute("UPDATE users SET password=? WHERE id=?", (hash_pw(new_pw), user_id))
    conn.commit()
    conn.close()
    return True

def update_theme(user_id, theme):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET theme=? WHERE id=?", (theme, user_id))
    conn.commit()
    conn.close()

# ── STUDENTS ────────────────────────────────────────
def add_student(student_id, name, password='student123'):
    """Add student to students table AND users table."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO students VALUES (?,?)", (student_id, name))
    c.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?)",
              (student_id, name, hash_pw(password), 'student', 'dark'))
    conn.commit()
    conn.close()
    print(f"[DB] Student added/ensured: {student_id} ({name})")

def get_students():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name FROM students ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def student_exists(student_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM students WHERE id=?", (student_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def delete_student(student_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    c.execute("DELETE FROM users WHERE id=?", (student_id,))
    conn.commit()
    conn.close()

# ── ATTENDANCE ──────────────────────────────────────
def mark_attendance(student_id, date_str, status='Present', subject='General'):
    """Mark or update attendance. Always ensures student exists first."""
    conn = get_conn()
    c = conn.cursor()
    # Ensure student exists in DB
    c.execute("SELECT id FROM students WHERE id=?", (student_id,))
    if not c.fetchone():
        conn.close()
        print(f"[DB] Warning: student {student_id} not found, cannot mark attendance")
        return False
    # Upsert attendance
    c.execute("""SELECT id FROM attendance
                 WHERE student_id=? AND date=? AND subject=?""",
              (student_id, date_str, subject))
    existing = c.fetchone()
    if existing:
        c.execute("""UPDATE attendance SET status=?
                     WHERE student_id=? AND date=? AND subject=?""",
                  (status, student_id, date_str, subject))
    else:
        c.execute("""INSERT INTO attendance (student_id,date,status,subject)
                     VALUES (?,?,?,?)""",
                  (student_id, date_str, status, subject))
    conn.commit()
    conn.close()
    print(f"[DB] Attendance marked: {student_id} → {status} on {date_str} ({subject})")
    return True

def get_attendance(date_str, subject=None):
    conn = get_conn()
    c = conn.cursor()
    sub_filter = f"AND a.subject='{subject}'" if subject else ""
    c.execute(f"""
        SELECT s.id, s.name,
               COALESCE(a.status,'Absent') as status
        FROM students s
        LEFT JOIN attendance a
          ON s.id=a.student_id AND a.date=? {sub_filter}
        ORDER BY s.name
    """, (date_str,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_attendance(student_id):
    """Get all attendance records for a student."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT date, status, subject
                 FROM attendance
                 WHERE student_id=?
                 ORDER BY date DESC""", (student_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_stats(student_id):
    """Get attendance statistics for a student."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM attendance WHERE student_id=?",
              (student_id,))
    total = c.fetchone()['total']
    c.execute("""SELECT COUNT(*) as p FROM attendance
                 WHERE student_id=? AND status='Present'""", (student_id,))
    present = c.fetchone()['p']
    conn.close()
    absent = total - present
    pct = round(present / total * 100, 1) if total > 0 else 0
    needed = 0
    if pct < 75 and total > 0:
        needed = max(0, int((0.75 * total - present) / 0.25) + 1)
    return {
        "total": total,
        "present": present,
        "absent": absent,
        "percentage": pct,
        "classes_needed": needed
    }

def get_monthly_summary(year, month):
    conn = get_conn()
    c = conn.cursor()
    month_str = f"{year}-{str(month).zfill(2)}"
    c.execute("""
        SELECT s.id, s.name,
               COUNT(a.id) as total,
               SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present
        FROM students s
        LEFT JOIN attendance a
          ON s.id=a.student_id AND a.date LIKE ?
        GROUP BY s.id
        ORDER BY s.name
    """, (f"{month_str}%",))
    rows = c.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['absent'] = d['total'] - d['present']
        d['percentage'] = round(d['present'] / d['total'] * 100, 1) if d['total'] > 0 else 0
        result.append(d)
    return result

def get_defaulters(threshold=75):
    students = get_students()
    out = []
    for s in students:
        stats = get_student_stats(s['id'])
        if stats['total'] > 0 and stats['percentage'] < threshold:
            out.append({**s, **stats})
    return sorted(out, key=lambda x: x['percentage'])

# ── NOTIFICATIONS ───────────────────────────────────
def add_notification(user_id, message, ntype='info'):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO notifications (user_id,message,type,created_at)
                 VALUES (?,?,?,?)""",
              (user_id, message, ntype,
               datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()

def get_notifications(user_id, limit=30):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT * FROM notifications WHERE user_id=?
                 ORDER BY created_at DESC LIMIT ?""", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_notifs_read(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def count_unread(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT COUNT(*) as n FROM notifications
                 WHERE user_id=? AND is_read=0""", (user_id,))
    n = c.fetchone()['n']
    conn.close()
    return n

def check_and_notify_at_risk(student_id):
    stats = get_student_stats(student_id)
    if stats['total'] > 0 and stats['percentage'] < 75:
        msg = (f"⚠️ Attendance dropped to {stats['percentage']}%. "
               f"Need {stats['classes_needed']} more classes to reach 75%.")
        add_notification(student_id, msg, 'warning')
        # Also notify teacher
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT name FROM students WHERE id=?", (student_id,))
        row = c.fetchone()
        conn.close()
        if row:
            add_notification(
                'teacher1',
                f"🚨 {row['name']} ({student_id}) is at {stats['percentage']}% attendance.",
                'danger'
            )