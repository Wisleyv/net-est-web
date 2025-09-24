# Inline Annotation System – Production Readiness Implementation Plan

Date: 2025-09-24  
Related Report: `INLINE_ANNOTATION_REVERSE_ENGINEERING_REPORT.md`  
Scope Phase Baseline: Branch `feature/hitl-phase1-stabilization`

## 0. Guiding Principles
- Root Cause Resolution over workaround patches.
- Evidence-Based: Every change tied to a measurable verification artifact (test, benchmark, a11y scan).
- Incremental Hardening: Small, reversible steps; each phase has an approval gate.
- Development Guidelines Compliance: Align with `docs_dev/development_guidelines.md` (cleanliness, documentation, regression-free discipline).
- Observability & Traceability: Each user-impacting change produces audit log entries, changelog updates, and test coverage.

## 1. Phase Framework (Summary)
| Phase | Theme | Core Objectives | Primary Risks Mitigated |
|-------|-------|-----------------|--------------------------|
| 1 | Baseline Integrity & Instrumentation | Add span modify backend action, gold validation flag correctness, metrics hooks | Silent data corruption, untracked regressions |
| 2 | Accessibility & Interaction Stabilization | Replace hover-only menu, keyboard workflow, scroll sync | A11y non-compliance, poor UX |
| 3 | Offset & Highlight Reliability | Canonical offset resolver, overlap merging, selection accuracy tests | Incorrect annotations, visual ambiguity |
| 4 | Data Model & Rationale Alignment | Unify comment/explanation, accept → validated, export parity | Data semantic drift |
| 5 | Performance & Scalability | Memoization, segmentation optimization, large-text benchmarks | Latency spikes, user frustration |
| 6 | Refactor & Modularization | Decompose monolith component, isolate services | Maintainability, change risk |
| 7 | Enhancement & Evidence Layer | Evidence tooltips, cross-panel synchronized highlighting | Cognitive load, analyst efficiency |
| 8 | Final Hardening & Release Prep | Full regression matrix, docs consolidation, tagging | Release risk |

Each phase contains: Objective, Prerequisites, Steps, Risks, Mitigation, Rollback, Documentation, Approval Gate.

---
## 2. Phase Details

### Phase 1 – Baseline Integrity & Instrumentation
**Objective:** Eliminate silent failures (span edits), ensure validation semantics, introduce lightweight instrumentation hooks without altering UX.
**Prerequisite Validation:** Tests pass (backend + frontend), reverse engineering report merged, no open critical bugs unrelated to span modify.

**Implementation Steps:**
1. Backend Model Update:
   - Extend `AnnotationAction` (add `modify_span` enum).
   - New Pydantic model `AnnotationSpanModify`: `{ action: 'modify_span', session_id, new_target_offsets: List[Offset] }` or reuse dynamic field.
   - Repository method `modify_span(annotation_id, session_id, offsets)` updating `target_offsets`, appending audit entry (`action='modify_span'`).
2. API Endpoint:
   - Update `PATCH /api/v1/annotations/{id}` to branch on `modify_span`.
   - Validation: reject empty or overlapping invalid ranges.
3. Frontend Store (`useAnnotationStore`):
   - Detect backend capability (optimistic first call; if 400 unknown action, fallback with user notification).
   - Update `modifyAnnotationSpan` to pass `new_target_offsets` and assert persisted values via subsequent GET.
4. Gold Validation Semantics:
   - Backend: Accept sets `validated=True` if origin=machine or status=modified? (Rule: accept of pending/modified marks validated; manual creations already validated or manually_assigned? Decide: manual stays `manually_assigned=True`, validated also true.)
   - Frontend: After accept, optimistic update sets both `status='accepted'` & `validated=true`.
5. Instrumentation:
   - Add minimal timing decorators (e.g., measuring detection, annotation PATCH latency) behind an env flag `HITL_ENABLE_METRICS`.
   - Expose metrics summary endpoint `/api/v1/system/hitl-metrics` (in-memory counters only; ephemeral).
6. Tests:
   - Backend: test_modify_span_success, test_modify_span_invalid, test_accept_sets_validated.
   - Frontend: integration test (mock backend) verifying span modify reflected in UI marker position.

**Risks & Mitigation:**
- Schema mismatch (Low/High): Feature flag & fallback path.
- Race on optimistic UI (Medium/Medium): After PATCH, force reconciliation fetch.
- Audit noise (Low/Low): Tag new audit actions distinctly.

