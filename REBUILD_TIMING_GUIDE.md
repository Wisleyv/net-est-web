# Container Rebuild Timing Guide

**Date**: November 7, 2025  
**Branch**: `fresh-start/docker-environment-2025-11-07`  
**Status**: Docker environment committed, rebuild pending

---

## ❓ When Codespaces Asks to Rebuild

You denied the rebuild request because we were in the middle of creating files. **Good call!** Here's when you should rebuild:

---

## 🟢 **SAFE TO REBUILD NOW** (Recommended Timing)

### Option A: Immediate Rebuild ⭐ **BEST CHOICE**
**When**: Right now (after this commit)

**Why**:
- ✅ All Docker files are committed and pushed
- ✅ Branch is backed up on GitHub
- ✅ No uncommitted work will be lost
- ✅ Fresh container will use new `.devcontainer/devcontainer.json`

**What Happens**:
1. Codespaces rebuilds container using `.devcontainer/devcontainer.json`
2. Auto-installs VS Code extensions (Python, Docker, GitLens, Copilot)
3. Auto-runs `postStartCommand`: `docker-compose up -d`
4. Services start automatically (backend, frontend, postgres, redis)
5. Ports auto-forward (8000, 3000, 5432, 6379, 8080)

**How to Trigger**:
```bash
# In Codespaces, press Cmd/Ctrl+Shift+P
# Type: "Codespaces: Rebuild Container"
# Select the command
```

**Expected Duration**: ~5-10 minutes
- Download base images (Python 3.12-slim, Node 22-alpine, Postgres, Redis)
- Install Poetry dependencies
- **Download ML model** (mpnet-base-v2, 278MB) ← This is the longest step
- Install pnpm dependencies
- Start all services

---

### Option B: Defer Until Testing Phase 🟡 **ACCEPTABLE**
**When**: After you've reviewed documentation (next 30 minutes)

**Why**:
- Review `DOCKER_SETUP_GUIDE.md` first
- Understand what will happen during rebuild
- Mentally prepare for 5-10 minute wait

**Action**:
1. Read `DOCKER_SETUP_GUIDE.md` (Quick Start section)
2. Read `DOCKER_SETUP_COMPLETE.md` (Next Steps section)
3. When ready, trigger rebuild (see above)

---

### Option C: After Branch Merge 🔴 **NOT RECOMMENDED**
**When**: After merging to `master`

**Why NOT**:
- You can't test the Docker environment before merging
- Risky: what if something doesn't work?
- Team can't validate on their machines first

---

## 🎯 **Recommended Action Plan**

### **Step 1: Rebuild Container Now** ⏰ **DO THIS NEXT**

```bash
# Trigger rebuild via VS Code Command Palette
Cmd/Ctrl+Shift+P → "Codespaces: Rebuild Container"
```

**What You'll See**:
```
Building codespace...
Starting container...
Running postCreateCommand...
Running postStartCommand... (docker-compose up -d)
✅ Container ready
```

---

### **Step 2: Verify Services Started** (After rebuild completes)

```bash
# Check service status
docker-compose ps

# Expected output:
# netest-backend    running  (healthy)
# netest-frontend   running
# netest-postgres   running  (healthy)
# netest-redis      running  (healthy)
```

**If services didn't start automatically**:
```bash
docker-compose up -d
```

---

### **Step 3: Access Services**

In Codespaces, ports should auto-forward. Check **PORTS** tab at bottom of VS Code:

| Port | Label | Visibility | URL |
|------|-------|------------|-----|
| 8000 | Backend API | Public | `https://8000-<workspace>.app.github.dev` |
| 3000 | Frontend | Public | `https://3000-<workspace>.app.github.dev` |
| 5432 | PostgreSQL | Private | localhost:5432 |
| 6379 | Redis | Private | localhost:6379 |
| 8080 | Adminer | Private | `https://8080-<workspace>.app.github.dev` |

**Test Backend**:
```bash
curl https://8000-$CODESPACE_NAME.app.github.dev/docs
# Should return HTML (Swagger UI)
```

