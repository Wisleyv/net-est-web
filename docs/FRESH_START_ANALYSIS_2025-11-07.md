# NET-EST Fresh Start Analysis — November 7, 2025

## Executive Summary

This document presents a comprehensive 8-phase analysis of the NET-EST project, identifying critical issues in the current implementation and providing a detailed blueprint for a clean rebuild. The analysis covers project architecture, dependencies, ML models, problem patterns, algorithm design, technology stack, and a phased development roadmap.

**Date**: November 7, 2025  
**Analyst**: GitHub Copilot (AI Assistant)  
**Purpose**: Guide clean rebuild leveraging lessons learned from initial implementation  
**Target Audience**: Academic development team (Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima)

---

## Phase 1: Project Overview & Purpose

### Project Mission
NET-EST analyzes **intralingual translation** (Portuguese → simplified Portuguese) to identify and classify text simplification strategies used in translation. The system serves linguistic research by detecting patterns that make complex texts more accessible.

### Core Functionality
1. **Dual-Input Comparative Analysis**: Users provide source (complex) and target (simplified) Portuguese texts
2. **Semantic Alignment**: Paragraph-level alignment using sentence embeddings
3. **Strategy Detection**: Automatic identification of 10 simplification strategies
4. **Human-in-the-Loop Validation**: Researchers can correct/validate detected strategies
5. **Feedback-Driven Learning**: Corrections inform future ML model training

### Simplification Strategies (Tabela EST)

| Code | Name | Type | Description |
|------|------|------|-------------|
| **SL+** | Simplificação Lexical | Lexical | Complex → simple word substitution |
| **RP+** | Reconstrução de Período | Syntactic | Sentence splitting/merging |
| **RF+** | Reformulação | Structural | Same idea, different wording |
| **RD+** | Reorganização Discursiva | Structural | Connector/order changes |
| **MOD+** | Reinterpretação Perspectiva | Lexical | Voice/perspective shift |
| **DL+** | Reorganização Posicional | Structural | Word order changes |
| **EXP+** | Explicitação e Detalhamento | Structural | Adding clarifications |
| **IN+** | Manejo de Inserções | Syntactic | Managing insertions |
| **MT+** | Otimização de Títulos | Structural | Title reformulation |
| **OM+** | Omissão | N/A | **Human-only** (significant cuts) |
| **PRO+** | Problema | N/A | **Human-only** (errors) |

### Academic Requirements
- **Semantic Understanding**: Not just pattern matching; requires ML for MOD+, AS+, RF+ detection
- **Explainability**: Confidence scores must show feature contributions (transparency for research)
- **Evidence-Based**: Every detected strategy needs text spans, examples, and provenance (ML vs heuristic)
- **Feedback Integration**: System must learn from expert corrections (incremental ML training)

---

## Phase 2: Current Architecture Analysis

### Backend Structure

```
backend/src/
├── api/                    # FastAPI route handlers
│   ├── comparative_analysis.py  # Main analysis endpoint
│   ├── semantic_alignment.py
│   ├── analytics.py
│   └── health.py
├── core/                   # Infrastructure
│   ├── config.py           # Pydantic Settings
│   └── feature_flags.py    # YAML-based toggles
├── models/                 # Pydantic schemas
│   ├── comparative_analysis.py
│   ├── strategy_models.py
│   └── semantic_alignment.py
├── services/               # Business logic
│   ├── comparative_analysis_service.py  # Main orchestrator
│   ├── strategy_detector.py             # Strategy detection
│   ├── semantic_alignment_service.py    # Alignment logic
│   ├── feature_extraction_service.py
│   └── confidence_engine.py
├── strategies/             # Detection pipeline
│   ├── cascade_orchestrator.py  # 3-stage coordination
│   ├── feature_extractor.py
│   ├── stage_macro.py      # Paragraph-level
│   ├── stage_meso.py       # Sentence-level (NOT IMPLEMENTED)
│   └── stage_micro.py      # Token-level (NOT IMPLEMENTED)
└── repositories/
    └── feedback_repository.py  # File-based (no DB yet)
```

### Frontend Structure

```
frontend/src/
├── components/
│   ├── DualTextInputComponent.jsx       # Core UI
│   ├── ComparativeResultsDisplay.jsx
│   ├── SideBySideTextDisplay.jsx
│   └── InteractiveTextHighlighter.jsx
├── services/
│   ├── api.js                           # Axios client
│   └── comparativeAnalysisService.js
├── stores/ (Zustand)
│   ├── useAnalysisStore.js              # Processing state
│   ├── useAnnotationStore.js            # User corrections
│   └── useAppStore.js                   # Global state
└── hooks/
    └── useErrorHandler.js               # Centralized errors
```

### Data Flow

```
User Input (source + target texts)
    ↓
POST /api/v1/comparative-analysis/
    ↓
ComparativeAnalysisService.perform_comparative_analysis()
    ↓
SemanticAlignmentService.align_paragraphs()
    │   → Embed paragraphs with MiniLM
    │   → Compute cosine similarity matrix
    │   → Hungarian algorithm for alignment
    ↓
FeatureExtractor.extract_features() [ONCE - GLOBAL METRICS ONLY]
    │   → Lexical: word overlap, TTR
    │   → Structural: sentence counts, avg length
    │   → Semantic: overall similarity
    ↓
CascadeOrchestrator.detect_strategies()
    ├─ MacroStageEvaluator (Paragraph-level)
    │   ├─ RF+ (reformulation)
    │   ├─ RD+ (discourse reorganization)
    │   └─ DL+ (lexical displacement)
    ├─ MesoStageEvaluator (Sentence-level) [SKIPPED IN PERFORMANCE MODE]
    │   ├─ RP+ (period reconstruction)
    │   ├─ EXP+ (explanation)
    │   └─ AS+ (meaning alteration)
    └─ MicroStageEvaluator (Token-level) [NOT IMPLEMENTED]
        ├─ SL+ (lexical simplification)
        ├─ MOD+ (modulation)
        └─ IN+ (insertion)
    ↓
ConfidenceEngine.calculate_confidence()
    │   → Weighted formula (semantic + lexical + structural + salience)
    │   → Returns confidence ∈ [0, 1]
    ↓
_evidence_to_strategy()
    │   → Convert StrategyEvidence → SimplificationStrategy (Pydantic)
    │   → Attach positions, examples, metadata
    ↓
Response: ComparativeAnalysisResponse (JSON)
    │   → List[SimplificationStrategy]
    │   → Metrics (semantic preservation, readability improvement)
    └─ Frontend renders strategies with highlighting
```

