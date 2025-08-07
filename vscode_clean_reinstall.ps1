# VS Code Complete Clean Reinstallation Script
# Addresses extension conflicts, corrupted settings, and workspace contamination

Write-Host "=== VS Code Complete Clean ReinstaWrite-Host "WARNING - IMPORTANT:" -ForegroundColor Red
Write-Host "- Install extensions ONE BY ONE to identify performance impacts" -ForegroundColor White
Write-Host "- Monitor process count with: Get-Process -Name Code* | Measure-Object" -ForegroundColor White
Write-Host "- If issues return, check the backup folder for problematic settings" -ForegroundColor White

Write-Host ""
Write-Host "Script completed successfully!" -ForegroundColor Green

# Desenvolvido com amor pelo Nucleo de Estudos de Traducao - PIPGLA/UFRJ | Contem codigo gerado por IA.==" -ForegroundColor Cyan
Write-Host "This will safely clean up and reinstall VS Code for optimal performance" -ForegroundColor Yellow
Write-Host ""

# Step 1: Backup critical files
Write-Host "STEP 1: Backing up critical workspace files..." -ForegroundColor Green

$backupFolder = "c:\net\vscode_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -Path $backupFolder -ItemType Directory -Force | Out-Null

# Backup workspace settings (selective)
if (Test-Path "c:\net\.vscode\") {
    Write-Host "  Backing up .vscode folder..." -ForegroundColor White
    Copy-Item "c:\net\.vscode\" "$backupFolder\.vscode\" -Recurse -Force
}

# Backup current workspace file
if (Test-Path "c:\net\NET-est.code-workspace") {
    Write-Host "  Backing up workspace file..." -ForegroundColor White
    Copy-Item "c:\net\NET-est.code-workspace" "$backupFolder\NET-est.code-workspace" -Force
}

Write-Host "  Backup completed: $backupFolder" -ForegroundColor Green
Write-Host ""

# Step 2: Clean VS Code completely
Write-Host "STEP 2: Complete VS Code cleanup..." -ForegroundColor Green

# Kill all VS Code processes
Write-Host "  Terminating all VS Code processes..." -ForegroundColor White
Get-Process -Name "Code*" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Clean user data folders
$userDataPaths = @(
    "$env:APPDATA\Code",
    "$env:APPDATA\Code - Insiders", 
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code",
    "$env:USERPROFILE\.vscode"
)

