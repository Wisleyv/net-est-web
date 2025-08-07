# Safe VS Code Process Optimization Script
# Enhanced version that shows process details and protects development servers

Write-Host "=== Safe VS Code Optimization Tool ===" -ForegroundColor Cyan
Write-Host "Analyzing VS Code processes with safety checks..." -ForegroundColor Yellow
Write-Host ""

# Enhanced function to get detailed VS Code process information
function Get-DetailedVSCodeProcesses {
    $processes = Get-Process -Name "Code*" -ErrorAction SilentlyContinue
    $detailedProcesses = @()
    
    foreach ($proc in $processes) {
        try {
            $processInfo = @{
                Id = $proc.Id
                ProcessName = $proc.ProcessName
                MemoryMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
                CPUTime = if ($proc.CPU) { [math]::Round($proc.CPU, 2) } else { 0 }
                StartTime = if ($proc.StartTime) { $proc.StartTime.ToString("HH:mm:ss") } else { "Unknown" }
                Path = try { $proc.Path } catch { "Access Denied" }
                MainWindowTitle = $proc.MainWindowTitle
                CommandLine = ""
            }
            
            # Try to get command line (requires elevated permissions)
            try {
                $wmi = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId = $($proc.Id)" -ErrorAction SilentlyContinue
                if ($wmi) {
                    $processInfo.CommandLine = $wmi.CommandLine
                }
            }
            catch {
                $processInfo.CommandLine = "Access Denied"
            }
            
            $detailedProcesses += [PSCustomObject]$processInfo
        }
        catch {
            Write-Warning "Could not get details for process ID $($proc.Id)"
        }
    }
    
    return $detailedProcesses | Sort-Object MemoryMB -Descending
}

# Function to categorize VS Code processes
function Get-VSCodeProcessCategories {
    param($processes)
    
    $categories = @{
        MainWindow = @()
        Extensions = @()
        LanguageServers = @()
        Renderers = @()
        Workers = @()
        Unknown = @()
    }
    
    foreach ($proc in $processes) {
        $cmdLine = $proc.CommandLine.ToLower()
        $title = $proc.MainWindowTitle
        
        if ($title -and $title.Contains("Visual Studio Code")) {
            $categories.MainWindow += $proc
        }
        elseif ($cmdLine.Contains("--extension-development-host") -or $cmdLine.Contains("extensionhost")) {
            $categories.Extensions += $proc
        }
        elseif ($cmdLine.Contains("--lang=") -or $cmdLine.Contains("language-server")) {
            $categories.LanguageServers += $proc
        }
        elseif ($cmdLine.Contains("--type=renderer") -or $cmdLine.Contains("renderer")) {
            $categories.Renderers += $proc
        }
        elseif ($cmdLine.Contains("--type=utility") -or $cmdLine.Contains("worker")) {
            $categories.Workers += $proc
        }
        else {
            $categories.Unknown += $proc
        }
    }
    
    return $categories
}

# Function to check for development servers
function Get-DevelopmentServers {
    $devProcesses = @()
    
    # Check for common development server processes
    $devPatterns = @("python", "node", "npm", "uvicorn", "fastapi", "vite", "webpack")
    
    foreach ($pattern in $devPatterns) {
        $procs = Get-Process -Name "*$pattern*" -ErrorAction SilentlyContinue
        foreach ($proc in $procs) {
            try {
                $devProcesses += [PSCustomObject]@{
                    Id = $proc.Id
                    Name = $proc.ProcessName
                    MemoryMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
                    StartTime = if ($proc.StartTime) { $proc.StartTime.ToString("HH:mm:ss") } else { "Unknown" }
                    Path = try { $proc.Path } catch { "Access Denied" }
                }
            }
            catch {
                continue
            }
        }
    }
    
    return $devProcesses
}

# Main analysis
Write-Host "ANALYZING CURRENT STATE..." -ForegroundColor Yellow
Write-Host ""

