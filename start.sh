#!/bin/bash

echo "Starting MessMenu Rater Application..."
echo "===================================="

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting Flask application..."
echo "Application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
