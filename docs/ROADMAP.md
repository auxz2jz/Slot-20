# Recovery-first firmware development roadmap

**Primary goal:** a safely installable, independent Linux firmware for RLC-811A `IPC_523128M8MP` that is **never stranded without an update or recovery path**. The first persistent firmware must provide reliable Ethernet, an authenticated browser management interface and firmware upload/update/rollback; see [BOOT_UPDATE_RECOVERY_REQUIREMENTS.md](BOOT_UPDATE_RECOVERY_REQUIREMENTS.md).

**Research caveat:** a web interface only works if Linux/networking boot. Independent rescue and verified complete backup on matching spare hardware are required. Original Reolink system fallback and A/B partition capacity are unverified hypotheses, not established features.

| Phase | Work | Release/test gate |
|---|---|---|
| A — Offline boot analysis (now) | Reproduce package extraction, boot sequence, U-Boot environment, NAND layout and image signature/validation logic | Evidence-backed boot and recovery hypotheses; no camera access |
| B — Design independent rescue | Evaluate stock preservation, RAM boot, bootloader recovery, A/B or physical recovery; assess NAND capacity | No assumption that `download` partition is safe |
| C — Minimal firmware prototype | Build custom Linux + Ethernet + simple authenticated local web admin + validated image upload/update + boot health/rollback logic | Reproducible offline image and tested update simulator |
| D — Backup/recovery proof on spare | Verify full flash backup and actual rescue mechanism; run interrupted update, invalid image and failed-boot cases | Independent restore demonstrated on matching camera hardware |
| E — Controlled first install | Only after all checks + explicit approval; observe successful access and subsequent update | First installed image is maintainable and recoverable |
| F — Camera functionality | Capture/encode video, RTSP, recording, lens, autofocus, IR, spotlight and audio | Measured functional hardware tests |
| G — Advanced features | Custom zones, tracking, modular AI/ALPR | Noncritical enhancement phase |

**A minimal test image without web management may be built offline or potentially booted temporarily from RAM on a safely recoverable spare, but it must never be the first persistent firmware on the working camera.**

**Current Phase D boundary (2026-10-19):** D1 planning is complete in
[`D1_BACKUP_RECOVERY_PLAN.md`](D1_BACKUP_RECOVERY_PLAN.md). No matching spare
has been sourced or contacted, no backup exists and no recovery method is
proved. D2a sourcing research and every later physical gate require fresh,
explicit authorization.

Keep minimal actionable boot/updater logs and project checkpoints, not the complete Android diagnostics framework. Stock firmware update packages are not full-device backups. Do not store vendor binaries, flash dumps or device-specific secrets in the public repository.
