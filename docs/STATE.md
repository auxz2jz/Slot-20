# Project state and handoff

**Last milestone:** 2026-10-15 — Atomic task A1 recorded a bounded, reproducible inventory of the actual matching-package U-Boot section: exact identity, raw ARM format, linked-base/reset evidence, and relocation-tail geometry. No boot-flow analysis was repeated and no camera interacted with.

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
- Installed pinned `ubi-reader` 0.8.16 with `lzallright` 0.2.6 in an isolated WSL private venv; system `mtd-utils` is 2.2.0 and Python is 3.12.3. No system package was installed.
- Independently extracted rootfs/app on the native Linux filesystem. Geometry matches the custom parser: 2,048-byte minimum I/O, 131,072-byte PEB, 126,976-byte LEB, 197 rootfs data blocks and 124 app data blocks, with no unknown blocks.
- Independent path totals match exactly after excluding each extraction root: 760 rootfs paths and 275 app paths. Its 299/255 regular files exceed the custom parser's 291/253 hashes by exactly the recorded 8/2 incomplete reconstructions. A deterministic 32-file sample per volume matched all 64 SHA-256 values with no missing, mismatched or unsafe entries.
- Task R0 inspected the interrupted workspace before synchronization: `main` was clean at `fd9945c`, no stash existed, and the only identified new work was safely ignored/private. After fetching, the branch was fast-forwarded without reset or overwrite to `f3e7d21`, which adds the bounded atomic-task workflow.
- The interrupted session's bounded static analysis of the actual matching-package U-Boot was recovered. It identified a raw little-endian ARMv7 U-Boot 2019.04 image linked around `0x06000000`, reset target `0x06001000`, runtime region ending at `0x80000`, and 6,007 trailing `R_ARM_RELATIVE` records. Its normal traced path uses `nvt_boot`, reads an FDT from NAND offset `0x00040000`, loads Linux at `0x05800000`, optionally expands `BCL1` data to `0x01100000`, and invokes `bootm`. This is static package evidence, not a live boot result.
- The recovered command table has 61 entries, including NAND/UBI, MMC/FAT, TFTP/DHCP, `bootm`, `nvt_update_all`, and `upgrade`. The compiled environment backend is `nowhere` and exposes no persistent `saveenv`; `bootdelay=0` makes the compiled Ctrl+C path only an immediate-poll lead. No DFU/UMS/fastboot, serial-transfer command, bootcount/bootlimit policy, A/B rollback, or demonstrated rescue path was found.
- A recovered boot-time path associates GPIO 43 (`reset_key`) with a conditional erase at `0x03c00000..0x03efffff` and then attempts `upgrade all 0x1800000 0x4500000`; this ties the declared `download` area at `0x04500000` to a staged-update mechanism. Observed update checks include additive checksums, CRCs, legacy-uImage CRCs and post-write MD5, but neither authenticated image acceptance nor power-fail rollback is proved.
- R0 reverified the preserved private U-Boot artifact at 572,344 bytes, SHA-256 `f2d4fe401c28d5be792b6e559ffc7cc14627ad69ed0f873672fbeca2cda7dc6b`, and retained two bounded, read-only helpers under ignored `firmware_workspace/`. It did not rerun the bootloader investigation or execute recovered code.
- Atomic task A1 added the actual packaged U-Boot evidence table to `docs/BOOT_RECOVERY_ANALYSIS.md`. Focused checks reconfirmed the 572,344-byte hash, decoded the first ARM instruction at linked base `0x06000000` to reset target `0x06001000`, located the ARM/ARMv7 identity strings, and verified the `0x80000..0x8bbb7` tail as 6,007 monotonic eight-byte records whose `r_info` value is always ARM type 23 (`R_ARM_RELATIVE`). The raw image has no ELF section headers, so the `.rel.dyn` name remains a layout inference.
- Project-specific lightweight safety / checkpoint rules established; deliberately **no automatic import** of the entire master-instruction-library.
- This public repository holds **notes and independent code only**, never firmware update images or other proprietary material.

## Not done / uncertainties
- The native-Linux independent extraction and isolated analyzer environment are private local artifacts under `/home/firmware-analysis/slot20_private/`; they are not a public Git backup. Recreate them only if tool/input changes or deeper comparison is required.
- The 64-file cross-check is a deterministic sample, not a claim that every reconstructed byte or UBIFS journal state was independently validated. Neither parser replays the journal as a mounted kernel UBIFS would.
- The original proprietary firmware, extracted sections/manifests and raw prior report ZIP remain private/off-repository; sanitized findings are summarized under `docs/HARDWARE.md`.
- Vendor executable ABI / callbacks and AI formats are not yet mapped.
- Exact sensor, flash chip, physical RAM, UART recovery and live AI support unverified.
- BootROM/loader authentication, OTP/fuse state, actual UART pads/timing, Ethernet/TFTP/MMC readiness, NAND OOB/ECC/bad-block handling, GPIO 43's physical mapping, staged-update completeness/power-loss behavior, and recovery from a damaged loader/U-Boot remain unverified. Command presence is not proof that a recovery route works.
- A1 now normalizes the artifact/layout evidence and bounded reproduction commands. Command-surface, boot-flow, environment and recovery findings still need their separate A2–A5 evidence records. Preserve and reuse the existing artifact/helper output; do not repeat broad extraction or disassembly.
- No camera read-only query, live video test, backup, recovery or flashing performed.
- No independent camera replacement image or hardware-validated build exists.

