param()

Write-Host 'Stopping frontend server...' -ForegroundColor Yellow

$frontendProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { 
    $_.CommandLine -like '*vite*' -or 
    $_.CommandLine -like '*5173*' -or 
    $_.CommandLine -like '*npm*dev*' 
}

if ($frontendProcesses) {
    $frontendProcesses | Stop-Process -Force
    Write-Host 'Frontend server stopped.' -ForegroundColor Green
} else {
    Write-Host 'No frontend server processes found.' -ForegroundColor Gray
}