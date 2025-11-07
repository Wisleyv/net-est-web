# NET-EST Development Roadmap (Fresh Start)

**Date**: November 7, 2025  
**Status**: Docker environment established → Implementation phase begins  
**Timeline**: 14 weeks (3.5 months)

---

## Implementation Status

| Milestone | Status | Priority | Est. Effort |
|-----------|--------|----------|-------------|
| **M0: Docker Environment** | ✅ **COMPLETE** | Critical | 1 week |
| **M1: Project Foundation** | 🔜 **NEXT** | Critical | 1 week |
| **M2: Hierarchical Alignment** | ⏳ Pending | High | 2 weeks |
| **M3: Multi-Level Features** | ⏳ Pending | High | 2 weeks |
| **M4: Evidence-Based Detection** | ⏳ Pending | Critical | 2 weeks |
| **M5: Feedback System** | ⏳ Pending | Medium | 2 weeks |
| **M6: Analytics & Reporting** | ⏳ Pending | Medium | 1 week |
| **M7: Production Deployment** | ⏳ Pending | High | 2 weeks |
| **M8: ML Training Pipeline** | ⏳ Pending | Low | 1 week |

---

## M0: Docker Environment ✅ COMPLETE (Week 1)

**Goal**: Establish consistent multi-platform development environment

**Deliverables**:
- ✅ **Backend Dockerfile** (`backend/Dockerfile.new`)
  - Multi-stage build (development + production)
  - ML model preloading (mpnet-base-v2)
  - Health checks
  
- ✅ **Frontend Dockerfile** (`frontend/Dockerfile`)
  - Development mode (Vite HMR)
  - Production mode (nginx)
  
- ✅ **Docker Compose** (`docker-compose.yml`)
  - Backend (FastAPI + mpnet)
  - Frontend (React + Vite)
  - PostgreSQL (persistent data)
  - Redis (caching)
  - Adminer (DB admin UI)
  
- ✅ **Devcontainer** (`.devcontainer/devcontainer.json`)
  - GitHub Codespaces auto-configuration
  - VS Code extensions
  - Port forwarding
  
- ✅ **Environment Templates**
  - `backend/.env.example`
  - `frontend/.env.example`
  
- ✅ **Setup Guide** (`DOCKER_SETUP_GUIDE.md`)
  - Quick start (all platforms)
  - Platform-specific instructions
  - Troubleshooting guide

**Next Action**: Start Milestone 1

---

## M1: Project Foundation 🔜 NEXT (Week 2)

**Goal**: Establish clean architecture and foundational services

### Backend Tasks

#### 1.1 Poetry Migration
```bash
cd backend

# Install Poetry
pip install poetry==1.8.3

# Initialize from pyproject.toml (already created)
poetry install

# Verify lockfile generated
ls poetry.lock
```

**Files**:
- ✅ `pyproject.toml` (already updated)
- ⏳ `poetry.lock` (generate)
- ⏳ Remove `requirements.txt` (legacy)

#### 1.2 Clean Package Structure
```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Pydantic settings
│   │   └── feature_flags.py       # YAML-based flags
│   ├── models/
│   │   ├── __init__.py
│   │   ├── domain.py              # Domain models (Text, Strategy, Evidence)
│   │   ├── database.py            # SQLAlchemy models
│   │   └── schemas.py             # Pydantic API schemas
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          # Async session factory
│   │   └── repository.py          # Base repository pattern
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ml_model_service.py    # Model loading & caching
│   │   └── cache_service.py       # Redis abstraction
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependency injection
│   │   ├── health.py              # Health check endpoint
│   │   └── v1/
│   │       └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py             # Structlog setup
│       └── errors.py              # Custom exceptions
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   ├── unit/
│   │   └── test_ml_model_service.py
│   └── integration/
│       └── test_health_endpoint.py
├── alembic/                       # Database migrations
│   ├── env.py
│   └── versions/
├── Dockerfile.new
├── docker-compose.yml
├── pyproject.toml
└── poetry.lock
```

**Key Files to Create**:

