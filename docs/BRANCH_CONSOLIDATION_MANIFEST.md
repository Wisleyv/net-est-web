# Branch Consolidation Manifest

Status: Phase 2 (Feature Flag Scaffold) – Safe Defaults Implemented & Verified
Date: 2025-09-24

## 1. Baseline Verification

| Item | Local | Remote | Match |
|------|-------|--------|-------|
| master HEAD | fadc8eeef23f2360e8ccea689c2e24c74846a9c0 | fadc8eeef23f2360e8ccea689c2e24c74846a9c0 | YES |

## 2. Safety Tags (Created & Pushed)

| Tag Name | Target Ref | Planned SHA | Purpose |
|----------|------------|-------------|---------|
| pre-consolidation/master | origin/master | fadc8eeef23f2360e8ccea689c2e24c74846a9c0 | Recoverable baseline |
| pre-consolidation/feat-annotation-phase1-integrity | origin/feat/annotation-phase1-integrity | 69ef6e4e47a2f6dfa417c466137a1a159a1fbee6 | Redundant branch preservation |
| pre-consolidation/feature-hilt-phase1-stabilization | origin/feature/hitl-phase1-stabilization | eb8d3c1e5160918742c176838f3e3129eb057495 | Redundant branch preservation |

## 3. Branch Disposition (Snapshot)

See `BRANCH_CONSOLIDATION_ANALYSIS.md` for full rationale.

| Branch | Planned Action | Tag? | Notes |
|--------|----------------|------|-------|
| feat/annotation-phase1-integrity | Archive/Delete | Yes | Redundant commits |
| feature/hitl-phase1-stabilization | Archive/Delete | Yes | Duplicate baseline |
| backup-pre-cleanup-2025-08-07 | Archive | Maybe | Historical snapshot |
| chore/sanitize-backend | Partial Integrate | No | Selective cherry-picks |
| dev-10-08-2025 | Partial Integrate | No | Feature extraction |
| dev-18-08-2025 | Partial Integrate | No | Feature extraction |
| chore/replace-neuralmind-with-minilm | Remove | No | Empty diff |
| feat/lexical-scorer | Remove | No | Empty diff |
| ci/fix-smoke-install | Remove | No | Empty diff |
| feature/human-in-loop-tests | Review/Archive | Maybe | Minor delta |

## 4. Pending Cherry-Pick Commit Collection

To be populated after approval (SHA lists):

| Source Branch | Candidate Commits (SHA prefix) | Feature Group |
|---------------|-------------------------------|--------------|
| chore/sanitize-backend | _TBD_ | Hygiene |
| dev-10-08-2025 | _TBD_ | Manual Tags / Hierarchical |
| dev-18-08-2025 | _TBD_ | Strategy Detector / Enhanced Input |

## 5. Verification Checklist (Phase 0)

| Check | Status | Evidence |
|-------|--------|----------|
| Refs pruned | DONE | `git fetch --all --prune` executed |
| master alignment | DONE | Matching SHA recorded |
| Tag targets captured | DONE | Section 2 table |
| Uncommitted changes | PENDING | (to record) |
| CI status (if available) | PENDING | (manual check) |

## 6. Proposed (Not Yet Executed) Commands

```
# Create safety tags (after approval)
git tag pre-consolidation/master fadc8eeef23f2360e8ccea689c2e24c74846a9c0
git tag pre-consolidation/feat-annotation-phase1-integrity 69ef6e4e47a2f6dfa417c466137a1a159a1fbee6
git tag pre-consolidation/feature-hilt-phase1-stabilization eb8d3c1e5160918742c176838f3e3129eb057495

# Push tags (after review)
git push origin pre-consolidation/master pre-consolidation/feat-annotation-phase1-integrity pre-consolidation/feature-hilt-phase1-stabilization

# (Later) Delete redundant branches (after manifest & approval)
# git push origin :feat/annotation-phase1-integrity :feature/hitl-phase1-stabilization
```

## 7. Approval Gates Status

| Gate | Description | Status | Notes |
|------|-------------|--------|-------|
| A | Safety tagging & freeze validation | COMPLETE | Tags pushed |
| B | Redundant branch removal | COMPLETE | feat/annotation-phase1-integrity & feature/hitl-phase1-stabilization deleted (tags retained) |
| C | Post-cherry-pick feature integration | PENDING | Await hygiene + feature SHA selection |
| D | Pruning remaining obsolete branches | PENDING | After integration branch stabilized |
| E | Baseline promotion | PENDING | Final verification phase |

Deletion Timestamp (UTC): (record at commit time)

Command Executed:
```
git push origin :feat/annotation-phase1-integrity :feature/hitl-phase1-stabilization
```

