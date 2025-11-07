# NET-EST (Núcleo de Estudos em Tradução - Estratégias de Simplificação)

---
applyTo: "**/*.md **/*.txt"
placement: end
---

## Scope & guardrails
- Append the attribution banner below only to Markdown/text docs; never to code. Keep existing banners when editing docs.
- Authority docs live in `docs/` and `docs_dev/`; favor updating those over ad-hoc notes so downstream automation stays accurate.

## Architecture snapshot
- **Backend (`backend/src`)** – FastAPI + Pydantic services split by domain: text input, semantic alignment, comparative analysis, analytics. `services/strategy_detector.py` runs a cascade orchestrator with spaCy + SentenceTransformers, caching models via `_initialize_models()` and honoring `NET_EST_DISABLE_MODELS=1` for lean test runs. `services/analytics_service.py` keeps all metrics in-memory (no DB) with export helpers and automatic session cleanup.
- **Frontend (`frontend/src`)** – React/Vite app driven by Zustand stores (`useAnalysisStore`, `useAppStore`) and React Query hooks (`useSemanticAlignment`, `useTextInputQueries`, etc.). `components/DualTextInputComponent.jsx` + `EnhancedTextInput.jsx` orchestrate dual text submission and show async status via the stores.
- **Pipelines** – Text flows: text input ➜ semantic alignment ➜ feature extraction/strategy detection ➜ analytics + feedback. Feature flags in `backend/config/feature_flags.yaml` gate experimental paths (hierarchical output, salience weighting, langextract integration).

## Core workflows
- **Backend runtime** – From `backend/`, run `python start_optimized.py`; it injects `backend/src` into `sys.path`, auto-selects ports (8000 → 8080 fallback), and preloads language models with logging. Manual fallback: `python -m uvicorn src.main:app --reload`.
- **Backend tests** – Execute `pytest` (root or `backend/`). `pytest.ini` forces verbose + coverage and the repo-level `conftest.py` auto-skips heavy models by setting `NET_EST_DISABLE_MODELS=1`. Integration scripts like `test_hierarchical_api.py` require `RUN_INTEGRATION=true` and a running server.
- **Frontend runtime** – From `frontend/`, use `npm ci` > `npm run dev` (Vite on :3000). Build with `npm run build`; run unit tests via `npm run test` and Playwright e2e via `npm run test:e2e` after `npx playwright install`.
- **VS Code tasks** – PowerShell helpers under `scripts/process/` wrap common flows (start/stop servers, run tests); invoke via the preconfigured tasks panel when available.

## Implementation patterns
- **Strategy tagging** – Keep `[PRO+]` human-only; cascade orchestrator assembles `StrategyEvidence` objects that are converted to `SimplificationStrategy` with fallback heuristics for model outages.
- **Semantic alignment** – `semantic_alignment_service.py` and hooks like `useSemanticAlignment()` expect paragraph-level pairs; validate inputs early (minimum length, batch size ≤ 10) mirroring frontend guard clauses.
- **Error + notification flow** – Route user-facing issues through `useErrorHandler` to emit `useAppStore` notifications, respecting the HTTP-status-specific copy already defined.
- **Analytics + feedback** – `analytics_service.py` exposes session CRUD endpoints under `/api/v1/analytics/`; exports go through JSON serialisation helpers. Feedback storage defaults to `data/feedback` per `feature_flags.yaml`.

## Debugging aids & docs
- `debug_*.py` scripts in the repo root exercise individual services without the UI; use them when triaging cascade or alignment regressions.
- `demos/test_confidence_demo.py` showcases the confidence/weighting engine (M5) and mirrors how session metrics should behave.
- Operational guides: see `docs_dev/backend_windows_troubleshooting.md` for Windows quirks and `docs/fase2_a3_analytics_implementation.md` for analytics design constraints.

## Expectations for new work
- Preserve the separation between API layer (`api/v1`) and business logic (`services/`); new endpoints should remain thin wrappers around service methods.
- When touching docs in Portuguese/English hybrids, keep bilingual terminology consistent with `docs/Tabela Simplificação Textual`.
- Prefer enriching automated exports/tests over ad-hoc logging; when adding ML-dependent behavior, provide `NET_EST_DISABLE_MODELS` fallbacks so CI stays green.

---
**Feedback:** Point out anything unclear or missing so we can refine these instructions.


/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/


