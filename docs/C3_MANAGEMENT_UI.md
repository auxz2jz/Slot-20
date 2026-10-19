# C3 host-only management UI

**Status:** C3 COMPLETE. The loopback server passes synthetic bundles through
the existing B2 verifier and exposes only the fixed B3 host-simulation actions.
Valid, corrupt, success, invalid-transition, rollback and recovery-required
paths are covered by tests and by clearly labeled offline browser evidence.

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

## C3.2 implementation result

`tools/management_demo.py` binds `ThreadingHTTPServer` only to `127.0.0.1` and
serves three explicit assets from `tools/management_demo_assets/`. Its status
response contains the bounded simulator snapshot and fixed false capability
flags for camera contact, flash writing and verified hardware recovery. It has
no outbound request, subprocess, device path or generic file-serving API.

The login uses the intentionally public `admin` / `slot20-demo` credential by
default and visibly labels it non-production. A random in-memory salt, PBKDF2
digest, maximum eight expiring sessions, HttpOnly/SameSite cookie and separate
CSRF token demonstrate the control boundary. The password may be overridden
through `SLOT20_DEMO_PASSWORD`; it is never saved by the application.

Focused C3.2 verification under Python 3.12.14 ran seven tests successfully:

```text
python -m unittest tests.test_management_demo -v
Ran 7 tests in 4.090s — OK
```

The tests prove loopback binding, explicit route handling, security headers,
unauthenticated status rejection, generic invalid-credential rejection,
sanitized authenticated status, CSRF rejection and logout invalidation. They
use a temporary simulator record and contact no external address or camera.

## C3.3 verifier and simulator integration

At server startup, an Ed25519 private key is generated only in memory. It signs
one small two-component synthetic release and populates the matching in-memory
B2 trust record and supported-release catalog. The UI can fetch that bundle or
a copy with one changed payload byte. No key, bundle or component is retained
after the process exits.

Authenticated uploads require `application/octet-stream`, CSRF and an exact
`Content-Length` within B2's existing cap. The request body is streamed in 1
MiB chunks to a private temporary regular file, verified through
`verify_bundle`, and deleted in `finally`. Components are never extracted.
A passing result advances B3 through receive/verify only; the B2 result still
reports `installation_authorized=false`. The user must invoke the separate
`host-simulation-only` authorization action before staging.

The fixed action enum maps directly to existing B3 methods: authorize, stage,
symbolic candidate write, pending boot, healthy, commit, boot failure, logical
rollback and recovery-required. A reset creates a fresh bounded simulator
record and atomically replaces only the local demo record. UI button
availability follows the validated state. Rejected actions do not change the
record.

Focused C3.3 verification under Python 3.12.14 ran 13 tests successfully:

```text
python -m unittest tests.test_management_demo -v
Ran 13 tests in 8.027s — OK
```

The six added tests cover authentication/CSRF on bundle endpoints, all four B2
checks on a valid bundle, corrupt-payload rejection with unchanged state,
separate authorization and successful commit with retained previous
known-good, invalid-transition preservation, and both logical rollback and
recovery-required outcomes with known-good preserved. An early-CSRF negative
test also exposed and verified the fix for unread POST bodies on keep-alive
connections: rejected POSTs now close instead of reinterpreting bundle bytes
as another request.

## C3.3 checkpoint recommendation

- **Completed:** C3.3 integrates bounded synthetic uploads with B2 and the
  fixed B3 simulation actions; all 13 focused tests pass.
- **Checkpoint:** commit and push C3.3 source, assets, tests and this result
  before browser automation or screenshot generation.
- **Next task:** C3.4 — exercise the actual localhost UI in a browser, capture
  clearly labeled screenshots, run regression tests and finalize the handoff.
- **Recommended model and reasoning:** Medium.
- **Why:** C3.4 is routine browser demonstration, visual verification and test
  documentation; no new firmware or hardware logic is required.
- **When to switch:** High is appropriate only if verifier/simulator integration
  exposes a non-routine security or state-consistency problem.
- **Usage preparation:** C3.3 is a recoverable source checkpoint. Refresh usage
  before launching the browser demonstration.

## C3.4 browser verification and completion

The reproducible capture driver is `tools/capture_management_demo.cjs`. It
refuses non-loopback URLs and drives an installed local Edge browser through
Playwright. The final run used Edge `155.0.4283.62`, Node.js `24.19.0` and
Playwright `1.62.1`. All six flows completed with zero browser console errors.
The server was stopped afterward and TCP port 8765 had no listener.

These are screenshots of the actual PC-hosted localhost application, not a
camera UI or a proposed hardware mockup:

| Evidence | Demonstrated state |
| --- | --- |
| [Offline system status](images/c3-offline-status.png) | Authenticated local status, known-good identity and explicit unproven-recovery warning |
| [Validation success](images/c3-validation-success.png) | B2 signature, hash, compatibility and policy checks pass while install authorization remains separate |
| [Simulated update committed](images/c3-update-committed.png) | Complete B3 logical success path and preserved previous known-good identity |
| [Corrupt bundle rejected](images/c3-corrupt-rejected.png) | Payload hash mismatch fails closed without changing the simulator state |
| [Logical rollback](images/c3-logical-rollback.png) | Simulator selects its known-good identity after a synthetic boot failure |
| [External recovery required](images/c3-recovery-required.png) | Explicit statement that no physical rescue method has been implemented or demonstrated |

The images, dimensions, sizes and SHA-256 values are recorded in
`configs/c3_management_demo_result.json`. They contain only synthetic state and
the deliberately public demo credential. No vendor binary, private device
identifier, key or camera data is present.

Final verification under Python 3.12.14:

```text
python -m unittest discover -s tests -v
Ran 77 tests in 8.315s — OK (skipped=2)

python -m py_compile tools/management_demo.py
node --check tools/capture_management_demo.cjs
git diff --check
All passed.
```

The two skips are the pre-existing Windows tests that cannot create symbolic
links without the account privilege. All 13 C3 HTTP/integration tests pass.
This host result does not prove a kernel/rootfs combination, Ethernet operation
on the camera, NAND installation, rollback, or independent hardware recovery.

## Running the offline demonstration

From the repository root with the Python dependencies installed:

```text
python tools/management_demo.py --port 8765
```

Open `http://127.0.0.1:8765/` and use the visibly labeled demonstration
credential `admin` / `slot20-demo`. `SLOT20_DEMO_PASSWORD` may override the
password for a local run. The application intentionally has no TLS,
production credential store, remote binding, installer or camera interface.

## C3 completion recommendation

- **Completed:** C3.1–C3.4 deliver and verify the host-only management demo,
  including authentication, B2 validation, B3 state controls, error/rollback
  explanations and six reproducible browser screenshots.
- **Checkpoint:** commit and push the sanitized source, screenshots, result
  manifest and documentation. The completed private kernel/rootfs trees remain
  unchanged and outside Git.
- **Next task:** D1 planning only — prepare an explicit-approval-gated protocol
  for acquiring a matching spare, obtaining a full per-device backup and
  demonstrating independent recovery. Do not contact hardware yet.
- **Recommended model and reasoning:** High.
- **Why:** recovery planning crosses board identity, NAND/OOB/ECC handling,
  bootloader behavior and evidence gates; mistakes could become destructive.
- **When to switch:** use Medium for documentation after the recovery route is
  established; consider Ultra only for one narrowly defined unresolved
  BootROM/bootloader question after a checkpoint and explicit model selection.
- **Usage preparation:** C3 is a safe source checkpoint. Refresh reliable usage
  and obtain explicit authorization before any expensive or physical D1 work.