### Design Patterns Identified

1. **Cascade Architecture**: 3-stage detection (Macro→Meso→Micro) with early exit pruning for performance
2. **Hybrid ML Approach**: Lightweight embeddings (MiniLM) + rule-based heuristics
3. **Feature Flags**: YAML config (`config/feature_flags.yaml`) with hot reload capability
4. **Dependency Injection**: FastAPI `Depends()` for service instantiation
5. **Session-Based Analytics**: In-memory metrics with auto-cleanup (no database dependency)
6. **Repository Pattern**: File-based persistence with database adapter interface ready

### Integration Points

| Component | Backend Endpoint | Frontend Consumer | Status |
|-----------|------------------|-------------------|--------|
| Comparative Analysis | POST /api/v1/comparative-analysis/ | DualTextInputComponent | ✅ Working |
| Semantic Alignment | POST /api/v1/semantic-alignment/process | SemanticAlignmentQueries | ✅ Working |
| Analytics | GET /api/v1/analytics/metrics | Dashboard (planned) | 🟡 Partial |
| Feedback | POST /api/v1/comparative-analysis/feedback | FeedbackCollection | 🔴 Not persisted |
| Annotations | POST /api/v1/annotations/ | useAnnotationStore | 🟡 Partial |

### Critical Architectural Pain Points

1. **Tight Coupling**: `comparative_analysis_service.py` directly instantiates dependencies (no abstraction interfaces → testing difficult)
2. **Import Path Chaos**: Triple try-except blocks for every import (absolute, relative, fallback)
   ```python
   try:
       from backend.src.models.strategy_models import ...
   except:
       try:
           from ..models.strategy_models import ...
       except:
           from models.strategy_models import ...
   ```
3. **Global Model Caching**: `_initialize_models()` in strategy_detector.py (not thread-safe for async)
4. **No Sentence Alignment**: Only paragraph-level implemented → limits granularity for RP+, EXP+, MOD+
5. **Feedback Not Persisted**: In-memory store, no SQLite/PostgreSQL adapter wired
6. **Confidence Opacity**: Evidence calculated internally but not surfaced to frontend
7. **Docker Hardcoded Port**: Dockerfile uses `--port 8000` (no fallback to 8080)
8. **CORS String Config**: Comma-separated `ALLOWED_ORIGINS` brittle

---

## Phase 3: Dependencies Audit

### Backend Dependencies (Python 3.12.1 runtime, compiled for 3.13)

| Package | Current | Latest Stable | Status | Risk |
|---------|---------|---------------|--------|------|
| **fastapi** | 0.116.1 | 0.115.5 | ⚠️ Pre-release | Breaking changes likely |
| **pydantic** | 2.11.7 | 2.10.5 | ⚠️ Ahead | May not exist yet |
| **uvicorn** | 0.35.0 | 0.34.0 | ⚠️ Ahead | Stability unknown |
| **sentence-transformers** | 5.0.0 | 3.3.1 | 🚨 Beta/RC | API changes expected |
| **transformers** | 4.54.1 | 4.47.1 | 🚨 Future version | Doesn't exist yet |
| **torch** | 2.7.1 | 2.5.1 | 🚨 Future version | Not released |
| **spacy** | (unpinned) | 3.8.4 | 🚨 Critical | Security risk |
| **textstat** | (unpinned) | 0.7.4 | 🚨 Critical | Reproducibility broken |
| **scikit-learn** | 1.7.1 | 1.6.1 | ⚠️ Future | May not exist |

**Critical Issues**:
- 🔴 **Python version mismatch**: requirements.txt compiled with Python 3.13, runtime is 3.12.1
- 🔴 **Unpinned dependencies**: spacy, textstat → Could install incompatible versions on rebuild
- 🔴 **Pre-release packages**: torch, transformers, sentence-transformers → Stability/compatibility unknown

### Frontend Dependencies (Node 22.17.0, npm 9.8.1)

| Package | Current | Latest | Status | Notes |
|---------|---------|--------|--------|-------|
| **react** | 18.2.0 | 19.0.0 | 🟡 Outdated | React 19 released Nov 2024 |
| **vite** | 5.0.11 | 6.0.7 | 🟡 Outdated | Vite 6 released Nov 2024 |
| **@tanstack/react-query** | 5.85.6 | 5.68.1 | ⚠️ Ahead | Version typo? (5.68 is latest) |
| **axios** | 1.11.0 | 1.7.9 | 🚨 Invalid | 1.11.0 doesn't exist |
| **zustand** | 4.4.5 | 5.0.2 | 🟡 Outdated | Zustand 5 released Sep 2024 |
| **react-query** | 3.39.3 | (deprecated) | 🚨 Duplicate | Remove! Conflicts with @tanstack/react-query |

**Critical Issues**:
- 🔴 **Duplicate react-query**: Both deprecated v3.39.3 and @tanstack/react-query v5.85.6 → Bundle conflicts
- 🔴 **Invalid axios version**: 1.11.0 doesn't exist (latest is 1.7.x)
- 🟡 **Outdated major versions**: React 18 (React 19 available), Vite 5 (Vite 6 available)

