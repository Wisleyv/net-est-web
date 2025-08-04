# PowerShell script to ensure correct directory and start backend
Set-Location $PSScriptRoot
Write-Host "Current directory: $(Get-Location)"
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"
Write-Host "Starting backend server..."
python start_optimized.py
