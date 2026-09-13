# Report scaffolding language

- Status: `completed`
- Updated: `2026-09-13`
- Related design: [[docs/design/run-bound-research-reports]]

## Outcome

Render the section scaffolding in `autoquant/reports.py` in the explicitly
declared language of the analysis, supporting English and Thai.

## Context

Thai prose already survives validation and publication. The renderer's headings,
field labels, and authority warning are fixed English strings. Report loading
re-renders Markdown, so historical default output must remain byte-identical.

## Scope

### In scope

- Optional analysis language, public schema, validation, and report scaffolding.
- Regression tests and the owning design contract.

### Out of scope

- Studio assets, acquisition, Study, Run, and Dossier paths.
- Historical artifact rewrites and translation of machine evidence.

## Acceptance

- [x] Omitted language preserves English output and normalized analysis bytes.
- [x] Explicit `en` and `th` render the requested scaffold; invalid values fail clearly.
- [x] Machine fields, numbers, units, and authored prose remain unchanged.
- [x] Existing report tests and new language regression tests pass.

## Work

- [x] Trace validation, rendering, publication, and immutable loading.
- [x] Implement the optional contract and literal scaffold translations.
- [x] Extend Thai coverage and document the contract.
- [x] Run relevant suites and audit the final diff.

## Findings and decisions

- 2026-09-13 — Preserve omission in normalized JSON to avoid changing historical
  analysis hashes; English is a rendering default, not a migration.
- 2026-09-13 — Translate literals before interpolating values; never replace
  strings in completed Markdown or evidence.

## Verification

- `UV_CACHE_DIR=/tmp/autoquant-uv-cache uv run --python 3.11 python -m unittest
  tests.test_thai_reports -v`: 11 tests passed, including publication/reload and
  byte preservation of the earlier report package.
- `UV_CACHE_DIR=/tmp/autoquant-uv-cache uv run --python 3.11 python -m unittest
  tests.test_reports tests.test_run_reports -v`: 29 tests passed.
- `UV_CACHE_DIR=/tmp/autoquant-uv-cache uv run --python 3.11 python -m unittest
  tests.test_documentation -v`: ownership test passed; double-link test failed
  only on the known pre-existing links in the vendored `self-scheduling` Skill
  copies under `.agents/skills/` and `.claude/skills/`. Those files are unchanged.
- `git diff --check`: passed.
- Captured 2,568 original-renderer UTF-8 bytes before implementation and pinned
  their SHA-256 in the regression test. Explicit English produces identical
  bytes; omission leaves normalized analysis unchanged.
- Scope audit: no changes to Studio assets, acquisition, Study, Run, Dossier,
  or historical research artifacts. Tool cache and test logs stayed in `/tmp`.

## Progress log

- 2026-09-13 — Plan created after tracing the report contract and renderer.
- 2026-09-13 — Added optional language validation/schema, 23 translated headings,
  six bold labels, complete authority warning, and authoring/handoff text.
- 2026-09-13 — Completed regression and existing-suite verification. Separate
  publication snapshots refresh derived timestamps, so the integration check
  compares frozen Run/Session evidence and preserves all prior package bytes.

## Completion

Delivered optional English/Thai report scaffolding with exact legacy English
compatibility, strict unsupported-language rejection, unchanged machine
material, and immutable historical packages. All acceptance items are verified;
no follow-up work is required within this scope.
