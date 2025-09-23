<#
.SYNOPSIS
  Sets up and verifies a pinned Python 3.12 virtual environment for NET-EST backend.

.DESCRIPTION
  - Creates backend/.venv_py312 with Python 3.12 if missing
  - Activates the venv and installs required packages from backend/requirements.txt
  - Installs minimal test tooling (pytest, requests)
  - Prints versions and short verification of key libs (fastapi, uvicorn)

.PARAMETER Python312
  Absolute path to a Python 3.12 executable. Default attempts in order:
    - C:\\Python312\\python.exe
    - py -3.12

.EXAMPLE
  pwsh -ExecutionPolicy Bypass -File scripts/setup_py312.ps1

.EXAMPLE
  pwsh -ExecutionPolicy Bypass -File scripts/setup_py312.ps1 -Python312 'D:\\Apps\\Python312\\python.exe'
#>

[CmdletBinding()] param(
  [string] $Python312 = 'C:\\Python312\\python.exe'
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host $msg -ForegroundColor Green }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host $msg -ForegroundColor Red }

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root 'backend'
$venvPath = Join-Path $backend '.venv_py312'
$activate = Join-Path $venvPath 'Scripts/Activate.ps1'

try {
  Write-Info "NET-EST: Setting up Python 3.12 virtual environment..."

  # Resolve Python 3.12 executable
  if (-not (Test-Path $Python312)) {
    Write-Warn "Python 3.12 not found at $Python312. Trying 'py -3.12' shim..."
    $shim = (Get-Command py -ErrorAction SilentlyContinue)
    if ($shim) {
      & py -3.12 --version 2>$null
      if ($LASTEXITCODE -eq 0) {
        $Python312 = 'py -3.12'
      } else {
        throw "Could not resolve a Python 3.12 interpreter. Install 3.12.x or provide -Python312 path."
      }
    } else {
      throw "Python 3.12 executable not found and 'py' shim is unavailable."
    }
  }

  # Create venv if missing
  if (-not (Test-Path $venvPath)) {
    Write-Info "Creating virtual environment at $venvPath ..."
    if ($Python312 -eq 'py -3.12') {
      & py -3.12 -m venv $venvPath
    } else {
      & $Python312 -m venv $venvPath
    }
  } else {
    Write-Info "Virtual environment already exists at $venvPath"
  }

  # Activate and install deps
  if (-not (Test-Path $activate)) {
    throw "Activation script not found at $activate"
  }

  Write-Info "Activating venv and installing dependencies..."
  & $activate
  pip install -q --upgrade pip

  $reqFile = Join-Path $backend 'requirements.txt'
  if (Test-Path $reqFile) {
    pip install -q -r $reqFile
  } else {
    Write-Warn "requirements.txt not found; installing core packages explicitly."
    pip install -q fastapi uvicorn[standard] pydantic pydantic-settings sentence-transformers transformers torch numpy scipy scikit-learn psutil python-multipart python-dotenv
  }

  pip install -q pytest requests

  Write-Info "Verifying interpreter and key packages..."
  python -c "import sys; print('Python:', sys.version)"
  python -c "import fastapi, uvicorn; print('fastapi', fastapi.__version__); print('uvicorn', uvicorn.__version__)"

  Write-Ok "Python 3.12 environment ready at $venvPath"

} catch {
  Write-Err "Setup failed: $($_.Exception.Message)"
  exit 1
}
