@echo off
title AI Calling Agent - Backend
cd /d "%~dp0"
echo [*] Starting Backend FastAPI on port 8000...
call venv\Scripts\activate.bat
set PYTHONPATH=.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Backend process terminated with error code %ERRORLEVEL%
    pause
)
