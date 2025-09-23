param()

Write-Host '=== NET-EST Safe Shutdown ===' -ForegroundColor Magenta

Write-Host 'Step 1: Stopping servers...' -ForegroundColor Cyan
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Write-Host 'Python processes stopped' -ForegroundColor Green

Stop-Process -Name node -Force -ErrorAction SilentlyContinue
Write-Host 'Node processes stopped' -ForegroundColor Green

Write-Host 'Step 2: Cleaning cache...' -ForegroundColor Cyan
Get-ChildItem -Recurse -Directory __pycache__ -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host '=== Shutdown Complete ===' -ForegroundColor Green