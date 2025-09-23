param()

Write-Host 'Stopping backend server...' -ForegroundColor Yellow

$backendProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { 
    $_.CommandLine -like '*start_server.py*' -or 
    $_.CommandLine -like '*uvicorn*' -or 
    $_.CommandLine -like '*:8000*' 
}

if ($backendProcesses) {
    $backendProcesses | Stop-Process -Force
    Write-Host 'Backend server stopped.' -ForegroundColor Green
} else {
    Write-Host 'No backend server processes found.' -ForegroundColor Gray
}