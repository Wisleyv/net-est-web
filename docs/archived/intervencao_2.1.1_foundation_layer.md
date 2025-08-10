# Especificação Técnica Detalhada - Intervenção 2.1.1 (Foundation Layer)

## Autoria e Créditos do Projeto

**Projeto:** NET-EST - Sistema de Análise Computacional para Estratégias de Simplificação em Tradução Intralingual

**Equipe de Desenvolvimento:**
- **Coordenação:** Profa. Dra. Janine Pimentel (PIPGLA/UFRJ e Politécnico de Leiria)
- **Desenvolvedor Principal:** Wisley Vilela (Doutorando PIPGLA/UFRJ - bolsista CAPES)
- **Especialista Linguística:** Luanny Matos de Lima (Mestranda PIPGLA/UFRJ)
- **Agentes Técnicos de IA:** Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash (mediados por GitHub Copilot)

**Instituições:** Núcleo de Estudos de Tradução - UFRJ | Politécnico de Leiria (PT)

**Financiamento:** Bolsa de Doutorado CAPES (Coordenação de Aperfeiçoamento de Pessoal de Nível Superior)

**Licença:** MIT License | **Repositório:** GitHub (código aberto)

*Para informações detalhadas sobre autoria e contribuições, consulte [AUTORIA_E_CREDITOS.md](./AUTORIA_E_CREDITOS.md)*

---

**Data:** 31 de Julho de 2025  
**Intervenção:** 2.1.1 - Foundation Layer  
**Prioridade:** ⭐ ALTA  
**Tempo Estimado:** 1-2 dias

---

## 🎯 Visão Geral da Intervenção

**Objetivo:** Estabelecer a infraestrutura base do projeto NET-EST, criando fundações sólidas para desenvolvimento incremental dos módulos subsequentes.

**Escopo:** Infraestrutura, configuração inicial, endpoints básicos e contratos de dados.

**Entregável Principal:** Sistema base funcional com API respondendo e frontend conectado.

---

## 📁 Estrutura de Projeto a Criar

### Estrutura Completa do Repositório

```
net-est/
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       └── frontend-ci.yml
├── backend/
│   ├── src/
│   │   ├── modules/
│   │   │   ├── __init__.py
│   │   │   ├── preprocessor.py          # Futuro
│   │   │   └── semantic_aligner.py      # Futuro
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── preprocessor_models.py
│   │   │   └── response_models.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           └── preprocessor.py  # Futuro
│   │   └── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   └── test_models.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── pytest.ini
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Loading.jsx
│   │   │   │   └── ErrorMessage.jsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   └── Footer.jsx
│   │   │   └── AboutCredits.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── config.js
│   │   ├── utils/
│   │   │   └── constants.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── .env.example
│   └── index.html
├── docs/
│   ├── [arquivos existentes...]
│   └── api/
│       └── endpoints.md
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🐍 Backend - Especificação Técnica

### 1. Configuração de Dependências

**requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.4.2
python-dotenv==1.0.0
structlog==23.2.0
pytest==7.4.2
httpx==0.25.0
```

**requirements-dev.txt:**
```
black==23.9.1
flake8==6.1.0
isort==5.12.0
mypy==1.6.1
pytest-cov==4.1.0
pytest-asyncio==0.21.1
```

### 2. Configuração Principal da API

**src/main.py:**
```python
"""
NET-EST API - Sistema de Análise de Tradução Intralinguística
Desenvolvido pelo Núcleo de Estudos de Tradução - UFRJ
"""

import os
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.core.config import settings, setup_logging
from src.api.health import router as health_router

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
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health_router, prefix="/api", tags=["health"])

# Handler de exceções global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Erro não tratado", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor", "type": "internal_error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Usar nosso logging customizado
    )
```

### 3. Configurações e Logging

**src/core/config.py:**
```python
"""Configurações centralizadas da aplicação"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações básicas
    APP_NAME: str = "NET-EST API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]  # Vite dev server
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Limites de processamento
    MAX_WORDS_LIMIT: int = 2000
    MAX_FILE_SIZE_MB: int = 10
    
    # Futuros - Modelos e API
    BERTIMBAU_MODEL: str = "neuralmind/bert-base-portuguese-cased"
    SIMILARITY_THRESHOLD: float = 0.5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def setup_logging():
    """Configurar logging estruturado"""
    import structlog
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.LOG_LEVEL.upper(), 20)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Instância global das configurações
settings = Settings()
```

