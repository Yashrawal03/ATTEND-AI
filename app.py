from flask import (Flask, request, jsonify, render_template,
                   session, send_from_directory, Response)
from flask_cors import CORS
from datetime import date
import database, face_utils
import os, functools, csv, io, base64

app = Flask(__name__)
app.secret_key = "edutrack_lms_secret_2025"
CORS(app, supports_credentials=True)
database.init_db()

FACE_DATA_DIR = "face_data"
os.makedirs(FACE_DATA_DIR, exist_ok=True)


# ── helpers ─────────────────────────────────────────
def login_required(role=None):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if "user" not in session:
                return jsonify({"error": "Not logged in"}), 401
            if role:
                allowed = role if isinstance(role, list) else [role]
                if session["user"]["role"] not in allowed:
                    return jsonify({"error": "Access denied"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def ensure_student_in_db(student_id):
    """
    Auto-add student to DB if they exist in face_data but not in DB.
    This is the KEY fix — without this, mark_attendance silently fails.
    """
    if not database.student_exists(student_id):
        # Find name from face_data folder name
        name = student_id
        if os.path.exists(FACE_DATA_DIR):
            for folder in os.listdir(FACE_DATA_DIR):
                if folder.startswith(student_id + "_"):
                    parts = folder.split("_", 1)
                    name = parts[1].replace("_", " ") if len(parts) > 1 else student_id
                    break
        database.add_student(student_id, name, "student123")
        print(f"[auto-add] Created DB entry: {student_id} ({name})")
        database.add_notification(
            'teacher1',
            f"ℹ️ Auto-added {name} ({student_id}) to database from face recognition.",
            'info'
        )
        return name
    return None


# ── pages ────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── auth ─────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json or {}
    user = database.login_user(data.get("id", ""), data.get("password", ""))
    if user:
        session["user"] = user
        return jsonify({**user, "unread": database.count_unread(user["id"])})
    return jsonify({"error": "Invalid ID or password"}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/me")
def me():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({**session["user"],
                    "unread": database.count_unread(session["user"]["id"])})


@app.route("/api/change-password", methods=["POST"])
@login_required()
def change_password():
    data = request.json or {}
    ok = database.change_password(
        session["user"]["id"],
        data.get("old_password", ""),
        data.get("new_password", "")
    )
    if ok:
        return jsonify({"message": "Password changed!"})
    return jsonify({"error": "Old password is incorrect"}), 400


@app.route("/api/theme", methods=["POST"])
@login_required()
def set_theme():
    theme = (request.json or {}).get("theme", "dark")
    database.update_theme(session["user"]["id"], theme)
    session["user"]["theme"] = theme
    return jsonify({"theme": theme})


# ── students ─────────────────────────────────────────
@app.route("/api/students", methods=["GET"])
@login_required()
def get_students():
    return jsonify(database.get_students())


@app.route("/api/students", methods=["POST"])
@login_required(role="teacher")
def add_student():
    try:
        d = request.json or {}
        sid  = d.get("id",   "").strip()
        name = d.get("name", "").strip()
        pw   = d.get("password", "student123").strip() or "student123"
        if not sid or not name:
            return jsonify({"error": "ID and name required"}), 400
        database.add_student(sid, name, pw)
        # Create face_data folder
        safe = name.replace(" ", "_")
        os.makedirs(os.path.join(FACE_DATA_DIR, f"{sid}_{safe}"), exist_ok=True)
        database.add_notification(
            session["user"]["id"],
            f"✅ Student {name} ({sid}) added. Password: {pw}", "success")
        return jsonify({
            "message": f"Student {name} added. Login: {sid} / {pw}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/students/<sid>", methods=["DELETE"])
@login_required(role="teacher")
def delete_student(sid):
    database.delete_student(sid)
    face_utils.delete_student_photos(sid)
    return jsonify({"ok": True})


# ── sync face_data → DB ──────────────────────────────
@app.route("/api/sync-students", methods=["POST"])
@login_required(role="teacher")
def sync_students():
    """Scan face_data/ and add every student folder to DB if missing."""
    synced = []
    existing_ids = [s["id"] for s in database.get_students()]

    if not os.path.exists(FACE_DATA_DIR):
        return jsonify({"message": "face_data folder not found", "synced": []})

    for folder in os.listdir(FACE_DATA_DIR):
        folder_path = os.path.join(FACE_DATA_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        parts = folder.split("_", 1)
        student_id = parts[0]
        name = parts[1].replace("_", " ") if len(parts) > 1 else student_id

        if student_id not in existing_ids:
            database.add_student(student_id, name, "student123")
            synced.append({"id": student_id, "name": name})
            existing_ids.append(student_id)

    if synced:
        names = ", ".join(s["name"] for s in synced)
        database.add_notification(session["user"]["id"],
                                  f"✅ Synced {len(synced)} student(s): {names}", "success")

    return jsonify({
        "message": f"Synced {len(synced)} new student(s)",
        "synced": synced
    })


# ── face photos ──────────────────────────────────────
@app.route("/api/student-photos")
@login_required(role="teacher")
def student_photos():
    return jsonify(face_utils.get_student_photo_list())


@app.route("/api/photo/<folder>/<filename>")
@login_required()
def serve_photo(folder, filename):
    return send_from_directory(os.path.join(FACE_DATA_DIR, folder), filename)


@app.route("/api/register-face", methods=["POST"])
@login_required(role="teacher")
def register_face():
    try:
        import cv2, numpy as np
        d = request.json or {}
        sid     = d.get("student_id", "")
        name    = d.get("name", "")
        img_b64 = d.get("image", "")
        if not sid or not img_b64:
            return jsonify({"error": "student_id and image required"}), 400
        img_data = base64.b64decode(img_b64.split(",")[-1])
        np_arr   = np.frombuffer(img_data, np.uint8)
        frame    = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({"error": "Invalid image"}), 400
        safe   = name.replace(" ", "_")
        folder = os.path.join(FACE_DATA_DIR, f"{sid}_{safe}")
        os.makedirs(folder, exist_ok=True)
        existing = [f for f in os.listdir(folder)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        path = os.path.join(folder, f"photo_{len(existing)+1}.jpg")
        cv2.imwrite(path, frame)
        return jsonify({"message": "Face saved!", "path": path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── attendance ───────────────────────────────────────
@app.route("/api/attendance")
@login_required()
def get_attendance():
    d   = request.args.get("date", str(date.today()))
    sub = request.args.get("subject")
    return jsonify(database.get_attendance(d, sub))


@app.route("/api/attendance/manual", methods=["POST"])
@login_required(role="teacher")
def mark_manual():
    try:
        d = request.json or {}
        database.mark_attendance(
            d["student_id"], str(date.today()),
            d.get("status", "Present"), d.get("subject", "General"))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── THE MAIN FIX: mark-detected ──────────────────────
@app.route("/api/attendance/mark-detected", methods=["POST"])
@login_required(role="teacher")
def mark_detected():
    """
    Called when face recognition verifies a student.
    Steps:
      1. Auto-add student to DB if missing (so login works for them)
      2. Mark them Present in attendance table
      3. Send notification to student so they see it in their portal
      4. Check if at-risk and notify if needed
    """
    try:
        d           = request.json or {}
        student_ids = d.get("student_ids", [])
        subject     = d.get("subject", "General")
        today_str   = str(date.today())
        marked      = []

        for sid in student_ids:
            # Step 1: ensure student exists in DB
            ensure_student_in_db(sid)

            # Step 2: mark present
            ok = database.mark_attendance(sid, today_str, "Present", subject)
            if not ok:
                print(f"[mark-detected] Failed to mark {sid} — student missing from DB?")
                continue

            marked.append(sid)

            # Step 3: notify student they are present
            database.add_notification(
                sid,
                f"✅ You were marked Present on {today_str} for {subject}.",
                "success"
            )

            # Step 4: check at-risk
            database.check_and_notify_at_risk(sid)

        print(f"[mark-detected] Marked present: {marked} on {today_str}")
        return jsonify({"marked": marked, "date": today_str, "subject": subject})

    except Exception as e:
        import traceback
        print("[mark-detected] ERROR:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ── analytics ────────────────────────────────────────
@app.route("/api/defaulters")
@login_required(role="teacher")
def defaulters():
    threshold = int(request.args.get("threshold", 75))
    return jsonify(database.get_defaulters(threshold))


@app.route("/api/monthly-summary")
@login_required(role="teacher")
def monthly_summary():
    year  = request.args.get("year",  str(date.today().year))
    month = request.args.get("month", str(date.today().month))
    return jsonify(database.get_monthly_summary(year, month))


@app.route("/api/export/csv")
@login_required(role="teacher")
def export_csv():
    year  = request.args.get("year",  str(date.today().year))
    month = request.args.get("month", str(date.today().month))
    data  = database.get_monthly_summary(year, month)
    out   = io.StringIO()
    w     = csv.writer(out)
    w.writerow(["Roll No","Name","Present","Absent","Total","Percentage","Status"])
    for r in data:
        w.writerow([r["id"], r["name"], r["present"], r["absent"],
                    r["total"], f"{r['percentage']}%",
                    "OK" if r["percentage"] >= 75 else "DEFAULTER"])
    out.seek(0)
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":
                             f"attachment;filename=attendance_{year}_{month}.csv"})


# ── notifications ────────────────────────────────────
@app.route("/api/notifications")
@login_required()
def get_notifications():
    return jsonify(database.get_notifications(session["user"]["id"]))


@app.route("/api/notifications/read", methods=["POST"])
@login_required()
def read_notifications():
    database.mark_notifs_read(session["user"]["id"])
    return jsonify({"ok": True})


# ── student portal ───────────────────────────────────
@app.route("/api/my/attendance")
@login_required(role="student")
def my_attendance():
    """
    Returns attendance records + stats for the logged-in student.
    This is what powers the student portal dashboard.
    """
    sid = session["user"]["id"]
    records = database.get_student_attendance(sid)
    stats   = database.get_student_stats(sid)
    print(f"[my-attendance] {sid}: {stats}")
    return jsonify({"records": records, "stats": stats})


if __name__ == "__main__":
    print("=" * 50)
    print("EduTrack LMS starting...")
    print("Teacher login: teacher1 / teacher123")
    print("Student login: <roll_no> / student123")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)