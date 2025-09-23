# List owners of TCP port 8000, print command lines, then stop the processes
try {
    $conns = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction Stop
} catch {
    Write-Host 'Get-NetTCPConnection not available or failed, falling back to netstat parsing'
    $lines = netstat -ano | Select-String ':8000\s+.*LISTENING'
    $pids = @()
    foreach ($ln in $lines) { $cols = ($ln.Line -replace '^\s+','') -split '\s+'; $pids += $cols[-1] }
    $pids = $pids | Sort-Object -Unique
    if ($pids.Count -eq 0) { Write-Host 'No listeners found on port 8000'; exit 0 }
    foreach ($id in $pids) {
        Write-Host 'PID:' $id
        try { $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$id"; Write-Host 'CommandLine:'; Write-Host $proc.CommandLine } catch { Write-Host 'Cannot read command line for PID' $id }
    }
    Write-Host 'Stopping processes...'
    foreach ($id in $pids) { try { Stop-Process -Id $id -Force -ErrorAction Stop; Write-Host 'Stopped PID' $id } catch { Write-Host 'Failed to stop PID' $id } }
    exit 0
}

$owners = $conns | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
if (!$owners -or $owners.Count -eq 0) { Write-Host 'No listeners on port 8000 (via Get-NetTCPConnection)'; exit 0 }

Write-Host 'Found PIDs listening on port 8000:' ($owners -join ', ')
foreach ($id in $owners) {
    Write-Host '--- PID:' $id '---'
    try { $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$id"; Write-Host 'CommandLine:'; Write-Host $proc.CommandLine } catch { Write-Host 'Cannot read command line for PID' $id }
}

Write-Host 'Stopping these processes now...'
foreach ($id in $owners) {
    try { Stop-Process -Id $id -Force -ErrorAction Stop; Write-Host 'Stopped PID' $id } catch { Write-Host 'Failed to stop PID' $id }
}

Write-Host 'Done.'