**Test Frontend** (in browser):
```
https://3000-$CODESPACE_NAME.app.github.dev
```

---

### **Step 4: View Logs** (if issues occur)

```bash
# Backend logs (watch ML model download)
docker-compose logs -f backend

# Expected:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000

# Frontend logs
docker-compose logs -f frontend

# Expected:
# VITE ready in XXX ms
# ➜  Local:   http://localhost:3000/
```

---

## 🚨 **What If Rebuild Fails?**

### Scenario 1: Out of Memory
**Symptoms**: Container crashes during model download

**Solution**:
```bash
# Use smaller model temporarily
# Edit docker-compose.yml:
environment:
  - BERTIMBAU_MODEL=paraphrase-multilingual-MiniLM-L12-v2  # 118MB

# Rebuild
docker-compose build backend --no-cache
docker-compose up -d backend
```

---

### Scenario 2: Port Conflicts
**Symptoms**: "port already in use" error

**Solution**:
```bash
# Check what's using ports
lsof -i :8000
lsof -i :3000

# Kill processes or change ports in docker-compose.yml
```

---

### Scenario 3: Services Won't Start
**Symptoms**: `docker-compose ps` shows "Exit 1" or "Restarting"

**Solution**:
```bash
# Check logs for specific service
docker-compose logs backend

# Common fixes:
# 1. Database not ready → wait 30s, restart backend
docker-compose restart backend

# 2. Missing environment variable → check .env files
cat backend/.env.example
cp backend/.env.example backend/.env

# 3. Poetry lock issue → rebuild without cache
docker-compose build backend --no-cache
```

---

## 📋 **Rebuild Checklist**

Before triggering rebuild:
- [x] All Docker files committed (`git status` clean)
- [x] Branch pushed to GitHub (backup exists)
- [x] Documentation reviewed (optional but recommended)
- [ ] Ready to wait 5-10 minutes (grab coffee ☕)

After rebuild completes:
- [ ] `docker-compose ps` shows all services running
- [ ] Backend accessible at `https://8000-<workspace>.app.github.dev/docs`
- [ ] Frontend accessible at `https://3000-<workspace>.app.github.dev`
- [ ] No errors in `docker-compose logs`

---

## 🎓 **Learning Resources**

**If this is your first time with Docker Compose**:
1. Read `DOCKER_SETUP_GUIDE.md` → Quick Start section
2. Read `QUICK_REFERENCE.md` → Docker Commands section
3. Experiment: `docker-compose down`, `docker-compose up -d`, `docker-compose logs`

**If rebuild fails**:
1. Read `DOCKER_SETUP_GUIDE.md` → Troubleshooting section
2. Check `docker-compose logs` for error messages
3. Search error in documentation (Ctrl+F in guides)

---

## 🔄 **Switching Between Old and New Environments**

### Work in Docker Environment (New)
```bash
git checkout fresh-start/docker-environment-2025-11-07
docker-compose up -d
```

### Switch Back to Old Environment
```bash
# Stop Docker services
docker-compose down

# Switch to master
git checkout master

# Use old start method
cd backend
python start_optimized.py  # or npm run dev in frontend/
```

---

## ✅ **Final Recommendation**

**DO THIS NOW**:
1. ☕ Grab a coffee or tea (5-10 minute break coming)
2. 🔄 Trigger rebuild: `Cmd/Ctrl+Shift+P` → "Codespaces: Rebuild Container"
3. 🕐 Wait for completion (watch progress in terminal)
4. ✅ Verify services with `docker-compose ps`
5. 🌐 Test backend: `https://8000-<workspace>.app.github.dev/docs`
6. 🌐 Test frontend: `https://3000-<workspace>.app.github.dev`
7. 📝 Report any issues (check logs with `docker-compose logs`)

**If successful** → Proceed to Milestone 1 (see `DEVELOPMENT_ROADMAP.md`)  
**If issues** → Check `DOCKER_SETUP_GUIDE.md` → Troubleshooting section

---

Good luck! 🚀

---

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
