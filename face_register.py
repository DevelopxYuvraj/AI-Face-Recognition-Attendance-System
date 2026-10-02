import cv2
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "students"
CASCADE_PATH = BASE_DIR / "haarcascade" / "haarcascade_frontalface_default.xml"


def get_cascade():
    if not CASCADE_PATH.exists():
        raise FileNotFoundError(
            "Haar Cascade not found. Put "
            "haarcascade_frontalface_default.xml inside the haarcascade folder."
        )
    cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
    if cascade.empty():
        raise RuntimeError("Haar Cascade file could not be loaded.")
    return cascade


def capture_faces(student_id, image_count=20, status_callback=None):
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    student_dir = DATASET_DIR / str(student_id)

    # Replace old captured images to keep the dataset clean.
    if student_dir.exists():
        shutil.rmtree(student_dir)
    student_dir.mkdir(parents=True, exist_ok=True)

    cascade = get_cascade()
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError(
            "Camera could not be opened. Check camera permission and make sure "
            "another application is not using the webcam."
        )

    saved = 0
    try:
        while saved < image_count:
            ok, frame = camera.read()
            if not ok:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(
                gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100)
            )

            # Give simple movement instructions during capture.
            instructions = [
                "Look at the camera",
                "Move slightly left",
                "Move slightly right",
                "Look straight again",
            ]
            message = instructions[saved % len(instructions)]
            if len(faces) == 0:
                message = "No face detected - " + message
            elif len(faces) > 1:
                message = "Multiple faces detected - only one person allowed"
            else:
                message = f"Face detected - {instructions[saved % len(instructions)]}"

                (x, y, w, h) = faces[0]
                face_crop = frame[y:y+h, x:x+w]
                file_path = student_dir / f"{student_id}_{saved+1:03d}.jpg"
                cv2.imwrite(str(file_path), face_crop)
                saved += 1

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.putText(
                frame, message, (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2
            )
            cv2.putText(
                frame, "Press Q to stop", (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2
            )

            cv2.imshow("Face Data Collection", frame)

            if status_callback:
                status_callback(message)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    if saved == 0:
        raise RuntimeError("No face images were captured.")

    return saved


def delete_face_data(student_id):
    student_dir = DATASET_DIR / str(student_id)
    if student_dir.exists():
        shutil.rmtree(student_dir)
        return True
    return False
