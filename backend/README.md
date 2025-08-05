# NET-EST Backend

This is the FastAPI backend for the NET-EST linguistic analysis tool.

## Quick Start

### Development Mode (Recommended)
```bash
# Windows
start_optimized.bat

# Cross-platform
python start_optimized.py
```

### Alternative Methods
```bash
# Backup batch script
start_backend.bat

# Manual uvicorn (from backend directory)
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

## Scripts Overview

- **`start_optimized.py`** ⭐ **PRIMARY**: Advanced startup script with automatic port detection and fallback
- **`start_optimized.bat`** ⭐ **PRIMARY**: Windows batch version with comprehensive checks
- **`start_backend.bat`**: Simple backup batch script
- **`start_server.py`**: Simple backup Python script

## Documentation

For comprehensive documentation on the backend architecture, API endpoints, and development guidelines, please refer to:

- [Central Documentation Hub](../DOCUMENTATION.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Development Guide](../DEVELOPMENT.md)

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
- **`diagnose_fixed.py`**: Environment diagnostic tool

## Directory Structure

```
backend/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   ├── core/              # Core configurations
│   ├── models/            # Data models
│   └── services/          # Business logic
├── tests/                 # All test files
├── venv/                  # Virtual environment
├── start_optimized.py     # 🚀 PRIMARY startup script
├── start_optimized.bat    # 🚀 PRIMARY batch script
└── requirements.txt       # Dependencies
```

## Configuration

The backend uses environment variables for configuration. Check `.env.example` for available options.

Default settings:
- Host: `127.0.0.1` (localhost)
- Port: `8000` (fallback to `8080` if occupied)
- Reload: `True` (development mode)
