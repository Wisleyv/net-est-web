# backend_du.ps1 - compute sizes (MB) for immediate subdirectories under backend
$root = 'C:\net\backend'
$out = Join-Path 'C:\net\tools' 'backend_du_report.txt'
if (Test-Path $out) { Remove-Item $out -Force }
Add-Content $out "Backend disk usage report for $root - $(Get-Date)"
Get-ChildItem -Path $root -Force -Directory | ForEach-Object {
    $d = $_.FullName
    Write-Host "Scanning $d ..."
    $files = Get-ChildItem -Path $d -Recurse -File -ErrorAction SilentlyContinue
    $size = 0
    if ($files) { $size = ($files | Measure-Object -Property Length -Sum).Sum }
    $mb = [math]::Round($size/1MB,2)
    $line = "{0,-30} {1,10} MB  {2}" -f $_.Name, $mb, $d
    Write-Host $line
    Add-Content $out $line
}
Write-Host "Report written to $out"