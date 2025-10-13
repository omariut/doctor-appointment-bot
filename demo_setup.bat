@echo off
echo ============================================
echo 🚀 DOCTOR APPOINTMENT BOT - FRESH SETUP DEMO
echo ============================================
echo.
echo Step 1: Delete existing virtual environment (for demo)
echo.

if exist env (
    echo Deleting existing virtual environment...
    rmdir /s /q env
    echo ✅ Virtual environment deleted
) else (
    echo No existing virtual environment found
)

echo.
echo Step 2: Create new virtual environment
echo.
python -m venv env
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

echo.
echo Step 3: Activate and install dependencies
echo.
call env\Scripts\activate
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo Step 4: Run setup script
echo.
python setup.py

echo.
echo ============================================
echo 🎉 DEMO COMPLETE!
echo ============================================
echo Next steps:
echo 1. Activate virtual environment: env\Scripts\activate
echo 2. Run the application: python main.py
echo 3. Visit: http://localhost:8000
echo.
pause



@REM @echo off
@REM echo ============================================
@REM echo 🚀 DOCTOR APPOINTMENT BOT - FRESH SETUP DEMO
@REM echo ============================================
@REM echo.
@REM echo This demo shows how to set up the project from scratch
@REM echo.
@REM echo Step 1: Delete existing virtual environment (for demo)
@REM echo.
@REM if exist env (
@REM     echo Deleting existing virtual environment...
@REM     rmdir /s /q env
@REM     echo ✅ Virtual environment deleted
@REM ) else (
@REM     echo No existing virtual environment found
@REM )
@REM echo.
@REM echo Step 2: Run the setup script
@REM echo.
@REM echo Running: python setup.py
@REM echo.
@REM python setup.py
@REM echo.
@REM echo ============================================
@REM echo 🎉 DEMO COMPLETE!
@REM echo ============================================
@REM echo.
@REM echo The setup script has created:
@REM echo ✅ Virtual environment (env/)
@REM echo ✅ Installed all dependencies
@REM echo ✅ Configured environment variables
@REM echo ✅ Tested API connections
@REM echo ✅ Populated vector database
@REM echo ✅ Verified functionality
@REM echo.
@REM echo Next steps:
@REM echo 1. Activate virtual environment: env\Scripts\activate
@REM echo 2. Run the application: python main.py
@REM echo 3. Visit: http://localhost:8000
@REM echo.
@REM pause
