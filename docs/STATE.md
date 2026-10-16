# Project state and handoff

**Last milestone:** 2026-10-16 — Atomic task A5 evaluated UART, U-Boot TFTP/Ethernet, MMC/FAT, SoC Boot ROM, external SPI-NAND programming, the existing reset/staged-update path, and proposed protected rescue/A-B designs. Every route remains unverified; the report now states each independence boundary, missing evidence, risk, required matching-spare equipment and minimum future proof. No camera interacted with.

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
- The interrupted session's bounded static analysis of the actual matching-package U-Boot was recovered. It identified a raw little-endian ARMv7 U-Boot 2019.04 image linked around `0x06000000`, reset target `0x06001000`, runtime region ending at `0x80000`, and 6,007 trailing `R_ARM_RELATIVE` records. Its boot path uses `nvt_boot`, loads Linux at `0x05800000`, optionally uses `0x01100000` while handling `BCL1` data, and invokes `bootm`. A3 later corrected the earlier FDT characterization: the one direct initializer call uses a loader-supplied memory pointer; the `0x00040000` NAND reader is compiled but not proved to be the normal path.
- The recovered command table has 61 entries, including NAND/UBI, MMC/FAT, TFTP/DHCP, `bootm`, `nvt_update_all`, and `upgrade`. The compiled environment backend is `nowhere` and exposes no persistent `saveenv`; `bootdelay=0` makes the compiled Ctrl+C path only an immediate-poll lead. No DFU/UMS/fastboot, serial-transfer command, bootcount/bootlimit policy, A/B rollback, or demonstrated rescue path was found.
- A recovered boot-time path associates GPIO 43 (`reset_key`) with a conditional erase at `0x03c00000..0x03efffff` and then attempts `upgrade all 0x1800000 0x4500000`; this ties the declared `download` area at `0x04500000` to a staged-update mechanism. Observed update checks include additive checksums, CRCs, legacy-uImage CRCs and post-write MD5, but neither authenticated image acceptance nor power-fail rollback is proved.
- R0 reverified the preserved private U-Boot artifact at 572,344 bytes, SHA-256 `f2d4fe401c28d5be792b6e559ffc7cc14627ad69ed0f873672fbeca2cda7dc6b`, and retained two bounded, read-only helpers under ignored `firmware_workspace/`. It did not rerun the bootloader investigation or execute recovered code.
- Atomic task A1 added the actual packaged U-Boot evidence table to `docs/BOOT_RECOVERY_ANALYSIS.md`. Focused checks reconfirmed the 572,344-byte hash, decoded the first ARM instruction at linked base `0x06000000` to reset target `0x06001000`, located the ARM/ARMv7 identity strings, and verified the `0x80000..0x8bbb7` tail as 6,007 monotonic eight-byte records whose `r_info` value is always ARM type 23 (`R_ARM_RELATIVE`). The raw image has no ELF section headers, so the `.rel.dyn` name remains a layout inference.
- Atomic task A2 verified a 61-entry, 28-byte command-table run at file offsets `0x7f5ac..0x7fc57`. The actual package binary registers normal/NAND boot, UART-disable, BOOTP/DHCP/TFTP/ping, NAND/MTD/UBI/UBIFS, MMC/FAT, checksum and two update command paths. It does not register USB/DFU/UMS/fastboot, serial-transfer or `saveenv` commands. Exact bounded string searches found compiled console/default-boot clues but no named bootcount/bootlimit/alternate-boot/rollback/rescue tokens. These are static command/string facts, not proof of working hardware or independent recovery.
- Atomic task A3 traced the registered `nvt_boot` handler at `0x0600d600`. The named-partition branch issues a `0x40`-byte probe and derived-length reload of `linux` at `0x05800000`, calls the bounded packaged-kernel transform, extends `bootargs`, sets the `bootm` memory limits, and dispatches `bootm 5800000 - <prepared-fdt>`. The prepared FDT comes through globals `0x060802bc`/`0x060802c8`; the only direct call to its initializer passes memory-source mode. The compiled raw-NAND FDT branch at offsets `0x00040000`/`0x00060000`, an alternate Linux loader, original FDT-pointer provenance and live success remain unverified.
- Atomic task A4 verified that the actual U-Boot environment linker list has only the `nowhere` driver with null load/save slots and a defaults-only initializer. The 391-byte default blob supplies the UBIFS bootargs, `nvt_boot`, zero delay and 115200 baud; early boot then derives volatile `mtdids`, `mtdparts` and `ubi.mtd=6 ro` from the package FDT before A3's runtime arguments. The FDT declares `uenv` at `0x00240000`, but current U-Boot does not use it for persistence. The generic optional NAND environment range `0x002c0000..0x002fffff` would overlap the matching FDT's kernel partition and must never be copied to this target.
- Atomic task A5 added the independent-recovery evidence matrix. Preserved U-Boot plus UART/TFTP or MMC/FAT are plausible Linux-independent leads but remain U-Boot-dependent and physically unverified. Boot ROM and external raw NAND access could reach below U-Boot but have the largest protocol/electrical/raw-geometry gaps. The GPIO 43/`download` staged-update path is not proven atomic or restorative, and no protected rescue/A-B design or automatic rollback currently exists. No candidate satisfies the recovery gate.
- Project-specific lightweight safety / checkpoint rules established; deliberately **no automatic import** of the entire master-instruction-library.
- This public repository holds **notes and independent code only**, never firmware update images or other proprietary material.

