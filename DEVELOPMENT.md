# NET-EST Development Guide

This document provides comprehensive instructions for setting up, developing, and maintaining the NET-EST project.

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Visual Studio Code (recommended)

### Initial Setup

1. **Clone the repository:**

```bash
git clone https://github.com/Wisleyv/net-est-web.git
cd net-est-web
```

2. **Set up the backend environment:**

```bash
cd backend

# Create and activate virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install development dependencies
pip install -r requirements-dev.txt
```

3. **Set up the frontend environment:**

```bash
cd frontend

# Install dependencies
npm ci

# Or with installation and update:
npm install
```

## Running the Application

### Backend

The recommended way to start the backend:

```bash
# From the backend directory
python start_optimized.py
```

This script automatically:
- Finds an available port (starting with 8000)
- Handles environment configuration
- Sets up proper Python paths
- Provides verbose logging

Alternative methods:

```bash
# Windows batch script
start_optimized.bat

# Manual startup with uvicorn
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```bash
# From the frontend directory
npm run dev
```

This starts the Vite development server with hot module replacement enabled.

## Development Workflow

### Backend Development

1. **Code Organization:**
   - Place new endpoints in `src/api/v1/`
   - Define data models in `src/models/`
   - Implement business logic in `src/services/`

2. **Testing:**
   - Run tests with: `pytest tests/ -v`
   - Add coverage reports: `pytest tests/ -v --cov=src`
   - Test specific files: `pytest tests/test_health.py -v`

3. **API Documentation:**
   - FastAPI docs available at: `http://localhost:8000/docs`
   - ReDoc available at: `http://localhost:8000/redoc`

4. **Troubleshooting:**
   - If you encounter port issues on Windows, ensure no other process is using port 8000
   - For import errors, ensure you're running from the correct directory
   - Validate environment variables in `.env` file

### Frontend Development

1. **Code Organization:**
   - Place components in `src/components/`
   - Define API services in `src/services/`
   - Implement shared utilities in `src/utils/`

2. **State Management:**
   - Use Zustand for global state management
   - Use React Query for server state (API data)
   - Use React hooks for component-local state

3. **Testing:**
   - Run tests with: `npm test`
   - Update test snapshots: `npm test -- -u`

4. **Building for Production:**
   - Generate a production build: `npm run build`
   - Preview the production build: `npm run preview`

## Common Issues and Solutions

### Backend Issues

1. **Port Permission Error ([WinError 10013]):**
   - Symptom: `[WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions`
   - Solution: Use `127.0.0.1` instead of `0.0.0.0`, try a different port, or run as administrator

2. **Import Errors:**
   - Symptom: `attempted relative import with no known parent package`
   - Solution: Ensure you're running from the `backend` directory, not inside `src` or another subdirectory

3. **Model Loading Timeout:**
   - Symptom: Analysis operations time out after 60 seconds
   - Solution: Use `start_optimized.py` which implements optimized model loading and caching

### Frontend Issues

1. **API Connection Refused:**
   - Symptom: `ERR_CONNECTION_REFUSED` errors in console
   - Solution: Ensure backend is running and `VITE_API_URL` is set correctly in `.env`

2. **Build Errors:**
   - Symptom: TypeScript or ESLint errors preventing build
   - Solution: Fix all linting errors or temporarily disable rules in `.eslintrc.js`

## Deployment

### Backend Deployment

The recommended deployment platform is Hugging Face Spaces:

1. Create a Space on Hugging Face
2. Configure Space to use Docker
3. Upload Dockerfile and requirements.txt
4. Set environment variables in Space settings

### Frontend Deployment

The recommended deployment platform is Vercel:

1. Connect GitHub repository to Vercel
2. Configure build settings (Vite will be auto-detected)
3. Set environment variables (`VITE_API_URL` pointing to backend)
4. Deploy

## Continuous Integration

The project uses GitHub Actions for CI/CD:

1. **Backend CI:**
   - Runs linting checks
   - Executes tests
   - Builds Docker image

2. **Frontend CI:**
   - Runs linting checks
   - Executes tests
   - Builds production bundle

## Documentation Standards

When documenting code or creating user documentation:

1. **Code Documentation:**
   - Use docstrings for all functions and classes
   - Follow Google Python Style Guide for docstrings
   - Document parameters, return values, and exceptions

2. **User Documentation:**
   - Place in `docs/` directory
   - Use Markdown format
   - Include examples and screenshots when relevant

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 3.5, ChatGPT-4o, Gemini 2.0 Flash
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