### 4. Modelos de Dados Base

**src/models/base.py:**
```python
"""Modelos base para toda a aplicação"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    """Resposta base para todas as APIs"""
    success: bool = True
    message: str = "Operação realizada com sucesso"
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseResponse):
    """Resposta de erro padronizada"""
    success: bool = False
    error_type: str
    details: Optional[dict] = None

class HealthResponse(BaseResponse):
    """Resposta do health check"""
    version: str
    status: str
    uptime_seconds: float
    
class ProcessingMetrics(BaseModel):
    """Métricas de processamento"""
    processing_time: float = Field(description="Tempo de processamento em segundos")
    word_count: int = Field(description="Número de palavras processadas")
    character_count: int = Field(description="Número de caracteres")
    paragraph_count: int = Field(description="Número de parágrafos")
```

**src/models/preprocessor_models.py:**
```python
"""Modelos específicos do pré-processador"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseResponse, ProcessingMetrics

class InputType(str, Enum):
    """Tipos de entrada suportados"""
    TEXT = "text"
    FILE = "file"

class FileFormat(str, Enum):
    """Formatos de arquivo suportados"""
    TXT = "txt"
    MD = "md"
    DOCX = "docx"
    ODT = "odt"
    PDF = "pdf"

class TextInput(BaseModel):
    """Entrada de texto direto"""
    source_text: str = Field(description="Texto fonte")
    target_text: str = Field(description="Texto alvo")
    input_type: InputType = InputType.TEXT

class PreprocessorOutput(BaseResponse):
    """Saída do pré-processador"""
    source_text: str = Field(description="Texto fonte limpo")
    target_text: str = Field(description="Texto alvo limpo")
    source_metrics: ProcessingMetrics
    target_metrics: ProcessingMetrics
    warnings: List[str] = Field(default_factory=list, description="Avisos para o usuário")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Textos processados com sucesso",
                "source_text": "Texto fonte processado...",
                "target_text": "Texto alvo processado...",
                "source_metrics": {
                    "processing_time": 0.05,
                    "word_count": 150,
                    "character_count": 800,
                    "paragraph_count": 3
                },
                "target_metrics": {
                    "processing_time": 0.03,
                    "word_count": 120,
                    "character_count": 650,
                    "paragraph_count": 3
                },
                "warnings": ["Texto fonte excede 2000 palavras. Processamento pode ser mais lento."]
            }
        }
```

### 5. Endpoints de Health Check

**src/api/health.py:**
```python
"""Endpoints de health check e status da API"""

import time
import psutil
from fastapi import APIRouter
from src.models.base import HealthResponse
from src.core.config import settings

router = APIRouter()

# Tempo de inicialização da aplicação
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check básico da API
    
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
        uptime_seconds=uptime
    )

@router.get("/status")
async def detailed_status():
    """
    Status detalhado do sistema
    
    Inclui informações sobre:
        - Recursos do sistema
        - Configurações ativas
        - Limites definidos
    """
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    return {
        "api": {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "debug": settings.DEBUG,
            "uptime_seconds": time.time() - START_TIME
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_percent": memory.percent
        },
        "limits": {
            "max_words": settings.MAX_WORDS_LIMIT,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB
        },
        "models": {
            "bertimbau_model": settings.BERTIMBAU_MODEL,
            "similarity_threshold": settings.SIMILARITY_THRESHOLD
        }
    }
```

### 6. Configuração de Testes

**tests/conftest.py:**
```python
"""Configuração base para testes"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    """Cliente de teste para a API"""
    return TestClient(app)

@pytest.fixture
def sample_text_pair():
    """Par de textos para testes"""
    return {
        "source_text": "Este é um texto de exemplo para testar o sistema. Contém várias palavras e frases.",
        "target_text": "Texto de exemplo para teste. Tem palavras e frases."
    }
```

