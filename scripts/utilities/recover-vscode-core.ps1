<#
recover_vscode_core.ps1

Purpose: Safe, reversible diagnostics & recovery helper for VS Code core failures when the GUI/Command Palette is non-functional.
- Collects VS Code logs and user settings into a timestamped backup folder
- Validates JSON in common workspace and VS Code files (tasks.json, settings.json, .code-workspace)
- Exports list of installed extensions (if `code` CLI is available)
- Offers to launch VS Code with a clean user-data & extensions directory for isolation testing
- Optionally moves cache folders to backups (non-destructive) to perform a clean start

Usage (PowerShell):
> pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\recover_vscode_core.ps1

IMPORTANT: This script only *moves* (not deletes) VS Code cache/workspace files to a backup location so you can restore them later.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
<#
recover_vscode_core.ps1

Purpose: Safe, reversible diagnostics & recovery helper for VS Code core failures when the GUI/Command Palette is non-functional.
- Collects VS Code logs and user settings into a timestamped backup folder
- Validates JSON in common workspace and VS Code files (tasks.json, settings.json, .code-workspace)
- Exports list of installed extensions (if `code` CLI is available)
- Offers to launch VS Code with a clean user-data & extensions directory for isolation testing
- Optionally moves cache folders to backups (non-destructive) to perform a clean start

Usage (PowerShell):
> pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\recover_vscode_core.ps1

IMPORTANT: This script only moves (not deletes) VS Code cache/workspace files to a backup location so you can restore them later.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Basic variables
$timestamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
$backupRoot = Join-Path -Path $env:TEMP -ChildPath "vscode_recovery_$timestamp"
$workspacePath = (Resolve-Path -Path .).Path

Write-Host "Recovery/diagnostic run: $timestamp" -ForegroundColor Cyan
Write-Host "Workspace: $workspacePath" -ForegroundColor Cyan
Write-Host "Backup root: $backupRoot`n" -ForegroundColor Cyan

# Create backup dirs
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$logsBackup = Join-Path $backupRoot 'logs'
$userBackup = Join-Path $backupRoot 'user'
$workspaceBackup = Join-Path $backupRoot 'workspace'
New-Item -ItemType Directory -Path $logsBackup -Force | Out-Null
New-Item -ItemType Directory -Path $userBackup -Force | Out-Null
New-Item -ItemType Directory -Path $workspaceBackup -Force | Out-Null

