# Hardware development and multi-camera architecture plan

**Status:** planning only. No camera connection, query, reboot, reset, opening,
electrical probing, NAND operation, firmware assembly or installation is
authorized by this document.

## Target roles and evidence boundary

The owner-confirmed primary development target is an existing Reolink RLC-811A
with hardware version `IPC_523128M8MP`. Its identity and installed firmware
`v3.1.0.1643_2402219117` were previously confirmed from owner-provided Device
Info screenshots. This unit is older but remains in active security service.
It is therefore an **in-service development reference**, not a sacrificial
recovery surrogate.

The D2a seller research remains useful but **D2a-1 seller contact is on hold**.
No candidate record or research is deleted. A separate exact-match spare is
still required before destructive testing or recovery proof.

Evidence classes must remain distinct:

1. **Previously supplied evidence:** owner screenshots and matching offline
   package analysis; safe to inventory without camera contact.
2. **Approved read-only live evidence:** one specifically authorized interface,
   observation and time window; never implied by this plan.
3. **Matching-spare evidence:** physical identity, backup and recovery results
   produced under the D1 G0–G9 gates.
4. **Production installation evidence:** eligible only after the full backup,
   independent recovery, update and owner-review gates are satisfied.

## Permanent safety boundary

- Preserve the in-service camera's stock firmware and availability. A planned
  observation must not silently become a configuration or reboot session.
- Every live action requires fresh approval naming the interface and action.
  Approval for viewing Device Info does not authorize discovery, scanning,
  authentication by a new client, streaming tests, motor movement, reboot,
  opening, UART, NAND access or update checks.
- Do not use the in-service camera for deliberate failure injection.
- Before any firmware installation or destructive test, acquire and verify the
  device-specific full backup required by D1 and independently demonstrate
  recovery on a matching spare. Development-file backups and vendor update
  packages do not satisfy that gate.
- Keep unique identifiers, credentials, recordings, full dumps and calibration
  data private. Public records use only redacted evidence and hashes.
- Any unexpected state change, service interruption, thermal/power anomaly,
  identity mismatch or tool offering a write/erase/update operation is an
  immediate abort.

## Three coordinated development lanes

| Lane | Purpose | Current boundary |
| --- | --- | --- |
| P — primary reference | Establish identity and ordinary behavior of the owner-confirmed unit with the least invasive approved observations | Offline evidence inventory first; no live action is authorized |
| M — modular software | Convert existing host-only concepts into vendor-neutral core contracts plus strict hardware profiles and adapters | Design only in this task; no refactor or device I/O |
| R — recovery spare | Acquire an exact-match sacrificial unit, verify complete raw/OOB backup, and prove independent restore/recovery | D2a-1 is on hold; D1 G0–G9 remain mandatory |

Progress in lane P does not waive lane R. A working read-only diagnostic session
on the primary camera cannot prove backup completeness, safe writing, rollback
or independent recovery.

## Staged primary-camera roadmap

Each stage is a separate atomic task and ends with an evidence review. No stage
automatically authorizes the next.

| Stage | Bounded objective | Pass evidence | Approval / abort boundary |
| --- | --- | --- | --- |
| **H0 — existing-evidence baseline** | Create a sanitized identity/capability record solely from existing screenshots and verified offline findings | Exact model, hardware revision, firmware, evidence source, known/unknown fields and redaction check recorded with no live contact | Current next task; stop if source evidence is unavailable or exposes private fields |
| **H1 — live-observation protocol** | Define one proposed read-only session: exact interface, screens/fields, operator, duration, privacy handling and zero-change checklist | Owner reviews a command/screen-level plan and explicit aborts; no connection made | Planning does not grant approval; stop until the owner explicitly approves the exact H2 actions |
| **H2 — approved identification observation** | Through only the already approved interface, view and record Device Info and immutable/read-only status fields | Redacted evidence matches `RLC-811A / IPC_523128M8MP`; before/after checklist shows no setting, update, reboot or motor action | Abort on login/setup prompts, update prompts, mismatch or any required setting change |
| **H3 — offline reconciliation** | Compare H2 observations with the matching package, FDT, U-Boot and BSP records | Discrepancy table classifies confirmed live facts, static leads and unresolved items | Offline only; discrepancies do not authorize deeper probing |
| **H4 — approved ordinary diagnostics** | One separately reviewed, non-disruptive health/status observation using an existing owner-approved path | Bounded status evidence and no security-coverage interruption | Discovery/scanning, new services, stream capture, motor/IR/light/audio actuation and reboot each remain separately prohibited unless explicitly approved |
| **H5 — external physical inventory** | During owner-approved maintenance downtime, photograph accessible exterior label, connectors, power/PoE arrangement and installation constraints without opening | Redacted exterior record and safe-access assessment | No depowering, removal, seal breaking or opening without a new approval |
| **H6 — primary-reference freeze** | Consolidate H0–H5 into a versioned board-profile evidence record | Every field names its evidence class and confidence; unknowns remain unknown | This profile permits host-side compatibility checks only, never writes |

