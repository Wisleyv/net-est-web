param()

Write-Host 'VS Code Process Analysis:' -ForegroundColor Cyan
Get-Process -Name 'Code*' | Format-Table Name, WorkingSet -AutoSize

Write-Host 'Cache directories:' -ForegroundColor Yellow
(Get-ChildItem -Path . -Recurse -Directory -Name '__pycache__' | Measure-Object).Count