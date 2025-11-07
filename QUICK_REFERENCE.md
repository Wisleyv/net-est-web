# NET-EST Quick Reference Card

**Last Updated**: November 7, 2025

---

## 🚀 Quick Start (< 5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/Wisleyv/net-est-web.git
cd net-est-web

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be healthy (~60 seconds)
docker-compose ps

# 4. Access services
# Backend API: http://localhost:8000
# API Docs:    http://localhost:8000/docs
# Frontend:    http://localhost:3000
# DB Admin:    http://localhost:8080 (login: netest / netest_dev_password)
```

---

## 📁 Project Structure

```
net-est-web/
├── backend/                    # Python/FastAPI backend
│   ├── src/                    # Source code
│   │   ├── api/                # API endpoints
│   │   ├── services/           # Business logic
│   │   ├── models/             # Data models
│   │   └── strategies/         # Strategy detectors
│   ├── tests/                  # Pytest tests
│   ├── Dockerfile.new          # Docker image
│   ├── docker-compose.yml      # Backend-only services
│   └── pyproject.toml          # Poetry dependencies
├── frontend/                   # React/Vite frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # React Query hooks
│   │   ├── services/           # API client
│   │   └── stores/             # Zustand state
│   ├── Dockerfile              # Docker image
│   └── package.json            # pnpm dependencies
├── docker-compose.yml          # Full stack services
├── .devcontainer/              # Codespaces config
└── docs/                       # Documentation
```

---

## 🐳 Docker Commands

### Start/Stop Services

```bash
# Start all (backend + frontend + database)
docker-compose up -d

# Start backend only
cd backend && docker-compose up -d

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove data (CAUTION: deletes database)
docker-compose down -v
```

### Development Workflow

```bash
# Rebuild after dependency changes
docker-compose build backend
docker-compose up -d backend

# Run tests
docker-compose exec backend pytest -v
docker-compose exec frontend pnpm test

# Access database
docker-compose exec postgres psql -U netest -d netest_dev

# Access Redis
docker-compose exec redis redis-cli

# View service status
docker-compose ps
```

---

## 🧪 Testing

### Backend (pytest)

```bash
# Run all tests
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=src --cov-report=term-missing

# Specific test file
docker-compose exec backend pytest tests/unit/test_alignment.py

# Specific test
docker-compose exec backend pytest tests/unit/test_alignment.py::test_paragraph_alignment
```

### Frontend (vitest)

```bash
# Run all tests
docker-compose exec frontend pnpm test

# Watch mode
docker-compose exec frontend pnpm test:watch

# Coverage
docker-compose exec frontend pnpm test:coverage
```

---

## 📡 API Endpoints

**Base URL**: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/semantic-alignment/` | POST | Align paragraphs & sentences |
| `/api/v1/features/` | POST | Extract linguistic features |
| `/api/v1/comparative-analysis/` | POST | Detect simplification strategies |
| `/api/v1/feedback/` | POST | Submit human corrections |
| `/api/v1/analytics/report/{id}` | GET | Generate PDF report |
| `/docs` | GET | Swagger UI (interactive docs) |

**Example Request** (comparative analysis):
```bash
curl -X POST http://localhost:8000/api/v1/comparative-analysis/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "O médico utilizou terminologia técnica.",
    "target_text": "O médico usou palavras simples."
  }'
```

**Example Response**:
```json
{
  "strategies": [
    {
      "strategy_tag": "SL+",
      "confidence": 0.85,
      "evidence": [
        {
          "type": "lexical",
          "description": "Synonym: 'utilizou' → 'usou'",
          "confidence": 0.9
        }
      ]
    }
  ]
}
```

---

## 🔧 Common Issues & Solutions

### Port Already in Use

**Symptoms**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
services:
  backend:
    ports:
      - "8001:8000"  # Use 8001 instead
```

### Hot Reload Not Working

**Symptoms**: Code changes don't trigger restart

**Solution**:
```bash
# Check volume mounts in docker-compose.yml
volumes:
  - ./backend/src:/app/src:delegated  # Should be present

