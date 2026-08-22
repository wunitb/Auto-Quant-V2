# Generic Harness Web Surface

- Status: `active`
- Target release: `0.9.33`
- Updated: `2026-08-22`
- Related design: [[docs/design/studio-observation-surface]],
  [[docs/design/agent-native-quant-workbench]], and
  [[docs/design/versioning-and-release]].

## Outcome

Make the existing AutoQuant Studio a vendor-neutral Harness Web Surface that
binds exact supervisor-assigned loopback authority, remains origin-neutral and
restrictively embeddable while managed, and preserves the unchanged standalone
Studio security and launch contract.

## Context

`v0.9.32` proved manifest discovery, fixed-port launch, readiness, and browser
suppression, but named its injected environment after OpenAlice and retained
unconditional anti-iframe headers. The Harness v1 contract now standardizes
`HARNESS_*` authority for any compatible supervisor and requires a narrow
managed-only embedding policy. AutoQuant owns its foreground HTTP process and
read-only routes; the supervisor owns allocation, routing, product chrome, and
public origin.

## Scope

### In scope

- Preserve the exact manifest v1 shape and one `http` entry port.
- Activate managed mode only for exact `HARNESS_CAPABILITY=studio`, require
  `HARNESS_HOST`, and require `HARNESS_PORTS` to match the manifest port set
  exactly.
- Bind the exact injected endpoint, reject conflicts and occupied ports, honor
  `HARNESS_NO_OPEN=1`, and retain foreground process ownership and cleanup.
- Pass managed state explicitly into response-header construction, retaining
  strict standalone anti-frame protection and using only the required managed
  `frame-ancestors` allowlist.
- Verify root, packaged assets, health/snapshot APIs, current-origin frontend
  references, opaque `oa-surface-*.localhost` Host handling, and SIGTERM port
  release with real subprocesses.

### Out of scope

- OpenAlice source changes, an OpenAlice SDK, a generic proxy, base paths,
  public-origin negotiation, UI changes, authentication, new SSE/WebSocket
  features, or a second listener.
- The separately proposed tiered-test runner, now targeted to `0.9.34`.

## Acceptance

- [ ] `harness.json` remains manifest v1, declares only `studio.http`, and its
  version agrees with every `0.9.33` product-version authority.
- [ ] Exact `HARNESS_CAPABILITY=studio` launch is fail-closed, binds only the
  injected host/port, suppresses browser opening when directed, and rejects
  incomplete, extra, invalid, conflicting, or occupied authority.
- [ ] Managed HTTP responses omit X-Frame-Options and same-origin CORP and use
  only the required restricted `frame-ancestors`; standalone responses retain
  all prior strict headers.
- [ ] A real manifest-command subprocess serves root, assets, health, and
  snapshot APIs under an opaque localhost Host, reaches truthful readiness,
  takes no fallback port, and releases its process and port after SIGTERM.
- [ ] Frontend runtime references remain same-origin and no internal bind
  address, cookie, authorization, CSRF, redirect, SSE, or WebSocket dependency
  is introduced.
- [ ] Focused, documentation, complete source, build/install, and clean-clone
  release checks pass before `v0.9.33` is tagged at the immutable release SHA.

## Work

- [x] Replace the vendor-specific launch resolver with strict manifest-matched
  `HARNESS_*` authority while preserving standalone isolation.
- [x] Split standalone and managed security headers and thread managed state
  explicitly through CLI, server creation, and request handling.
- [x] Add bounded unit and real-subprocess acceptance coverage, including
  opaque Host routing and SIGTERM cleanup.
- [ ] Update durable Studio/CLI/operator/architecture/version documentation and
  prepare the patch-version authorities.
- [ ] Complete the full release audit, installed artifact replay, tag, push,
  and remote SHA verification.

## Findings and decisions

- 2026-08-22 — Studio currently uses only same-origin root-relative HTTP assets
  and snapshot polling. It has no SSE or WebSocket route, so acceptance covers
  every actually used transport and records those protocols as absent rather
  than adding unused infrastructure.
- 2026-08-22 — The shipped `OPENALICE_*` variables are not retained as aliases:
  the generic contract says only exact `HARNESS_CAPABILITY=studio` activates
  managed mode, and permanent dual parsing would make launch authority
  ambiguous before another host contract has shipped.
- 2026-08-22 — macOS retains closed client connections briefly in `TIME_WAIT`.
  SIGTERM acceptance therefore proves both that the listener rejects new
  connections and that a fresh Studio-style `SO_REUSEADDR` listener can bind
  the same endpoint immediately; it does not confuse connection bookkeeping
  with an owned process or listening-socket leak.

## Verification

- Pending.

## Progress log

- 2026-08-22 — Read the Harness Web Surface v1 contract and acceptance matrix,
  inspected the real manifest, launcher, response headers, frontend URL use,
  readiness route, and current subprocess tests, then activated this plan.
- 2026-08-22 — Implemented generic launch authority, explicit mode-specific
  response policies, and real foreground-process tests. All 20 Studio/version
  focused tests pass in 16.654 seconds.

## Completion

Pending.
