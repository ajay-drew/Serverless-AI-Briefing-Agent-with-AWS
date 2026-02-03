@echo off
echo ============================================================
echo AI Briefing Agent - Full Stack Local Development
echo ============================================================
echo.
echo Starting both Backend and Frontend servers...
echo.
echo Backend API will be available at:
echo   http://localhost:8080/docs (API Documentation)
echo   http://localhost:8080/api/health (Health Check)
echo.
echo Frontend will be available at:
echo   http://localhost:5173 (React App)
echo.
echo Press Ctrl+C in each server window to stop them
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist .venv\Scripts\activate.bat (
    if not exist venv\Scripts\activate.bat (
        echo Creating Python virtual environment...
        python -m venv .venv
        if errorlevel 1 (
            echo ERROR: Failed to create virtual environment
            echo Please make sure Python is installed and in your PATH
            pause
            exit /b 1
        )
    )
)

REM Activate virtual environment (prefer .venv, fallback to venv)
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    call venv\Scripts\activate.bat
)

REM Check if Python dependencies are installed
echo Checking Python dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install Python dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Please create a .env file with your configuration.
    echo You can copy .env.example as a template:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM Check if database tables exist, if not run migrations
echo Checking database migrations...
alembic current >nul 2>&1
if errorlevel 1 (
    echo Running database migrations...
    alembic upgrade head
    if errorlevel 1 (
        echo WARNING: Database migration failed
        echo Make sure DATABASE_URL is set in .env
        echo For local development, you can use:
        echo   DATABASE_URL=sqlite:///./local.db
        echo.
    )
)

REM Check if frontend dependencies are installed
echo Checking frontend dependencies...
if not exist frontend\node_modules (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        echo Please make sure Node.js and npm are installed
        cd ..
        pause
        exit /b 1
    )
    cd ..
)

echo.
echo ============================================================
echo Starting Servers...
echo ============================================================
echo.
echo [BACKEND] Starting FastAPI on http://localhost:8080
echo [FRONTEND] Starting Vite on http://localhost:5173
echo.
echo NOTE: Both servers are running. Close individual windows to stop.
echo ============================================================
echo.

REM Determine which venv to use
if exist .venv\Scripts\activate.bat (
    set VENV_PATH=.venv
) else (
    set VENV_PATH=venv
)

REM Start both servers in the background
start "AI Briefing - Backend" cmd /k "cd /d %CD% && %VENV_PATH%\Scripts\activate.bat && uvicorn app.main:app --reload --host 127.0.0.1 --port 8080"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

start "AI Briefing - Frontend" cmd /k "cd /d %CD%\frontend && npm run dev"

echo.
echo ============================================================
echo Both servers are starting in separate windows!
echo ============================================================
echo.
echo Backend: http://localhost:8080/docs
echo Frontend: http://localhost:5173
echo.
echo Close the individual server windows to stop them.
echo You can close this window now.
echo ============================================================
pause
