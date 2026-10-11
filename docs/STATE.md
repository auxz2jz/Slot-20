# Project state and handoff

**Last milestone:** 2026-10-11 — Repository initialized for Codex/ChatGPT collaboration. No firmware source compiled. No camera interacted with. Work remains offline.

## Goal
Completely independent firmware for Reolink RLC-811A `IPC_523128M8MP`, preserving camera hardware functionality. Prioritize zones/tripwires, tracking and ALPR with external PC CodeProject.AI engine initially. The installed stock firmware remains operational throughout the research phase.

## Completed
- User confirmed hardware and current version from Reolink app.
- Matching `.pak` SHA-256 verified and static Device Tree / partition inventory documented.
- Offline extraction of rootfs and app identified 1,035 paths and CRC-validated 21,220 UBIFS records; 10 file reconstructions incomplete.
- Located vendor startup chain, streaming/recording services, focus/zoom candidates, and AI model/module references.
- Project-specific lightweight safety / checkpoint rules established; deliberately **no automatic import** of the entire master-instruction-library.
- This public repository holds **notes and independent code only**, never firmware update images or other proprietary material.

## Not done / uncertainties
- Original offline scripts and full report exist as ChatGPT-generated toolkit files, but **they must still be copied into the Codex working tree**; verify file checksums/behavior before considering a fresh reimplementation equivalent.
- Vendor executable ABI / callbacks and AI formats are not yet mapped.
- Exact sensor, flash chip, physical RAM, UART recovery and live AI support unverified.
- No camera read-only query, live video test, backup, recovery or flashing performed.
- No independent camera replacement image or hardware-validated build exists.

## Next Codex task
1. Clone this repository; read `AGENTS.md` and `docs/HARDWARE.md`.
2. Privately obtain the original `.pak` and the `RLC811A_Offline_Reverse_Engineering_Toolkit.zip` from the user (do **not** commit proprietary binaries).
3. Import the toolkit's Python scripts into `tools/` and sanitize documentation before commit; verify read-only usage with `--help` or static inspection.
4. Reproduce the 1,035-path filesystem inventory and compare against the existing report.
5. Create a compact ABI/interface investigation plan for sensor/ISP/encoder, lens, AI/zones and RTSP service.
6. Report current findings and stop; **no access to the actual camera**.

## Recovery/checkpoint rule
Keep last successful commit; after two repeated failures with the same hypothesis, log a short blocker and change approach. Before any future hardware testing, independently validate a full-device backup and demonstrated recovery on matching hardware.
