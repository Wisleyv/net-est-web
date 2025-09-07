# Changelog

## [Unreleased]
### Added
- Phase 1 HITL stabilization (branch `feature/hitl-phase1-stabilization`).
- Feature flags: `HITL_MODEL_VERSION`, `HITL_ALLOW_AUTO_OMISSION`, `HITL_ALLOW_AUTO_PROBLEM`, `HITL_ENABLE_POSITION_OFFSETS`, `HITL_EXPOSE_DETECTION_CONFIG`, `HITL_STRATEGY_ID_METHOD`.
- Additive response metadata: `model_version`, `detection_config`.
- Per-strategy fields: `strategy_id`, `source_offsets`, `target_offsets`.
- Documentation: `docs/HITL_CONFIGURATION.md`.
- Tests: `tests/test_hitl_phase1.py` verifying IDs, offsets, and guardrails.
- Demo script: `tools/demo_phase1_probe.py`.

### Changed
- Extended `SimplificationStrategy` models (both internal variants) with optional additive fields.
- Enhanced comparative analysis service to enforce OM+/PRO+ guardrails.

### Backward Compatibility
- No fields removed or renamed; changes are additive.
- Legacy `sourcePosition` / `targetPosition` remain intact.

---
/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