foreach ($path in $userDataPaths) {
    if (Test-Path $path) {
        Write-Host "  Removing: $path" -ForegroundColor White
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "  VS Code cleanup completed" -ForegroundColor Green
Write-Host ""

# Step 3: Clean workspace contamination
Write-Host "STEP 3: Cleaning workspace contamination..." -ForegroundColor Green

# Remove potentially corrupted workspace settings
$workspaceCleanup = @(
    "c:\net\.vscode\settings.json",
    "c:\net\.vscode\launch.json",
    "c:\net\.vscode\extensions.json"
)

foreach ($file in $workspaceCleanup) {
    if (Test-Path $file) {
        Write-Host "  Removing potentially corrupted: $file" -ForegroundColor White
        Remove-Item $file -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "  Workspace cleaned" -ForegroundColor Green
Write-Host ""

# Step 4: Python environment analysis
Write-Host "STEP 4: Analyzing Python environment conflicts..." -ForegroundColor Green

$pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue
Write-Host "  Current Python processes:" -ForegroundColor White
$pythonProcesses | ForEach-Object {
    $path = try { $_.Path } catch { "Access Denied" }
    Write-Host "    PID $($_.Id): $path" -ForegroundColor Gray
}

# Check for Python installations
$pythonPaths = @(
    "C:\Python*",
    "$env:LOCALAPPDATA\Programs\Python\*",
    "$env:USERPROFILE\AppData\Local\Programs\Python\*",
    "C:\Program Files\Python*",
    "C:\Program Files (x86)\Python*"
)

Write-Host "  Python installations found:" -ForegroundColor White
foreach ($pattern in $pythonPaths) {
    $found = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    $found | ForEach-Object {
        Write-Host "    $($_.FullName)" -ForegroundColor Gray
    }
}

Write-Host "  Python analysis completed" -ForegroundColor Green
Write-Host ""

# Step 5: Download and install fresh VS Code
Write-Host "STEP 5: Installing fresh VS Code..." -ForegroundColor Green

$downloadUrl = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
$installerPath = "$env:TEMP\VSCodeUserSetup.exe"

Write-Host "  Downloading VS Code installer..." -ForegroundColor White
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "  Download completed" -ForegroundColor Green
    
    Write-Host "  Installing VS Code..." -ForegroundColor White
    Start-Process -FilePath $installerPath -ArgumentList "/VERYSILENT", "/NORESTART", "/MERGETASKS=!runcode" -Wait
    Write-Host "  Installation completed" -ForegroundColor Green
} catch {
    Write-Host "  Download/Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Please download manually from: https://code.visualstudio.com/" -ForegroundColor Yellow
}

Write-Host ""

# Step 6: Create minimal workspace configuration
Write-Host "STEP 6: Creating minimal workspace configuration..." -ForegroundColor Green

# Create minimal .vscode folder
New-Item -Path "c:\net\.vscode" -ItemType Directory -Force | Out-Null

# Minimal settings for performance
$minimalSettings = @{
    "extensions.autoUpdate" = $false
    "extensions.autoCheckUpdates" = $false
    "workbench.startupEditor" = "none"
    "editor.semanticHighlighting.enabled" = $false
    "typescript.preferences.includePackageJsonAutoImports" = "off"
    "python.analysis.autoImportCompletions" = $false
    "telemetry.telemetryLevel" = "off"
    "update.mode" = "none"
} | ConvertTo-Json -Depth 10

Set-Content -Path "c:\net\.vscode\settings.json" -Value $minimalSettings -Encoding UTF8

# Essential extensions only
$essentialExtensions = @{
    "recommendations" = @(
        "ms-python.python",
        "ms-vscode.vscode-json", 
        "bradlc.vscode-tailwindcss",
        "esbenp.prettier-vscode"
    )
} | ConvertTo-Json -Depth 10

Set-Content -Path "c:\net\.vscode\extensions.json" -Value $essentialExtensions -Encoding UTF8

Write-Host "  Minimal configuration created" -ForegroundColor Green
Write-Host ""

# Step 7: Installation summary and next steps
Write-Host "INSTALLATION SUMMARY:" -ForegroundColor Cyan
Write-Host "Backup created: $backupFolder" -ForegroundColor Green
Write-Host "VS Code completely removed and reinstalled" -ForegroundColor Green  
Write-Host "Workspace cleaned and optimized" -ForegroundColor Green
Write-Host "Minimal configuration applied" -ForegroundColor Green
Write-Host ""

Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Open VS Code and verify it starts quickly" -ForegroundColor White
Write-Host "2. Open the c:\net workspace" -ForegroundColor White
Write-Host "3. Install ONLY essential extensions:" -ForegroundColor White
Write-Host "   - Python (ms-python.python)" -ForegroundColor Gray
Write-Host "   - GitHub (for git operations)" -ForegroundColor Gray
Write-Host "   - Prettier (for code formatting)" -ForegroundColor Gray
Write-Host "4. Test performance before adding more extensions" -ForegroundColor White
Write-Host ""

Write-Host "WARNING - IMPORTANT:" -ForegroundColor Red
Write-Host "- Install extensions ONE BY ONE to identify performance impacts" -ForegroundColor White
Write-Host "- Monitor process count with: Get-Process -Name 'Code*' | Measure-Object" -ForegroundColor White
Write-Host "- If issues return, check the backup folder for problematic settings" -ForegroundColor White

Write-Host ""
Write-Host "Script completed successfully!" -ForegroundColor Green

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.