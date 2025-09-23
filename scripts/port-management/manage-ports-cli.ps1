<# CLI wrapper for port-management functions. Use this from `pwsh -File` to avoid param parsing issues when the module is dot-sourced. #>
param(
    [ValidateSet('Get-PortProcess','Test-PortAvailable')][Parameter(Mandatory=$true)][string]$Function,
    [Parameter(Mandatory=$true)][ValidateRange(1,65535)][int]$Port
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$modulePath = Join-Path -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) -ChildPath 'port-management.ps1'
if (-not (Test-Path $modulePath)) { Write-Error "Module not found: $modulePath"; exit 2 }

. $modulePath

if ($Function -eq 'Get-PortProcess') {
    $out = Get-PortProcess -Port $Port
    $out | ConvertTo-Json -Depth 5
    exit 0
} elseif ($Function -eq 'Test-PortAvailable') {
    $ok = Test-PortAvailable -Port $Port
    if ($ok) { Write-Output 'True'; exit 0 } else { Write-Output 'False'; exit 1 }
}