1. **src/main.py** (FastAPI app):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.api.health import router as health_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    # Initialize ML models, database, cache
    pass

@app.on_event("shutdown")
async def shutdown():
    # Cleanup resources
    pass
```

2. **src/config/settings.py** (Pydantic settings):
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App
    APP_NAME: str = "NET-EST API"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    ENABLE_REDIS_CACHE: bool = True
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # ML Models
    BERTIMBAU_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    SIMILARITY_THRESHOLD: float = 0.5

settings = Settings()
```

3. **src/api/health.py** (health check):
```python
from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    return HealthResponse(status="ok", version="2.0.0")
```

4. **Database Setup** (Alembic):
```bash
# Initialize Alembic
docker-compose exec backend alembic init alembic

# Create first migration
docker-compose exec backend alembic revision --autogenerate -m "initial schema"

# Apply migration
docker-compose exec backend alembic upgrade head
```

#### 1.3 Testing Infrastructure

**conftest.py**:
```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_ml_model():
    # Mock SentenceTransformer to avoid loading in tests
    pass
```

**test_health_endpoint.py**:
```python
def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

**Run tests**:
```bash
docker-compose exec backend pytest -v
```

### Frontend Tasks

#### 1.4 React 19 + Vite 6 Upgrade

**Current** (from existing package.json):
- React 18.2.0 → React 19
- Vite 5.0.11 → Vite 6
- Zustand 4.4.5 → Zustand 5
- Remove duplicate `react-query` (v3.39.3)
- Keep `@tanstack/react-query` (5.85.6) → upgrade to v6

**Steps**:
```bash
cd frontend

# Remove duplicate
pnpm remove react-query

# Upgrade major versions
pnpm add react@19 react-dom@19
pnpm add -D vite@6
pnpm add zustand@5
pnpm add @tanstack/react-query@6
pnpm add axios@1.7.9  # Fix invalid version

# Verify
pnpm install
pnpm dev  # Test hot reload
```

#### 1.5 API Client Refactor

**src/services/api.js** (clean up for React Query):
```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (handle FormData)
apiClient.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']; // Let browser set boundary
  }
  return config;
});

// Response interceptor (error handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
```

**src/hooks/useHealthCheck.js** (React Query example):
```javascript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/health');
      return data;
    },
    refetchInterval: 30000, // Poll every 30s
  });
};
```

### Deliverables (M1)

- ✅ Poetry dependency management (lockfile)
- ✅ Clean package structure (installable with `pip install -e .`)
- ✅ Pydantic settings (12-factor app)
- ✅ Health check endpoint (`/api/v1/health`)
- ✅ Database connection (async SQLAlchemy + Alembic)
- ✅ Redis connection (async cache service)
- ✅ Structlog logging (JSON output)
- ✅ pytest infrastructure (unit + integration tests)
- ✅ React 19 + Vite 6 upgrade
- ✅ API client refactor (FormData-aware)
- ✅ React Query hooks (health check example)

**Validation**:
```bash
# Backend
docker-compose exec backend pytest -v
curl http://localhost:8000/api/v1/health

# Frontend
curl http://localhost:3000
# Should see React app with health status indicator
```

---

## M2: Hierarchical Alignment (Weeks 3-4)

**Goal**: Implement paragraph, sentence, and token-level alignment

### Backend Tasks

#### 2.1 Preprocessing Service

**src/services/preprocessing_service.py**:
- Normalize Unicode (NFKC)
- Detect language (Portuguese validation)
- Split paragraphs (newline-based)
- Tokenize sentences (spaCy `pt_core_news_sm`)
- Tokenize words (spaCy)

**Key Functions**:
```python
class PreprocessingService:
    def normalize_text(self, text: str) -> str
    def split_paragraphs(self, text: str) -> list[str]
    def split_sentences(self, paragraph: str) -> list[str]
    def tokenize(self, sentence: str) -> list[str]
```

#### 2.2 Semantic Alignment Service

**src/services/alignment_service.py**:
- Load mpnet model (cached)
- Encode paragraphs → embeddings
- Compute cosine similarity matrix
- Map source paragraphs → target paragraphs (greedy matching)
- Align sentences within matched paragraphs
- Detect splits/merges

**Models**:
```python
@dataclass
class AlignmentPair:
    source_idx: int
    target_idx: int
    similarity: float
    alignment_type: str  # "one-to-one", "split", "merge"

