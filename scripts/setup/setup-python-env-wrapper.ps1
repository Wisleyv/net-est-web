param(
    [string]$WorkspaceFolder = $env:WORKSPACEFOLDER
)

# Resolve ${workspaceFolder} placeholder if present
if ([string]::IsNullOrEmpty($WorkspaceFolder) -and $env:COMPUTERNAME) {
    # Try to infer the workspace folder from the script's parent directories
    $WorkspaceFolder = (Get-Location).Path
}

Try {
    $venvPath = Join-Path -Path $WorkspaceFolder -ChildPath 'backend/.venv_py312/Scripts/python.exe'
    if (!(Test-Path $venvPath)) {
        Write-Host "Creating Python 3.12 venv at: $($WorkspaceFolder)\backend\.venv_py312" -ForegroundColor Yellow
        # Use an explicit absolute python.exe if available in PATH
        $pythonExe = 'C:/Python312/python.exe'
        if (!(Test-Path $pythonExe)) {
            Write-Error "Required Python executable not found at $pythonExe. Please install Python 3.12 or update this wrapper."; exit 2
        }
        & $pythonExe -m venv "$($WorkspaceFolder)\backend\.venv_py312"
        if ($LASTEXITCODE -ne 0) { Write-Error 'Failed to create venv.'; exit $LASTEXITCODE }
        Write-Host 'Virtual environment created successfully.' -ForegroundColor Green
    } else {
        Write-Host "Python 3.12 venv already exists: $venvPath" -ForegroundColor Green
    }
    exit 0
} Catch {
    Write-Error "Error while setting up venv: $_"
    exit 1
}
