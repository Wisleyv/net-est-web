"""Endpoints de health check e status da API"""

import time

import psutil
from fastapi import APIRouter

from src.core.config import settings
from src.models.base import HealthResponse


router = APIRouter()

# Tempo de inicialização da aplicação
START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check básico da API

    Retorna:
        - Status da aplicação
        - Versão atual
        - Tempo de uptime
        - Uso básico de recursos
    """
    uptime = time.time() - START_TIME

    return HealthResponse(
        message="NET-EST API está funcionando",
        version=settings.VERSION,
        status="healthy",
        uptime_seconds=uptime,
    )


@router.get("/status")
async def detailed_status():
    """Status detalhado do sistema

    Inclui informações sobre:
        - Recursos do sistema
        - Configurações ativas
        - Limites definidos
        - Status de componentes (database, cache)
    """
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)

    # Database status check (when database is implemented)
    database_status = {"status": "not_configured", "details": "Database not initialized"}
    try:
        from src.core.database import check_database_health

        database_status = await check_database_health()
    except ImportError:
        database_status = {
            "status": "module_unavailable",
            "details": "Database module not available",
        }
    except Exception as e:
        database_status = {"status": "error", "details": f"Database check failed: {str(e)}"}

    # Cache status (future)
    cache_status = {"status": "not_configured", "details": "Cache not configured"}
    if settings.ENABLE_REDIS_CACHE:
        cache_status = {"status": "configured", "details": f"Redis URL: {settings.REDIS_URL}"}

    return {
        "api": {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "debug": settings.DEBUG,
            "uptime_seconds": time.time() - START_TIME,
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_percent": memory.percent,
        },
        "components": {
            "database": database_status,
            "cache": cache_status,
            "rate_limiting": {
                "enabled": settings.RATE_LIMIT_ENABLED,
                "requests_per_minute": settings.REQUESTS_PER_MINUTE,
            },
        },
        "configuration": {
            "allowed_origins": settings.allowed_origins_list,
            "upload_dir": settings.UPLOAD_DIR,
            "allowed_file_types": settings.allowed_file_types_list,
        },
        "limits": {
            "max_words": settings.MAX_WORDS_LIMIT,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        },
        "models": {
            "bertimbau_model": settings.BERTIMBAU_MODEL,
            "similarity_threshold": settings.SIMILARITY_THRESHOLD,
        },
    }
