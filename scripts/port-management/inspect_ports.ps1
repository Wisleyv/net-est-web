# Temporary inspector: list listeners on 8000 and 5173, map PIDs to processes, and probe endpoints
$ports = @(8000,5173)
$lines = netstat -ano
$pids = @()
foreach ($p in $ports) {
    $pattern = ":$p\s+.*LISTENING"
    $matches = $lines | Select-String -Pattern $pattern
    if ($matches) {
        Write-Host ('Lines for port ' + $p + ':') -ForegroundColor Cyan
        $matches | ForEach-Object { Write-Host $_.Line; $cols = ($_ -replace '^\s+','') -split '\s+'; $pid = $cols[-1]; $pids += $pid }
    } else {
        Write-Host ('No listeners for port ' + $p)
    }
}
$pids = $pids | Sort-Object -Unique
if ($pids.Count -gt 0) {
    Write-Host "`nPID -> Process mapping:" -ForegroundColor Cyan
    foreach ($pid in $pids) {
        try {
            $proc = Get-Process -Id $pid -ErrorAction Stop
            Write-Host "PID $pid => $($proc.ProcessName)"
            try { Write-Host "  Path: $($proc.MainModule.FileName)" } catch { Write-Host "  Path: <no-file>" }
        } catch {
            Write-Host "PID $pid => process not accessible or exited"
        }
    }
} else {
    Write-Host "No PIDs found for the requested ports"
}

Write-Host "`nHTTP probes:" -ForegroundColor Cyan
$urls = 'http://localhost:8000/','http://localhost:8000/docs','http://localhost:8000/openapi.json','http://localhost:5173/'
foreach ($u in $urls) {
    try {
        $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 5
        Write-Host "$u => $($r.StatusCode)"
    } catch {
        Write-Host "$u => error: $($_.Exception.Message)"
    }
}
