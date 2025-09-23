#Requires -Version 5.1
<#
.SYNOPSIS
    Sets up the NET-EST backend Python environment
.DESCRIPTION
    Creates or validates the Python virtual environment and installs dependencies
.PARAMETER WorkspaceFolder
    Path to NET-EST workspace root (defaults to current directory parent)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$WorkspaceFolder = (Split-Path $PSScriptRoot -Parent | Split-Path -Parent)
)

$ErrorActionPreference = "Stop"

try {
    Write-Host 'Setting up NET-EST Backend Environment...' -ForegroundColor Cyan
    
    $BackendPath = Join-Path $WorkspaceFolder "backend"
    $VenvPath = Join-Path $BackendPath ".venv_py312"
    
    Set-Location $BackendPath
    
    if (Test-Path $VenvPath) {
        Write-Host 'Virtual environment exists, checking dependencies...' -ForegroundColor Green
        $PipExe = Join-Path $VenvPath "Scripts\pip.exe"
        & $PipExe install --quiet fastapi uvicorn pydantic sentence-transformers psutil
    } else {
        Write-Host 'Creating new virtual environment...' -ForegroundColor Yellow
        py -3.12 -m venv $VenvPath --prompt 'NET-EST'
        
        Write-Host 'Installing dependencies...' -ForegroundColor Blue
        $PipExe = Join-Path $VenvPath "Scripts\pip.exe"
        & $PipExe install --upgrade pip setuptools wheel
        & $PipExe install fastapi uvicorn[standard] pydantic pydantic-settings sentence-transformers transformers torch numpy scipy scikit-learn psutil python-multipart python-dotenv
    }
    
    Write-Host 'Backend environment ready!' -ForegroundColor Green
    exit 0
}
catch {
    Write-Error "Failed to setup backend environment: $($_.Exception.Message)"
    exit 1
}