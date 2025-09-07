# HITL Configuration (Phase 1 – Stabilization & Data Integrity)

This document describes newly introduced backend feature flags and response fields enabling Human-in-the-Loop workflows while maintaining full backward compatibility.

## New Environment / Settings Flags

| Flag | Default | Purpose | Notes |
|------|---------|---------|-------|
| `HITL_MODEL_VERSION` | `hitl-phase1-0.1` | Advertises model / rule bundle version | Included as `model_version` in responses. |
| `HITL_ALLOW_AUTO_OMISSION` | `False` | Allow automatic OM+ (Supressão Seletiva) suggestions | Must remain False unless explicitly approved; OM+ still manually annotatable later. |
| `HITL_ALLOW_AUTO_PROBLEM` | `False` | Allow automatic PRO+ (Desvio Semântico) suggestions | Always False for production; research override only. |
| `HITL_ENABLE_POSITION_OFFSETS` | `True` | Emit granular `{paragraph, sentence, char_start, char_end}` offsets | Heuristic char boundaries (sentence-level) in Phase 1; refined in later phases. |
| `HITL_EXPOSE_DETECTION_CONFIG` | `True` | Add `detection_config` block to API responses | Purely additive metadata. |
| `HITL_STRATEGY_ID_METHOD` | `uuid4` | Strategy ID generation method | Future option: `content-hash`. |

All flags map to `Settings` in `src/core/config.py` and can be overridden through `.env`.

## Response Additions (Additive Only)

`ComparativeAnalysisResponse` now includes:

```jsonc
{
  "model_version": "hitl-phase1-0.1",
  "detection_config": {
    "allow_auto_omission": false,
    "allow_auto_problem": false,
    "position_offsets": true,
    "strategy_id_method": "uuid4",
    "model_version": "hitl-phase1-0.1"
  }
}
```

Each strategy object now includes:

```jsonc
{
  "strategy_id": "uuid-v4",
  "code": "SL+",
  "source_offsets": {"paragraph":0, "sentence":0, "char_start":0, "char_end":32},
  "target_offsets": {"paragraph":0, "sentence":0, "char_start":0, "char_end":30}
}
```

Legacy fields (`sourcePosition`, `targetPosition`) are preserved for existing UI compatibility.

## Guardrails

- OM+ and PRO+ are filtered out of automatic detection unless their respective flags are set `True`.
- Manual insertion (future phases) will not require enabling these flags.

## Strategy ID Semantics

- Default method `uuid4` ensures uniqueness and decouples IDs from content changes (stable per response instance, not across re-runs yet).
- Future `content-hash` mode will yield deterministic IDs for identical detections; introduced later to avoid premature coupling.

## Migration & Backward Compatibility

- No existing field removed or renamed.
- Consumers ignoring new fields continue to function unchanged.
- Downstream logging/analytics can safely record `strategy_id` when present.

## Example cURL

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/comparative-analysis/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "Texto original longo.",
    "target_text": "Texto simplificado.",
    "analysis_options": {"include_strategy_identification": true}
  }' | jq '.model_version, .detection_config, .simplification_strategies[0]'
```

## Next Phases (Preview)

Later phases will introduce: manual annotation endpoints, explanation templates, validation workflow, and gold dataset export. Those will extend – not replace – the structures defined here.

---
/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
