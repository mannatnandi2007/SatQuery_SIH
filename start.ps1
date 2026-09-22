# SatQuery AI — PowerShell Startup Script
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location "$scriptDir"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   SATQUERY AI  |  Multimodal Satellite Intelligence & VQA System     " -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Verify React frontend build exists
$distPath = Join-Path $scriptDir "frontend\dist\index.html"
if (-not (Test-Path $distPath)) {
    Write-Host "[INFO] React production bundle not detected in frontend\dist." -ForegroundColor Yellow
    Write-Host "[INFO] Building React UI via Vite..." -ForegroundColor Yellow
    Set-Location "$scriptDir\frontend"
    npm run build
    Set-Location "$scriptDir"
}

Write-Host "[1/2] Launching Tier 1 Fine-Tuned RS-VLM Specialist (Port 8001)..." -ForegroundColor Cyan
Write-Host "      Hosting Qwen2-VL LoRA / BigEarthNet Checkpoint" -ForegroundColor DarkGray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$scriptDir\backend'; python -m uvicorn serve_fine_tuned:app --host 127.0.0.1 --port 8001 --reload"

Start-Sleep -Seconds 3

Write-Host "[2/2] Launching SatQuery Main Orchestrator & React UI (Port 8000)..." -ForegroundColor Cyan
Write-Host "      Hosting FastAPI, Siamese Change Detection, Fusion & React SPA" -ForegroundColor DarkGray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$scriptDir\backend'; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  SatQuery AI Platform is live!                                       " -ForegroundColor Green
Write-Host "                                                                      " -ForegroundColor Green
Write-Host "  * Main Interface (React SPA):   http://localhost:8000               " -ForegroundColor White
Write-Host "  * Main API Documentation:       http://localhost:8000/docs          " -ForegroundColor White
Write-Host "  * RS-VLM Specialist Endpoint:   http://localhost:8001/analyze       " -ForegroundColor White
Write-Host "  * RS-VLM Specialist Health:     http://localhost:8001/health        " -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Opening http://localhost:8000 in your browser..." -ForegroundColor Cyan
Start-Process "http://localhost:8000"
