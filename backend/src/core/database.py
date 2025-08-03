"""Database configuration and models for future scalability"""

from collections.abc import AsyncGenerator


# Conditional imports for database functionality
# These will only work when SQLAlchemy is installed
try:
    from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.sql import func

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    # Create dummy classes for type hints when SQLAlchemy is not available
    AsyncSession = None
    Base = None

from .config import settings


# Database Base Model (only available if SQLAlchemy is installed)
if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
else:
    Base = None

# Database Engine (not initialized by default)
engine = None
async_session_maker = None


async def init_database():
    """Initialize database connection - call this when database is needed"""
    global engine, async_session_maker

    if not SQLALCHEMY_AVAILABLE:
        raise ImportError(
            "SQLAlchemy not installed. Install with: pip install sqlalchemy alembic asyncpg"
        )

    if engine is None:
        # Convert SQLite URL to async version if needed
        db_url = settings.DATABASE_URL
        if db_url.startswith("sqlite://"):
            db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")

        engine = create_async_engine(
            db_url,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
        )

        async_session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency for FastAPI"""
    if not SQLALCHEMY_AVAILABLE:
        raise ImportError("SQLAlchemy not installed")

    if async_session_maker is None:
        await init_database()

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables - run this during app startup if database is enabled"""
    if not SQLALCHEMY_AVAILABLE:
        raise ImportError("SQLAlchemy not installed")

    if engine is None:
        await init_database()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Future Database Models (only defined if SQLAlchemy is available)
if SQLALCHEMY_AVAILABLE and Base is not None:

    class AnalysisResult(Base):
        """Store analysis results for user feedback and improvement"""

        __tablename__ = "analysis_results"

        id = Column(Integer, primary_key=True, index=True)
        session_id = Column(String(255), index=True)  # For anonymous tracking
        source_text = Column(Text, nullable=False)
        target_text = Column(Text, nullable=False)
        similarity_score = Column(Float)
        processing_time = Column(Float)
        created_at = Column(DateTime(timezone=True), server_default=func.now())

        # User feedback (when Module 5 is implemented)
        user_rating = Column(Integer, nullable=True)  # 1-5 scale
        user_feedback = Column(Text, nullable=True)

    class UserSession(Base):
        """Track user sessions for analytics"""

        __tablename__ = "user_sessions"

        id = Column(String(255), primary_key=True)  # UUID
        ip_address = Column(String(45))  # IPv6 support
        user_agent = Column(Text)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        last_activity = Column(DateTime(timezone=True), server_default=func.now())
        analysis_count = Column(Integer, default=0)

    class SystemMetrics(Base):
        """Store system performance metrics"""

        __tablename__ = "system_metrics"

        id = Column(Integer, primary_key=True, index=True)
        metric_name = Column(String(100), nullable=False)
        metric_value = Column(Float, nullable=False)
        timestamp = Column(DateTime(timezone=True), server_default=func.now())


# Health check for database
async def check_database_health() -> dict:
    """Check database connectivity and return status"""
    if not SQLALCHEMY_AVAILABLE:
        return {"status": "not_available", "details": "SQLAlchemy not installed"}

    try:
        if engine is None:
            return {"status": "not_initialized", "details": "Database engine not initialized"}

        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
            return {"status": "healthy", "details": "Database connection successful"}
    except Exception as e:
        return {"status": "unhealthy", "details": f"Database error: {str(e)}"}