Opening, passive electrical work, raw backup, RAM boot and write/recovery tests
remain in the separate D1 G2–G9 spare-camera protocol. Because the primary unit
is in active service, those activities should normally occur first on the
matching spare even if the owner later approves downtime.

## Reusable software architecture

The existing code already separates several host-only responsibilities:

- `verify_update_bundle.py` provides bounded container parsing, cryptographic
  verification and policy evaluation.
- `update_state_simulator.py` provides the logical update/boot state machine and
  durable host record.
- `management_demo.py` and its static assets demonstrate authentication,
  request bounds, CSRF protection, status presentation and explicit separation
  of validation from simulated authorization.
- Offline package/UBI tools provide read-only artifact processing with bounded
  input handling.

These are reusable concepts, but the current implementation is not yet a
multi-camera framework: the RLC-811A hardware profile is hard-coded, component
installation has no trusted mapping, and there are no real boot, storage,
health, recovery, network or media backends.

### Proposed layers

| Layer | Portable responsibility | Hardware-specific responsibility |
| --- | --- | --- |
| Core security and policy | Bundle framing, canonical manifest, signature/hash checks, key status, version policy, authorization separation | Exact profile allow-list, component roles and installed-size limits supplied by a trusted board profile |
| Update orchestration | State transitions, audit events, health deadline semantics and failure handling | Storage transaction, boot selector, durable state location, watchdog and actual rollback implementation |
| Management service/UI | Authentication/session/CSRF controls, bounded upload, status/update workflow and recovery explanations | Board capabilities, supported actions, network provisioning and hardware health fields |
| Build/provenance | Input manifests, source/license hashes, reproducibility checks and artifact metadata | Architecture/ABI, BSP/toolchain, kernel config, DTS, firmware packaging and required proprietary dependencies |
| Artifact analysis | Bounded parsers, hashing, evidence manifests and generic UBI/UBIFS handling | Vendor container layout, image validation rules, encryption/compression and partition interpretation |
| Diagnostics | Typed observation records, redaction, evidence class and capability reporting | Vendor protocol/client, register/sysfs paths, sensor/ISP status and safe per-board probes |
| Media features | Capability API for video, audio, lens, lighting and AI | Sensor, ISP, encoder, motor, IR-cut, spotlight, microphone/speaker and model-specific calibration/drivers |
| Recovery | Common evidence/approval model and recovery result format | Boot ROM, UART/U-Boot, TFTP/MMC, raw NAND programmer, OOB/ECC/bad-block rules and board wiring |

### Strict hardware-specific profile

Each supported target should have one immutable, versioned profile keyed by
manufacturer, model and exact hardware revision. A profile should eventually
contain only reviewed declarations and adapter selections:

- CPU/SoC, instruction architecture, ABI, DRAM evidence and toolchain/build
  inputs;
- board DTS/DTSI and pinctrl, clocks, regulators and GPIO ownership;
- bootloader family, image-validation scheme, environment behavior, load/RAM
  addresses and boot-control capabilities;
- flash technology, chip/geometry, page/OOB/ECC/bad-block policy, partition
  ownership and protected calibration/identity regions;
- Ethernet MAC/PHY, MDIO/pinctrl/reset wiring and kernel driver;
- image sensor, ISP, encoder, lens/motor, IR-cut, illumination, audio and other
  peripheral drivers and calibration dependencies;
