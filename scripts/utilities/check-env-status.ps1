<#
.SYNOPSIS
Enhanced environment status check for NET-EST project (Fixed)

.DESCRIPTION
Provides comprehensive status information about the NET-EST development environment,
including Python environment, port usage, and service status.

.NOTES
Author: NET-EST Development Team
Version: 1.1.0 (Fixed)
Date: 2025-09-23
#>

param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

# Define colors for consistent output
$colors = @{
    Header = 'Cyan'
    Success = 'Green'
    Warning = 'Yellow' 
    Error = 'Red'
    Info = 'Blue'
    Detail = 'Gray'
}

# Helper function to write colored output
function Write-StatusMessage {
    param(
        [string]$Message,
        [string]$Type = 'Info',
        [string]$Prefix = ''
    )
    
    $color = $colors[$Type]
    if ($Prefix) {
        Write-Host "$Prefix " -NoNewline -ForegroundColor $color
        Write-Host $Message
    } else {
        Write-Host $Message -ForegroundColor $color
    }
}

# Main status check function
function Get-EnvironmentStatus {
    Write-StatusMessage "NET-EST Environment Status Check" -Type 'Header'
    Write-Host ("=" * 50) -ForegroundColor $colors.Header
    
    # Determine workspace folder - try multiple methods
    $workspaceFolder = $env:WORKSPACEFOLDER
    if (-not $workspaceFolder -or -not (Test-Path $workspaceFolder)) {
        # Try to detect from script location (assuming script is in scripts/utilities/ subdirectory)
        $scriptDir = Split-Path -Parent $PSCommandPath
        $scriptsDir = Split-Path -Parent $scriptDir
        $workspaceFolder = Split-Path -Parent $scriptsDir
        Write-StatusMessage "Auto-detected workspace: $workspaceFolder" -Type 'Info'
    }
    
    if (-not (Test-Path $workspaceFolder)) {
        Write-StatusMessage "❌ Cannot determine workspace folder" -Type 'Error'
        return
    }
    
    # Check Python environments
    Write-StatusMessage "`nPython Environment Status:" -Type 'Header'
    
    # Check for Python 3.12 venv (primary)
    $venv312Path = "$workspaceFolder\backend\.venv_py312\Scripts\python.exe"
    if (Test-Path $venv312Path) {
        Write-StatusMessage "✅ Python 3.12 virtual environment found" -Type 'Success'
        try {
            $pythonVersion = & $venv312Path --version 2>$null
            Write-StatusMessage "   Version: $pythonVersion" -Type 'Detail'
        } catch {
            Write-StatusMessage "   Warning: Could not get Python version" -Type 'Warning'
        }
    } else {
        Write-StatusMessage "❌ Python 3.12 virtual environment missing" -Type 'Error'
        Write-StatusMessage "   Expected: $venv312Path" -Type 'Detail'
    }
    
    # Check for legacy venv
    $venvLegacyPath = "$workspaceFolder\backend\venv\Scripts\python.exe"
    if (Test-Path $venvLegacyPath) {
        Write-StatusMessage "📋 Legacy virtual environment found" -Type 'Info'
        try {
            $pythonVersion = & $venvLegacyPath --version 2>$null
            Write-StatusMessage "   Version: $pythonVersion" -Type 'Detail'
        } catch {
            Write-StatusMessage "   Warning: Could not get legacy Python version" -Type 'Warning'
        }
    }
    
    # Check key Python packages
    if (Test-Path $venv312Path) {
        Write-StatusMessage "`nKey Package Status:" -Type 'Header'
        try {
            $pipPath = "$workspaceFolder\backend\.venv_py312\Scripts\pip.exe"
            $packages = & $pipPath list 2>$null | Where-Object { $_ -match '(fastapi|uvicorn|sentence-transformers|torch|transformers)' }
            if ($packages) {
                foreach ($package in $packages) {
                    Write-StatusMessage "   $package" -Type 'Success' -Prefix '✅'
                }
            } else {
                Write-StatusMessage "⚠️  No key packages found - may need installation" -Type 'Warning'
            }
        } catch {
            Write-StatusMessage "❌ Could not check package status" -Type 'Error'
        }
    }
    
    # Check port status using basic netstat
    Write-StatusMessage "`nPort Status Analysis:" -Type 'Header'
    try {
        $netstatOutput = netstat -an | Select-String ":800[0-9].*LISTENING|:300[0-9].*LISTENING|:517[0-9].*LISTENING"
        if ($netstatOutput) {
            foreach ($line in $netstatOutput) {
                Write-StatusMessage "   $line" -Type 'Detail'
            }
        } else {
            Write-StatusMessage "❌ No services detected on common ports (8000, 3000, 5173)" -Type 'Warning'
        }
    } catch {
        Write-StatusMessage "❌ Port status check failed" -Type 'Error'
    }
    
    # Check workspace structure
    Write-StatusMessage "`nWorkspace Structure:" -Type 'Header'
    
    $criticalPaths = @(
        "$workspaceFolder\backend",
        "$workspaceFolder\frontend",
        "$workspaceFolder\scripts",
        "$workspaceFolder\docs",
        "$workspaceFolder\docs_dev"
    )
    
    foreach ($path in $criticalPaths) {
        if (Test-Path $path) {
            $itemCount = (Get-ChildItem $path | Measure-Object).Count
            Write-StatusMessage "✅ $(Split-Path $path -Leaf) ($itemCount items)" -Type 'Success'
        } else {
            Write-StatusMessage "❌ $(Split-Path $path -Leaf) (missing)" -Type 'Error'
        }
    }
    
    Write-StatusMessage "`nEnvironment Status Check Complete!" -Type 'Header'
}

# Execute the status check
try {
    Get-EnvironmentStatus
    exit 0
} catch {
    Write-StatusMessage "❌ Environment status check failed: $($_.Exception.Message)" -Type 'Error'
    exit 1
}