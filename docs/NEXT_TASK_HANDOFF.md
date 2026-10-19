# Slot-20 — Current task handoff

**Status:** C3.2 COMPLETE — the localhost-only server, bounded demonstration
authentication/session/CSRF boundary, static dashboard shell and authenticated
simulator status API are implemented and tested. Update controls remain
disabled pending C3.3.

**LAST TASK ID / STATUS:** C3.2 authentication/status shell — **COMPLETE; 7
FOCUSED TESTS PASS**.

**EVIDENCE AND TESTS:**

- `docs/C3_MANAGEMENT_UI.md` defines C3.1–C3.4, loopback-only serving,
  bounded authentication/session/CSRF controls, temporary-file B2 validation,
  B3 action mapping, synthetic-only keys/bundles, browser flows and focused
  tests. It explicitly excludes camera/device/flash access and hardware claims.
- `tools/management_demo.py` binds only `127.0.0.1`; static routes are explicit,
  authenticated status is sanitized, and no outbound/device/subprocess API
  exists. Seven C3.2 HTTP tests pass under Python 3.12.14.
- Git began clean at pushed `d63c138`; pre-build input checkpoint `1ad67c4`
  is pushed.
- The clean output `.config` is byte-identical to the original at SHA-256
  `ccda34ef...686eb`.
- Exactly one `-j1` rootfs build ran under a 1,800-second bound and exited zero
  in 3:10.17 with 162,992 KiB peak RSS.
- Original and reproduced tar files are both 3,696,640 bytes with 374 entries.
  Their hashes are `df413f6a...e06a` and `b039fa24...635`.
- All paths/order match. After timestamp removal, types, permissions, numeric
  ownership, sizes, links and device metadata are identical. Of 41 regular
  files, 40 are byte-identical.
- BusyBox differs in four bytes solely in its 15:37:48 versus 15:56:33 build
  banner. Replacing only that text in private comparison copies makes both
  files hash to `9bd2c666...514c`; architecture remains ELF32 ARM EABI5,
  ARMv7 hard-float.
- Raw metadata differs for 337 entries and matches for 37, explaining the
  archive-hash variance together with the BusyBox banner.
- `legal-info` exited zero, collected BusyBox plus eight versioned host-source
  sets and licenses, and left the rootfs hash unchanged. It also exposed three
  gaps: Buildroot source not copied, external toolchain sources/licenses not
  collected, and acl/attr license files without package hash entries.
- No make/compiler process remains. Full sanitized evidence is in
  `docs/C2B2C_ROOTFS_REPRODUCIBILITY.md` and
  `configs/c2b2c_rootfs_reproducibility_result.json`.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; C3.1 checkpoint `88d3d2a` is pushed.
The commit containing this handoff is the C3.2 source checkpoint and must match
`origin/main` after push.

**LOCAL UNTRACKED OR PRIVATE WORK:** Preserve both
`/home/firmware-analysis/slot20_private/c2b2b_20261018/` and
`/home/firmware-analysis/slot20_private/c2b2c_20261018/`. They contain the two
rootfs artifacts, Buildroot outputs, legal-info, source cache, compatibility
patches and full logs. Do not clean or publish these directories. Preserve the
separate completed kernel tree unchanged.

**NEXT SINGLE TASK ID + INPUT:** **C3.3.** Add ephemeral-key synthetic demo
bundles, bounded temporary upload validation through B2, and only the fixed B3
simulation action enum described in `docs/C3_MANAGEMENT_UI.md`.

**PASS CRITERION FOR NEXT TASK:** Focused tests prove valid and corrupt bundle
results, verification/authorization separation, success/commit, boot
failure/rollback, recovery-required and invalid-transition rejection while
preserving known-good. No camera/device/installer API.

**RECOMMENDED REASONING + WHY:** **Medium**. C3 is routine host-only UI and
integration work against already tested Python components.

**WHEN TO SWITCH:** Use High if authentication, signed-bundle integration or
simulator state handling exposes a non-routine persistent failure. Ultra is
not warranted unless a later recovery-critical hardware uncertainty must be
resolved.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** Reliable C3-start telemetry
on 2026-10-18 showed 0% used in the five-hour window (100% remaining) and 37%
used in the weekly window (63% remaining). This is a snapshot, not continuous
monitoring.

**USAGE PREPARATION:** Push this tested C3.2 checkpoint before C3.3. Refresh
usage after C3.3 and before browser screenshot work.

**CONTINUE OR STOP + REASON:** Continue to C3.3 only after this tested source
checkpoint is pushed; no work beyond C3 is authorized.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot,
modification, or flash was performed or authorized.
