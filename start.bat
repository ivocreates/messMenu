@echo off
echo Starting MessMenu Rater Application...
echo ====================================

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Flask application...
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py
