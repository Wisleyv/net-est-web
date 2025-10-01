# Identify and stop the entire Uvicorn reload process tree bound to port 8000
$ErrorActionPreference = 'Stop'

function Get-ListeningPids {
    $matches = netstat -ano | Select-String ':8000\s+.*LISTENING'
    if (-not $matches) { return @() }
    $pids = @()
    foreach ($match in $matches) {
        $cols = ($match.Line -replace '^\s+', '') -split '\s+'
        $pid = $cols[-1]
        if ($pid) { $pids += [int]$pid }
    }
    return ($pids | Sort-Object -Unique)
}

function Get-ProcessInfo($pid) {
    try {
        return Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$pid"
    } catch {
        Write-Host ("Failed to read process info for PID $pid: $($_.Exception.Message)") -ForegroundColor Red
        return $null
    }
}

# Recursively collect parent processes that belong to the Uvicorn/watchfiles tree
function Collect-RelatedPids {
    param(
        [int]$Pid,
        [int]$Depth,
        [hashtable]$Collected
    )

    if ($Collected.ContainsKey($Pid)) {
        if ($Depth -gt $Collected[$Pid].Depth) {
            $Collected[$Pid].Depth = $Depth
        }
        return
    }

    $info = Get-ProcessInfo -pid $Pid
    $Collected[$Pid] = [pscustomobject]@{
        Info  = $info
        Depth = $Depth
    }

    if (-not $info) { return }

    $parentId = [int]$info.ParentProcessId
    if ($parentId -le 0) { return }

    $parentInfo = Get-ProcessInfo -pid $parentId
    if (-not $parentInfo) { return }

    $commandLine = $parentInfo.CommandLine
    $isBackendParent = $false
    if ($commandLine) {
        if ($commandLine -match '(uvicorn|watchfiles|watchgod|start_optimized|src\.main:app)') {
            $isBackendParent = $true
        }
    }

    if ($isBackendParent) {
        Collect-RelatedPids -Pid $parentId -Depth ($Depth + 1) -Collected $Collected
    }
}

Write-Host 'Scanning for listeners on port 8000...' -ForegroundColor Cyan
$listeningPids = Get-ListeningPids
if (-not $listeningPids) {
    Write-Host 'No listeners found on port 8000.'
    exit 0
}

Write-Host ('Initial listener PIDs: ' + ($listeningPids -join ', '))
$related = @{}
foreach ($pid in $listeningPids) {
    Collect-RelatedPids -Pid $pid -Depth 0 -Collected $related
}

Write-Host 'Process tree slated for termination:' -ForegroundColor Yellow
foreach ($entry in ($related.GetEnumerator() | Sort-Object { $_.Value.Depth } -Descending)) {
    $pid = $entry.Key
    $info = $entry.Value.Info
    $depth = $entry.Value.Depth
    $indent = ' ' * ($depth * 2)
    if ($info) {
        Write-Host ("$indent- PID $pid (Depth $depth) :: $($info.CommandLine)")
    } else {
        Write-Host ("$indent- PID $pid (Depth $depth) :: <no command line available>")
    }
}

# Terminate parents first so the reloader cannot spawn new workers
$ordered = $related.GetEnumerator() | Sort-Object { $_.Value.Depth } -Descending
foreach ($entry in $ordered) {
    $pid = $entry.Key
    try {
        Stop-Process -Id $pid -Force -ErrorAction Stop
        Write-Host ("Stopped PID $pid") -ForegroundColor Green
    } catch {
        Write-Host ("Failed to stop PID $pid: $($_.Exception.Message)") -ForegroundColor Red
    }
}

# Double-check whether the port is still occupied; repeat once if necessary
Start-Sleep -Seconds 1
$remaining = Get-ListeningPids
if ($remaining) {
    Write-Host ('Warning: port 8000 still in use by PID(s): ' + ($remaining -join ', ')) -ForegroundColor Red
    Write-Host 'You may need to close these processes manually via Task Manager.'
    exit 1
}

Write-Host 'Port 8000 successfully released.' -ForegroundColor Green
