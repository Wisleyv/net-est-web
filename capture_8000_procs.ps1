# Capture PIDs and full command lines for processes listening on port 8000
Write-Host "Inspecting listeners on port 8000..." -ForegroundColor Cyan
$lines = netstat -ano | Select-String -Pattern ':8000\s+.*LISTENING' | ForEach-Object { $_.Line }
if (-not $lines) {
    Write-Host "No listeners found on port 8000." -ForegroundColor Green
    exit 0
}
$pidList = @()
foreach ($line in $lines) {
    $cols = ($line -replace '^\s+','') -split '\s+'
    $listenPid = $cols[-1]
    if ($pidList -notcontains $listenPid) { $pidList += $listenPid }
}
Write-Host "PIDs listening on 8000: $($pidList -join ', ')" -ForegroundColor Cyan
foreach ($p in $pidList) {
    try {
        $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$p" -ErrorAction Stop
        $procName = $proc.Name
        $cmdLine = $proc.CommandLine
        if (-not $cmdLine) { $cmdLine = '<no command line available>' }
        Write-Host "PID $p => $procName" -ForegroundColor Yellow
        Write-Host "  Cmd: $cmdLine"
    } catch {
        Write-Host "PID $p => process not accessible or exited" -ForegroundColor Red
    }
}
