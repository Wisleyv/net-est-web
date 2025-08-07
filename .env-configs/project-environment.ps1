# NET-EST Project Environment Configuration
# Source this file to set project-centric caching

# Python/Pip Cache
$env:PIP_CACHE_DIR = "c:\net\.pip-cache"
$env:PYTHONPYCACHEPREFIX = "c:\net\.python-cache"

# HuggingFace Cache
$env:HUGGINGFACE_HUB_CACHE = "c:\net\.huggingface-cache"
$env:TRANSFORMERS_CACHE = "c:\net\.huggingface-cache"
$env:HF_HOME = "c:\net\.huggingface-cache"

# Torch Cache
$env:TORCH_HOME = "c:\net\.models\torch"

# Project-specific
$env:NET_EST_PROJECT_ROOT = "c:\net"
$env:NET_EST_BACKEND_ROOT = "c:\net\backend"
$env:NET_EST_FRONTEND_ROOT = "c:\net\frontend"

Write-Host "Environment configured for NET-EST project" -ForegroundColor Green
