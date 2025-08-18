# Hierarchical Pipeline — Design, Data Structures, and API Changes

This document describes the hierarchical pipeline integration implemented for comparative analysis:
- dataclass node models and their location
- how the comparative analysis service builds and serializes hierarchical output
- API surface changes and expected JSON shapes
- testing notes and developer guidance for extending or debugging the pipeline

Files referenced in this document (click to open):
- [`backend/src/models/hierarchical_nodes.py`](backend/src/models/hierarchical_nodes.py:1)
- [`backend/src/models/comparative_analysis.py`](backend/src/models/comparative_analysis.py:1)
- [`backend/src/services/comparative_analysis_service.py`](backend/src/services/comparative_analysis_service.py:1)
- [`backend/tests/test_hierarchical_integration.py`](backend/tests/test_hierarchical_integration.py:1)
- [`backend/tests/test_hierarchical_output.py`](backend/tests/test_hierarchical_output.py:1)

1) Purpose and overview
-----------------------
The hierarchical pipeline produces a structured representation of the comparative analysis at three levels:
- Paragraph (meso)
- Sentence (meso)
- Phrase / micro-operations (micro)

Two outputs are produced by the service:
- legacy `hierarchical_analysis` (kept for backward compatibility) — may contain dataclass instances in its values (internal form).
- new `hierarchical_tree` — a JSON-serializable list of dicts (one dict per ParagraphNode) intended for frontend consumption.

2) Dataclass models (source of truth)
-------------------------------------
Primary dataclasses are centralized in:
- [`backend/src/models/hierarchical_nodes.py`](backend/src/models/hierarchical_nodes.py:1)

Key classes (dataclasses):
- ParagraphNode: level="paragraph", tag, confidence, source_text, target_text, explanation, nested_findings: List[SentenceNode]
- SentenceNode: level="sentence", tag, confidence, source_text, target_text, explanation, nested_findings: List[PhraseNode]
- PhraseNode: level="phrase", tag, confidence, source_text, target_text, explanation

These dataclasses are intentionally minimal and include an `extra`/`any`-style field to allow forward compatibility.

3) Pydantic response model update
---------------------------------
The comparative analysis response model was extended at:
- [`backend/src/models/comparative_analysis.py`](backend/src/models/comparative_analysis.py:180)

Changes:
- Added `hierarchical_tree: Optional[List[Dict[str, Any]]]` (JSON-safe representation)
- Kept `hierarchical_analysis: Optional[Dict[str, Any]]` for compatibility

Why both?
- `hierarchical_analysis` preserves the existing programmatic shape and avoids breaking internal code/tests.
- `hierarchical_tree` guarantees a JSON-friendly shape for the frontend (dataclasses converted to dicts).

4) Service behavior and serialization
-------------------------------------
Implementation in:
- [`backend/src/services/comparative_analysis_service.py`](backend/src/services/comparative_analysis_service.py:1)

Flow (high-level):
- Paragraph segmentation (split by blank lines).
- Optional salience computation at paragraph and sentence levels (via SalienceProvider).
- Paragraph alignment using the SemanticAlignmentService (semantic paragraph alignment).
- Per-paragraph sentence alignment using SentenceAlignmentService (sentence-level similarity).
- Per-sentence micro-level analysis via analyze_phrases() and optional MicroSpanExtractor when enabled by `include_micro_spans`.
- The service constructs two outputs:
  - `hierarchy` (legacy dict-shaped payload): contains "hierarchy_version", "source_paragraphs", "target_paragraphs", and "metadata".
  - `hierarchical_tree`: a list of paragraph dicts produced by converting ParagraphNode dataclasses to plain dicts using `dataclasses.asdict()`.

Important implementation notes:
- Conversions use dataclasses.asdict so nested dataclasses (SentenceNode, PhraseNode) are also converted recursively to native lists/dicts/primitives.
- The `hierarchy_version` is bumped to "1.2" when micro spans are included (M4).
- The service still preserves legacy shapes so existing consumers and tests remain valid.

