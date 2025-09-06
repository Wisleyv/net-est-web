$lines = netstat -ano | Select-String ":8000\s+.*LISTENING"
$ids = @()
if ($lines) {
  foreach ($ln in $lines) {
    $cols = ($ln.Line -replace '^\s+','') -split '\s+'
    $id = $cols[-1]
    if ($id) { $ids += $id }
  }
  $ids = $ids | Sort-Object -Unique
  Write-Host "Found PIDs listening on port 8000: $($ids -join ', ')"
  foreach ($id in $ids) {
    Write-Host "--- PID: $id ---"
    try {
      $p = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$id"
      if ($p) {
        Write-Host "CommandLine:`n$p.CommandLine"
      } else {
        Write-Host "No process info for PID $id"
      }
    } catch {
      Write-Host ('Error retrieving process info for PID ' + $id + ': ' + $__)
    }
  }
} else {
  Write-Host "No listeners found on port 8000"
}