class AlignmentService:
    def align_paragraphs(
        self, 
        source_paras: list[str], 
        target_paras: list[str]
    ) -> list[AlignmentPair]
    
    def align_sentences(
        self, 
        source_sents: list[str], 
        target_sents: list[str]
    ) -> list[AlignmentPair]
```

#### 2.3 API Endpoint

**src/api/v1/alignment.py**:
```python
@router.post("/semantic-alignment/", response_model=AlignmentResponse)
async def semantic_alignment(
    request: AlignmentRequest,
    alignment_service: AlignmentService = Depends()
):
    # Preprocess
    source_paras = preprocessing.split_paragraphs(request.source_text)
    target_paras = preprocessing.split_paragraphs(request.target_text)
    
    # Align paragraphs
    para_pairs = alignment_service.align_paragraphs(source_paras, target_paras)
    
    # Align sentences within each paragraph pair
    for pair in para_pairs:
        source_sents = preprocessing.split_sentences(source_paras[pair.source_idx])
        target_sents = preprocessing.split_sentences(target_paras[pair.target_idx])
        pair.sentence_alignments = alignment_service.align_sentences(source_sents, target_sents)
    
    return AlignmentResponse(alignments=para_pairs)
```

### Frontend Tasks

#### 2.4 Alignment Visualization

**Component**: `src/components/AlignmentVisualization.jsx`
- Side-by-side paragraph display
- Color-coded similarity scores (green=high, yellow=medium, red=low)
- Expandable sentence-level view
- Interactive highlighting (hover source → highlight target)

### Deliverables (M2)

- ✅ Preprocessing service (paragraphs, sentences, tokens)
- ✅ Paragraph alignment (mpnet embeddings + cosine similarity)
- ✅ Sentence alignment (within matched paragraphs)
- ✅ Split/merge detection (one-to-many, many-to-one)
- ✅ API endpoint (`/api/v1/semantic-alignment/`)
- ✅ Alignment visualization (frontend component)
- ✅ Unit tests (alignment accuracy)
- ✅ Integration tests (API contract)

**Validation**:
```bash
# Test paragraph alignment
curl -X POST http://localhost:8000/api/v1/semantic-alignment/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Parágrafo 1 complexo.\nParágrafo 2 técnico.",
    "target_text": "Parágrafo 1 simplificado.\nParágrafo 2 acessível."
  }'
# Should return aligned paragraph pairs with similarity scores
```

---

## M3: Multi-Level Features (Weeks 5-6)

**Goal**: Extract linguistic features at paragraph, sentence, and token levels

### Backend Tasks

#### 3.1 Feature Extraction Service

**src/services/feature_extraction_service.py**:

**Paragraph-Level Features**:
- Length (characters, words, sentences)
- Average sentence length
- Lexical diversity (type-token ratio)
- Readability (Flesch-Kincaid, Coleman-Liau)

**Sentence-Level Features**:
- Length (characters, words)
- POS tag distribution (spaCy)
- Dependency tree depth (spaCy)
- Named entities (spaCy)
- Syntactic complexity (subordinate clauses)

**Token-Level Features**:
- Word frequency (UFRJ corpus or Portuguese word lists)
- Word length
- POS tag (noun, verb, adjective, etc.)
- Lemma (base form)
- Morphological features (number, gender, tense)

**Models**:
```python
@dataclass
class ParagraphFeatures:
    char_count: int
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    lexical_diversity: float
    flesch_kincaid: float

@dataclass
class SentenceFeatures:
    char_count: int
    word_count: int
    pos_distribution: dict[str, int]  # {"NOUN": 5, "VERB": 3, ...}
    dependency_depth: int
    named_entities: list[str]
    has_subordinate_clause: bool

@dataclass
class TokenFeatures:
    text: str
    lemma: str
    pos: str
    frequency_rank: int  # Lower = more common
    is_stopword: bool
    
