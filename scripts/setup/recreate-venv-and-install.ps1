# recreate_venv_and_install.ps1 - create .venv and install backend requirements
$root = 'C:\net'
Set-Location $root
if (Test-Path (Join-Path $root '.venv')) { Write-Host 'Removing existing .venv' ; Remove-Item -Recurse -Force (Join-Path $root '.venv') }
Write-Host 'Creating virtual environment .venv' ; python -m venv .venv
Write-Host 'Activating venv and upgrading pip' ; .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
if (Test-Path (Join-Path $root 'backend\requirements.txt')) { Write-Host 'Installing backend requirements...' ; .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt } else { Write-Host 'No backend requirements.txt found, skipping pip install' }
Write-Host 'Virtual environment recreation and install complete.'