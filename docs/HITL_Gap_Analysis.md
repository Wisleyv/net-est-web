## Human-in-the-Loop (HITL) Gap Analysis – NET-EST (2025-09-07)

Legend for Status: Present = implemented and functionally aligned with requirement; Partial = some support exists but incomplete or deviates; Missing = no substantive implementation.

| Feature                                                                          | Status (Present / Partial / Missing) | Needed Adjustments                                                                                                                                                                                                                                                                           |
| -------------------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Side-by-side display of source & target texts                                    | Present                              | Component `SideBySideTextDisplay` already renders both; keep stable.                                                                                                                                                                                                                         |
| Color coding applied to BOTH source & target sentences                           | Partial                              | Logic exists for both (uses `sourcePosition` / `targetPosition`), but backend often only supplies meaningful target positions; ensure detector populates accurate source positions (alignment-based) to avoid regression where only target highlights.                                       |
| Superscript strategy tag at start of each simplified (target) excerpt            | Missing                              | Add inline rendering: inject `<sup class="strategy-tag">CODE</sup>` before highlighted target span start (sentence/segment). Provide accessible aria-label.                                                                                                                                  |
| Click interaction on tag (not just hover)                                        | Missing                              | Add click handler to open persistent side panel / popover with full details; current tooltip is hover-only and ephemeral.                                                                                                                                                                    |
| Display of strategy label (code + human-readable name) in interaction panel      | Partial                              | Tooltip shows both; needs persistent panel and reuse for click-based workflow.                                                                                                                                                                                                               |
| Display of confidence score                                                      | Present                              | Tooltip & legend show percentage; replicate inside new panel & superscript (e.g. title attr).                                                                                                                                                                                                |
| Explanation of reasoning (narrative)                                             | Missing                              | Transform `TagEvidence` + feature deltas into templated natural-language explanation (e.g., “Redução média de comprimento de sentença de X → Y (-Z) e similaridade semântica alta indicam Fragmentação Sintática (RP+)”). Implement server-side explanation generator or frontend formatter. |
| Evidence list supporting decision                                                | Partial                              | Tooltip lists first 3 raw evidence items; need full ordered list + mapping evidence_name → descriptive text.                                                                                                                                                                                 |
| OM+ never auto-suggested unless explicitly enabled                               | Partial                              | Enforcement via `UserConfiguration` (inactive by default) & heuristic path; need explicit API param (e.g., `enable_om_detection=true`) to force plus UI toggle reflecting state.                                                                                                             |
| PRO+ never auto-suggested (manual only)                                          | Present                              | `manual_only=True` & inactive; no auto logic present. Still add explicit override path (config flag) if future research requires.                                                                                                                                                            |
| Ability to force-enable OM+ via configuration                                    | Partial                              | Backend flag indirectly via user_config but no documented / dedicated endpoint param or UI control; add UI toggle + pass through in request payload.                                                                                                                                         |
| Ability to force-enable PRO+ (research override)                                 | Missing                              | Add guarded config flag (e.g., `allow_pro_auto=true`) default false; restrict in production.                                                                                                                                                                                                 |
| Manual addition (Create) of a missing annotation                                 | Missing                              | Add UI flow: select text span (target or source+target pair), choose tag from dropdown (including OM+/PRO+), enter optional note; POST new annotation endpoint.                                                                                                                              |
| Accept (confirm) machine suggestion                                              | Missing                              | Add buttons per suggestion (Accept) -> feedback endpoint (action=confirm) and mark TagAnnotation.validated=true (new endpoint).                                                                                                                                                              |
| Modify (change label via dropdown)                                               | Missing                              | Provide Modify action that opens dropdown of allowed tags; send feedback (action=adjust, suggested_tag=NEW); update annotation record.                                                                                                                                                       |
| Reject (remove suggestion)                                                       | Missing                              | Provide Reject action -> feedback (action=reject); mark annotation removed (soft delete) & persist decision.                                                                                                                                                                                 |
| Create (manual new annotation) action distinct from adjust                       | Missing                              | Extend FeedbackAction enum or introduce separate endpoint; ensure manual annotations flagged `manually_assigned=true` & optionally `validated=true` immediately.                                                                                                                             |
| Persistence of expert-validated (gold) annotations separate from raw predictions | Missing                              | Introduce `validated_annotations` collection/file (e.g., `data/feedback/validated/validated_<date>.json`) or DB table; implement repository methods save/get.                                                                                                                                |
| TagAnnotation fields for manual & validated flags                                | Present                              | Fields exist (`manually_assigned`, `validated`) but unused—add endpoints to set/update.                                                                                                                                                                                                      |
| Endpoint to update validation status of an annotation                            | Missing                              | Create PATCH `/api/v1/comparative-analysis/annotations/{id}` to set validated / modified label.                                                                                                                                                                                              |
| Feedback endpoint capturing confirm/reject/adjust                                | Present                              | `/feedback` supports confirm/reject/adjust; extend to link back to annotation & persist updated state.                                                                                                                                                                                       |
| Feedback action “create” (manual new)                                            | Missing                              | Either extend enum (CREATE) or treat manual addition as adjust with special metadata flag; prefer explicit CREATE enumerant for clarity.                                                                                                                                                     |
| Storage of reasoning/evidence for academic audit                                 | Partial                              | `TagEvidence` captured but raw, no human-readable mapping persisted; add explanation field (string) in TagAnnotation or separate `reasoning` property.                                                                                                                                       |
| Use of feedback for retraining / fine-tuning                                     | Missing                              | Define pipeline spec & background task to export confirmed vs rejected annotations (positive/negative examples) and schedule model update (manual for now).                                                                                                                                  |
| Strategy position mapping (sentence / span indices)                              | Partial                              | Basic sentence indices; need alignment to paragraph-level or char offsets for precise highlighting & manual span selection; add offsets in API.                                                                                                                                              |
| UI filtering/toggling of strategies                                              | Partial                              | `selectedStrategies` prop exists, but no in-component selection management (parent must handle); implement internal state & interactive filtering + “Show All / None”.                                                                                                                       |
| Colorblind-friendly palette                                                      | Present                              | Provided via `useColorblindFriendly` prop & alternate color map; ensure toggle exposed in UI settings.                                                                                                                                                                                       |
| Accessibility (keyboard navigation & aria labels)                                | Partial                              | Buttons have ARIA labels; superscript tags & popover will need proper focus management and ESC close. Perform audit.                                                                                                                                                                         |
| Prevention of auto-generation for manual-only tags (PRO+)                        | Present                              | `manual_only` config flag in models ensures not processed; maintain checks in classification path.                                                                                                                                                                                           |
| Logging/audit trail of validation decisions                                      | Partial                              | Feedback saved with timestamp & action; need linkage to original annotation IDs and resulting state changes (pre/post diff) + session context for full audit.                                                                                                                                |
| Differentiated dataset export (raw predictions vs validated corpus)              | Missing                              | Add export endpoint `/analytics/export/validated` producing standardized JSON/CSV for ML.                                                                                                                                                                                                    |
| Narrative report including human decisions                                       | Missing                              | Extend report generator / analytics to summarize acceptance rates per strategy, inter-annotator potential.                                                                                                                                                                                   |
| Frontend component for feedback (`FeedbackCollection.jsx`)                       | Missing                              | File exists but empty; implement interactive panel listing suggestions with Accept/Modify/Reject.                                                                                                                                                                                            |
| Server-side generation of unique strategy IDs consistent across sessions         | Partial                              | Current IDs built in frontend (`strategy_${index}`); move ID generation to backend for persistence & feedback correlation.                                                                                                                                                                   |
| Mechanism to prevent duplicate feedback submissions per annotation               | Missing                              | Add repository check (session_id + strategy_id + action) de-dup or annotate occurrences.                                                                                                                                                                                                     |
| Configuration surface (API) to pass user tag activation & weights                | Partial                              | `UserConfiguration` exists but not clearly exposed through comparative analysis endpoint; document and add request body support or dedicated config endpoint.                                                                                                                                |
| Academic metadata (versioning of detection model in responses)                   | Missing                              | Include model_version & ruleset_version fields in strategy annotations for research reproducibility.                                                                                                                                                                                         |
| Batch validation operations (accept all / reject selected)                       | Missing                              | Add bulk endpoint to streamline expert workflow.                                                                                                                                                                                                                                             |
| Offline / deferred feedback queue resilience                                     | Missing                              | For network failures, design local queue in frontend with retry; not implemented.                                                                                                                                                                                                            |
| Char-level span capture for manual annotations                                   | Missing                              | Extend backend models to store start/end offsets alongside sentence index for precise training data.                                                                                                                                                                                         |
| Safeguard to prevent accidental deletion of validated annotations                | Missing                              | Soft-delete flag & confirmation dialog; repository versioning.                                                                                                                                                                                                                               |
| Data schema ready for ML retraining (positive/negative pairs)                    | Missing                              | Design standardized JSON lines format with fields: source_span, target_span, tag, decision, confidence, features.                                                                                                                                                                            |
| Automatic rationale templating engine                                            | Missing                              | Implement mapping dictionary: evidence.feature_name → Portuguese template fragment; compose explanation.                                                                                                                                                                                     |
| Unit tests for HITL workflows                                                    | Missing                              | Add tests for: forcing OM+, prohibiting PRO+, feedback state transitions, manual create, rationale generation.                                                                                                                                                                               |