**tests/test_health.py:**
```python
"""Testes para endpoints de health check"""

import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Teste básico do health check"""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0

def test_detailed_status(client: TestClient):
    """Teste do status detalhado"""
    response = client.get("/api/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "api" in data
    assert "system" in data
    assert "limits" in data
    assert "models" in data
    
    # Verificar estrutura da resposta
    assert data["api"]["name"] == "NET-EST API"
    assert data["limits"]["max_words"] == 2000
```

---

## 🌐 Frontend - Especificação Técnica

### 1. Configuração do Projeto React

**package.json:**
```json
{
  "name": "net-est-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.1.0",
    "eslint": "^8.53.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.4",
    "vite": "^4.5.0",
    "vitest": "^0.34.6"
  }
}
```

**vite.config.js:**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  },
  define: {
    'process.env': process.env
  }
})
```

### 2. Configuração de API e Serviços

**src/services/config.js:**
```javascript
/**
 * Configurações centralizadas do frontend
 */

const config = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  APP_NAME: 'NET-EST',
  VERSION: '1.0.0',
  
  // Limites de interface
  MAX_WORDS_WARNING: 2000,
  MAX_FILE_SIZE_MB: 10,
  
  // Timeouts
  API_TIMEOUT: 30000, // 30 segundos
  
  // URLs de documentação
  DOCS_URL: 'https://github.com/net-est/docs',
  REPO_URL: 'https://github.com/net-est/net-est'
}

export default config
```

**src/services/api.js:**
```javascript
/**
 * Cliente API centralizado
 */

import axios from 'axios'
import config from './config'

// Criar instância do axios
const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para requests
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ API Request Error:', error)
    return Promise.reject(error)
  }
)

// Interceptor para responses
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Funções específicas da API
export const healthAPI = {
  check: () => api.get('/api/health'),
  status: () => api.get('/api/status')
}

export default api
```

### 3. Componentes Base

**src/components/common/Loading.jsx:**
```jsx
/**
 * Componente de loading padronizado
 */

import React from 'react'

const Loading = ({ message = 'Carregando...', size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  }

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizeClasses[size]}`}></div>
      <p className="mt-2 text-sm text-gray-600">{message}</p>
    </div>
  )
}

export default Loading
```

**src/components/common/ErrorMessage.jsx:**
```jsx
/**
 * Componente de erro padronizado
 */

import React from 'react'

const ErrorMessage = ({ error, onRetry }) => {
  const getErrorMessage = (error) => {
    if (error.response?.data?.detail) {
      return error.response.data.detail
    }
    if (error.message) {
      return error.message
    }
    return 'Ocorreu um erro inesperado'
  }

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <span className="text-red-400">❌</span>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">
            Erro no Sistema
          </h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{getErrorMessage(error)}</p>
          </div>
          {onRetry && (
            <div className="mt-4">
              <button
                onClick={onRetry}
                className="bg-red-100 text-red-800 px-3 py-1 rounded text-sm hover:bg-red-200"
              >
                Tentar Novamente
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ErrorMessage
```

### 4. Layout Principal

**src/components/layout/Header.jsx:**
```jsx
/**
 * Header da aplicação
 */

import React from 'react'
import AboutCredits from '../AboutCredits'

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">NET-EST</h1>
            <span className="ml-2 text-sm text-gray-500">v1.0</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              Núcleo de Estudos de Tradução - UFRJ
            </span>
            <AboutCredits />
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
```

### 5. Aplicação Principal

