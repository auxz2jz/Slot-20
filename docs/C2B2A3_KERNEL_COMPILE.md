# C2b-2a-3 OpenSSL host dependency and bounded kernel build

**Scope:** supply the missing host OpenSSL development input without installing
packages, verify the kernel's host `extract-cert` source, and resume the existing
configured private tree for exactly one single-threaded generic kernel build.
This task did not build a root filesystem, use the private Reolink FDT, assemble
firmware, execute target code, or contact a camera.

**Result:** COMPLETE WITH ONE NEXT BLOCKER. The OpenSSL dependency is resolved:
Kbuild produced `scripts/extract-cert` and the build advanced into ARM platform
objects. The sole `-j1` build then stopped at a malformed vendor-generated
`nvtversion.h`. No kernel image was produced.

## Preserved inputs and private dependency

The task reused `/home/firmware-analysis/slot20_private/c2b2a2_20261017/`, its
existing `.config`, patched DTC source, generated objects, host utilities, and
the C2b-1 GCC 6.5.0 ARM toolchain. Their previously recorded hashes remained
unchanged. The public Git tree was clean at pushed checkpoint `a1af255` before
the operation.

No suitable development header was present in `/usr/include`, the private host
prefix, the toolchain host tree, or the inspected package cache. Ubuntu package
metadata identified this exact match for the already installed runtime:

| Item | Provenance and verification |
| --- | --- |
| Development package | Ubuntu 24.04 `noble-updates/main`, `libssl-dev:amd64` `3.0.13-0ubuntu3.16`; repository filename `pool/main/o/openssl/libssl-dev_3.0.13-0ubuntu3.16_amd64.deb` |
| Downloaded `.deb` | 2,408,684 bytes; SHA-256 `2b4734df0475e305ac03abb0a2cc5659651ed37ef02d967a1c4033a154cf714b`, matching APT metadata |
| Package dependency | exact `libssl3t64 (= 3.0.13-0ubuntu3.16)` |
| Installed runtime | `libssl3t64:amd64` and `openssl` both `3.0.13-0ubuntu3.16`; `libcrypto.so.3` SHA-256 `6866ed711dab8927e1bf82bf1cd30e828bdfc34f3cc1e83b1c9eb01ce6c37d9a` |
| `openssl/bio.h` | package-extracted SHA-256 `9dde507c18007338ee90517748b2b468cf416b4738f56a68baab0b4bb362cbc0` |
| amd64 `opensslconf.h` | package-extracted SHA-256 `890184233890bacd52fd420fef07befad411b9a318b97efbf36f46673d3e7841` |
| packaged `libcrypto.a` | SHA-256 `9dffa9e77b1cb29b890e473cf9ee379818cb57a576c7ef476356cd4d5a433bcd` |

The `.deb` was downloaded and extracted only below private `deps/openssl/`.
`libssl-dev` was not installed and the WSL package database was not changed.
The host compile used the two package-provided include roots and the matching
installed `libcrypto.so.3` explicitly.

## Focused `extract-cert` verification

A direct host compile of the unmodified kernel `scripts/extract-cert.c` passed
after including both the generic and amd64 package header directories. Its
private output was an x86-64 PIE linked to `libcrypto.so.3`; SHA-256
`9ede0315dd5da6ac2bfc2e817e05d4ab4ca822f2b846fbb9e9e48b8053405df4`.

The final kernel build scoped those same include paths to
`HOSTCFLAGS_extract-cert.o` and provided an explicit matching
`HOSTLDLIBS_extract-cert`. Kbuild independently produced the same 17,728-byte
x86-64 `out/scripts/extract-cert` with the same SHA-256 and runtime dependency.
OpenSSL 3 deprecation diagnostics were warnings only.

Two exploratory target invocations are retained in the private logs: this
vendor tree exposes no top-level `scripts/extract-cert` target, and a global
`HOST_EXTRACFLAGS` override suppresses DTC's subdirectory include augmentation.
Neither invocation was a kernel build. The working solution uses the
extract-cert-specific flag and does not retain the global override.

## The one kernel build and next exact blocker

The default kernel target was invoked exactly once with the preserved inputs,
the host-only OpenSSL settings, and `-j1`. It ran for 16.14 seconds, peaked at
76,416 KiB resident memory, and exited 2. It passed host DTC and `extract-cert`,
then compiled ARM core, memory-management, crypto, and initial Novatek platform
objects before failing at `arch/arm/mach-nvt-ivot/nvt-info.o`.

The first fatal input is the 39-byte generated file
`out/include/generated/nvtversion.h`, SHA-256
`7520d5cf5cfad5012ce2be5e295ad22e107af2cc98846d4b02434511c08bd0c0`:

```text
-e #define NVT_UTS_RELEASE  "4.19.91_"
```

The leading `-e` is not valid C. Source `Makefile:1058-1063` selects between
`echo` and `echo -e` using `[ "$(SHELL)" == "/bin/dash" ]`. On this host,
`/bin/sh` resolves to `/usr/bin/dash`, but the literal make value is `/bin/sh`;
dash also rejects the non-POSIX `==` operator. The false branch therefore runs
dash's `echo -e`, which emits `-e` literally. A direct `/bin/sh` probe reproduces
that byte sequence.

The compiler consequently reports the first errors at `nvtversion.h:1` and an
undeclared `NVT_UTS_RELEASE`. Later `pci_iomap` type diagnostics occur in the
same failed translation unit and remain unresolved until the malformed header
is corrected and the object is compiled again. No workaround or second kernel
build was attempted.

## Preserved evidence and limits

Private logs remain under `c2b2a2_20261017/logs/`:

| File | SHA-256 |
| --- | --- |
| successful standalone host-check time log | `568b2064e1118ad9855a03d00902b20ece072d904c1fcdd8f610de1f7204bc9c` |
| `build-c2b2a3.log` | `4b75ddcee15ef6d42d14a6e441481b987dfd9b30354b455cfcd6270d5763d88a` |
| `build-c2b2a3.time` | `680cecad1b7827a1c24f919c373a48e620df22074fc9bf4f3bd3d06b59847156` |

All intermediate objects and diagnostic logs remain private/off-Git. There is
no `vmlinux`, `Image`, or `zImage`, and no compiler process remains running.
Progress into ARM objects does not prove that the generic kernel will link,
boot, support `IPC_523128M8MP`, or be lawfully redistributable.

## Next bounded task

**C2b-2a-4, only after explicit authorization:** verify and apply a minimal
private-tree, reproducible POSIX-shell correction to the public vendor
`nvtversion.h` generation rule, preferably replacing the shell-dependent echo
branch with `printf`. Regenerate and inspect the header, then make one further
`-j1` build attempt. Stop at a successful generic compile or the next exact
blocker, including whether the observed `pci_iomap` diagnostics persist.
