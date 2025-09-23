# du_top_dirs.ps1 - list top-level directory sizes under C:\net and write a summary
$root = 'C:\net'
$out = Join-Path $root 'tools\du_top_dirs_report.txt'
if (Test-Path $out) { Remove-Item $out -Force }
Add-Content $out "Disk usage report for $root - $(Get-Date)"
Add-Content $out "============================="
Get-ChildItem -Path $root -Force -Directory | ForEach-Object {
    $d = $_.FullName
    Write-Host "Scanning $d ..."
    $files = Get-ChildItem -Path $d -Recurse -File -ErrorAction SilentlyContinue
    $size = 0
    if ($files) { $size = ($files | Measure-Object -Property Length -Sum).Sum }
    $mb = [math]::Round($size/1MB,2)
    $line = "{0,-40} {1,10} MB  {2}" -f $_.Name, $mb, $d
    Write-Host $line
    Add-Content $out $line
}
Write-Host "Report written to $out"
Add-Content $out "Done."