5) API contract
---------------
Endpoint:
- POST /api/v1/comparative-analysis/ (see router in [`backend/src/api/comparative_analysis.py`](backend/src/api/comparative_analysis.py:1))

Response model:
- `ComparativeAnalysisResponse` now includes:
  - hierarchical_analysis: Optional[Dict[str, Any]] (legacy)
  - hierarchical_tree: Optional[List[Dict[str, Any]]] (serialized for frontend)

Serialization:
- FastAPI / Pydantic will serialize `hierarchical_tree` directly because it is a list/dict structure containing only JSON-native types.

Frontend expectations:
- Prefer `hierarchical_tree` for display and interactions (no dataclass objects).
- `hierarchical_tree` is a flat list containing paragraph dicts for both source and target paragraphs (the service appends source paragraphs and then target paragraphs to the list).
- If you prefer a different shape (e.g., {"source_paragraphs": [...], "target_paragraphs": [...]}) we can easily change serialization — discuss if product prefers that shape.

6) Tests added / updated
------------------------
- New integration tests: [`backend/tests/test_hierarchical_integration.py`](backend/tests/test_hierarchical_integration.py:1)
  - These tests monkeypatch embeddings, paragraph alignment, and salience to create deterministic outputs and to validate:
    - legacy `hierarchical_analysis` exists and has paragraph/sentence structure
    - `hierarchical_tree` exists and is JSON-serializable (list of paragraph dicts)
    - micro-span behavior and hierarchy_version bump to "1.2" when `include_micro_spans=True`
- Updated unit test: [`backend/tests/test_hierarchical_output.py`](backend/tests/test_hierarchical_output.py:1) to assert `hierarchical_tree` presence in addition to the legacy checks.

Developer notes:
- Tests run locally in workspace using: python -m pytest backend/tests/test_hierarchical_integration.py -q
- Integration tests are purposely lightweight and mock heavy external ops (no real ML models required).
- When adding tests that inspect `hierarchical_analysis`, be prepared to handle either dataclass instances or dicts — the service preserves dataclasses in the legacy field. Prefer `hierarchical_tree` when asserting JSON shapes.

7) How to extend or debug
--------------------------
- Add new fields to ParagraphNode / SentenceNode / PhraseNode in [`backend/src/models/hierarchical_nodes.py`](backend/src/models/hierarchical_nodes.py:1).
- When adding new analysis passes (e.g., rhetorical roles, discourse markers), attach results into SentenceNode.nested_findings or ParagraphNode.extra as appropriate.
- To debug serialized output quickly:
  - Run the service with a small request that sets `hierarchical_output=True`.
  - Inspect `response.hierarchical_tree` (guaranteed JSON types).
  - If you must inspect legacy `hierarchical_analysis`, remember it might still contain dataclass instances; use dataclasses.asdict() to convert them.

8) Migration and backward compatibility
--------------------------------------
- No breaking changes to existing endpoints: `hierarchical_analysis` kept.
- Frontend should migrate to `hierarchical_tree` for a stable JSON schema and better compatibility with TypeScript/JS.

9) Open questions / future work
-------------------------------
- Preferrable final API shape for hierarchical tree: single list of paragraphs (current) vs grouped source/target dict. I recommend grouped shape for clarity; change is trivial to implement.
- Add a Pydantic model wrapper for `hierarchical_tree` to provide stronger validation at API-level. Currently `hierarchical_tree` is typed as List[Dict[str, Any]] for flexibility.
- Consider exposing a compact schema for micro-ops (to reduce payload) when sending to the frontend (e.g., only include top-K micro-spans or a compressed representation).
- Add more tests asserting the exact content shape of `hierarchical_tree` for frontend contracts.

Contact / authorship
--------------------
Documentation and code changes implemented by the development team. For integration questions, reference the integration tests:
- [`backend/tests/test_hierarchical_integration.py`](backend/tests/test_hierarchical_integration.py:1)