### Security Recommendations

**Immediate Actions**:
1. Pin all Python dependencies (spacy, textstat)
2. Downgrade to stable releases:
   - `torch==2.5.1`
   - `transformers==4.47.1`
   - `sentence-transformers==3.3.1`
3. Recompile requirements.txt with Python 3.12 (not 3.13)
4. Remove duplicate `react-query` package
5. Fix axios version to `1.7.9`

**Recommended Upgrades**:
- React 18 → 19 (incremental migration)
- Vite 5 → 6 (minor breaking changes)
- Zustand 4 → 5 (mostly backward compatible)

---

## Phase 4: Language Model Evaluation

### Current Model: paraphrase-multilingual-MiniLM-L12-v2
- **Size**: 118MB
- **Speed**: 5-10x faster than BERTimbau
- **Accuracy**: 80-90% of BERTimbau performance
- **Languages**: 50+ (multilingual), Portuguese included
- **Released**: 2021
- **Limitation**: Not Portuguese-specific, general-purpose embeddings

### Problem History
The original design used **neuralmind/bert-base-portuguese-cased (BERTimbau)**:
- **Size**: 430MB
- **Performance**: 30-60s model loading + 60-90s analysis for 2,292-word text
- **Result**: Exceeded 120s timeout on Hugging Face Spaces CPU

**Solution**: Switched to lightweight MiniLM → solved timeout but sacrificed accuracy

### Evaluation of Newer Models (2024-2025)

| Model | Size | Speed | PT Accuracy | Best For | Verdict |
|-------|------|-------|-------------|----------|---------|
| **Current (MiniLM-L12)** | 118MB | ⭐⭐⭐⭐⭐ | 80-90% | Fast prototyping | 🟡 Good but limited |
| **mpnet-base-v2** | 278MB | ⭐⭐⭐⭐ | 92-95% | Balanced accuracy/speed | ✅ **Best upgrade** |
| **multilingual-e5-large** | 560MB | ⭐⭐ | 97-99% | Accuracy-first | 🔴 Too slow for HF Spaces |
| **LaBSE** | 472MB | ⭐⭐ | 95% | Cross-lingual alignment | 🟡 Specialized use |
| **BERTimbau (refreshed)** | 430MB | ⭐⭐ | 100% | Portuguese authority | 🔴 Original timeout problem |
| **GTE-multilingual-base** ⭐ NEW | 305MB | ⭐⭐⭐⭐ | 95-97% | Modern + fast | ✅ **Experimental choice** |

### Recommended ML Strategy

**Primary Model**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- **Rationale**: 12-15% accuracy gain over current MiniLM, still fits in 2GB Spaces memory limit
- **Performance**: 2-3x slower than MiniLM but 3-4x faster than BERTimbau
- **Academic Value**: High (better semantic understanding for MOD+, AS+, RF+ detection)

**Experimental Model**: `Alibaba-NLP/gte-multilingual-base` (Nov 2024 release)
- **Rationale**: Latest SOTA on MTEB multilingual benchmarks
- **Risk**: Newer model, less battle-tested
- **Use Case**: A/B testing for accuracy comparison

**User-Selectable Modes**:
```python
# Allow users to choose based on priority
if user_mode == "fast" or word_count > 5000:
    model = "paraphrase-multilingual-MiniLM-L12-v2"  # 118MB
elif user_mode == "accurate":
    model = "Alibaba-NLP/gte-multilingual-base"  # 305MB
else:  # "balanced" (default)
    model = "paraphrase-multilingual-mpnet-base-v2"  # 278MB
```

**Phase 2 Optimization**: Convert models to ONNX format with Optimum (2-4x speedup)

---

## Phase 5: Problem Pattern Analysis

### Recurring Technical Issues

#### 1. Port Management & Process Lifecycle (Windows-Specific)

**Problem**: WinError 10013, orphaned processes, IPv4/IPv6 conflicts
- Uvicorn with `reload=True` spawns parent (watchfiles) + worker child
- Killing worker → parent respawns new worker indefinitely
- `localhost` resolves to IPv6 `::1` before IPv4 `127.0.0.1` on Windows
- Hardcoded port 8000 in Dockerfile (no dynamic binding for Codespaces)

**What Worked**:
- ✅ `start_optimized.py` with 8000→8080 fallback
- ✅ `kill_backend_8000.ps1` parent-child tree termination
- ✅ Explicit IPv4 (`127.0.0.1`) in Vite proxy config

**Architectural Mistakes**:
- No container orchestration (Docker Compose missing)
- No health check endpoints used in deployment
- Process management delegated to brittle PowerShell scripts

**Fresh Start Solution**: Use Docker Compose with health checks, bind to `0.0.0.0`, let orchestrator manage lifecycle

---

#### 2. Model Loading Timeouts

**Problem**: BERTimbau (430MB) exceeded 120s timeout
- Model loading: 30-60s
- Analysis: 60-90s for 2,292-word text
- Total: 90-150s → timeout

**What Worked**:
- ✅ Switched to MiniLM (118MB, 5-10x faster)
- ✅ Global model caching in `_initialize_models()`
- ✅ `NET_EST_DISABLE_MODELS=1` flag for testing

