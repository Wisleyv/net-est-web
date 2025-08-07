# Workspace Cleanup Script - Pre VS Code Reinstallation
# Removes outdated files, large models, debug artifacts, and redundant data

Write-Host "=== NET-EST Workspace Cleanup ===" -ForegroundColor Cyan
Write-Host "Preparing workspace for optimal VS Code performance" -ForegroundColor Yellow
Write-Host ""

# Initialize cleanup tracking
$totalSizeFreed = 0
$filesRemoved = 0
$foldersRemoved = 0

function Get-FolderSize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-ChildItem $Path -Recurse -Force -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum
        return [math]::Round($size / 1MB, 2)
    }
    return 0
}

function Remove-ItemSafe {
    param([string]$Path, [string]$Description)
    if (Test-Path $Path) {
        $sizeMB = Get-FolderSize $Path
        try {
            Remove-Item $Path -Recurse -Force -ErrorAction Stop
            Write-Host "  ✅ Removed: $Description ($sizeMB MB)" -ForegroundColor Green
            return $sizeMB
        }
        catch {
            Write-Host "  ❌ Failed to remove: $Description - $($_.Exception.Message)" -ForegroundColor Red
            return 0
        }
    }
    return 0
}

# Step 1: Analyze current workspace size
Write-Host "📊 STEP 1: Analyzing workspace size..." -ForegroundColor Green
$initialSize = Get-FolderSize "c:\net"
Write-Host "  Current workspace size: $initialSize MB" -ForegroundColor White
Write-Host ""

# Step 2: Remove large ML models and caches
Write-Host "🤖 STEP 2: Removing large ML models and caches..." -ForegroundColor Green

# Common locations for cached models
$modelCachePaths = @(
    "c:\net\backend\models\cache",
    "c:\net\backend\.cache",
    "c:\net\backend\__pycache__",
    "c:\net\backend\src\__pycache__",
    "c:\net\backend\src\*\__pycache__",
    "$env:USERPROFILE\.cache\huggingface",
    "$env:USERPROFILE\.cache\torch",
    "$env:LOCALAPPDATA\pip\cache"
)

foreach ($path in $modelCachePaths) {
    $paths = Get-ChildItem $path -ErrorAction SilentlyContinue
    foreach ($p in $paths) {
        $totalSizeFreed += Remove-ItemSafe $p.FullName "Model cache: $($p.Name)"
        $foldersRemoved++
    }
}

# Look for specific large model files
$largeModelPatterns = @(
    "c:\net\**\*bertimbau*",
    "c:\net\**\*pytorch_model.bin",
    "c:\net\**\*model.safetensors", 
    "c:\net\**\*.bin",
    "c:\net\**\*.pt",
    "c:\net\**\*.pth"
)

foreach ($pattern in $largeModelPatterns) {
    $files = Get-ChildItem $pattern -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 10MB }
    foreach ($file in $files) {
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        if ($sizeMB -gt 50) {  # Only remove files larger than 50MB
            Write-Host "  Found large model file: $($file.Name) ($sizeMB MB)" -ForegroundColor Yellow
            $confirm = Read-Host "  Remove this file? (y/N)"
            if ($confirm -eq 'y' -or $confirm -eq 'Y') {
                try {
                    Remove-Item $file.FullName -Force
                    Write-Host "  ✅ Removed: $($file.Name) ($sizeMB MB)" -ForegroundColor Green
                    $totalSizeFreed += $sizeMB
                    $filesRemoved++
                }
                catch {
                    Write-Host "  ❌ Failed to remove: $($file.Name)" -ForegroundColor Red
                }
            }
        }
    }
}

Write-Host ""

# Step 3: Clean Python caches and temp files
Write-Host "🐍 STEP 3: Cleaning Python caches and temp files..." -ForegroundColor Green

# Python cache cleanup
$pythonCachePaths = @(
    "c:\net\backend\**\__pycache__",
    "c:\net\frontend\node_modules\.cache",
    "c:\net\**\*.pyc",
    "c:\net\**\*.pyo",
    "c:\net\**\*.pyd"
)

