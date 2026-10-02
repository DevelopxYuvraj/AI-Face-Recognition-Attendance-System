from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from database import (
    get_attendance_by_date,
    get_all_students,
    get_student,
    get_student_attendance,
    get_student_attendance_stats,
)


def show_attendance_history(parent):
    window = tk.Toplevel(parent)
    window.title("Attendance History")
    window.geometry("950x560")

    top = ttk.Frame(window, padding=10)
    top.pack(fill="x")

    ttk.Label(top, text="Date (YYYY-MM-DD):").pack(side="left")
    date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    date_entry = ttk.Entry(top, textvariable=date_var, width=15)
    date_entry.pack(side="left", padx=8)

    columns = ("student_id", "roll", "name", "date", "time", "status")
    tree = ttk.Treeview(window, columns=columns, show="headings")
    headings = {
        "student_id": "Student ID",
        "roll": "Roll Number",
        "name": "Student Name",
        "date": "Date",
        "time": "Time",
        "status": "Status"
    }

    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=140)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    summary = ttk.Label(window, text="")
    summary.pack(pady=5)

    def load():
        for item in tree.get_children():
            tree.delete(item)

        date_string = date_var.get().strip()
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Enter the date like 2026-10-01."
            )
            return

        rows = get_attendance_by_date(date_string)
        total = len(rows)
        present = sum(1 for row in rows if row["status"] == "Present")
        absent = total - present

        for row in rows:
            tree.insert("", "end", values=(
                row["student_id"], row["roll_number"], row["name"],
                row["date"], row["time"] or "-", row["status"]
            ))

        summary.config(
            text=f"Total Students: {total}    Present: {present}    "
                 f"Absent: {absent}"
        )

    ttk.Button(top, text="Load", command=load).pack(side="left")
    load()


def show_student_attendance(parent):
    window = tk.Toplevel(parent)
    window.title("Student-wise Attendance")
    window.geometry("800x560")

    students = get_all_students()
    if not students:
        messagebox.showinfo("No Students", "Register a student first.")
        window.destroy()
        return

    top = ttk.Frame(window, padding=10)
    top.pack(fill="x")

    ttk.Label(top, text="Select Student:").pack(side="left")

    student_map = {
        f"{row['student_id']} - {row['name']}": row["student_id"]
        for row in students
    }
    selected = tk.StringVar(value=list(student_map.keys())[0])

    combo = ttk.Combobox(
        top, textvariable=selected,
        values=list(student_map.keys()), state="readonly", width=35
    )
    combo.pack(side="left", padx=8)

    stats = ttk.Label(window, text="", font=("Arial", 11, "bold"))
    stats.pack(pady=10)

    columns = ("date", "time", "status")
    tree = ttk.Treeview(window, columns=columns, show="headings")
    for col, heading in zip(columns, ("Date", "Time", "Status")):
        tree.heading(col, text=heading)
        tree.column(col, width=200)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load():
        for item in tree.get_children():
            tree.delete(item)

        student_id = student_map[selected.get()]
        student = get_student(student_id)
        rows = get_student_attendance(student_id)
        info = get_student_attendance_stats(student_id)

        for row in rows:
            tree.insert("", "end", values=(
                row["date"], row["time"], row["status"]
            ))

        stats.config(
            text=(
                f"{student['name']} ({student_id})  |  "
                f"Total Classes/Days: {info['total_classes']}  |  "
                f"Present: {info['present']}  |  "
                f"Absent: {info['absent']}  |  "
                f"Attendance: {info['percentage']:.2f}%"
            )
        )

    ttk.Button(top, text="View", command=load).pack(side="left")
    combo.bind("<<ComboboxSelected>>", lambda event: load())
    load()
