# Inline Annotation & Highlighting Reverse Engineering Report

Date: 2025-09-24  
Branch: `feature/hitl-phase1-stabilization`

## 1. Overview
Comprehensive reverse engineering of the current inline annotation (HITL) feature covering data flow, component architecture, UX interaction patterns, backend integration, gap analysis, and technical debt. Focus: production readiness blockers (P0), high-impact gaps (P1), and systemic risks.

## 2. High-Level Architecture

### 2.1 Frontend Core
- **`ComparativeResultsDisplay.jsx`**: Monolithic controller/view (~2000 LOC). Handles:
  - Strategy merging / filtering / confidence thresholding
  - Superscript marker layer integration
  - Unified character-level highlighting (feature-flagged but hard-coded ON)
  - Manual annotation creation (selection → rationale dialog → API)
  - Hover / context menus (incomplete radial design)
  - Inline edit scaffolding (not complete)
- **`StrategySuperscriptRenderer.jsx`**: Pure render of interleaved text + `<sup>` markers from normalized strategy offsets; roving focus; outlines reflect status.
- **`useAnnotationStore.js`** (Zustand): Annotation CRUD & lifecycle (accept/reject/modify/create/export) with optimistic updates.
- **`unifiedStrategyMapping.js`**: Deterministic code→color mapping, pattern overlay, segment extraction (multi-format offsets) + unused overlap merge helper.
- **`strategyColorMapping.js`**: Color palette + accessible contrast logic.
- **Offset utilities**: `utils/strategyOffsets.js` (insertion points & normalization).

### 2.2 Backend Components
- **API** `annotations.py`: CRUD + export + audit; *no span modify action*.
- **Model** `Annotation` (`models/annotation.py`): `strategy_code`, `target_offsets: List[Offset]`, flags (`validated`, `manually_assigned`), `comment`, `explanation` (unused currently on creation).
- **Strategy pipeline** `comparative_analysis_service.py`:
  - `_identify_simplification_strategies` using `StrategyDetector`
  - Guardrails: OM+/PRO+ filtered unless flags allow
  - Sentence-based positioning → heuristic char offsets
  - Provides `strategy_id`, `target_offsets` (char range), sentence fallback

### 2.3 Data Flow (Selection → Persistence)
1. User selects text inside target panel (unified highlight container or superscript wrapper).
2. `handleTextSelection` (DOM Range → TreeWalker) resolves tentative char offsets.
3. Fallback disambiguation: `disambiguateWithContext` if TreeWalker ambiguous.
4. Context menu & rationale dialog appear (manual strategy selection required).
5. On save: `createAnnotation` (optimistic) → POST → replace temp id.
6. `strategiesDetected` recomputes (merges backend original + store modifications + manual-only).
7. Rendering: superscripts & unified highlight segments update.
8. Accept/reject/modify code patch calls performed with optimistic state; span adjust attempt currently non-persistent.

### 2.4 Interaction Patterns
- Selection events bound to `onMouseUp` and custom `contextmenu` (native menu suppressed inside results container).
- Hover markers spawn delayed (300ms) ephemeral menu; hides after 100ms (risk of flicker).
- Rationale dialog steals focus (textarea autopopulated).
- Keyboard nav for markers (roving index) present; *no keyboard path for manual creation without mouse*.

## 3. Gap Analysis (Condensed)
| Area | Expected | Current | Gap | Priority |
|------|----------|---------|-----|----------|
| Hover menu stability | Persistent, accessible | 300ms show / premature hide | Flicker, lost intent | P0 |
| Scroll synchronization | Bidirectional | None implemented | Misaligned reading | P0 |
| Span modification | Persist new offsets | Backend lacks action | Edits silently lost | P0 |
| Selection precision | Accurate despite markers | `<sup>` interleaved; tree filtering whitespace | Offset drift risk | P0 |
| Keyboard tagging | Non-pointer path | Mouse + suppressed context menu only | Accessibility failure | P0 |
| Gold validation | Accept sets validated flag | Flag not toggled | Training data quality gap | P1 |
| Overlap rendering | Clear composite | Overlaps unmerged | Ambiguity | P1 |
| Tooltip & ARIA for menus | Semantic roles | Partial / missing for hover menu | A11y compliance risk | P1 |
| Circular menu design | Radial UX | Linear/placeholder | Spec deviation | P1 |
| Rationale mapping | Map to explanation | Stored in comment only | Semantic drift | P2 |
| Pattern accessibility | Pattern toggle & persistence | Patterns conditional; no user toggle UI | Incomplete accessibility | P2 |
| Performance instrumentation | Metrics & tracing | DEV console only | Limited observability | P2 |

## 4. Detailed Critical Findings
### 4.1 Span Adjustment Failure
- UI: `modifyAnnotationSpan` sends PATCH `action: 'modify_span'` (then fallback to `'modify'`).
- Backend: `AnnotationAction` only supports `accept|reject|modify`; ignoring offsets.
- Outcome: User perceives success; offsets unchanged after refresh.
- Impact: Data integrity + user trust.

### 4.2 Selection Offset Fragility
- Superscripts inject additional text nodes; TreeWalker excludes whitespace nodes altering index alignment vs original raw text.
- Fallback disambiguation patchy for repeated substrings.
- Needed: canonical raw string index resolution before DOM mapping + normalization.

