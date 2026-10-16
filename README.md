# Slot-20 — Reolink RLC-811A Custom Firmware

**Status:** Offline reverse engineering only. **No camera flashing or configuration changes are authorized.**

## Goal

Build an independent Linux-based firmware for the Reolink RLC-811A, retaining functional video capture/encoding, networking, RTSP/ONVIF, recording, motorized 5× zoom/autofocus, audio, IR/spotlight and other supported hardware. **First-install requirement:** Ethernet, secure browser-accessible maintenance interface, compatible new/previous firmware upload, and a *verified independent recovery/rollback method* before persistent installation. A Linux image that only boots is not sufficient. Future enhancements include user-drawn detection polygons, object tracking, and AI license-plate recognition (ALPR), potentially using a separate PC with CodeProject.AI or alternatives.

## Confirmed target

- **Camera:** Reolink RLC-811A
- **Hardware:** `IPC_523128M8MP` (**not** `IPC_560B158MP`)
- **Installed firmware:** `v3.1.0.1643_2402219117`
- **Matching reference package:** `IPC_523128M8MP.1643_2402219117.RLC-811A.IMX415.8MP.AF.REOLINK.pak`
- **Reference SHA-256:** `f62a68d21397da9bb2aadefc66edfdbe91f35270b2cc64857a9082ed17e6a2e9`
- **Firmware Device Tree:** Novatek NA51055; Linux 4.19.91; 112 MiB Linux-visible memory and a 128 MiB NAND partition map (declared values, not live measurements).

Read `AGENTS.md` first, then `docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`, `docs/HARDWARE.md` and `docs/STATE.md` before modifying the project.

## Safety boundary

This repository is **public**. Never commit original proprietary firmware blobs, reconstructed vendor binaries, private-key/certificate contents, passwords, camera UID/MAC/IP, full flash dumps, firmware signing data, or personal recordings. Use private local inputs, referenced by name and hash.

Do not log into, probe, reboot, reconfigure, move the lens on, or flash the working camera without a separate explicit approval for that operation. Experimental flashing is additionally blocked until a full device-specific backup and a *verified* recovery procedure exist. A Reolink update package is **not** a full-device backup.

## Workflow

- **GitHub is shared project history** for ChatGPT discussions and Codex changes; it is not a real-time sync mechanism. Codex clones/pulls/pushes this repository. In ChatGPT, inspect the latest GitHub state before giving development instructions.
- Keep the firmware packages in a private local research directory, not this repo.
- Prioritize reproducible read-only extraction, evidence-backed architecture, small changes, checkpoints, and minimal useful diagnostics.
- Avoid full Android diagnostics/guided-testing standards; only include features that help firmware reliability, recovery, or testing.
- Keep `docs/STATE.md` current for handoffs.

See `docs/ROADMAP.md` for milestones, `docs/BOOT_RECOVERY_ANALYSIS.md` for the current static boot/recovery evidence, `docs/BSP_BUILD_AUDIT.md` for the pinned NA51055 build-input/toolchain audit, and `docs/MINIMAL_MAINTENANCE_FIRMWARE.md` for the offline maintenance-baseline design.