foreach ($pattern in $pythonCachePaths) {
    $items = Get-ChildItem $pattern -Recurse -Force -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            $totalSizeFreed += Remove-ItemSafe $item.FullName "Python cache: $($item.Name)"
            $foldersRemoved++
        } else {
            $sizeMB = [math]::Round($item.Length / 1MB, 2)
            try {
                Remove-Item $item.FullName -Force
                Write-Host "  ✅ Removed: $($item.Name) ($sizeMB MB)" -ForegroundColor Green
                $totalSizeFreed += $sizeMB
                $filesRemoved++
            }
            catch {
                Write-Host "  ❌ Failed to remove: $($item.Name)" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""

# Step 4: Remove test and debug files
Write-Host "🧪 STEP 4: Removing test and debug files..." -ForegroundColor Green

$debugFiles = @(
    "c:\net\test_*.py",
    "c:\net\debug_*.py", 
    "c:\net\diagnose*.py",
    "c:\net\test_*.json",
    "c:\net\*_test.py",
    "c:\net\*.log",
    "c:\net\backend\test_*.py",
    "c:\net\backend\debug_*.py",
    "c:\net\backend\*.log",
    "c:\net\vscode_performance_log_*.txt"
)

foreach ($pattern in $debugFiles) {
    $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        Write-Host "  Found debug file: $($file.Name) ($sizeMB MB)" -ForegroundColor Yellow
        $confirm = Read-Host "  Remove this file? (y/N)"
        if ($confirm -eq 'y' -or $confirm -eq 'Y') {
            try {
                Remove-Item $file.FullName -Force
                Write-Host "  ✅ Removed: $($file.Name) ($sizeMB MB)" -ForegroundColor Green
                $totalSizeFreed += $sizeMB
                $filesRemoved++
            }
            catch {
                Write-Host "  ❌ Failed to remove: $($file.Name)" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""

# Step 5: Clean frontend build artifacts and node_modules issues
Write-Host "⚛️  STEP 5: Cleaning frontend build artifacts..." -ForegroundColor Green

$frontendCleanup = @(
    "c:\net\frontend\dist",
    "c:\net\frontend\build", 
    "c:\net\frontend\.next",
    "c:\net\frontend\.vite",
    "c:\net\frontend\node_modules\.vite",
    "c:\net\frontend\node_modules\.cache"
)

foreach ($path in $frontendCleanup) {
    $totalSizeFreed += Remove-ItemSafe $path "Frontend cache: $(Split-Path $path -Leaf)"
    $foldersRemoved++
}

# Check for oversized node_modules
$nodeModulesPath = "c:\net\frontend\node_modules"
if (Test-Path $nodeModulesPath) {
    $nodeModulesSize = Get-FolderSize $nodeModulesPath
    Write-Host "  node_modules size: $nodeModulesSize MB" -ForegroundColor White
    if ($nodeModulesSize -gt 500) {
        Write-Host "  ⚠️  node_modules is very large ($nodeModulesSize MB)" -ForegroundColor Yellow
        $confirm = Read-Host "  Remove and reinstall node_modules? (y/N)"
        if ($confirm -eq 'y' -or $confirm -eq 'Y') {
            $totalSizeFreed += Remove-ItemSafe $nodeModulesPath "node_modules"
            $foldersRemoved++
            Write-Host "  💡 Run 'npm install' in frontend folder after cleanup" -ForegroundColor Cyan
        }
    }
}

Write-Host ""

# Step 6: Remove backup and temporary files
Write-Host "🗂️  STEP 6: Removing backup and temporary files..." -ForegroundColor Green

$backupPatterns = @(
    "c:\net\**\*.backup",
    "c:\net\**\*.bak",
    "c:\net\**\*.tmp",
    "c:\net\**\*~",
    "c:\net\**\*.orig",
    "c:\net\vscode_backup_*"
)

foreach ($pattern in $backupPatterns) {
    $items = Get-ChildItem $pattern -Recurse -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            # For backup folders, ask for confirmation
            $sizeMB = Get-FolderSize $item.FullName
            if ($sizeMB -gt 1) {
                Write-Host "  Found backup folder: $($item.Name) ($sizeMB MB)" -ForegroundColor Yellow
                $confirm = Read-Host "  Remove this backup? (y/N)"
                if ($confirm -eq 'y' -or $confirm -eq 'Y') {
                    $totalSizeFreed += Remove-ItemSafe $item.FullName "Backup: $($item.Name)"
                    $foldersRemoved++
                }
            }
        } else {
            $sizeMB = [math]::Round($item.Length / 1MB, 2)
            try {
                Remove-Item $item.FullName -Force
                Write-Host "  ✅ Removed: $($item.Name) ($sizeMB MB)" -ForegroundColor Green
                $totalSizeFreed += $sizeMB
                $filesRemoved++
            }
            catch {
                Write-Host "  ❌ Failed to remove: $($item.Name)" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""

# Step 7: Final analysis and summary
Write-Host "📈 STEP 7: Cleanup summary..." -ForegroundColor Green

$finalSize = Get-FolderSize "c:\net"
$actualFreed = $initialSize - $finalSize

Write-Host "  📊 CLEANUP RESULTS:" -ForegroundColor Cyan
Write-Host "    Initial size: $initialSize MB" -ForegroundColor White
Write-Host "    Final size: $finalSize MB" -ForegroundColor White
Write-Host "    Space freed: $actualFreed MB" -ForegroundColor Green
Write-Host "    Files removed: $filesRemoved" -ForegroundColor White
Write-Host "    Folders removed: $foldersRemoved" -ForegroundColor White
Write-Host ""

if ($actualFreed -gt 100) {
    Write-Host "🎉 Excellent! Freed $actualFreed MB - this should significantly improve VS Code performance!" -ForegroundColor Green
} elseif ($actualFreed -gt 50) {
    Write-Host "✅ Good cleanup! Freed $actualFreed MB - moderate performance improvement expected." -ForegroundColor Yellow
} else {
    Write-Host "ℹ️  Workspace was already clean. Freed $actualFreed MB." -ForegroundColor White
}

Write-Host ""
Write-Host "🚀 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. The workspace is now optimized for VS Code" -ForegroundColor White
Write-Host "2. Run the VS Code clean reinstall script: .\vscode_clean_reinstall.ps1" -ForegroundColor White
Write-Host "3. If you removed node_modules, run 'npm install' in the frontend folder" -ForegroundColor White
Write-Host "4. Large model downloads will be needed when you first run the backend" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  IMPORTANT NOTES:" -ForegroundColor Red
Write-Host "- BERTimbau and other models will be re-downloaded automatically when needed" -ForegroundColor White
Write-Host "- This is normal and expected for ML applications" -ForegroundColor White
Write-Host "- The models will be cached in a cleaner, more organized way" -ForegroundColor White

Write-Host ""
Write-Host "Workspace cleanup completed! 🎉" -ForegroundColor Green

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
