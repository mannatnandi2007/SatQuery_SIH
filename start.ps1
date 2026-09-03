# SatQuery AI — PowerShell Startup Script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location "$scriptDir\backend"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       SatQuery AI - Satellite Image VQA System         " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Launching Fine-Tuned Specialist (Port 8001)..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn serve_fine_tuned:app --host 127.0.0.1 --port 8001"

Start-Sleep -Seconds 2

Write-Host "[2/2] Launching Main Backend & UI (Port 8000)..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn main:app --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Opening http://localhost:8000 in your browser..." -ForegroundColor Green
Start-Process "http://localhost:8000"
