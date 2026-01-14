@echo off
REM Simple command file to run the AI Briefing Agent
echo ========================================
echo AI Briefing Agent
echo ========================================
echo.

REM Check if virtual environment exists
set VENV_PATH=venv
if not exist venv\Scripts\activate.bat (
    if exist .venv\Scripts\activate.bat (
        set VENV_PATH=.venv
    ) else (
        echo Creating virtual environment...
        python -m venv venv
        if errorlevel 1 (
            echo ERROR: Failed to create virtual environment
            echo Please make sure Python is installed and in your PATH
            pause
            exit /b 1
        )
        echo Virtual environment created successfully.
        echo.
        set VENV_PATH=venv
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call %VENV_PATH%\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
)

REM Check if .env file exists
if not exist .env (
    echo.
    echo WARNING: .env file not found!
    echo Please create .env file with your API keys.
    echo You can copy .env.example to .env and add your keys.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Running Agent with Email Sending...
echo ========================================
echo.
echo The agent will:
echo   1. Search for news articles
echo   2. Generate summaries
echo   3. Draft and send email to TEST_EMAIL_RECIPIENT from .env
echo.
echo Note: If TEST_EMAIL_RECIPIENT is not set, email will be logged only.
echo.

REM Run the agent
python main.py
set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE% equ 0 (
    echo ========================================
    echo Agent completed successfully!
    echo ========================================
) else (
    echo ========================================
    echo Agent completed with errors (Exit code: %EXIT_CODE%)
    echo ========================================
)

pause
exit /b %EXIT_CODE%
