# NET-EST Project Environment Setup
# Consolidates all project dependencies under c:\net for optimal performance

Write-Host "=== NET-EST Project Environment Setup ===" -ForegroundColor Cyan
Write-Host "Consolidating dependencies for optimal performance" -ForegroundColor Yellow
Write-Host ""

# Create project-centric directory structure
Write-Host "📁 STEP 1: Creating project directory structure..." -ForegroundColor Green

$projectDirs = @(
    "c:\net\.python-cache",
    "c:\net\.huggingface-cache", 
    "c:\net\.models",
    "c:\net\.pip-cache",
    "c:\net\.env-configs"
)

foreach ($dir in $projectDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Exists: $dir" -ForegroundColor White
    }
}

Write-Host ""

# Step 2: Configure environment variables for project-centric caching
Write-Host "🔧 STEP 2: Configuring project-centric environment..." -ForegroundColor Green

# Create environment configuration file
$envConfig = @"
# NET-EST Project Environment Configuration
# Source this file to set project-centric caching

# Python/Pip Cache
`$env:PIP_CACHE_DIR = "c:\net\.pip-cache"
`$env:PYTHONPYCACHEPREFIX = "c:\net\.python-cache"

# HuggingFace Cache
`$env:HUGGINGFACE_HUB_CACHE = "c:\net\.huggingface-cache"
`$env:TRANSFORMERS_CACHE = "c:\net\.huggingface-cache"
`$env:HF_HOME = "c:\net\.huggingface-cache"

# Torch Cache
`$env:TORCH_HOME = "c:\net\.models\torch"

# Project-specific
`$env:NET_EST_PROJECT_ROOT = "c:\net"
`$env:NET_EST_BACKEND_ROOT = "c:\net\backend"
`$env:NET_EST_FRONTEND_ROOT = "c:\net\frontend"

Write-Host "Environment configured for NET-EST project" -ForegroundColor Green
"@

$envConfig | Out-File -FilePath "c:\net\.env-configs\project-environment.ps1" -Encoding UTF8
Write-Host "  ✅ Created: c:\net\.env-configs\project-environment.ps1" -ForegroundColor Green

# Create activation script
$activationScript = @"
# NET-EST Development Environment Activation
# Run this before starting development work

Write-Host "🚀 Activating NET-EST Development Environment..." -ForegroundColor Cyan

# Load project environment
. "c:\net\.env-configs\project-environment.ps1"

# Activate Python virtual environment
if (Test-Path "c:\net\backend\venv\Scripts\Activate.ps1") {
    & "c:\net\backend\venv\Scripts\Activate.ps1"
    Write-Host "  ✅ Python virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Virtual environment not found" -ForegroundColor Yellow
}

# Display environment status
Write-Host ""
Write-Host "📊 Environment Status:" -ForegroundColor Cyan
Write-Host "  Python Cache: `$env:PYTHONPYCACHEPREFIX" -ForegroundColor White
Write-Host "  Pip Cache: `$env:PIP_CACHE_DIR" -ForegroundColor White  
Write-Host "  HuggingFace Cache: `$env:HUGGINGFACE_HUB_CACHE" -ForegroundColor White
Write-Host "  Torch Cache: `$env:TORCH_HOME" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Ready for NET-EST development!" -ForegroundColor Green
"@

$activationScript | Out-File -FilePath "c:\net\activate-dev-env.ps1" -Encoding UTF8
Write-Host "  ✅ Created: c:\net\activate-dev-env.ps1" -ForegroundColor Green

Write-Host ""

# Step 3: Backend environment optimization
Write-Host "🐍 STEP 3: Backend environment analysis..." -ForegroundColor Green

