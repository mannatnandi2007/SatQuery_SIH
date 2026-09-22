@echo off
setlocal enabledelayedexpansion
title SatQuery AI — Intelligence Platform Launcher

echo ======================================================================
echo    SATQUERY AI  ^|  Multimodal Satellite Intelligence & VQA System
echo ======================================================================
echo.

:: Set root directory
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in your PATH.
    echo Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

:: Verify React frontend build exists
if not exist "%ROOT_DIR%frontend\dist\index.html" (
    echo [INFO] React production bundle not detected in frontend\dist.
    echo [INFO] Building React UI via Vite...
    cd /d "%ROOT_DIR%frontend"
    call npm run build
    cd /d "%ROOT_DIR%"
)

echo [1/2] Starting Tier 1 Fine-Tuned RS-VLM Specialist (Port 8001)...
echo       Hosting Qwen2-VL LoRA / BigEarthNet Checkpoint
start "SatQuery AI - Fine-Tuned RS-VLM [Port 8001]" cmd /k "title SatQuery RS-VLM Specialist (Port 8001) && cd /d "%ROOT_DIR%backend" && python -m uvicorn serve_fine_tuned:app --host 127.0.0.1 --port 8001 --reload"

timeout /t 3 >nul

echo [2/2] Starting SatQuery Main Orchestrator & React UI (Port 8000)...
echo       Hosting FastAPI, Siamese Change Detection, Fusion & React SPA
start "SatQuery AI - Main Server [Port 8000]" cmd /k "title SatQuery Main Server (Port 8000) && cd /d "%ROOT_DIR%backend" && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 >nul

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
echo Press any key to exit this launcher window...
pause >nul
