# Accessibility & E2E Timeline (Phase 4f)

Scope
- Accessibility hardening (WCAG): keyboard navigation, aria-labels, focus management, color contrast.
- E2E tests (Playwright): annotation CRUD, export, audit search.
- Persistence modes: validate under FS and SQLite where applicable.

Milestones
- Week 1: Audit UI for WCAG issues; add aria-labels and focus traps; set up Playwright.
- Week 2: Implement E2E for annotation CRUD and audit search; stabilize selectors (data-testid).
- Week 3: Add export flow validations and cross-mode matrix runs; polish color contrast themes.

Success Criteria
- All focusable elements reachable via keyboard; visible focus indicators.
- Aria attributes on interactive controls; no Axe-core critical violations in main flows.
- E2E suite green locally and in CI; flake rate <2% across runs.

Notes
- Use existing feature flags for incremental rollout.
- Keep docs updated alongside code changes.

## 2025-09-10 Audit Kickoff
- Added automated axe-core Playwright spec (`accessibilityAudit.spec.js`) covering main analysis landing state.
- Initial run scope: wcag2a, wcag2aa; region rule temporarily disabled pending landmark refactor.
- Next planned targets: strategy results tab, audit search panel once feature flag enabled.
- Pending manual checks: keyboard focus order, skip link presence, color contrast tokens.
 - Found 1 serious color-contrast violation (primary nav button + green status text). Fixed by darkening blue (#2563eb) and green text class (green-700) and adding visible focus outline.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/