**Rollback:**
- Revert commit range: `git revert <range>` (feature branch). Remove enum, remove repo method.
- Confirm removal by running failing test (modify_span) now skipped.

**Documentation Updates:**
- CHANGELOG: Added `modify_span` action, validation semantics.
- API Docs: New action & payload.
- ONBOARDING: Clarify accept → gold flag behavior.

**Approval Gate Criteria:**
- All new tests pass.
- Manual functional demo: create → modify span → export verifies offsets.
- Metrics endpoint returns non-empty structure after actions.

---
### Phase 2 – Accessibility & Interaction Stabilization
**Objective:** Provide fully keyboard-accessible annotation actions; stabilize interaction surfaces (menu, scroll sync).
**Prerequisite:** Phase 1 metrics stable; no failing modify_span tests.

**Implementation Steps:**
1. Replace hover menu with `AnnotationActionPopover` component:
   - Trigger: click on `<sup>` marker or keyboard Enter/Space.
   - Uses portal + focus trap; ARIA `role="menu"`.
2. Add keyboard-driven selection action bar after text selection (persistent until dismissed) with visible buttons: Add Annotation, Cancel.
3. Scroll Synchronization Service:
   - `useScrollSync(refSource, refTarget)` with rAF throttle & recursion guard boolean.
   - Apply to side-by-side comparison view; test large text dataset.
4. Axe-core accessibility audits added to CI gating for markers, popover, selection bar.
5. Update marker ARIA labels to unify phrasing; add `aria-describedby` for status hints.

**Risks:**
- Focus trap deadlocks (Medium/Medium) → Add escape fallback & timeouts.
- Performance scroll jitter (Low/Medium) → Throttle at 16ms min interval.

**Rollback:**
- Toggle feature flag `HITL_ENABLE_POPOVER_MENU=false` to revert to hover interim (kept behind conditional rendering for one phase).

**Documentation:**
- Accessibility section in `HITL_CONFIGURATION.md`.
- CHANGELOG: Replaces hover menu with accessible popover.

**Approval Gate:**
- Keyboard-only user flow: select text → add annotation (recorded test) passes.
- Axe violations = 0 (critical/serious).
- Scroll panes remain synchronized within 1 line vertical delta in test fixture.

---
### Phase 3 – Offset & Highlight Reliability
**Objective:** Guarantee canonical char-level offsets independent of DOM mutation; handle overlapping strategies clearly.
**Prerequisite:** Popover menu stable; no regression in span modify.

**Implementation Steps:**
1. Introduce `offsetResolver.ts`:
   - API: `resolveSelection(fullText, rawSelected, domContext) -> { start, end, method, confidence }`.
   - Methods: direct match (unique substring), context window disambiguation, fallback hashed segment mapping.
2. Remove whitespace-filtering in TreeWalker or bypass DOM entirely for primary resolution.
3. Integrate `mergeOverlappingSegments` into highlight pipeline; composite badge (e.g., first code + "+n"). Tooltip lists all overlapping codes.
4. Add post-creation verification test harness: after annotation creation, extracted substring equals original selection.
5. Unit tests for resolver edge cases: repeated substrings, diacritics, punctuation adjacency, multi-line spans.

**Risks:**
- Over-merge causing lost differentiation (Low/High) → maintain per-strategy data attributes within merged span.
- Performance overhead resolver (Medium/Medium) → Cache by `(fullHash, selectedHash)`.

**Rollback:**
- Feature flag `HITL_USE_CANONICAL_RESOLVER=false` reverts to existing DOM approach.

**Approval Gate:**
- 100% pass on new resolver tests.
- Overlap visual test snapshot approved by design.
- No increase in average annotation creation latency > +5% baseline.

---
### Phase 4 – Data Model & Rationale Alignment
**Objective:** Harmonize `comment` vs `explanation`; ensure semantic export quality.
**Prerequisite:** Resolver in place; overlap rendering accepted.

**Implementation Steps:**
1. Migration logic: When creating manual annotation, map rationale to both `comment` and `explanation` during transition window.
2. Add backend acceptance: if `comment` present and `explanation` missing, auto-populate.
3. Deprecation notice in export: Add `meta.deprecations.comment_field` in response headers (optional).
4. Update frontend creation to send `explanation` primarily after flag date.
5. Enhance export tests asserting explanation non-null for manual + accepted annotations.

