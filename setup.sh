#!/bin/bash

echo "MessMenu Rater Setup Script"
echo "=========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed!"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

echo "Python found!"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment!"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing required packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install packages!"
    exit 1
fi

# Initialize database
echo "Initializing database..."
python init_db.py
if [ $? -ne 0 ]; then
    echo "Failed to initialize database!"
    exit 1
fi

echo "Setup completed successfully!"
echo ""
echo "Default login credentials:"
echo "Admin: username='admin', password='admin123'"
echo "Student: username='student', password='student123'"
echo ""
echo "To start the application, run: ./start.sh"
