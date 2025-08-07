# Cache Migration Script - Move system caches to project-local locations
# Improves performance by consolidating dependencies under c:\net

Write-Host "=== NET-EST Cache Migration ===" -ForegroundColor Cyan
Write-Host "Moving system caches to project-local locations" -ForegroundColor Yellow
Write-Host ""

# Ensure project directories exist
. "c:\net\setup_project_environment.ps1"
Write-Host ""

# Step 1: Analyze current cache sizes
Write-Host "📊 STEP 1: Analyzing current cache sizes..." -ForegroundColor Green

$migrations = @(
    @{
        Name = "PIP Cache"
        Source = "$env:LOCALAPPDATA\pip\cache"
        Target = "c:\net\.pip-cache"
        EnvVar = "PIP_CACHE_DIR"
    },
    @{
        Name = "HuggingFace Cache"  
        Source = "$env:USERPROFILE\.cache\huggingface"
        Target = "c:\net\.huggingface-cache"
        EnvVar = "HUGGINGFACE_HUB_CACHE"
    },
    @{
        Name = "Torch Cache"
        Source = "$env:USERPROFILE\.cache\torch" 
        Target = "c:\net\.models\torch"
        EnvVar = "TORCH_HOME"
    }
)

$totalSizeMB = 0
foreach ($migration in $migrations) {
    if (Test-Path $migration.Source) {
        $sizeMB = (Get-ChildItem $migration.Source -Recurse -Force -ErrorAction SilentlyContinue | 
                  Measure-Object -Property Length -Sum).Sum / 1MB
        $migration.SizeMB = [math]::Round($sizeMB, 2)
        $totalSizeMB += $sizeMB
        Write-Host "  $($migration.Name): $($migration.SizeMB) MB" -ForegroundColor White
    } else {
        $migration.SizeMB = 0
        Write-Host "  $($migration.Name): Not found" -ForegroundColor Gray
    }
}

Write-Host "  📊 Total cache size: $([math]::Round($totalSizeMB, 2)) MB" -ForegroundColor Cyan
Write-Host ""

if ($totalSizeMB -eq 0) {
    Write-Host "ℹ️  No caches found to migrate. Environment is ready!" -ForegroundColor Green
    exit 0
}

# Step 2: Confirm migration
Write-Host "🚚 STEP 2: Migration confirmation..." -ForegroundColor Green
Write-Host "  This will move $([math]::Round($totalSizeMB, 2)) MB of cache data to project-local locations." -ForegroundColor White
Write-Host "  Benefits:" -ForegroundColor Yellow
Write-Host "    - Faster model loading (shorter paths)" -ForegroundColor Green
Write-Host "    - Better VS Code performance" -ForegroundColor Green
Write-Host "    - Easier project portability" -ForegroundColor Green
Write-Host "    - Cleaner system cache locations" -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "  Proceed with cache migration? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "❌ Migration cancelled." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Perform migrations
Write-Host "🔄 STEP 3: Performing cache migrations..." -ForegroundColor Green

