# Recovery-first firmware development roadmap

**Primary goal:** a safely installable, independent Linux firmware for RLC-811A `IPC_523128M8MP` that is **never stranded without an update or recovery path**. The first persistent firmware must provide reliable Ethernet, an authenticated browser management interface and firmware upload/update/rollback; see [BOOT_UPDATE_RECOVERY_REQUIREMENTS.md](BOOT_UPDATE_RECOVERY_REQUIREMENTS.md).

**Research caveat:** a web interface only works if Linux/networking boot. Independent rescue and verified complete backup on matching spare hardware are required. Original Reolink system fallback and A/B partition capacity are unverified hypotheses, not established features.

## Current target roles

- The **primary development reference** is the owner's existing, screenshot-confirmed
  RLC-811A `IPC_523128M8MP`, currently running
  `v3.1.0.1643_2402219117`. It remains in active security service and is not a
  sacrificial recovery target.
- D2a matching-spare research is preserved, while D2a-1 seller outreach is **on
  hold**. No seller contact or purchase is authorized.
- Read-only observations on the primary reference and destructive recovery proof
  are separate lanes. The first cannot replace a verified full-device backup
  and independent recovery demonstration on a matching spare.
- The staged hardware and reusable-platform plan is
  [HARDWARE_DEVELOPMENT_PLAN.md](HARDWARE_DEVELOPMENT_PLAN.md).

| Phase | Work | Release/test gate |
|---|---|---|
| A — Offline boot analysis (complete through A5) | Reproduce package extraction, boot sequence, U-Boot environment, NAND layout and image signature/validation logic | Evidence-backed boot and recovery hypotheses; no camera access |
| B — Host update/recovery design (complete through B4) | Signed bundle verification plus update/boot-state simulation and deterministic fault tests | Host-only evidence; no physical rollback claim |
| C — Offline Linux and management prototype (complete through C3) | Reproducible generic kernel/rootfs plus authenticated browser-management demonstration using the verifier/simulator | No combined image, matching FDT, flash path or hardware claim |
| H — Primary-reference observations | Begin with existing screenshot evidence, then propose separately approved, read-only identification and diagnostics on the in-service owner camera | No live action without exact approval; no settings, reboot, actuation, opening or storage access |
| M — Multi-camera framework | Introduce vendor-neutral security/update/management contracts with exact board profiles and SoC/board adapters | Synthetic contract tests first; unsupported hardware fails closed |
| D/R — Backup/recovery proof on spare | Resume exact-match spare acquisition when the hold is removed; verify full raw/OOB backup and actual independent rescue before controlled failures | Independent restore demonstrated on matching spare; original factory media preserved where feasible |
| E — Controlled first install | Only after all backup/recovery/update/UI checks and a new owner review/approval | First installed image is maintainable and recoverable |
| F — Camera functionality | Capture/encode video, RTSP, recording, lens, autofocus, IR, spotlight and audio through hardware-specific adapters | Measured functional tests on a safely recoverable target |
| G — Advanced features | Custom zones, tracking, modular AI/ALPR | Noncritical, profile-aware enhancement phase |

**A minimal test image without web management may be built offline or potentially booted temporarily from RAM on a safely recoverable spare, but it must never be the first persistent firmware on the working camera.**

**Current boundary (2026-10-19):** D1 planning and D2a non-contact sourcing
research are complete. The owner-confirmed primary development camera is now
explicitly recognized, but it remains in service and has not been contacted by
this project. D2a-1 outreach is on hold; no matching spare, full-device backup
or proved recovery method exists. The next task is the offline H0 evidence
baseline. Every later live or physical gate requires fresh, action-specific
authorization.

The software should evolve by retaining a vendor-neutral core for bounded
artifact verification, authentication, update policy/state and management UX,
while placing SoC, device-tree, bootloader, flash/OOB/ECC, Ethernet, sensor/ISP,
lens and recovery behavior behind exact-version profiles and narrow adapters.
No such refactor is performed by this planning checkpoint.

Keep minimal actionable boot/updater logs and project checkpoints, not the complete Android diagnostics framework. Stock firmware update packages are not full-device backups. Do not store vendor binaries, flash dumps or device-specific secrets in the public repository.
