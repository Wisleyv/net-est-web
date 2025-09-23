param()

Write-Host 'Comprehensive cache cleanup...' -ForegroundColor Cyan

Write-Host 'Cleaning Python cache files...' -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory -Name '__pycache__' -ErrorAction SilentlyContinue | ForEach-Object { 
    Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue 
}

Write-Host 'Cleaning Node.js cache...' -ForegroundColor Yellow
if (Test-Path 'frontend/node_modules/.cache') { 
    Remove-Item -Path 'frontend/node_modules/.cache' -Recurse -Force -ErrorAction SilentlyContinue 
}

Write-Host 'Cleaning Vite cache...' -ForegroundColor Yellow
if (Test-Path 'frontend/node_modules/.vite') { 
    Remove-Item -Path 'frontend/node_modules/.vite' -Recurse -Force -ErrorAction SilentlyContinue 
}

Write-Host 'Cleaning temporary files...' -ForegroundColor Yellow
Get-ChildItem -Path . -Name '*.tmp' -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Name 'tmp_*' -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host 'Cache cleanup complete!' -ForegroundColor Green