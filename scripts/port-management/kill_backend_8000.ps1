# List PIDs listening on port 8000, print command lines, then attempt to stop them
Write-Host 'Listing listeners on port 8000...' -ForegroundColor Cyan
$lines = netstat -ano | Select-String ':8000\s+.*LISTENING'
if (-not $lines) {
    Write-Host 'No listeners found on port 8000.'
    exit 0
}

$pids = @()
foreach ($ln in $lines) {
    $cols = ($ln.Line -replace '^\s+','') -split '\s+'
    $id = $cols[-1]
    if ($id) { $pids += $id }
}
$pids = $pids | Sort-Object -Unique
Write-Host ('Found PIDs: ' + ($pids -join ', '))

foreach ($id in $pids) {
    Write-Host "--- PID: $id ---"
    try {
        $info = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$id"
        if ($info) {
            Write-Host 'CommandLine:'
            Write-Host $info.CommandLine
        } else {
            Write-Host 'No process info available (might be elevated or system process)'
        }
    } catch {
        Write-Host ('Failed to read process info for PID ' + $id + ': ' + $_.Exception.Message)
    }
}

Write-Host 'Attempting to stop these processes (Stop-Process -Force)...' -ForegroundColor Yellow
foreach ($id in $pids) {
    try {
        Stop-Process -Id $id -Force -ErrorAction Stop
        Write-Host ('Stopped PID ' + $id) -ForegroundColor Green
    } catch {
        Write-Host ('Failed to stop PID ' + $id + ': ' + $_.Exception.Message) -ForegroundColor Red
    }
}

Write-Host 'Done.'
