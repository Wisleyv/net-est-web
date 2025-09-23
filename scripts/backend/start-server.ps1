param()

# Backend Server Starter
# Centralized Python venv path management for starting the FastAPI server

$ErrorActionPreference = "Stop"

Write-Host "Starting NET-EST Backend Server..." -ForegroundColor Cyan

# Define venv Python path
$venvPython = "backend\.venv_py312\Scripts\python.exe"

# Verify Python exists
if (-not (Test-Path $venvPython)) {
    Write-Host "Error: Python venv not found at $venvPython" -ForegroundColor Red
    Write-Host "Please run 'Setup Backend Environment' task first." -ForegroundColor Yellow
    exit 1
}

# Start the server
Write-Host "Using Python: $venvPython" -ForegroundColor Green
& $venvPython backend\start_server.py