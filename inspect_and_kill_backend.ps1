# Inspect PIDs listening on port 8000, show command lines, and stop only ones matching backend patterns
Write-Host 'Inspecting listeners on port 8000...' -ForegroundColor Cyan
$lines = netstat -ano | Select-String ':8000\s+.*LISTENING'
if (-not $lines) { Write-Host 'No listeners on port 8000'; exit 0 }

$pids = @()
foreach ($ln in $lines) {
  $cols = ($ln.Line -replace '^\s+','') -split '\s+'
  $id = $cols[-1]
  if ($id) { $pids += $id }
}
$pids = $pids | Sort-Object -Unique
Write-Host ('Found PIDs: ' + ($pids -join ', '))

$toStop = @()
foreach ($id in $pids) {
  Write-Host "--- PID $id ---"
  try {
    $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$id"
    if ($proc) {
      $cmd = $proc.CommandLine
      Write-Host "CommandLine:"
      Write-Host $cmd
      # Decide if it's our backend: look for start_server.py, start_optimized.py or backend\venv\Scripts\python.exe
      if ($cmd -match 'start_server\.py' -or $cmd -match 'start_optimized\.py' -or $cmd -match '\\backend\\venv\\Scripts\\python\.exe') {
        Write-Host '-> Marking for stop (backend candidate)'
        $toStop += $id
      } else {
        Write-Host '-> Not marked for stop'
      }
    } else {
      Write-Host 'No process info available'
    }
  } catch {
    Write-Host ('Error reading process info for PID ' + $id + ': ' + $_.Exception.Message)
  }
}

if ($toStop.Count -eq 0) { Write-Host 'No backend-related PIDs to stop' ; exit 0 }

Write-Host 'Stopping backend-related PIDs: ' ($toStop -join ', ') -ForegroundColor Yellow
foreach ($id in $toStop) {
  try {
    Stop-Process -Id $id -Force -ErrorAction Stop
    Write-Host ('Stopped PID ' + $id) -ForegroundColor Green
  } catch {
    Write-Host ('Failed to stop PID ' + $id + ': ' + $_.Exception.Message) -ForegroundColor Red
  }
}

Write-Host 'Done.'
