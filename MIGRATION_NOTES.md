# Migration Notes – HITL Phase 1 (Stabilization & Data Integrity)

Date: 2025-09-07
Branch: `feature/hitl-phase1-stabilization`

## Summary
This phase introduces additive response fields and model attributes to support upcoming Human-in-the-Loop (HITL) workflows. No database schema changes were performed; persistence layer unaffected. All changes are backward-compatible.

## Added (API Response Level)
`ComparativeAnalysisResponse`:
- `model_version`
- `detection_config`

`SimplificationStrategy` (both model variants):
- `strategy_id`
- `source_offsets`
- `target_offsets`

Legacy fields (`sourcePosition`, `targetPosition`) retained.

## Feature Flags (see `docs/HITL_CONFIGURATION.md`)
- `HITL_MODEL_VERSION`
- `HITL_ALLOW_AUTO_OMISSION`
- `HITL_ALLOW_AUTO_PROBLEM`
- `HITL_ENABLE_POSITION_OFFSETS`
- `HITL_EXPOSE_DETECTION_CONFIG`
- `HITL_STRATEGY_ID_METHOD`

## Idempotency / Backwards Compatibility
- Clients ignoring new fields continue functioning.
- No renames; no removals.
- Strategy guardrails (OM+/PRO+) only restrict additions; they do not alter existing codes.

## Rollback
To revert Phase 1: revert commits in this branch or cherry-pick excluding files:
- `core/config.py` (remove new flags)
- `models/comparative_analysis.py` (remove added fields)
- `models/strategy_models.py` (remove added fields)
- `services/comparative_analysis_service.py` (remove enrichment + guardrail logic)

## Forward Plan Considerations
Phase 2 will rely on `strategy_id` and offsets; removing them later would break the HITL UI layer. Keep stable.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
