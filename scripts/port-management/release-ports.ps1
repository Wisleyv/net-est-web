param()

Write-Host 'Checking and releasing NET-EST ports...' -ForegroundColor Cyan

$ports = @(8000, 5173, 5174)

foreach ($port in $ports) {
    Write-Host "Checking port $port..." -ForegroundColor Gray
    
    $connections = netstat -ano | findstr ":$port"
    
    if ($connections) {
        Write-Host "Port $port in use:" -ForegroundColor Yellow
        $connections | ForEach-Object {
            $pids = ($_ -split '\s+' | Where-Object { $_ -match '^\d+$' })
            foreach ($pid in $pids) {
                try {
                    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($process) {
                        Write-Host "  Stopping PID $pid ($($process.ProcessName))" -ForegroundColor Red
                        Stop-Process -Id $pid -Force
                    }
                } catch {
                    Write-Host "  Could not stop PID $pid" -ForegroundColor Gray
                }
            }
        }
    } else {
        Write-Host "Port $port is free" -ForegroundColor Green
    }
}

Write-Host 'Port release complete.' -ForegroundColor Cyan