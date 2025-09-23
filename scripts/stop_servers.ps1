<#
.SYNOPSIS
  Safely stops local NET-EST backend and frontend dev servers.

.DESCRIPTION
  - Stops Python backend processes related to start_server.py/uvicorn (port 8000 by default)
  - Stops frontend dev server processes (Vite/Node) typically on ports 5173 or 3000
  - Also kills any process listening on the provided Ports list as a fallback

.PARAMETER Ports
  Ports to target for termination via owning process. Default: 8000, 5173, 3000

.PARAMETER Force
  Use -Force when stopping processes.

.EXAMPLE
  pwsh -ExecutionPolicy Bypass -File scripts/stop_servers.ps1

.EXAMPLE
  pwsh -ExecutionPolicy Bypass -File scripts/stop_servers.ps1 -Ports 8000,5173 -Force
#>

[CmdletBinding(SupportsShouldProcess=$true)]
param(
  [int[]] $Ports = @(8000, 5173, 3000),
  [switch] $Force,
  [int] $MaxRetries = 5,
  [int] $WaitMs = 400
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host $msg -ForegroundColor Green }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host $msg -ForegroundColor Red }

try {
  Write-Info "NET-EST: Stopping dev servers..."

  # 1) Stop backend python processes by command line signature
  $backendCandidates = @()
  try {
    $backendCandidates = Get-Process -Name python -ErrorAction SilentlyContinue |
      Where-Object { $_.CommandLine -match 'start_server\.py|uvicorn|gunicorn' }
  } catch { }

  if ($backendCandidates.Count -gt 0) {
    Write-Info "Attempting to stop backend (python) processes: $($backendCandidates.Id -join ', ')"
    foreach ($p in $backendCandidates) {
      try {
        if ($PSCmdlet.ShouldProcess("PID $($p.Id)", "Stop-Process")) {
          Stop-Process -Id $p.Id -Force:$Force.IsPresent -ErrorAction SilentlyContinue
        }
      } catch { Write-Warn "Could not stop backend process PID $($p.Id): $($_.Exception.Message)" }
    }
  } else {
    Write-Warn "No backend python processes matched (start_server.py/uvicorn)."
  }

  # 2) Stop frontend (Vite/Node) processes by command line signature
  $frontendCandidates = @()
  try {
    $frontendCandidates = Get-Process -Name node -ErrorAction SilentlyContinue |
      Where-Object { $_.CommandLine -match 'vite|react-scripts|vite-node' }
  } catch { }

  if ($frontendCandidates.Count -gt 0) {
    Write-Info "Attempting to stop frontend (node) processes: $($frontendCandidates.Id -join ', ')"
    foreach ($p in $frontendCandidates) {
      try {
        if ($PSCmdlet.ShouldProcess("PID $($p.Id)", "Stop-Process")) {
          Stop-Process -Id $p.Id -Force:$Force.IsPresent -ErrorAction SilentlyContinue
        }
      } catch { Write-Warn "Could not stop frontend process PID $($p.Id): $($_.Exception.Message)" }
    }
  } else {
    Write-Warn "No node/vite processes matched."
  }

  # 3) Fallback: kill by listening ports with retries (handles PID churn)
  function Get-ListeningByPorts([int[]] $p) {
    try {
      return Get-NetTCPConnection -State Listen | Where-Object { $p -contains $_.LocalPort }
    } catch { return @() }
  }

  for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
    $listeners = Get-ListeningByPorts -p $Ports
    if (-not $listeners -or $listeners.Count -eq 0) { break }

    $pids = ($listeners | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -gt 0 })
    if ($pids -and $pids.Count -gt 0) {
      Write-Info ("[Attempt ${attempt}/${MaxRetries}] Stopping listeners by port: " + ($listeners | Select-Object LocalPort, OwningProcess | Sort-Object LocalPort | Format-Table -HideTableHeaders | Out-String).Trim())
      foreach ($procId in $pids) {
        try {
          if ($PSCmdlet.ShouldProcess("PID $procId (port-based)", "Stop-Process + taskkill /T")) {
            # Try native Stop-Process first
            Stop-Process -Id $procId -Force:$Force.IsPresent -ErrorAction SilentlyContinue
            # Then ensure the process tree is terminated
            try {
              Start-Process -FilePath "taskkill.exe" -ArgumentList "/PID", $procId, "/T", "/F" -NoNewWindow -Wait -ErrorAction SilentlyContinue | Out-Null
            } catch { }
          }
        } catch {
          Write-Warn "Could not stop PID ${procId}: $($_.Exception.Message)"
        }
      }
      Start-Sleep -Milliseconds $WaitMs
    } else {
      break
    }
  }

  # 4) Summary check
  $backAlive = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'start_server\.py|uvicorn|gunicorn' }
  $frontAlive = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'vite|react-scripts|vite-node' }
  $portAlive = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $Ports -contains $_.LocalPort }

  if (-not $backAlive -and -not $frontAlive -and -not $portAlive) {
    Write-Ok "All target dev servers appear to be stopped."
  } else {
    Write-Warn "Some targets may still be active. Review manually if needed."
    if ($backAlive)  { Write-Warn ("Backend PIDs still alive: " + ($backAlive.Id -join ', ')) }
    if ($frontAlive) { Write-Warn ("Frontend PIDs still alive: " + ($frontAlive.Id -join ', ')) }
    if ($portAlive)  {
      $byPort = $portAlive | Group-Object LocalPort | ForEach-Object {
        $lp = $_.Name; $pids = ($_.Group | Select-Object -ExpandProperty OwningProcess -Unique);
        "${lp}: " + ($pids -join ', ')
      }
      Write-Warn ("Ports still listening: " + ($byPort -join ' | '))
    }
  }

} catch {
  Write-Err "Unexpected error: $($_.Exception.Message)"
  exit 1
}