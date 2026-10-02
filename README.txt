AI FACE RECOGNITION ATTENDANCE MANAGEMENT SYSTEM
=================================================

IMPORTANT: This package is prepared for Windows + Python 3.11.

EASIEST WAY TO START
--------------------
1. Extract this ZIP.
2. Open the AI_Face_Attendance folder in VS Code.
3. Double-click SETUP_WINDOWS.bat ONE TIME.
4. Wait until it says: SETUP COMPLETED SUCCESSFULLY.
5. Double-click RUN_PROJECT.bat.

If Windows shows a security warning, choose More info -> Run anyway only
if you trust the file you downloaded.

WHY THIS VERSION IS DIFFERENT
------------------------------
The normal face-recognition installation asks pip to build dlib from source.
That often fails on Windows. This project installs the ready-made dlib-bin
wheel first and then installs face-recognition with --no-deps, so pip does
not try to compile dlib again.

RECOMMENDED PYTHON
------------------
Python 3.11 (64-bit)

MANUAL VS CODE COMMANDS (CMD)
------------------------------
py -3.11 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install dlib-bin==20.0.1
python -m pip install face-recognition-models==0.3.0 click
python -m pip install face-recognition==1.3.0 --no-deps
python -m pip install -r requirements.txt
python check_setup.py
python main.py

FIRST USE INSIDE THE APP
-------------------------
1. Add Student
   Enter Student ID, Roll Number, Name, Branch, Section and Semester.
2. Capture Face
   Select the student and allow webcam access.
   Look at the camera and move slightly left/right when instructed.
3. Train/Encode Faces
   This creates the local face encoding file.
4. Start Attendance
   Look at the camera. A recognized student is marked Present.
   The same student is not marked twice on the same date.
5. Unknown Person
   An unregistered face is displayed as "Unknown Person" and is NOT
   recorded as attendance.
6. Attendance History
   Select a date to see Present/Absent records.
7. Student Attendance
   See student-wise attendance percentage.
8. Export Report
   CSV and Excel reports are saved inside reports\.

KEYBOARD
--------
During face capture: Q = stop capture
During live attendance: Q = close attendance window

FOLDERS
-------
dataset\students\     Face images
data? (not used)
encodings\             Saved face encodings
database\              SQLite database
reports\               CSV/Excel reports
haarcascade\           Face detection XML

PRIVACY
-------
Face images and encodings are stored locally in this project folder.
Use the system only with appropriate permission/consent and protect the
stored biometric data.

TROUBLESHOOTING
---------------
A) dlib installation error:
   Do NOT run plain "pip install face-recognition" on Windows.
   Run SETUP_WINDOWS.bat.

B) Camera not opening:
   Close Zoom/Teams/Camera and allow camera permission in Windows.

C) Haar Cascade error:
   The XML is already included in this ZIP. Do not rename it.

D) No face images:
   Make sure your face is visible, well lit, and only one person is in
   front of the camera during capture.

E) Unknown Person:
   Capture the student's face again and run Train/Encode Faces again.
