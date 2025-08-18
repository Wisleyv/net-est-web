# Module 3 (Hierarchical Strategy Extraction & Classification) Implementation Checklist

**Date:** 2025-08-12

This checklist is based on the consolidated algorithm documentation and current project status.

---

## 1. Sentence-Level Alignment
- [ ] Implement sentence segmentation for each aligned paragraph pair.
- [ ] Align sentences using MiniLM embeddings (with caching).
- [ ] Handle sentence splits/merges and unaligned sentences.

## 2. Micro-Diff Layer (Phrase/Token)
- [ ] For each aligned sentence pair, compute token/phrase-level diffs (e.g., using difflib + spaCy POS).
- [ ] Classify operations: replace, delete, insert.
- [ ] Extract key phrases from source sentences (LangExtract or TF-IDF fallback).

## 3. Hierarchical Feature Extraction
- [ ] Extract features at paragraph, sentence, and phrase/token levels.
- [ ] Detect and tag strategies: RP+, EXP+, AS+, SL+, TA+, MV+, MOD+, IN+, etc.
- [ ] Build evidence objects with level, scope, features, and base confidence.

## 4. Scoring & Aggregation
- [ ] Implement unified confidence formula (semantic, lexical, structural, salience, penalties, weights).
- [ ] Apply user_config weights to adjust confidence.
- [ ] De-duplicate overlapping strategies.

## 5. Output Structure
- [ ] Assemble hierarchical JSON result: paragraphs → sentences → operations (with strategies).
- [ ] Provide flattened strategies list for UI summary.

## 6. User Configurability
- [ ] Add user_config schema for tag activation and weights.
- [ ] Propagate config to strategy detector and scoring logic.
- [ ] Expose config options in frontend (settings panel).

## 7. Explainability
- [ ] Return feature_contributors (top 3 features + weights) for each strategy in API response.
- [ ] Surface evidence and confidence details to frontend.

## 8. Feedback Integration
- [ ] Implement /api/v1/feedback endpoint (POST, GET).
- [ ] Store feedback events (in-memory, then SQLite adapter).
- [ ] Allow frontend tag edits with rationale and optimistic update.

## 9. Testing & Validation
- [ ] Unit and integration tests for sentence alignment, micro-diff, and hierarchical extraction.
- [ ] Validate confidence and salience impact on strategy detection.

## 10. Documentation & Reporting
- [ ] Update docs to reflect new pipeline and API contract.
- [ ] Centralize report generation for hierarchical and summary views.

---

Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