## 8. Post-Deletion Verification

| Check | Result | Evidence |
|-------|--------|----------|
| Inventory regenerated | PASS | `python tools/branch_inventory.py` -> 9 branches |
| Deleted branches absent | PASS | No matches for names in `BRANCH_INVENTORY.json` |
| Safety tags still present | PASS | `git tag -l 'pre-consolidation/*'` (manual check) |
| Master unchanged | PASS | SHA still `fadc8eeef23f2360e8ccea689c2e24c74846a9c0` |

---

## 9. Candidate Cherry-Pick Matrix (Gate C Preparation)

Legend: Type = hygiene | feature-core | feature-support | docs-only; Inclusion = yes | review | exclude.

### 9.1 Hygiene Branch (`chore/sanitize-backend`)

| SHA | Subject (truncated) | Key Paths (sample) | Type | Inclusion | Rationale |
|-----|---------------------|--------------------|------|-----------|-----------|
| 0537cab | ci: install dependencies... | .github/workflows/ci-backend.yml | hygiene | review | CI change may already be on master; verify diff |
| 4ed12db | chore: archive debug files... | backend/archived/* | hygiene | yes | Archive reduces clutter; non-runtime |
| d4b282e | chore: add archive scaffolding... | backend/.gitignore, workflows | hygiene | yes | Improves ignore + structure |
| 61f256e | test: rebaseline API snapshots... | services + snapshot tests | feature-support | exclude | Snapshot alignment obsolete vs current master state |
| 2e191f8 | test: rebaseline + normalize... | broad service/model spread | mixed | review | Large surface; may overlap with current code; extract only needed normalization later |
| 8a90c53 | Stabilize comparative analysis substitution heuristics... | comparative_analysis_service.py | feature-core | review | Need diff vs master to confirm uniqueness |
| 2a9c7a9 | Phase C implementation (full-stack) | services, frontend, docs | feature-core | review | Overlaps with dev branches; de-duplicate with selected feature commits |
| 9095afd | feat: semantic-based algorithm suite... | strategy detector docs | feature-core | exclude | Superseded by later integrated changes (duplicate with other branch commits) |
| 354cdb8 | Fix NetWork error on Frontend | EnhancedTextInput.jsx | feature-support | yes | Narrow, low-risk bug fix |

### 9.2 Feature Set A (`dev-10-08-2025`)

| SHA | Subject | Key Paths | Type | Inclusion | Rationale |
|-----|---------|----------|------|-----------|-----------|
| 6f0013f | hierarchical pipeline (Module 3) | hierarchical_nodes, services, tests | feature-core | review | Introduces new structures; ensure no regression vs current master implementation |
| 621163c | semantic-based algorithm suite | manual_tags, services, frontend components | feature-core | review | Large multi-surface commit; consider partial extraction for manual tags only |

### 9.3 Feature Set B (`dev-18-08-2025`)

| SHA | Subject | Key Paths | Type | Inclusion | Rationale |
|-----|---------|----------|------|-----------|-----------|
| 2a9c7a9 | Phase C implementation | strategy_detector, EnhancedTextInput, docs | feature-core | review | Overlaps with hygiene branch listing; consolidate once |
| 354cdb8 | Frontend network fix | EnhancedTextInput.jsx | feature-support | yes | Already marked; duplicate origin commit; include once only |
| 9095afd | semantic algorithm suite | strategy docs | docs-only | exclude | Superseded docs; replaced by revised report version |

### 9.4 Preliminary Inclusion Plan

Planned YES (initial draft):
- 4ed12db, d4b282e (hygiene / archival)
- 354cdb8 (frontend bug fix)

Needs REVIEW (diff assessment next):
- 0537cab (ensure not already applied)
- 8a90c53 (heuristic stabilization uniqueness)
- 2a9c7a9 (Phase C – avoid double pulling)
- 2e191f8 (extract only stable normalization logic if still absent)
- 6f0013f (hierarchical pipeline – validate compatibility)
- 621163c (manual tags portion isolatable?)

Planned EXCLUDE:
- 61f256e (obsolete snapshot baselines)
- 9095afd (duplicate semantic suite doc focus)

### 9.5 Next Analytical Step

For each REVIEW commit: produce `git diff master..<sha>` focused summary (service/model/API changes) and map to existing master lines to confirm necessity. Results will populate section 10.

---

---

No destructive operations have been performed; this document is preparatory only.

---

## 10. Focused Uniqueness Matrix (Strategic Extraction View)

Strategic Direction Applied:
- Manual tagging: integrate into existing annotation pipeline (not a parallel subsystem)
- Hierarchical output: gated behind feature flag (disabled by default)
- CI: retain current simplified workflow; defer enhancements

Legend:
- Mode: cherry-pick (raw), reconstruct (hand-extracted minimal patch), omit (do nothing)
- Flag: name of gating mechanism (env var or config key) where applicable

| Asset Group | Source Commit(s) | Representative Files (planned subset) | Overlap w/ master | Mode | Flag | Tests Required | Risk | Notes |
|-------------|------------------|---------------------------------------|-------------------|------|------|----------------|------|-------|
| Hierarchical Core (data model only) | 6f0013f | backend/src/models/hierarchical_nodes.py | Absent | reconstruct | FEATURE_HIER_OUTPUT | Add unit: node shape & serialization | Low | Limit to model + minimal import wiring; defer service logic until stable |
| Hierarchical Service Hooks (minimal) | 6f0013f (subset) | comparative_analysis_service.py (specific insert points), semantic_alignment_service.py (only if required) | Partial overlap | reconstruct | FEATURE_HIER_OUTPUT | Integration test (guarded) | Moderate | Avoid pulling unrelated refactors; add conditional return fields |
| Manual Tagging (API + Service + Model) | 621163c | backend/src/api/manual_tags.py; backend/src/models/manual_tags.py; backend/src/services/manual_tags_service.py | Fully absent | reconstruct | FEATURE_MANUAL_TAGS (or reuse generic) | Route test + service unit test | Low | Ensure reuse of existing auth / request parsing utilities |
| Comparative Heuristic Refinement | 8a90c53 | backend/src/services/comparative_analysis_service.py (diff hunks) | Partially present | reconstruct | (none) | Existing test extension + one new edge case | Low | Extract only substitution heuristic changes |
| Salience Heatmap Frontend | 621163c | frontend/src/components/SentenceSalienceHeatmap.jsx + tests | Absent | reconstruct | FEATURE_HIER_OUTPUT (reuse) | Component render + data contract mock test | Low | Depends on hierarchical salience data shape; behind same flag |
| Enhanced ComparativeResults Display Augmentation | 621163c | frontend/src/components/ComparativeResultsDisplay.jsx (partial diff) | Present (older) | reconstruct | FEATURE_HIER_OUTPUT | Snapshot / behavior test | Low | Only add flag-aware conditional blocks |
| Manual Tagging Frontend Hooks (if any) | 621163c | (Portions of components / services referencing manual tags) | Not present | defer | FEATURE_MANUAL_TAGS | Later when backend stable | N/A | Stage 2 (post-backend validation) |
| Frontend API Service Extensions | 621163c | frontend/src/services/manualTagsService.js (maybe unify) | Absent | defer | FEATURE_MANUAL_TAGS | Service mock test | N/A | Only after deciding UI surfacing timing |
| Strategy Detector Bulk Changes | 2e191f8 / 2a9c7a9 | backend/src/services/strategy_detector*.py | High overlap / churn | omit | (n/a) | None | High | Current master already consolidated; skip to avoid regression |
| Snapshot Rebaseline Assets | 2e191f8 | backend/tests/snapshot_tests/... | Obsolete | omit | (n/a) | None | Low | Regenerate small curated set later if needed |
| CI Workflow Install Step | 0537cab | .github/workflows/ci-backend.yml (add pip install) | Possibly superseded | omit | (n/a) | None | Low | Keep simplified pipeline; revisit post-stabilization |
| Frontend Network Bug Fix | 354cdb8 | frontend/src/components/EnhancedTextInput.jsx | Not present | cherry-pick | (none) | Existing tests pass / add simple interaction test | Low | Small isolated fix |

Planned Feature Flags:
| Flag | Purpose | Default | Location | Implementation Sketch |
|------|---------|---------|----------|----------------------|
| FEATURE_HIER_OUTPUT | Gate hierarchical enriched output & salience heatmap | False | env var -> config | Add boolean in config; conditional assembly of hierarchical fields + conditional frontend render |
| FEATURE_MANUAL_TAGS | Gate manual tagging endpoints & UI | False | env var -> config | Register route only if flag enabled; UI conditional fetch |

Feature Flag Mechanism (proposed):
1. Add environment variables (e.g., `FEATURE_HIER_OUTPUT=0`, `FEATURE_MANUAL_TAGS=0`).
2. Extend existing config loader (`backend/src/core/config.py`) to expose booleans.
3. Wrap API route registration and response augmentation in conditional checks.
4. Frontend: simple runtime flag fetch via existing config endpoint or .env build-time injection.

## 11. Cherry-Pick / Reconstruction Recommendation (For Approval)

Execution Branch: `integration/consolidation-phase2`

Order (dependency aware):
1. Config & Feature Flags Scaffold (new flags only; no behavior change).
2. Hierarchical Core Model (nodes file + minimal export wiring) – reconstruct.
3. Hierarchical Service Hooks (guarded optional fields) – reconstruct.
4. Manual Tagging Backend (model -> service -> API route) – reconstruct.
5. Comparative Heuristic Refinement (service diff hunks) – reconstruct.
6. Frontend: Salience Heatmap component + tests (flagged) – reconstruct.
7. Frontend: ComparativeResults conditional augmentation (flagged) – reconstruct.
8. Frontend: Network bug fix (354cdb8) – cherry-pick (or re-author if conflict trivial).
9. (Deferred) Manual Tagging Frontend + Service wrapper – pending backend validation.

Concrete Patch File List (initial slice):
Backend (new):
- backend/src/models/hierarchical_nodes.py
- backend/src/models/manual_tags.py
- backend/src/services/manual_tags_service.py
- backend/src/api/manual_tags.py

Backend (modified):
- backend/src/core/config.py (add flags)
- backend/src/services/comparative_analysis_service.py (heuristic diff + conditional hierarchical output)
- backend/src/services/semantic_alignment_service.py (only if hierarchical dependency required)
- backend/src/api/comparative_analysis.py (conditional response fields)
- backend/src/main.py (conditional route registration / feature flags wiring)

Frontend (new):
- frontend/src/components/SentenceSalienceHeatmap.jsx
- frontend/src/components/__tests__/SentenceSalienceHeatmap.test.jsx (consolidated test)

Frontend (modified):
- frontend/src/components/ComparativeResultsDisplay.jsx
- frontend/src/components/EnhancedTextInput.jsx (network fix if not yet present)
- frontend/src/services/api.js (only if hierarchical or manual tag endpoints enumerated)

Tests (backend additions):
- backend/tests/test_hierarchical_output.py (flag-aware update)
- backend/tests/test_manual_tags_api.py (new)
- backend/tests/test_comparative_analysis_heuristics.py (new minimal cases)

Exclusions Justification:
- Strategy detector large churn skipped to avoid destabilizing baseline.
- Snapshot directories excluded; will create lean, behavior-focused tests instead.
- CI modifications postponed; current pipeline sufficient for consolidation phase.

Rollback Strategy:
- Each patch applied in a separate commit with prefix `consolidation:` and scope tag.
- If a patch introduces regression, revert that single commit without impacting others.

Approval Gate Criteria (before execution):
| Criterion | Condition |
|-----------|-----------|
| Matrix Accepted | Section 10 table acknowledged |
| File List Approved | Concrete patch file list confirmed or amended |
| Flag Names Approved | FEATURE_HIER_OUTPUT / FEATURE_MANUAL_TAGS accepted or revised |
| Order Approved | Step sequence confirmed |

Pending User Decisions (if any):
- Confirm flag naming (alternative: HIER_OUTPUT_ENABLED, MANUAL_TAGS_ENABLED)
- Confirm whether manual tags need initial seed data (none assumed)

Once approved: proceed to create integration branch and begin reconstruction commits.

---

## 12. Phase 2 Completion Summary (Added 2025-09-24)

Scope: Establish minimal, production-safe feature flag infrastructure enabling deferred reconstruction without destabilizing current baseline.

Implemented:
- Added experimental flags (defaults false): `hierarchical_output`, `manual_tagging`.
- Introduced `backend/src/core/feature_switches.py` providing stable import surface (`FEATURE_HIERARCHICAL_OUTPUT`, `FEATURE_MANUAL_TAGGING`).
- Hardened YAML: set previous `hierarchical_output: true` to `false` (safety-first posture).
- Added pytest `test_feature_flags_defaults.py` (asserting YAML path + accessor constants + key presence).
- Test run (models disabled) passed; zero regressions.

Risk Posture:
- Flags default to disabled; no latent code paths activated.
- Manual tagging logic not yet present—scaffold only (no dead imports).
- Hierarchical output remains available only via explicit request param override or future flag enablement.

Rollback:
- Revert Phase 2 checkpoint commit to restore prior flag state.
- Or toggle YAML booleans directly for rapid enablement.

Deferred (Phase 3+):
- Reconstruction patches (hierarchical core, manual tagging backend, salience heatmap, comparative heuristics refinement).
- Frontend conditional rendering components.
- Hot-reload facility for dynamic flag toggling.

Next Focus (outside consolidation scope):
- Resume P0 inline annotation debugging tasks using stable baseline.

Audit Note: This summary marks a safe pause point; no partial feature integrations pending activation.
