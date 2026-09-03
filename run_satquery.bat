@echo off
title SatQuery AI - Launcher
echo ========================================================
echo        SatQuery AI - Satellite Image VQA System
echo ========================================================
echo.

cd /d "%~dp0backend"

echo [1/2] Starting Fine-Tuned RS-VLM Specialist on port 8001...
start "SatQuery Fine-Tuned Specialist (Port 8001)" cmd /k "python -m uvicorn serve_fine_tuned:app --host 127.0.0.1 --port 8001"

timeout /t 2 >nul

echo [2/2] Starting SatQuery Main Orchestrator on port 8000...
start "SatQuery Main Server (Port 8000)" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000"

timeout /t 2 >nul

echo.
echo ========================================================
echo   SatQuery AI is running!
echo   Frontend UI: http://localhost:8000
echo ========================================================
start http://localhost:8000
pause