### Prioritized Action Plan (Stability First → Full HITL Enablement)

1. Stabilization & Data Integrity (Low-Risk)
   
   - Backend: Add stable unique strategy IDs in detection response; document `UserConfiguration` usage; expose model_version.
   - Populate accurate `sourcePosition` & `targetPosition` (paragraph + sentence + char offsets) using semantic alignment output.
   - Ensure OM+/PRO+ guardrails (explicit override flags, default false).  

2. Core UI Interaction Layer
   
   - Implement superscript tag rendering and click-driven persistent details panel (evidence + confidence).
   - Build `FeedbackCollection` component listing suggestions with Accept / Modify / Reject controls; keyboard accessible.
   - Local state management for strategy filtering; show/hide controls; colorblind toggle surface.

3. Validation & Annotation CRUD
   
   - New endpoints: PATCH annotation (validate/modify), POST manual annotation (CREATE), bulk operations endpoint.
   - Extend FeedbackAction enum (add CREATE) OR introduce `action_type` in payload; update repository & tests.
   - Persist changes: update TagAnnotation fields (`validated`, `manually_assigned`) and maintain audit trail (previous_label, new_label, timestamp, user/session).  

4. Reasoning & Explanation Layer
   
   - Implement server-side rationale generator using TagEvidence → template mapping; add `explanation` field in TagAnnotation / strategy output.
   - Provide separate academic-friendly explanation (long form) and short tooltip summary.
   - Add unit tests verifying explanation correctness for representative strategies.

