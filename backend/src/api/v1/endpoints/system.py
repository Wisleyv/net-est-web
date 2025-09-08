from fastapi import APIRouter
from src.core.config import settings

router = APIRouter(prefix="/api/v1/system", tags=["system"])

@router.get("/persistence")
async def get_persistence_info():
    return {
        "active_backend": settings.PERSISTENCE_BACKEND,
        "enable_dual_write": settings.ENABLE_DUAL_WRITE,
        "enable_fs_fallback": settings.ENABLE_FS_FALLBACK,
        "sqlite_db_path": settings.SQLITE_DB_PATH,
    }
