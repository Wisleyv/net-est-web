#!/usr/bin/env python3
"""NET-EST API - Sistema de Análise de Tradução Intralinguística
Developed by Núcleo de Estudos de Tradução - UFRJ
This version avoids printing non-ASCII characters to the console to prevent
Unicode encoding errors on Windows consoles.
"""

import sys
from pathlib import Path

import structlog

# Add the root directory to PYTHONPATH
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings, setup_logging

from .api.health import router as health_router
from .api.semantic_alignment import router as semantic_alignment_router
from .api.text_input import router as text_input_router
from .api.analytics import router as analytics_router
from .api.comparative_analysis import router as comparative_analysis_router
from .api.v1.feature_extraction import router as feature_extraction_router
from .api.manual_tags import router as manual_tags_router


# Configure logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management (startup / shutdown)"""

    # Use ASCII-only log messages to avoid Windows console encoding issues
    logger.info("NET-EST API starting up...")
    
    # Pre-load models at startup for better performance
    logger.info("Loading ML models...")
    try:
        from .services.strategy_detector import _initialize_models
        nlp, semantic_model = _initialize_models()
        if semantic_model:
            logger.info("Semantic model loaded on startup")
        else:
            logger.info("Semantic model not available - using heuristics only")
    except Exception as e:
        logger.warning(f"Error while loading models: {e}")
    
    yield
    logger.info("NET-EST API shutting down...")


# Create the FastAPI application
app = FastAPI(
    title="NET-EST API",
    description="Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual",
    version="1.0.0",
    contact={
        "name": "Núcleo de Estudos de Tradução - UFRJ",
        "email": "contato@net-est.ufrj.br",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(text_input_router)
app.include_router(semantic_alignment_router)
app.include_router(analytics_router)
app.include_router(comparative_analysis_router)
app.include_router(feature_extraction_router, prefix="/api/v1")
app.include_router(manual_tags_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled error", error=str(exc), path=str(request.url.path))
    return JSONResponse(
        status_code=500, content={"detail": "Erro interno do servidor", "type": "internal_error"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # Use our custom logging
    )
