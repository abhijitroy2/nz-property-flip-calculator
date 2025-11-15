@echo off
REM Quick launcher for RealFlip Desktop App

REM Navigate to project root
cd /d "%~dp0\.."

REM Check if virtual environment exists
if not exist "venv_desktop" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_desktop.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv_desktop\Scripts\activate.bat

REM Check for command line arguments
if "%1"=="--run-once" (
    echo Running analysis once...
    python -m desktop.app --run-once
) else if "%1"=="--show-config-path" (
    python -m desktop.app --show-config-path
) else (
    echo Starting RealFlip Desktop App...
    echo.
    python -m desktop.app
)

pause

