"""NET-EST API - Sistema de Análise de Tradução Intralinguística
Desenvolvido pelo Núcleo de Estudos de Tradução - UFRJ
"""

import sys
from pathlib import Path

import structlog


# Adicionar o diretório raiz ao PYTHONPATH
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


# Configurar logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    logger.info("🚀 NET-EST API iniciando...")
    yield
    logger.info("🔥 NET-EST API finalizando...")


# Criar aplicação FastAPI
app = FastAPI(
    title="NET-EST API",
    description="Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual",
    version="1.0.0",
    contact={
        "name": "Núcleo de Estudos de Tradução - UFRJ",
        "email": "contato@net-est.ufrj.br",  # placeholder
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
# Include routers
app.include_router(health_router)
app.include_router(text_input_router)
app.include_router(semantic_alignment_router)
app.include_router(analytics_router)


# Handler de exceções global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Erro não tratado", error=str(exc), path=request.url.path)
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
        log_config=None,  # Usar nosso logging customizado
    )
