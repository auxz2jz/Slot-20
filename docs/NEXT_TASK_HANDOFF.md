# Slot-20 — Current task handoff

**Status:** Task B3 COMPLETE — a deterministic host-only, file-backed update/boot-state simulator now enforces normal transition invariants. It consumes B2 verification as a separate input and requires an independent, explicitly host-simulation-only install authorization.

**LAST TASK ID / STATUS:** B3 host-only firmware-update and boot-state simulator — **VERIFIED COMPLETE (host software only)**. B4 interruption/power-loss fault injection, physical storage mapping and camera integration were not started.

**EVIDENCE AND TESTS:**

- `tools/update_state_simulator.py` models `idle -> receiving -> verifying -> verified -> staged -> writing_candidate -> pending_boot -> healthy -> committed` plus verification rejection and boot-failure outcomes leading to symbolic known-good selection or `recovery_required`.
- The candidate digest and signed release identity must match a passing B2 `VerificationResult`. The result's `installation_authorized` field cannot authorize a transition and is rejected if asserted.
- Staging requires a separate `SimulationInstallAuthorization` bound to the exact candidate digest, an explicit approval, a bounded approval ID and the literal `host-simulation-only` scope. It cannot authorize a real install.
- The simulated known-good identity is unchanged throughout receive, verify, stage, candidate-write, pending and failure states. Only a healthy commit promotes the candidate; the former known-good identity is retained as `previous_known_good`.
- Persistence is one exact-schema canonical JSON record capped at 16 KiB. It has a bounded monotonic generation and bounded strings, rejects duplicate/unknown/inconsistent data and non-regular files, and replaces the record only after full validation and synchronous temporary-file write.
- `tests/test_update_state_simulator.py` adds 15 deterministic tests for successful/rejected paths, authorization separation, forbidden transitions, boot failure outcomes, reload/continuation, known-good preservation, canonical/bounded records and generation exhaustion.
- Final command: bundled Python 3.12.14, `python -m unittest discover -s tests -v` — **53 tests ran: 51 passed, 2 skipped**. Both skips are Windows symlink cases requiring a privilege unavailable to this account; all B3, B2 and prior tests otherwise passed.
- `docs/UPDATE_STATE_SIMULATOR.md` records the logical model and explicitly distinguishes symbolic state from physical A/B, rollback or recovery proof.

**IMPORTANT LIMITS:** B3 does not model real NAND geometry, slots, partitions, redundant boot metadata, boot-attempt limits or a proven recovery action. Normal same-directory replacement is not a power-loss guarantee. `writing_candidate`, `rolled_back` and `recovery_required` are logical simulation states only. No camera, network, device-node or flash API exists.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; parent checkpoint `f9eeb07`. The B3 checkpoint is the commit containing this file and is pushed to `origin/main` after final verification; use `git log -1 --oneline` for its immutable ID.

**LOCAL UNTRACKED OR PRIVATE WORK (NO SECRETS):** proprietary firmware/FDT/U-Boot, bounded helpers, extracted trees and isolated WSL analyzer/upstream environments remain local/private and are not Git-backed. B3 used only synthetic release identities and manually constructed verification results. Do not delete or upload private artifacts.

**WHAT REMAINS UNFINISHED:** B4 interrupted-write/power-loss fault tests; production builder/key custody; signed trust-policy format; durable device trust store/release catalog/security floor; real component-to-storage mapping; redundant boot metadata and attempt policy; physical health/rollback/recovery; full device backup; and every matching-spare recovery demonstration.

**NEXT SINGLE TASK ID + INPUT:** **B4** — add bounded interrupted-write/power-loss fault tests to the B3 host simulator. Reuse the deterministic normal-transition baseline and keep all results explicitly labeled as host simulation, not hardware proof.

**PASS CRITERION FOR NEXT TASK:** selected persistence boundaries are interrupted deterministically; restart behavior preserves or rejects state without silently losing the last validated known-good identity; stale, partial and corrupted records fail closed or follow an explicitly documented simulator recovery rule; the normal B3 suite stays passing; no real NAND/camera code or assumed A/B mechanism is added.

**RECOMMENDED REASONING + WHY:** **High** for B4. Interruption points, stale/corrupt persistence and recovery invariants require careful safety reasoning even in a bounded simulator.

**WHEN TO SWITCH:** Medium is sufficient once the fault matrix and expected invariants are fixed and only routine test/document updates remain. Ultra is not indicated unless two materially different bounded approaches leave a narrowly scoped recovery-state ambiguity unresolved.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** reliable Codex telemetry at 2026-10-16 13:07 PDT reported 22% used in the five-hour window and 37% used in the weekly window (78% and 63% remaining respectively). This is a timestamped snapshot, not continuous monitoring.

**USAGE PREPARATION:** Commit and push B3 before B4. Recheck reliable telemetry at the next task boundary and checkpoint before expanding B4's fault matrix.

**CONTINUE OR STOP + REASON:** **STOP after B3**, as explicitly requested. Do not start B4 automatically.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot, modification or flash was performed or authorized.
