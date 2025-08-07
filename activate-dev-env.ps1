# NET-EST Development Environment Activation
# Run this before starting development work

Write-Host "🚀 Activating NET-EST Development Environment..." -ForegroundColor Cyan

# Load project environment
. "c:\net\.env-configs\project-environment.ps1"

# Activate Python virtual environment
if (Test-Path "c:\net\backend\venv\Scripts\Activate.ps1") {
    & "c:\net\backend\venv\Scripts\Activate.ps1"
    Write-Host "  ✅ Python virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Virtual environment not found" -ForegroundColor Yellow
}

# Display environment status
Write-Host ""
Write-Host "📊 Environment Status:" -ForegroundColor Cyan
Write-Host "  Python Cache: $env:PYTHONPYCACHEPREFIX" -ForegroundColor White
Write-Host "  Pip Cache: $env:PIP_CACHE_DIR" -ForegroundColor White  
Write-Host "  HuggingFace Cache: $env:HUGGINGFACE_HUB_CACHE" -ForegroundColor White
Write-Host "  Torch Cache: $env:TORCH_HOME" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Ready for NET-EST development!" -ForegroundColor Green
