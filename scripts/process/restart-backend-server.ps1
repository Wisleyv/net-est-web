#Requires -Version 5.1
<#
.SYNOPSIS
    Restarts the NET-EST backend server
.DESCRIPTION
    Stops existing backend server processes and starts a new instance
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$WorkspaceFolder = (Split-Path $PSScriptRoot -Parent | Split-Path -Parent)
)

$ErrorActionPreference = "Stop"

try {
    Write-Host 'Restarting backend server...' -ForegroundColor Yellow
    
    # Stop existing backend processes
    Get-Process -Name python -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like '*start_server.py*' } | 
        Stop-Process -Force
    
    Start-Sleep -Seconds 2
    
    # Start new instance
    $BackendPath = Join-Path $WorkspaceFolder "backend"
    $PythonExe = Join-Path $BackendPath ".venv_py312\Scripts\python.exe"
    $ServerScript = Join-Path $BackendPath "start_server.py"
    
    Set-Location $BackendPath
    Write-Host 'Starting backend server with updated configuration...' -ForegroundColor Green
    & $PythonExe $ServerScript
}
catch {
    Write-Error "Failed to restart backend server: $($_.Exception.Message)"
    exit 1
}