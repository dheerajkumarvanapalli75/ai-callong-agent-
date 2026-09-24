@echo off
setlocal enabledelayedexpansion
title AI Calling Agent - Launcher

echo ======================================================================
echo          AI CALLING AGENT PLATFORM - START SCRIPT
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Check & prepare .env file
if not exist ".env" (
    echo [*] Creating .env from .env.example...
    copy ".env.example" ".env" >nul
    echo [OK] .env file initialized.
) else (
    echo [OK] .env configuration file found.
)

:: 2. Check and start databases with Podman
echo.
echo [*] Checking database services via Podman...
where podman >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [*] Starting MongoDB and Redis with Podman...
    podman compose -f infra\podman-compose.yml up -d mongodb redis 2>nul
    if not errorlevel 1 (
        echo [OK] Podman database containers started successfully.
    ) else (
        echo [!] Podman containers already running or offline. Backend will connect or use in-memory fallback.
    )
) else (
    echo [!] Podman CLI not detected in PATH. Backend will use in-memory database fallback.
)

:: 3. Setup and verify Backend
echo.
echo [*] Checking backend environment...
if not exist "backend\venv\Scripts\python.exe" (
    echo [*] Setting up Python virtual environment in backend\venv...
    python -m venv backend\venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
        pause
        exit /b 1
    )
    echo [*] Installing backend dependencies...
    backend\venv\Scripts\pip install -r backend\requirements.txt
)
echo [OK] Backend virtual environment ready.

:: 4. Setup and verify Frontend
echo.
echo [*] Checking frontend environment...
if not exist "frontend\node_modules" (
    echo [*] Installing frontend node_modules...
    cd frontend
    call npm.cmd install
    cd ..
)
echo [OK] Frontend dependencies ready.

:: 5. Launch Backend in dedicated window
echo.
echo [*] Starting Backend - FastAPI on http://localhost:8000 ...
start "AI Calling Agent - Backend" "%~dp0backend\run.bat"

:: 6. Launch Frontend in dedicated window
echo [*] Starting Frontend - Vite on http://localhost:5173 ...
start "AI Calling Agent - Frontend" "%~dp0frontend\run.bat"

:: 7. Wait briefly and open application in default browser
echo.
echo [*] Waiting 3 seconds for services to initialize...
ping 127.0.0.1 -n 4 >nul
start http://localhost:5173

echo.
echo ======================================================================
echo   ALL SERVICES STARTED SUCCESSFULLY!
echo ======================================================================
echo.
echo   Frontend Dashboard:  http://localhost:5173
echo   Backend Health:      http://localhost:8000/health
echo   Backend API Docs:    http://localhost:8000/api/v1/docs
echo.
echo   To stop all services and containers, run: stop.bat
echo ======================================================================
echo.
pause
