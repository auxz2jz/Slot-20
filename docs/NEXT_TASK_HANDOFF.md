# Slot-20 — Current task handoff

**Status:** Task A4 COMPLETE — the matching-package U-Boot environment, bootargs assembly and declared flash ownership now have a bounded evidence record. Actual-binary/FDT facts are separated from generic Novatek build options and unresolved partition owners.

**LAST TASK ID / STATUS:** A4 environment, boot arguments and flash ownership — **VERIFIED COMPLETE**. Private artifacts remained ignored, recovered ARM code was disassembled but never executed, and no A5 recovery-candidate work was started.

**EVIDENCE AND TESTS:**

- The matching binary's environment linker list is one 20-byte entry at file offsets `0x7fe0c..0x7fe1f`: name `nowhere`, null load/save slots, and initializer `0x060425f0`. That initializer selects the compiled default blob at `0x0606c0b8`; there is no registered `saveenv` command.
- The 391-byte default blob has 15 entries. Relevant exact values are the UBIFS `bootargs` at `0x6c0b8`, `bootcmd=nvt_boot` at `0x6c14a`, `bootdelay=0` at `0x6c15b`, and `baudrate=115200` at `0x6c167`.
- Early boot calls `0x0600acc8` to derive volatile `mtdids=nand0=spi_nand.0`, `mtdparts`, and a rootfs argument from the prepared package FDT. Actual helper `0x06005750` counts `partition_rootfs` as MTD index 6, and the matching caller appends `ubi.mtd=6 ro`.
- The package FDT `/chosen/bootargs` is a single space, so U-Boot owns the effective base command line. A3's handler later appends timestamps, resume address and debug state before `bootm`.
- The FDT reserves `uenv` at `0x00240000..0x0027ffff`, but the actual U-Boot does not load or save an environment there. Its contents and owner remain unknown and must be preserved.
- The pinned generic header optionally places a NAND environment at `0x002c0000` with a `0x40000` range. On this matching FDT that range lies inside `kernel` (`0x00280000..0x006fffff`), so the generic offset is incompatible and dangerous. The generic defconfig's `saveenv` option also does not match the shipped command table.
- The FDT `partition_kernel` role is translated to runtime MTD name `linux`; this explains A3's named load and is not a second partition. Omitted `fdt.restore`, `uenv`, `para`, `sp`, `ext_para`, and `download` regions remain preserve/unknown; prior static evidence means `para` and `download` are not free space.
- Focused verification used capped exact-token/default-blob checks, the sole environment-driver table and initializer, bounded partition/rootfs disassembly, in-memory DTC output for bootargs/partition/NVTPACK nodes, pinned generic Git objects, documentation consistency/whitespace checks, ignored-private-file checks, staged-file scope review, and final push confirmation.

**IMPORTANT STATIC LIMITS:** No installed-camera environment bytes, live command line, NAND contents or persistence behavior were observed. The separate `uenv` region might be reserved or used by another stage; `fdt.restore`, `sp`, `ext_para`, and detailed `para`/`download` lifecycle remain unresolved. Generic source explains mechanisms but is not the Reolink build configuration.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; parent checkpoint `6bd99b9`. The A4 checkpoint is the commit containing this file and is pushed to `origin/main` after focused verification; use `git log -1 --oneline` for its immutable ID.

**LOCAL UNTRACKED OR PRIVATE WORK (NO SECRETS):** proprietary `uboot.bin`/`fdt.bin`, bounded helpers, prior extracted firmware, and isolated WSL analyzer/upstream environments remain local/private and are not Git-backed. Missing public objects were read through the existing pinned upstream clone without checking out or modifying its preserved worktree. Do not delete or upload `firmware_workspace/` or `/home/firmware-analysis/slot20_private/`.

**WHAT REMAINS UNFINISHED:** A5's independent-rescue evidence matrix; installed-camera byte identity; exact ownership/restore semantics of all omitted partitions; BootROM/loader authentication; fuse state; physical UART/Ethernet/MMC interfaces; NAND OOB/ECC behavior; power-loss safety; rollback; and every live recovery path.

**NEXT SINGLE TASK ID + INPUT:** **A5** — review the already recovered rescue leads and produce a concise matrix for UART, TFTP/Ethernet, MMC/FAT, Boot ROM, external programmer and any protected recovery path. For each, separate actual-binary evidence, generic capability, missing board evidence and minimum matching-spare test. Do not claim a route works and do not begin B1.

**PASS CRITERION FOR NEXT TASK:** one sanitized matrix identifies the independence boundary, destructive risks and exact missing evidence/test hardware for each candidate; it reuses A1–A4, executes no target code, touches no camera, and does not promote command presence into recovery proof.

**RECOMMENDED REASONING + WHY:** **High** for A5 because it requires careful cross-evidence and safety-boundary analysis, but the relevant command, boot-flow and ownership findings are already bounded.

**WHEN TO SWITCH:** use Medium once only matrix/document editing remains. Consider Ultra only after the A5 checkpoint for one specifically identified Novatek Boot ROM, recovery-architecture or critical hardware uncertainty that cannot be resolved at High.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** reliable Codex telemetry at 2026-10-16 02:42 PDT reported 60% used in the five-hour window and 30% used in the weekly window (40% and 70% remaining respectively). This is a timestamped snapshot, not continuous monitoring.

**USAGE PREPARATION:** A4 is committed and pushed before A5. With five-hour usage in the project's 30–50% band, start A5 only from a fresh checkpoint and recheck telemetry; do not use this snapshot as a live meter.

**CONTINUE OR STOP + REASON:** **STOP after A4**, as explicitly requested. Do not start A5 automatically.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot, modification, or flash was performed or authorized.
