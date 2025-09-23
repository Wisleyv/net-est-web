Phase 1 Amended Plan — Normalization, Schema, Performance & Error Policy

Date: 2025-09-20
Branch: feature/hitl-phase1-stabilization

This document amends the Phase 1 plan with the operational constraints and definitions required before any implementation. No coding will occur until this plan is approved.

1) Implementation Strategy for Normalization

Immediate Task: Option A — Frontend Stripping
- Implement normalization on the frontend that strips bracketed strategy markers (e.g., [OM+], [SL+]), removes zero-width/invisible characters, and normalizes whitespace to single spaces.
- Logging required for every normalization operation (see Logging Spec below).

Medium-Term Goal: Architect for Option C — Dual Normalization Layer
- Design the normalization code so it can be refactored into a shared Normalizer utility that can be ported to backend later.
- Keep normalization logic isolated and exported from UI components (e.g., src/services/textNormalizer.js).

Logging Spec (required for every normalization operation)
- Log entries MUST include:
  - rawDomLength: number (length of container.textContent)
  - normalizedLength: number (length after normalization)
  - rawHash: string (SHA-256 hex of raw DOM text)
  - normalizedHash: string (SHA-256 hex of normalized text)
  - selectionOffsets: { startOffset: number, endOffset: number } (calculated offsets in normalized text)
  - timestamp: ISO8601
  - sessionId: string (from analysisResult.analysis_id or id) if available
- Logging destination: local console in DEV, and a configurable telemetry sink (to be implemented in Phase 3).
- Sensitive data: do NOT log full text content in production logs. Use hashes and lengths instead.

2) Semantic Schema Contract (Annotation Payload)

Before any semantic-layer coding, the UnifiedSelectionHandler.processSelection() MUST return a JSON payload matching this contract.

Annotation Payload Schema (JSON Schema simplified)

{
  "startOffset": 0,              // number: inclusive start index in normalizedText
  "endOffset": 0,                // number: exclusive end index in normalizedText
  "normalizedText": "",        // string: normalized slice or entire normalized text (TBD: store entire normalizedText for verification)
  "semanticContext": {          // object: semantic metadata
    "crossedTags": [            // array of objects for elements crossed by selection
      { "tag": "SPAN", "class": "unified-highlight target", "attributes": {"data-code":"RF+","data-strategy-id":"..."}, "textPreview": "..." }
    ],
    "strategyMarkers": ["RF+", "OM+"],
    "nestingDepth": 2,
    "structuralBoundaries": { "startBlock": "p", "endBlock": "p" }
  },
  "confidence": 0.0,           // number between 0 and 1 estimating mapping reliability
  "normalizationMismatch": false, // boolean: true if normalized frontend text does not match backend expected text length/hash
  "metadata": {                // optional telemetry/debug info
    "rawDomLength": 0,
    "normalizedLength": 0,
    "rawHash": "",
    "normalizedHash": "",
    "timestamp": "2025-09-20T...Z",
    "sessionId": "..."
  }
}

Notes:
- "normalizedText" may be the entire normalized document or just the selection slice; initial implementation will include the selection slice and normalized document length in metadata to keep payload size modest.
- "confidence" is computed from verification checks (text equality, hash match, duplicate occurrences, etc.) and ranges 0..1.

3) Performance Constraints & Instrumentation

Requirement:
- calculateOffsets() end-to-end must complete within 50ms for documents up to 10,000 characters on a developer-class laptop (modern CPU, single tab). This includes normalization and offset mapping.

Instrumentation:
- Measure and log timings (ms) for:
  - normalizationTimeMs
  - rangeCalculationTimeMs (DOM Range + mapping)
  - semanticExtractionTimeMs (TreeWalker traversal) — optional and may run asynchronously
  - totalTimeMs
- Use performance.now() in the browser to measure high-resolution timings and include them in the telemetry metadata.

Theoretical performance analysis (TreeWalker worst-case):
- TreeWalker visits text nodes; worst-case node count is O(N) where N = number of text nodes. For a document of 10,000 characters split into 1-char text nodes (extreme), node count = 10,000.
- Processing each node involves O(1) work (length, comparisons), so complexity = O(N). For N=10,000 on modern browsers, a well-optimized TreeWalker should complete within tens of milliseconds.
- Recommendation: limit TreeWalker to operate only within the common ancestor container that holds the normalized text.
- If semanticExtraction is expensive, run it asynchronously after Layer 1 completes and return the annotation payload with semanticContext=null initially; update the annotation later via a PATCH endpoint when semantic data is ready.

4) Mismatch Error Handling Policy

Options analyzed:
- Option 1 (Fail Fast): Block annotation creation on mismatch.
  - Pros: ensures only high-fidelity data reaches backend
  - Cons: poor user UX; blocks annotators and reduces throughput

- Option 2 (Degrade Gracefully): Proceed with best-effort offsets, mark annotation as low-confidence, log a severe warning.
  - Pros: preserves annotator workflow, collects data (including mismatch telemetry) for ML team, allows post-hoc cleanup
  - Cons: introduces noisy labels if not filtered by confidence

Recommendation (Chosen): Option 2 — Degrade Gracefully
- Rationale: Human-in-the-loop workflows must prioritize annotator flow. Blocking is harmful. Proceeding and flagging low-confidence allows ML engineers to filter data or prioritize fixes. Maintain a strict telemetry pipeline to track mismatch frequency.

Policy details:
- If normalizationMismatch === true OR normalized hash != backend expected hash:
  - Set confidence to a low value (e.g., 0.1)
  - Add `normalizationMismatch: true` to payload
  - Log an error-level telemetry event with metadata
  - Allow annotation to be created and stored, but mark it in backend as `low_confidence`
  - Trigger optional background job to attempt remapping with alternate strategies (e.g., indexOf fallback with context-aware disambiguation)

Approval & Next Steps
- This document requires your explicit approval before any code is written.
- Upon approval I will implement Phase 1 (Option A) following this plan, add tests for normalization, add performance instrumentation, and include rich logging as specified.

Appendix: Implementation checklist (for coding phase, post-approval)
- [ ] Add `src/services/textNormalizer.js` with normalization + exports
- [ ] Add `src/services/perfInstrumentation.js` helper
- [ ] Update `ComparativeResultsDisplay.jsx` to call Normalizer, compute hashes, measure timings, and emit schema-compliant payloads
- [ ] Unit tests for normalization and mapping (jest)
- [ ] Integration test to validate annotations round-trip to backend
- [ ] Telemetry hooks for production logging
