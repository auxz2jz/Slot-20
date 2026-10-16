# Slot-20 — Current task handoff

**Status:** Task A3 COMPLETE — the actual matching-package U-Boot normal path is documented from the registered `nvt_boot` handler through the named `linux` load and prepared FDT to the constructed `bootm` command. Static facts, compiled alternatives and unresolved provenance are explicitly separated.

**LAST TASK ID / STATUS:** A3 normal U-Boot boot sequence — **VERIFIED COMPLETE**. The private artifact remained ignored; recovered ARM code was disassembled but never executed, and no A4/A5 work was started.

**EVIDENCE AND TESTS:**

- The A2 table's `nvt_boot` entry at file offset `0x7f948` points to handler `0x0600d600`. The handler reads existing `bootargs`, calls the loader wrapper at `0x0600d550`, appends timestamp/resume arguments, and writes the updated environment value.
- The wrapper passes the prepared FDT (`[0x060802c8]`) to `0x0600c984`, which reads `/nvt_memory_cfg/rtos` `reg` cells and chooses the named-partition Linux loader at `0x0600cacc` or unresolved alternate `0x0600ce5c`.
- The traced NAND branch constructs `nand read 0x5800000 linux 0x40`, derives total size from the big-endian legacy-image size field, reloads that total, and calls the packaged-kernel helper with `0x05800000` and `0x01100000`. A separate `0x03800000` branch remains semantically unresolved.
- Before `nvt_boot`, the only direct call to FDT initializer `0x06003c90` is at `0x060012c8` with argument zero. That branch verifies and copies a loader-supplied memory FDT from global `0x060802bc` to the destination referenced by `0x060802c8`. The compiled nonzero/NAND branch reads `0x20000` bytes at flash offset `0x00040000`, optionally continuing at `0x00060000`, with a `0x80000` cap; it is not proved to be the normal path.
- The handler sets `fdt_high`, `bootm_size`, and `bootm_mapsize` to `0x07000000`, sets `bootm_low` to zero, constructs `bootm 5800000 - <fdt-address>`, and dispatches it through the command executor at `0x0601d7b4`.
- Focused verification used bounded Capstone ranges around the FDT caller/loader, selector, Linux loader, wrapper and handler, plus one input-capped full-image direct-call scan. Documentation consistency, whitespace, private-file ignore status, staged-file scope, and the final Git push are checked at checkpoint time.

**IMPORTANT STATIC LIMITS:** `0x0600d550` discards the selected loader's return and returns zero; `nvt_boot` does not check the final command executor's return. No live failure behavior was tested. The source of the loader-temporary FDT pointer, meanings of the FDT `reg` cells/selection global, alternate Linux loader, installed-camera byte identity, actual boot success and standard `bootm` acceptance policy remain unresolved.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; parent checkpoint `acef47c`. The A3 checkpoint is the commit containing this file and is pushed to `origin/main` after focused verification; use `git log -1 --oneline` for its immutable ID.

**LOCAL UNTRACKED OR PRIVATE WORK (NO SECRETS):** proprietary `uboot.bin`, the two ignored bounded helper scripts, prior extracted firmware, and isolated WSL analyzer environments remain local/private and are not Git-backed. Do not delete or upload `firmware_workspace/` or `/home/firmware-analysis/slot20_private/`.

**WHAT REMAINS UNFINISHED:** environment persistence/partition ownership (A4) and independent-rescue evidence (A5). FDT source-pointer provenance, alternate boot branches, installed-camera byte identity, BootROM/loader authentication, fuse state, physical interfaces, NAND/OOB/ECC behavior, update power-loss safety, rollback and every live recovery path remain unverified.

**NEXT SINGLE TASK ID + INPUT:** **A4** — analyze the actual environment location and boot arguments relative to the matching package FDT and generic BSP. Reuse the recovered environment findings, explicitly report offset/partition ownership mismatches, and never convert generic offsets into camera instructions. Do not begin A5.

**PASS CRITERION FOR NEXT TASK:** one concise sanitized report identifies actual-binary environment backend/persistence evidence, maps relevant boot arguments to the package FDT, distinguishes matching-binary facts from generic BSP defaults, and lists unresolved ownership without executing target code or touching hardware.

**RECOMMENDED REASONING + WHY:** **High** for A4 because correlating stripped-binary environment calls with the board-specific FDT and generic BSP requires careful provenance and mismatch analysis, but the preserved findings keep it bounded.

**WHEN TO SWITCH:** use Medium when only documentation remains. Consider Ultra only after an A4 checkpoint if one specific hardware-critical environment backend or partition-ownership ambiguity cannot be resolved with bounded High analysis.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** reliable Codex telemetry at 2026-10-16 01:31 PDT reported 8% used in the five-hour window and 22% used in the weekly window (92% and 78% remaining respectively). This is a timestamped snapshot, not continuous monitoring.

**USAGE PREPARATION:** A3 is committed and pushed before A4. Recheck usage at the next task boundary; do not use this snapshot as a live meter. A4 should begin from this handoff without repeating A3 disassembly.

**CONTINUE OR STOP + REASON:** **STOP after A3**, as explicitly requested. Do not start A4 automatically.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot, modification, or flash was performed or authorized.
