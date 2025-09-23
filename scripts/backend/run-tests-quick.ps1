param()

# Backend Quick Test Runner
# For running tests from backend directory (simpler path)

$ErrorActionPreference = "Stop"

Write-Host "Running Backend Tests (Quick)..." -ForegroundColor Cyan

# Define venv Python path
$venvPython = ".venv_py312\Scripts\python.exe"

# Verify Python exists
if (-not (Test-Path $venvPython)) {
    Write-Host "Error: Python venv not found at $venvPython" -ForegroundColor Red
    Write-Host "Please run 'Setup Backend Environment' task first." -ForegroundColor Yellow
    exit 1
}

# Run tests
Write-Host "Using Python: $venvPython" -ForegroundColor Green
& $venvPython -m pytest -q