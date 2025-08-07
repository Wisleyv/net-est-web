# VS Code Performance Diagnostic Script
# Run this in a separate PowerShell window to monitor system performance
# while VS Code is running and experiencing lag

Write-Host "=== VS Code Performance Diagnostic Tool ===" -ForegroundColor Cyan
Write-Host "Starting continuous monitoring... Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Function to get VS Code processes
function Get-VSCodeProcesses {
    return Get-Process -Name "Code*" -ErrorAction SilentlyContinue | 
           Sort-Object CPU -Descending
}

# Function to get system resource usage
function Get-SystemResources {
    try {
        # Try English counter names first, then Portuguese
        $cpuCounters = @(
            "\Processor(_Total)\% Processor Time",
            "\Processador(_Total)\% Tempo do Processador"
        )
        
        $cpu = $null
        foreach ($counter in $cpuCounters) {
            try {
                $cpu = Get-Counter $counter -SampleInterval 1 -MaxSamples 1 -ErrorAction Stop
                break
            }
            catch {
                continue
            }
        }
        
        $memory = Get-CimInstance -ClassName Win32_OperatingSystem
        $memoryUsed = [math]::Round(($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize * 100, 2)
        
        return @{
            CPU = if ($cpu) { [math]::Round($cpu.CounterSamples[0].CookedValue, 2) } else { "N/A" }
            Memory = $memoryUsed
            FreeMemoryGB = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
            TotalMemoryGB = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
        }
    }
    catch {
        $memory = Get-CimInstance -ClassName Win32_OperatingSystem
        return @{
            CPU = "Error"
            Memory = [math]::Round(($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize * 100, 2)
            FreeMemoryGB = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
            TotalMemoryGB = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
        }
    }
}

# Function to get disk I/O activity
function Get-DiskIOActivity {
    try {
        # Try multiple counter name variations for different Windows languages
        $diskCounters = @{
            Reads = @("\PhysicalDisk(_Total)\Disk Reads/sec", "\Disco Físico(_Total)\Leituras de Disco/s")
            Writes = @("\PhysicalDisk(_Total)\Disk Writes/sec", "\Disco Físico(_Total)\Gravações de Disco/s") 
            Queue = @("\PhysicalDisk(_Total)\Current Disk Queue Length", "\Disco Físico(_Total)\Tamanho Atual da Fila do Disco")
        }
        
        $diskReads = $null
        $diskWrites = $null
        $diskQueue = $null
        
        # Try to get disk reads
        foreach ($counter in $diskCounters.Reads) {
            try {
                $diskReads = Get-Counter $counter -SampleInterval 1 -MaxSamples 1 -ErrorAction Stop
                break
            }
            catch { continue }
        }
        
        # Try to get disk writes
        foreach ($counter in $diskCounters.Writes) {
            try {
                $diskWrites = Get-Counter $counter -SampleInterval 1 -MaxSamples 1 -ErrorAction Stop
                break
            }
            catch { continue }
        }
        
        # Try to get disk queue
        foreach ($counter in $diskCounters.Queue) {
            try {
                $diskQueue = Get-Counter $counter -SampleInterval 1 -MaxSamples 1 -ErrorAction Stop
                break
            }
            catch { continue }
        }
        
        return @{
            ReadsPerSec = if ($diskReads) { [math]::Round($diskReads.CounterSamples[0].CookedValue, 2) } else { "N/A" }
            WritesPerSec = if ($diskWrites) { [math]::Round($diskWrites.CounterSamples[0].CookedValue, 2) } else { "N/A" }
            QueueLength = if ($diskQueue) { [math]::Round($diskQueue.CounterSamples[0].CookedValue, 2) } else { "N/A" }
        }
    }
    catch {
        return @{
            ReadsPerSec = "Error"
            WritesPerSec = "Error"
            QueueLength = "Error"
        }
    }
}

# Function to get top CPU and memory consuming processes
function Get-TopProcesses {
    $topCPU = Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 ProcessName, CPU, WorkingSet64
    $topMemory = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 ProcessName, CPU, WorkingSet64
    
    return @{
        TopCPU = $topCPU
        TopMemory = $topMemory
    }
}

# Function to check for suspicious Windows services
function Get-SuspiciousServices {
    $suspiciousServices = @(
        "Windows Search",
        "Superfetch",
        "Windows Update",
        "BITS",
        "Windows Defender",
        "Background Intelligent Transfer Service"
    )
    
    $runningServices = foreach ($service in $suspiciousServices) {
        $svc = Get-Service -Name "*$($service.Split(' ')[0])*" -ErrorAction SilentlyContinue
        if ($svc -and $svc.Status -eq 'Running') {
            $svc | Select-Object Name, Status
        }
    }
    
    return $runningServices
}

# Function to check network activity
function Get-NetworkActivity {
    try {
        # Try different network counter names for localization
        $networkCounters = @{
            Sent = @("\Network Interface(*)\Bytes Sent/sec", "\Interface de Rede(*)\Bytes Enviados/s")
            Received = @("\Network Interface(*)\Bytes Received/sec", "\Interface de Rede(*)\Bytes Recebidos/s")
        }
        
        $netSent = $null
        $netReceived = $null
        
        # Try to get network sent
        foreach ($counter in $networkCounters.Sent) {
            try {
                $netSent = Get-Counter $counter -SampleInterval 1 -MaxSamples 1 -ErrorAction Stop | 
                           Where-Object { $_.CounterSamples.InstanceName -notlike "*Loopback*" -and $_.CounterSamples.InstanceName -notlike "*isatap*" }
                break
            }
            catch { continue }
        }
        
        # Try to get network received
        foreach ($counter in $networkCounters.Received) {
            try {
                $netReceived = Get-Counter $counter -SampleInterval 1 -MaxSamples 1 -ErrorAction Stop | 
                               Where-Object { $_.CounterSamples.InstanceName -notlike "*Loopback*" -and $_.CounterSamples.InstanceName -notlike "*isatap*" }
                break
            }
            catch { continue }
        }
        
        $totalSent = if ($netSent) { ($netSent.CounterSamples | Measure-Object CookedValue -Sum).Sum / 1KB } else { 0 }
        $totalReceived = if ($netReceived) { ($netReceived.CounterSamples | Measure-Object CookedValue -Sum).Sum / 1KB } else { 0 }
        
        return @{
            SentKBps = [math]::Round($totalSent, 2)
            ReceivedKBps = [math]::Round($totalReceived, 2)
        }
    }
    catch {
        return @{
            SentKBps = "Error"
            ReceivedKBps = "Error"
        }
    }
}

# Main monitoring loop
$iteration = 0
$logFile = "c:\net\vscode_performance_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

Write-Host "Logging to: $logFile" -ForegroundColor Green
Write-Host ""

while ($true) {
    $iteration++
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    Clear-Host
    Write-Host "=== VS Code Performance Monitor - Iteration $iteration ===" -ForegroundColor Cyan
    Write-Host "Time: $timestamp" -ForegroundColor White
    Write-Host ""
    
    # Get all monitoring data
    $vscodeProcesses = Get-VSCodeProcesses
    $systemResources = Get-SystemResources
    $diskIO = Get-DiskIOActivity
    $topProcesses = Get-TopProcesses
    $suspiciousServices = Get-SuspiciousServices
    $networkActivity = Get-NetworkActivity
    
    # Display VS Code processes
    Write-Host "VS CODE PROCESSES:" -ForegroundColor Yellow
    if ($vscodeProcesses) {
        $vscodeProcesses | ForEach-Object {
            $memMB = [math]::Round($_.WorkingSet64 / 1MB, 2)
            $cpuTime = if ($_.CPU) { [math]::Round($_.CPU, 2) } else { 0 }
            Write-Host "  $($_.ProcessName) - CPU: $cpuTime sec, Memory: $memMB MB" -ForegroundColor White
        }
        Write-Host "  Total VS Code Processes: $($vscodeProcesses.Count)" -ForegroundColor Green
    } else {
        Write-Host "  No VS Code processes found!" -ForegroundColor Red
    }
    Write-Host ""
    
    # Display system resources
    Write-Host "SYSTEM RESOURCES:" -ForegroundColor Yellow
    Write-Host "  CPU Usage: $($systemResources.CPU)%" -ForegroundColor $(if ($systemResources.CPU -eq "N/A" -or $systemResources.CPU -eq "Error") { "Gray" } elseif ($systemResources.CPU -gt 80) { "Red" } elseif ($systemResources.CPU -gt 50) { "Yellow" } else { "Green" })
    Write-Host "  Memory Usage: $($systemResources.Memory)% ($($systemResources.FreeMemoryGB)GB free of $($systemResources.TotalMemoryGB)GB)" -ForegroundColor $(if ($systemResources.Memory -gt 85) { "Red" } elseif ($systemResources.Memory -gt 70) { "Yellow" } else { "Green" })
    
    # Calculate VS Code total memory usage
    $vscodeMemoryMB = ($vscodeProcesses | Measure-Object WorkingSet64 -Sum).Sum / 1MB
    Write-Host "  VS Code Total Memory: $([math]::Round($vscodeMemoryMB, 0)) MB" -ForegroundColor $(if ($vscodeMemoryMB -gt 3000) { "Red" } elseif ($vscodeMemoryMB -gt 2000) { "Yellow" } else { "Green" })
    Write-Host ""
    
    # Display disk I/O
    Write-Host "DISK I/O ACTIVITY:" -ForegroundColor Yellow
    Write-Host "  Reads/sec: $($diskIO.ReadsPerSec)" -ForegroundColor $(if ($diskIO.ReadsPerSec -gt 50) { "Red" } elseif ($diskIO.ReadsPerSec -gt 20) { "Yellow" } else { "Green" })
    Write-Host "  Writes/sec: $($diskIO.WritesPerSec)" -ForegroundColor $(if ($diskIO.WritesPerSec -gt 50) { "Red" } elseif ($diskIO.WritesPerSec -gt 20) { "Yellow" } else { "Green" })
    Write-Host "  Queue Length: $($diskIO.QueueLength)" -ForegroundColor $(if ($diskIO.QueueLength -gt 2) { "Red" } elseif ($diskIO.QueueLength -gt 1) { "Yellow" } else { "Green" })
    Write-Host ""
    
    # Display network activity
    Write-Host "NETWORK ACTIVITY:" -ForegroundColor Yellow
    Write-Host "  Sent: $($networkActivity.SentKBps) KB/s" -ForegroundColor White
    Write-Host "  Received: $($networkActivity.ReceivedKBps) KB/s" -ForegroundColor White
    Write-Host ""
    
    # Display top CPU processes
    Write-Host "TOP CPU PROCESSES:" -ForegroundColor Yellow
    $topProcesses.TopCPU | ForEach-Object {
        $memMB = [math]::Round($_.WorkingSet64 / 1MB, 2)
        $cpuTime = if ($_.CPU) { [math]::Round($_.CPU, 2) } else { 0 }
        Write-Host "  $($_.ProcessName) - CPU: $cpuTime sec, Memory: $memMB MB" -ForegroundColor White
    }
    Write-Host ""
    
    # Display top memory processes
    Write-Host "TOP MEMORY PROCESSES:" -ForegroundColor Yellow
    $topProcesses.TopMemory | ForEach-Object {
        $memMB = [math]::Round($_.WorkingSet64 / 1MB, 2)
        $cpuTime = if ($_.CPU) { [math]::Round($_.CPU, 2) } else { 0 }
        Write-Host "  $($_.ProcessName) - Memory: $memMB MB, CPU: $cpuTime sec" -ForegroundColor White
    }
    Write-Host ""
    
    # Display suspicious services
    Write-Host "ACTIVE SYSTEM SERVICES:" -ForegroundColor Yellow
    if ($suspiciousServices) {
        $suspiciousServices | ForEach-Object {
            Write-Host "  $($_.Name) - $($_.Status)" -ForegroundColor $(if ($_.Status -eq "Running") { "Yellow" } else { "Green" })
        }
    } else {
        Write-Host "  No suspicious services detected" -ForegroundColor Green
    }
    Write-Host ""
    
    # Performance warnings
    Write-Host "PERFORMANCE ALERTS:" -ForegroundColor Red
    $alerts = @()
    if ($systemResources.CPU -gt 80) { $alerts += "High CPU usage: $($systemResources.CPU)%" }
    if ($systemResources.Memory -gt 85) { $alerts += "High memory usage: $($systemResources.Memory)%" }
    if ($diskIO.QueueLength -gt 2) { $alerts += "High disk queue: $($diskIO.QueueLength)" }
    if ($diskIO.ReadsPerSec -gt 50 -or $diskIO.WritesPerSec -gt 50) { $alerts += "High disk I/O activity" }
    if ($vscodeProcesses.Count -gt 10) { $alerts += "Too many VS Code processes: $($vscodeProcesses.Count)" }
    
    if ($alerts.Count -gt 0) {
        $alerts | ForEach-Object { Write-Host "  ⚠️  $_" -ForegroundColor Red }
    } else {
        Write-Host "  ✅ System performance looks normal" -ForegroundColor Green
    }
    
    # Log to file
    $logEntry = @"
[$timestamp] CPU: $($systemResources.CPU)%, Memory: $($systemResources.Memory)%, DiskReads: $($diskIO.ReadsPerSec), DiskWrites: $($diskIO.WritesPerSec), DiskQueue: $($diskIO.QueueLength), VSCodeProcesses: $($vscodeProcesses.Count)
"@
    Add-Content -Path $logFile -Value $logEntry
    
    Write-Host ""
    Write-Host "Press Ctrl+C to stop monitoring..." -ForegroundColor Gray
    Write-Host "Log file: $logFile" -ForegroundColor Gray
    
    # Wait before next iteration
    Start-Sleep -Seconds 3
}
