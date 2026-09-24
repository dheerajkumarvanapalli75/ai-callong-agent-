@echo off
title AI Calling Agent - Frontend
cd /d "%~dp0"
echo [*] Starting Frontend Vite on port 5173...
call npm.cmd run dev -- --host 0.0.0.0 --port 5173
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Frontend process terminated with error code %ERRORLEVEL%
    pause
)
