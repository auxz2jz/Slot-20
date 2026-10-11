# Project state and handoff

**Last milestone:** 2026-10-11 — Repository initialized for Codex/ChatGPT collaboration. No firmware source compiled. No camera interacted with. Work remains offline.

## Goal
Completely independent firmware for Reolink RLC-811A `IPC_523128M8MP`, preserving camera hardware functionality. **Current overriding priority:** safe boot, authenticated web management, upgrade/downgrade workflow and proven recovery of the first installed image. Sensor/video and later zones/tripwires, tracking, and ALPR follow only after the maintenance baseline is established. The installed stock firmware remains operational throughout the research phase.

**Owner-facing release gate:** Before any flash, user expects a demonstrable management UI screenshot/local preview plus written evidence explaining the *next* firmware update, broken-boot recovery, and actual rollback target; no first install until these are reviewed and separately approved. See `docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`.

**2026-10-11 priority update:** The user explicitly requires every *permanently installed* custom firmware to retain browser-accessible management, firmware update capability, and a proven independent rescue/rollback method. Details and evidence gates: `docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`. No assumption is made that A/B partitions or restoring Reolink firmware are supported.

## Completed
- User confirmed hardware and current version from Reolink app.
- Matching `.pak` SHA-256 verified and static Device Tree / partition inventory documented.
- Offline extraction of rootfs and app identified 1,035 paths and CRC-validated 21,220 UBIFS records; 10 file reconstructions incomplete.
- Located vendor startup chain, streaming/recording services, focus/zoom candidates, and AI model/module references.
- Project-specific lightweight safety / checkpoint rules established; deliberately **no automatic import** of the entire master-instruction-library.
- This public repository holds **notes and independent code only**, never firmware update images or other proprietary material.

## Not done / uncertainties
- The two original offline Python extraction scripts are now versioned under `tools/` and ready for Codex to inspect. The original proprietary firmware and raw prior report ZIP remain private/off-repository; the sanitized findings are summarized under `docs/HARDWARE.md`.
- Vendor executable ABI / callbacks and AI formats are not yet mapped.
- Exact sensor, flash chip, physical RAM, UART recovery and live AI support unverified.
- No camera read-only query, live video test, backup, recovery or flashing performed.
- No independent camera replacement image or hardware-validated build exists.

## Next Codex task
1. Clone this repository; read `AGENTS.md` and `docs/HARDWARE.md`.
2. Obtain the original `.pak` privately from the user; do **not** commit the proprietary binary. The previous toolkit ZIP/report is optional reference.
3. Use the already-committed scripts in `tools/`; verify they run read-only (prefer WSL2/Linux for `liblzo2.so.2`), then build focused tests.
4. Reproduce the 1,035-path filesystem inventory and compare against the existing report.
5. Focus first on the bootloader's image loading/checking, flash layout, factory rescue possibilities, and feasibility of a management-enabled first custom image; do not prioritize AI/video yet.
6. Produce an offline design for Ethernet + web UI + verified firmware updater and a *separate* independent rescue/recovery gate. Do not assert support without actual evidence.
7. Report current findings and stop; **no access to the actual camera**.

## Recovery/checkpoint rule
Keep last successful commit; after two repeated failures with the same hypothesis, log a short blocker and change approach. Before any future hardware testing, independently validate a full-device backup and demonstrated recovery on matching hardware.
