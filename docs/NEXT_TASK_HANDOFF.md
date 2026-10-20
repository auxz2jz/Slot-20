# Slot-20 — Current task handoff

**Status:** HARDWARE DEVELOPMENT PLAN UPDATED — the owner's existing,
screenshot-confirmed RLC-811A `IPC_523128M8MP` is the primary in-service
development reference. No live camera action occurred.

**LAST TASK ID / STATUS:** Hardware-development planning update — **COMPLETE;
DOCUMENTATION AND ARCHITECTURE PLAN ONLY**.

**COMPLETED AND VERIFIED:**

- The primary reference identity remains `RLC-811A / IPC_523128M8MP`, with
  installed firmware `v3.1.0.1643_2402219117` previously confirmed through
  owner-provided screenshots.
- Because this camera remains in active security service, it is not a
  sacrificial recovery surrogate and must retain its working stock firmware.
- D2a research remains intact. D2a-1 seller evidence collection is **on hold**;
  no seller contact or purchase is authorized.
- `docs/HARDWARE_DEVELOPMENT_PLAN.md` defines three lanes: bounded primary-unit
  observations, modular software architecture, and separate matching-spare
  recovery proof. Its H0–H6 stages begin offline and require a fresh,
  action-specific approval before any live observation.
- The plan identifies portable security/update/management/build/evidence
  functions and isolates exact SoC, DTS, bootloader, NAND/OOB/ECC, network,
  sensor/ISP, drivers, calibration and recovery behavior behind strict hardware
  profiles and narrow adapters. No refactor was performed.
- `docs/ROADMAP.md`, `docs/HARDWARE.md`, `docs/ATOMIC_TASK_PLAN.md` and
  `docs/STATE.md` reflect the new target role and small-task sequence.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; starting checkpoint `f8673f3` was
clean. The planning-completion commit containing this handoff must match
`origin/main` after push.

**LOCAL UNTRACKED OR PRIVATE WORK:** Preserve every existing private firmware,
analysis, compiler, kernel and rootfs artifact under
`/home/firmware-analysis/slot20_private/` and the previously supplied camera
screenshots in their protected location. Do not commit device identifiers or
screenshots without redaction review.

**NEXT SINGLE TASK ID + INPUT:** **H0 — existing-evidence primary-target
baseline only.** Inputs are the previously supplied screenshots or their
already verified fields, `docs/HARDWARE.md`, the matching package hash and the
evidence classifications in `docs/HARDWARE_DEVELOPMENT_PLAN.md`. Do not request
or perform a new camera session.

**PASS CRITERION FOR NEXT TASK:** Produce a concise public human-readable record
and machine-readable manifest stating model, exact hardware revision, installed
firmware, evidence source/class and capture-date/unknown status. UID, serial,
MAC, IP, QR/account data and credentials must be absent. Processor, NAND, RAM,
PCB, sensor and driver facts must remain static leads or unknown unless the
existing evidence proves them. Verify no live access occurred.

**RECOMMENDED REASONING + WHY:** **Medium.** H0 is bounded evidence
normalization, provenance classification and privacy review; it requires no
hardware interaction, build or reverse engineering.

**WHEN TO SWITCH:** High is appropriate for H2's first separately approved
live-device observation and for M1/M2 profile/adapter implementation. Use Ultra
only for one narrowly scoped persistent BootROM or recovery-architecture
uncertainty after a safe checkpoint and explicit selection.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** Reliable closeout telemetry
on 2026-10-19 showed 50% of the five-hour window used (50% remaining) and 56%
of the weekly window used (44% remaining). This is a point-in-time snapshot,
not continuous monitoring.

**USAGE PREPARATION:** This planning commit is the safe checkpoint before H0.
H0 requires no expensive operation. Checkpoint again before requesting H2
approval or any live-device session.

**CONTINUE OR STOP + REASON:** STOP after this planning task. H0 is the next
atomic task. H1 planning and every H2/live, seller, purchase or physical action
remain separate future tasks.

**CAMERA CONTACT/FLASH:** NONE. No discovery, scan, authentication, query,
network contact, power change, reboot, reset, configuration, actuation, opening,
UART, NAND read/write, firmware assembly or flash was performed or authorized.
