# Configuration Guide

This document explains how to configure the NET-EST application for different environments.

## Backend Configuration

The backend uses environment variables loaded from `.env` files. Configuration is handled by Pydantic Settings for type safety and validation.

### Environment Files

- **`.env`**: Development configuration (already exists)
- **`.env.example`**: Template for new environments
- **`src/core/config.py`**: Configuration class definition

### Available Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | NET-EST API | Application name |
| `VERSION` | string | 1.0.0 | Application version |
| `DEBUG` | boolean | false | Debug mode |
| `HOST` | string | 127.0.0.1 | Server host |
| `PORT` | integer | 8000 | Primary server port |
| `FALLBACK_PORT` | integer | 8080 | Fallback port if primary is occupied |
| `RELOAD` | boolean | true | Auto-reload on code changes |
| `ALLOWED_ORIGINS` | string | localhost:3000,localhost:5173 | CORS allowed origins (comma-separated) |
| `LOG_LEVEL` | string | INFO | Logging level |
| `MAX_WORDS_LIMIT` | integer | 2000 | Maximum words for processing |
| `MAX_FILE_SIZE_MB` | integer | 10 | Maximum file size in MB |

### NLP Models (spaCy)

- Strongly recommended: Portuguese language model `pt_core_news_sm` for more accurate tokenization and POS/NER features used by strategy detection.
- Install via VS Code task: "Install spaCy PT model (recommended)". This uses the project venv (`backend/.venv_py312`).
- Fallback behavior: If the model is missing, the backend falls back to heuristic-only analysis; accuracy will be reduced and some tags may be less reliable.

### Usage Example

```bash
# .env
HOST=0.0.0.0
PORT=8080
DEBUG=false
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://myapp.com
```

## Frontend Configuration

The frontend uses Vite's environment variable system with the `VITE_` prefix.

### Environment Files

- **`.env.development`**: Development-specific settings
- **`.env.production`**: Production-specific settings  
- **`.env.example`**: Template for new environments

### Available Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VITE_API_BASE_URL` | string | http://localhost:8000 | Backend API URL |
| `VITE_APP_NAME` | string | NET-EST | Application name |
| `VITE_VERSION` | string | 1.0.0 | Application version |
| `VITE_DEBUG` | boolean | false | Debug mode |

### Usage Example

```bash
# .env.production
VITE_API_BASE_URL=https://api.myapp.com
VITE_DEBUG=false
```

## Environment Setup

### For Development
1. Copy `.env.example` to `.env` in both `backend/` and `frontend/` directories
2. Adjust values as needed for your local environment
3. Run the application using the startup scripts
4. (Recommended) Run the task "Install spaCy PT model (recommended)" and restart the backend

### For Production
1. Create `.env.production` files with production-specific values
2. Ensure sensitive values are properly secured
3. Use environment variable injection in your deployment system

## Best Practices

1. **Never commit sensitive data** like API keys or passwords to version control
2. **Use `.env.example`** files to document required environment variables
3. **Validate configuration** on application startup
4. **Use different ports** for different environments to avoid conflicts
5. **Set DEBUG=false** in production environments

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
