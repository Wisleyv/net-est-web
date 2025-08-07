Write-Host "=== NET-EST Cache Status ===" -ForegroundColor Cyan
Write-Host ""

$caches = @{
    "PIP Cache" = "c:\net\.pip-cache"
    "HuggingFace Cache" = "c:\net\.huggingface-cache"
    "Torch Cache" = "c:\net\.models\torch"
    "Python Cache" = "c:\net\.python-cache"
}

foreach ($cache in $caches.GetEnumerator()) {
    if (Test-Path $cache.Value) {
        $size = (Get-ChildItem $cache.Value -Recurse -Force -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "$($cache.Key): $([math]::Round($size, 2)) MB" -ForegroundColor Green
    } else {
        Write-Host "$($cache.Key): Empty" -ForegroundColor Gray
    }
}

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
