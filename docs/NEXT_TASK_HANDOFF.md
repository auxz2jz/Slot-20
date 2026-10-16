# Slot-20 — Current task handoff

**Status:** Task B4 COMPLETE — deterministic host-filesystem interruption, stale/missing/partial/corrupt-record tests now exercise the B3 simulator. Results are host simulation evidence only and do not prove NAND, bootloader or camera recovery.

**LAST TASK ID / STATUS:** B4 interrupted-write/power-loss/state-corruption fault tests — **VERIFIED COMPLETE (host software only)**. Phase C was not started.

**EVIDENCE AND TESTS:**

- The state schema is now `slot20.update-state.v2`. A domain-separated SHA-256 over all other record fields detects accidental corruption; it is unkeyed and does not authenticate a hostile rewrite.
- `UpdateStateSimulator.load(..., minimum_generation=N)` rejects a complete record older than a separately trusted floor. Without an external floor, a stale but valid record is intentionally indistinguishable from the latest record.
- Abrupt interruption before temporary-file sync or before replacement leaves the prior primary and known-good identity loadable; orphan temporary files are ignored.
- Interruption immediately after replacement leaves a complete new checksummed record loadable after restart. Process memory may still reflect the prior state until reloaded.
- Missing, truncated, checksum-corrupt and checksum-valid/invariant-invalid primary records fail closed. A complete orphan is never promoted automatically.
- Missing/corrupt primary state and unanchored stale-state ambiguity require a separately trusted state/known-good source. The simulator implements no physical recovery action.
- `tests/test_update_state_faults.py` adds 11 deterministic cases. Final full suite with bundled Python 3.12.14: **64 tests ran; 62 passed, 2 skipped**. Both skips are Windows symlink cases requiring unavailable privilege; all B4, B3, B2 and earlier tests otherwise passed.
- Python compilation and `git diff --check` passed. No network, camera, device-node, partition, NAND or flash interface was added.

**IMPORTANT LIMITS:** Host `fsync` and file replacement do not model NAND programming, bad blocks, controller caches, boot metadata, A/B partitions or actual power-loss behavior, and no portable directory-entry durability is claimed. The checksum detects accidents, not malicious rewrites. The external generation floor and external trusted recovery copy are caller responsibilities and are not implemented as device features.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; parent checkpoint `9a122e9`. The B4 checkpoint is the commit containing this file and is pushed to `origin/main` after final verification; use `git log -1 --oneline` for its immutable ID.

**LOCAL UNTRACKED OR PRIVATE WORK (NO SECRETS):** proprietary firmware/FDT/U-Boot, extracted trees and private analysis environments remain local and outside Git. B4 used temporary synthetic state only. Do not delete or upload private artifacts.

**WHAT REMAINS UNFINISHED:** Real redundant/anti-replay boot metadata; production trust-policy and key custody; component-to-storage mapping; physical update, health, rollback and recovery mechanisms; full device backup; and every matching-spare demonstration.

**NEXT SINGLE TASK ID + INPUT:** **C1**, only when explicitly started — audit required Novatek BSP build inputs, shipped binary objects, licensing and cross-compiler ABI. Reuse pinned local BSP evidence; do not repeat firmware extraction or bootloader analysis and do not produce a flashable image.

**PASS CRITERION FOR NEXT TASK:** a bounded dependency/toolchain inventory identifies source versus shipped binary inputs, licenses/restrictions, ABI/toolchain requirements, reproducibility blockers and the next exact build-preparation step; no camera access or Phase C2 build is performed.

**RECOMMENDED REASONING + WHY:** **High** for C1. Cross-toolchain/ABI compatibility and licensing provenance require careful evidence review, though difficult bootloader reverse engineering is not expected.

**WHEN TO SWITCH:** Medium is sufficient after the dependency/license inventory is established and only routine documentation remains. Consider Ultra only for one specific opaque ABI blocker that persists after two materially different bounded approaches.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** reliable Codex telemetry at 2026-10-16 13:25 PDT reported 38% used in the five-hour window and 40% used in the weekly window (62% and 60% remaining). This is a timestamped snapshot, not continuous monitoring.

**USAGE PREPARATION:** Commit and push B4 before any Phase C work. Recheck reliable telemetry at the C1 boundary and checkpoint before an expensive toolchain or build probe.

**CONTINUE OR STOP + REASON:** **STOP after B4**, as explicitly requested. Do not begin Phase C automatically.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot, modification or flash was performed or authorized.
