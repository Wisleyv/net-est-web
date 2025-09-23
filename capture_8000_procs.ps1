param(
    [int]$Port = 8000
)

$scriptPath = Join-Path $PSScriptRoot 'scripts/capture_8000_procs.ps1'
if (Test-Path $scriptPath) {
    & pwsh -NoProfile -ExecutionPolicy Bypass -File $scriptPath -Port $Port
} else {
    Write-Host "scripts/capture_8000_procs.ps1 not found; falling back to inline netstat parser" -ForegroundColor DarkYellow
    $lines = netstat -ano | Select-String -Pattern ":$Port\s+.*LISTENING" | ForEach-Object { $_.Line }
    if (-not $lines) { Write-Host "No listeners found on port $Port." -ForegroundColor Green; exit 0 }
    $pids = @()
        foreach ($line in $lines) {
            $cols = ($line -replace '^\s+','') -split '\s+'
            $procId = $cols[-1]
            if ($pids -notcontains $procId) { $pids += $procId }
    }
        Write-Host "PIDs listening on $Port: $($pids -join ', ')" -ForegroundColor Cyan
        foreach ($procId in $pids) {
        try {
                $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$procId" -ErrorAction Stop
            $name = $proc.Name
            $cmd  = if ($proc.CommandLine) { $proc.CommandLine } else { '<no command line available>' }
                Write-Host "PID $procId => $name" -ForegroundColor Yellow
            Write-Host "  Cmd: $cmd"
        } catch {
                Write-Host "PID $procId => process not accessible or exited" -ForegroundColor Red
        }
    }
}
