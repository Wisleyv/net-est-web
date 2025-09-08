"""Configurações centralizadas da aplicação"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Configurações básicas
    APP_NAME: str = "NET-EST API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    FALLBACK_PORT: int = 8080
    RELOAD: bool = True

    # CORS - Handling comma-separated string from .env
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Database Configuration (Future Scalability)
    DATABASE_URL: str = "sqlite:///./net_est.db"  # Default to SQLite for development
    DATABASE_ECHO: bool = False  # Set to True for SQL query logging
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # External Database Options (Production)
    # For Neon PostgreSQL: postgresql+asyncpg://user:pass@host/dbname
    # For Supabase: postgresql+asyncpg://postgres:pass@host:5432/postgres

    # Redis Configuration (Optional for caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    ENABLE_REDIS_CACHE: bool = False

    # API Rate Limiting (Future)
    RATE_LIMIT_ENABLED: bool = False
    REQUESTS_PER_MINUTE: int = 60

    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    ALLOWED_FILE_TYPES: str = "txt,docx,pdf"

    @property
    def allowed_file_types_list(self) -> list[str]:
        """Convert comma-separated file types to list"""
        return [ftype.strip() for ftype in self.ALLOWED_FILE_TYPES.split(",")]

    # Limites de processamento
    MAX_WORDS_LIMIT: int = 2000
    MAX_FILE_SIZE_MB: int = 10

    # Strategy Detection Configuration
    STRATEGY_DETECTION_MODE: str = "complete"  # "complete" or "performance"
    MAX_SENTENCES_FOR_PERFORMANCE: int = 5  # Only used in performance mode

    # Futuros - Modelos e API
    BERTIMBAU_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    SIMILARITY_THRESHOLD: float = 0.5

    # HITL Phase 1 Feature Flags (additive, safe defaults)
    HITL_MODEL_VERSION: str = "hitl-phase1-0.1"
    HITL_ALLOW_AUTO_OMISSION: bool = False  # OM+ auto detection disabled unless explicitly enabled
    HITL_ALLOW_AUTO_PROBLEM: bool = False   # PRO+ auto detection never enabled by default
    HITL_ENABLE_POSITION_OFFSETS: bool = True  # expose paragraph/sentence/char offsets
    HITL_EXPOSE_DETECTION_CONFIG: bool = True  # include detection_config block in responses
    HITL_STRATEGY_ID_METHOD: str = "uuid4"  # future: 'content-hash'

    # Phase 4c - Persistence Abstraction
    # fs | sqlite (default fs for compatibility in ephemeral deployments)
    PERSISTENCE_BACKEND: str = "fs"
    # When true, writes go to FS (primary) and SQLite (shadow). Reads remain FS.
    ENABLE_DUAL_WRITE: bool = False
    # SQLite file path (only used when SQLite is selected or dual-write enabled)
    SQLITE_DB_PATH: str = "src/data/net_est.sqlite3"
    # Phase 4d - FS fallback when SQLite is primary
    ENABLE_FS_FALLBACK: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Re-enabling .env file loading
    )


def setup_logging():
    """Configurar logging estruturado"""
    import structlog

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            (
                structlog.dev.ConsoleRenderer()
                if settings.DEBUG
                else structlog.processors.JSONRenderer()
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.LOG_LEVEL.upper(), 20)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Instância global das configurações
settings = Settings()
