# HITL Phase 3 - Feedback Actions (Step 3.1 Accept / Reject)

This document describes the initial frontend integration of human-in-the-loop validation actions for simplification strategy annotations.

## Scope (Step 3.1)
- Actions implemented: Accept, Reject
- Modify / Create deferred to later steps
- All UI changes gated behind feature flag: `config.enableFeedbackActions` (default: false)

## Backend Reference
PATCH `/api/v1/annotations/{id}?session_id=...` with body `{ "action": "accept" | "reject", "session_id": "..." }`
Response returns the updated annotation. Rejected annotations are hidden from subsequent list calls.

## Frontend Additions
- `useAnnotationStore.js`: Zustand store for annotations with optimistic Accept / Reject.
- `StrategyDetailPanel`: Accept / Reject buttons in footer when feature flag enabled.
- `StrategySuperscriptRenderer`: Visual indicator for accepted annotations (green outline ring). Rejected annotations removed from store optimistically.

## UX & Accessibility
- Buttons are keyboard focusable and have explicit `aria-label` attributes.
- Accepted markers expose updated aria-label including `(aceita)`.
- Reject closes the panel immediately to avoid focusing a now-removed marker.

## State Flow
1. User opens detail panel via superscript marker.
2. User clicks Accept or Reject.
3. Store performs optimistic update:
   - Accept: status -> `accepted` (marker remains, outlined in green)
   - Reject: annotation removed from `annotations` array (marker disappears)
4. API PATCH request is sent; rollback on failure with notification.

## Audit & Persistence
- Backend persists accept / reject events with audit entries and hides rejected items in list responses.
- Frontend does not keep a local audit log (will be integrated in later steps for UI surface of history).

## Testing
- Added lightweight store tests (`useAnnotationStore.test.js`) covering optimistic transitions.

## Future Steps
- Step 3.2: Modify existing annotation (status `modified`), conflict rules (cannot accept modified directly).
- Step 3.3: Create new annotation (origin = human) and editing workflow.
- Step 3.4: Audit timeline viewer + export.

## Step 3.2 (Modify)
Implemented:
- Added "Modificar" button (feature-flag gated) in `StrategyDetailPanel`.
- Dropdown of canonical codes (from `STRATEGY_METADATA`).
- Confirm sends PATCH `{ action: "modify", new_code }`.
- First modify preserves prior code into `original_code`.
- Status set to `modified`; superscript ring amber; aria-label updated `(modificada de <orig>)`.
- Cancel restores prior view without mutation.

State & Optimistic Flow:
1. User enters modify mode (local UI state only).
2. Select new code, confirm -> optimistic update applied.
3. API call; on failure rollback & notification.

Accessibility:
- Select element has hidden label; focus rings on all controls.
- Aria labels reflect accepted / modified / active states cumulatively.

Testing:
- Extended `useAnnotationStore.test.js` with modify scenario (status, code, original_code preservation).

## Step 3.3 (Create)
Implemented:
- Text selection (target text) triggers inline action to add a new strategy (UI hook pending integration with selection layer — store & API support complete).
- Store method `createAnnotation` with optimistic temp ID and rollback.
- Backend `POST /api/v1/annotations` creates human-origin annotation (`status=created`).
- Superscript renderer: blue ring for created/human annotations + aria label `(criada manualmente)`.
- Tests extended: create scenario covers optimistic -> commit replacement.
 
UI Selection Workflow (Finalized in this iteration):
1. User selects text inside the target panel; empty or cross-panel selections are ignored.
2. A floating popover (role="dialog") appears near the selection with:
   - Strategy dropdown (canonical codes from `STRATEGY_METADATA`).
   - Optional comment textarea.
   - Adicionar / Cancelar buttons.
3. Live region announces: “Seleção pronta. Pressione Enter para atribuir estratégia.”
4. On Adicionar: optimistic create -> immediate blue-ring superscript; backend POST validates & commits (temp ID replaced).
5. On Cancelar: popover dismissed; no mutation.

Accessibility & A11y Notes:
- Popover fully keyboard navigable; controls have visible focus rings.
- aria-live polite region communicates readiness state.
- Future enhancement: initial focus shift + ESC to close (deferred).

