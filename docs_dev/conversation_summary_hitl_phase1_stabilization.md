Conversation summary — HITL phase1 stabilization

Date: 2025-09-20
Branch: feature/hitl-phase1-stabilization

Purpose
- Record the investigation, findings, and recommended next steps for the inline annotation selection mapping issue.

Key actors
- User: Project owner requesting production-ready stability and semantic preservation.
- Agent: Performed DOM investigation, proposed Range-based + semantic metadata hybrid.

Chronology
1. Initial discovery: selection-to-offset mapping failed; `indexOf()` used and caused duplicate text ambiguity.
2. TreeWalker attempt: implemented but produced incorrect mappings. Development halted.
3. Root cause analysis: found mismatch between backend plain text (2421 chars) and frontend DOM text (2459 chars) — a 38-char discrepancy.
4. DOM investigation: added logging in `ComparativeResultsDisplay.jsx` to inspect Range details and container contents. Confirmed target container: `div.strategy-superscript-layer`.
5. Proposed solution: dual-layer mapping (Range-based stable offsets + TreeWalker-based semantic metadata) along with synchronization strategy (prefer frontend marker stripping in short term).

Findings
- Primary blocker: backend/frontend text synchronization mismatch (38 characters).
- Range works within DOM but verification against backend text fails.
- TreeWalker-only approach is brittle and was halted.

Recommendations
- Immediate: Implement frontend normalization (strip markers and normalize whitespace) before offset calculation to align lengths and avoid fallback to `indexOf()`.
- Medium: Implement dual-layer mapping: Layer 1 = normalized Range offsets; Layer 2 = optional semantic metadata extraction. Only run Layer 2 when Layer 1 verifies.
- Long-term: Consider backend normalization or marker-aware responses if stricter single-source-of-truth is required.

Next steps (short-term)
1. Implement and test frontend normalization logic.
2. Validate offsets against backend text for many selection cases (start/middle/end, multi-span selections).
3. Add unit tests for normalization and mapping functions.

Files touched during investigation (non-exhaustive)
- `frontend/src/components/ComparativeResultsDisplay.jsx` (logging and selection handling)
- `frontend/src/components/StrategySuperscriptRenderer.jsx`
- `frontend/src/components/SideBySideTextDisplay.jsx`

Status
- Investigation: completed
- Plan: dual-layer mapping drafted
- Implementation: pending (Phase 1: normalization)

Contact
- For questions or to request follow-up tasks, open an issue referencing this summary.
