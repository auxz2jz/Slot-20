# Project state and handoff

**Last milestone:** 2026-10-14 — Preserved Linux extraction evidence, bounded manifest-comparison tooling, static boot/recovery analysis and the maintenance-firmware design were verified as an offline checkpoint. Mandatory usage-aware and next-stage recommendation rules are now in `AGENTS.md`. No camera interacted with; work remains offline.

## Goal
Completely independent firmware for Reolink RLC-811A `IPC_523128M8MP`, preserving camera hardware functionality. **Current overriding priority:** safe boot, authenticated web management, upgrade/downgrade workflow and proven recovery of the first installed image. Sensor/video and later zones/tripwires, tracking, and ALPR follow only after the maintenance baseline is established. The installed stock firmware remains operational throughout the research phase.

**Owner-facing release gate:** Before any flash, user expects a demonstrable management UI screenshot/local preview plus written evidence explaining the *next* firmware update, broken-boot recovery, and actual rollback target; no first install until these are reviewed and separately approved. See `docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`.

**2026-10-11 priority update:** The user explicitly requires every *permanently installed* custom firmware to retain browser-accessible management, firmware update capability, and a proven independent rescue/rollback method. Details and evidence gates: `docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`. No assumption is made that A/B partitions or restoring Reolink firmware are supported.

## Completed
- User confirmed hardware and current version from Reolink app.
- Matching `.pak` SHA-256 verified and static Device Tree / partition inventory documented.
- Offline extraction of rootfs and app identified 1,035 paths and CRC-validated 21,220 UBIFS records; 10 file reconstructions incomplete.
- Located vendor startup chain, streaming/recording services, focus/zoom candidates, and AI model/module references.
- Reverified the local matching package: 46,376,279 bytes; SHA-256 `f62a68d21397da9bb2aadefc66edfdbe91f35270b2cc64857a9082ed17e6a2e9`.
- Native Windows/Python 3.14 reproduced all six package sections, 760 rootfs paths, 275 app paths, 13,513 rootfs CRC-valid UBIFS nodes and 7,707 app nodes. Private outputs remain under ignored `firmware_workspace/`.
- Corrected UBI VID sequence-number selection to read the 64-bit field rather than its low 32 bits. The matching-package inventory was unchanged after the fix.
- Added six synthetic regression tests for package order/boundaries/trailing data, section output, 64-bit UBI sequence selection, path-name rejection and reconstruction size limits. `python -m unittest discover -s tests -v` passes on Python 3.14.8.
- Inspected two saved private Linux extraction runs dated 2026-10-12 and 2026-10-13. Their rootfs manifests are byte-identical (SHA-256 `1defc5037d3646d1cad424d81e35c058346f5abf1850bc8ce9057d63b372afd0`), as are their app manifests (`6013e12cd47641649c78cf9c07d55c6a2c6ea27c3f45b9e8296d3d230cd836ae`); both record the expected 8 rootfs and 2 app incomplete files. This session verified the saved artifacts and did not redundantly rerun extraction.
- Added a read-only deterministic manifest/tree sampling helper with bounded manifest and target reads, safe relative-path checks, no symlink traversal and path/content-free issue reports. Under the bundled Python 3.12.14, the complete suite runs 16 tests: 15 pass and the Windows symlink-creation case is skipped without the required privilege.
- Added `docs/BOOT_RECOVERY_ANALYSIS.md`, separating matching-package facts from generic Novatek source capabilities and unproven recovery candidates. Pinned Novatek source commits/configurations were checked from local Git objects.
- Added `docs/MINIMAL_MAINTENANCE_FIRMWARE.md`, defining the offline Ethernet/web management/signed-update/health/rollback architecture and test gates without claiming an installable image.
- Added mandatory usage-aware checkpoint/backup rules and concise next-stage model recommendations to `AGENTS.md`; instruction checkpoint `2a6abf4` is pushed.
- Project-specific lightweight safety / checkpoint rules established; deliberately **no automatic import** of the entire master-instruction-library.
- This public repository holds **notes and independent code only**, never firmware update images or other proprietary material.

