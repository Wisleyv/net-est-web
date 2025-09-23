param(
    [string]$WorkspaceFolder = $env:WORKSPACEFOLDER
)

if ([string]::IsNullOrEmpty($WorkspaceFolder)) { $WorkspaceFolder = (Get-Location).Path }

Try {
    Write-Host 'Cleaning Python cache files...' -ForegroundColor Yellow
    Push-Location $WorkspaceFolder
    Get-ChildItem -Path . -Recurse -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq '__pycache__' } | ForEach-Object {
        Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
    }
    Write-Host 'Cache cleanup complete!' -ForegroundColor Green
    Pop-Location
    exit 0
} Catch {
    Write-Error "Cache cleanup failed: $_"
    exit 1
}
