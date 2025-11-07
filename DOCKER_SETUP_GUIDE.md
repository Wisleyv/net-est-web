# NET-EST Docker Development Environment Guide

**Date**: November 7, 2025  
**Purpose**: Quick start guide for multi-platform development (Codespaces, Windows, Mac, Linux)

---

## Quick Start (All Platforms)

### Prerequisites
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **Git**

### 1. Clone Repository
```bash
git clone https://github.com/Wisleyv/net-est-web.git
cd net-est-web
```

### 2. Start All Services
```bash
# Full stack (backend + frontend + database)
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **Frontend** | http://localhost:3000 | React application |
| **Database Admin** | http://localhost:8080 | Adminer (DB GUI) |
| **PostgreSQL** | localhost:5432 | Direct DB access |
| **Redis** | localhost:6379 | Cache access |

### 4. Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (data)
docker-compose down -v
```

---

## Platform-Specific Setup

### GitHub Codespaces (Recommended for Remote Work)

**Automatic Setup**:
1. Open repository in Codespaces
2. Container auto-builds with `.devcontainer/devcontainer.json`
3. Services auto-start with `docker-compose up -d`
4. Ports automatically forwarded

**Access URLs**:
- Backend: `https://8000-<workspace>.app.github.dev`
- Frontend: `https://3000-<workspace>.app.github.dev`
- API Docs: `https://8000-<workspace>.app.github.dev/docs`

**Manual Start** (if needed):
```bash
docker-compose up -d
```

---

### Windows (Docker Desktop)

**Prerequisites**:
1. Install **Docker Desktop for Windows**
2. Enable **WSL 2** backend (recommended)
3. Allocate resources:
   - Memory: 4GB minimum, 8GB recommended
   - CPU: 2 cores minimum, 4 cores recommended

**Setup**:
```powershell
# Clone repository
git clone https://github.com/Wisleyv/net-est-web.git
cd net-est-web

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

**Common Windows Issues**:

1. **Port Already in Use**:
   ```powershell
   # Find process using port 8000
   netstat -ano | findstr :8000
   
   # Kill process (replace PID)
   taskkill /PID <PID> /F
   ```

2. **Volume Mount Performance**:
   - Use WSL 2 backend (faster file sharing)
   - Clone repository inside WSL filesystem for best performance

3. **Line Endings**:
   ```bash
   # Configure git to use LF (not CRLF)
   git config --global core.autocrlf false
   ```

---

### macOS (Docker Desktop)

**Prerequisites**:
1. Install **Docker Desktop for Mac**
2. Allocate resources:
   - Memory: 4GB minimum, 8GB recommended
   - CPU: 2 cores minimum, 4 cores recommended

**Setup**:
```bash
# Clone repository
git clone https://github.com/Wisleyv/net-est-web.git
cd net-est-web

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

**macOS-Specific Tips**:
- File sharing is fast by default
- Use `cmd + space` and type "docker" to manage Docker Desktop
- Check Docker Desktop → Preferences → Resources for memory/CPU allocation

---

### Linux (Docker Engine)

**Prerequisites**:
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group (no sudo needed)
sudo usermod -aG docker $USER
newgrp docker
```

**Setup**:
```bash
# Clone repository
git clone https://github.com/Wisleyv/net-est-web.git
cd net-est-web

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

---

## Development Workflow

### Hot Reload (Code Changes Auto-Refresh)

**Backend** (FastAPI with `--reload`):
- Edit files in `backend/src/`
- Server auto-restarts on save
- No need to rebuild container

**Frontend** (Vite HMR):
- Edit files in `frontend/src/`
- Browser auto-refreshes on save
- No need to rebuild container

### Running Tests

**Backend Tests**:
```bash
# Run pytest inside container
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=src --cov-report=term-missing

# Run specific test file
docker-compose exec backend pytest tests/unit/test_alignment.py
```

**Frontend Tests**:
```bash
# Run vitest inside container
docker-compose exec frontend pnpm test

# Watch mode
docker-compose exec frontend pnpm test:watch
```

### Database Access

**Using Adminer** (Web UI):
1. Open http://localhost:8080
2. Login:
   - System: PostgreSQL
   - Server: `postgres`
   - Username: `netest`
   - Password: `netest_dev_password`
   - Database: `netest_dev`

**Using psql** (Command Line):
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U netest -d netest_dev

# Example queries
\dt                          # List tables
\d feedback_events           # Describe table
SELECT * FROM feedback_events LIMIT 10;
```

**Using Redis CLI**:
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Example commands
KEYS *                       # List all keys
GET embedding:12345          # Get cached embedding
FLUSHDB                      # Clear all cache (careful!)
```

### Viewing Logs

**All services**:
```bash
docker-compose logs -f
```

**Specific service**:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

**Last 100 lines**:
```bash
docker-compose logs --tail=100 backend
```

### Rebuilding Containers

**When to rebuild**:
- Added new dependencies to `pyproject.toml` or `package.json`
- Changed `Dockerfile` or `docker-compose.yml`
- ML model changed

