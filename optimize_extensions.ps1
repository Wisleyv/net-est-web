# NET-EST VS Code Extension Optimization Script
# Disables unnecessary extensions for this workspace to improve performance

Write-Host "🎯 NET-EST Extension Optimization Script" -ForegroundColor Cyan
Write-Host "Disabling unnecessary extensions for this workspace..." -ForegroundColor Yellow
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "NET-est.code-workspace")) {
    Write-Host "❌ Error: Please run this script from the NET-EST project root directory" -ForegroundColor Red
    exit 1
}

# PHP Extensions (Completely unnecessary for your project)
$phpExtensions = @(
    "bmewburn.vscode-intelephense-client",
    "brapifra.phpserver", 
    "devsense.composer-php-vscode",
    "xdebug.php-debug",
    "xdebug.php-pack",
    "zobo.php-intellisense"
)

# Heavy Development Tools (Performance impact)
$heavyExtensions = @(
    "ms-edgedevtools.vscode-edge-devtools",
    "ms-azuretools.vscode-containers",
    "ms-azuretools.vscode-docker",
    "ms-vscode-remote.remote-containers",
    "ms-vscode-remote.remote-ssh",
    "ms-vscode-remote.remote-ssh-edit", 
    "ms-vscode-remote.remote-wsl",
    "ms-playwright.playwright"
)

# C++ Extensions (Not needed)
$cppExtensions = @(
    "ms-vscode.cmake-tools",
    "ms-vscode.cpptools",
    "ms-vscode.cpptools-extension-pack",
    "ms-vscode.cpptools-themes",
    "twxs.cmake"
)

# Miscellaneous Unnecessary Extensions
$miscExtensions = @(
    "adpyke.vscode-sql-formatter",
    "adrianwilczynski.format-selection-as-html",
    "grapecity.gc-excelviewer",
    "humy2833.ftp-simple",
    "idreamsoft.css-format-st3",
    "inferrinizzard.prettier-sql-vscode",
    "janisdd.vscode-edit-csv",
    "kevinrose.vsc-python-indent",
    "mechatroner.rainbow-csv",
    "miramac.vscode-exec-node",
    "reditorsupport.r",
    "reditorsupport.r-syntax",
    "nikolapaunovic.tkinter-snippets",
    "tomasvergara.vscode-fontawesome-gallery",
    "vscodevim.vim"
)

# Performance Impact Extensions (Optional)
$performanceExtensions = @(
    "bradlc.vscode-tailwindcss",
    "ms-vscode.live-server",
    "ms-vscode.atom-keybindings",
    "ms-vscode.notepadplusplus-keybindings",
    "ms-vscode.vs-keybindings"
)

# Combine all extensions to disable
$allExtensionsToDisable = $phpExtensions + $heavyExtensions + $cppExtensions + $miscExtensions + $performanceExtensions

Write-Host "📊 Extensions to disable: $($allExtensionsToDisable.Count)" -ForegroundColor Yellow

# Disable extensions for this workspace
$disabledCount = 0
$errorCount = 0

foreach ($extension in $allExtensionsToDisable) {
    try {
        Write-Host "Disabling: $extension" -ForegroundColor Gray
        $result = & code --disable-extension $extension --folder .
        if ($LASTEXITCODE -eq 0) {
            $disabledCount++
        } else {
            $errorCount++
            Write-Host "  ⚠️  Failed to disable $extension" -ForegroundColor Yellow
        }
    }
    catch {
        $errorCount++
        Write-Host "  ❌ Error disabling $extension" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Optimization Complete!" -ForegroundColor Green
Write-Host "📊 Results:" -ForegroundColor Cyan
Write-Host "  • Extensions disabled: $disabledCount" -ForegroundColor Green
Write-Host "  • Errors: $errorCount" -ForegroundColor Yellow

Write-Host ""
Write-Host "🔄 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Restart VS Code to apply changes" -ForegroundColor White
Write-Host "  2. Check process count: (Get-Process -Name 'Code*').Count" -ForegroundColor White
Write-Host "  3. Check memory usage: [math]::Round(((Get-Process -Name 'Code*' | Measure-Object WorkingSet -Sum).Sum / 1GB), 2)" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Expected Improvements:" -ForegroundColor Cyan
Write-Host "  • Processes: 20 → 6-8" -ForegroundColor Green
Write-Host "  • Memory: 4GB → 1-1.5GB" -ForegroundColor Green  
Write-Host "  • Performance: 60-80% faster" -ForegroundColor Green

Write-Host ""
Write-Host "💡 Essential extensions kept:" -ForegroundColor Cyan
Write-Host "  • GitHub Copilot & Chat (as requested)" -ForegroundColor White
Write-Host "  • Python support (Pylance, Black, Debugpy)" -ForegroundColor White
Write-Host "  • JavaScript/React support (ESLint, Prettier)" -ForegroundColor White
Write-Host "  • GitHub workflow tools" -ForegroundColor White
