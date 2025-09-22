<#
.SYNOPSIS
Enhanced environment status check for NET-EST project

.DESCRIPTION
Provides comprehensive status information about the NET-EST development environment,
including Python environment, port usage, and service status. Uses robust CLI wrappers
for port detection to avoid PowerShell parsing errors.

.NOTES
Author: NET-EST Development Team
Version: 1.0.0
Date: 2025-09-22
#>

param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'  # Allow continuing on non-critical errors

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
        # Try to detect from script location (assuming script is in scripts/ subdirectory)
        $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
        $workspaceFolder = Split-Path -Parent $scriptDir
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
    
    # Check port status using CLI wrapper
    Write-StatusMessage "`nPort Status Analysis:" -Type 'Header'
    
    $cliWrapperPath = "$workspaceFolder\scripts\port-management-cli.ps1"
    if (Test-Path $cliWrapperPath) {
        # Check backend port 8000
        try {
            $result8000 = & $cliWrapperPath -Function "Get-PortProcess" -Port 8000 2>$null
            if ($LASTEXITCODE -eq 0 -and $result8000) {
                $portInfo = $result8000 | ConvertFrom-Json
                Write-StatusMessage "✅ Backend running on port 8000" -Type 'Success'
                Write-StatusMessage "   Process: $($portInfo.ProcessName) (PID: $($portInfo.OwningProcess))" -Type 'Detail'
                Write-StatusMessage "   Command: $($portInfo.CommandLine)" -Type 'Detail'
            } else {
                Write-StatusMessage "❌ Backend not running on port 8000" -Type 'Error'
            }
        } catch {
            Write-StatusMessage "⚠️  Could not check port 8000 status" -Type 'Warning'
        }
        
        # Check frontend ports 3000 and 5173
        foreach ($port in @(3000, 5173)) {
            try {
                $result = & $cliWrapperPath -Function "Get-PortProcess" -Port $port 2>$null
                if ($LASTEXITCODE -eq 0 -and $result) {
                    $portInfo = $result | ConvertFrom-Json
                    Write-StatusMessage "✅ Service running on port $port" -Type 'Success'
                    Write-StatusMessage "   Process: $($portInfo.ProcessName) (PID: $($portInfo.OwningProcess))" -Type 'Detail'
                } else {
                    Write-StatusMessage "❌ No service running on port $port" -Type 'Error'
                }
            } catch {
                Write-StatusMessage "⚠️  Could not check port $port status" -Type 'Warning'
            }
        }
    } else {
        Write-StatusMessage "❌ Port management CLI wrapper not found" -Type 'Error'
        Write-StatusMessage "   Expected: $cliWrapperPath" -Type 'Detail'
        
        # Fallback to basic netstat check
        Write-StatusMessage "   Using fallback netstat check..." -Type 'Info'
        try {
            $netstatOutput = netstat -an | Select-String ":800[0-9].*LISTENING|:300[0-9].*LISTENING|:517[0-9].*LISTENING"
            if ($netstatOutput) {
                foreach ($line in $netstatOutput) {
                    Write-StatusMessage "   $line" -Type 'Detail'
                }
            } else {
                Write-StatusMessage "   No services detected on common ports" -Type 'Warning'
            }
        } catch {
            Write-StatusMessage "   Fallback netstat check failed" -Type 'Error'
        }
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
            Write-StatusMessage "✅ $(Split-Path $path -Leaf)/ ($itemCount items)" -Type 'Success'
        } else {
            Write-StatusMessage "❌ $(Split-Path $path -Leaf)/ missing" -Type 'Error'
        }
    }
    
    # Summary
    Write-StatusMessage "`nEnvironment Summary:" -Type 'Header'
    Write-StatusMessage "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Type 'Detail'
    Write-StatusMessage "PowerShell Version: $($PSVersionTable.PSVersion)" -Type 'Detail'
    Write-StatusMessage "Execution Policy: $(Get-ExecutionPolicy)" -Type 'Detail'
    
    Write-Host "`n" -NoNewline
    Write-StatusMessage "Environment Status Check Complete" -Type 'Header'
}

# Execute the status check
try {
    Get-EnvironmentStatus
    exit 0
} catch {
    Write-StatusMessage "❌ Environment status check failed: $($_.Exception.Message)" -Type 'Error'
    exit 1
}