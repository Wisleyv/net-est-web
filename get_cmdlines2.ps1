$ids = @(10884,29468)
foreach ($id in $ids) {
    $proc = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$id"
    if ($proc) {
        Write-Host "PID: $($proc.ProcessId)"
        Write-Host "CommandLine: $($proc.CommandLine)"
        Write-Host "---"
    } else {
        Write-Host "PID $id not found"
    }
}
