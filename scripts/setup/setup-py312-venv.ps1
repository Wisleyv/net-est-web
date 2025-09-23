#Requires -Version 5.1
<#
.SYNOPSIS
    Sets up Python 3.12 virtual environment with test dependencies
.DESCRIPTION
    Creates the .venv_py312 virtual environment and installs all dependencies including test tools
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$WorkspaceFolder = (Split-Path $PSScriptRoot -Parent | Split-Path -Parent)
)

$ErrorActionPreference = "Stop"

try {
    $BackendPath = Join-Path $WorkspaceFolder "backend"
    $VenvPath = Join-Path $BackendPath ".venv_py312"
    
    if (!(Test-Path $VenvPath)) {
        Write-Host 'Creating Python 3.12 virtual environment...' -ForegroundColor Yellow
        py -3.12 -m venv $VenvPath
    }
    
    Write-Host 'Installing dependencies...' -ForegroundColor Blue
    $PipExe = Join-Path $VenvPath "Scripts\pip.exe"
    & $PipExe install -q --upgrade pip
    & $PipExe install -q -r (Join-Path $BackendPath "requirements.txt")
    & $PipExe install -q pytest requests
    
    Write-Host 'Python 3.12 environment ready!' -ForegroundColor Green
}
catch {
    Write-Error "Failed to setup Python 3.12 environment: $($_.Exception.Message)"
    exit 1
}