param(
  [int]$Port = 8000
)

Write-Host "Inspecting listeners on port $Port..." -ForegroundColor Cyan

try {
  $listeners = Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object { $_.LocalPort -eq $Port }
} catch {
  Write-Host "Get-NetTCPConnection unavailable; falling back to netstat parsing" -ForegroundColor DarkYellow
  $lines = netstat -ano | Select-String -Pattern ":$Port\s+.*LISTENING" | ForEach-Object { $_.Line }
  if (-not $lines) { Write-Host "No listeners found on port $Port." -ForegroundColor Green; exit 0 }
  $pids = @()
  foreach ($line in $lines) {
    $cols = ($line -replace '^\s+','') -split '\s+'
    $pid = $cols[-1]
    if ($pids -notcontains $pid) { $pids += $pid }
  }
  $listeners = foreach ($pid in $pids) {
    [pscustomobject]@{ LocalAddress='0.0.0.0'; LocalPort=$Port; OwningProcess=[int]$pid }
  }
}

if (-not $listeners -or $listeners.Count -eq 0) {
  Write-Host "No listeners found on port $Port." -ForegroundColor Green
  exit 0
}

$uniquePids = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
Write-Host ("PIDs listening on {0}: {1}" -f $Port, ($uniquePids -join ', ')) -ForegroundColor Cyan

foreach ($procId in $uniquePids) {
  try {
    $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$procId" -ErrorAction Stop
    $name = $proc.Name
    $cmd  = if ($proc.CommandLine) { $proc.CommandLine } else { '<no command line available>' }
    Write-Host ("PID {0} => {1}" -f $procId, $name) -ForegroundColor Yellow
    Write-Host "  Cmd: $cmd"
  } catch {
    Write-Host ("PID {0} => process not accessible or exited" -f $procId) -ForegroundColor Red
  }
}
