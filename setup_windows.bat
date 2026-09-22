@echo off
REM ============================================================
REM  LibraryPro — Windows CMD Setup (for Command Prompt users)
REM  Double-click this file OR run: setup_windows.bat
REM ============================================================

echo.
echo ========================================
echo   LibraryPro Windows Setup
echo ========================================
echo.

REM ── Virtual env ──
echo.
echo [1/3] Setting up Python virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [OK] Virtual environment ready

REM ── Install packages ──
echo.
echo [2/3] Installing Python packages...
pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip install failed
    pause
    exit /b 1
)
echo [OK] Packages installed

REM ── .env file ──
echo.
echo [3/3] Setting up .env...
if not exist .env (
    copy .env.example .env
    echo [OK] .env created - EDIT IT with your MySQL password!
) else (
    echo [OK] .env already exists
)

echo.
echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo   Edit .env with your MySQL credentials/Gemini key, then run:
echo.
echo   Step 1: Setup database schema
echo     mysql -u root -p < database\schema.sql
echo.
echo   Step 2: Seed the 100 library books
echo     python seed_books.py
echo.
echo   Step 3: Run the app server
echo     python backend\app.py
echo.
echo   Step 4: Open browser
echo     http://localhost:5000
echo     Login: admin / admin@123
echo.
pause