foreach ($migration in $migrations) {
    if ($migration.SizeMB -gt 0) {
        Write-Host "  📦 Migrating $($migration.Name)..." -ForegroundColor Yellow
        Write-Host "    From: $($migration.Source)" -ForegroundColor Gray
        Write-Host "    To: $($migration.Target)" -ForegroundColor Gray
        
        try {
            # Create target directory if it doesn't exist
            if (!(Test-Path $migration.Target)) {
                New-Item -ItemType Directory -Path $migration.Target -Force | Out-Null
            }
            
            # Copy cache contents
            $sourceItems = Get-ChildItem $migration.Source -Force -ErrorAction SilentlyContinue
            if ($sourceItems) {
                foreach ($item in $sourceItems) {
                    $targetPath = Join-Path $migration.Target $item.Name
                    if ($item.PSIsContainer) {
                        Copy-Item $item.FullName $targetPath -Recurse -Force -ErrorAction SilentlyContinue
                    } else {
                        Copy-Item $item.FullName $targetPath -Force -ErrorAction SilentlyContinue
                    }
                }
                Write-Host "    ✅ Copied $($migration.SizeMB) MB" -ForegroundColor Green
                
                # Verify copy was successful
                $targetSize = (Get-ChildItem $migration.Target -Recurse -Force -ErrorAction SilentlyContinue | 
                              Measure-Object -Property Length -Sum).Sum / 1MB
                $targetSizeMB = [math]::Round($targetSize, 2)
                
                if ($targetSizeMB -ge ($migration.SizeMB * 0.95)) {  # 95% threshold for success
                    # Remove original cache (with confirmation for large caches)
                    if ($migration.SizeMB -gt 500) {
                        $confirmDelete = Read-Host "    Remove original cache ($($migration.SizeMB) MB)? (y/N)"
                        if ($confirmDelete -eq 'y' -or $confirmDelete -eq 'Y') {
                            Remove-Item $migration.Source -Recurse -Force -ErrorAction SilentlyContinue
                            Write-Host "    ✅ Original cache removed" -ForegroundColor Green
                        } else {
                            Write-Host "    ℹ️  Original cache preserved" -ForegroundColor Yellow
                        }
                    } else {
                        Remove-Item $migration.Source -Recurse -Force -ErrorAction SilentlyContinue
                        Write-Host "    ✅ Original cache removed" -ForegroundColor Green
                    }
                } else {
                    Write-Host "    ⚠️  Copy verification failed - original cache preserved" -ForegroundColor Yellow
                }
            } else {
                Write-Host "    ℹ️  Cache was empty" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "    ❌ Migration failed: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        Write-Host ""
    }
}

# Step 4: Update environment configuration
Write-Host "🔧 STEP 4: Updating environment configuration..." -ForegroundColor Green

# Load and apply project environment
. "c:\net\.env-configs\project-environment.ps1"

# Verify environment variables are set
$envVerification = @{
    "PIP_CACHE_DIR" = $env:PIP_CACHE_DIR
    "HUGGINGFACE_HUB_CACHE" = $env:HUGGINGFACE_HUB_CACHE  
    "TORCH_HOME" = $env:TORCH_HOME
}

foreach ($envVar in $envVerification.GetEnumerator()) {
    if ($envVar.Value) {
        Write-Host "  ✅ $($envVar.Key): $($envVar.Value)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($envVar.Key): Not set" -ForegroundColor Red
    }
}

Write-Host ""

# Step 5: Create convenience scripts
Write-Host "🛠️  STEP 5: Creating convenience scripts..." -ForegroundColor Green

# Quick cache status script
$cacheStatusScript = @"
Write-Host "=== NET-EST Cache Status ===" -ForegroundColor Cyan
Write-Host ""

`$caches = @{
    "PIP Cache" = "c:\net\.pip-cache"
    "HuggingFace Cache" = "c:\net\.huggingface-cache"
    "Torch Cache" = "c:\net\.models\torch"
    "Python Cache" = "c:\net\.python-cache"
}

foreach (`$cache in `$caches.GetEnumerator()) {
    if (Test-Path `$cache.Value) {
        `$size = (Get-ChildItem `$cache.Value -Recurse -Force -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "`$(`$cache.Key): `$([math]::Round(`$size, 2)) MB" -ForegroundColor Green
    } else {
        Write-Host "`$(`$cache.Key): Empty" -ForegroundColor Gray
    }
}
"@

$cacheStatusScript | Out-File -FilePath "c:\net\cache-status.ps1" -Encoding UTF8
Write-Host "  ✅ Created: c:\net\cache-status.ps1" -ForegroundColor Green

Write-Host ""

# Step 6: Final verification and summary
Write-Host "✅ STEP 6: Migration summary..." -ForegroundColor Green

$finalSize = 0
foreach ($migration in $migrations) {
    if (Test-Path $migration.Target) {
        $size = (Get-ChildItem $migration.Target -Recurse -Force -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1MB
        $finalSize += $size
        Write-Host "  $($migration.Name): $([math]::Round($size, 2)) MB at $($migration.Target)" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "📊 MIGRATION RESULTS:" -ForegroundColor Cyan
Write-Host "  Original cache size: $([math]::Round($totalSizeMB, 2)) MB" -ForegroundColor White
Write-Host "  Migrated cache size: $([math]::Round($finalSize, 2)) MB" -ForegroundColor White
Write-Host "  Migration efficiency: $([math]::Round(($finalSize / $totalSizeMB) * 100, 1))%" -ForegroundColor Green
Write-Host ""

Write-Host "🎯 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Test environment: .\activate-dev-env.ps1" -ForegroundColor White
Write-Host "2. Check cache status: .\cache-status.ps1" -ForegroundColor White  
Write-Host "3. Start backend to verify model loading works" -ForegroundColor White
Write-Host "4. Proceed with VS Code reinstallation" -ForegroundColor White
Write-Host ""

Write-Host "Cache migration completed! 🎉" -ForegroundColor Green

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