- permitted bundle component types, bounded sizes and **no write destinations
  until the recovery gate is independently satisfied**; and
- recovery methods with explicit evidence status (`unverified`, `read-only
  observed`, `spare-demonstrated`) rather than a Boolean claim derived from
  compiled commands.

Device-instance data—serials, MAC addresses, credentials, certificates,
calibration blobs, bad-block maps and raw backups—must never be stored in the
public profile. It belongs in a separately protected private instance record.

### Adapter contracts for later implementation

Future refactoring should introduce narrow contracts rather than forks of the
whole application:

- `HardwareIdentityProvider`: returns a trusted exact profile and evidence
  provenance; never accepts the bundle's self-claimed identity.
- `ArtifactFormatAdapter`: parses one vendor/container family with fixed bounds.
- `StorageInventory`: read-only geometry/partition/protection reporting.
- `InstallBackend`: privileged component-to-storage transactions; absent by
  default and impossible to construct until profile/recovery prerequisites pass.
- `BootControl`: candidate selection, health confirmation and rollback semantics.
- `NetworkBackend`: MAC/PHY/link/address status and provisioning.
- `HealthProvider`: bounded boot/service/watchdog readiness.
- `RecoveryProvider`: capability and evidence reporting plus separately gated
  recovery actions.
- `MediaBackend`: sensor/ISP/encode/lens/audio/lighting capabilities.

The web service and bundle parser should depend on these contracts, not on
Reolink paths or NAND offsets. Unsupported methods fail closed. A new camera
model should normally add a profile plus required adapters/tests; it must not
weaken exact-match checks or duplicate the security/update core.

## Atomic continuation plan

| ID | Single output | Completion criterion | Reasoning |
| --- | --- | --- | --- |
| **H0 (NEXT)** | Sanitized primary-target evidence baseline from already supplied material | Required/unknown fields and source class recorded; private fields excluded; no live contact | Medium |
| H1 | Proposed read-only live-observation protocol | Exact actions, non-actions, privacy handling, aborts and approval prompt reviewed; no connection | Medium |
| H2 | One approved identification observation record | Redacted exact identity captured with no setting/reboot/update/motor change | High because it is the first live-device action |
| H3 | Offline live-vs-static reconciliation table | Every item marked confirmed, contradicted or unresolved with provenance | Medium–High |
| M1 | Versioned hardware-profile schema and synthetic fixtures | Schema separates public board data from private instance data and rejects ambiguous revisions | High |
| M2 | Adapter interface design plus no-op/synthetic reference adapters | Contract tests prove fail-closed behavior; no camera/device path | High |
| M3 | Incremental extraction of portable core from hard-coded profile use | Existing B2–C3 tests remain passing plus multi-profile synthetic negatives | High; only after separate approval to refactor |
| R0 | Resume D2a evidence outreach if the owner removes the hold | Exact-unit seller proof or rejection; no purchase | Medium |
| R1+ | Continue D1 G0–G9 on an acquired exact-match spare | One separately approved gate and evidence package per task | High; Ultra only for a narrow persistent recovery uncertainty |

## Smallest next task specification

**H0 — existing-evidence primary-target baseline**

- **Objective:** create a redacted, machine-readable and human-readable record
  of the owner-confirmed RLC-811A using only screenshots already supplied and
  verified offline project evidence.
- **Required inputs:** the existing private screenshots or their already
  verified fields, `docs/HARDWARE.md`, matching package hash and the current
  safety/evidence classifications. Do not request a new camera session.
- **Completion criteria:** model, exact hardware revision, installed firmware,
  source/evidence class and capture date/unknown status are explicit; UID,
  serial, MAC, IP, QR/account and credentials are absent from public output;
  a review confirms no live access occurred.
- **Recommended model and reasoning:** Medium. This is bounded evidence
  normalization and privacy review, not hardware interaction or reverse
  engineering.
- **When to switch:** High for H2 because it would be a specifically approved
  live-device action. Ultra is unnecessary unless a later, narrowly scoped
  recovery-architecture blocker persists after High reasoning.
- **Usage preparation:** this planning commit is the safe checkpoint before H0.
  H0 needs no expensive operation; checkpoint again before requesting H2
  approval or starting any live-device session.