5. Gold Annotation Persistence
   
   - Create `ValidatedAnnotationRepository` (or extend existing repository with separate directory) storing only accepted / manually created annotations after validation.
   - Export endpoint for validated corpus + metadata (model_version, timestamp, tag distribution).
   - De-dup and enforce idempotent saves; implement soft-delete & versioning.

6. Enhanced Feedback & Audit
   
   - Add duplicate feedback prevention, batch endpoints, and improved logging (annotation_id, action, rationale length).
   - Add analytics summarizing acceptance / rejection rates per strategy and confidence calibration (e.g., reliability diagram data).  

7. Manual Annotation Precision
   
   - Add char-level span selection in frontend (text selection API) and extend backend to store offsets.
   - Migrate highlighting logic to operate on offsets (fallback to sentence index) to future-proof for more granular strategies.

8. Retraining Preparation
   
   - Define JSONL schema for training samples; implement nightly (manual) export task combining validated positives + rejected (as negative/ambiguous) with features.
   - Provide documentation & script placeholder for future model fine-tuning (not executing training yet).  

9. Advanced Workflow & Resilience
   
   - Implement offline feedback queue (IndexedDB/localStorage) with retry.
   - Add bulk Accept/Reject & multi-select UI to accelerate expert review.
   - Accessibility improvements: focus management for panels, ARIA roles, high-contrast mode verification.

10. Future (Optional / Research)
    
    - Active learning loop: prioritize low-confidence or high-disagreement strategies for expert review.
    - Inter-annotator agreement module (if multi-expert usage) for reliability statistics (Cohen’s κ / Krippendorff’s α).  

### Refactoring Notes

Minimal invasive changes recommended early (IDs, endpoints, small UI components). Larger refactors (char-offset architecture, active learning, alignment-driven rationale generation) postponed until core HITL lifecycle (detect → display → validate → persist → export) is robust and covered by tests. Avoid premature redesign of strategy detector; instead wrap outputs with adapter producing enriched annotation objects.

### Test Coverage Additions (High Priority)

1. API: enabling OM+ vs default disabled; PRO+ override blocked without flag.
2. Annotation lifecycle: detect → accept → modify → reject → create manual.
3. Rationale generation: each evidence feature yields expected template fragment.
4. Export endpoint: validated corpus JSON schema integrity.
5. Duplicate feedback prevention logic.

### Risks & Mitigations

| Risk                                                        | Impact                 | Mitigation                                                                    |
| ----------------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------- |
| Inaccurate sentence indices cause misaligned highlights     | Confusing UI           | Switch to char offsets + alignment mapping; add consistency check test.       |
| Manual overrides conflicting with future model improvements | Data noise             | Store provenance (auto vs manual) & exclude manual from certain metrics.      |
| Growing feedback files (size/performance)                   | File IO slowdown       | Rotate & compress archives; implement size guard (already partially present). |
| Explanation generation drift after feature changes          | Academic inconsistency | Version explanation templates; include template_version in output.            |

### Summary

System has foundational detection, evidence capture, color infrastructure, and feedback persistence primitives, but lacks the interactive validation UI, explanation generation, CRUD endpoints, and gold dataset pipeline required for full HITL functionality. The outlined phased plan incrementally introduces these capabilities while containing risk and avoiding large early refactors.

---

Generated on 2025-09-07 for strategic planning; implement iteratively with versioned milestones (HITL-M1…M5).

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/