class FeatureExtractionService:
    def extract_paragraph_features(self, text: str) -> ParagraphFeatures
    def extract_sentence_features(self, sentence: str) -> SentenceFeatures
    def extract_token_features(self, tokens: list[str]) -> list[TokenFeatures]
```

#### 3.2 Feature Comparison

**src/services/feature_comparison_service.py**:
- Compare source vs target features
- Compute deltas (absolute & relative)
- Detect significant changes (thresholds)

**Example**:
```python
@dataclass
class FeatureDelta:
    feature_name: str
    source_value: float
    target_value: float
    absolute_delta: float
    relative_delta: float  # Percentage
    is_significant: bool  # |delta| > threshold

class FeatureComparisonService:
    def compare_paragraphs(
        self, 
        source_features: ParagraphFeatures, 
        target_features: ParagraphFeatures
    ) -> list[FeatureDelta]
```

### Frontend Tasks

#### 3.3 Feature Dashboard

**Component**: `src/components/FeatureDashboard.jsx`
- Tabbed interface (Paragraph / Sentence / Token)
- Side-by-side feature comparison (source vs target)
- Delta visualization (bar charts, color-coded)
- Drill-down to sentence/token details

### Deliverables (M3)

- ✅ Paragraph features (length, diversity, readability)
- ✅ Sentence features (POS, syntax, entities)
- ✅ Token features (frequency, lemma, POS)
- ✅ Feature comparison (deltas, thresholds)
- ✅ API endpoint (`/api/v1/features/`)
- ✅ Feature dashboard (frontend)
- ✅ Unit tests (feature extraction accuracy)

---

## M4: Evidence-Based Detection (Weeks 7-8)

**Goal**: Implement modular strategy detection with explainable evidence

### Backend Tasks

#### 4.1 Strategy Detector Interface

**src/strategies/base.py**:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Evidence:
    """Supporting evidence for strategy detection"""
    type: str  # "lexical", "syntactic", "semantic"
    description: str
    source_text: str
    target_text: str
    confidence: float

@dataclass
class StrategyDetectionResult:
    strategy_tag: str  # "SL+", "RP+", etc.
    confidence: float  # 0.0-1.0
    evidence: list[Evidence]
    rule_id: str  # e.g., "SL001_synonym_replacement"

class BaseStrategyDetector(ABC):
    @abstractmethod
    def detect(
        self, 
        source_features: dict, 
        target_features: dict,
        alignment: AlignmentPair
    ) -> list[StrategyDetectionResult]:
        """Detect strategy with evidence"""
        pass
```

#### 4.2 Individual Strategy Detectors

**SL+ (Lexical Substitution)**:
```python
class LexicalSubstitutionDetector(BaseStrategyDetector):
    def detect(self, source_features, target_features, alignment):
        # Rule SL001: Synonym replacement (high-freq word replaces low-freq)
        source_tokens = source_features.tokens
        target_tokens = target_features.tokens
        
        substitutions = []
        for s_token, t_token in zip(source_tokens, target_tokens):
            if s_token.lemma != t_token.lemma:  # Different words
                if t_token.frequency_rank < s_token.frequency_rank:  # Simpler
                    substitutions.append(
                        Evidence(
                            type="lexical",
                            description=f"Synonym: '{s_token.text}' → '{t_token.text}'",
                            source_text=s_token.text,
                            target_text=t_token.text,
                            confidence=0.8
                        )
                    )
        
        if substitutions:
            return [StrategyDetectionResult(
                strategy_tag="SL+",
                confidence=min(1.0, len(substitutions) * 0.2),
                evidence=substitutions,
                rule_id="SL001_synonym_replacement"
            )]
        return []
```

**RP+ (Paraphrase)**:
- Detect semantic similarity (embedding cosine > threshold)
- Lexical overlap < 50% (different words, same meaning)

**RF+ (Sentence Splitting)**:
- One source sentence → multiple target sentences
- Detect coordinating conjunctions removal ("e", "mas")

**RD+ (Content Reduction)**:
- Compare word counts (source > target)
- Detect clause deletion (subordinate clauses removed)

