<#
.SYNOPSIS
  Port management utilities (Phase 1) - detection only.

.DESCRIPTION
  Provides `Get-PortProcess` and `Test-PortAvailable` to detect which process(es)
  are using a local TCP port and to verify whether a port is available for use.

  This Phase 1 module intentionally excludes termination/kill operations. It is
  designed for safe, read-only inspection and lightweight programmatic checks.

.NOTES
  - Create logs under scripts/logs/port-management.log
  - Designed to be called with `pwsh -NoProfile -File scripts/port-management.ps1 -Function Get-PortProcess -Port 8000`
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Log {
    param([string]$Message)
    try {
        $logDir = Join-Path -Path (Split-Path -Parent $PSCommandPath) -ChildPath 'logs'
        if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
        $logFile = Join-Path $logDir 'port-management.log'
        $entry = "$(Get-Date -Format o) | $Message"
        Add-Content -Path $logFile -Value $entry -ErrorAction SilentlyContinue
    } catch { }
}

function Get-PortProcess {
    <#
    .SYNOPSIS
      Returns detailed information about process(es) listening on a TCP port.

    .PARAMETER Port
      TCP port to inspect (1-65535)

    .EXAMPLE
      Get-PortProcess -Port 8000

    .OUTPUTS
      An array of PSObjects with properties: LocalAddress, LocalPort, State,
      OwningProcess, ProcessName, CommandLine, ExecutablePath, ParentProcessId
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][ValidateRange(1,65535)][int]$Port
    )

    Write-Log "Get-PortProcess called for port $Port"

    try {
        # Use Get-NetTCPConnection where available; fall back to no-op if not present
        try {
            $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        } catch {
            Write-Log "Get-NetTCPConnection failed: $($_.Exception.Message)"
            return @()
        }

        if (-not $conns -or $conns.Count -eq 0) {
            Write-Log "No listeners found on port $Port"
            return @()
        }

        $results = @()
        foreach ($c in $conns) {
            $procId = $c.OwningProcess
            $procName = $null
            $cmdLine = $null
            $exePath = $null
            $parent = $null

            try {
                $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
                if ($p) { $procName = $p.ProcessName }
            } catch { }

            try {
                $info = Get-CimInstance -Namespace root\cimv2 -ClassName Win32_Process | Where-Object { $_.ProcessId -eq $procId }
                if ($info) {
                    $cmdLine = $info.CommandLine
                    $exePath = $info.ExecutablePath
                    $parent = $info.ParentProcessId
                }
            } catch {
                Write-Log ("Get-CimInstance failed for PID {0}: {1}" -f $procId, $_.Exception.Message)
            }

            $obj = [PSCustomObject]@{
                LocalAddress    = $c.LocalAddress
                LocalPort       = $c.LocalPort
                State           = $c.State
                OwningProcess   = $procId
                ProcessName     = $procName
                CommandLine     = $cmdLine
                ExecutablePath  = $exePath
                ParentProcessId = $parent
            }
            $results += $obj
        }

        Write-Log "Get-PortProcess returning $($results.Count) entry(s) for port $Port"
        return $results
    } catch {
        Write-Log "Get-PortProcess unexpected error: $($_.Exception.Message)"
        throw
    }
}

function Test-PortAvailable {
    <#
    .SYNOPSIS
      Tests whether a local TCP port is available for binding.

    .PARAMETER Port
      TCP port to test (1-65535)

    .EXAMPLE
      Test-PortAvailable -Port 8000

    .OUTPUTS
      Boolean: $true if available, $false if in use or unreachable for binding
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][ValidateRange(1,65535)][int]$Port,
        [int]$ConnectTimeoutMs = 1000
    )

    Write-Log "Test-PortAvailable called for port $Port"

    try {
        try {
            $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        } catch {
            Write-Log "Test-PortAvailable: Get-NetTCPConnection failed: $($_.Exception.Message)"
            # If Get-NetTCPConnection is unavailable or fails, attempt a TCP connect test below
            $conns = $null
        }

        if ($conns -and $conns.Count -gt 0) {
            Write-Log "Port $Port is in LISTEN state"
            return $false
        }

        # Attempt a TCP connect to check if some other endpoint accepts connections
        try {
            $client = New-Object System.Net.Sockets.TcpClient
            $async = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
            $wait = $async.AsyncWaitHandle.WaitOne($ConnectTimeoutMs)
            if ($wait -and $client.Connected) {
                $client.EndConnect($async)
                $client.Close()
                Write-Log "Test-PortAvailable: port $Port accepted a TCP connection (in use)"
                return $false
            } else {
                try { $client.Close() } catch { }
                Write-Log "Test-PortAvailable: port $Port appears available"
                return $true
            }
        } catch {
            Write-Log "Test-PortAvailable TCP connect attempt failed: $($_.Exception.Message)"
            # If connect fails, assume available for bind (but return false conservatively?)
            # We'll return $true here because no listener was detected and TCP connect failed likely due to no service.
            return $true
        }

    } catch {
        Write-Log "Test-PortAvailable unexpected error: $($_.Exception.Message)"
        throw
    }
}

# NOTE: This file defines functions only. Use dot-sourcing in scripts or
# call the dedicated CLI wrapper `scripts/port-management-cli.ps1` to invoke
# functions from the command line without parsing issues.