### 4.3 Accessibility Gaps
- No keyboard path to open strategy selection (context menu suppressed globally; no toolbar alternative).
- Hover menu not keyboard reachable; ephemeral timing undermines motor accessibility.
- Missing ARIA roles on hover menu container & actions.

### 4.4 Incomplete Color / Mapping Semantics
- Source/target highlight parity exists (unified map) but no cross-panel hover linking or synchronized emphasis.
- Overlapping strategies not combined; potential misinterpretation.

### 4.5 Data Model Divergence
- `comment` used for rationale; `explanation` field remains null in exports → confusion for downstream consumers expecting consistent semantics.
- Accept does not set `validated`; export includes `validated` but remains false.

## 5. Technical Debt Inventory
### 5.1 Structural
- God component `ComparativeResultsDisplay` mixes concerns (render, API coordination, accessibility, selection logic, color mapping).
- Legacy sentence highlight code coexists with unified approach (double maintenance surface).

### 5.2 Data & Consistency
- Multiple offset shape variants create normalization complexity.
- Strategy ID stability dependent on config; optimistic referencing brittle if server mode changes mid-session.

### 5.3 Performance
- Repeated segmentation & console diagnostics (only DEV flagged but risk in mis-configured builds).
- No memoization keyed by (textHash, strategiesHash).

### 5.4 Testing Gaps
- No automated test ensuring span modify persists.
- No a11y test coverage (markers focus cycle only partially addresses).
- No export schema verification for manual vs modified tags.

## 6. Automatic Tagging System Evaluation
- Coverage: No explicit hard cap; fallback modulo indexing may conceal missing sentence positions.
- Guardrails: OM+/PRO+ filtered (correct per spec) but UI lacks explanatory messaging.
- Confidence: Direct pass-through; no calibration layer or threshold justification surfaced to user.
- Integration: Manual annotations merged properly; always displayed (activeCodes bypass) – GOOD.
- Weakness: Accept does not promote to gold (`validated`), reducing downstream dataset quality.

## 7. Recommended Remediation (Sequenced)
1. **Backend Schema Upgrade**: Add `modify_span` action with `new_target_offsets`; ensure audit logging; set `validated=True` on accept.
2. **Frontend Store Alignment**: Conditional capability detection (probe HEAD/OPTIONS or feature flag) to use new action; post-response offset verification.
3. **Selection Refactor**: Extract pure function: `resolveOffsets(fullText, selectedText, approxHint) -> {start,end, confidence}`; maintain mapping independent of injected markers.
4. **Accessible Action Surface**: Replace hover ephemeral menu with anchored popover (click / keyboard). Provide toolbar button after selection.
5. **Scroll Synchronization**: Pair refs + throttled ratio sync using rAF guard.
6. **Overlap Strategy Visualization**: Integrate `mergeOverlappingSegments`; composite chip (stacked codes or plus-count badge).
7. **Rationale Field Harmonization**: Decide canonical field (`explanation`); migrate existing `comment` or map at export.
8. **Gold Promotion Logic**: Accept sets `validated`; UI badges reflect gold state.
9. **Instrumentation**: Add lightweight timing (performance.now) & counters exposed via debug panel toggle; remove console spam in production.
10. **Decompose Component**: Split into: `AnnotationInteractionController`, `StrategyPanels`, `SideBySideView`, `HighlightLayer`, `PopoverMenu`.

## 8. Risk Register (Top Five)
| Risk | Mitigation | Residual |
|------|------------|----------|
| Silent span edit failure | Backend action + UI confirmation toast | Low |
| Misaligned offsets | Canonical resolver + validation substring check | Low |
| A11y non-compliance | Keyboard pathways + ARIA roles + tests | Low-Med |
| Overlap ambiguity | Merge & composite representation | Low |
| Data gold flag absence | Update accept path + export validation | Low |

## 9. Traceability (Representative Code Anchors)
- Selection logic: `ComparativeResultsDisplay.jsx` ~400–740
- Hover menu timing: ~770–900 & ~1353–1415
- Unified highlight segmentation: `unifiedStrategyMapping.js` 92–171
- Unused overlap merge: `unifiedStrategyMapping.js` 199–234
- Superscript rendering with status outlines: `StrategySuperscriptRenderer.jsx` entire file
- Store actions & optimistic logic: `useAnnotationStore.js` full file
- Backend patch limitations: `annotations.py` lines 26–61
- Strategy char offset derivation: `comparative_analysis_service.py` lines 460–520

## 10. Proposed Test Additions
| Test | Purpose |
|------|---------|
| create → modify_span → export | Verify persisted offsets reflect adjustment |
| selection offset stability | Ensure substring of stored offsets matches selected text |
| overlap render merging | Confirm merged node count vs overlapping inputs |
| a11y keyboard navigation | Tab/arrow traversal + menu action activation |
| export gold promotion | Accept sets `validated` in JSONL/CSV |

## 11. Summary
Current implementation achieves baseline HITL annotation with integrated manual strategy insertion and unified highlighting but falls short on span persistence, accessibility, and structural modularity. Addressing the P0 list (span modify, scroll sync, hover menu stability, selection precision, keyboard path) is critical for production usability and trust.

---
## 12. Appendices
### 12.1 Glossary
- *Unified Highlighting*: Character-level deterministic color mapping across source & target.
- *Gold Annotation*: Accepted or manually created annotation marked `validated` for ML training.

### 12.2 Abbreviations
- P0 / P1 / P2: Priority tiers (Critical / High / Medium)
- HITL: Human-in-the-Loop

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
