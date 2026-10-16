# Slot-20 — Current task handoff

**Status:** Task A5 COMPLETE — seven potential independent-recovery routes now have a bounded evidence matrix. Every route is explicitly unverified, and Linux-independent paths are distinguished from recovery below factory U-Boot.

**LAST TASK ID / STATUS:** A5 independent firmware recovery evaluation — **VERIFIED COMPLETE (static/documentary evidence only)**. A1–A4 findings were reused; firmware was not re-extracted or executed, no B1 work was started, and no camera was accessed.

**EVIDENCE AND TESTS:**

- UART: matching U-Boot contains console/baud/interrupt clues and `nvt_uart_disable`, but zero boot delay, pads, voltage, mux and input acceptance remain unknown. It could bypass failed Linux only while factory loader/U-Boot remains intact.
- TFTP/Ethernet: matching U-Boot registers BOOTP/DHCP/ping/TFTP plus `bootm`; generic NA51055 source has Ethernet support. Actual PHY/link initialization, safe RAM load addresses and command access are untested, so this is not a demonstrated network rescue route.
- MMC/FAT: matching U-Boot registers MMC and FAT read/write commands. No exposed slot, pinout, boot strap or direct Boot-ROM media path is established. Manual FAT loading would remain U-Boot-dependent.
- Boot ROM: immutable downloader access is only a hypothesis. No matching board trigger, transport, protocol, accepted loader, authentication or eFuse state is known.
- External SPI-NAND programming: the FDT/generic BSP establish only an SPI-NAND lead. Exact chip, voltage, OOB/ECC/bad-block semantics and safe access are unknown; this has the strongest potential software independence but highest physical/data-loss risk.
- Existing reset/staged update: recovered GPIO 43 logic erases part of `para` and invokes `upgrade all` from `download`. Image provenance/completeness, physical trigger, authentication, atomicity and power-loss recovery remain unproved; a reset button is not brick recovery evidence.
- Protected rescue/A-B: no implemented selector, protected slot, persistent health state or rollback target is established. Exact rollback/rescue strings and standard boot-count policy were absent in the bounded image, and the environment backend is volatile `nowhere`.
- Focused verification cross-checked the matrix against A2 command/string offsets, A3 boot dependencies, A4 environment/partition ownership, pinned generic-source limitations and `docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`. Documentation consistency, whitespace, tracked-file scope and private-file exclusion were checked before the checkpoint.

**IMPORTANT STATIC LIMITS:** None of these candidates has been observed on hardware or satisfies the independent-recovery gate. UART/TFTP/MMC could at most be Linux-independent until demonstrated and cannot protect against loader/U-Boot loss. Boot ROM/programmer routes require major protocol/electrical/raw-flash evidence. Matching-spare tests remain blocked behind a full verified backup and separate explicit approval.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; parent checkpoint `7c5aadc`. The A5 checkpoint is the commit containing this file and is pushed to `origin/main` after focused verification; use `git log -1 --oneline` for its immutable ID.

**LOCAL UNTRACKED OR PRIVATE WORK (NO SECRETS):** proprietary `uboot.bin`/`fdt.bin`, bounded helpers, prior extracted firmware, and isolated WSL analyzer/upstream environments remain local/private and are not Git-backed. Do not delete or upload `firmware_workspace/` or `/home/firmware-analysis/slot20_private/`.

**WHAT REMAINS UNFINISHED:** every live recovery demonstration; installed-camera byte identity; physical UART/Ethernet/MMC access; Boot-ROM protocol/security state; exact NAND/OOB/ECC/bad-block geometry; ownership/restore semantics of omitted partitions; authenticated/power-fail-safe updates; protected rollback; full per-device backup; and matching-spare proof.

**NEXT SINGLE TASK ID + INPUT:** **B1** — define a host-only compatible signed update-bundle format. Specify the hardware/profile identifier, version and downgrade policy, bounded component manifest, cryptographic hashes/signature, canonical encoding and explicit trust/security assumptions. Do not implement B2, choose camera flash offsets, or perform hardware work.

**PASS CRITERION FOR NEXT TASK:** one sanitized format specification defines deterministic signing/verification input, rejects ambiguous or mismatched metadata by design, bounds every length/count, states key-rotation/downgrade assumptions, and remains host-only. No target binaries, camera operations or claims of installability.

**RECOMMENDED REASONING + WHY:** **Medium** for B1. It is a bounded schema and threat-model design task using standard cryptographic primitives; it needs careful policy choices but no new reverse engineering, Linux build or hardware uncertainty.

**WHEN TO SWITCH:** use High for B2 implementation, cryptographic negative tests, parser-hardening or a substantive schema ambiguity. Ultra is not indicated unless a later narrowly scoped Novatek recovery/security question remains intractable at High.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** reliable Codex telemetry at 2026-10-16 02:52 PDT reported 4% used in the five-hour window and 32% used in the weekly window (96% and 68% remaining respectively). This is a timestamped snapshot, not continuous monitoring.

**USAGE PREPARATION:** A5 is committed and pushed before B1. Recheck telemetry at the next task boundary; no additional checkpoint is needed before routine B1 drafting beyond starting from this clean A5 commit, but checkpoint before any later cryptographic implementation or large build.

**CONTINUE OR STOP + REASON:** **STOP after A5**, as explicitly requested. Do not start B1 automatically.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot, modification or flash was performed or authorized.
