Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Safe wrapper for environment status using new port-management-cli.ps1
$moduleCli = Join-Path -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) -ChildPath 'port-management-cli.ps1'
if (-not (Test-Path $moduleCli)) { Write-Host "port-management-cli.ps1 not found at $moduleCli" -ForegroundColor Yellow; exit 2 }

Write-Host 'NET-EST Environment Status:' -ForegroundColor Cyan
Write-Host 'Backend (.venv_py312):' -ForegroundColor Yellow
if (Test-Path "${PWD}\backend\.venv_py312\Scripts\python.exe") {
    Write-Host '✅ Python 3.12 venv exists' -ForegroundColor Green
    & "${PWD}\backend\.venv_py312\Scripts\python.exe" --version
} else {
    Write-Host '❌ Python 3.12 venv missing' -ForegroundColor Red
}

# Check port 8000 using the new CLI wrapper
Write-Host "\nPorts:" -ForegroundColor Yellow
try {
    $out = pwsh -NoProfile -File $moduleCli -Function Get-PortProcess -Port 8000 -ErrorAction Stop
    if ($LASTEXITCODE -eq 0 -and $out) {
        Write-Host "Port 8000 listeners:" -ForegroundColor Green
        $json = $out | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($json -is [System.Array]) {
            $json | ForEach-Object { Write-Host " - PID: $($_.OwningProcess) Name: $($_.ProcessName) Path: $($_.ExecutablePath)" }
        } else {
            Write-Host " - $($json.OwningProcess) $($json.ProcessName) $($json.ExecutablePath)"
        }
    } else {
        Write-Host 'No listeners on port 8000' -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error checking port 8000: $($_.Exception.Message)" -ForegroundColor Red
}

# Test port availability
try {
    pwsh -NoProfile -File $moduleCli -Function Test-PortAvailable -Port 8000
    if ($LASTEXITCODE -eq 0) { Write-Host 'Port 8000 available' -ForegroundColor Green } else { Write-Host 'Port 8000 in use' -ForegroundColor Yellow }
} catch {
    Write-Host "Test-PortAvailable failed: $($_.Exception.Message)" -ForegroundColor Red
}
