@echo off
echo MessMenu Rater Setup Script
echo ==========================

echo Checking if Python is installed...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Python found!

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment!
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install packages!
    pause
    exit /b 1
)

echo Initializing database...
python init_db.py
if %errorlevel% neq 0 (
    echo Failed to initialize database!
    pause
    exit /b 1
)

echo Setup completed successfully!
echo.
echo Default login credentials:
echo Admin: username='admin', password='admin123'
echo Student: username='student', password='student123'
echo.
echo To start the application, run: start.bat
pause
