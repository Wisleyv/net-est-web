# VS Code Process Optimization Script
# Addresses the 15 VS Code processes issue identified in monitoring

Write-Host "=== VS Code Optimization Tool ===" -ForegroundColor Cyan
Write-Host "Analyzing VS Code processes and performance..." -ForegroundColor Yellow
Write-Host ""

# Get current VS Code processes
$vscodeProcesses = Get-Process -Name "Code*" -ErrorAction SilentlyContinue | Sort-Object WorkingSet64 -Descending
$totalMemoryMB = ($vscodeProcesses | Measure-Object WorkingSet64 -Sum).Sum / 1MB

Write-Host "CURRENT VS CODE STATUS:" -ForegroundColor Yellow
Write-Host "  Total Processes: $($vscodeProcesses.Count)" -ForegroundColor $(if ($vscodeProcesses.Count -gt 10) { "Red" } elseif ($vscodeProcesses.Count -gt 8) { "Yellow" } else { "Green" })
Write-Host "  Total Memory Usage: $([math]::Round($totalMemoryMB, 0)) MB" -ForegroundColor $(if ($totalMemoryMB -gt 3000) { "Red" } elseif ($totalMemoryMB -gt 2000) { "Yellow" } else { "Green" })
Write-Host ""

if ($vscodeProcesses.Count -gt 0) {
    Write-Host "TOP MEMORY CONSUMING VS CODE PROCESSES:" -ForegroundColor Yellow
    $vscodeProcesses | Select-Object -First 5 | ForEach-Object {
        $memMB = [math]::Round($_.WorkingSet64 / 1MB, 2)
        Write-Host "  PID $($_.Id): $memMB MB" -ForegroundColor White
    }
    Write-Host ""
}

# Performance recommendations
Write-Host "RECOMMENDATIONS:" -ForegroundColor Green

if ($vscodeProcesses.Count -gt 10) {
    Write-Host "🔴 CRITICAL: Too many VS Code processes ($($vscodeProcesses.Count))" -ForegroundColor Red
    Write-Host "   Recommended actions:" -ForegroundColor White
    Write-Host "   1. Close VS Code completely and restart" -ForegroundColor White
    Write-Host "   2. Disable unnecessary extensions" -ForegroundColor White
    Write-Host "   3. Check for extension memory leaks" -ForegroundColor White
    Write-Host ""
    
    $userChoice = Read-Host "Would you like to close all VS Code processes now? (y/N)"
    if ($userChoice -eq 'y' -or $userChoice -eq 'Y') {
        Write-Host "Closing all VS Code processes..." -ForegroundColor Yellow
        $vscodeProcesses | ForEach-Object {
            try {
                Stop-Process -Id $_.Id -Force
                Write-Host "  Closed PID $($_.Id)" -ForegroundColor Green
            }
            catch {
                Write-Host "  Failed to close PID $($_.Id): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        Write-Host "All VS Code processes closed. You can now restart VS Code." -ForegroundColor Green
    }
    else {
        Write-Host "VS Code processes left running. Consider restarting when convenient." -ForegroundColor Yellow
    }
}
elseif ($totalMemoryMB -gt 3000) {
    Write-Host "🟡 WARNING: High memory usage ($([math]::Round($totalMemoryMB, 0)) MB)" -ForegroundColor Yellow
    Write-Host "   Recommended actions:" -ForegroundColor White
    Write-Host "   1. Close large files or unused workspaces" -ForegroundColor White
    Write-Host "   2. Review extension memory usage" -ForegroundColor White
    Write-Host "   3. Consider restarting VS Code" -ForegroundColor White
}
else {
    Write-Host "✅ VS Code performance looks good!" -ForegroundColor Green
    Write-Host "   Process count: $($vscodeProcesses.Count) (normal range: 6-8)" -ForegroundColor White
    Write-Host "   Memory usage: $([math]::Round($totalMemoryMB, 0)) MB (acceptable under 2GB)" -ForegroundColor White
}

Write-Host ""

# Additional system recommendations
Write-Host "ADDITIONAL SYSTEM OPTIMIZATIONS:" -ForegroundColor Cyan

# Check for running system services that might affect performance
$troubleServices = @(
    @{Name="BITS"; DisplayName="Background Intelligent Transfer Service"},
    @{Name="WSearch"; DisplayName="Windows Search"},
    @{Name="SysMain"; DisplayName="Superfetch/SysMain"},
    @{Name="TrustedInstaller"; DisplayName="Windows Modules Installer"}
)

foreach ($service in $troubleServices) {
    $svc = Get-Service -Name $service.Name -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -eq 'Running') {
        Write-Host "⚠️  $($service.DisplayName) is running - may impact performance" -ForegroundColor Yellow
    }
}

# Memory pressure check
$memory = Get-CimInstance -ClassName Win32_OperatingSystem
$memoryUsedPercent = [math]::Round(($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize * 100, 2)

if ($memoryUsedPercent -gt 85) {
    Write-Host "🔴 CRITICAL: System memory usage is $memoryUsedPercent%" -ForegroundColor Red
    Write-Host "   Consider closing applications or adding more RAM" -ForegroundColor White
}
elseif ($memoryUsedPercent -gt 75) {
    Write-Host "🟡 WARNING: System memory usage is $memoryUsedPercent%" -ForegroundColor Yellow
    Write-Host "   Monitor for performance impact" -ForegroundColor White
}

Write-Host ""
Write-Host "Run this script periodically to monitor VS Code performance." -ForegroundColor Gray

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
*/
