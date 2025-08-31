# PowerShell script to git-move common debug/backup files into backend/archived/
# Run from repo root (C:\net) in PowerShell:
#   .\scripts\archive_debug_files.ps1
# The script uses git mv so history is preserved. It will skip missing files.

$repoRoot = Resolve-Path .
$archiveDir = Join-Path $repoRoot "backend\archived"

if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir | Out-Null
}

# Patterns to archive (adjust as needed)
$patterns = @(
    "backend\debug_*.py",
    "backend\debug-*.py",
    "backend\src\services\*.py.bak",
    "backend\src\services\strategy_detector_backup*.py",
    "vscode_backup_*",
    "backend\*.py.bak"
)

$anyMoved = $false

foreach ($pattern in $patterns) {
    $matches = Get-ChildItem -Path $repoRoot -Recurse -ErrorAction SilentlyContinue |
               Where-Object { $_.FullName -like (Join-Path $repoRoot $pattern) }
    foreach ($m in $matches) {
        $relativePath = $m.FullName.Substring($repoRoot.Path.Length + 1)
        $dest = Join-Path $archiveDir $m.Name
        Write-Host "Archiving $relativePath -> backend/archived/$($m.Name)"
        git mv --force -- "$("$($m.FullName)")" "$dest" 2>$null
        if ($LASTEXITCODE -eq 0) { $anyMoved = $true }
    }
}

if ($anyMoved) {
    git commit -m "chore: archive debug and backup files to backend/archived (non-destructive)"
    Write-Host "Archived files committed. Review and push the branch as needed."
} else {
    Write-Host "No matching debug/backup files found to archive. Please review patterns in the script."
}
