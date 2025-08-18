Salience scoring implementation & maintenance pipeline
=====================================

Purpose
-------
Keep a living implementation plan and status log for salience scoring and hierarchical integration. Track completed tasks and next steps so the AI coding-agent and contributors can proceed with minimal bottlenecks.

Current status (snapshot)
- Salience provider implemented: frequency / keybert / yake with LRU cache.
  - Implementation: [`backend/src/services/salience_provider.py`](backend/src/services/salience_provider.py:84)
- Feature-extractor wrapper implemented: `FeatureExtractor.salience_score(...)`.
  - Implementation: [`backend/src/services/feature_extractor.py`](backend/src/services/feature_extractor.py:155)
- Hierarchical integration (paragraph + sentence salience, normalization, feature_extraction_summary).
  - Implementation and normalization logic: [`backend/src/services/comparative_analysis_service.py`](backend/src/services/comparative_analysis_service.py:706)
- Dataclass models already contain salience/key-phrases/features:
  - Dataclasses: [`backend/src/models/hierarchical_nodes.py`](backend/src/models/hierarchical_nodes.py:6)
  - Pydantic response includes hierarchical_tree and feature_extraction_summary: [`backend/src/models/comparative_analysis.py`](backend/src/models/comparative_analysis.py:148)

Design notes
------------
- Normalization semantics:
  - Paragraph salience: average unit weight per paragraph, then normalized across paragraphs (divide by paragraph max).
  - Sentence salience: computed per sentence and normalized per paragraph (per-paragraph max => 1.0).
  - These semantics are intentional (salience relative inside paragraph) — document for API consumers.
- Concurrency note:
  - Current code mutates `self.salience_provider.method` for request overrides. This is a potential race if the service instance is reused for concurrent requests.
  - Recommended: create a per-request provider instance when `request.salience_method` is present.

Saved iterative implementation pipeline
--------------------------------------
Sprint 0 — Prep & quick wins (small, low-risk changes)
- [x] Add this pipeline document for future reference.
- [ ] Add inline comments documenting normalization semantics in:
  - [`backend/src/services/comparative_analysis_service.py`](backend/src/services/comparative_analysis_service.py:706)
  - [`backend/src/models/hierarchical_nodes.py`](backend/src/models/hierarchical_nodes.py:69)
- [ ] Remove duplicate early `analyze_phrases` stub (there is a full implementation later) to avoid confusion:
  - File: [`backend/src/services/comparative_analysis_service.py`](backend/src/services/comparative_analysis_service.py:168)
- [ ] Add TODO comment at `salience_provider.method` override site about concurrency risk:
  - File: [`backend/src/services/comparative_analysis_service.py`](backend/src/services/comparative_analysis_service.py:733)

Sprint 1 — Safety & tests (low-to-medium effort)
- [ ] Make SalienceProvider request-scoped when `request.salience_method` is provided:
  - Create provider = SalienceProvider(method=request.salience_method) inside `_build_hierarchy_async`.
  - Keep service-level shared provider as fallback.
  - Files: [`backend/src/services/comparative_analysis_service.py`](backend/src/services/comparative_analysis_service.py:706), [`backend/src/services/salience_provider.py`](backend/src/services/salience_provider.py:84)
- [ ] Add unit tests for SalienceProvider:
  - cache LRU behavior
  - method fallbacks (keybert/yake -> frequency)
  - per-request override behavior

Sprint 2 — Normalization semantics + tests
- [ ] Add unit tests verifying:
  - paragraph salience normalization across paragraphs
  - sentence salience normalization per paragraph
  - behavior when provider returns no units (0.0 / None)
- [ ] Add tests for `FeatureExtractor.salience_score` with and without provider

Sprint 3 — Schema tightening & API ergonomics (optional)
- [ ] Add Pydantic models for hierarchical nodes (Phrase/Sentence/Paragraph) and type `ComparativeAnalysisResponse.hierarchical_tree`:
  - File suggestion: `backend/src/models/hierarchical_nodes_pydantic.py`
  - Update `backend/src/models/comparative_analysis.py` to reference new models
- [ ] Optionally add `salience_visual_bucket` mapping in hierarchical output honoring `salience_visual_mode`
  - Files: [`backend/src/services/comparative_analysis_service.py`](backend/src/services/comparative_analysis_service.py:706),
    [`backend/src/models/comparative_analysis.py`](backend/src/models/comparative_analysis.py:39)

