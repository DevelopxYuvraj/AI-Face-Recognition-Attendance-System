"""Quick installation check for the AI Face Attendance project."""
from pathlib import Path
import sys

print("Python:", sys.version.split()[0])

try:
    import cv2
    print("OpenCV: OK", cv2.__version__)
except Exception as exc:
    print("OpenCV: ERROR", exc)
    raise

try:
    import dlib
    print("dlib: OK", dlib.__version__)
except Exception as exc:
    print("dlib: ERROR", exc)
    raise

try:
    import face_recognition
    print("face_recognition: OK", face_recognition.__version__)
except Exception as exc:
    print("face_recognition: ERROR", exc)
    raise

try:
    import numpy, pandas, openpyxl, PIL
    print("NumPy/Pandas/OpenPyXL/Pillow: OK")
except Exception as exc:
    print("Data/Excel packages: ERROR", exc)
    raise

try:
    import tkinter
    print("Tkinter: OK")
except Exception as exc:
    print("Tkinter: ERROR", exc)
    raise

base = Path(__file__).resolve().parent
cascade = base / "haarcascade" / "haarcascade_frontalface_default.xml"
if not cascade.exists() or cascade.stat().st_size < 100000:
    raise RuntimeError("Haar Cascade XML is missing or incomplete.")
print("Haar Cascade: OK")

print("ALL CHECKS PASSED")