**MOD+ (Modalization)**:
- Detect modal verb changes (imperativo → indicativo)
- Detect hedging additions ("talvez", "possivelmente")

**EXP+ (Explanatory Insertion)**:
- Detect parenthetical additions
- Detect definition insertions (X-bar theory: "Y (isto é, Z)")

**IN+ (Inversion)**:
- Detect word order changes (subject-verb → verb-subject)
- Detect passive → active voice

**MT+ (Metaphor)**:
- Detect metaphoric → literal (requires semantic knowledge base)

#### 4.3 Orchestrator

**src/services/strategy_orchestrator.py**:
```python
class StrategyOrchestrator:
    def __init__(self):
        self.detectors = [
            LexicalSubstitutionDetector(),
            ParaphraseDetector(),
            SentenceSplittingDetector(),
            ContentReductionDetector(),
            ModalizationDetector(),
            ExplanatoryInsertionDetector(),
            InversionDetector(),
            # MT+ disabled (requires manual annotation)
        ]
    
    def detect_all(
        self, 
        alignment: AlignmentPair,
        source_features: dict,
        target_features: dict
    ) -> list[StrategyDetectionResult]:
        results = []
        for detector in self.detectors:
            results.extend(detector.detect(source_features, target_features, alignment))
        return results
```

#### 4.4 Confidence Engine

**src/services/confidence_engine.py**:
- Aggregate evidence from multiple rules
- Weight by evidence type (semantic > syntactic > lexical)
- Normalize confidence scores (0.0-1.0)
- Explain confidence (JSON with evidence breakdown)

### Frontend Tasks

#### 4.5 Strategy Results Display

**Component**: `src/components/StrategyResults.jsx`
- Strategy tag badges (color-coded)
- Confidence meter (0-100%)
- Evidence list (expandable)
- Inline highlighting (hover evidence → highlight text)

### Deliverables (M4)

- ✅ Base strategy detector interface
- ✅ 7 strategy detectors (SL+, RP+, RF+, RD+, MOD+, EXP+, IN+)
- ✅ Strategy orchestrator (run all detectors)
- ✅ Confidence engine (explainable scores)
- ✅ API endpoint (`/api/v1/comparative-analysis/`)
- ✅ Strategy results display (frontend)
- ✅ Unit tests (rule accuracy)
- ✅ Integration tests (end-to-end)

**Validation**:
```bash
# Test comparative analysis
curl -X POST http://localhost:8000/api/v1/comparative-analysis/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "O médico utilizou terminologia técnica.",
    "target_text": "O médico usou palavras simples."
  }'
# Should return: [{"strategy_tag": "SL+", "confidence": 0.8, "evidence": [...]}]
```

---

## M5: Feedback System (Weeks 9-10)

**Goal**: Capture human corrections for future ML training

### Backend Tasks

#### 5.1 Database Schema

**Alembic migration**:
```sql
CREATE TABLE feedback_events (
    id UUID PRIMARY KEY,
    session_id VARCHAR(50),
    source_text TEXT NOT NULL,
    target_text TEXT NOT NULL,
    predicted_strategies JSONB,  -- AI prediction
    corrected_strategies JSONB,  -- Human correction
    user_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_feedback_session ON feedback_events(session_id);
CREATE INDEX idx_feedback_created ON feedback_events(created_at);
```

#### 5.2 Feedback Service

**src/services/feedback_service.py**:
```python
class FeedbackService:
    async def save_feedback(
        self,
        session_id: str,
        source_text: str,
        target_text: str,
        predicted_strategies: list[dict],
        corrected_strategies: list[dict],
        user_notes: str | None
    ) -> UUID:
        # Save to PostgreSQL
        # Return feedback ID
        pass
    
    async def export_training_data(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> bytes:
        # Export as JSON for ML training
        pass
```

#### 5.3 API Endpoint

