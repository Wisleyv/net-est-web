$pids = @(10884,29468)
foreach ($pid in $pids) {
    $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$pid"
    if ($proc) {
        Write-Host "PID: $($proc.ProcessId)"
        Write-Host "CommandLine: $($proc.CommandLine)"
        Write-Host "---"
    } else {
        Write-Host "PID $pid not found"
    }
}
