# Project state and handoff

**Last milestone:** 2026-10-11 — Matching package rechecked with the committed offline tools; parser tests and one correctness fix added; next static interface stage planned. No camera interacted with. Work remains offline.

## Goal
Completely independent firmware for Reolink RLC-811A `IPC_523128M8MP`, preserving camera hardware functionality. Prioritize zones/tripwires, tracking and ALPR with external PC CodeProject.AI engine initially. The installed stock firmware remains operational throughout the research phase.

## Completed
- User confirmed hardware and current version from Reolink app.
- Matching `.pak` SHA-256 verified and static Device Tree / partition inventory documented.
- Offline extraction of rootfs and app identified 1,035 paths and CRC-validated 21,220 UBIFS records; 10 file reconstructions incomplete.
- Located vendor startup chain, streaming/recording services, focus/zoom candidates, and AI model/module references.
- Reverified the local matching package: 46,376,279 bytes; SHA-256 `f62a68d21397da9bb2aadefc66edfdbe91f35270b2cc64857a9082ed17e6a2e9`.
- Native Windows/Python 3.14 reproduced all six package sections, 760 rootfs paths, 275 app paths, 13,513 rootfs CRC-valid UBIFS nodes and 7,707 app nodes. Private outputs remain under ignored `firmware_workspace/`.
- Corrected UBI VID sequence-number selection to read the 64-bit field rather than its low 32 bits. The matching-package inventory was unchanged after the fix.
- Added six synthetic regression tests for package order/boundaries/trailing data, section output, 64-bit UBI sequence selection, path-name rejection and reconstruction size limits. `python -m unittest discover -s tests -v` passes on Python 3.14.8.
- Project-specific lightweight safety / checkpoint rules established; deliberately **no automatic import** of the entire master-instruction-library.
- This public repository holds **notes and independent code only**, never firmware update images or other proprietary material.

## Not done / uncertainties
- Complete LZO reconstruction was not reproduced on this host: WSL2 has no Linux distribution and the installed Docker client has no running Linux engine. The Windows run reports 279 rootfs and 190 app files blocked by missing `liblzo2.so.2`, plus two directly observed rootfs missing-block failures. The earlier Linux result of 8 rootfs and 2 app incomplete files remains the expected baseline but needs a fresh Linux rerun.
- The original proprietary firmware, extracted sections/manifests and raw prior report ZIP remain private/off-repository; sanitized findings are summarized under `docs/HARDWARE.md`.
- Vendor executable ABI / callbacks and AI formats are not yet mapped.
- Exact sensor, flash chip, physical RAM, UART recovery and live AI support unverified.
- No camera read-only query, live video test, backup, recovery or flashing performed.
- No independent camera replacement image or hardware-validated build exists.

## Next Codex task
1. In Linux with `liblzo2.so.2`, rerun the matching package without `--write-files`; confirm the structural totals and prior 8-rootfs/2-app incomplete-file result.
2. Cross-check UBI geometry and a sampled path/hash set with maintained `mtd-utils`/`ubireader`. Keep all outputs private and ignored.
3. Follow `docs/INTERFACE_RE_PLAN.md` Stage B1: reconstruct privately, then record startup/module/process order and per-binary ELF/module metadata for the video, streaming, AI and lens candidates.
4. Publish only a sanitized dependency/interface matrix and update this handoff. Stop before deep decompilation or any live-device work.

## Current reproducibility checkpoint

- `tools/unpack_reolink_offline.py`: SHA-256 `28f6db826841df5cdf983051f07a87b221ed01377b5ecdd590a5865a767e9392`
- `tools/extract_ubifs_readonly.py`: SHA-256 `d1085f0040826d650cb92e5ee52dd2a430a644ffdd41f32c324f027c82a87e77`
- `tests/test_extractors.py`: SHA-256 `c59bc399804424dbfc652971fbfcc0878468a42c8cb1aa4937090ee5a9ce5ee1`
- Untested here: successful LZO decompression, independent UBI tooling comparison, ARM ELF/ABI analysis, and all hardware behavior.

## Recovery/checkpoint rule
Keep last successful commit; after two repeated failures with the same hypothesis, log a short blocker and change approach. Before any future hardware testing, independently validate a full-device backup and demonstrated recovery on matching hardware.
