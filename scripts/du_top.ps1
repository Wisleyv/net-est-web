Write-Host 'Getting top-level directory sizes under C:\net (this may take a few minutes)...' -ForegroundColor Cyan
$root = 'C:\net'
$results = @()
Get-ChildItem -Path $root -Directory -Force | ForEach-Object {
    $p = $_.FullName
    $sizeBytes = (Get-ChildItem -Path $p -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $results += [PSCustomObject]@{FullName=$p; SizeMB = [math]::Round(($sizeBytes/1MB),2)}
}
$results | Sort-Object SizeMB -Descending | Select-Object -First 15 | Format-Table -AutoSize

Write-Host ''
Write-Host 'Presence check for common cache dirs:' -ForegroundColor Cyan
$paths=@('frontend\\node_modules','frontend\\node_modules\\.vite','frontend\\dist','frontend\\build','frontend\\node_modules\\.cache','backend\\venv','backend\\.venv','.venv','venv','.pytest_cache','.vscode\\.cache','.huggingface-cache','.cache')
foreach($p in $paths){ Write-Host "$p => " (Test-Path (Join-Path $root $p)) }
Write-Host ''
if(Test-Path (Join-Path $root '.git')){ Write-Host 'Git repo detected. Preview of git clean -fdxn (no deletions):' -ForegroundColor Yellow; Set-Location $root; git clean -fdxn } else { Write-Host 'No .git directory found in workspace root.' -ForegroundColor Yellow }
