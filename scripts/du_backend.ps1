Write-Host 'Listing largest items under C:\net\backend...' -ForegroundColor Cyan
$root = 'C:\net\backend'
$results = @()
Get-ChildItem -Path $root -Force | ForEach-Object {
    $p = $_.FullName
    $size = (Get-ChildItem -Path $p -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $results += [PSCustomObject]@{Path=$p; SizeMB=[math]::Round($size/1MB,2)}
}
$results | Sort-Object SizeMB -Descending | Select-Object -First 40 | Format-Table -AutoSize
