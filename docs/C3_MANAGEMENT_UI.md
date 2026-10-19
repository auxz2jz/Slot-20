# C3 host-only management UI

**Status:** C3.1 DESIGN CHECKPOINT. No server or UI implementation exists at
this checkpoint.

## Scope and evidence boundary

C3 is a PC-hosted, localhost-only demonstration that connects the existing B2
bundle verifier to the B3/B4 file-backed state simulator. It is not embedded
camera software, an installer, a flash writer, a network-camera client or an
independent recovery mechanism. Every screen must say **offline host
simulation** and must not imply that rollback or external recovery works on
the physical RLC-811A.

The completed private kernel and rootfs trees are inputs to neither the server
nor its tests and must remain unchanged.

## Bounded sub-tasks

| ID | Deliverable | Independent pass criterion |
| --- | --- | --- |
| C3.1 | This design, endpoint contract and test plan | Sanitized design checkpoint committed and pushed before implementation |
| C3.2 | Loopback HTTP server, login/session/CSRF controls, static dashboard and status API | Unauthenticated requests are denied, authenticated status loads, and all state-changing endpoints require CSRF |
| C3.3 | Synthetic demo-bundle upload through B2 plus B3 state transitions | Tests cover valid and corrupt bundles, separate simulation authorization, success/commit, boot failure/rollback and recovery-required paths |
| C3.4 | Browser verification, labeled screenshots and final handoff | Screenshots show status, validation/update, rollback/error and recovery explanation; focused and regression tests pass |

Stop C3 at C3.4. Do not assemble firmware or add camera/device access.

## Architecture

- Python standard-library `ThreadingHTTPServer` binds only to `127.0.0.1`.
  There is no configurable remote bind address, discovery, outbound network
  request, device-node access or subprocess execution.
- Static HTML, CSS and JavaScript are served only from explicit packaged asset
  names. The server sets a restrictive content-security policy, no-sniff and
  no-store headers.
- Demonstration authentication uses a clearly labeled non-production password,
  an in-memory random salt/digest, bounded expiring sessions and an HttpOnly,
  SameSite=Strict cookie. A per-session CSRF token is required for every
  state-changing API call. This demonstrates an authenticated boundary; it is
  not a production credential store or TLS design.
- Uploaded bundle bodies require a valid bounded `Content-Length`, are streamed
  into a private temporary regular file, and are passed unchanged to
  `verify_update_bundle.verify_bundle`. Temporary uploads are deleted. No
  component is extracted or installed.
- An ephemeral test-only Ed25519 key is created in memory at server startup.
  It signs small synthetic demo bundles and supplies the corresponding B2 trust
  record and release catalog. No private key is written or committed.
- One bounded canonical simulator record is stored in the selected local demo
  data directory. UI actions call `UpdateStateSimulator` methods directly;
  names such as `writing_candidate`, `rolled_back` and `recovery_required`
  remain logical host states only.

## Endpoint contract

| Method/path | Authentication | Behavior |
| --- | --- | --- |
| `GET /` and explicit assets | No | Offline-demo shell and login form |
| `POST /api/login` | No | Bounded JSON login; returns CSRF token and demo session cookie |
| `POST /api/logout` | Session + CSRF | Invalidates only the current in-memory session |
| `GET /api/status` | Session | Returns sanitized simulator snapshot and fixed safety/evidence labels |
| `GET /api/demo-bundle` | Session | Returns a small valid synthetic bundle generated with the ephemeral key |
| `GET /api/demo-bundle-corrupt` | Session | Returns the same class of bundle with a deliberately changed payload byte |
| `POST /api/validate` | Session + CSRF | Streams raw bundle bytes to a temporary file, invokes B2, and on success records receive/verify transitions in B3 |
| `POST /api/action` | Session + CSRF | Allows only a fixed action enum for simulation authorization, stage, write, pending boot, healthy, commit, boot failure, rollback, recovery-required and demo reset |

API responses contain concise codes and authenticated manifest identity only.
They never return payload bytes, key material, filesystem paths or unbounded
logs. Installation authorization remains a separate host-simulation-only
action after successful B2 verification.

## Browser flows

1. Log in with the visibly labeled demo credential and view exact hardware
   profile, known-good release, current logical state and unproven recovery
   warning.
2. Load/validate the valid synthetic bundle. Show all four B2 checks and make
   clear that `installation_authorized` remains false.
3. Give separate demo authorization, then advance through staging, symbolic
   candidate write, pending boot, health confirmation and commit.
4. In a reset run, advance to pending boot, inject a simulated boot failure and
   select logical rollback to the unchanged known-good identity.
5. In another reset run, reject a corrupted bundle and show its exact B2 error.
6. From a simulated boot failure, select `recovery_required` and display that no
   physical recovery method is implemented or independently demonstrated.

## Focused test plan

- Request bounds, unsupported methods/routes, security headers and loopback
  binding.
- Login failure/success, cookie properties, session requirement, CSRF rejection,
  logout and bounded session handling.
- Valid synthetic bundle passes B2 but does not authorize installation.
- Corrupted synthetic bundle fails closed and leaves simulator state unchanged.
- Valid action sequence commits the candidate and retains previous known-good.
- Invalid/unauthorized transitions fail without changing persisted state.
- Boot failure reaches either logical rollback or recovery-required while the
  known-good identity remains preserved.
- Existing B2, B3 and B4 tests continue to pass.

Browser screenshots are demonstration evidence only. They do not satisfy any
hardware, Ethernet, boot, backup, flash, update, rollback or rescue gate in
`docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`.

## C3.1 checkpoint recommendation

- **Completed:** C3 is decomposed into four bounded outputs and its host-only
  API, authentication, upload, state and evidence boundaries are defined.
- **Checkpoint:** commit and push this design before server implementation.
- **Next task:** C3.2 — implement the loopback server, authentication/status
  shell and focused boundary tests.
- **Recommended model and reasoning:** Medium.
- **Why:** C3.2 is routine Python/HTML implementation with explicit boundaries.
- **When to switch:** High is appropriate only if verifier/simulator integration
  exposes a non-routine security or state-consistency problem.
- **Usage preparation:** this design checkpoint precedes all substantial source
  changes; checkpoint C3.2 again before adding full workflows/screenshots.
