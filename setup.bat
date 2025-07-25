@echo off
echo ===================================
echo    Mess Menu Rater Setup Script
echo ===================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✓ Python is installed

:: Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment created

:: Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed

:: Setup database
echo.
echo Setting up database...
python setup.py
if errorlevel 1 (
    echo ERROR: Failed to setup database
    pause
    exit /b 1
)

echo ✓ Database setup completed

echo.
echo ===================================
echo     Setup Completed Successfully!
echo ===================================
echo.
echo To start the application:
echo 1. Run: start_app.bat
echo 2. Or manually:
echo    - venv\Scripts\activate
echo    - python app.py
echo.
echo Default admin login:
echo Username: admin
echo Password: admin123
echo.
echo Application will be available at: http://localhost:5000
echo.
pause