**src/api/v1/feedback.py**:
```python
@router.post("/feedback/", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    feedback_service: FeedbackService = Depends()
):
    feedback_id = await feedback_service.save_feedback(
        session_id=request.session_id,
        source_text=request.source_text,
        target_text=request.target_text,
        predicted_strategies=request.predicted_strategies,
        corrected_strategies=request.corrected_strategies,
        user_notes=request.user_notes
    )
    return FeedbackResponse(feedback_id=feedback_id)

@router.get("/feedback/export/")
async def export_feedback(
    start_date: datetime,
    end_date: datetime,
    feedback_service: FeedbackService = Depends()
):
    # Return JSON file
    pass
```

### Frontend Tasks

#### 5.4 Feedback UI

**Component**: `src/components/FeedbackPanel.jsx`
- Edit detected strategies (add/remove tags)
- Adjust confidence scores
- Add notes (explain correction)
- Submit button (save to backend)

### Deliverables (M5)

- ✅ Feedback database schema (PostgreSQL)
- ✅ Feedback service (save, export)
- ✅ API endpoints (`/api/v1/feedback/`, `/api/v1/feedback/export/`)
- ✅ Feedback UI (edit strategies, submit)
- ✅ Export training data (JSON format)
- ✅ Integration tests (feedback workflow)

---

## M6: Analytics & Reporting (Week 11)

**Goal**: Generate analysis reports and aggregate statistics

### Backend Tasks

#### 6.1 Analytics Service

**src/services/analytics_service.py**:
```python
class AnalyticsService:
    async def get_session_stats(self, session_id: str) -> dict:
        # Total analyses run
        # Most common strategies
        # Average confidence
        pass
    
    async def generate_report(
        self, 
        analysis_id: str
    ) -> bytes:
        # PDF report with:
        # - Alignment visualization
        # - Feature comparison tables
        # - Strategy detection summary
        # - Evidence breakdown
        pass
```

#### 6.2 Report Generation

**Library**: `reportlab` (PDF) or `weasyprint` (HTML→PDF)

**Template**:
- Header (source/target metadata)
- Alignment section (paragraph pairs)
- Feature comparison (tables, charts)
- Strategy summary (tag frequencies, confidence histogram)
- Evidence appendix (detailed breakdowns)

### Frontend Tasks

#### 6.3 Export UI

**Component**: `src/components/ExportButton.jsx`
- Export formats (JSON, CSV, PDF)
- Download button

### Deliverables (M6)

- ✅ Analytics service (session stats)
- ✅ Report generation (PDF)
- ✅ API endpoint (`/api/v1/analytics/report/{analysis_id}`)
- ✅ Export UI (download button)

---

## M7: Production Deployment (Weeks 12-13)

**Goal**: Deploy to Railway (backend) + Vercel (frontend)

### Backend Tasks

#### 7.1 Railway Deployment

**Steps**:
1. Create Railway project
2. Add PostgreSQL (Neon free tier)
3. Add Redis (Upstash free tier)
4. Deploy backend from GitHub
5. Configure environment variables
6. Run database migrations

**Railway Configuration** (`railway.toml`):
```toml
[build]
builder = "dockerfile"
dockerfilePath = "backend/Dockerfile.new"

[deploy]
startCommand = "uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 2"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 10
restartPolicyType = "on-failure"
```

#### 7.2 Environment Variables (Production)

```bash
# Railway environment variables
DATABASE_URL=postgresql+asyncpg://...  # Neon connection string
REDIS_URL=rediss://...  # Upstash connection string
ALLOWED_ORIGINS=https://netest.vercel.app
DEBUG=False
LOG_LEVEL=INFO
```

### Frontend Tasks

#### 7.3 Vercel Deployment

**Steps**:
1. Connect GitHub repository
2. Configure build command: `pnpm build`
3. Configure output directory: `dist`
4. Set environment variables:
   ```
   VITE_API_BASE_URL=https://netest-backend.up.railway.app
   ```

**Vercel Configuration** (`vercel.json`):
```json
{
  "buildCommand": "cd frontend && pnpm install && pnpm build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### CI/CD

#### 7.4 GitHub Actions

**Backend CI** (`.github/workflows/backend-ci.yml`):
```yaml
name: Backend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
  pull_request:
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: cd backend && poetry install
      - name: Run tests
        run: cd backend && poetry run pytest
      - name: Run linting
        run: cd backend && poetry run ruff check src/
