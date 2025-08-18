# NET-EST Algorithm & Architecture v3.0 (Consolidated Update – 2025-08-10)

"Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA"

## 0. Executive Overview

This document consolidates the original proposta_arquitetura_algoritmo.md with the 2025-08-10 Module 3 hierarchical update and maps it against the current implemented code (backend + frontend). It provides: (1) status assessment, (2) variances vs. original plan, (3) integrated revised pipeline, (4) risk & mitigation plan, (5) incremental roadmap to reach production-readiness.

## 1. Current Implementation Status (As of 2025-08-10)

Legend: ✅ Implemented | 🟡 Partial / Basic | 🔴 Missing | 🧪 Planned refinement

| Module                                                 | Planned Scope                                                                         | Current State | Notes                                                                                                                                                                                                     |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Pre-process / Input                                 | Dual text input, basic validation, paragraph segmentation                             | ✅             | Frontend provides dual input; backend expects raw strings; no multi-format ingestion yet (.pdf/.docx).                                                                                                    |
| 2. Semantic Alignment (Paragraph)                      | Embedding-based alignment + unaligned detection + similarity matrix                   | ✅ (robust)    | Implemented in semantic_alignment_service.py using MiniLM (updated), caching, thresholds, stats, confidence tiers.                                                                                        |
| 3. Strategy Extraction & Classification (Hierarchical) | Discourse→Sentence→Phrase staged analysis with weighted rules + feedback adaptability | 🟡            | Current strategy_detector.py: single-pass feature extraction + evidence classifier at global text-pair level; no multi-level alignment (sentence/phrase) or key-phrase weighting yet; partial heuristics. |
| 4. UI Rendering & Interaction                          | Side-by-side view, highlighting, strategy legends, tagging overlay                    | ✅             | ComparativeResultsDisplay + SideBySideTextDisplay + InteractiveTextHighlighter (baseline). No hierarchical drill-down yet.                                                                                |
| 5. Feedback Capture / Knowledge Store                  | Endpoint + persistence for corrected tags                                             | 🔴            | Not yet implemented; no persistence layer (session only).                                                                                                                                                 |
| 6. Report Generation / Export                          | PDF / structured export                                                               | 🟡            | Export button present; backend PDF/report logic not fully centralized.                                                                                                                                    |
| 7. Hosting / Deployment Strategy                       | Decoupled FE (Vercel) + BE (HF Spaces) + external DB                                  | 🧪            | Architectural intent documented; code containerization present (Dockerfile). No CORS hardening / external DB wiring yet.                                                                                  |
| Cross-Cutting: Configurable Tag Weights                | user_config controlling activation + weights                                          | 🔴            | Strategy detector lacks dynamic per-tag config injection.                                                                                                                                                 |
| Cross-Cutting: Analytics (Session)                     | In-memory metrics, export                                                             | ✅             | analytics_service.py present (session-based).                                                                                                                                                             |
| Cross-Cutting: Caching & Performance                   | Embedding cache, truncated analysis for large texts                                   | ✅             | Implemented (MiniLM, truncation at 5000 chars).                                                                                                                                                           |
| Cross-Cutting: Explainability                          | Feature-level evidence surfaced to UI                                                 | 🟡            | Evidence objects exist internally but not fully exported to frontend.                                                                                                                                     |

## 2. Variance vs. Original Algorithm Proposal

| Planned Principle                                                | Status Gap                                                     | Impact                                                         | Mitigation                                                                       |
| ---------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Discourse-first hierarchical cascade (Paragraph→Sentence→Phrase) | Only paragraph-level + whole-text features                     | Moderate: limits precision of SL+, RP+, EXP+, MOD+ granularity | Introduce sentence alignment layer + targeted micro-diff engine (see Section 4). |
| Human-in-the-loop (editable + feedback loop)                     | UI partially editable; no feedback persistence                 | High: cannot learn from corrections                            | Implement /api/v1/feedback with queue + future DB adapter.                       |
| Modular interchangeability (ML vs heuristic)                     | Modules partially coupled inside comparative_analysis_service  | Low                                                            | Add abstraction interfaces (IAlignmentService, IStrategyPipeline).               |
| Weighted rule engine w/ user_config                              | Hard-coded thresholds                                          | Medium: no customization                                       | Inject config object down to classifier; expose settings in UI panel.            |
| Strategy confidence explainability                               | Confidence derived but not surfaced with feature contributions | Medium: reduces trust                                          | Include feature vector + top contributing signals in API payload.                |
| Key-phrase salience (LangExtract)                                | Not implemented                                                | Moderate: SL+ signal weaker                                    | Add pluggable salience provider with graceful fallback.                          |
| Multilevel metrics aggregation                                   | Only global summary (some lexical/syntactic)                   | Low                                                            | Derive per-level counts once hierarchical pipeline lands.                        |

## 3. Integrated Revised Pipeline (Incorporating Module 3 Update)

### 3.1 Target Hierarchical Flow

