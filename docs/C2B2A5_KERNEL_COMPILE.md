# C2b-2a-5 PLL Kbuild correction and bounded kernel build

**Scope:** correct only the enabled NA51055 clock object-list entry in the
existing disposable private source tree, verify Kbuild includes the shipped PLL
provider, and run exactly one single-threaded generic kernel build. This task
did not build a root filesystem, use the private Reolink FDT, assemble firmware,
execute target code, or contact a camera.

**Result:** COMPLETE WITH ONE NEXT BLOCKER. The one-line Kbuild correction
materializes the private shipped PLL object, adds it to the clock archive, and
resolves `pll_dump_info`. The generic kernel now links successfully and produces
`vmlinux`, `System.map`, and an uncompressed ARM `Image`. The same build stops at
the configured zImage compression step because host command `lz4c` is absent.

## Preserved source and minimal correction

Git began clean at pushed checkpoint `3deb3e3`. The task reused the existing
source, output objects, GCC 6.5.0 ARM hard-float toolchain, private OpenSSL input,
and host utilities. Nothing was reinstalled, redownloaded, or rebuilt.

The original private `drivers/clk/novatek/Makefile` is preserved as
`Makefile.orig-c2b2a5`, SHA-256
`2beb443d6fd4d355fee001f814f9e72222c4664ad63448daeaaf4b3ceaf30dcf`.
Portable public-source patch
`patches/linux-4.19-na51055-pll-kbuild-object.patch`, SHA-256
`2535865c84c633af2fd5d16399e9f1e14a086044e7af2d1c7c4d2be9bbaac48a`,
changes only the enabled NA51055 member:

```diff
-obj-$(CONFIG_COMMON_CLK_NA51055) += ... na51055/pll.o_shipped
+obj-$(CONFIG_COMMON_CLK_NA51055) += ... na51055/pll.o
```

The NA51089 entry is unchanged. The patch passed a dry run, was applied once,
and was pushed before the full build at checkpoint `e753060`. The patched
private Makefile SHA-256 is
`88ea634fc4bb0a236eb95c1a297d23f9c0561aced3877a646b6757c47ebe4cf9`.
The binary-only `pll.o_shipped` remains private and uncommitted.

## Focused Kbuild verification

The successful focused target logged `SHIPPED .../pll.o` followed by `AR
drivers/clk/novatek/built-in.a`. Verification showed:

- output `na51055/pll.o` is byte-identical to its private input, both SHA-256
  `a676bf4a156726769578710994704e863585034615001b3d7b9b90d2c5a6a87c`;
- the clock archive, SHA-256
  `bef7514f76cbbf3027471cde50dd7096ce35b376586af9fa4c73a5f527d19494`,
  contains `na51055/pll.o` as its fourth member; and
- the archive contains the consumer's undefined reference and the provider's
  global text definition, `00001cc0 T pll_dump_info`.

The first focused invocation omitted the already-required per-target OpenSSL
flags and stopped during Kbuild prerequisite checking; it did not compile the
kernel. The corrected focused invocation reused those existing flags and exited
zero in 1.09 seconds. Both private logs are retained so the setup mistake is not
hidden or repeated.

## The one kernel build

The existing default target was invoked exactly once with the preserved host
OpenSSL settings and `-j1`. It ran 8.49 seconds, peaked at 78,756 KiB resident
memory, and exited 2. Before the stop it completed `LD vmlinux`, `SORTEX
vmlinux`, `SYSMAP System.map`, and `OBJCOPY arch/arm/boot/Image`.

| Private output | Bytes | SHA-256 |
| --- | ---: | --- |
| `out/vmlinux` | 7,663,316 | `cdad3126f41b07bc147cfc83132b18999bf628b0cf7f0cfe8fbc755917328913` |
| `out/System.map` | 1,198,837 | `1c51ceba0fcb76846d671c86fa7b9cabf9415f56f279c9cfe764deb0d529db0c` |
| `out/arch/arm/boot/Image` | 7,577,616 | `04c6f8cf7061a8b00947c0e38a5a3227ad2c0faa499f6043ead86f13319ea040` |

`file` identifies `vmlinux` as a statically linked, unstripped ELF32
little-endian ARM EABI5 executable. Its symbol table contains
`80341794 T pll_dump_info`. These outputs stay private and are not claimed to be
camera-compatible or redistributable.

Private build evidence:

| File | Lines | SHA-256 |
| --- | ---: | --- |
| `build-c2b2a5.log` | 49 | `e9049583b226c93b12b6ea06cfde05881bd219d11d4b8494d93ddb953e7bee5e` |
| `build-c2b2a5.time` | 24 | `9715ef70059825a39295fcc55fbd96192ae1f83be54ab976fb45199eda1f4879` |

## Next exact blocker and limits

The first failure after the successful generic link is:

```text
LZ4     arch/arm/boot/compressed/piggy_data
/bin/sh: 1: lz4c: not found
```

`lz4c` is absent from the build `PATH`; `zImage` is absent. No dependency was
installed and no second build was attempted. No compiler process remains.

The linked generic output still depends on binary-only PLL and OTP objects and
lacks a matching-board device tree. A successful generic link is not evidence
of bootability, hardware compatibility, redistribution rights, recovery, or
installation safety.

## Next bounded task

**C2b-2a-6, only after explicit authorization:** obtain or reuse a
provenance-recorded host `lz4c` compatible with this Linux 4.19 build, verify its
version/hash, and resume the preserved build with one bounded `-j1` attempt.
Stop at a produced generic `zImage` or the next exact blocker. Do not start a
rootfs or firmware assembly.
