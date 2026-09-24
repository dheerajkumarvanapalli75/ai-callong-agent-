@echo off
setlocal enabledelayedexpansion
title AI Calling Agent - Stop Script

echo ======================================================================
echo          AI CALLING AGENT PLATFORM - STOP SCRIPT
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Close Backend & Frontend CMD Windows
echo [*] Terminating server console windows...
taskkill /fi "WINDOWTITLE eq AI Calling Agent - Backend*" /f /t >nul 2>nul
taskkill /fi "WINDOWTITLE eq AI Calling Agent - Frontend*" /f /t >nul 2>nul

:: 2. Terminate any lingering processes listening on Port 8000 and 5173
echo [*] Releasing Ports 8000 (Backend) and 5173 (Frontend)...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000,5173 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }" >nul 2>nul

:: 3. Stop Podman Containers (if running)
echo [*] Stopping Podman database containers...
where podman >nul 2>nul
if %ERRORLEVEL% equ 0 (
    podman stop phone_agent_mongodb phone_agent_redis >nul 2>nul
    podman compose -f infra\podman-compose.yml down >nul 2>nul
    echo [OK] Podman containers stopped.
)

echo.
echo ======================================================================
echo   ALL SERVICES AND CONTAINERS HAVE BEEN STOPPED CLEANLY!
echo ======================================================================
echo.
pause