# Restart service
docker-compose restart backend
```

### Container Out of Memory

**Symptoms**: Container crashes during model loading

**Solution**:
```bash
# Increase Docker memory (Docker Desktop → Settings → Resources)
# Minimum: 4GB, Recommended: 8GB

# Or use smaller model temporarily
BERTIMBAU_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

### Database Connection Errors

**Symptoms**: `connection refused` in backend logs

**Solution**:
```bash
# Wait for PostgreSQL to be healthy
docker-compose ps postgres  # Should show "healthy"

# Restart backend after DB is ready
docker-compose restart backend
```

---

## 📊 Simplification Strategies (Taxonomy)

| Tag | Strategy | Description | Example |
|-----|----------|-------------|---------|
| **SL+** | Lexical Substitution | Replace complex word with simpler synonym | "utilizar" → "usar" |
| **RP+** | Paraphrase | Rewrite with different words, same meaning | "devido ao fato de" → "porque" |
| **RF+** | Sentence Splitting | Split long sentence into multiple shorter ones | "A, B e C" → "A. B. C." |
| **RD+** | Content Reduction | Remove non-essential information | Delete subordinate clauses |
| **MOD+** | Modalization | Change modality (imperative → indicative) | "Faça!" → "Você pode fazer" |
| **DL+** | Discourse Labels | Add connectives for clarity | Insert "portanto", "assim" |
| **EXP+** | Explanatory Insertion | Add definitions or explanations | "X (isto é, Y)" |
| **IN+** | Inversion | Change word order | Passive → Active voice |
| **MT+** | Metaphor | Literal paraphrase of metaphor | "Correr contra o tempo" → "ter pressa" |
| **OM+** | Omission | Delete information (manual only) | N/A (not auto-detected) |
| **PRO+** | Pronoun | Pronoun substitution (manual only) | N/A (not auto-detected) |

**Note**: `OM+` and `PRO+` are human-annotated only (not auto-detected).

---

## 🌍 Environment Variables

### Backend (`.env`)

```bash
# Copy from template
cp backend/.env.example backend/.env

# Key variables
DATABASE_URL=postgresql+asyncpg://netest:netest_dev_password@postgres:5432/netest_dev
REDIS_URL=redis://redis:6379/0
BERTIMBAU_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (`.env`)

```bash
# Copy from template
cp frontend/.env.example frontend/.env

# Key variables
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `DOCKER_SETUP_GUIDE.md` | Detailed setup instructions (all platforms) |
| `DEVELOPMENT_ROADMAP.md` | 8-milestone implementation plan |
| `docs/FRESH_START_ANALYSIS_2025-11-07.md` | Comprehensive codebase analysis |
| `ARCHITECTURE.md` | System architecture |
| `docs/tabela_est.md` | Strategy taxonomy (Portuguese) |
| `.github/copilot-instructions.md` | AI coding agent guidance |

---

## 🎯 Current Status (November 7, 2025)

- ✅ **M0: Docker Environment** - COMPLETE
- 🔜 **M1: Project Foundation** - NEXT (Poetry, clean architecture, health check)
- ⏳ **M2: Hierarchical Alignment** - Pending (paragraph/sentence alignment)
- ⏳ **M3-M8** - See `DEVELOPMENT_ROADMAP.md`

---

## 🤝 Team Workflow

### Daily Development

```bash
# 1. Pull latest changes
git pull origin main

# 2. Start services
docker-compose up -d

# 3. Make changes (backend/src or frontend/src)
# Changes auto-reload (hot reload enabled)

# 4. Run tests
docker-compose exec backend pytest
docker-compose exec frontend pnpm test

# 5. Commit and push
git add .
git commit -m "feat: implement sentence alignment"
git push origin feature/sentence-alignment

# 6. Stop services (optional)
docker-compose down
```

### Creating Feature Branch

```bash
# Create and checkout branch
git checkout -b feature/feedback-persistence

# Start development
docker-compose up -d

# Merge to main (after PR approval)
git checkout main
git pull origin main
git merge feature/feedback-persistence
git push origin main
```

---

## 🆘 Getting Help

**Documentation**: See `docs/` folder
**Issues**: GitHub Issues (tag with milestone M1, M2, etc.)
**Discussions**: GitHub Discussions
**Email**: (add team email here)

---

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
