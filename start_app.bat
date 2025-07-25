@echo off
echo Starting Mess Menu Rater Application...
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the application.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check if database exists
if not exist "database\mess_menu.db" (
    echo Setting up database...
    python setup.py
)

:: Start the application
echo.
echo Starting Flask application...
echo.
echo ===================================
echo   Mess Menu Rater is starting...
echo   Open your browser and go to:
echo   http://localhost:5000
echo ===================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