**Rebuild backend**:
```bash
docker-compose build backend
docker-compose up -d backend
```

**Rebuild frontend**:
```bash
docker-compose build frontend
docker-compose up -d frontend
```

**Rebuild everything**:
```bash
docker-compose build
docker-compose up -d
```

**Force rebuild** (no cache):
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Troubleshooting

### Service Won't Start

**Check logs**:
```bash
docker-compose logs backend
docker-compose logs postgres
```

**Check service status**:
```bash
docker-compose ps
```

**Restart specific service**:
```bash
docker-compose restart backend
```

### Database Connection Errors

**Symptoms**:
- Backend logs: "connection refused" or "could not connect"

**Solutions**:
1. Wait for PostgreSQL to be healthy:
   ```bash
   docker-compose ps postgres
   # Should show "healthy" status
   ```

2. Restart backend after DB is ready:
   ```bash
   docker-compose restart backend
   ```

3. Check database credentials in `docker-compose.yml`

### Port Already in Use

**Windows**:
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

**macOS/Linux**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

**Alternative**: Change port in `docker-compose.yml`:
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Use 8001 instead of 8000
```

### Container Out of Memory

**Symptoms**:
- Container crashes during model loading
- "Killed" in logs

**Solutions**:
1. Increase Docker memory allocation:
   - **Docker Desktop**: Settings → Resources → Memory → 8GB
   - **Linux**: Edit `/etc/docker/daemon.json`

2. Use smaller model temporarily:
   ```yaml
   environment:
     - BERTIMBAU_MODEL=paraphrase-multilingual-MiniLM-L12-v2  # Smaller
   ```

### Hot Reload Not Working

**Backend** (Python):
1. Check volume mount in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./backend/src:/app/src:delegated
   ```

2. Verify `RELOAD=True` environment variable

**Frontend** (React):
1. Check volume mount:
   ```yaml
   volumes:
     - ./frontend/src:/app/src:delegated
   ```

2. Clear Vite cache:
   ```bash
   docker-compose exec frontend rm -rf node_modules/.vite
   docker-compose restart frontend
   ```

### Database Data Persists After `docker-compose down`

**This is intentional** (volumes persist):
```bash
# To remove data (CAUTION: irreversible)
docker-compose down -v
```

**To keep code but reset database**:
```bash
# Remove only database volume
docker volume rm net-est-web_postgres-data
```

---

## Advanced Usage

### Running Backend Only

```bash
cd backend
docker-compose up
```

**Access**:
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Adminer: http://localhost:8080

### Running with Optional Tools

```bash
# Start with Adminer (DB GUI)
docker-compose --profile tools up -d
```

### Custom Environment Variables

1. Copy `.env.example`:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

2. Edit `.env` files with your settings

3. Restart services:
   ```bash
   docker-compose restart
   ```

### Production Mode (No Hot Reload)

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

**Note**: `docker-compose.prod.yml` not included yet (see deployment guide)

---

## Team Best Practices

### 1. Daily Workflow

**Start work**:
```bash
git pull origin main
docker-compose up -d
```

**End work**:
```bash
git add .
git commit -m "feat: implement sentence alignment"
git push origin feature/sentence-alignment
docker-compose down
```

### 2. Branch Workflow

**Create feature branch**:
```bash
git checkout -b feature/feedback-persistence
docker-compose up -d
```

**Merge to main**:
```bash
git checkout main
git pull origin main
git merge feature/feedback-persistence
git push origin main
```

### 3. Dependency Updates

**Backend** (Poetry):
```bash
# Update pyproject.toml
cd backend
# Rebuild container
docker-compose build backend
docker-compose up -d backend
```

**Frontend** (pnpm):
```bash
# Update package.json
cd frontend
# Rebuild container
docker-compose build frontend
docker-compose up -d frontend
```

### 4. Database Migrations (Future)

**Create migration**:
```bash
docker-compose exec backend alembic revision --autogenerate -m "add feedback table"
```

**Apply migration**:
```bash
docker-compose exec backend alembic upgrade head
```

---

## Next Steps

Once your Docker environment is running:

1. **✅ Test the setup**: Visit http://localhost:8000/docs and try the health endpoint
2. **📚 Read the API docs**: Explore available endpoints in Swagger UI
3. **🧪 Run tests**: `docker-compose exec backend pytest`
4. **🔧 Start coding**: Edit files in `backend/src/` or `frontend/src/`
5. **📊 Check database**: Open http://localhost:8080 (Adminer)

For development roadmap, see:
- `docs/FRESH_START_ANALYSIS_2025-11-07.md` - Comprehensive analysis
- `DEVELOPMENT_ROADMAP.md` - Milestone breakdown (to be created)

---

## Getting Help

**Documentation**:
- Docker Compose: https://docs.docker.com/compose/
- FastAPI: https://fastapi.tiangolo.com/
- React + Vite: https://vitejs.dev/

**Logs**:
```bash
# Save logs to file for debugging
docker-compose logs > debug.log
```

**Reset Everything** (nuclear option):
```bash
# Stop services
docker-compose down -v

# Remove all images
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
