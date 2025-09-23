# backup_vscode_userdata.ps1
# Non-interactive comprehensive VS Code backup used before reinstall.
# Usage: pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_vscode_userdata.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ts = (Get-Date).ToString('yyyyMMdd_HHmmss')
$bak = Join-Path $env:USERPROFILE "vscode_reinstall_backup_$ts"
New-Item -ItemType Directory -Path $bak -Force | Out-Null
Write-Host "Backup root: $bak"

# Backup AppData\Roaming\Code (user settings, global storage, etc.)
$roamingCode = Join-Path $env:APPDATA 'Code'
if (Test-Path $roamingCode) {
    Write-Host "Backing up %APPDATA%\Code -> $($bak)\AppData_Code" -ForegroundColor Yellow
    try {
        Copy-Item -Path $roamingCode -Destination (Join-Path $bak 'AppData_Code') -Recurse -Force -ErrorAction Stop
        Write-Host "Backed up AppData Code" -ForegroundColor Green
    } catch {
        Write-Warning ("Failed to copy AppData Code: {0}" -f $_)
    }
} else { Write-Host "No %APPDATA%\Code folder found" -ForegroundColor Yellow }

# Backup Local AppData\Code (cache data)
$localCode = Join-Path $env:LOCALAPPDATA 'Code'
if (Test-Path $localCode) {
    Write-Host "Backing up %LOCALAPPDATA%\Code -> $($bak)\LocalAppData_Code" -ForegroundColor Yellow
    try {
        Copy-Item -Path $localCode -Destination (Join-Path $bak 'LocalAppData_Code') -Recurse -Force -ErrorAction Stop
        Write-Host "Backed up LocalAppData Code" -ForegroundColor Green
    } catch {
        Write-Warning ("Failed to copy LocalAppData Code: {0}" -f $_)
    }
} else { Write-Host "No %LOCALAPPDATA%\Code folder found" -ForegroundColor Yellow }

# Backup extensions folder
$extFolder = Join-Path $env:USERPROFILE '.vscode\extensions'
if (Test-Path $extFolder) {
    Write-Host "Backing up extensions folder -> $($bak)\extensions" -ForegroundColor Yellow
    try {
        Copy-Item -Path $extFolder -Destination (Join-Path $bak 'extensions') -Recurse -Force -ErrorAction Stop
        Write-Host "Backed up extensions folder" -ForegroundColor Green
    } catch {
        Write-Warning ("Failed to copy extensions folder: {0}" -f $_)
    }
} else { Write-Host "No extensions folder found" -ForegroundColor Yellow }

# Backup workspace .vscode and .code-workspace
$ws = (Resolve-Path -Path .).Path
if (Test-Path (Join-Path $ws '.vscode')) {
    Write-Host "Backing up workspace .vscode -> $($bak)\workspace_vscode" -ForegroundColor Yellow
    try {
        Copy-Item -Path (Join-Path $ws '.vscode') -Destination (Join-Path $bak 'workspace_vscode') -Recurse -Force -ErrorAction Stop
        Write-Host "Backed up workspace .vscode" -ForegroundColor Green
    } catch {
        Write-Warning ("Failed to copy workspace .vscode: {0}" -f $_)
    }
} else { Write-Host "No .vscode folder in workspace" -ForegroundColor Yellow }

$workspaceFiles = Get-ChildItem -Path $ws -Filter '*.code-workspace' -File -ErrorAction SilentlyContinue
if ($workspaceFiles) {
    New-Item -ItemType Directory -Path (Join-Path $bak 'workspace_files') -Force | Out-Null
    foreach ($f in $workspaceFiles) {
        Copy-Item -Path $f.FullName -Destination (Join-Path $bak 'workspace_files') -Force
    }
    Write-Host "Backed up .code-workspace files" -ForegroundColor Green
} else { Write-Host "No .code-workspace files found in workspace" -ForegroundColor Yellow }

# Export installed extensions list using code CLI if present
$codeExe = $null
try { $codeCmd = Get-Command code -ErrorAction SilentlyContinue; if ($codeCmd) { $codeExe = $codeCmd.Source } } catch {}
if ($codeExe) {
    Write-Host "Exporting installed extensions list via code CLI" -ForegroundColor Yellow
    try {
        & $codeExe --list-extensions 2>$null | Out-File -FilePath (Join-Path $bak 'extensions_list.txt') -Encoding UTF8
        Write-Host "Extensions list saved to: $($bak)\extensions_list.txt" -ForegroundColor Green
    } catch {
        Write-Warning ("Failed to export extensions list: {0}" -f $_)
    }
} else {
    Write-Host "code CLI not found; saved extension folder instead" -ForegroundColor Yellow
}

# Summarize
Write-Host "\nBackup complete. Backup root: $bak" -ForegroundColor Cyan
Write-Host "Contents summary:" -ForegroundColor Cyan
Get-ChildItem -Path $bak | Select-Object Name,PSIsContainer | Format-Table -AutoSize

# Save backup path to a marker file for later steps
$bak | Out-File -FilePath (Join-Path $env:USERPROFILE 'vscode_last_backup_path.txt') -Encoding UTF8
Write-Host "Saved backup path marker to: $env:USERPROFILE\vscode_last_backup_path.txt" -ForegroundColor Green

# End of non-interactive backup script