**Risks:**
- Tooling downstream expecting `comment` only (Medium/Medium) → Dual-field grace period.

**Rollback:**
- Remove mapping layer; keep legacy `comment` only (single revert commit).

**Approval Gate:**
- Exports show populated `explanation` for >95% manual annotations in test corpus.
- No failing consumer integration tests (if available).

---
### Phase 5 – Performance & Scalability
**Objective:** Maintain or reduce latency under large documents (e.g., 50k chars).
**Prerequisite:** Data model alignment.

**Implementation Steps:**
1. Hash-based memoization for `segmentTextForHighlights` keyed by `(textSHA256, strategySignature)`.
2. Lazy virtualization for superscript rendering if > N markers (threshold e.g., 500) using windowing.
3. Add performance benchmark script: measure selection→annotation round-trip (p95 < 300ms on baseline machine).
4. Optimize resolver: bail out early if unique substring found.
5. Perf tests integrated into CI (warn-only threshold initially).

**Risks:**
- Premature optimization complexity (Low/Medium) → Keep changes isolated & documented.

**Approval Gate:**
- Benchmarks show <= baseline +5% CPU time.
- Memory footprint stable (< +10%).

---
### Phase 6 – Refactor & Modularization
**Objective:** Reduce complexity & improve maintainability without feature regression.
**Prerequisite:** Stable performance metrics.

**Implementation Steps:**
1. Extract subcomponents: `AnnotationPopover`, `SelectionToolbar`, `HighlightLayer`, `StrategyLegend`, `AnnotationController` service.
2. Create façade service `annotationOrchestrator.ts` exposing: `mergeStrategies`, `applyOffsets`, `prepareExportData`.
3. Add component-level integration tests (mount + simulate events) for each extracted part.
4. Remove legacy sentence-only highlight code (if unified path stable > 2 phases).

**Risks:**
- Regression via subtle prop mismatch (Medium/High) → Snapshot and behavior tests before and after refactor.

**Approval Gate:**
- Test suite parity (no net decrease coverage).
- LOC of `ComparativeResultsDisplay.jsx` reduced by >40%.

---
### Phase 7 – Enhancement & Evidence Layer
**Objective:** Improve analyst efficiency via contextual evidence and cross-panel linking.
**Prerequisite:** Modular architecture in place.

**Implementation Steps:**
1. Evidence tooltip: On marker focus/hover show evidence lines (if `strategy.evidence`).
2. Cross-panel synchronization: Hover in target highlights corresponding approximate source segment (shared event bus / context).
3. Add user preference toggles (persist in localStorage via store) for evidence & sync.
4. Add tests verifying aria-live polite updates when evidence changes.

**Approval Gate:**
- Usability review sign-off.
- No a11y violations introduced.

---
### Phase 8 – Final Hardening & Release Prep
**Objective:** Consolidate, audit, and tag production-ready release.
**Prerequisite:** All prior phases closed; no open P0/P1.

**Implementation Steps:**
1. Full regression matrix run (backend + frontend + E2E + a11y + perf).
2. Security pass (dependency audit + sandbox tests for selection injection).
3. Update `INLINE_ANNOTATION_REVERSE_ENGINEERING_REPORT.md` with "Implemented" markers.
4. Tag release: `v1.0-inline-annotation` (annotated tag).
5. CHANGELOG finalize entries; create summary section in `DOCUMENTATION.md`.
6. Prepare rollback tag pointer (previous stable) and release notes.

**Approval Gate:**
- Sign-off from engineering + product + a11y reviewer.
- All gating tests green.

---
## 3. Safety & Quality Gates (Cross-Phase)
| Gate | Trigger | Verification |
|------|---------|--------------|
| Pre-Phase Entry | Start of each phase | All previous phase approval criteria satisfied |
| Schema Change Gate | Model / API modifications | Pydantic validation tests + backward compatibility tests |
| A11y Gate | After Phase 2 & 7 | Axe-core severity (critical/serious) == 0 |
| Performance Gate | After Phase 5 | Benchmarks vs baseline within thresholds |
| Release Gate | Phase 8 | Full matrix green + sign-offs |

