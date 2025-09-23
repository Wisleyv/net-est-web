param()

# Backend Test Runner
# Centralized Python venv path management for running pytest

$ErrorActionPreference = "Stop"

Write-Host "Running NET-EST Backend Tests..." -ForegroundColor Cyan

# Define venv Python path
$venvPython = "backend\.venv_py312\Scripts\python.exe"

# Verify Python exists
if (-not (Test-Path $venvPython)) {
    Write-Host "Error: Python venv not found at $venvPython" -ForegroundColor Red
    Write-Host "Please run 'Setup Backend Environment' task first." -ForegroundColor Yellow
    exit 1
}

# Run tests
Write-Host "Using Python: $venvPython" -ForegroundColor Green
Write-Host "Test directory: backend\tests" -ForegroundColor Gray

& $venvPython -m pytest backend\tests -q