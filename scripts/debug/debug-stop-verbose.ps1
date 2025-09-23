# Test version of stop script with extensive debugging
[CmdletBinding(SupportsShouldProcess=$true)]
param(
  [int[]] $Ports = @(8000, 5173, 3000),
  [switch] $Force
)

$ErrorActionPreference = 'Continue'
$VerbosePreference = 'Continue'

function Write-Info($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host $msg -ForegroundColor Green }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host $msg -ForegroundColor Red }

Write-Info "Starting stop_servers with extensive debugging..."
Write-Info "PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Info "Process ID of this script: $PID"
Write-Info "Ports to check: $($Ports -join ', ')"

try {
  # 3) Fallback: kill by listening ports
  foreach ($port in $Ports) {
    Write-Info "Processing port: $port"
    try {
      $listeners = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
      Write-Info "Found $($listeners.Count) listeners on port $port"
      
      if ($listeners) {
        $processIds = ($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
        Write-Info "Unique process IDs: $($processIds -join ', ')"
        
        if ($processIds) {
          Write-Info "Stopping processes on port ${port}: $($processIds -join ', ')"
          foreach ($currentProcessId in $processIds) {
            Write-Info "Attempting to stop process ID: $currentProcessId"
            try {
              if ($PSCmdlet.ShouldProcess("PID $currentProcessId (port $port)", "Stop-Process")) {
                Write-Info "Calling Stop-Process -Id $currentProcessId -Force:$($Force.IsPresent)"
                Stop-Process -Id $currentProcessId -Force:$Force.IsPresent -ErrorAction SilentlyContinue
                Write-Ok "Stop-Process command completed for PID $currentProcessId"
              } else {
                Write-Info "ShouldProcess returned false for PID $currentProcessId"
              }
            } catch { 
              Write-Err "Could not stop PID $currentProcessId for port ${port}: $($_.Exception.Message)"
              Write-Err "Error details: $($_.Exception | Format-List | Out-String)"
            }
          }
        }
      }
    } catch { 
      Write-Err "Port-based termination skipped for ${port}: $($_.Exception.Message)"
      Write-Err "Error details: $($_.Exception | Format-List | Out-String)"
    }
  }

  Write-Ok "Debug stop script completed successfully."

} catch {
  Write-Err "Unexpected error: $($_.Exception.Message)"
  Write-Err "Error details: $($_.Exception | Format-List | Out-String)"
  exit 1
}