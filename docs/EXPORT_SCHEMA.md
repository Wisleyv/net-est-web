## Phase 4e: Gold Annotations Export

New fields and options to support ML-ready exports:

- API: `POST /api/v1/annotations/export?session_id=...&format=jsonl|csv&scope=gold|raw|both`
- CLI: `python -m src.tools.export --session <id> --type annotations --format jsonl|csv --scope gold|raw|both`

Record fields (JSONL/CSV):
- id, session_id, strategy_code, original_code
- status: lifecycle status (pending|accepted|rejected|modified|created)
- decision: alias of status for ML pipelines
- origin, confidence
- source_offsets, target_offsets
- created_at, updated_at, updated_by
- evidence, comment
- explanation: human-readable rationale
- validated: boolean, true when accepted by a human (gold)
- manually_assigned: boolean, true when created directly by a human

Scope semantics:
- gold: only records with validated=true and status in {accepted, created}
- raw: unvalidated predictions, status in {pending, modified}
- both: all non-rejected records (default)

Example (JSONL):
{"id":"...","session_id":"S1","strategy_code":"OM+","status":"accepted","decision":"accepted","validated":true,"manually_assigned":true,"explanation":"..."}

# Export Schema (Phase 4e)

This document defines the canonical export schema for annotations and audit logs across persistence backends (FS and SQLite). The schema is deterministic and versioned to support analytics and ML datasets.

Schema version: 1.0.0

## Annotation Record

Fields (annotations.*):

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| id | string | Annotation UUID | Stable per session |
| session_id | string | Session identifier | Included in export file for multi-session joins |
| strategy_code | string | Current (possibly modified) strategy code | Original version stored in original_code when modified |
| original_code | string/null | Pre-modification code | Only set after first modify action |
| status | string | One of accepted / modified / created | Rejected excluded by default filter |
| origin | string | machine or human | Manual creates = human |
| confidence | number/null | Confidence score if available | 0-1 range |
| source_offsets | JSON array/null | List of {start,end} offsets in source text | May be null |
| target_offsets | JSON array/null | List of {start,end} offsets in target text | Required for manual creates |
| created_at | string (ISO-8601) | Creation timestamp UTC | Normalized to Z in CLI jsonl |
| updated_at | string (ISO-8601) | Last update timestamp UTC | |
| updated_by | string/null | Session ID or user applying last action | |
| evidence | JSON array/null | Evidence feature strings | Optional |
| comment | string/null | Free-form user comment | Manual creates/modifications |
| explanation | string/null | Human-readable rationale template | Added Phase 4f (SL+, RP+ initial templates) |

Notes:
- explanation is generated lazily on create / modify / accept for supported strategy codes. If missing at export time for eligible codes it is backfilled (FS & SQLite parity).

### JSONL Example (annotations)
```
{"id":"...","session_id":"sess123","strategy_code":"SL+","status":"created","origin":"human","confidence":null,"source_offsets":null,"target_offsets":[{"start":0,"end":3}],"created_at":"2025-09-10T14:34:10.042533Z","updated_at":"2025-09-10T14:34:10.042536Z","updated_by":null,"evidence":null,"comment":"primeiro","explanation":"Adequação de Vocabulário: substituições léxicas sugerem simplificação (confiança 0%)."}
```

### CSV Header (annotations.csv)
```
id,session_id,strategy_code,original_code,status,origin,confidence,source_offsets,target_offsets,created_at,updated_at,updated_by,evidence,comment,explanation
```
Only accepted/modified/created statuses are exported by default; pass --statuses to override.

## Formats
- JSONL: one record per line (type field differentiates)
- CSV: two files: annotations.csv, audit.csv (normalized)

## Determinism
- Stable ordering by (session_id asc, created_at asc, id asc)
- Normalize timestamps to UTC with 'Z' suffix

## Feature Flags & Guardrails
- Exports MUST respect frontend feature flags, notably `enableAuditSearch` paths.
- Validate under both persistence modes: FS and SQLite, with dual-write/fallback if enabled.

## CLI Usage
- Module: `python -m src.tools.export`
- Args:
	- `--session <id>` (required)
	- `--format jsonl|csv` (default jsonl)
	- `--out <dir>` (default `export`)
	- `--statuses <list>` (optional filter)
- Output files:
	- `<session>.annotations.jsonl` or `<session>.annotations.csv`
	- Records include `session_id` to support multi-session analytics.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
