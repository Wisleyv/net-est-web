param()

Write-Host 'Cleaning Python cache files...' -ForegroundColor Yellow

# Find and remove all __pycache__ directories
Get-ChildItem -Path . -Recurse -Directory -Name '__pycache__' | ForEach-Object { 
    Remove-Item -Path $_ -Recurse -Force 
}

Write-Host 'Cache cleanup complete!' -ForegroundColor Green