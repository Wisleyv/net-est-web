# cleanup_targets.ps1 - remove selected cache and venv directories safely and log actions
$log = 'C:\net\MAINTENANCE_LOG.md'
Add-Content $log "\n-- Deletion actions started: $(Get-Date)"
$targets = @(
    'C:\net\.venv_py312',
    'C:\net\backend\venv',
    'C:\net\.huggingface-cache',
    'C:\net\frontend\node_modules',
    'C:\net\backend\node_modules'
)
foreach ($t in $targets) {
    if (Test-Path $t) {
        Add-Content $log "Removing: $t"
        Write-Host "Removing: $t"
        try {
            Remove-Item -Recurse -Force -Path $t -ErrorAction Stop
            Add-Content $log "Removed: $t"
            Write-Host "Removed: $t" -ForegroundColor Green
        } catch {
            Add-Content $log "Failed to remove: $t - $_"
            Write-Host "Failed to remove: $t - $_" -ForegroundColor Red
        }
    } else {
        Add-Content $log "Not found (skipped): $t"
        Write-Host "Not found (skipped): $t"
    }
}
Add-Content $log "-- Deletion actions completed: $(Get-Date)"
Write-Host 'Deletion actions completed.'