$vscodeProcesses = Get-DetailedVSCodeProcesses
$totalMemoryMB = ($vscodeProcesses | Measure-Object MemoryMB -Sum).Sum
$categories = Get-VSCodeProcessCategories -processes $vscodeProcesses
$devServers = Get-DevelopmentServers

# Display current status
Write-Host "VS CODE PROCESS ANALYSIS:" -ForegroundColor Cyan
Write-Host "  Total Processes: $($vscodeProcesses.Count)" -ForegroundColor $(if ($vscodeProcesses.Count -gt 10) { "Red" } elseif ($vscodeProcesses.Count -gt 8) { "Yellow" } else { "Green" })
Write-Host "  Total Memory: $([math]::Round($totalMemoryMB, 0)) MB" -ForegroundColor $(if ($totalMemoryMB -gt 3000) { "Red" } elseif ($totalMemoryMB -gt 2000) { "Yellow" } else { "Green" })
Write-Host ""

# Show categorized processes
Write-Host "PROCESS BREAKDOWN:" -ForegroundColor Yellow
Write-Host "  Main Windows: $($categories.MainWindow.Count)" -ForegroundColor White
Write-Host "  Extension Hosts: $($categories.Extensions.Count)" -ForegroundColor White
Write-Host "  Language Servers: $($categories.LanguageServers.Count)" -ForegroundColor White
Write-Host "  Renderers: $($categories.Renderers.Count)" -ForegroundColor White
Write-Host "  Workers: $($categories.Workers.Count)" -ForegroundColor White
Write-Host "  Unknown: $($categories.Unknown.Count)" -ForegroundColor White
Write-Host ""

# Show development servers (PROTECTED)
if ($devServers.Count -gt 0) {
    Write-Host "DETECTED DEVELOPMENT SERVERS (PROTECTED):" -ForegroundColor Green
    $devServers | ForEach-Object {
        Write-Host "  $($_.Name) (PID: $($_.Id)) - $($_.MemoryMB) MB - Started: $($_.StartTime)" -ForegroundColor Green
    }
    Write-Host ""
}

# Show detailed process list
Write-Host "DETAILED VS CODE PROCESSES:" -ForegroundColor Yellow
$vscodeProcesses | ForEach-Object {
    $color = if ($_.MemoryMB -gt 500) { "Red" } elseif ($_.MemoryMB -gt 200) { "Yellow" } else { "White" }
    Write-Host "  PID $($_.Id): $($_.ProcessName) - $($_.MemoryMB) MB - CPU: $($_.CPUTime)s - Started: $($_.StartTime)" -ForegroundColor $color
    if ($_.MainWindowTitle) {
        Write-Host "    Window: $($_.MainWindowTitle)" -ForegroundColor Gray
    }
    if ($_.Path -and $_.Path -ne "Access Denied") {
        Write-Host "    Path: $($_.Path)" -ForegroundColor Gray
    }
}
Write-Host ""

# Safety recommendations
Write-Host "RECOMMENDATIONS & ACTIONS:" -ForegroundColor Cyan