## Next Codex task
1. **A2 only:** use the preserved command-table output and bounded string lookups to publish an actual-binary present/absent/uncertain table for boot, UART, network-recovery and flash operations. Include offsets or command-table references, and do not infer that a compiled command is usable on hardware.
2. After an A2 checkpoint, use the atomic plan for one task at a time; A3–A5 should validate and publish the already recovered boot-flow, environment and recovery leads without replaying the whole investigation.
3. Define and test a host-only signed bundle schema plus file-backed update/boot-state simulator only after the Phase-A evidence handoff is adequately normalized.
4. Keep all live-device work and `docs/INTERFACE_RE_PLAN.md` deferred until the maintenance and recovery gates are satisfied.

## Current reproducibility checkpoint

- `tools/unpack_reolink_offline.py`: SHA-256 `28f6db826841df5cdf983051f07a87b221ed01377b5ecdd590a5865a767e9392`
- `tools/extract_ubifs_readonly.py`: SHA-256 `d1085f0040826d650cb92e5ee52dd2a430a644ffdd41f32c324f027c82a87e77`
- `tests/test_extractors.py`: SHA-256 `c59bc399804424dbfc652971fbfcc0878468a42c8cb1aa4937090ee5a9ce5ee1`
- `tools/compare_manifest_sample.py`: SHA-256 `303ed20c29ce79cac54237fdaca984896f7b1d12ae05c4bc3fbff1b5212164ea`
- `tests/test_compare_manifest_sample.py`: SHA-256 `efef7f146d3a2f5524e76639ccd50fe67a340871fb87bc5e0fdd6e2af123f276`
- Private `rootfs.bin`: SHA-256 `57a4da9da4abc3ea1d65fa80653f3ab57879c962d8c39675f000f6c50476ae64`
- Private `app.bin`: SHA-256 `f1d3511609aa2d8642e05bfbff4fb02c192a4faa032bdd6de4f6fd44da043531`
- Private `uboot.bin`: 572,344 bytes; SHA-256 `f2d4fe401c28d5be792b6e559ffc7cc14627ad69ed0f873672fbeca2cda7dc6b`
- Tested here: A1 artifact hash/size, first-instruction/vector decode, identity-string offsets and relocation-region geometry; R0 Git/worktree reconciliation and private-work preservation; saved Linux manifest identity; independent UBI geometry/path totals/64-file sample; focused generic Novatek config evidence; synthetic parser/sampler behavior.
- Recovered but not yet normalized after A1: bounded command-table, boot-flow and update-path observations summarized above.
- Untested here: installed-camera byte identity, full all-file independent hash comparison, live Reolink U-Boot behavior, Linux build/boot, independent recovery and all hardware behavior.

## Recovery/checkpoint rule
Keep last successful commit; after two repeated failures with the same hypothesis, log a short blocker and change approach. Before any future hardware testing, independently validate a full-device backup and demonstrated recovery on matching hardware.

## Next-stage recommendation

- **Completed:** Task A1 published and verified the matching-package U-Boot identity, raw ARM layout, linked-base/reset evidence, and relocation geometry with bounded commands. No target code was executed and A2 work was not started.
- **Checkpoint:** the A1 documentation commit containing the evidence table, this state and the current handoff is pushed after focused checks. Private firmware, helpers, extracted trees and analyzer venv remain outside Git; no proprietary bytes are committed and no tracked WIP remains.
- **Next task:** **A2** — publish a bounded actual-binary table of boot, UART, network-recovery and flash commands/strings, classified as present, absent in the inspected table/region, or uncertain.
- **Recommended model and reasoning:** **High**.
- **Why:** A2 requires careful mapping of a stripped binary's command table and strings while avoiding false claims about hardware availability, but recovered output makes it a bounded verification task.
- **When to switch:** use Medium if A2 becomes documentation-only; consider Ultra only after a new checkpoint for one specific unresolved A3+ control-flow, BootROM-authentication, fuse, or independent-recovery question.
- **Usage preparation:** A1 is the required checkpoint before A2. Reliable telemetry at 2026-10-15 14:27 PDT showed 88% five-hour and 82% weekly usage remaining, but the user explicitly requested stopping after A1; recheck before any later expensive task.
