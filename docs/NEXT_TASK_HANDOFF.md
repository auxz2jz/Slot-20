# Slot-20 — Current task handoff

**Status:** D1 PLANNING COMPLETE — no camera was contacted, opened, powered,
rebooted, connected to UART, read from or written.

**LAST TASK ID / STATUS:** D1.1–D1.4 matching-spare backup and independent
recovery planning — **COMPLETE; HARDWARE EVIDENCE REMAINS UNVERIFIED**.

**EVIDENCE AND TESTS:**

- `docs/D1_BACKUP_RECOVERY_PLAN.md` defines exact Class A matching across model,
  hardware ID, PCB, SoC, NAND, DRAM, boot chain and boot-critical routing.
- A future verified backup requires three whole-chip physical raw data+OOB
  reads, two ECC-corrected reads, stable bad/reserved-block maps, exact geometry
  and tool provenance, all unique/factory regions, and two encrypted private
  copies. At least two independent raw reads must be byte-identical; mismatches
  and uncorrectable pages block writes.
- External raw programming or a proved authenticated Boot-ROM path provides
  the strongest potential independence. UART with TFTP/MMC can be
  Linux-independent but remains U-Boot-dependent. Reset/staged update and A/B
  are not trusted or established recovery paths.
- G0–G9 separate purchase, acceptance, opening, passive electrical work,
  backup, RAM-only loading, clone restore, Linux-failure recovery, early-boot
  recovery and production review. Each needs fresh approval.
- Global aborts cover identity/geometry/voltage mismatches, current/thermal
  anomalies, bus contention, any unexpected write/erase/BBT/OTP action,
  unavailable OOB, divergent reads, ECC failures and insufficient recovery
  copies.
- `configs/d1_recovery_plan.json` is the machine-readable target, acceptance,
  priority and approval-gate record. Focused JSON/schema consistency,
  documentation and Git checks must pass before the completion commit.
- Authoritative sources are limited to Reolink support/product information,
  Linux MTD/UBI documentation, `mtd-utils`, U-Boot and NIST; priced examples are
  dated planning anchors, not equipment approvals.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; pre-detail D1 design checkpoint
`0ba4303` is pushed. The final D1 completion commit containing this handoff must
match `origin/main` after push.

**LOCAL UNTRACKED OR PRIVATE WORK:** Preserve the completed kernel and both
rootfs trees under `/home/firmware-analysis/slot20_private/` and the existing
private firmware-analysis inputs. D1 did not modify them. No device dump,
identity, credential, private key or hardware photograph was created or
committed.

**NEXT SINGLE TASK ID + INPUT:** **D2a acquisition research only, BLOCKED until
the user explicitly authorizes it.** Locate a returnable exact-revision
`RLC-811A / IPC_523128M8MP` offer and request redacted seller device-info and
label evidence.

**PASS CRITERION FOR NEXT TASK:** One or more candidate offers record current
price/return terms plus redacted proof of exact model/hardware number. Reject
ambiguous or different hardware. Do not purchase or contact/power a camera.

**RECOMMENDED REASONING + WHY:** **Medium.** D2a is bounded sourcing and
evidence comparison against the fixed D1 checklist.

**WHEN TO SWITCH:** High is required before G1–G5 physical acceptance,
electrical or backup design. Ultra/highest capability is reserved for one
narrow persistent BootROM or recovery-architecture question after a safe
checkpoint and explicit model selection.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** Reliable D1 closeout telemetry
on 2026-10-19 showed 62% five-hour usage (38% remaining) and 47% weekly usage
(53% remaining). This is a point-in-time snapshot, not continuous monitoring.

**USAGE PREPARATION:** D1 is checkpointed. Refresh usage before D2a and save a
new checkpoint before each separately approved physical gate.

**CONTINUE OR STOP + REASON:** STOP after D1. D2a is a separately authorized
sourcing task; D2b and all physical stages are more restrictive.

**CAMERA CONTACT/FLASH:** NONE. No discovery, authentication, network contact,
power, reboot, opening, probing, UART, NAND read/write, firmware assembly or
flash was performed or authorized.