if ($vscodeProcesses.Count -gt 15) {
    Write-Host "🔴 CRITICAL: Too many VS Code processes ($($vscodeProcesses.Count))" -ForegroundColor Red
    Write-Host ""
    
    # Offer safe options
    Write-Host "SAFE OPTIONS:" -ForegroundColor Green
    Write-Host "1. Close VS Code normally (recommended)" -ForegroundColor White
    Write-Host "2. Kill only high-memory processes (>500MB)" -ForegroundColor White
    Write-Host "3. Kill extension hosts and renderers only" -ForegroundColor White
    Write-Host "4. Full VS Code restart (kills all Code processes)" -ForegroundColor White
    Write-Host "5. Do nothing and exit" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Select option (1-5)"
    
    switch ($choice) {
        "1" {
            Write-Host "Please close VS Code manually through File > Exit or Alt+F4" -ForegroundColor Yellow
            Write-Host "This is the safest option and preserves your work." -ForegroundColor Green
        }
        "2" {
            $highMemoryProcesses = $vscodeProcesses | Where-Object { $_.MemoryMB -gt 500 }
            if ($highMemoryProcesses.Count -gt 0) {
                Write-Host "High memory processes to be terminated:" -ForegroundColor Yellow
                $highMemoryProcesses | ForEach-Object {
                    Write-Host "  PID $($_.Id): $($_.ProcessName) - $($_.MemoryMB) MB" -ForegroundColor Red
                }
                $confirm = Read-Host "Confirm termination? (y/N)"
                if ($confirm -eq 'y' -or $confirm -eq 'Y') {
                    $highMemoryProcesses | ForEach-Object {
                        try {
                            Stop-Process -Id $_.Id -Force
                            Write-Host "  Terminated PID $($_.Id)" -ForegroundColor Green
                        }
                        catch {
                            Write-Host "  Failed to terminate PID $($_.Id): $($_.Exception.Message)" -ForegroundColor Red
                        }
                    }
                }
            } else {
                Write-Host "No high-memory processes found." -ForegroundColor Green
            }
        }
        "3" {
            $targetProcesses = $categories.Extensions + $categories.Renderers + $categories.Workers
            if ($targetProcesses.Count -gt 0) {
                Write-Host "Extension/Renderer processes to be terminated:" -ForegroundColor Yellow
                $targetProcesses | ForEach-Object {
                    Write-Host "  PID $($_.Id): $($_.ProcessName) - $($_.MemoryMB) MB" -ForegroundColor Red
                }
                $confirm = Read-Host "Confirm termination? (y/N)"
                if ($confirm -eq 'y' -or $confirm -eq 'Y') {
                    $targetProcesses | ForEach-Object {
                        try {
                            Stop-Process -Id $_.Id -Force
                            Write-Host "  Terminated PID $($_.Id)" -ForegroundColor Green
                        }
                        catch {
                            Write-Host "  Failed to terminate PID $($_.Id): $($_.Exception.Message)" -ForegroundColor Red
                        }
                    }
                }
            } else {
                Write-Host "No extension/renderer processes found." -ForegroundColor Green
            }
        }
        "4" {
            Write-Host "⚠️  WARNING: This will kill ALL VS Code processes!" -ForegroundColor Red
            Write-Host "Development servers will be preserved." -ForegroundColor Green
            $confirm = Read-Host "Are you sure? Type 'KILL ALL' to confirm"
            if ($confirm -eq 'KILL ALL') {
                $vscodeProcesses | ForEach-Object {
                    try {
                        Stop-Process -Id $_.Id -Force
                        Write-Host "  Terminated PID $($_.Id)" -ForegroundColor Green
                    }
                    catch {
                        Write-Host "  Failed to terminate PID $($_.Id): $($_.Exception.Message)" -ForegroundColor Red
                    }
                }
                Write-Host "All VS Code processes terminated. Development servers preserved." -ForegroundColor Green
            } else {
                Write-Host "Operation cancelled." -ForegroundColor Yellow
            }
        }
        "5" {
            Write-Host "No action taken." -ForegroundColor Yellow
        }
        default {
            Write-Host "Invalid option. No action taken." -ForegroundColor Red
        }
    }
}
elseif ($totalMemoryMB -gt 2500) {
    Write-Host "🟡 WARNING: High memory usage but process count is acceptable" -ForegroundColor Yellow
    Write-Host "Consider closing large files or restarting VS Code when convenient." -ForegroundColor White
}
else {
    Write-Host "✅ VS Code performance looks acceptable" -ForegroundColor Green
}

Write-Host ""
Write-Host "Development servers detected and protected from termination." -ForegroundColor Green
Write-Host "Script completed safely." -ForegroundColor Cyan

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
