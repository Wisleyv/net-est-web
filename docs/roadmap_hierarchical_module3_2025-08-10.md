# NET-EST Roadmap: Hierarchical Module 3 & Salience Expansion (Post `algorithm_v3_consolidated_2025-08-10.md`)

## 0. Purpose

Provide a concrete, execution-focused roadmap translating the design & gap analysis in `algorithm_v3_consolidated_2025-08-10.md` into sequenced milestones with scope, deliverables, acceptance criteria, risks, and lightweight test strategy. This file is the operational companion to the conceptual spec.

## 1. Guiding Principles (Ref: Sections 2, 4, 5 of consolidated algorithm doc)

1. Add hierarchy incrementally: Paragraph ➜ Sentence ➜ Micro-span (token / phrase).
2. Maintain backward compatibility of current API until new response schema is versioned (`/api/v1/comparative-analysis/` returns legacy flat structure unless `hierarchical_output=true`).
3. Salience & confidence always explainable (expose feature contributors when requested: `debug_features=true`).
4. No premature ML: rule + feature transparency first; data collection (feedback loop) second; modeling third.
5. Every milestone must add at least one new automated test & one documentation delta.

## 2. Milestone Summary Table

| Milestone | Title                                      | Core Theme                  | Depends On                   | Target Outcome                                           |
| --------- | ------------------------------------------ | --------------------------- | ---------------------------- | -------------------------------------------------------- |
| M1        | Sentence Alignment Layer                   | Hierarchy foundation        | Existing paragraph alignment | Reliable P↔S↔S mapping with confidence tiers             |
| M2        | Hierarchical Data Model & API v1.1         | Data struct & serialization | M1                           | Unified JSON tree + optional legacy flattening           |
| M3        | Salience Provider (Keyphrase + Fallback)   | Salience weighting          | M2                           | Ranked salient units influencing strategy weights        |
| M4        | Strategy Detector Cascade Refactor         | Modular cascade             | M3                           | Macro→Meso→Micro staged evaluation & pruning             |
| M5        | Confidence & Weighting Engine              | Scoring layer               | M4                           | Unified confidence formula + per-strategy attribution    |
| M6        | Feedback Capture & Persistence Abstraction | Human-in-loop loop          | M5                           | Endpoint + local storage adapter (file/JSON)             |
| M7        | Analytics & Reporting Consolidation        | Observability               | M6                           | Exportable session analytics + structured report builder |
| M8        | Performance & Caching Optimizations        | Scale                       | M7                           | Measured latency reduction & memory bounds               |
| M9        | Hardening, Docs & Release                  | Stabilization               | All prior                    | Versioned release + migration guidance                   |

## 3. Detailed Milestones

### M1. Sentence Alignment Layer (Ref: Sections: Alignment Gaps, Roadmap Step 1)

Objectives:

- Implement sentence segmentation (spaCy if available; fallback regex / nltk-like simple splitter).
- For each aligned paragraph pair, compute sentence embeddings & similarity matrix.
- Produce alignment tuples (source_sentence_ids, target_sentence_ids, score, status: {aligned, split, merged, unmatched}).
- Confidence tiers derived from similarity + dispersion metrics.

Deliverables:

- `src/services/sentence_alignment_service.py` (new).
- Unit tests: paragraph w/ 1:1, 1:2 split, 2:1 merge, and unmatched cases.
- Update existing `semantic_alignment_service` (non-breaking) to call sentence layer when flag `enable_sentence_alignment=True`.

Acceptance Criteria:

- ≥95% correct mapping on synthetic test cases.
- Adds <15% runtime overhead relative to baseline paragraph-only run on sample test payload.

Risks & Mitigations:

- R: spaCy model missing. M: graceful fallback + warn once.
- R: O(N^2) sentence similarity blow-up. M: cap sentences per paragraph or use top-k pruning.

### M2. Hierarchical Data Model & API v1.1 (Ref: Data Model Section)

Objectives:

- Define internal classes: ParagraphNode, SentenceNode, MicroSpanNode (placeholder), StrategyAnnotation.
- Serializer producing nested JSON (`hierarchy_version: 1.1`).
- Add query param / request option `hierarchical_output`.
- Preserve legacy flat `strategies` list when flag is false.

