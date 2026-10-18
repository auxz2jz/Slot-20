# C2b-2a-4 POSIX version header and bounded kernel build

**Scope:** correct the public Novatek version-header rule only in the disposable
private source tree, validate its generated C syntax, and run exactly one
single-threaded generic kernel build. This task did not build a root filesystem,
use the private Reolink FDT, assemble firmware, execute target code, or contact
a camera.

**Result:** COMPLETE WITH ONE NEXT BLOCKER. The POSIX correction works, the
prior `pci_iomap` errors do not recur, and compilation reaches the final
`vmlinux` link. The link stops because the vendor clock Makefile omits the
shipped PLL object that defines `pll_dump_info`. No kernel image was produced.

## Preserved input and exact source correction

The task reused the existing private source, output objects, GCC 6.5.0 ARM
toolchain, OpenSSL files, and host utilities. No dependency was reinstalled,
redownloaded, or rebuilt. Before modification:

- public Git was clean at pushed `f8e9d91`;
- private source `Makefile` SHA-256 was
  `426e1381390a092ff937b6e1203c8fe5330ce5da8cfffb9cc758a46dfa6cdecb`;
- the invalid generated header SHA-256 was
  `7520d5cf5cfad5012ce2be5e295ad22e107af2cc98846d4b02434511c08bd0c0`;
- no compiler process was running and 943 GiB was free.

The original Makefile is preserved privately as `Makefile.orig-c2b2a4` with the
same original hash. Portable patch
`patches/linux-4.19-nvtversion-posix-printf.patch`, SHA-256
`9708234c6450f640fd8c5900fb1417d3203a951d371ef67637a635f5b0798638`,
replaces the five-line shell-name/`echo` conditional with one line:

```make
printf '#define NVT_UTS_RELEASE\t"%s_%s"\n' "$(KERNELVERSION)" "$$($(CONFIG_SHELL) $(srctree)/scripts/setlocalversion --show-nvtver)"
```

This uses POSIX `printf`, keeps variable data outside the format string, and
removes both the non-POSIX `==` test and shell-specific `echo -e`. The patch
passed a dry run before being applied once. The patched private Makefile
SHA-256 is
`681521f1027d322ad4fffbb57f38919f3bfa0c2db1e3e16bbf909d8e66c77ff2`;
a reverse dry run confirms the exact patch is present. The public patch was
checkpointed and pushed at `d9e6db1` before compilation.

## Header regeneration and verification

The targeted `include/generated/nvtversion.h` rule exited zero. It produced the
35-byte header below, SHA-256
`e12d54040a10d69a57425bc2cd68b4d50a9cff5846828c390397390aa85074a7`:

```c
#define NVT_UTS_RELEASE	"4.19.91_"
```

The leading `-e` is absent. A syntax-only parse using the preserved
`arm-buildroot-linux-gnueabihf-gcc` passed. Regeneration-log hashes are:

| File | SHA-256 |
| --- | --- |
| `nvtversion-c2b2a4.log` | `38466cd9a018a5e09e6c5b0929b2b9089dab8fab22d21247f1589e7660c0e1e5` |
| `nvtversion-c2b2a4.time` | `a3937375c0cdb27582c9fa73bab31236493d9375af6d2ae635cd9ebadafcee97` |

## The one kernel build

The existing default target was invoked exactly once with the preserved host
OpenSSL settings and `-j1`. It ran 4 minutes 52.25 seconds, peaked at 136,860
KiB resident memory, and exited 2. The build compiled the remaining ARM objects,
archived `built-in.a`, produced `vmlinux.o`, passed `MODPOST vmlinux.o`, and
entered the final `vmlinux` link.

The prior `nvt-info.o` compile passed. Exact searches of both saved streams find
none of the prior conflicting/previous-definition/error diagnostics for
`pci_iomap`; only the successful compilation of `lib/pci_iomap.o` is logged.

Private build evidence:

| File | Lines | SHA-256 |
| --- | ---: | --- |
| `build-c2b2a4.log` | 1,553 | `e138e875bd98b9a71d4c06d9253d28d0a2af1e2eb87089d14e4eb7903fb13a10` |
| `build-c2b2a4.time` | 32 | `1050d4d09ae5929514f6d23e81204fef4ec324f00dba155b6d6fa9619309d17d` |

## Next exact linker blocker

The sole final-link diagnostic is:

```text
nvt-clk-dbg.c:(.text+0x30): undefined reference to `pll_dump_info'
```

Static evidence identifies an object-list problem rather than a missing symbol
inside the supplied blob:

- `.config` enables `CONFIG_COMMON_CLK_NA51055=y`.
- `drivers/clk/novatek/nvt-clk-dbg.o`, SHA-256
  `5bea5ac361db22bb4b741327e530b1a0866e275837481be8d3750a7391aca8e7`,
  has an undefined `pll_dump_info` reference.
- The 25,892-byte ARM EABI5
  `drivers/clk/novatek/na51055/pll.o_shipped`, SHA-256
  `a676bf4a156726769578710994704e863585034615001b3d7b9b90d2c5a6a87c`,
  defines global text symbol `pll_dump_info` at offset `0x1cc0`.
- The vendor Makefile lists `na51055/pll.o_shipped` directly in `obj-y` rather
  than the Kbuild output name `na51055/pll.o`.
- No `out/.../na51055/pll.o` exists. The generated thin archive command and
  member list contain only `nvt-im-clk-fr.o`, `na51055-clk.o`, and
  `nvt-clk-dbg.o`; the provider is absent.

Thus the binary object is present and exposes the required symbol, but Kbuild
does not copy or archive it under the current object list. The blob remains a
binary-only provenance/redistribution blocker even if a private build can link.
No Makefile correction or second build was attempted in this task.

## Preserved outputs and limits

The private tree is now about 952 MiB and retains the original/patched source,
valid header, all objects, and logs. Failed-link intermediates may be removed by
Kbuild, and there is no `vmlinux`, `Image`, or `zImage`. No compiler process
remains running. Reaching the generic final link does not prove camera
compatibility, bootability, redistributability, recovery, or installation
safety.

## Next bounded task

**C2b-2a-5, only after explicit authorization:** make the minimal private
NA51055-only Kbuild object-name correction from `na51055/pll.o_shipped` to
`na51055/pll.o`. Verify that Kbuild materializes the shipped object, its hash or
symbol provenance is preserved, and the Novatek clock archive includes the
provider. Then run one further `-j1` build and stop at a successful generic
compile or the next exact blocker. Do not publish the binary object.