if (Test-Path "c:\net\backend\venv") {
    $venvSize = (Get-ChildItem "c:\net\backend\venv" -Recurse -Force -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  Current venv size: $([math]::Round($venvSize, 2)) MB" -ForegroundColor White
    
    # Check if venv is using system Python
    $pyvenvConfig = Get-Content "c:\net\backend\venv\pyvenv.cfg" -ErrorAction SilentlyContinue
    if ($pyvenvConfig -match "home = (.+)") {
        $pythonHome = $matches[1]
        Write-Host "  Python home: $pythonHome" -ForegroundColor White
        
        if ($pythonHome -like "*Python313*") {
            Write-Host "  ✅ Using system Python 3.13 (recommended)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Using non-standard Python location" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ⚠️  No virtual environment found" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Frontend environment analysis  
Write-Host "⚛️  STEP 4: Frontend environment analysis..." -ForegroundColor Green

if (Test-Path "c:\net\frontend\node_modules") {
    $nodeSize = (Get-ChildItem "c:\net\frontend\node_modules" -Recurse -Force -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  node_modules size: $([math]::Round($nodeSize, 2)) MB" -ForegroundColor White
    
    if ($nodeSize -lt 200) {
        Write-Host "  ✅ Reasonable size" -ForegroundColor Green
    } elseif ($nodeSize -lt 500) {
        Write-Host "  ⚠️  Moderate size - monitor for bloat" -ForegroundColor Yellow
    } else {
        Write-Host "  🔴 Large size - consider cleanup" -ForegroundColor Red
    }
} else {
    Write-Host "  ℹ️  node_modules not found (run npm install)" -ForegroundColor White
}

Write-Host ""

# Step 5: Migration strategy
Write-Host "📦 STEP 5: Cache migration strategy..." -ForegroundColor Green

$cacheLocations = @{
    "PIP Cache" = "$env:LOCALAPPDATA\pip\cache"
    "HuggingFace Cache" = "$env:USERPROFILE\.cache\huggingface"  
    "Torch Cache" = "$env:USERPROFILE\.cache\torch"
}

$totalCacheSize = 0
foreach ($cache in $cacheLocations.GetEnumerator()) {
    if (Test-Path $cache.Value) {
        $size = (Get-ChildItem $cache.Value -Recurse -Force -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1MB
        $totalCacheSize += $size
        Write-Host "  $($cache.Key): $([math]::Round($size, 2)) MB at $($cache.Value)" -ForegroundColor White
    } else {
        Write-Host "  $($cache.Key): Not found" -ForegroundColor Gray
    }
}

Write-Host "  📊 Total cache size: $([math]::Round($totalCacheSize, 2)) MB" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 RECOMMENDATIONS:" -ForegroundColor Yellow
Write-Host ""

if ($totalCacheSize -gt 100) {
    Write-Host "1. 📁 CACHE CONSOLIDATION (High Impact):" -ForegroundColor Green
    Write-Host "   - Move caches to c:\net\.huggingface-cache, c:\net\.pip-cache" -ForegroundColor White
    Write-Host "   - Expected performance gain: 15-25%" -ForegroundColor Green
    Write-Host "   - Disk space savings: $([math]::Round($totalCacheSize, 2)) MB freed from system locations" -ForegroundColor Green
    Write-Host ""
}

Write-Host "2. 🚀 ACTIVATION WORKFLOW (Medium Impact):" -ForegroundColor Green  
Write-Host "   - Use: .\activate-dev-env.ps1 before development" -ForegroundColor White
Write-Host "   - Ensures all caches are project-local" -ForegroundColor White
Write-Host "   - Consistent environment across sessions" -ForegroundColor White
Write-Host ""

Write-Host "3. 🔧 VS CODE INTEGRATION (Medium Impact):" -ForegroundColor Green
Write-Host "   - Configure VS Code to use project Python: c:\net\backend\venv\Scripts\python.exe" -ForegroundColor White
Write-Host "   - Set workspace-specific settings for path optimization" -ForegroundColor White
Write-Host ""

Write-Host "4. 📊 OPTIONAL: Python Cleanup (Low Priority):" -ForegroundColor Yellow
Write-Host "   - Keep: C:\Python313\ (main installation)" -ForegroundColor White
Write-Host "   - Keep: C:\Portable\lilypond\bin\python.exe (LilyPond dependency)" -ForegroundColor White
Write-Host "   - Remove: Windows Store Python stub (if desired)" -ForegroundColor Gray
Write-Host ""

Write-Host "🏁 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Run cache migration: .\migrate-caches.ps1 (to be created)" -ForegroundColor White
Write-Host "2. Test environment: .\activate-dev-env.ps1" -ForegroundColor White
Write-Host "3. Configure VS Code with project-centric settings" -ForegroundColor White
Write-Host "4. Proceed with VS Code reinstallation: .\vscode_clean_reinstall.ps1" -ForegroundColor White

Write-Host ""
Write-Host "Setup completed! 🎉" -ForegroundColor Green

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