Deliverables:

- `src/models/hierarchy.py`.
- Modified comparative analysis response schema.
- Tests: serialization round-trip + backward compatibility test.

Acceptance Criteria:

- Legacy clients unaffected (snapshot test equality for prior default request).
- Hierarchical response passes JSON schema validation.

Risks:

- Scope creep into micro-span too early: explicitly defer micro-span extraction to M4.

### M3. Salience Provider (Ref: Salience Weighting Section)

Objectives:

- Introduce abstraction `SalienceProvider` with method: `extract(document_text, sentences)` ➜ list of {unit, type, weight, span_indices}.
- Provide fallback implementations: KeyBERT (if installed), YAKE, and a trivial frequency/TF-IDF baseline.
- Map salience outputs to sentence & paragraph nodes; propagate normalized weights (0–1).

Deliverables:

- `src/services/salience_provider.py`.
- Config option: `salience_method` (env / request override).
- Tests: deterministic output using mocked embeddings / seeded randomness.

Acceptance Criteria:

- Runs without external model if no optional deps present (baseline path).
- Salience influences strategy weighting (logged when `debug_features=true`).

Risks:

- Extra latency from keyphrase extraction. Mitigate with result caching keyed by text hash.

### M4. Strategy Detector Cascade Refactor (Ref: Cascade Pipeline Section)

Objectives:

- Split current monolithic `strategy_detector` into staged evaluators: Macro (paragraph diffs), Meso (sentence operations), Micro (token/phrase heuristics placeholder).
- Early exit pruning: if macro stage rejects candidate paragraphs, skip deeper stages.
- Record evidence chain per strategy node reference.

Deliverables:

- Refactored `strategy_detector.py` ➜ orchestrator.
- New modules: `strategies/stage_macro.py`, `strategies/stage_meso.py`, `strategies/stage_micro.py`.
- Tests: ensure identical (or improved) detection vs baseline on existing test corpus; add performance snapshot.

Acceptance Criteria:

- Equal or higher F1 (proxy via heuristic assertions) on existing tests.
- Mean latency increase ≤10% pre-optimization; doc improvement plan.

Risks:

- Regression risk in rules: mitigate with golden fixture tests from pre-refactor output.

### M5. Confidence & Weighting Engine (Ref: Confidence Formula Section)

Objectives:

- Implement formula combining similarity scores, salience aggregation, evidence count, and penalty factors.
- Provide per-strategy confidence plus global analysis confidence.
- Expose optional breakdown object when `include_confidence_breakdown=true`.

Deliverables:

- `src/services/confidence_engine.py`.
- Update strategy annotation schema with `confidence` & `contributors`.
- Tests: boundary cases (max, min, missing salience) and monotonicity checks.

Acceptance Criteria:

- Confidence within [0,1]; monotonic increase with added positive evidence in tests.

Risks:

- Overfitting to heuristics; keep formula weights configurable in config file.

### M6. Feedback Capture & Persistence Abstraction (Ref: Feedback Loop Section)

Objectives:

- Implement endpoint `POST /api/v1/feedback` (temporary in-memory/file store).
- Feedback schema: {session_id, strategy_id, action: {confirm|reject|adjust}, note?, suggested_tag?}.
- Add simple repository interface with pluggable backend (future DB).

Deliverables:

- `src/routers/feedback.py`.
- `src/repositories/feedback_repository.py` (file-based JSON store by default).
- Tests: submit, retrieve (if GET support added), and persistence across process restarts (file mode only).

Acceptance Criteria:

- Feedback call <100ms avg on sample data.
- Persists at least 100 feedback items without degradation.

Risks:

- Concurrency on file writes: mitigate with append+atomic rename or threading lock.

### M7. Analytics & Reporting Consolidation (Ref: Analytics & Reporting Sections)

Objectives:

- Unify session metrics + hierarchical analysis snapshot into export builder.
- Provide `/api/v1/analytics/export?format=json|markdown`.
- Add basic Markdown report: summary table + strategy distribution + salience highlights.

