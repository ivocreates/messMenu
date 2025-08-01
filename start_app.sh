#!/bin/bash

# Mess Menu Rater - Start Application Script
# This script starts the Flask development server

echo "🍽️ Starting Mess Menu Rater..."
echo "=============================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.7+"
    exit 1
fi

# Check if Flask is installed
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Flask not found. Please run setup.sh first"
    exit 1
fi

# Check if database exists
if [ ! -f "database/mess_menu.db" ]; then
    echo "⚠️ Database not found. Running setup first..."
    ./setup.sh
fi

echo "🚀 Starting Flask application..."
echo ""
echo "🌐 Application will be available at:"
echo "   Local:   http://127.0.0.1:5000"
echo "   Network: http://0.0.0.0:5000"
echo ""
echo "📋 Demo Accounts:"
echo "   👨‍🎓 Student: username=student, password=student123" 
echo "   👨‍💼 Admin: username=admin, password=admin123"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo "=============================="

# Start the application
python app.py
