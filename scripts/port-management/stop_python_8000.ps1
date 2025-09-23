# Stop Python processes listening on port 8000
$lines = netstat -ano | Select-String -Pattern ':8000\s+.*LISTENING' | ForEach-Object { $_.Line }
if (-not $lines) {
    Write-Host "No listeners found on port 8000." -ForegroundColor Green
    exit 0
}
$found = @()
foreach ($l in $lines) {
    $cols = ($l -replace '^\s+','') -split '\s+'
    $thepid = $cols[-1]
    if ($found -notcontains $thepid) { $found += $thepid }
}
if ($found.Count -eq 0) {
    Write-Host "No PIDs parsed from netstat lines." -ForegroundColor Yellow
    exit 0
}
Write-Host "PIDs listening on 8000: $($found -join ', ')" -ForegroundColor Cyan
foreach ($targetPid in $found) {
    try {
        $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$targetPid" -ErrorAction Stop
        $name = $proc.Name
        $cmd = $proc.CommandLine
        Write-Host "PID $targetPid => $name" -ForegroundColor Cyan
        Write-Host "  Cmd: $cmd"
        if ($name -match '(?i)python' -or ($cmd -and $cmd -match '(?i)python')) {
            Write-Host "  -> Identified as Python process, stopping PID $targetPid..." -ForegroundColor Yellow
            try { Stop-Process -Id $targetPid -Force -ErrorAction Stop; Write-Host "  -> PID $targetPid terminated." -ForegroundColor Green } catch { Write-Host ('  -> Failed to terminate PID ' + $targetPid + ': ' + $_.Exception.Message) -ForegroundColor Red }
        } else {
            Write-Host "  -> Not a Python process; skipping." -ForegroundColor Gray
        }
    } catch {
        Write-Host "PID $targetPid => process not accessible or already exited" -ForegroundColor Yellow
    }
}