1. Input (Module 1) → normalized source/target paragraphs.
2. Paragraph Alignment (Module 2) → aligned_pairs + unaligned_source.
3. For each aligned paragraph pair:
   a. Sentence Segmentation → sentence lists.
   b. Sentence Embedding Alignment (MiniLM) → aligned_sentence_pairs + splits (fragmentation) + merges.
   c. For each aligned sentence pair:
   - Micro diff (token spans) using diff/levenshtein + POS from spaCy
   - Key phrase extraction (LangExtract or fallback TF-IDF) on source sentence
   - Operation classification (replace/delete/insert).
4. Feature Extraction Hierarchy:
   - Paragraph Level: length ratios, semantic similarity, structural markers, order shift.
   - Sentence Level: fragmentation (RP+), explicitness (EXP+), semantic drift (AS+), multi-map (one→many).
   - Phrase/Token Level: lexical complexity delta (SL+), pronoun→noun (TA+), voice shift (MV+), content structuring markers (RD+), perspective reinterpretation (MOD+) via semantic + lexical divergence pattern.
5. Scoring & Aggregation:
   - Each candidate strategy builds evidence object with: level, scope indices, features, base confidence.
   - Apply user_config weights: adjusted_confidence = base_confidence * weight.
   - De-duplicate overlapping strategies (keep higher confidence or escalate to multi-span variant).
6. Output Assembly:
   - Hierarchical JSON tree: paragraphs[] → sentences[] → operations[] with their attached strategies.
   - Flattened strategies list for UI summary.
7. Feedback Integration (Module 5):
   - UI edits produce PATCH/POST with context (paragraph_index, sentence_index, original_tag, corrected_tag, text_snippets, timestamp, optional rationale).
   - Backend stores feedback events for future ML training.

### 3.2 Updated Module 3 Responsibilities

| Stage                | Function                        | Key Artifacts                    | Risks                                                                       |
| -------------------- | ------------------------------- | -------------------------------- | --------------------------------------------------------------------------- |
| Macro (Paragraph)    | detect OM+, RF+, RD+, DL+       | aligned_pairs metadata           | Over-alignment false positives → calibrate threshold & fallback heuristics. |
| Meso (Sentence)      | detect RP+, EXP+, AS+           | aligned_sentence_pairs           | Sentence boundary accuracy in Portuguese; fallback regex.                   |
| Micro (Phrase/Token) | detect SL+, TA+, MV+, MOD+, IN+ | diff operations + POS + salience | Performance if all tokens embedded; restrict to high-value operations.      |

### 3.3 Confidence Model (Proposed)

Confidence = (SemanticTerm * α + LexicalTerm * β + StructuralTerm * γ + SalienceBoost + Penalties) * Weight(tag)

Recommended initial weights: α=0.35, β=0.25, γ=0.25, SalienceBoost ≤ 0.15. Normalize to [0,1].

### 3.4 Data Structures (Additions)

```json
{
  "hierarchical_result": {
    "paragraphs": [
      {
        "source_index": 0,
        "target_index": 0,
        "similarity": 0.88,
        "strategies": [ { "tag": "RF+", "confidence": 0.82 } ],
        "sentences": [
          {
            "source_index": 0,
            "target_index": 0,
            "strategies": [ { "tag": "EXP+", "confidence": 0.74 } ],
            "operations": [
              {
                "type": "replace",
                "source_span": "fatores psicossociais",
                "target_span": "aspectos sociais",
                "salient": true,
                "strategies": [ { "tag": "SL+", "confidence": 0.86 } ]
              }
            ]
          }
        ]
      }
    ]
  },
  "flat_strategies": [ ... existing SimplificationStrategy objects ... ]
}
```

### 3.5 Extensibility Interfaces

Introduce abstract interfaces to decouple services:

- IAlignmentService: align_paragraphs(), align_sentences()
- IFeatureExtractor: extract(level, scope)
- IStrategyRule: evaluate(context) → evidence | None
- IFeedbackStore: record(event), query(filters)

## 4. Gap Remediation & Improvement Measures

| Gap                                         | Proposed Action                                                                                                | Effort (S/M/L) | Priority |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------- | -------- |
| Lack of sentence-level alignment            | Implement sentence alignment using existing MiniLM model with caching; add max sentence cap & streaming yield  | M              | P1       |
| Missing micro diff layer                    | Introduce token diff module (difflib + POS) with salience filter                                               | M              | P1       |
| Key phrase weighting absent                 | Add SalienceProvider (LangExtract adapter → fallback TF-IDF)                                                   | S              | P1       |
| No user_config weighting                    | Add config schema + propagate to classifier; expose endpoint & FE settings drawer                              | S              | P1       |
| Feedback persistence                        | Implement /api/v1/feedback + pluggable store (in-memory → SQLite adapter)                                      | M              | P1       |
| Confidence opacity                          | Return feature vector & top contributions in API strategy objects                                              | S              | P2       |
| Performance risk (hierarchical)             | Early exits: limit sentences per paragraph, skip micro-analysis if semantic_similarity > 0.93 & low diff ratio | S              | P2       |
| Absence of PRO+ safeguard logic centralized | Central flag (already) + enforce at final aggregation stage                                                    | S              | P2       |
| Report generator fragmented                 | Centralize report builder service formatting hierarchical + flat views                                         | M              | P2       |
| Deployment CORS hardening                   | Add configurable ALLOWED_ORIGINS env; enforce in FastAPI middleware                                            | S              | P2       |
| External DB for feedback                    | Add adapter pattern for Neon/Supabase; feature flag                                                            | M              | P3       |

