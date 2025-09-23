<# Lightweight integration test for scripts/port-management.ps1 (Phase 1)

This script exercises Get-PortProcess and Test-PortAvailable.
It is safe and read-only.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$module = Join-Path -Path (Split-Path -Parent $PSCommandPath) -ChildPath 'port-management.ps1'
if (-not (Test-Path $module)) { Write-Host "Module not found: $module" -ForegroundColor Red; exit 2 }

. $module

$portsToCheck = @(8000, 5173, 3000, 8001)
foreach ($port in $portsToCheck) {
    Write-Host "\n--- Port: $port ---" -ForegroundColor Cyan
    try {
        $res = Get-PortProcess -Port $port
        if ($res -and $res.Count -gt 0) {
            Write-Host "Listeners found:" -ForegroundColor Green
            $res | Format-Table LocalAddress,LocalPort,OwningProcess,ProcessName -AutoSize
        } else {
            Write-Host "No listeners found on port $port" -ForegroundColor Yellow
        }
    } catch {
        Write-Host ("Get-PortProcess error for {0}: {1}" -f $port, $_.Exception.Message) -ForegroundColor Red
    }

    try {
        $avail = Test-PortAvailable -Port $port -ConnectTimeoutMs 500
        Write-Host ("Test-PortAvailable => {0}" -f $avail) -ForegroundColor Cyan
    } catch {
        Write-Host ("Test-PortAvailable error for {0}: {1}" -f $port, $_.Exception.Message) -ForegroundColor Red
    }
}

Write-Host "\nTest script completed." -ForegroundColor Green
