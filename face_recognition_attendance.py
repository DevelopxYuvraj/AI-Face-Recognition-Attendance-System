import pickle
from pathlib import Path
from datetime import datetime

import cv2
import face_recognition

from database import get_all_students, mark_attendance
from face_register import get_cascade

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "students"
ENCODING_DIR = BASE_DIR / "encodings"
ENCODING_FILE = ENCODING_DIR / "face_encodings.pkl"


def train_encodings():
    ENCODING_DIR.mkdir(parents=True, exist_ok=True)
    students = get_all_students()

    if not students:
        raise RuntimeError("No students are registered yet.")

    known_encodings = []
    known_ids = []

    for student in students:
        student_id = student["student_id"]
        student_dir = DATASET_DIR / str(student_id)

        if not student_dir.exists():
            continue

        image_files = list(student_dir.glob("*.jpg")) + list(student_dir.glob("*.png"))

        for image_path in image_files:
            image = face_recognition.load_image_file(str(image_path))
            locations = face_recognition.face_locations(image, model="hog")

            if len(locations) != 1:
                continue

            encodings = face_recognition.face_encodings(image, locations)
            if encodings:
                known_encodings.append(encodings[0])
                known_ids.append(student_id)

    if not known_encodings:
        raise RuntimeError(
            "No usable face images were found. Capture face data first."
        )

    with open(ENCODING_FILE, "wb") as file:
        pickle.dump({
            "encodings": known_encodings,
            "student_ids": known_ids
        }, file)

    return len(known_encodings)


def load_encodings():
    if not ENCODING_FILE.exists():
        raise FileNotFoundError(
            "Encoding file not found. Click 'Train/Encode Faces' first."
        )

    with open(ENCODING_FILE, "rb") as file:
        data = pickle.load(file)

    if not data.get("encodings") or not data.get("student_ids"):
        raise RuntimeError("Encoding file is empty. Train the faces again.")

    return data["encodings"], data["student_ids"]


def run_live_attendance(status_callback=None):
    known_encodings, known_ids = load_encodings()
    students = {row["student_id"]: row for row in get_all_students()}

    cascade = get_cascade()
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Camera could not be opened.")

    last_message = "Starting attendance..."

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                continue

            # Haar Cascade performs the requested face detection.
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(
                gray, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80)
            )

            display_message = "Look at the camera"

            if len(faces) == 0:
                display_message = "No face detected"
            elif len(faces) > 1:
                display_message = "Multiple faces detected"
            else:
                # Convert the frame for face_recognition.
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                locations = face_recognition.face_locations(rgb, model="hog")

                if len(locations) == 1:
                    face_encs = face_recognition.face_encodings(rgb, locations)

                    if face_encs:
                        current_encoding = face_encs[0]
                        distances = face_recognition.face_distance(
                            known_encodings, current_encoding
                        )
                        best_index = distances.argmin()
                        best_distance = float(distances[best_index])

                        # Smaller distance means greater similarity.
                        threshold = 0.50

                        if best_distance <= threshold:
                            student_id = known_ids[best_index]
                            student = students.get(student_id)

                            if student:
                                marked = mark_attendance(student_id)

                                if marked:
                                    display_message = (
                                        f"Present: {student['name']} | "
                                        f"ID: {student_id} | "
                                        f"Distance: {best_distance:.3f}"
                                    )
                                else:
                                    display_message = (
                                        f"Already Present: {student['name']} | "
                                        f"ID: {student_id} | "
                                        f"Distance: {best_distance:.3f}"
                                    )
                        else:
                            # IMPORTANT: unknown faces never reach mark_attendance().
                            display_message = (
                                f"Unknown Person | Distance: {best_distance:.3f}"
                            )

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            current_dt = datetime.now()
            cv2.putText(
                frame, display_message, (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2
            )
            cv2.putText(
                frame,
                f"Date: {current_dt.strftime('%Y-%m-%d')}  "
                f"Time: {current_dt.strftime('%H:%M:%S')}",
                (15, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2
            )
            cv2.putText(
                frame, "Press Q to close attendance", (15, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2
            )

            cv2.imshow("Live Face Attendance", frame)

            if status_callback and display_message != last_message:
                status_callback(display_message)
                last_message = display_message

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