## 5. Incremental Roadmap (4 Iterations)

### Iteration 1 (Foundational Hierarchy)

- Sentence alignment service method + tests.
- Micro diff scaffold (operations classification stub).
- Integrate hierarchical_result into ComparativeAnalysisResponse (optional flag include_hierarchy).
- Add user_config to request schema; pass to strategy detector.

### Iteration 2 (Salience & Confidence)

- SalienceProvider (LangExtract→TF-IDF fallback).
- Modify SL+/EXP+ scoring to incorporate salience.
- Unified confidence formula implementation.
- Return feature_contributors array per strategy (top 3 features + weights).

### Iteration 3 (Feedback Loop & Storage)

- /api/v1/feedback endpoint (POST, GET session scoped).
- In-memory FeedbackStore + SQLite adapter behind repo pattern.
- Frontend: allow tag edit + reason modal; optimistic update + rollback on failure.
- Analytics: track correction counts and strategy drift frequency.

### Iteration 4 (Reporting & Deployment Hardening)

- ReportBuilder: Markdown + PDF export (hierarchical + summary toggle).
- Configurable CORS origins + rate limiting middleware (basic token bucket optional).
- Optional external DB plug-in for feedback (env-based switch).
- Performance tuning (profiling longest paragraphs; embed caching hits metric).

## 6. Data & Performance Considerations

| Aspect          | Strategy                                                                                                         |
| --------------- | ---------------------------------------------------------------------------------------------------------------- |
| Embedding reuse | Existing embedding cache; extend to sentence level with composite key paragraphIdx:sentenceIdx:textHash.         |
| Large texts     | Early truncation already; add adaptive sampling for paragraphs > N tokens before micro-analysis.                 |
| Memory pressure | Cap sentence embeddings per paragraph (e.g., first 12 sentences or top salient by TF-IDF).                       |
| Latency budget  | Target < 6s for 1500-word pair on CPU: allocate ~40% alignment, 35% hierarchical extraction, 25% classification. |
| Fault tolerance | Graceful degradation: if sentence alignment fails → fall back to paragraph-only strategies.                      |

## 7. API Contract Adjustments (Proposed Additions)

Request (new fields):

- analysis_options.include_hierarchical: bool
- user_config: { TAG: { active: bool, weight: float } }

Response (extensions):

- hierarchical_result (see Section 3.4)
- strategies[i].feature_contributors: [{ name, value, weight_contribution }]
- feedback_supported: bool

## 8. Security & Integrity

| Concern                                  | Mitigation                                                                          |
| ---------------------------------------- | ----------------------------------------------------------------------------------- |
| Tag spoofing (client alters tag locally) | Recompute server-side confidence upon feedback receipt; store original + corrected. |
| Model supply variance                    | Pin model name & checksum in config; log mismatch warnings.                         |
| Data privacy (feedback texts)            | Hash paragraph IDs; optionally store only spans necessary for learning.             |

## 9. Future ML Evolution Path

Phase A: Collect feedback events (minimum 500 curated corrections).  
Phase B: Train lightweight classifier (e.g., gradient boosting over engineered features + salience flags).  
Phase C: Replace individual rule thresholds with learned probability calibration.  
Phase D: Fine-tune domain-specific Portuguese MiniLM variant (if licensing permits).  

## 10. Acceptance Criteria for v3.0 Completion

| Criterion                        | Definition                                                        |
| -------------------------------- | ----------------------------------------------------------------- |
| Hierarchical Enabled             | API returns hierarchical_result for >90% analyses without error.  |
| Strategy Confidence Transparency | Each strategy lists top 3 feature contributors.                   |
| Feedback Persistence             | Edits survive server restart (SQLite).                            |
| Salience Impact                  | SL+ confidence > baseline in ≥70% cases where key phrase flagged. |
| Performance                      | P95 processing time < 8s for 2k-word input pair on CPU.           |
| Configurability                  | Disabling a tag in user_config reduces its occurrences by ≥95%.   |

## 11. Implementation Sequencing Dependencies

1. Sentence alignment requires no DB changes → safe first.
2. Micro diff depends on sentence segmentation.
3. Salience weighting depends on micro diff tokens & sentence boundaries.
4. Feedback persistence can be built in parallel once strategy IDs stable.

## 12. Summary

The system is strongly aligned with the Discourse-first and Modular principles at the paragraph layer but requires hierarchical deepening and persistence features to unlock adaptive intelligence. The integrated roadmap prioritizes high-impact enhancements (hierarchical strategy fidelity, feedback loop, explainability) while controlling latency through caching, sampling, and staged fallbacks.

---
---

Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