```

**Frontend CI** (`.github/workflows/frontend-ci.yml`):
```yaml
name: Frontend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
  pull_request:
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml
      - name: Install dependencies
        run: cd frontend && pnpm install
      - name: Run tests
        run: cd frontend && pnpm test
      - name: Build
        run: cd frontend && pnpm build
```

### Deliverables (M7)

- ✅ Railway backend deployment
- ✅ Vercel frontend deployment
- ✅ GitHub Actions CI/CD
- ✅ Production environment variables
- ✅ Health checks & monitoring
- ✅ Database migrations (Alembic)

---

## M8: ML Training Pipeline (Week 14)

**Goal**: Prepare infrastructure for supervised learning (future)

### Backend Tasks

#### 8.1 Training Data Preparation

**Script**: `scripts/prepare_training_data.py`
```python
# Fetch feedback events from database
# Convert to ML training format:
# {
#   "source_text": "...",
#   "target_text": "...",
#   "features": {...},
#   "labels": ["SL+", "RP+"]
# }
# Export as JSONL (one example per line)
```

#### 8.2 Model Training (Placeholder)

**Future work** (not implemented in M8):
- Fine-tune BERTimbau for multi-label classification
- Train on corrected feedback data
- Evaluate on held-out test set
- Deploy as API endpoint

**Documentation**:
- `docs/ML_TRAINING_GUIDE.md` (placeholder)
- Instructions for future researchers

### Deliverables (M8)

- ✅ Training data export script
- ✅ Documentation (ML training guide)
- ⏳ Model training (future work, not implemented)

---

## Success Metrics

**Technical**:
- ✅ Docker Compose starts in < 2 minutes
- ✅ Backend health check responds in < 100ms
- ✅ Frontend loads in < 3 seconds
- ✅ API response time < 5 seconds (mpnet analysis)
- ✅ Test coverage > 80% (backend)
- ✅ Zero critical security vulnerabilities

**Functional**:
- ✅ Paragraph alignment accuracy > 90% (manual validation)
- ✅ Strategy detection precision > 85% (vs human annotations)
- ✅ Feedback submission success rate > 99%
- ✅ Report generation success rate > 99%

**User Experience**:
- ✅ Onboarding time < 5 minutes (new developer)
- ✅ Zero port conflicts (Docker isolation)
- ✅ Hot reload works on all platforms
- ✅ Clear error messages (no stack traces in UI)

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **ML model timeout** | Medium | High | Use mpnet (278MB), implement 60s timeout, fallback to heuristics |
| **Database migration failure** | Low | High | Test migrations in staging, backup before production deploy |
| **Team onboarding friction** | Medium | Medium | Comprehensive setup guide, Docker Compose automation |
| **Strategy detection accuracy** | High | High | Human-in-the-loop validation, feedback system, iterative rule tuning |
| **Port conflicts (local dev)** | Low | Low | Docker Compose handles port mapping |
| **Dependency version drift** | Medium | Medium | Poetry lockfile, Dependabot, CI checks |

---

## Post-Launch Maintenance

**Weekly**:
- Review feedback submissions
- Triage bug reports
- Monitor Railway/Vercel usage

**Monthly**:
- Update dependencies (Dependabot PRs)
- Review analytics (most common strategies)
- Refine detection rules based on feedback

**Quarterly**:
- Evaluate ML model training (if sufficient feedback data)
- Research new NLP models (Portuguese SOTA)
- User interviews (academic team)

---

## Getting Help

**Documentation**:
- `DOCKER_SETUP_GUIDE.md` - Development environment
- `docs/FRESH_START_ANALYSIS_2025-11-07.md` - Architecture analysis
- `ARCHITECTURE.md` - System design

**Issues**:
- GitHub Issues: Tag with milestone (M1, M2, etc.)
- Discussions: Use GitHub Discussions for questions

**Team Communication**:
- Weekly sync: Review progress, unblock issues
- Async updates: GitHub PR comments, issue threads

---

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
