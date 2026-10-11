# Mandatory first-install requirements: management, updates, and recovery

**Status: DESIGN REQUIREMENTS ONLY.** No booted image, tested updater, full-flash backup, or recovery mechanism exists yet for the RLC-811A IPC_523128M8MP. This document authorizes no camera access or flashing.

## Fundamental rule

A minimal Linux image that boots but provides no reliable management, firmware replacement, or recovery path is **NOT ACCEPTABLE FOR PERMANENT INSTALLATION**. Offline builds and temporary RAM-only boot experiments may be useful *after* safe test-hardware recovery is established, but they must not overwrite factory firmware.

A working web server alone is not enough: broken kernels, flash partitions, network initialization, or update interruptions can prevent the server from running. A tested path to recover **independently of the experimental main operating system** is mandatory.

## User-facing maintenance baseline (first *permanently installed* image)

- Ethernet comes up predictably, with documented IP discovery/fallback; camera advertises a verifiable identity/version.
- Browser-accessible local web management interface (simple HTML is fine), secured with authentication, with a clearly visible firmware/version/hardware profile.
- Upload newer or previous **supported** custom firmware from a local computer; cryptographically verify authenticity/integrity and board compatibility before writing; refuse mismatched board versions, corrupt/incomplete payloads and unsafe downgrades.
- Report upload, validation, installation, reboot, boot-health confirmation, and rollback status honestly. Protect against interrupted/power-failed uploads and writes.
- Optional SSH/rescue CLI for authorized maintenance; disable insecure defaults, use unique credentials.
- Logging limited to updater/boot status and actionable failure reports. Do not add general Android diagnostics infrastructure.
- Never enable remote/cloud automatic updating by default.

## Recovery / rollback safety (mandatory before any permanent install)

1. Analyze board-specific boot process and current partitions. Preserve existing bootloader and factory calibration/identity/keys; don't assume the 59 MiB `download` partition can be repurposed.
2. Obtain **and verify** a full, device-specific flash backup, including device-specific data and NAND bad-block/ECC considerations, via an approved method. Manufacturer `.pak` upgrade file does **not** replace this backup.
3. Establish a **documented, demonstrated independent rescue path** on matching sacrificial hardware. Possible designs include a preserved factory rescue mechanism, verified secondary recovery system, tested bootloader network recovery, or hardware programmer. A factory reset button is NOT presumed to repair unbootable firmware.
4. Evaluate A/B dual-bank updates or factory-slot retention, but do not promise either without proving capacity, image format, boot selection, health marking, and independent recovery on this exact revision. If flash capacity is inadequate, use a verified external recovery strategy, not invented partitions.
5. When a second OS slot is feasible, only mark new firmware healthy once the network and management/update services are reachable. Failed or unconfirmed boots must deterministically revert to a previously verified bootable slot.
6. Validate interrupted upload, interrupted update, bad image, mismatched hardware version, failed first boot, loss of networking, and restoration of the original system (if technically possible), on **matching spare hardware**. An existing vendor `.pak` being available does not prove it can be restored using a custom loader.
7. Hardware test and installation require separate, explicit user consent for each intrusive step. Never test unverified flashing on the working production camera.

## Priority order

1. Offline study of bootloader, U-Boot environment, image validation/signing, flash geometry and independent rescue routes.
2. Choose recovery design and verify feasibility with actual target constraints.
3. Implement/test offline web maintenance UI, local upload API, board/image validation and update state machine; simulate hard failures/power loss.
4. Build minimal independent Linux with predictable Ethernet and management services. No need for video/AI yet.
5. Backup/recovery and boot/rollback demonstrations **on matching spare hardware**.
6. Only after all gates are satisfied, consider first persistent install with explicit approval.
7. Add video/recording, lens/peripheral features, then zones/ALPR.

## Proof checklist for the release gate

- [ ] Image boots on matching test hardware and web interface is reachable over Ethernet
- [ ] Authenticated upload of a compatible new custom image succeeds
- [ ] Invalid/mismatched/truncated images are rejected **before writing**
- [ ] A previously working image can be restored after a bad update
- [ ] Recovery remains available when Linux/web/network do not start
- [ ] A complete per-device flash backup is verified, with restore demonstrated
- [ ] Bootloader/rescue/calibration and unique identity preserved
- [ ] Original Reolink fallback or independent restoration path verified (or documented as unavailable; no false fallback claims)
- [ ] Production camera remained untouched; any future install requires fresh user approval

Do not label an item complete based on static analysis, emulation, or a build succeeding. Separate each evidence class.
