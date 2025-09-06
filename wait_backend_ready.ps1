# Poll for backend readiness and show PIDs + command lines for listeners on port 8000
$timeout = 60
$start = Get-Date
Write-Host "Waiting up to $timeout seconds for backend to be ready..." -ForegroundColor Cyan
while ((Get-Date) -lt $start.AddSeconds($timeout)) {
    $lines = netstat -ano | Select-String -Pattern ':8000\s+.*LISTENING' | ForEach-Object { $_.Line }
    $pids = @()
    foreach ($l in $lines) { $cols = ($l -replace '^\s+','') -split '\s+'; $pids += $cols[-1] }
    $pids = $pids | Sort-Object -Unique
    if ($pids.Count -gt 0) {
        Write-Host "Found listeners on 8000: $($pids -join ', ')" -ForegroundColor Green
        foreach ($pid in $pids) {
            try {
                $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$pid" -ErrorAction Stop
                $cmd = $proc.CommandLine
                $name = $proc.Name
                Write-Host "PID $pid => $name" -ForegroundColor Cyan
                Write-Host "  Cmd: $cmd"
            } catch {
                Write-Host "PID $pid => process not accessible" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "No listeners on 8000 yet." -ForegroundColor Yellow
    }

    # Probe two endpoints
    $ok = $true
    foreach ($u in ('http://localhost:8000/docs','http://localhost:8000/openapi.json')) {
        try {
            $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 3
            Write-Host "$u => $($r.StatusCode)"
            if ($r.StatusCode -ne 200) { $ok = $false }
        } catch {
            Write-Host "$u => error: $($_.Exception.Message)"
            $ok = $false
        }
    }
    if ($ok) { Write-Host "Backend is ready." -ForegroundColor Green; exit 0 }
    Start-Sleep -Seconds 1
}
Write-Host "Timeout waiting for backend readiness after $timeout seconds." -ForegroundColor Red
exit 2