## Not done / uncertainties
- The native-Linux independent extraction and isolated analyzer environment are private local artifacts under `/home/firmware-analysis/slot20_private/`; they are not a public Git backup. Recreate them only if tool/input changes or deeper comparison is required.
- The 64-file cross-check is a deterministic sample, not a claim that every reconstructed byte or UBIFS journal state was independently validated. Neither parser replays the journal as a mounted kernel UBIFS would.
- The original proprietary firmware, extracted sections/manifests and raw prior report ZIP remain private/off-repository; sanitized findings are summarized under `docs/HARDWARE.md`.
- Vendor executable ABI / callbacks and AI formats are not yet mapped.
- Exact sensor, flash chip, physical RAM, UART recovery and live AI support unverified.
- BootROM/loader authentication, OTP/fuse state, actual UART pads/timing, Ethernet/TFTP/MMC readiness, NAND OOB/ECC/bad-block handling, GPIO 43's physical mapping, staged-update completeness/power-loss behavior, and recovery from a damaged loader/U-Boot remain unverified. Command presence is not proof that a recovery route works.
- A1–A5 now normalize artifact/layout, command/string, normal-boot, environment/partition ownership and independent-recovery candidate evidence. Preserve and reuse the existing artifact/helper output; do not repeat broad extraction or disassembly.
- No camera read-only query, live video test, backup, recovery or flashing performed.
- No independent camera replacement image or hardware-validated build exists.

## Next Codex task
1. **B1 only:** define a host-only compatible signed update-bundle format with board ID, version/downgrade policy, bounded component metadata, cryptographic hashes/signature, and explicit security assumptions. Do not write flash or target the camera.
2. Keep the bundle schema independent of unresolved physical recovery choices; A5 does not authorize persistent installation or repurposing `download`/unknown partitions.
3. Defer B2 implementation/negative tests until B1 is reviewed and checkpointed.
4. Keep all live-device work and `docs/INTERFACE_RE_PLAN.md` deferred until the maintenance and recovery gates are satisfied.

## Current reproducibility checkpoint

- `tools/unpack_reolink_offline.py`: SHA-256 `28f6db826841df5cdf983051f07a87b221ed01377b5ecdd590a5865a767e9392`
- `tools/extract_ubifs_readonly.py`: SHA-256 `d1085f0040826d650cb92e5ee52dd2a430a644ffdd41f32c324f027c82a87e77`
- `tests/test_extractors.py`: SHA-256 `c59bc399804424dbfc652971fbfcc0878468a42c8cb1aa4937090ee5a9ce5ee1`
- `tools/compare_manifest_sample.py`: SHA-256 `303ed20c29ce79cac54237fdaca984896f7b1d12ae05c4bc3fbff1b5212164ea`
- `tests/test_compare_manifest_sample.py`: SHA-256 `efef7f146d3a2f5524e76639ccd50fe67a340871fb87bc5e0fdd6e2af123f276`
- Private `rootfs.bin`: SHA-256 `57a4da9da4abc3ea1d65fa80653f3ab57879c962d8c39675f000f6c50476ae64`
- Private `app.bin`: SHA-256 `f1d3511609aa2d8642e05bfbff4fb02c192a4faa032bdd6de4f6fd44da043531`
- Private `fdt.bin`: 17,399 bytes; SHA-256 `62a2b0f96262702f7ec97c6df2423a4abc8ed47e881db1248ceab66e763c9a8c`
- Private `uboot.bin`: 572,344 bytes; SHA-256 `f2d4fe401c28d5be792b6e559ffc7cc14627ad69ed0f873672fbeca2cda7dc6b`
- Tested here: A5 matrix cross-references against the bounded A2 command/string offsets, A3 boot dependencies, A4 environment/partition ownership, pinned generic-source limits and the recovery-gate checklist; A4 environment/partition evidence; A3 boot-flow ranges; A2 command-table/string evidence; A1 artifact/layout evidence; R0 recovery; extraction cross-checks; synthetic parser/sampler behavior.
- Recovered static boot/update/recovery observations are normalized through A5; no hardware route was exercised.
- Untested here: installed-camera byte identity, full all-file independent hash comparison, live Reolink U-Boot behavior, Linux build/boot, independent recovery and all hardware behavior.

## Recovery/checkpoint rule
Keep last successful commit; after two repeated failures with the same hypothesis, log a short blocker and change approach. Before any future hardware testing, independently validate a full-device backup and demonstrated recovery on matching hardware.

## Next-stage recommendation

- **Completed:** Task A5 published and cross-checked a seven-route recovery matrix covering UART, TFTP/Ethernet, MMC/FAT, Boot ROM, external SPI-NAND programming, the existing staged-update/reset path, and protected rescue/A-B options. It states the evidence class, independence boundary, unknowns, risks, equipment and minimum matching-spare verification for each. No route is claimed proven; no target code ran and no camera was accessed.
- **Checkpoint:** the A5 documentation commit containing the report, this state and the current handoff is pushed after focused verification. Private firmware, FDT, helpers, extracted trees and analyzer/upstream environments remain outside Git; no proprietary bytes are included and no other tracked WIP remains.
- **Next task:** **B1** — define the host-only signed update-bundle schema and security assumptions; do not implement B2 or bind the schema to unresolved camera flash regions.
- **Recommended model and reasoning:** **Medium**.
- **Why:** B1 is a bounded data-format and threat-model design task using established cryptographic primitives; it needs careful compatibility and downgrade-policy reasoning but no new binary reverse engineering or build.
- **When to switch:** use High for B2 cryptographic verification implementation, adversarial negative tests or a substantive schema ambiguity. Ultra is not indicated unless a later narrowly scoped recovery/security uncertainty remains intractable at High.
- **Usage preparation:** A5 must be committed and pushed before B1. Reliable telemetry at 2026-10-16 02:52 PDT showed 96% five-hour and 68% weekly usage remaining. This is a snapshot, not continuous monitoring; the requested A5 stop is the checkpoint before any new task.