function Find-CodeExecutable {
    # Try `code` on PATH
    $codeCmd = Get-Command code -ErrorAction SilentlyContinue
    if ($codeCmd) { return $codeCmd.Source }

    # Common installation locations
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
        "$env:ProgramFiles\Microsoft VS Code\Code.exe",
        "$env:ProgramFiles(x86)\Microsoft VS Code\Code.exe",
        "$env:USERPROFILE\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

$codeExe = Find-CodeExecutable
if ($null -eq $codeExe) {
    Write-Warning "VS Code executable not found on PATH or common locations. Some steps (like launching with a clean profile) will be skipped."
} else {
    Write-Host "Found Code executable: $codeExe" -ForegroundColor Green
    try {
        $versionOut = & $codeExe --version 2>$null
        Write-Host "Code version:`n$versionOut" -ForegroundColor Green
    } catch {
        Write-Warning ("Unable to run Code --version: {0}" -f $_)
    }
}

# 1) Collect latest logs
$roaming = $env:APPDATA
$logsDir = Join-Path $roaming 'Code\logs'
if (Test-Path $logsDir) {
    Write-Host "Collecting latest logs from: $logsDir" -ForegroundColor Yellow
    # copy entire logs folder (safe)
    try {
        Copy-Item -Path $logsDir -Destination $logsBackup -Recurse -Force -ErrorAction Stop
        Write-Host "Logs copied to: $logsBackup" -ForegroundColor Green
    } catch {
        Write-Warning ("Failed copying logs: {0}" -f $_)
    }
} else {
    Write-Warning "Logs directory not found: $logsDir"
}

# 2) Backup User settings (non-destructive)
$userSettingsDir = Join-Path $roaming 'Code\User'
if (Test-Path $userSettingsDir) {
    Write-Host "Backing up User settings from: $userSettingsDir" -ForegroundColor Yellow
    Copy-Item -Path $userSettingsDir -Destination $userBackup -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "User settings backed up to: $userBackup" -ForegroundColor Green
} else {
    Write-Warning "VS Code User settings directory not found: $userSettingsDir"
}

# 3) Backup workspace files (.vscode and *.code-workspace)
$dotVscode = Join-Path $workspacePath '.vscode'
if (Test-Path $dotVscode) {
    Write-Host "Backing up workspace .vscode folder" -ForegroundColor Yellow
    Copy-Item -Path $dotVscode -Destination $workspaceBackup -Recurse -Force -ErrorAction SilentlyContinue
}
$workspaceFiles = Get-ChildItem -Path $workspacePath -Filter '*.code-workspace' -File -ErrorAction SilentlyContinue
if ($workspaceFiles) {
    foreach ($f in $workspaceFiles) { Copy-Item -Path $f.FullName -Destination $workspaceBackup -Force }
}
Write-Host "Workspace artifacts copied to: $workspaceBackup`n" -ForegroundColor Green

# 4) Export installed extensions list (if CLI available) OR list extension folder names
$extListFile = Join-Path $backupRoot 'extensions_list.txt'
if ($codeExe) {
    try {
        & $codeExe --list-extensions 2>$null | Out-File -FilePath $extListFile -Encoding UTF8
        Write-Host "Extensions list exported to $extListFile" -ForegroundColor Green
    } catch {
        Write-Warning ("Failed to export extensions via CLI: {0}. Falling back to folder list." -f $_)
    }
}
if (-not (Test-Path $extListFile)) {
    $extDirs = @()
    $userExt1 = Join-Path $env:USERPROFILE '.vscode\extensions'
    if (Test-Path $userExt1) { $extDirs += Get-ChildItem -Path $userExt1 -Directory | Select-Object -ExpandProperty Name }
    $extDirs | Out-File -FilePath $extListFile -Encoding UTF8
    Write-Host "Extensions folder listing exported to $extListFile" -ForegroundColor Green
}

# 5) Validate important JSON files (non-destructive checks)
function Test-JsonFile([string]$path) {
    if (-not (Test-Path $path)) { return @{Path=$path; Exists=$false} }
    $content = Get-Content -Path $path -Raw -ErrorAction SilentlyContinue
    try {
        $null = $content | ConvertFrom-Json -ErrorAction Stop
        return @{Path=$path; Exists=$true; Valid=$true}
    } catch {
        return @{Path=$path; Exists=$true; Valid=$false; Error=$_.Exception.Message}
    }
}

$filesToCheck = @()
$filesToCheck += Join-Path -Path $dotVscode -ChildPath 'tasks.json'
$filesToCheck += Join-Path -Path $dotVscode -ChildPath 'settings.json'
$filesToCheck += Join-Path -Path $workspacePath -ChildPath 'NET-est-optimized.code-workspace'
$report = @()
foreach ($f in $filesToCheck) {
    $r = Test-JsonFile -path $f
    $report += $r
}
$report | Format-Table -AutoSize

$reportFile = Join-Path $backupRoot 'json_validation.txt'
$report | Out-File -FilePath $reportFile -Width 200 -Encoding UTF8
Write-Host "JSON validation report saved to: $reportFile`n" -ForegroundColor Green

# 6) Provide an isolation test: run Code with clean profile (non-destructive)
if ($codeExe) {
    $tempUserData = Join-Path $backupRoot 'temp_user_data'
    $tempExtDir = Join-Path $backupRoot 'temp_extensions'
    New-Item -ItemType Directory -Path $tempUserData -Force | Out-Null
    New-Item -ItemType Directory -Path $tempExtDir -Force | Out-Null

    Write-Host "You can test VS Code startup with a clean profile (no extensions, fresh user data)." -ForegroundColor Yellow
    Write-Host "To run the test, press Y then Enter. (This launches VS Code; close it after testing.)"
    $go = Read-Host "Launch VS Code with clean profile now? (Y/N)"
    if ($go -match '^[Yy]') {
        $args = @("--user-data-dir", "$tempUserData", "--extensions-dir", "$tempExtDir", "$workspacePath")
        Write-Host "Launching: $codeExe $($args -join ' ')" -ForegroundColor Cyan
        Start-Process -FilePath $codeExe -ArgumentList $args
        Write-Host "Launched VS Code with clean profile. Wait for it to appear and test Command Palette / Tasks." -ForegroundColor Green
    } else {
        Write-Host "Skipping clean-profile test." -ForegroundColor Yellow
    }
} else {
    Write-Warning "Skipping clean-profile test because Code executable not found." -ForegroundColor Yellow
}

# 7) Offer to move caches to backups (non-destructive) — user confirmation required
$cacheCandidates = @()
$cacheCandidates += Join-Path -Path $roaming -ChildPath 'Code\CachedData'
$cacheCandidates += Join-Path -Path $roaming -ChildPath 'Code\CachedExtensions'
$cacheCandidates += Join-Path -Path $roaming -ChildPath 'Code\GPUCache'
$cacheCandidates += Join-Path -Path $roaming -ChildPath 'Code\User\workspaceStorage'
$cacheCandidates += Join-Path -Path $roaming -ChildPath 'Code\Backups'
$existing = $cacheCandidates | Where-Object { Test-Path $_ }
if ($existing.Count -gt 0) {
    Write-Host "The following cache/workspace storage folders were found:" -ForegroundColor Yellow
    $existing | ForEach-Object { Write-Host " - $_" }
    Write-Host "\nYou can move these folders to the backup directory (non-destructive). This often fixes corrupted extension host / workspace state issues." -ForegroundColor Yellow
    $doMove = Read-Host "Move detected cache folders to backup now? (Y/N)"
    if ($doMove -match '^[Yy]') {
        foreach ($p in $existing) {
            $dest = Join-Path $backupRoot (Split-Path $p -Leaf)
            Write-Host "Moving $p -> $dest"
            try {
                Move-Item -Path $p -Destination $dest -Force -ErrorAction Stop
                Write-Host (("Moved: {0}" -f $p)) -ForegroundColor Green
            } catch {
                Write-Warning (("Failed to move {0}: {1}" -f $p, $_))
            }
        }
        Write-Host "Cache folders moved to backup. Start VS Code normally to test. (This is reversible by moving them back.)" -ForegroundColor Green
    } else {
        Write-Host "Skipping cache move." -ForegroundColor Yellow
    }
} else {
    Write-Host "No common cache/workspace storage folders found to move." -ForegroundColor Yellow
}

# 8) Final instructions
Write-Host "\nRecovery run complete. Backups and diagnostics are in: $backupRoot" -ForegroundColor Cyan
Write-Host "If you need to restore any moved folders, they are inside the backup folder. To fully reinstall VS Code, first keep this backup folder safe (it contains your settings and extensions list)." -ForegroundColor Cyan

Write-Host "Suggested next steps:" -ForegroundColor Magenta
Write-Host "1) Run the clean-profile test above and check whether Command Palette / Tasks are functional." -ForegroundColor Magenta
Write-Host "2) If clean-profile works, you can either keep using the clean profile (copy necessary settings) or restore selective items from the backup." -ForegroundColor Magenta
Write-Host "3) If clean-profile also fails, consider reinstalling VS Code (see documentation) after backing up $backupRoot." -ForegroundColor Magenta

# end of script