Sprint 4 — CI, perf & hardening
- [ ] Run full test suite, fix regressions and flaky tests
- [ ] Profile pipeline to tune `SALIENCE_CACHE_MAX` and heavy model usage
- [ ] Add mocks for heavy optional libraries in CI (KeyBERT, YAKE, spaCy, sentence-transformers)

Operational guidance for AI coding-agent
---------------------------------------
- Make changes small and focused: one logical change per PR, 1–2 files maximum.
- Always include unit tests for behavior changes (especially for normalization and provider behavior).
- Prefer deterministic, local tests over integration tests that require heavy models; mock external libs.
- When changing shared state, prefer per-request instantiation to avoid flakiness and race conditions.
- Add inline comments + docstrings where behavior is non-obvious (normalization choices, units, ranges).

How to signal completed tasks
-----------------------------
- Update the project's TODO list file (use existing tool `update_todo_list`) to reflect completed steps.
- Update this document by adding a "Completed tasks" section or marking checklist items as done.
- Example: when `salience_provider` request-scoped change is merged, mark:
  - [x] Make SalienceProvider request-scoped...

Change log (this document)
--------------------------
- 2025-08-13 — Created pipeline and initial assessment. Saved references to implementations and suggested pipeline.
- 2025-08-14 — Local development fixes and environment note:
  - [x] Fixed invalid replacement character in the frontend App component: [`frontend/src/App.jsx:151`](frontend/src/App.jsx:151)
  - [x] Removed malformed/duplicated export and added default export for the axios instance in [`frontend/src/services/api.js:108`](frontend/src/services/api.js:108)
  - [x] Verified Vite dev server successfully started and served at http://localhost:5174
  - [ ] Verify single active dev server (there was a stale Vite process on port 5173). Recommended action: kill the old process and hard-reload the browser to ensure consistent HMR and no stale builds.
- 2025-08-14 — Notes about impact:
  - The frontend fixes address parsing and runtime import errors encountered during local visual testing. These changes are low-risk and follow the "small and focused" principle from the Operational guidance section.
  - Add a short checklist to the pipeline to capture environment/CI hygiene actions so local dev issues don't block milestone progress.

Developer note & next steps
---------------------------
Recent local debugging resolved a blocking frontend build issue that would have interfered with delivering early milestones (notably M1 / sentence alignment scaffolding which requires a healthy local dev loop for frontend visualization). Based on the current pipeline and the roadmap for Hierarchical Module 3 (`docs/roadmap_hierarchical_module3_2025-08-10.md`), I recommend the following immediate next step:

1) Stabilize the local dev environment (quick, operational):
   - Kill the stale Vite process (port 5173) so only the active dev server remains (port 5174).
   - Hard-reload the browser to pick up the updated module graph and HMR state.
   - Confirm no remaining parse/runtime errors in the browser console and terminal.

Why this first:
- A stable local dev server ensures HMR and deterministic builds so that work on M1 (sentence alignment scaffold + visualization) isn't blocked by unrelated tooling noise.

2) Start M1 (development work that directly follows from the roadmap):
   - Create the scaffold for `sentence_alignment_service.py` and accompanying lightweight unit tests (see roadmap M1).
   - Add the feature-flag plumbing for `enable_sentence_alignment` so the service can be toggled without breaking existing endpoints.
   - Add a minimal frontend visualization hook / placeholder that will consume sentence-level alignment results when available (keeps frontend & backend integration tests actionable).

Why this second:
- M1 is the first numbered milestone in the roadmap and is the logical developer work after ensuring the dev loop is healthy. The sentence alignment layer enables hierarchical outputs required by later salience & strategy tasks.

Suggested short checklist to add to this document (I can update the file to include these as well if you want):
- [ ] Kill stale Vite process and confirm single dev server
- [ ] Hard-reload browser and verify no console errors
- [ ] Create `sentence_alignment_service.py` scaffold + tests (M1)
- [ ] Add `enable_sentence_alignment` feature flag
- [ ] Add minimal frontend hook/placeholder for sentence alignment output

References
- Roadmap: [`docs/roadmap_hierarchical_module3_2025-08-10.md:1`](docs/roadmap_hierarchical_module3_2025-08-10.md:1)
- Recent edits (frontend): [`frontend/src/App.jsx:151`](frontend/src/App.jsx:151), [`frontend/src/services/api.js:108`](frontend/src/services/api.js:108)

If you want, I can now:
- (A) Kill the stale Vite process and restart/verify the dev server (I will run the commands and report back), or
- (B) Immediately scaffold M1 (create the backend service file + tests) and add the feature flag plumbing.

Please choose (A) or (B) and I'll proceed.