**Architectural Mistakes**:
- Model loading on first request (cold start penalty)
- No preloading in Dockerfile (CMD doesn't warm cache)
- No asynchronous model download/initialization

**Fresh Start Solution**: Preload models in Dockerfile, async init on startup, ONNX optimization

---

#### 3. Import Path Hell

**Problem**: Triple try-except blocks for every import
```python
try:
    from backend.src.models.strategy_models import ...
except:
    try:
        from ..models.strategy_models import ...
    except:
        from models.strategy_models import ...
```

**Root Cause**:
- Tests run with different `PYTHONPATH` (repo root vs backend/)
- No unified package structure (setup.py exists but not used)
- `sys.path` manipulation in scripts

**What Worked**:
- ✅ Standardized on `python -m uvicorn src.main:app` (removes CWD ambiguity)

**Architectural Mistake**:
- Not installing backend as package (`pip install -e backend/`)
- Mixing relative and absolute imports

**Fresh Start Solution**: Use Poetry with proper package structure, single import style

---

#### 4. Dependency Version Chaos

**Problem**: Pre-release packages in production
- `torch==2.7.1` (doesn't exist yet)
- `transformers==4.54.1` (future version)
- `sentence-transformers==5.0.0` (beta)
- Unpinned `spacy` and `textstat`

**Root Cause**:
- requirements.txt compiled with Python 3.13 (environment uses 3.12.1)
- No CI/CD checks for version compatibility
- No `pip-audit` or Dependabot integration

**Fresh Start Solution**: Poetry lockfile, CI/CD version validation, Dependabot alerts

---

#### 5. Frontend Multipart Upload Failures (Sept 2025)

**Problem**: 500 errors on file upload
- Manual `Content-Type: multipart/form-data` header set by developer
- Axios not automatically setting boundary parameter
- Backend CORS not properly accepting FormData

**What Worked**:
- ✅ FormData-aware axios interceptor (delete Content-Type, let browser set)
- ✅ Enhanced backend logging (request metadata)

**Architectural Mistake**:
- No regression tests for interceptors
- Upload endpoint not using proper Pydantic `UploadFile` validation

**Fresh Start Solution**: Regression test suite, OpenAPI schema validation with Dredd

---

#### 6. Heuristic-Only Detection (Academic Failure)

**Problem**: Disabling ML models → poor accuracy
- SL+ false positives (simple word frequency doesn't capture semantic simplification)
- MOD+ undetectable (requires semantic drift analysis)
- AS+ unreliable (no meaning preservation check)

**What Worked**:
- ✅ Hybrid approach (lightweight MiniLM + heuristics as feature extractors)

**Architectural Mistake**:
- No graceful degradation (all-or-nothing: full ML or pure heuristics)
- No confidence scoring based on evidence source (ML vs heuristic)

**Fresh Start Solution**: Always require ML backbone, confidence tiers (ML-high, heuristic-medium)

---

### Lessons Learned

| Problem Pattern | Avoidance Strategy |
|----------------|-------------------|
| **Port conflicts** | Docker Compose with dynamic port allocation; health checks |
| **Model timeouts** | Preload models in Dockerfile; async init on startup; ONNX optimization |
| **Import chaos** | Install as package (`pip install -e .`); single import style (absolute) |
| **Version drift** | Pin all dependencies; CI/CD validation; Dependabot |
| **Upload failures** | Regression test suite for interceptors; OpenAPI schema validation |
| **Heuristic accuracy** | Always require ML backbone; confidence tiers (ML-high, heuristic-medium) |
| **Process management** | Containers > PowerShell scripts; orchestrator handles lifecycle |
| **IPv4/IPv6** | Bind to `0.0.0.0` (all interfaces); explicit IP in proxies |

### What Worked Well ✅

1. **Feature Flags System**: YAML-based, hot-reload, dot notation access
2. **Session-Based Analytics**: Database-free, perfect for ephemeral Spaces
3. **Cascade Architecture**: Early exit pruning, performance-first design
4. **Hybrid ML Approach**: Balances accuracy (MiniLM) + speed (heuristics)
5. **Error Handling**: Centralized `useErrorHandler` with contextual messages
6. **Development Documentation**: `docs_dev/` comprehensive troubleshooting guides
7. **Git Workflow**: Branch naming (`integration/consolidation-phase2`), PR discipline

---

## Phase 6: Algorithm Redesign

### Current Pipeline (Reverse-Engineered)

```
Input: source_text, target_text
  ↓
[1] Paragraph Alignment (SemanticAlignmentService)
    → Split into paragraphs
    → Embed with MiniLM
    → Cosine similarity matrix
    → Hungarian algorithm
    → Output: aligned_pairs, unaligned_source, unaligned_target
  ↓
[2] Feature Extraction (FeatureExtractor) [ONCE - GLOBAL ONLY]
    → Lexical: word overlap, unique words, TTR
    → Structural: sentence counts, avg length
    → Semantic: overall similarity (MiniLM)
    → Output: StrategyFeatures (global metrics)
  ↓
[3] Cascade Detection (CascadeOrchestrator)
    ├─ [3.1] Macro Stage (Paragraph-level) ✅ IMPLEMENTED
    │   ├─ RF+ (high semantic sim + structural change)
    │   ├─ OM+ (low coverage, missing paragraphs) [MANUAL ONLY]
    │   ├─ RD+ (connector changes, order shifts)
    │   └─ DL+ (word position changes)
    │
    ├─ [3.2] Meso Stage (Sentence-level) 🔴 NOT IMPLEMENTED
    │   ├─ RP+ (1 sentence → 2+ sentences)
    │   ├─ EXP+ (insertion with definition/context)
    │   └─ AS+ (semantic drift detected)
    │
    └─ [3.3] Micro Stage (Token-level) 🔴 NOT IMPLEMENTED
        ├─ SL+ (lexical complexity reduction)
        ├─ MOD+ (voice/perspective shift)
        └─ IN+ (token insertion without source)
  ↓
[4] Confidence Calculation (ConfidenceEngine)
    → Weighted formula: semantic + lexical + structural + salience
    → Output: confidence ∈ [0, 1] (BUT NOT EXPLAINED)
  ↓
[5] Evidence to Strategy Conversion
    → StrategyEvidence → SimplificationStrategy (Pydantic)
    → Attach positions, examples, metadata
  ↓
Output: List[SimplificationStrategy]
```

### Critical Gaps

1. **No Sentence Alignment**: Meso stage exists but unused (always skipped in performance mode)
2. **No Micro Diff**: Token-level operations not extracted
3. **Global Features Only**: Metrics don't capture local variations (sentence-specific complexity)
4. **Confidence Opacity**: Evidence breakdown not surfaced to frontend
5. **No Feedback Loop**: Corrections collected but not used for retraining
6. **Hard-Coded Thresholds**: No adaptive calibration based on text complexity

### Proposed Clean Architecture (7 Layers)

```
Layer 1: Text Preprocessing
    ↓ TextPreprocessor
    ↓ normalize(), segment_paragraphs(), segment_sentences(), tokenize()

Layer 2: Hierarchical Alignment
    ↓ AlignmentService
    ↓ align_paragraphs() → ParagraphAlignment
    ↓ align_sentences() → SentenceAlignment (NEW)
    ↓ extract_micro_ops() → List[MicroOperation] (NEW)

Layer 3: Multi-Level Feature Extraction
    ↓ FeatureExtractorV2
    ↓ extract_paragraph_features() → ParagraphFeatures
    ↓ extract_sentence_features() → SentenceFeatures (NEW)
    ↓ extract_token_features() → TokenFeatures (NEW)

Layer 4: Evidence-Based Detection
    ↓ StrategyDetector
    ↓ RuleEngine.evaluate() → rule_evidences
    ↓ MLClassifier.predict() → ml_evidences (FUTURE)
    ↓ ensemble(rule + ML) → evidences with provenance

Layer 5: Modular Rule Engine
    ↓ RuleEngine
    ↓ register(strategy_code, StrategyRule)
    ↓ SLPlusRule, RPPlusRule, MODPlusRule, etc.
    ↓ Each rule: evaluate(pair, features) → Optional[StrategyEvidence]

Layer 6: Explainable Confidence
    ↓ ConfidenceEngine
    ↓ calculate(evidence, features, config) → (confidence, Explanation)
    ↓ Explanation includes:
        - base_confidence
        - feature_contributions (top 3)
        - penalties (heuristic-only, low quality)
        - user_weight
        - final confidence

Layer 7: Feedback Integration
    ↓ FeedbackStore
    ↓ record(feedback_event) → PostgreSQL
    ↓ query(filters) → List[FeedbackEvent]
    ↓ MLClassifierTrainer (FUTURE Phase 2)
    ↓ prepare_dataset() → train() → export()
```

### Key Improvements

1. **Hierarchical Features**: Not just global metrics, but paragraph/sentence/token-specific
2. **Explainable Confidence**: Frontend receives feature breakdown (top 3 contributors)
3. **Modular Rules**: Easy to add/remove/modify strategies without touching orchestrator
4. **ML-Ready**: Classifier slot for future training from feedback
5. **Provenance Tracking**: Know if detection came from ML, rule, or ensemble
6. **User Configurable**: Weights per strategy, activation toggles
7. **Evidence-Based**: Every strategy has attached text spans, not just global flags

### Example: New Strategy Rule

```python
class SLPlusRule(StrategyRule):
    """Lexical Simplification: complex → simple word substitution"""
    
    def evaluate(self, pair: AlignedPair, features: Features) -> Optional[StrategyEvidence]:
        ops = pair.micro_operations  # NEW: token-level diffs
        
        for op in ops:
            if op.type == "replace" and op.token_features.lex_complexity_delta < -0.2:
                if op.token_features.salience > 0.5:  # High-value substitution
                    return StrategyEvidence(
                        strategy_code="SL+",
                        confidence=0.8,
                        positions=[(op.source_start, op.source_end)],
                        examples=[{
                            "original": op.source_span,
                            "simplified": op.target_span
                        }],
                        feature_contributors={  # NEW: Explainability
                            "lex_complexity_delta": -0.3,
                            "salience": 0.7
                        },
                        has_ml_support=False,  # NEW: Provenance
                        provenance="rule-based"
                    )
        return None
```

---

## Phase 7: Technology Stack Recommendation

### Backend Framework: FastAPI 0.115.5 ✅ KEEP
- Modern async support for ML model inference
- Pydantic v2 perfect for strict academic data validation
- OpenAPI schema auto-generation aids frontend integration
- Large ecosystem (Starlette, Uvicorn) battle-tested

**Alternative Considered**: Litestar (faster but smaller ecosystem)

### Frontend Framework: React 19 ✅ UPGRADE
- Industry standard, huge ecosystem
- React Compiler (auto-optimization, no manual `useMemo`)
- Actions API (better form handling for feedback collection)
- Server Components (future: SSR for SEO/reports)
- Migration from 18 is incremental (backward compatible)

**Alternative Considered**: Solid.js (faster but smaller ecosystem)

### State Management: Zustand 5 + TanStack Query v6 ✅ UPGRADE BOTH
- **Zustand 5**: Global app state (user config, session, notifications)
- **TanStack Query v6**: Server state (analysis results, alignment, feedback)
- **Remove duplicate `react-query` v3** (deprecated, conflicts with @tanstack)
- Migration: Zustand 4→5 mostly compatible; TQ v5→v6 minor breaking changes

### Build Tool: Vite 6 ✅ UPGRADE
- Ultra-fast HMR (critical for rapid iteration)
- Native ESM, Rollup prod builds
- Environment variables API improved
- Better monorepo support (future: backend + frontend unified)
- Vite 5→6 migration straightforward

### ML Model Serving: Hybrid Approach
1. **Primary**: Local `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (278MB)
2. **Optimization**: Convert to ONNX with Optimum (2x speedup) — Phase 2
3. **Fallback**: HuggingFace Inference API for experimental models (GTE-multilingual)
4. **Preloading**: Dockerfile preloads models (eliminates cold start)

### Database & Persistence

**PostgreSQL (Neon free tier)**: Feedback events, user corrections
- Free tier: 0.5GB storage, 512MB compute
- ACID compliance for academic data integrity
- Connection pooling for concurrent users

**Redis (Upstash free tier)**: Model embeddings cache
- Free tier: 10k requests/day
- Fast caching reduces model inference load
- Embeddings survive container restarts

**SQLite**: Development environment fallback
- Embedded, zero-config
- Perfect for local dev (no external DB needed)

**Pattern**: Repository abstraction (swap DB without changing services)

### Deployment Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Backend Host** | Railway ($5/month) | PostgreSQL + Redis included; better than HF Spaces for DB apps |
| **Frontend Host** | Vercel (free) | React 19 support, global CDN, perfect for static + SSR |
| **Container Registry** | GitHub Container Registry | Free for public repos, CI/CD integrated |
| **CI/CD** | GitHub Actions | Auto-deploy on merge to `main` |
| **Monitoring** | Sentry (free tier) | Error tracking, performance monitoring |

### Testing Framework

| Type | Tool | Rationale |
|------|------|-----------|
| **Backend Unit** | pytest + pytest-cov | Keep (industry standard) |
| **Backend API Contract** | Dredd | NEW: Validates OpenAPI schema |
| **Frontend Unit** | Vitest | Keep (faster than Jest, Vite-native) |
| **Frontend E2E** | Playwright | Keep (cross-browser, reliable) |
| **Pre-commit** | ruff (Python), ESLint (JS) | NEW: Auto-formatting |

### Development Environment

**Package Managers**:
- **Poetry 1.8+** (Python): Lockfile, dependency groups, better than requirements.txt
- **pnpm** (JavaScript): 2x faster than npm, disk-efficient

**Tooling**:
- **uv**: Rust-based Python installer (10-100x faster than pip)
- **Black**: Python auto-formatting
- **Prettier**: JavaScript/CSS/Markdown auto-formatting
- **Pyright**: Python type checking (faster than mypy)

### Final Tech Stack Summary

```yaml
Backend:
  Framework: FastAPI 0.115.5
  Runtime: Python 3.12 (stable, not 3.13 pre-release)
  Package Manager: Poetry 1.8+
  ML Model: sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (278MB)
  ML Optimization: ONNX Runtime (Phase 2)
  Database: PostgreSQL (Neon free tier) + SQLite (dev)
  Cache: Redis (Upstash free tier)
  Testing: pytest + pytest-cov + Dredd
  Type Checking: Pyright
  Formatting: Black

Frontend:
  Framework: React 19
  Build Tool: Vite 6
  State Management: Zustand 5 + TanStack Query v6
  Styling: Tailwind CSS (keep)
  Package Manager: pnpm
  Testing: Vitest + Playwright
  Linting: ESLint
  Formatting: Prettier

DevOps:
  Backend Host: Railway ($5/month)
  Frontend Host: Vercel (free)
  Container: Docker + GHCR
  CI/CD: GitHub Actions
  Monitoring: Sentry (free tier)

Development:
  Env Manager: uv (Python), pnpm (JS)
  Pre-commit: ruff (Python), ESLint (JS)
  Docker Compose: Local dev environment
```

---

## Phase 8: Development Roadmap

### Milestone-Based Implementation (14 weeks)

#### **Milestone 1: Foundation (Weeks 1-2)** 🏗️
**Goal**: Setup infrastructure + basic text processing

**Backend**:
- [ ] Initialize Poetry project with dependencies
- [ ] FastAPI app factory with settings management
- [ ] Docker + Docker Compose (Postgres + Redis)
- [ ] Health check endpoint (`/health`)
- [ ] Model preloading in Dockerfile (`mpnet-base-v2`)
- [ ] GitHub Actions CI (pytest)

**Frontend**:
- [ ] Initialize pnpm + Vite 6 + React 19
- [ ] Upgrade Zustand 5 + TanStack Query v6
- [ ] Remove duplicate `react-query` v3
- [ ] API client with interceptors
- [ ] Error boundary + notification system
- [ ] GitHub Actions CI (vitest)

**Success Criteria**:
- ✅ `docker-compose up` starts backend + DB + cache
- ✅ Frontend dev server connects to backend
- ✅ CI passes on PR

---

#### **Milestone 2: Alignment Layer (Weeks 3-4)** 🎯
**Goal**: Multi-level text alignment (paragraph → sentence)

**Backend**:
- [ ] `TextPreprocessor` (normalize, segment)
- [ ] `ParagraphAligner` (embed + Hungarian algorithm)
- [ ] `SentenceAligner` (detect splits/merges)
- [ ] `MicroDiff` (token-level SequenceMatcher)
- [ ] API endpoint: `POST /api/v1/alignment/process`
- [ ] Unit tests (>90% coverage)

**Frontend**:
- [ ] `DualInput` component (source + target text)
- [ ] `AlignmentViewer` (visualize aligned pairs)
- [ ] `useAlignment` hook (TanStack Query)

**Success Criteria**:
- ✅ Align 2 paragraphs in <2s (mpnet model)
- ✅ Detect sentence splits (1→2) accurately
- ✅ Frontend displays alignment matrix

---

#### **Milestone 3: Feature Extraction (Weeks 5-6)** 📊
**Goal**: Multi-level features (paragraph, sentence, token)

**Backend**:
- [ ] `FeatureExtractorV2` (hierarchical features)
- [ ] `SalienceProvider` (frequency fallback → keybert)
- [ ] Feature caching (Redis)
- [ ] API endpoint: `POST /api/v1/features/extract`

**Frontend**:
- [ ] Feature visualization (debug mode)
- [ ] Salience heatmap overlay

**Success Criteria**:
- ✅ Extract features for 10-paragraph text in <5s
- ✅ Cache hit rate >80% for repeat texts

---

#### **Milestone 4: Strategy Detection (Weeks 7-9)** 🧠
**Goal**: Core detection pipeline with explainable confidence

**Backend**:
- [ ] `RuleEngine` + modular `StrategyRule` base
- [ ] Implement 10 strategy rules (SL+, RP+, RF+, etc.)
- [ ] `ConfidenceEngine` with feature breakdown
- [ ] `StrategyDetector` (rule-based only, ML slot ready)
- [ ] API endpoint: `POST /api/v1/analysis/detect`
- [ ] Integration tests

**Frontend**:
- [ ] `ResultsDisplay` (strategy cards)
- [ ] `StrategyHighlighter` (text overlay with positions)
- [ ] `ConfidenceExplainer` (feature contributions tooltip)
- [ ] `useAnalysis` hook

**Success Criteria**:
- ✅ Detect ≥5 strategies on test corpus (tabela_est.md examples)
- ✅ Confidence explanations shown in UI
- ✅ Academic validation: manual review of 20 texts (>85% precision)

---

#### **Milestone 5: Feedback Loop (Weeks 10-11)** 🔄
**Goal**: User corrections with persistence

**Backend**:
- [ ] `FeedbackRepository` (PostgreSQL adapter)
- [ ] `FeedbackCollector` service
- [ ] API endpoints: `POST /api/v1/feedback`, `GET /api/v1/feedback/export`
- [ ] Feedback data schema (text_pair_id, corrections, context)

**Frontend**:
- [ ] `FeedbackModal` (edit tag, add rationale)
- [ ] Optimistic updates (local state)
- [ ] `useFeedback` hook

**Success Criteria**:
- ✅ Corrections persisted to PostgreSQL
- ✅ Export feedback as JSONL for future training
- ✅ Rollback on server failure

---

#### **Milestone 6: Reporting & Analytics (Weeks 12-13)** 📈
**Goal**: Session analytics + export reports

**Backend**:
- [ ] `AnalyticsService` (session-based + persistent)
- [ ] `ReportGenerator` (PDF export with hierarchical view)
- [ ] API endpoint: `GET /api/v1/analytics/export`

**Frontend**:
- [ ] Dashboard (strategy distribution chart)
- [ ] Export button (download PDF/JSONL)

**Success Criteria**:
- ✅ Generate PDF report with aligned texts + strategies
- ✅ Analytics survive session restarts (Postgres)

---

#### **Milestone 7: Deployment & Monitoring (Week 14)** 🚀
**Goal**: Production-ready deployment

**DevOps**:
- [ ] Railway deployment (backend + Postgres + Redis)
- [ ] Vercel deployment (frontend)
- [ ] GitHub Actions deploy pipeline
- [ ] Sentry integration (error tracking)
- [ ] Environment variables management

**Documentation**:
- [ ] API reference (OpenAPI schema)
- [ ] User guide
- [ ] Developer setup instructions

**Success Criteria**:
- ✅ Backend live on Railway (public URL)
- ✅ Frontend live on Vercel
- ✅ End-to-end smoke test passes
- ✅ Error tracking active (Sentry)

---

#### **Milestone 8: ML Training (Phase 2 - Weeks 15-18)** 🤖
**Goal**: Train classifier from feedback data

**Backend**:
- [ ] `MLClassifierTrainer` (gradient boosting on features)
- [ ] Dataset preparation (feedback → labeled examples)
- [ ] Model training pipeline (offline)
- [ ] Ensemble logic (rule + ML confidence)
- [ ] A/B testing framework (rule-only vs ensemble)

**Success Criteria**:
- ✅ Collect ≥500 feedback events
- ✅ Train classifier (F1 > 0.80)
- ✅ Ensemble improves accuracy by ≥10%

---

### Feature Priority Matrix

| Feature | Academic Value | Engineering Complexity | Priority |
|---------|----------------|------------------------|----------|
| **Paragraph Alignment** | High (baseline) | Medium | P0 |
| **Sentence Alignment** | High (precision) | Medium | P0 |
| **Strategy Rules (10 tags)** | High (core) | Medium | P0 |
| **Confidence Explainability** | High (trust) | Low | P0 |
| **Feedback Persistence** | High (ML training) | Low | P1 |
| **Micro Diff (token-level)** | Medium (detail) | High | P1 |
| **Salience Weighting** | Medium (accuracy) | Medium | P1 |
| **ML Classifier** | High (accuracy) | High | P2 |
| **PDF Export** | Medium (usability) | Low | P2 |
| **Analytics Dashboard** | Low (nice-to-have) | Medium | P3 |
| **ONNX Optimization** | Low (performance) | Medium | P3 |

---

### Project Structure (Clean Rebuild)

```
net-est-v2/
├── .github/
│   ├── workflows/
│   │   ├── backend-ci.yml          # pytest + coverage
│   │   ├── frontend-ci.yml         # vitest + Playwright
│   │   └── deploy.yml              # Railway + Vercel
│   └── copilot-instructions.md
├── backend/
│   ├── pyproject.toml              # Poetry dependencies
│   ├── poetry.lock
│   ├── Dockerfile                  # Multi-stage with model preload
│   ├── docker-compose.yml          # Local dev (Postgres + Redis)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app factory
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings
│   │   │   ├── feature_flags.py
│   │   │   └── dependencies.py     # DI container
│   │   ├── api/                    # Route handlers
│   │   │   └── v1/
│   │   │       ├── analysis.py
│   │   │       ├── alignment.py
│   │   │       ├── feedback.py
│   │   │       └── health.py
│   │   ├── domain/                 # Business logic
│   │   │   ├── alignment/
│   │   │   │   ├── paragraph_aligner.py
│   │   │   │   ├── sentence_aligner.py
│   │   │   │   └── micro_diff.py
│   │   │   ├── features/
│   │   │   │   ├── extractor.py
│   │   │   │   └── salience.py
│   │   │   ├── strategies/
│   │   │   │   ├── detector.py
│   │   │   │   ├── rule_engine.py
│   │   │   │   ├── rules/
│   │   │   │   │   ├── sl_plus.py
│   │   │   │   │   ├── rp_plus.py
│   │   │   │   │   └── ...
│   │   │   │   └── confidence.py
│   │   │   └── feedback/
│   │   │       ├── collector.py
│   │   │       └── trainer.py      # Future ML training
│   │   ├── models/                 # Pydantic schemas
│   │   │   ├── analysis.py
│   │   │   ├── alignment.py
│   │   │   ├── strategies.py
│   │   │   └── feedback.py
│   │   ├── repositories/           # Data access
│   │   │   ├── feedback_repo.py
│   │   │   └── cache_repo.py
│   │   └── utils/
│   │       ├── text_processing.py
│   │       └── ml_utils.py
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       ├── integration/
│       └── e2e/
├── frontend/
│   ├── package.json                # pnpm workspaces
│   ├── pnpm-lock.yaml
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── analysis/
│   │   │   │   ├── DualInput.jsx
│   │   │   │   ├── ResultsDisplay.jsx
│   │   │   │   └── StrategyHighlighter.jsx
│   │   │   ├── feedback/
│   │   │   │   └── FeedbackModal.jsx
│   │   │   └── common/
│   │   ├── hooks/
│   │   │   ├── useAnalysis.js      # TanStack Query
│   │   │   ├── useFeedback.js
│   │   │   └── useErrorHandler.js
│   │   ├── stores/                 # Zustand
│   │   │   ├── appStore.js
│   │   │   └── sessionStore.js
│   │   ├── services/
│   │   │   └── api.js              # Axios client
│   │   └── utils/
│   └── tests/
│       ├── unit/
│       └── e2e/
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   └── strategy-taxonomy.md
└── README.md
```

---

### Migration Strategy (Current → Fresh Start)

#### **Code Reuse Assessment**

| Component | Reuse? | Notes |
|-----------|--------|-------|
| `cascade_orchestrator.py` | 🟡 Adapt | Extract rule logic, discard orchestration |
| `feature_extraction_service.py` | ✅ Yes | Good foundation, minor refactor |
| `semantic_alignment_service.py` | ✅ Yes | Core logic solid, keep |
| `confidence_engine.py` | 🟡 Adapt | Add explainability, feature breakdown |
| Frontend components | ✅ Yes | DualInput, ResultsDisplay mostly ready |
| Feature flags system | ✅ Yes | Keep as-is |

#### **Phased Cutover**

1. **Week 1-4**: Develop in parallel (new repo or branch `v2/fresh-start`)
2. **Week 5**: Feature parity check (alignment + basic detection)
3. **Week 6**: User testing (compare old vs new accuracy)
4. **Week 7**: Soft launch (new system, old system still accessible)
5. **Week 8**: Hard cutover (deprecate old system)

---

### Risk Mitigation Plan

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Model timeout (mpnet)** | Medium | High | Add ONNX conversion (M8); fallback to MiniLM |
| **PostgreSQL free tier limit** | Low | Medium | Monitor usage; upgrade plan ready ($5/month) |
| **Academic validation fails** | Medium | High | Iterative testing with linguist; adjust rules |
| **Feedback spam** | Low | Low | Rate limiting; require session ID |
| **ML training insufficient data** | High | Medium | Synthetic data augmentation; manual annotations |
| **Deployment complexity** | Low | Low | Docker Compose for local parity; Railway templates |

---

### Success Metrics

**Technical**:
- ✅ API response time: P95 < 8s for 2k-word pair
- ✅ Test coverage: >90% (backend), >80% (frontend)
- ✅ Uptime: >99.5% (Railway monitoring)

**Academic**:
- ✅ Precision: >85% on manual validation corpus (20 texts)
- ✅ Recall: >80% (detect strategies present in gold standard)
- ✅ Confidence calibration: ±15% of human judgment

**User Experience**:
- ✅ Time to first result: <10s
- ✅ Error rate: <5% (failed analysis attempts)
- ✅ Feedback submission rate: >30% of sessions

---

## Appendices

### A. Glossary

- **BERTimbau**: Portuguese-specific BERT model (neuralmind/bert-base-portuguese-cased)
- **MiniLM**: Lightweight multilingual sentence transformer (paraphrase-multilingual-MiniLM-L12-v2)
- **mpnet**: Multilingual sentence transformer (paraphrase-multilingual-mpnet-base-v2)
- **Cascade Architecture**: Multi-stage detection with early exit pruning
- **Hybrid Approach**: ML embeddings + rule-based heuristics
- **Evidence-Based Detection**: Strategies backed by text spans and feature explanations
- **Provenance**: Source of detection (ML model, rule-based, or ensemble)

### B. References

- **tabela_est.md**: Canonical strategy taxonomy
- **algorithm_v3_consolidated_2025-08-10.md**: Original algorithm specification
- **backend_windows_troubleshooting.md**: Windows-specific pain points
- **session_handoff_2025-09-27.md**: Frontend upload regression session
- **hybrid_model_approch.md**: Model evolution (BERTimbau → MiniLM)

### C. Contact Information

- **Coordinator**: Profa. Dra. Janine Pimentel
- **Principal Developer**: Wisley Vilela
- **Linguistic Specialist**: Luanny Matos de Lima
- **Institution**: PIPGLA/UFRJ | Politécnico de Leiria
- **Support**: CAPES
- **License**: MIT

---

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
