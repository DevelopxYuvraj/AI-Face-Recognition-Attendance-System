import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

import database
from database import (
    add_student,
    get_all_students,
    get_student,
    update_student,
    delete_student,
    get_today_summary,
)
from face_register import capture_faces, delete_face_data
from face_recognition_attendance import train_encodings, run_live_attendance
from attendance import show_attendance_history, show_student_attendance
from reports import export_attendance


BASE_DIR = Path(__file__).resolve().parent


class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Face Recognition Attendance Management System")
        self.root.geometry("1100x700")
        self.root.minsize(950, 620)

        database.initialize_database()
        self.setup_style()
        self.build_ui()
        self.refresh_dashboard()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Arial", 22, "bold"))
        style.configure("Card.TFrame", relief="solid", borderwidth=1)
        style.configure("Big.TLabel", font=("Arial", 18, "bold"))
        style.configure("Action.TButton", font=("Arial", 11, "bold"), padding=10)

    def build_ui(self):
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="AI Face Recognition Attendance",
            style="Title.TLabel"
        ).pack(side="left")

        self.date_label = ttk.Label(header, text="")
        self.date_label.pack(side="right")
        self.update_clock()

        dashboard = ttk.Frame(self.root, padding=15)
        dashboard.pack(fill="x")

        self.total_var = tk.StringVar(value="0")
        self.present_var = tk.StringVar(value="0")
        self.absent_var = tk.StringVar(value="0")
        self.percent_var = tk.StringVar(value="0%")

        self.make_card(dashboard, "Total Students", self.total_var, 0)
        self.make_card(dashboard, "Today's Present", self.present_var, 1)
        self.make_card(dashboard, "Today's Absent", self.absent_var, 2)
        self.make_card(dashboard, "Attendance %", self.percent_var, 3)

        buttons = ttk.Frame(self.root, padding=20)
        buttons.pack(fill="x")

        actions = [
            ("Add Student", self.add_student_window),
            ("Capture Face", self.capture_face_window),
            ("Train/Encode Faces", self.train_faces),
            ("Start Attendance", self.start_attendance),
            ("Attendance History", lambda: show_attendance_history(self.root)),
            ("Student Records", self.student_records_window),
            ("Student Attendance", lambda: show_student_attendance(self.root)),
            ("Export Report", self.export_report),
            ("Exit", self.root.destroy),
        ]

        for index, (text, command) in enumerate(actions):
            button = ttk.Button(
                buttons, text=text, command=command, style="Action.TButton"
            )
            button.grid(
                row=index // 3, column=index % 3,
                padx=8, pady=8, sticky="ew"
            )

        for col in range(3):
            buttons.columnconfigure(col, weight=1)

        info = ttk.LabelFrame(self.root, text="How the system works", padding=15)
        info.pack(fill="both", expand=True, padx=20, pady=10)

        text = (
            "1. Add a student and save their details.\n"
            "2. Capture 20 face images from the webcam.\n"
            "3. Train/Encode Faces to create the local encoding file.\n"
            "4. Start Attendance and look at the camera.\n"
            "5. A recognized student is marked Present only once per day.\n"
            "6. An unregistered face is shown as 'Unknown Person' and is NOT marked present.\n"
            "7. Use Attendance History or Student Attendance to view records.\n"
            "8. Export Report creates both CSV and Excel files in the reports folder."
        )
        ttk.Label(info, text=text, justify="left").pack(anchor="w")

    def make_card(self, parent, title, variable, column):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        frame.grid(row=0, column=column, padx=7, sticky="nsew")
        parent.columnconfigure(column, weight=1)

        ttk.Label(frame, text=title).pack()
        ttk.Label(frame, textvariable=variable, style="Big.TLabel").pack(pady=8)

    def update_clock(self):
        self.date_label.config(
            text=datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
        )
        self.root.after(1000, self.update_clock)

    def refresh_dashboard(self):
        summary = get_today_summary()
        self.total_var.set(str(summary["total"]))
        self.present_var.set(str(summary["present"]))
        self.absent_var.set(str(summary["absent"]))
        self.percent_var.set(f"{summary['percentage']:.2f}%")

    def add_student_window(self):
        window = tk.Toplevel(self.root)
        window.title("Add Student")
        window.geometry("450x450")
        window.resizable(False, False)

        fields = [
            ("Student ID", "student_id"),
            ("Roll Number", "roll_number"),
            ("Student Name", "name"),
            ("Branch", "branch"),
            ("Section", "section"),
            ("Semester", "semester"),
        ]

        entries = {}
        form = ttk.Frame(window, padding=20)
        form.pack(fill="both", expand=True)

        for row, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(
                row=row, column=0, padx=8, pady=8, sticky="w"
            )
            entry = ttk.Entry(form, width=30)
            entry.grid(row=row, column=1, padx=8, pady=8)
            entries[key] = entry

        def save():
            values = {key: entry.get().strip() for key, entry in entries.items()}

            if not all(values.values()):
                messagebox.showwarning(
                    "Missing Information",
                    "Please fill every student field."
                )
                return

            if get_student(values["student_id"]):
                messagebox.showerror(
                    "Student Already Registered",
                    "This Student ID is already registered."
                )
                return

            try:
                add_student(**values)
                messagebox.showinfo(
                    "Success",
                    "Student registered successfully.\n\n"
                    "Next step: click Capture Face."
                )
                window.destroy()
                self.refresh_dashboard()
            except Exception as exc:
                messagebox.showerror(
                    "Database Error",
                    f"Could not save student.\n\n{exc}"
                )

        ttk.Button(form, text="Save Student", command=save).grid(
            row=len(fields), column=0, columnspan=2, pady=20
        )

    def select_student(self, title="Select Student"):
        students = get_all_students()
        if not students:
            messagebox.showinfo("No Students", "Register a student first.")
            return None

        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("500x180")

        selected = tk.StringVar()
        mapping = {
            f"{s['student_id']} - {s['name']}": s["student_id"]
            for s in students
        }

        ttk.Label(window, text="Student:").pack(pady=15)
        combo = ttk.Combobox(
            window, values=list(mapping.keys()),
            textvariable=selected, state="readonly", width=40
        )
        combo.pack()

        result = {"student_id": None}

        def choose():
            if not selected.get():
                return
            result["student_id"] = mapping[selected.get()]
            window.destroy()

        ttk.Button(window, text="Continue", command=choose).pack(pady=15)
        window.transient(self.root)
        window.grab_set()
        self.root.wait_window(window)
        return result["student_id"]

    def capture_face_window(self):
        student_id = self.select_student("Select Student for Face Capture")
        if not student_id:
            return

        try:
            count = capture_faces(student_id)
            messagebox.showinfo(
                "Capture Complete",
                f"{count} face images captured successfully.\n\n"
                "Now click 'Train/Encode Faces'."
            )
        except Exception as exc:
            messagebox.showerror("Face Capture Error", str(exc))

    def train_faces(self):
        try:
            count = train_encodings()
            messagebox.showinfo(
                "Training Complete",
                f"{count} face encodings were saved locally.\n\n"
                "You can now start attendance."
            )
        except Exception as exc:
            messagebox.showerror("Training Error", str(exc))

    def start_attendance(self):
        try:
            run_live_attendance(
                status_callback=lambda message: self.root.after(
                    0, self.refresh_dashboard
                )
            )
            self.refresh_dashboard()
        except Exception as exc:
            messagebox.showerror("Attendance Error", str(exc))

    def student_records_window(self):
        window = tk.Toplevel(self.root)
        window.title("Student Records")
        window.geometry("1050x520")

        columns = (
            "student_id", "roll", "name",
            "branch", "section", "semester"
        )
        tree = ttk.Treeview(window, columns=columns, show="headings")

        titles = {
            "student_id": "Student ID",
            "roll": "Roll Number",
            "name": "Name",
            "branch": "Branch",
            "section": "Section",
            "semester": "Semester",
        }

        for col in columns:
            tree.heading(col, text=titles[col])
            tree.column(col, width=150)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load():
            for item in tree.get_children():
                tree.delete(item)

            for s in get_all_students():
                tree.insert("", "end", values=(
                    s["student_id"], s["roll_number"], s["name"],
                    s["branch"], s["section"], s["semester"]
                ))

        def get_selected_id():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning(
                    "Select Student", "Please select a student first."
                )
                return None
            return tree.item(selected[0])["values"][0]

        def edit():
            student_id = get_selected_id()
            if not student_id:
                return
            self.edit_student_window(student_id, load)

        def remove():
            student_id = get_selected_id()
            if not student_id:
                return

            if not messagebox.askyesno(
                "Confirm Delete",
                "Delete this student and their attendance/face data?"
            ):
                return

            try:
                delete_face_data(student_id)
                delete_student(student_id)
                messagebox.showinfo("Deleted", "Student deleted safely.")
                load()
                self.refresh_dashboard()
            except Exception as exc:
                messagebox.showerror("Delete Error", str(exc))

        toolbar = ttk.Frame(window, padding=10)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Update", command=edit).pack(
            side="left", padx=5
        )
        ttk.Button(toolbar, text="Delete", command=remove).pack(
            side="left", padx=5
        )
        ttk.Button(toolbar, text="Refresh", command=load).pack(
            side="left", padx=5
        )

        load()

    def edit_student_window(self, student_id, refresh_callback):
        student = get_student(student_id)
        if not student:
            return

        window = tk.Toplevel(self.root)
        window.title("Update Student")
        window.geometry("450x450")

        fields = [
            ("Student ID", "student_id"),
            ("Roll Number", "roll_number"),
            ("Student Name", "name"),
            ("Branch", "branch"),
            ("Section", "section"),
            ("Semester", "semester"),
        ]

        entries = {}
        for row, (label, key) in enumerate(fields):
            ttk.Label(window, text=label).grid(
                row=row, column=0, padx=10, pady=10, sticky="w"
            )
            entry = ttk.Entry(window, width=30)
            entry.insert(0, student[key])
            entry.grid(row=row, column=1, padx=10, pady=10)
            entries[key] = entry

        def save():
            values = {key: entry.get().strip() for key, entry in entries.items()}
            if not all(values.values()):
                messagebox.showwarning(
                    "Missing Information", "Fill every field."
                )
                return

            try:
                update_student(
                    student_id,
                    values["student_id"],
                    values["roll_number"],
                    values["name"],
                    values["branch"],
                    values["section"],
                    values["semester"],
                )
                messagebox.showinfo("Updated", "Student updated successfully.")
                window.destroy()
                refresh_callback()
            except Exception as exc:
                messagebox.showerror("Update Error", str(exc))

        ttk.Button(window, text="Save Changes", command=save).grid(
            row=len(fields), column=0, columnspan=2, pady=20
        )

    def export_report(self):
        date_string = datetime.now().strftime("%Y-%m-%d")
        try:
            csv_path, xlsx_path = export_attendance(date_string)
            messagebox.showinfo(
                "Export Complete",
                "Reports created successfully:\n\n"
                f"CSV: {csv_path}\n"
                f"Excel: {xlsx_path}"
            )
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc))


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
