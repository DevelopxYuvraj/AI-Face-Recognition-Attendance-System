@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   AI Face Recognition Attendance - Windows Setup
echo ============================================================
echo.

echo [1/7] Checking Python 3.11...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python 3.11 was not found.
    echo Install Python 3.11 from python.org, then run this file again.
    echo.
    pause
    exit /b 1
)
py -3.11 --version

echo.
echo [2/7] Creating virtual environment...
if not exist "venv\Scripts\python.exe" (
    py -3.11 -m venv venv
    if errorlevel 1 goto :error
) else (
    echo Existing venv found - keeping it.
)

call "venv\Scripts\activate.bat"
if errorlevel 1 goto :error

python --version

echo.
echo [3/7] Upgrading pip tools...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :error

echo.
echo [4/7] Installing Windows dlib wheel...
python -m pip install dlib-bin==20.0.1
if errorlevel 1 goto :error

echo.
echo [5/7] Installing face-recognition without rebuilding dlib...
python -m pip install face-recognition-models==0.3.0 click
if errorlevel 1 goto :error
python -m pip install face-recognition==1.3.0 --no-deps
if errorlevel 1 goto :error

echo.
echo [6/7] Installing OpenCV, NumPy, Pandas, Excel and Pillow...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo [7/7] Checking the complete installation...
python check_setup.py
if errorlevel 1 goto :error

echo.
echo ============================================================
echo   SETUP COMPLETED SUCCESSFULLY
echo ============================================================
echo.
echo To start the project later, double-click RUN_PROJECT.bat
echo or use: venv\Scripts\activate
echo       python main.py
echo.
pause
exit /b 0

:error
echo.
echo ============================================================
echo   SETUP FAILED
echo ============================================================
echo.
echo Keep this window open and send me a screenshot of the error.
echo.
pause
exit /b 1
