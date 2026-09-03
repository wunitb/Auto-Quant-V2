# Studio readable type scale

- Status: `active`
- Updated: `2026-09-03`
- Related design: [[docs/design/studio-observation-surface]]

## Outcome

Make AutoQuant Studio reports and quantitative evidence readable at 100% zoom
without weakening their dense professional hierarchy or enlarging headings that
are already correctly sized.

## Context

The maintainer verified the surrounding OpenAlice typography improvement but
reported that most AutoQuant Report copy remained extremely small. The current
Studio stylesheet contains 263 explicit font declarations at 5–11px. Report
summaries are commonly 9px, proof blocks 7px, and table labels or values 5–8px,
while headings already range from 13px upward.

OpenAlice owns only iframe zoom and must not inject CSS into this independently
owned Harness surface. The maintainer considered uniform iframe zoom, a Studio
source correction, and a report-renderer-only override, then approved the Studio
source correction. This work uses the private `wunitb/Auto-Quant-V2` fork and
never edits the dirty active research Workspace in place.

## Scope

### In scope

- Add one small Studio typography token set.
- Raise report/body copy to 13px/20px.
- Raise table text to 11–12px with at least 16px line height.
- Keep compact metadata at 10–11px and preserve existing headings.
- Preserve responsive overflow/scroll behavior instead of shrinking text.
- Add static regression coverage and update the Studio design contract.

### Out of scope

- OpenAlice iframe injection or a forced per-Workspace zoom.
- Report schema, research evidence, CLI output, or generated artifacts.
- Marketing, color, spacing, or unrelated Studio redesign.
- Direct edits to the active dirty AutoQuant Workspace.

## Acceptance

- [x] Report executive summaries and explanatory paragraphs compute to 13px with 20px line height.
- [x] Table values compute to 12px/16px and table metadata never drops below 10px.
- [x] Non-heading Studio text has no authored size below 10px.
- [x] Existing heading sizes and evidence hierarchy remain intact.
- [x] Desktop and narrow browser views remain usable without page-level horizontal overflow.
- [x] Static contracts, document links, and complete unit suite pass.

## Work

- [x] Audit current font declarations and agree on the role scale.
- [x] Introduce role tokens and migrate compact metadata/data declarations.
- [x] Calibrate report prose and table surfaces.
- [x] Add guard tests and update durable Studio design guidance.
- [x] Verify the real sample Studio at desktop and narrow widths.
- [ ] Complete the final delivery record after the exact merge commit is tagged.

## Findings and decisions

- 2026-09-03 — The stylesheet has 286 explicit font declarations; 263 are 5–11px. This is a source-scale defect rather than an OpenAlice font regression.
- 2026-09-03 — The maintainer approved a Studio-owned correction: 13/20px report body, 11–12/16px tables, 10–11px metadata, unchanged headings.
- 2026-09-03 — Uniform iframe zoom was rejected because it enlarges already-correct headings and controls together with the undersized copy.
- 2026-09-03 — A renderer-only override was rejected because Studio preview and other evidence surfaces would retain inconsistent typography.
- 2026-09-03 — Browser acceptance passed at desktop and phone widths with the approved computed roles and no page-level overflow.
- 2026-09-03 — The first complete suite exposed only a stale root Skill manifest after the version bump. The repository materializer updated that manifest, its focused regression passed, and the exact-state complete suite then passed all 470 tests.

## Verification

- `uv lock --check` — passed.
- `uv run python -m py_compile autoquant/*.py` — passed.
- `node --check autoquant/studio_assets/studio.js` — passed.
- `uv run python -m unittest tests.test_studio_typography -v` — 5 tests passed.
- `uv run python -m unittest tests.test_repository_workspace.RepositoryWorkspaceTests.test_repository_skill_bundle_matches_current_harness -v` — passed after regenerating the `0.9.35` root Skill manifest with the repository materializer.
- `uv run python scripts/check_doc_links.py` — all 1,574 documentation links resolve.
- `uv run python -m unittest discover -s tests -v` — all 470 tests passed in 883.218 seconds.
- `uv build` — produced the `0.9.35` source distribution and wheel.
- A fresh Python 3.11 environment installed the candidate wheel from `dist/`; `aq --version`, version/capability JSON, `aq-python`, Project listing, and Studio snapshot JSON all resolved from the installed package.
- Chromium rendered the real repository sample at 1440×1000 and 390×844. Computed report/decision prose was 13px/20px, quantitative table rows were 12px/16px, no visible text was below 10px, display headings retained their existing sizes, and document width equalled viewport width at both breakpoints.

## Progress log

- 2026-09-03 — Plan created from the maintainer-approved design after a complete stylesheet audit.
- 2026-09-03 — Implemented the four-role type floor, calibrated report/data surfaces, added static contracts, and completed desktop/narrow browser acceptance.
- 2026-09-03 — Prepared `0.9.35`, regenerated its canonical Workspace Skill manifest, and completed the source, documentation, build, installed-wheel, and 470-test release-candidate audit.

## Completion

Implementation and release-candidate verification are complete. Record the exact merged commit and immutable `v0.9.35` tag here before accepting the plan.
