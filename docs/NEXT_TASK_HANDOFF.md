# Slot-20 — Current task handoff

**Status:** D1 PLANNING IN PROGRESS — scope and atomic outputs are frozen; no
camera or other hardware has been contacted.

**LAST TASK ID / STATUS:** D1 design checkpoint — COMPLETE. Detailed D1.1–D1.4
planning remains.

**EVIDENCE AND TESTS:**

- C3 was split and checkpointed as C3.1 design (`88d3d2a`), C3.2 localhost
  shell (`cb3023d`) and C3.3 verifier/simulator integration (`ecab661`).
- `tools/management_demo.py` binds only `127.0.0.1`, uses bounded demo
  sessions and CSRF, accepts bounded temporary uploads, invokes the existing B2
  verifier and exposes only a fixed B3 simulator-action enum.
- Bundle verification never authorizes installation. The next simulated action
  is a separate, visibly labeled host-only authorization step.
- `tools/capture_management_demo.cjs` refuses non-loopback URLs and reproduced
  six browser states using local Edge/Playwright. The final capture reported
  zero browser console errors. Screenshot sizes and SHA-256 values are in
  `configs/c3_management_demo_result.json`.
- The actual localhost UI screenshots are under `docs/images/c3-*.png` and are
  labeled offline simulation. They show status, successful validation,
  committed logical update, corrupt-bundle rejection, logical rollback and
  recovery required.
- `python -m unittest discover -s tests -v` ran 77 tests in 8.315 seconds:
  75 passed and two pre-existing Windows symlink tests skipped because the
  account lacks symlink privilege. All 13 C3 tests passed.
- `py_compile`, `node --check tools/capture_management_demo.cjs` and
  `git diff --check` passed. The demo server was stopped; no TCP 8765 listener
  remained.
- `docs/C3_MANAGEMENT_UI.md` contains the design, implementation boundaries,
  reproduction command, screenshot links and explicit evidence limits.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; C3.1–C3.3 checkpoints are pushed.
The C3.4 completion commit containing this handoff must match `origin/main`
after the final push.

**LOCAL UNTRACKED OR PRIVATE WORK:** Preserve the completed kernel and both
successful rootfs trees under `/home/firmware-analysis/slot20_private/`.
They were not modified by C3 and remain outside Git. No proprietary input,
private key, synthetic bundle or persistent demo state is committed.

**NEXT SINGLE TASK ID + INPUT:** Complete **D1.1–D1.4 planning only** using the
existing A5 evidence and authoritative public references. Do not contact any
camera.

**PASS CRITERION FOR NEXT TASK:** A reviewed written protocol specifies exact
hardware-match evidence, full-flash/OOB/ECC/calibration preservation, backup
integrity checks, independent restore path, abort criteria and explicit
approval gates. It must not assert that UART, TFTP, Boot ROM or external NAND
recovery works without matching-hardware evidence.

**RECOMMENDED REASONING + WHY:** **High.** The task crosses destructive-risk
boundaries, board identity, NAND geometry/ECC/OOB handling and boot/recovery
evidence. It requires careful synthesis, although no reverse engineering or
hardware action is yet authorized.

**WHEN TO SWITCH:** Medium is sufficient once the recovery architecture is
settled and the work becomes routine documentation. Ultra/highest capability
should be considered only for one narrowly scoped, persistent Novatek
BootROM/bootloader uncertainty after a safe checkpoint and explicit model
selection.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** At the D1 design checkpoint
on 2026-10-19, reliable telemetry showed 52% five-hour usage (48% remaining)
and 45% weekly usage (55% remaining). This is a point-in-time snapshot.

**USAGE PREPARATION:** C3 is fully checkpointed. Refresh reliable usage before
any expensive D1 investigation and create another checkpoint before any later
physical operation.

**CONTINUE OR STOP + REASON:** Continue only through the authorized D1 written
plan, then stop before D2 or any physical operation.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot,
modification, firmware assembly or flash was performed or authorized.
