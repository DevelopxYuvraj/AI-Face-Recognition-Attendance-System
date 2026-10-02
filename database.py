import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "attendance.db"


def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                roll_number TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                branch TEXT NOT NULL,
                section TEXT NOT NULL,
                semester TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT NOT NULL,
                UNIQUE(student_id, date),
                FOREIGN KEY(student_id) REFERENCES students(student_id)
                    ON DELETE CASCADE
            )
        """)
        conn.commit()
    finally:
        conn.close()


def add_student(student_id, roll_number, name, branch, section, semester):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO students
            (student_id, roll_number, name, branch, section, semester, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id.strip(), roll_number.strip(), name.strip(),
            branch.strip(), section.strip(), semester.strip(),
            datetime.now().isoformat(timespec="seconds")
        ))
        conn.commit()
    finally:
        conn.close()


def get_student(student_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
    finally:
        conn.close()


def get_all_students():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM students ORDER BY name"
        ).fetchall()
    finally:
        conn.close()


def update_student(old_student_id, student_id, roll_number, name, branch, section, semester):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE students
            SET student_id=?, roll_number=?, name=?, branch=?, section=?, semester=?
            WHERE student_id=?
        """, (
            student_id.strip(), roll_number.strip(), name.strip(),
            branch.strip(), section.strip(), semester.strip(),
            old_student_id
        ))
        conn.commit()
    finally:
        conn.close()


def delete_student(student_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
    finally:
        conn.close()


def mark_attendance(student_id, date_string=None, time_string=None):
    now = datetime.now()
    date_string = date_string or now.strftime("%Y-%m-%d")
    time_string = time_string or now.strftime("%H:%M:%S")

    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO attendance(student_id, date, time, status)
            VALUES (?, ?, ?, 'Present')
        """, (student_id, date_string, time_string))
        conn.commit()
        return cursor.rowcount == 1
    finally:
        conn.close()


def has_attendance_today(student_id, date_string=None):
    date_string = date_string or datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT 1 FROM attendance
            WHERE student_id=? AND date=?
        """, (student_id, date_string)).fetchone()
        return row is not None
    finally:
        conn.close()


def get_attendance_by_date(date_string):
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT s.student_id, s.roll_number, s.name,
                   ? AS date,
                   a.time,
                   CASE WHEN a.attendance_id IS NOT NULL
                        THEN 'Present' ELSE 'Absent' END AS status
            FROM students s
            LEFT JOIN attendance a
              ON s.student_id=a.student_id AND a.date=?
            ORDER BY s.name
        """, (date_string, date_string)).fetchall()
    finally:
        conn.close()


def get_student_attendance(student_id):
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT date, time, status
            FROM attendance
            WHERE student_id=?
            ORDER BY date DESC
        """, (student_id,)).fetchall()
    finally:
        conn.close()


def get_student_attendance_stats(student_id):
    conn = get_connection()
    try:
        total_students = conn.execute(
            "SELECT COUNT(*) AS c FROM students"
        ).fetchone()["c"]

        present = conn.execute("""
            SELECT COUNT(*) AS c FROM attendance
            WHERE student_id=? AND status='Present'
        """, (student_id,)).fetchone()["c"]

        all_dates = conn.execute("""
            SELECT COUNT(DISTINCT date) AS c FROM attendance
        """).fetchone()["c"]

        total_classes = all_dates
        absent = max(total_classes - present, 0)
        percentage = (present / total_classes * 100) if total_classes else 0

        return {
            "total_classes": total_classes,
            "present": present,
            "absent": absent,
            "percentage": percentage,
            "total_students": total_students
        }
    finally:
        conn.close()


def get_today_summary(date_string=None):
    date_string = date_string or datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
        present = conn.execute("""
            SELECT COUNT(*) AS c FROM attendance
            WHERE date=? AND status='Present'
        """, (date_string,)).fetchone()["c"]
        absent = max(total - present, 0)
        percentage = (present / total * 100) if total else 0
        return {
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": percentage
        }
    finally:
        conn.close()
