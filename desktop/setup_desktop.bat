@echo off
REM Desktop App Setup Script for Windows
REM This script sets up the desktop application environment

echo ========================================
echo RealFlip Desktop App Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Navigate to project root
cd /d "%~dp0\.."
echo.
echo [INFO] Working directory: %CD%

REM Create virtual environment if it doesn't exist
if not exist "venv_desktop" (
    echo.
    echo [INFO] Creating virtual environment...
    python -m venv venv_desktop
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [INFO] Activating virtual environment...
call venv_desktop\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install main dependencies
echo.
echo [INFO] Installing main dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [WARNING] Some dependencies may have failed to install
    ) else (
        echo [OK] Main dependencies installed
    )
) else (
    echo [WARNING] requirements.txt not found, skipping
)

REM Install desktop-specific dependencies
echo.
echo [INFO] Installing desktop-specific dependencies...
pip install apscheduler jinja2 --quiet
if errorlevel 1 (
    echo [WARNING] Failed to install some desktop dependencies
) else (
    echo [OK] Desktop dependencies installed
)

REM Try to install weasyprint (optional)
echo.
echo [INFO] Attempting to install WeasyPrint (optional, for PDF generation)...
pip install weasyprint --quiet
if errorlevel 1 (
    echo [INFO] WeasyPrint installation skipped (will use HTML fallback)
) else (
    echo [OK] WeasyPrint installed (PDF generation available)
)

REM Test imports
echo.
echo [INFO] Testing imports...
python -c "from desktop import app; print('[OK] Desktop app imports successful')" 2>nul
if errorlevel 1 (
    echo [WARNING] Import test failed - you may need to install additional dependencies
) else (
    echo [OK] All imports successful
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the desktop app:
echo   1. Activate virtual environment: venv_desktop\Scripts\activate
echo   2. Run: python -m desktop.app
echo.
echo Or use the run_desktop.bat script
echo.
pause

