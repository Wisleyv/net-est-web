# Quick Reference: Restore Development Context
# Run this script to quickly restore conversation context and development environment

Write-Host "=== NET-EST Development Context Restoration ===" -ForegroundColor Cyan
Write-Host ""

# Show key files and scripts available
Write-Host "📋 Available Scripts & Files:" -ForegroundColor Green
$keyFiles = @(
    "conversation_archive.md",
    "activate-dev-env.ps1", 
    "cache-status.ps1",
    "setup_project_environment.ps1",
    "migrate-caches.ps1",
    "workspace_cleanup.ps1",
    "vscode_clean_reinstall.ps1",
    "NET-est-optimized.code-workspace"
)

foreach ($file in $keyFiles) {
    if (Test-Path "c:\net\$file") {
        $size = (Get-Item "c:\net\$file").Length
        Write-Host "  ✅ $file ($([math]::Round($size/1KB, 1)) KB)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (missing)" -ForegroundColor Red
    }
}

Write-Host ""

# Show current environment status
Write-Host "🔧 Current Environment Status:" -ForegroundColor Green

if (Test-Path "c:\net\backend\venv\Scripts\python.exe") {
    Write-Host "  ✅ Python venv: Available" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python venv: Missing" -ForegroundColor Red
}

if (Test-Path "c:\net\frontend\node_modules") {
    Write-Host "  ✅ Node modules: Available" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Node modules: Missing (run: npm install)" -ForegroundColor Yellow
}

# Check VS Code status
$vscodeProcesses = Get-Process -Name "Code*" -ErrorAction SilentlyContinue
if ($vscodeProcesses) {
    Write-Host "  ✅ VS Code: Running ($($vscodeProcesses.Count) processes)" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  VS Code: Not running" -ForegroundColor White
}

Write-Host ""

# Quick start commands
Write-Host "🚀 Quick Start Commands:" -ForegroundColor Yellow
Write-Host "  Read full context: Get-Content 'conversation_archive.md' | more" -ForegroundColor White
Write-Host "  Activate environment: .\activate-dev-env.ps1" -ForegroundColor White
Write-Host "  Check caches: .\cache-status.ps1" -ForegroundColor White
Write-Host "  Open optimized workspace: code NET-est-optimized.code-workspace" -ForegroundColor White
Write-Host ""

# Show recent session summary
Write-Host "📊 Recent Session Summary:" -ForegroundColor Cyan
Write-Host "  • Workspace optimized: 164.22 MB freed" -ForegroundColor Green
Write-Host "  • Project-centric caching configured" -ForegroundColor Green
Write-Host "  • VS Code workspace optimized" -ForegroundColor Green
Write-Host "  • Ready for VS Code clean reinstallation" -ForegroundColor Yellow
Write-Host ""

Write-Host "💡 For full conversation history, see: conversation_archive.md" -ForegroundColor Green

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
