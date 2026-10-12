# Codex project instructions — lightweight firmware rules

Scope: **Reolink RLC-811A hardware IPC_523128M8MP**, independently developed camera firmware and an optional local-PC AI companion. See README, `docs/HARDWARE.md`, `docs/STATE.md`, `docs/ROADMAP.md`.

This project deliberately **does NOT automatically inherit** the Master Instruction Library or its complete diagnostics/guided-test frameworks.

## Non-negotiable safety
1. Default to **offline, read-only** reverse engineering. The actual camera is a production device.
2. Do not discover, scan, connect to, authenticate with, reset, reconfigure, reboot, update, or move motors on a camera without user approval for that specific live-device action. Never infer consent from a stored IP address.
3. Do not propose or execute firmware flashing until a device-specific **full flash backup is acquired, verified**, and a **matching-hardware recovery method is demonstrated**, preferably on a sacrificial spare. Require fresh, explicit approval even after those gates.
4. Do not alter the factory bootloader or device-specific calibration/identity partitions without a validated independent recovery pathway.
5. Keep hardware revisions strictly separate; no cross-flashing. Treat firmware-device-tree claims as leads rather than proven component identities.
6. Vendor firmware binaries, reconstructed proprietary libraries, private keys, recordings, personal camera identifiers and full flash dumps stay out of this public repository. Never print or commit secrets. Extract vendor firmware only to an ignored local/private workspace.
7. Firmware parsing is untrusted-data processing: cap decompression sizes, avoid shell interpolation, never execute recovered ARM binaries on the workstation. Static analysis first.

## Lean working procedure
- **Before changing code:** inspect `docs/STATE.md`, current branch, and the last passing baseline. State the narrow task and acceptance criteria.
- **Small, reversible increments:** commit/record a checkpoint when a meaningful stage passes. Keep scripts reproducible and preserve the last known-good version.
- **Do not loop:** after 2 attempts with substantially the same failure, stop repeating the same solution; record evidence and change hypothesis or ask for help.
- **Useful tests only:** unit tests for parsers, checksums, file boundaries and offline software; boot logs and crash diagnostics once a safely testable board exists. No bloated always-on logging framework.
- **No fabricated successes:** clearly distinguish source inspection, emulated validation, live hardware tests and unverified hypotheses.
- **Keep handoffs concise:** update `docs/STATE.md` with latest findings, exact next step, blocker, relevant hashes, and tested/untested status.
- **Cost discipline:** avoid redundant scans, logs and massive output. Prefer focused tools, sampled inspection and existing artifacts; preserve enough evidence to reproduce findings.

## Hard installation gate (user requirement)
**Read `docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md` before any firmware-image design or update work.** The **first permanently installed firmware** must include Ethernet connectivity, a secure browser-accessible management interface, a verified updater for supported new/previous versions, plus a demonstrated rescue/rollback path independent of the experimental Linux/web server. A firmware that merely boots is not eligible for persistent installation. Do not confuse the presence of an upload form with actual brick protection. No promises of dual-boot/stock restoration without proven hardware support. **No installation approval may be requested until a concrete pre-install review with the user includes actual UI screenshots or a labeled mockup, demonstrated subsequent-version updating on a matching spare, exact independent recovery/rollback steps, and remaining risks; see the owner-review section of that document.**

## Development priorities
1. Reproduce the offline firmware extraction and inspect bootloader/flash/image validation without accessing the camera.
2. Analyze how to obtain a full backup, preserve factory data, and restore independently of the experimental operating system.
3. Design and test offline a minimal bootable Linux system with Ethernet, authenticated web management, compatible-image validation, firmware upload/update, and rollback state machine.
4. Establish and physically demonstrate recovery, updates, and bad-boot rollback **on matching spare hardware**, after explicit approval.
5. Only once the installed-baseline and recovery gates are demonstrated, investigate video/sensor/ISP/zoom and later zones/ALPR.
