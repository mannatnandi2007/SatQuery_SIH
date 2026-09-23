@echo off
setlocal enabledelayedexpansion
title SatQuery AI — Intelligence Platform Launcher

echo ======================================================================
echo    SATQUERY AI  ^|  Multimodal Satellite Intelligence ^& VQA System
echo ======================================================================
echo.

:: Clean ROOT_DIR path without trailing slash
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"
cd /d "%ROOT_DIR%"

:: Detect Python executable (VirtualEnv or System Python)
set "PY_CMD=python"
if exist "%ROOT_DIR%\.venv\Scripts\python.exe" (
    set "PY_CMD=%ROOT_DIR%\.venv\Scripts\python.exe"
    echo [INFO] Using virtualenv Python: .venv
) else if exist "%ROOT_DIR%\venv\Scripts\python.exe" (
    set "PY_CMD=%ROOT_DIR%\venv\Scripts\python.exe"
    echo [INFO] Using virtualenv Python: venv
) else (
    where python >nul 2>nul
    if !ERRORLEVEL! neq 0 (
        where py >nul 2>nul
        if !ERRORLEVEL! equ 0 (
            set "PY_CMD=py"
        ) else (
            echo [ERROR] Python is not found in your system PATH.
            echo Please install Python 3.10+ and ensure "Add to PATH" is checked.
            pause
            exit /b 1
        )
    )
)

:: Clear lingering processes on ports 8000 and 8001
echo [INFO] Checking for lingering processes on port 8000 and 8001...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Freeing port 8000 PID %%a
    taskkill /F /PID %%a >nul 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo [INFO] Freeing port 8001 PID %%a
    taskkill /F /PID %%a >nul 2>nul
)

:: Verify React frontend build exists
if not exist "%ROOT_DIR%\frontend\dist\index.html" (
    echo [INFO] React production bundle not detected in frontend\dist.
    echo [INFO] Building React UI via Vite...
    cd /d "%ROOT_DIR%\frontend"
    call npm run build
    cd /d "%ROOT_DIR%"
)

echo.
echo [1/2] Starting Tier 1 Fine-Tuned RS-VLM Specialist on Port 8001...
echo       Hosting Qwen2-VL LoRA / BigEarthNet Checkpoint
start "SatQuery AI - Fine-Tuned RS-VLM [Port 8001]" /d "%ROOT_DIR%\backend" cmd /k "title SatQuery RS-VLM Specialist (Port 8001) && "%PY_CMD%" -m uvicorn serve_fine_tuned:app --host 127.0.0.1 --port 8001 --reload"

ping 127.0.0.1 -n 3 >nul 2>nul

echo [2/2] Starting SatQuery Main Orchestrator and React UI on Port 8000...
echo       Hosting FastAPI, Siamese Change Detection, Fusion and React SPA
start "SatQuery AI - Main Server [Port 8000]" /d "%ROOT_DIR%\backend" cmd /k "title SatQuery Main Server (Port 8000) && "%PY_CMD%" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

ping 127.0.0.1 -n 3 >nul 2>nul

echo.
echo ======================================================================
echo   SatQuery AI Platform is live!
echo.
echo   * Main Interface (React SPA):   http://localhost:8000
echo   * Main API Documentation:       http://localhost:8000/docs
echo   * RS-VLM Specialist Endpoint:   http://localhost:8001/analyze
echo   * RS-VLM Specialist Health:     http://localhost:8001/health
echo ======================================================================
echo.
echo Opening http://localhost:8000 in your browser...
start http://localhost:8000

echo.
echo Keep both service windows open while using the platform.
echo To shut down all services, run stop_satquery.bat.
echo Press any key to close this launcher window...
pause >nul
