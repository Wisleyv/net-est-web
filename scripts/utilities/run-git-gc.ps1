# run_git_gc.ps1 - run git gc and log output
Set-Location 'C:\net'
Write-Host 'Running git gc --aggressive --prune=now... (may take a while)'
$processInfo = Start-Process -FilePath git -ArgumentList 'gc','--aggressive','--prune=now' -NoNewWindow -RedirectStandardOutput 'C:\net\tools\git_gc_output.txt' -RedirectStandardError 'C:\net\tools\git_gc_err.txt' -Wait -PassThru
Write-Host 'git gc completed. Output captured to C:\net\tools\git_gc_output.txt'
Add-Content 'C:\net\MAINTENANCE_LOG.md' "`n[Step] git gc output:`n"
Get-Content 'C:\net\tools\git_gc_output.txt' | ForEach-Object { Add-Content 'C:\net\MAINTENANCE_LOG.md' $_ }
Get-Content 'C:\net\tools\git_gc_err.txt' | ForEach-Object { Add-Content 'C:\net\MAINTENANCE_LOG.md' $_ }
Write-Host 'git gc logs appended to MAINTENANCE_LOG.md'