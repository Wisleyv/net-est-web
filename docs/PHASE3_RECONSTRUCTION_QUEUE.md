# Phase 3 Reconstruction Queue (Deferred)

Status: Paused post Phase 2 – focus shifted to P0 debugging (inline annotation).
Date: 2025-09-24

## Guiding Principles
- Only reintroduce deferred features once P0 stability issues are resolved.
- All additions must be guarded by existing feature flags or new flags if scope expands.
- Prefer reconstruction (surgical patches) over raw cherry-picks where commits contain mixed concerns.

## Feature Backlog Overview
| Item | Flag | Scope Type | Current State | Effort | Risk | Notes |
|------|------|-----------|---------------|--------|------|-------|
| Hierarchical Core Data Model | FEATURE_HIERARCHICAL_OUTPUT | backend model | Not present (concept scaffolding only) | S | Low | Create isolated `hierarchical_nodes` model + serialization tests. |
| Hierarchical Service Injection | FEATURE_HIERARCHICAL_OUTPUT | backend service | Partial logic placeholders exist | M | Medium | Add conditional assembly path; ensure no latency spike. |
| Manual Tagging Backend API | FEATURE_MANUAL_TAGGING | backend api/service/model | Absent | M | Low | Implement minimal CRUD or ingest + validation. |
| Comparative Heuristic Refinement | (none) | backend service tweak | Not applied | S | Low | Extract only substitution logic improvements. |
| Salience Heatmap Component | FEATURE_HIERARCHICAL_OUTPUT | frontend component | Absent | S | Low | Pure presentation; mock data test. |
| ComparativeResults Conditional UI | FEATURE_HIERARCHICAL_OUTPUT | frontend enhancement | Partial (baseline) | S | Low | Add guarded sections; no regression. |
| Manual Tagging Frontend Hooks | FEATURE_MANUAL_TAGGING | frontend service + components | Absent | M | Medium | Wait until backend stable + data contract fixed. |
| API Endpoint Flag Exposure | (existing) | backend route | Exists (`/list_feature_flags`) | XS | Low | Optional expansion: embed descriptions + groups. |

## Execution Order (Recommended When Resuming)
1. Hierarchical Core Data Model
2. Manual Tagging Backend API (foundation)
3. Comparative Heuristic Refinement (quick win)
4. Hierarchical Service Injection (ties model + service)
5. Salience Heatmap Component (visualization)
6. ComparativeResults Conditional UI
7. Manual Tagging Frontend Hooks

## Tests To Add
| Test Name | Purpose | Blocking Dependency |
|-----------|---------|--------------------|
| test_hierarchical_nodes_model.py | Validate structure & JSON schema | Model definition |
| test_manual_tags_api_basic.py | Round-trip create/list | API scaffold |
| test_comparative_substitution_refinement.py | Ensure improved heuristic triggers | Logic patch |
| test_hierarchical_output_integration.py | End-to-end flag-enabled output | Model + service injection |
| test_salience_heatmap_component.jsx | Render & prop contract | Component scaffold |

## Non-Goals For Phase 3
- Bulk strategy detector rewrites
- Snapshot-based golden file expansions
- CI pipeline restructuring

## Rollback Guidelines
Each reconstruction commit must:
- Use prefix `reconstruct:<scope>`
- Include a Revert Plan line in commit body
- Contain only one logical feature slice

## Metrics To Watch (Post-Resume)
| Metric | Source | Threshold |
|--------|--------|-----------|
| API latency (comparative) | adhoc timing logs | p95 < 1.5x baseline |
| Error rate | structured logs | No new error class |
| Flag enable regression | selective enable test | 0 failing tests |

## Enablement Playbook (Future)
```
# Enable hierarchical output temporarily
export FEATURE_HIER_OUTPUT=1
# Run targeted tests
pytest -k hierarchical_output -q

# Roll back quickly if regression observed
git revert <commit_sha>
```

## Decision Log Placeholder
| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| (pending) | | | |

----
Audit Note: This queue intentionally remains dormant until P0 issues cleared.
