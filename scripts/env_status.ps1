Write-Host 'NET-EST Environment Status:' -ForegroundColor Cyan
Write-Host 'Backend (.venv_py312):' -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot/../backend/.venv_py312/Scripts/python.exe") {
  Write-Host '✅ Python 3.12 venv exists' -ForegroundColor Green
  & "$PSScriptRoot/../backend/.venv_py312/Scripts/python.exe" --version
} else {
  Write-Host '❌ Python 3.12 venv missing' -ForegroundColor Red
}
Write-Host 'Ports:' -ForegroundColor Yellow
try {
  $ports = 8000,5173,3000
  $conns = Get-NetTCPConnection -State Listen | Where-Object { $ports -contains $_.LocalPort }
  if ($conns) {
    foreach ($c in $conns) {
      "{0}:{1} PID={2}" -f $c.LocalAddress, $c.LocalPort, $c.OwningProcess | Write-Output
    }
  } else {
    Write-Host 'No dev servers running' -ForegroundColor Yellow
  }
} catch {
  Write-Host 'Port check unavailable' -ForegroundColor DarkYellow
}
