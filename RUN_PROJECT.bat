@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Project is not set up yet.
    echo First run SETUP_WINDOWS.bat
    echo.
    pause
    exit /b 1
)

call "venv\Scripts\activate.bat"
python main.py

if errorlevel 1 (
    echo.
    echo The application closed because of an error.
    echo Send me a screenshot of this window.
    pause
)