Deliverables:

- `src/services/report_builder.py`.
- Router extension for export.
- Tests: stable deterministic export on fixture input.

Acceptance Criteria:

- Report generation <300ms on medium sample.
- Markdown passes lint (optional) and includes required sections.

### M8. Performance & Caching Optimizations (Ref: Performance Considerations)

Objectives:

- Introduce layered cache (paragraph embeddings → sentence embeddings → salience).
- Add timing instrumentation & log summary when `performance_logging=true`.
- Optimize similarity matrix operations (vectorized or approximate if needed).

Deliverables:

- `src/utils/perf_metrics.py`.
- Caching enhancements in alignment & salience providers.
- Benchmark script `scripts/benchmark_sample.py`.

Acceptance Criteria:

- ≥25% reduction in median end-to-end latency vs post-M7 baseline on sample dataset.
- Memory footprint stable (no unbounded cache growth) verified via simple stress test.

Risks:

- Premature optimization: defer aggressive techniques until baseline measurements captured.

### M9. Hardening, Documentation & Release (Ref: Rollout & Versioning Section)

Objectives:

- Version bump (e.g., API minor version 1.1) + change log.
- Migration guide summarizing request/response changes & flags.
- Security & CORS review; configurable allowed origins.
- Final integration tests across full pipeline.

Deliverables:

- `CHANGELOG.md` (add section).
- `docs/migration_guide_v1_0_to_v1_1.md`.
- Integration test covering hierarchical + salience + feedback path.

Acceptance Criteria:

- All tests green in CI.
- Zero Pydantic validation errors on staged sample requests.

## 4. Cross-Cutting Concerns

Observability:

- Structured logging context keys: request_id, session_id, stage, duration_ms.
  Configuration:
- Centralize new flags in a single config module with env + request override precedence order.
  Testing Strategy Layers:
- Unit (pure functions), Functional (service orchestrations), Integration (API endpoints), Regression (golden outputs), Performance (benchmark script), Property-based (optional for alignment invariants).

## 5. Proposed Sequencing & Timeboxing (Indicative)

- Week 1: M1
- Week 2: M2 + start M3
- Week 3: Finish M3, start M4
- Week 4: Finish M4, M5
- Week 5: M6 + M7
- Week 6: M8 baseline + optimizations
- Week 7: M9 hardening & release prep

## 6. Metrics Dashboard (Initial Set)

- Alignment: sentence_alignment_precision, sentence_alignment_recall (synthetic set)
- Performance: e2e_latency_ms_p50/p95, embedding_cache_hit_ratio
- Strategy Quality: strategies_detected_per_1k_tokens, mean_strategy_confidence
- Feedback: feedback_items_collected, agreement_rate
- Salience: mean_salience_weight_top5, salience_coverage (sentences with ≥1 salient unit)

## 7. Risk Register (Condensed)

| Risk                                   | Impact                            | Likelihood | Mitigation                                     |
| -------------------------------------- | --------------------------------- | ---------- | ---------------------------------------------- |
| Sentence alignment poor on noisy input | Low-quality downstream strategies | Medium     | Hybrid threshold + fallback lexical similarity |
| Salience lib adds heavy deps           | Increased cold start              | Medium     | Lazy import + optional extras group            |
| Cascade increases latency              | Slower UX                         | Medium     | Early pruning + caching                        |
| Feedback store race conditions         | Data loss                         | Low        | File lock + future DB adapter                  |
| Confidence misunderstood               | Misinterpretation by users        | Medium     | Provide breakdown & docs                       |

## 8. Definition of Done (Overall Initiative)

All milestones delivered; hierarchical output enabled & documented; salience weighting and confidence integrated; feedback captured; analytics/export unified; performance targets met; release artifacts published; migration guide validated by test run.

## 9. Immediate Next Actions Snapshot

1. Create `sentence_alignment_service.py` scaffold + tests (M1).
2. Add feature flag plumbing (`enable_sentence_alignment`).
3. Generate golden output fixture of current (pre-hierarchy) analysis for regression lock.

---

Questions or deviations should be appended to this file under an "Amendments" heading with timestamped entries.

Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
