param(
  [int]$TargetPid = 24232
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'SilentlyContinue'

Write-Host "Inspecting PID: $TargetPid" -ForegroundColor Cyan

try {
  $p = Get-Process -Id $TargetPid -ErrorAction Stop
  Write-Host "Get-Process: Id=$($p.Id) Name=$($p.ProcessName) Path=$($p.Path)" -ForegroundColor Green
} catch {
  Write-Host "Get-Process failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "\nWin32_Process info (if available):" -ForegroundColor Cyan
try {
  $info = Get-CimInstance -Namespace root\cimv2 -ClassName Win32_Process | Where-Object { $_.ProcessId -eq $TargetPid }
  if ($info) {
    Write-Host "ProcessId: $($info.ProcessId)"
    Write-Host "ParentProcessId: $($info.ParentProcessId)"
    Write-Host "ExecutablePath: $($info.ExecutablePath)"
    Write-Host "CommandLine:" -ForegroundColor Magenta
    Write-Host $info.CommandLine
  } else {
    Write-Host "No Win32_Process entry found for PID $Pid" -ForegroundColor Yellow
  }
} catch {
  Write-Host "Get-CimInstance failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "\nListening TCP connections on port 8000:" -ForegroundColor Cyan
try {
  $listeners = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
  if ($listeners) {
    $listeners | Select-Object LocalAddress,LocalPort,State,OwningProcess | Format-Table -AutoSize
  } else {
    Write-Host "No listeners found on port 8000" -ForegroundColor Green
  }
} catch {
  Write-Host "Get-NetTCPConnection failed: $($_.Exception.Message)" -ForegroundColor Red
}
