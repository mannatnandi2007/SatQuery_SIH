@echo off
title SatQuery AI — Stop Platform
echo ======================================================================
echo    SATQUERY AI  ^|  Stopping Background Services
echo ======================================================================
echo.

echo Stopping services on Port 8000 (Main Server) and Port 8001 (RS-VLM)...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8000...
    taskkill /F /PID %%a >nul 2>nul
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8001...
    taskkill /F /PID %%a >nul 2>nul
)

echo.
echo All SatQuery AI services have been stopped.
timeout /t 2 >nul
