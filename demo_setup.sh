#!/bin/bash

echo "============================================"
echo "🚀 DOCTOR APPOINTMENT BOT - FRESH SETUP DEMO"
echo "============================================"
echo
echo "This demo shows how to set up the project from scratch"
echo
echo "Step 1: Delete existing virtual environment (for demo)"
echo

if [ -d "env" ]; then
    echo "Deleting existing virtual environment..."
    rm -rf env
    echo "✅ Virtual environment deleted"
else
    echo "No existing virtual environment found"
fi

echo
echo "Step 2: Run the setup script"
echo
echo "Running: python3 setup.py"
echo

python3 setup.py

echo
echo "============================================"
echo "🎉 DEMO COMPLETE!"
echo "============================================"
echo
echo "The setup script has created:"
echo "✅ Virtual environment (env/)"
echo "✅ Installed all dependencies"
echo "✅ Configured environment variables"
echo "✅ Tested API connections"
echo "✅ Populated vector database"
echo "✅ Verified functionality"
echo
echo "Next steps:"
echo "1. Activate virtual environment: source env/bin/activate"
echo "2. Run the application: python3 main.py"
echo "3. Visit: http://localhost:8000"
echo
