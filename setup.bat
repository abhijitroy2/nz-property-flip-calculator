@echo off
REM Setup script for NZ Property Flip Calculator (Windows)

echo Setting up NZ Property Flip Calculator...

REM Check prerequisites
echo Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed. Please install Node.js 16 or higher.
    exit /b 1
)

where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL is not installed. Please install PostgreSQL 12 or higher.
    exit /b 1
)

echo Prerequisites met

REM Setup database
echo.
echo Setting up database...
set /p db_user="Enter PostgreSQL username (default: postgres): "
if "%db_user%"=="" set db_user=postgres

set /p db_password="Enter PostgreSQL password: "

set /p db_name="Enter database name (default: nz_property_flip): "
if "%db_name%"=="" set db_name=nz_property_flip

REM Create database
set PGPASSWORD=%db_password%
psql -U %db_user% -c "CREATE DATABASE %db_name%;" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Database created
) else (
    echo Database may already exist (this is okay)
)

REM Setup backend
echo.
echo Setting up backend...
cd backend

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Create .env file
if not exist .env (
    copy .env.example .env
    echo Created .env file - please update DATABASE_URL with your credentials
) else (
    echo .env file already exists
)

deactivate
cd ..

REM Setup frontend
echo.
echo Setting up frontend...
cd frontend

call npm install

cd ..

echo.
echo Setup complete!
echo.
echo To run the application:
echo.
echo 1. Start the backend (in one terminal):
echo    cd backend
echo    venv\Scripts\activate
echo    python app.py
echo.
echo 2. Start the frontend (in another terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open http://localhost:3000 in your browser
echo.

pause

