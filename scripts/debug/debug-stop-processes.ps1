# Debug script to isolate the $PID variable issue
$ErrorActionPreference = 'Stop'

Write-Host "Testing port-based termination..." -ForegroundColor Cyan

$Ports = @(8000, 5173, 3000)

foreach ($port in $Ports) {
    try {
        Write-Host "Checking port $port..." -ForegroundColor Yellow
        $listeners = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
        if ($listeners) {
            $processIds = ($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
            if ($processIds) {
                Write-Host "Found processes on port ${port}: $($processIds -join ', ')" -ForegroundColor Green
                foreach ($processId in $processIds) {
                    Write-Host "Would stop process $processId" -ForegroundColor Magenta
                    # Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                }
            }
        } else {
            Write-Host "No listeners on port $port" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Error checking port ${port}: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "Debug script completed." -ForegroundColor Green