## Not done / uncertainties
- Current WSL availability could not be enumerated from the restricted Windows session. The two saved Linux no-write manifests agree exactly, but their extracted file trees were intentionally not materialized; a manifest-to-independent-tree hash comparison therefore remains pending.
- The earlier `ubireader` attempt under Windows-mounted storage is incomplete and must not be treated as an independent validation. Repeat it in a private native Linux filesystem, record tool versions/geometry, and use the bounded sampler against the independent tree.
- The original proprietary firmware, extracted sections/manifests and raw prior report ZIP remain private/off-repository; sanitized findings are summarized under `docs/HARDWARE.md`.
- Vendor executable ABI / callbacks and AI formats are not yet mapped.
- Exact sensor, flash chip, physical RAM, UART recovery and live AI support unverified.
- No camera read-only query, live video test, backup, recovery or flashing performed.
- No independent camera replacement image or hardware-validated build exists.

## Next Codex task
1. In a private native Linux filesystem, complete the maintained `mtd-utils`/`ubireader` geometry and sampled path/hash comparison. Record exact tool versions and keep all extracted output ignored.
2. Follow recovery-first Roadmap Phase A: statically inspect the matching package's actual U-Boot image loading/validation, environment assumptions, command surface, factory rescue leads and full-backup requirements. Do not execute recovered ARM code or prioritize video/AI/lens analysis.
3. Define and test a host-only signed bundle schema plus file-backed update/boot-state simulator with bounded power-loss fault injection.
4. Audit the BSP build dependencies/binary objects, pin a lawful toolchain, then build the maintenance-only Linux prototype offline. A build is not a boot or recovery claim.
5. Keep `docs/INTERFACE_RE_PLAN.md` deferred until the maintenance and recovery gates are satisfied. Publish only sanitized findings and stop before any live-device work.

## Current reproducibility checkpoint

- `tools/unpack_reolink_offline.py`: SHA-256 `28f6db826841df5cdf983051f07a87b221ed01377b5ecdd590a5865a767e9392`
- `tools/extract_ubifs_readonly.py`: SHA-256 `d1085f0040826d650cb92e5ee52dd2a430a644ffdd41f32c324f027c82a87e77`
- `tests/test_extractors.py`: SHA-256 `c59bc399804424dbfc652971fbfcc0878468a42c8cb1aa4937090ee5a9ce5ee1`
- `tools/compare_manifest_sample.py`: SHA-256 `303ed20c29ce79cac54237fdaca984896f7b1d12ae05c4bc3fbff1b5212164ea`
- `tests/test_compare_manifest_sample.py`: SHA-256 `efef7f146d3a2f5524e76639ccd50fe67a340871fb87bc5e0fdd6e2af123f276`
- Tested here: saved Linux manifest identity, focused generic Novatek config evidence, synthetic parser/sampler behavior.
- Untested here: independent UBI tree comparison, actual Reolink U-Boot behavior, Linux build/boot, recovery and all hardware behavior.

## Recovery/checkpoint rule
Keep last successful commit; after two repeated failures with the same hypothesis, log a short blocker and change approach. Before any future hardware testing, independently validate a full-device backup and demonstrated recovery on matching hardware.

## Next-stage recommendation

- **Completed:** Linux manifest reproducibility evidence, bounded comparison tooling, static boot/recovery findings and the maintenance-firmware design are verified offline; tests pass with one platform privilege skip.
- **Checkpoint:** instruction commit `2a6abf4` is pushed; the verified code/document milestone is included in the commit containing this handoff. Private firmware/extraction/upstream artifacts remain ignored; no proprietary work is committed.
- **Next task:** complete the independent `mtd-utils`/`ubireader` geometry and sampled hash comparison in a private native Linux filesystem.
- **Recommended model and reasoning:** **High**.
- **Why:** this is firmware extraction/tooling work with filesystem-geometry and parser discrepancy risk, but it is bounded and does not yet require speculative recovery architecture.
- **When to switch:** return to Medium for routine documentation/test maintenance; switch to Ultra before deep matching-binary Novatek bootloader/recovery analysis if the independent comparison is complete and hardware-specific uncertainty becomes the main problem.
- **Usage preparation:** commit and push this sanitized checkpoint before creating another private extracted tree or beginning deeper bootloader work.
