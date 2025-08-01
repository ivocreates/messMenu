@echo off
REM Mess Menu Rater - Start Application Script (Windows)
REM This script starts the Flask development server

echo 🍽️ Starting Mess Menu Rater...
echo ==============================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flask not found. Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Check if database exists
if not exist "database\mess_menu.db" (
    echo ⚠️ Database not found. Running setup first...
    call setup_windows.bat
)

echo 🚀 Starting Flask application...
echo.
echo 🌐 Application will be available at:
echo    Local:   http://127.0.0.1:5000
echo    Network: http://0.0.0.0:5000
echo.
echo 📋 Demo Accounts:
echo    👨‍🎓 Student: username=student, password=student123
echo    👨‍💼 Admin: username=admin, password=admin123
echo.
echo 🛑 Press Ctrl+C to stop the server
echo ==============================

REM Start the application
python app.py