**src/App.jsx:**
```jsx
/**
 * Aplicação principal NET-EST
 */

import React, { useState, useEffect } from 'react'
import Header from './components/layout/Header'
import Loading from './components/common/Loading'
import ErrorMessage from './components/common/ErrorMessage'
import { healthAPI } from './services/api'
import './App.css'

function App() {
  const [systemStatus, setSystemStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    checkSystemHealth()
  }, [])

  const checkSystemHealth = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await healthAPI.check()
      setSystemStatus(response.data)
    } catch (err) {
      setError(err)
      console.error('Erro ao verificar saúde do sistema:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Sistema de Análise de Tradução Intralinguística
          </h2>
          <p className="text-lg text-gray-600">
            Ferramenta de análise linguística computacional para identificação e classificação 
            de estratégias de simplificação textual.
          </p>
        </div>

        {loading && (
          <Loading message="Verificando status do sistema..." />
        )}

        {error && (
          <ErrorMessage error={error} onRetry={checkSystemHealth} />
        )}

        {systemStatus && (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center mb-4">
              <span className="text-green-400 text-xl">✅</span>
              <h3 className="ml-2 text-lg font-medium text-gray-900">
                Sistema Operacional
              </h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Status:</span>
                <span className="ml-2 font-medium text-green-600">
                  {systemStatus.status}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Versão:</span>
                <span className="ml-2 font-medium">{systemStatus.version}</span>
              </div>
              <div>
                <span className="text-gray-500">Uptime:</span>
                <span className="ml-2 font-medium">
                  {Math.round(systemStatus.uptime_seconds)}s
                </span>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2">
                🚧 Em Desenvolvimento - Foundation Layer
              </h4>
              <p className="text-blue-700 text-sm">
                Esta é a primeira intervenção do projeto. O sistema básico está funcionando 
                e pronto para receber as próximas funcionalidades (entrada de texto, 
                processamento de arquivos, etc.).
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
```

---

## 🧪 Configuração de Testes e CI/CD

### 1. Workflow de CI para Backend

**.github/workflows/backend-ci.yml:**
```yaml
name: Backend CI

on:
  push:
    branches: [ main, develop ]
    paths: [ 'backend/**' ]
  pull_request:
    branches: [ main ]
    paths: [ 'backend/**' ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        cd backend
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Test with pytest
      run: |
        cd backend
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

### 2. Workflow de CI para Frontend

**.github/workflows/frontend-ci.yml:**
```yaml
name: Frontend CI

on:
  push:
    branches: [ main, develop ]
    paths: [ 'frontend/**' ]
  pull_request:
    branches: [ main ]
    paths: [ 'frontend/**' ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Lint
      run: |
        cd frontend
        npm run lint
    
    - name: Build
      run: |
        cd frontend
        npm run build
    
    - name: Test
      run: |
        cd frontend
        npm run test
```

---

## 📋 Critérios de Aceite Detalhados

### ✅ Funcionalidades Obrigatórias

1. **API Funcional:**
   - [ ] Servidor FastAPI iniciando sem erros
   - [ ] Endpoint `/api/health` respondendo com status 200
   - [ ] Endpoint `/api/status` retornando informações detalhadas
   - [ ] CORS configurado para desenvolvimento local

2. **Frontend Conectado:**
   - [ ] Aplicação React carregando sem erros
   - [ ] Comunicação com API estabelecida
   - [ ] Interface exibindo status do sistema
   - [ ] Componente de créditos funcionando

3. **Estrutura de Projeto:**
   - [ ] Pastas backend/frontend criadas
   - [ ] Arquivos de configuração no lugar
   - [ ] Dependências instaladas e funcionando

4. **Testes Básicos:**
   - [ ] Testes de health check passando
   - [ ] Cobertura de testes > 80% (código existente)
   - [ ] CI/CD configurado e executando

### 🎯 Métricas de Qualidade

- **Performance:** API respondendo em < 100ms
- **Confiabilidade:** Uptime de 100% durante desenvolvimento
- **Manutenibilidade:** Código documentado e estruturado
- **Testabilidade:** Cobertura > 80%

---

## 🚀 Comandos de Execução

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Testes
```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm run test
```

---

## 📊 Entregáveis da Intervenção

1. **✅ Estrutura de Projeto Completa**
2. **✅ API Backend Funcional**
3. **✅ Frontend Base Conectado**
4. **✅ Testes Automatizados**
5. **✅ CI/CD Configurado**
6. **✅ Documentação Técnica**

**Status Esperado:** Sistema base operacional, testado e pronto para receber Intervenção 2.1.2 (Text Input Core).

---

*Especificação preparada por: Wisley Vilela - Desenvolvedor Principal NET-EST*  
*Intervenção 2.1.1 - Foundation Layer | Prioridade ALTA | 1-2 dias*

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
