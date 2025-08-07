# Enhanced VS Code Optimizer with Smart Process Analysis
# Balanced approach for performance vs functionality

function Get-SmartVSCodeAnalysis {
    param($processes)
    
    $analysis = @{
        Critical = @()      # Main windows, active editors
        Important = @()     # Language servers for open files
        Beneficial = @()    # Extensions providing active features
        Expendable = @()    # Redundant renderers, inactive extensions
        Unknown = @()       # Unclassified processes
    }
    
    foreach ($proc in $processes) {
        $cmdLine = $proc.CommandLine.ToLower()
        $memoryMB = $proc.MemoryMB
        $title = $proc.MainWindowTitle
        
        # Critical: Never kill these
        if ($title -and $title.Contains("Visual Studio Code") -and $memoryMB -lt 800) {
            $analysis.Critical += $proc
        }
        # Important: Language servers for active development
        elseif ($cmdLine.Contains("typescript") -or $cmdLine.Contains("python") -or 
                $cmdLine.Contains("javascript") -or $cmdLine.Contains("json")) {
            $analysis.Important += $proc
        }
        # Beneficial: Active extensions
        elseif ($cmdLine.Contains("copilot") -or $cmdLine.Contains("intellicode") -or
                $cmdLine.Contains("debugger") -and $memoryMB -lt 300) {
            $analysis.Beneficial += $proc
        }
        # Expendable: High memory or redundant processes
        elseif ($memoryMB -gt 400 -or $cmdLine.Contains("renderer") -or 
                $cmdLine.Contains("utility") -or $cmdLine.Contains("worker")) {
            $analysis.Expendable += $proc
        }
        else {
            $analysis.Unknown += $proc
        }
    }
    
    return $analysis
}

# Smart optimization options
function Get-SmartOptimizationPlan {
    param($analysis, $totalMemoryMB)
    
    $plans = @()
    
    # Conservative plan (recommended for active development)
    $conservativeSavings = ($analysis.Expendable | Where-Object { $_.MemoryMB -gt 500 } | 
                           Measure-Object MemoryMB -Sum).Sum
    $plans += @{
        Name = "Conservative (Recommended)"
        Description = "Kill only high-memory expendable processes (>500MB)"
        Targets = $analysis.Expendable | Where-Object { $_.MemoryMB -gt 500 }
        EstimatedSavings = $conservativeSavings
        Risk = "Low"
        FunctionalityImpact = "Minimal"
    }
    
    # Balanced plan
    $balancedSavings = ($analysis.Expendable | Measure-Object MemoryMB -Sum).Sum
    $plans += @{
        Name = "Balanced"
        Description = "Kill all expendable processes, preserve critical/important"
        Targets = $analysis.Expendable
        EstimatedSavings = $balancedSavings
        Risk = "Medium"
        FunctionalityImpact = "Some extensions may restart"
    }
    
    # Aggressive plan (only if critical performance issues)
    $aggressiveSavings = ($analysis.Expendable + $analysis.Unknown | 
                         Measure-Object MemoryMB -Sum).Sum
    $plans += @{
        Name = "Aggressive (Last Resort)"
        Description = "Kill expendable + unknown processes"
        Targets = $analysis.Expendable + $analysis.Unknown
        EstimatedSavings = $aggressiveSavings
        Risk = "High"
        FunctionalityImpact = "May require VS Code restart"
    }
    
    return $plans
}
