# HITL Phase 2 UI Additions (2a–2c)

This document summarizes the UI enhancements delivered through Phase 2 (superscripts, detail panel, filtering & accessibility).

## 2a Superscript Strategy Markers
Rendered inline at target text boundaries using backend `strategy_id`, `code`, and `target_offsets` / sentence fallback.

## 2b Detail Panel
Clicking a marker opens an accessible side panel (role=dialog) with metadata, evidence, offsets and examples. Esc closes, focus returns to marker.

## 2c Filtering & Accessibility (Current)
Features:
- Strategy filter bar (checkboxes per detected code, select all/none)
- Confidence threshold slider (0–100%)
- Colorblind-friendly mode toggle (switches palette; future: pattern overlay)
- Roving tabindex among markers (arrow keys move focus; Home/End supported)
- ARIA labels for markers (`aria-label`, `aria-current` for active)
- Deferred final highlight styling (will integrate with comparative color mapping later)

### Keyboard Navigation
When target marker container focused:
- Arrow Right/Left: move to next/previous marker
- Home/End: jump to first/last marker
- Enter/Space: open detail panel
- Esc: close panel (when panel open)

### Non-Regressive Guarantee
Original Phase 1 data fields untouched; components are additive. Filtering operates purely in view layer—does not mutate raw response.

### Future (Phase 2d / Beyond)
- Guardrail awareness badges (OM+/PRO+ explanation)
- Manual edit / rejection controls
- Unified color mapping across source/target spans + markers
 - Pattern overlays in colorblind mode (implemented Step 4)

## 2d Step 4: Colorblind Pattern Overlays (Unified Mapping)
Adds per-strategy pattern overlays (diagonal stripes, dots, crosshatch, etc.) layered atop unified background colors when colorblind mode is enabled. Patterns:
- Are deterministic per strategy code (stable across sessions)
- Apply only to source/target highlight spans (markers keep solid color for readability)
- Maintain text contrast (patterns rendered at ~30–40% alpha over base color)
- Exposed via `HighContrastPatternLegend` component listing code → name → pattern label

Technical:
- Controlled by existing `colorblindMode` state; no new user setting
- Patterns generated in `buildUnifiedStrategyMap` when `{ enablePatterns: true, colorblindMode: true }`
- CSS injected by `injectUnifiedCSS` combines base color with repeating gradients (no external assets)

Accessibility:
- Superscripts remain solid backgrounds for legibility
- `aria-label` unchanged; patterns are visual affordances only

Testing:
- `patternInjection.test.js` verifies pattern assignment and CSS generation.

Rollback:
- Disable colorblind toggle → patterns removed automatically (pattern property null in unified map)

## Migration Notes
No backend changes required. Frontend adds new optional UI state. Existing API responses remain valid.
# HITL Phase 2 UI Documentation (Starting with 2a)

## 2a Superscript Strategy Markers
Adds inline, Unicode superscript markers (¹ ² ³ ...) above target text representing detected simplification strategies.

### Data Dependencies
- Relies on Phase 1 fields: `strategy_id`, `target_offsets`.
- Offsets optional: sentence fallback used when none provided.

### Rendering Flow
1. Normalize strategies (ensure `strategy_id`, clamp offsets).
2. Build insertion points at each start offset.
3. Assign stable display indices (first occurrence ordering).
4. Insert <sup> markers preserving original text; no mutation of existing highlight spans.
5. Fallback: sentence splitting via regex if no offsets.

### Accessibility
- Markers focusable (tabIndex=0).
- Activation keys: Enter / Space (onMarkerActivate callback).
- Visible focus outline; small footprint to avoid reading disruption.

### Performance Considerations
- O(k log k) for k insertion points; single pass scan building segments.
- No expensive DOM reflow loops; pure React fragment generation.

### Testing
- Vitest unit tests for offset normalization & renderer fallback behavior.

### Non-Regressive Guarantees
- Existing sentence-level highlighting remains untouched.
- All new logic additive; removal simply detaches the superscript layer wrapper.

## Upcoming (Planned)
- 2b: Non-modal detail panel
- 2c: Filtering, keyboard nav, colorblind mode, confidence threshold
- 2d: Guardrail awareness (OM+/PRO+ disabled visuals)

This file will evolve incrementally with each sub-phase.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