Testing Additions:
- Added UI abstraction test `CreateAnnotationFlow.test.jsx` (jsdom limitation prevents native selection; store-level invocation verifies merge/render path).
- End-to-end selection simulation proposed for future Cypress suite (Phase 3.5 hardening).

Deferred / Limitations:
- Source text selection not yet supported.
- No toast for network failure rollback yet (hook reserved for Step 3.4/3.5 notification consolidation).
- Focus trapping inside popover optional; presently relies on natural tab order.

## Step 3.4 (Audit & Export)
Implemented:
- Append-only in-memory + persisted audit log capturing: create, modify, accept, reject (with from_status → to_status and timestamp, session_id).
- Backend endpoints:
   - GET `/api/v1/annotations/audit?session_id=...` (optional `&annotation_id=...` filter)
   - POST `/api/v1/annotations/export?session_id=...&format=jsonl|csv`
      - JSONL: one JSON object per line (datetimes ISO8601).
      - CSV: columns `id,strategy_code,status,origin,created_at,updated_at,original_code,comment`.
- Frontend store additions:
   - `fetchAudit(annotationId?)` populates per-annotation audit cache.
   - `exportAnnotations(format)` triggers file download (no-op in test env).
- UI:
   - Export JSONL / CSV buttons inside `StrategyDetailPanel` (temporary placement; future global toolbar candidate).
   - Collapsible audit history per annotation (lazy loads on first expand).
- Accessibility:
   - Buttons keyboard-focusable with clear labels / aria-labels.
   - Audit history region has `aria-label` and preserves natural reading order.
- Testing:
   - Backend: `test_annotations_export.py` end-to-end create → modify → accept second ann → export JSONL/CSV + audit retrieval.
   - Frontend: `annotationExport.test.js` verifies correct export endpoint call assembly (jsonl, csv) under feature flag environment.
   - Store & UI tests unchanged still green; total frontend tests updated.

Data Format Examples:
JSONL (line excerpt):
`{"id":"uuid","strategy_code":"OM+","status":"modified","origin":"human","created_at":"2025-09-08T16:22:04.529007","updated_at":"2025-09-08T16:23:10.120001","original_code":"OM+","comment":"teste"}`

CSV (header + row):
`id,strategy_code,status,origin,created_at,updated_at,original_code,comment`
`uuid,SL+,modified,human,2025-09-08T16:22:04.529007,2025-09-08T16:23:10.120001,OM+,teste`

Notes & Future Enhancements:
- Potential addition: global export dialog with filter toggles (status subset, date range, session grouping).
- Potential addition: audit diff view for modified code transitions (show old/new code inline).
- Consider migrating datetimes to timezone-aware UTC objects in later refactor (current use of `utcnow()` flagged by deprecation warnings).
- Source selection + multi-offset creation candidate for Phase 3.5+.

Status: Step 3.4 complete and feature remains behind `enableFeedbackActions` until full Phase 3 sign-off.

## Phase 3.5 (Hardening & Refinements)
Enhancements Implemented:
- Focus trap + ESC handling for creation popover (first focusable receives focus; Tab loops within; Escape closes and restores context).
- Timezone-aware UTC datetimes (`datetime.now(timezone.utc)`) across Annotation and Audit models; exports now emit ISO8601 with `Z` assumption.
- Global export buttons (JSONL / CSV) added to header (temporary placement) gated by feature flag.
- Audit log enriched with `from_code` / `to_code`; diff visualization (strike-through old, green new) for modified events in panel.
- Accessibility pass: Export buttons have aria-labels; audit toggle exposes aria-expanded; popover retains logical tab order; live region unchanged.
- Test adjustments: Existing backend export test passes with timezone change; frontend export test guards against missing `URL.createObjectURL` in jsdom.

Remaining Gaps / Future Considerations:
- Could add toast confirmation after successful export trigger.
- Consider batching audit persistence to reduce file writes on rapid actions (not critical now).
- Potential E2E tests (Playwright/Cypress) to verify keyboard traversal of focus trap.
- Source text selection & multi-range creation remain deferred.

---
/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