## 4. Risk Register (Ongoing)
| Risk | Likelihood | Impact | Mitigation | Monitor Metric |
|------|------------|--------|-----------|----------------|
| Span drift persists post Phase 3 | Low | High | Canonical resolver + verification tests | Drift test failures |
| Performance regression due to virtualization complexity | Medium | Medium | Controlled thresholds + early profiling | Benchmark p95 |
| A11y regressions after refactor | Medium | Medium | Automated Axe in CI | Axe report delta |
| Overlap merge confusion | Low | Medium | Tooltip listing all codes | User feedback loop |
| Data model confusion during comment/explanation transition | Medium | Medium | Dual-write + telemetry | Export completeness % |

## 5. Git & Branching Strategy
- Branch per phase: `feat/annotation-phase1-integrity`, `feat/annotation-phase2-a11y`, etc.
- Optional sub-branches for large steps (e.g., `feat/annotation-phase3-resolver`).
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:` + issue ID.
- Tags: `phase1-done`, `phase2-done`, … culminating in release tag.
- Rollback: revert merge commit; fast-forward disabled for audit clarity.

## 6. Testing Protocol Matrix
| Layer | Tooling | Coverage Focus |
|-------|---------|----------------|
| Unit (frontend) | Vitest/Jest | Resolver, store actions, overlap merging |
| Unit (backend) | Pytest | modify_span, accept sets validated, export semantics |
| Integration | API + UI harness | Create→modify→accept→export end-to-end |
| E2E | Playwright | Keyboard-only workflow, accessibility menu usage |
| A11y | axe-core CI | Role/label/contrast validation |
| Performance | Custom scripts | Selection→annotation latency, segmentation time |

## 7. Success Metrics
| Metric | Target |
|--------|--------|
| P0 Issues Resolved | 100% (span modify, scroll sync, a11y keyboard, selection precision, gold flag) |
| Annotation Creation Latency | p95 ≤ 300ms on reference dataset |
| A11y Violations (serious+) | 0 |
| Offset Drift Rate (test corpus) | 0% mismatches |
| Code Coverage (delta) | ≥ baseline (+2% goal for affected modules) |
| Component LOC Reduction | ≥ 40% for original monolith file |

## 8. Communication Protocol
- Weekly status summary appended to `STATUS.md` under "Inline Annotation Hardening".
- Phase Kickoff & Closure sections logged in `PROJECT_STATUS_*.md`.
- Escalation Path: Dev → Lead → Product → Stakeholders (documented in STATUS.md entry).

## 9. Approval Checklist Template (Per Phase)
```
Phase <N> Approval Checklist:
[ ] All implementation steps merged
[ ] Tests (unit/integration/E2E) green
[ ] CHANGELOG updated
[ ] Docs updated (ONBOARDING/API/HITL config if applicable)
[ ] Metrics baseline captured
[ ] Rollback instructions validated (dry-run revert)
[ ] Sign-off: Eng Lead / A11y / Product
```

## 10. Rollback Procedures (General Pattern)
1. Identify merge commit: `git log --oneline -n 5`.
2. Create rollback branch: `git checkout -b rollback/phaseN <pre-merge-sha>`.
3. Revert merge (if needed): `git revert -m 1 <merge-sha>`.
4. Run full test matrix; update `CHANGELOG.md` with rollback notice.
5. Tag hotfix: `rollback-phaseN-<date>`.

## 11. Parallel Development Strategy
- Phases 2 & 3 can overlap partially (UI popover vs backend resolver) if feature flags isolate changes.
- Modularization (Phase 6) must wait until earlier stability proven; small pre-factor extractions allowed if test-covered.
- Enhancement layer (Phase 7) gated behind flags until all P0+P1 closed.

## 12. Open Questions (Resolve Before Implementation)
- Should manual annotation creation auto-set `validated`? (Proposed: Yes – gold by definition.)
- Overlap visualization design: stacked pills vs badge count? (Need UX decision.)
- Accept-after-modify semantics: allow & mark validated, or force re-review state? (Clarify rule.)

## 13. Change Log Stub Entry (Planned)
```
## [Unreleased]
- Plan: Added production readiness implementation plan for inline annotation system (`INLINE_ANNOTATION_IMPLEMENTATION_PLAN.md`).
- Upcoming: Phase 1 backend span modification action and gold validation semantics.
```

## 14. Appendices
### 14.1 Strategy Signatures
Signature hash = SHA256 of sorted list: `<strategy_id>|<code>|<char_start>|<char_end>` used for memoization keys.
### 14.2 Metrics Proposal
- `annotation_span_modify_latency_ms` (histogram)
- `annotation_create_offset_corrections` (counter)
- `selection_resolution_method{method=<direct|context|fallback>}` (counter)

---
/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
