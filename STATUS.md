# NET-EST project status snapshot (2025-09-21)

This is a lightweight status for quick onboarding and planning. It synthesizes objectives, the core pipeline, what’s shipped vs. planned, and a few immediate next steps.

## Objectives
- Human-in-the-loop platform for intralingual translation (simplification).
- Align source/target, detect strategies with explainable confidence, and capture feedback.
- Persist annotations (FS/SQLite/dual), export ML-ready datasets (gold/raw/both), and support session analytics.

## Core pipeline (backend)
- Input and feature flags via `ComparativeAnalysisRequest` and `AnalysisOptions`.
- Alignment: paragraphs → sentences (semantic + cosine), optional micro-spans.
- Cascade strategy detection (macro → meso → micro) with a confidence engine and salience provider.
- Hierarchical output (paragraphs, sentences, optional micro-spans), position tracking, and salience normalization.
- Persistence abstraction (FS/SQLite/dual-write with fallback) and feedback repository.
- Exports: deterministic schema for gold/raw/both.

Key files: `backend/src/services/comparative_analysis_service.py`, `backend/src/services/{strategy_detector,salience_provider,langextract_provider,confidence_engine}.py`, models in `backend/src/models/`, repositories in `backend/src/repository/`.

## Current vs. target
- Done: end-to-end HITL flow, strategy detection cascade, confidence explanations, hierarchical output (M2/M3), micro-spans (M4 experimental), feedback, deterministic exports, robust tests around persistence/export.
- Partial: hierarchical UX, analytics dashboards, salience A/B (LangExtract) scaffolding, observability, broader E2E.
- Planned: ML-based classification to augment rules, richer analytics, stronger A/B harness, accessibility/perf hardening.

## Risks and notes
- Rule-based brittleness on edge cases; use flags and tests to guard behavior.
- Alignment + micro-spans increase offset complexity—keep tests for bounds/normalization.
- Dual-write requires drift checks; keep monitoring and fallbacks.

## Near-term next steps
- Expand hierarchy tests (node integrity, offsets, salience ranges) and wire small UI affordances.
- Simple A/B harness for salience (base vs. LangExtract) with overlap/quality logs already supported.
- Ship a thin analytics view (counts, distributions) backed by session metrics and export sampling.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
