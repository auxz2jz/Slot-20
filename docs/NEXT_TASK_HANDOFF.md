# Slot-20 — Current task handoff

**Status:** C2b-2a-5 COMPLETE WITH NEXT EXACT BLOCKER — the one-line NA51055
Kbuild correction is verified, `pll_dump_info` resolves, and the generic kernel
links. The one authorized `-j1` build produced private `vmlinux`, `System.map`,
and uncompressed `Image`, then stopped because host command `lz4c` is absent.

**LAST TASK ID / STATUS:** C2b-2a-5 PLL Kbuild correction and bounded rebuild —
**COMPLETE WITH REPRODUCIBLE zImage-COMPRESSION BLOCKER**.

**EVIDENCE AND TESTS:**

- Git began clean at pushed `3deb3e3`. Reused the existing private source,
  objects, GCC 6.5.0 toolchain, OpenSSL input, and host utilities; nothing was
  installed, redownloaded, or rebuilt.
- Original private clock Makefile is preserved as `Makefile.orig-c2b2a5`,
  SHA-256
  `2beb443d6fd4d355fee001f814f9e72222c4664ad63448daeaaf4b3ceaf30dcf`.
- Public patch `patches/linux-4.19-na51055-pll-kbuild-object.patch`, SHA-256
  `2535865c84c633af2fd5d16399e9f1e14a086044e7af2d1c7c4d2be9bbaac48a`,
  changes only enabled NA51055 `na51055/pll.o_shipped` to `na51055/pll.o`.
  NA51089 is unchanged. The patched Makefile hash is
  `88ea634fc4bb0a236eb95c1a297d23f9c0561aced3877a646b6757c47ebe4cf9`.
- The public patch was checkpointed and pushed before the full build at
  `e753060`.
- Focused Kbuild verification exited zero: generated `pll.o` is byte-identical
  to the private shipped input (SHA-256 `a676bf4a...e7af2d1`), the clock archive
  contains it, and the archive defines `00001cc0 T pll_dump_info`.
- Exactly one default-target build ran with `-j1`. It exited 2 after 8.49
  seconds, but completed `vmlinux`, `System.map`, and uncompressed `Image`.
- Private `vmlinux` is a statically linked, unstripped ELF32 little-endian ARM
  EABI5 executable and contains `80341794 T pll_dump_info`.
- Output hashes: `vmlinux` `cdad3126...328913`; `System.map`
  `1c51ceba...9db0c`; `Image` `04c6f8cf...a040` (full values are in
  `configs/c2b2a5_compile_result.json`).
- First blocker: `LZ4 arch/arm/boot/compressed/piggy_data`, then `/bin/sh: 1:
  lz4c: not found`. `lz4c` is absent from the build PATH and `zImage` is absent.
- Private build log hashes: `build-c2b2a5.log`
  `e9049583b226c93b12b6ea06cfde05881bd219d11d4b8494d93ddb953e7bee5e`;
  `build-c2b2a5.time`
  `9715ef70059825a39295fcc55fbd96192ae1f83be54ab976fb45199eda1f4879`.
- No retry was made and no compiler process remains. Full sanitized evidence is
  in `docs/C2B2A5_KERNEL_COMPILE.md` and
  `configs/c2b2a5_compile_result.json`.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; pre-build patch checkpoint `e753060`
is pushed. The commit containing this handoff is the C2b-2a-5 completion
checkpoint and must match `origin/main` after push.

**LOCAL UNTRACKED OR PRIVATE WORK:** Preserve
`/home/firmware-analysis/slot20_private/c2b2a2_20261017/`. It contains the
original/patched source, binary-only shipped objects, generated ARM objects,
linked outputs, and full logs. These remain private/off-Git. Do not clean or
re-extract it.

**NEXT SINGLE TASK ID + INPUT:** **C2b-2a-6, only after explicit
authorization.** Obtain or reuse a provenance-recorded host `lz4c` compatible
with this Linux 4.19 build, without reinstalling or rebuilding working inputs.

**PASS CRITERION FOR NEXT TASK:** Verify `lz4c` version/origin/hash, then resume
the preserved configured tree with exactly one bounded `-j1` build. Stop at a
produced generic `zImage` or the next exact blocker. Do not start C2b-2b, build
a rootfs, package a kernel, use the private Reolink FDT, assemble firmware, or
access hardware.

**RECOMMENDED REASONING + WHY:** **High**. The next step is bounded legacy host-
tool provenance and kernel compression/build debugging; the linked output still
has binary-only licensing boundaries.

**WHEN TO SWITCH:** Medium is sufficient after `zImage` generation if only
routine artifact inventory and documentation remain. Consider Ultra only after
two materially different High-level approaches expose a persistent critical
ABI or build-system failure; return to High after isolation.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** Reliable closeout telemetry
on 2026-10-18 showed 15% used in the five-hour window (85% remaining) and 14%
used in the weekly window (86% remaining). This is a snapshot, not continuous
monitoring; refresh at the next authorized task.

**USAGE PREPARATION:** Pre-build checkpoint `e753060` is pushed. Push this
completion checkpoint before acquiring `lz4c` or running another build.

**CONTINUE OR STOP + REASON:** **STOP after C2b-2a-5**, as requested. The one
authorized build reached its next exact blocker; no host-tool acquisition or
second build is authorized in this task.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot, modification,
or flash was performed or authorized.
