# C2b-2a-2 host-DTC correction and bounded kernel build

**Scope:** resume the recovered private Linux tree, verify the previously applied
upstream DTC correction, use the vendor-compatible relative output layout, and
make exactly one single-threaded generic kernel build attempt. This task did not
build a root filesystem, use the private Reolink FDT, assemble firmware, execute
target code, or contact a camera.

**Result:** COMPLETE WITH ONE NEXT BLOCKER. The upstream `yylloc` correction is
now build-verified and the relative `O=../out` layout works. The sole `-j1`
default-target attempt stopped at the next deterministic host prerequisite:
`scripts/extract-cert.c` cannot find `openssl/bio.h`. No kernel image was
produced.

## Reused inputs and pre-build checks

The disposable private tree remained at
`/home/firmware-analysis/slot20_private/c2b2a2_20261017/`. The build reused the
C2b-1 host tools and Buildroot 2019.05.2 GCC 6.5.0
`arm-buildroot-linux-gnueabihf` toolchain. Nothing was re-extracted, downloaded,
installed, patched again, or rebuilt before configuration.

| Item | Verified evidence |
| --- | --- |
| Git checkpoint before build | clean `main` at pushed `35c4933` |
| Free private-build storage | 943 GiB before the bounded build |
| Patched DTC lexer | SHA-256 `69564959cad177a54298c21903c8a242c5b167cfeee3b1265dca1ccdb5cca94c` |
| Preserved original lexer | SHA-256 `f3d221c5a7d243c456e0516f751ddbd7cf2cc6d28e0783a81e9ccaa0fb313902` |
| Upstream source | Linux commit `e33a814e772cdc36436c8c188d8c42d019fda639`; private patch SHA-256 `b683608be3be4048de517587b636982ebaa0a1cdbc315c45b7661aef3f9264d9` |
| Target compiler | Buildroot GCC 6.5.0; wrapper SHA-256 `c04c34d6014b183f08559d95c16c98f47622db9bf11a5007d1b4acc46adc3df3` |

## Configuration, preparation, and output geometry

The recovered tree used the C2b-1 environment and the relative output form:

```text
make -C source O=../out ARCH=arm \
  KBUILD_DEFCONFIG=na51055_evb_defconfig_nand_squash_release \
  CROSS_COMPILE=.../arm-buildroot-linux-gnueabihf- \
  NVT_VOS_DIR=.../vos NVT_HDAL_DIR=.../hdal defconfig
make -C source O=../out ARCH=arm \
  CROSS_COMPILE=.../arm-buildroot-linux-gnueabihf- \
  NVT_VOS_DIR=.../vos NVT_HDAL_DIR=.../hdal prepare
```

Both commands passed. The resulting `.config` SHA-256 is
`9a9c7ac6ecddd7900dcce61715c45507d02f0f510f6ea93fc46e33fe2c9ddbf5`,
matching both C2b-1 preflights. The vendor OTP copy rule put these files in the
intended external output tree:

| `out/drivers/soc/nvt/otp/na51055/` file | Bytes |
| --- | ---: |
| `otp_chkver.sh` | 249 |
| `otp_protected.o_shipped` | 19,764 |
| `otp_protected_no_l2.o_shipped` | 19,764 |
| `otp_protected_no_tracer.o_shipped` | 19,764 |

No malformed `source/home/...` path was created. The controlled VOS and HDAL
inputs remained empty. The known nonfatal `/bin/sh: [: unexpected operator`
warning remains, but did not stop `prepare`.

## The one compile attempt and exact blocker

The default target was invoked once with the same arguments and `-j1`.
`/usr/bin/time -v` records exit status 2 after 4.91 seconds and peak resident
memory of 43,336 KiB. The build passed the former failure point:

- `out/scripts/dtc/dtc` linked as an x86-64 host executable, SHA-256
  `e193fdda1bf389fef9796d974d48b1a9aa520b38be2ce1a9e491c4447adb382f`.
- `out/scripts/mod/empty.o` is an ELF32 little-endian ARM EABI5 relocatable,
  confirming that the preserved target compiler was invoked for a build helper.

The next fatal diagnostic is:

```text
HOSTCC  scripts/extract-cert
scripts/extract-cert.c:21:10: fatal error: openssl/bio.h: No such file or directory
```

This is a **missing host OpenSSL development-header prerequisite**, not a target
compiler, shipped-object ABI, kernel linker, or camera-compatibility result.
`CONFIG_SYSTEM_TRUSTED_KEYRING=y` selects `extract-cert`, and
`scripts/Makefile` links it with `-lcrypto`. The WSL host has the OpenSSL 3.0.13
program, but `/usr/include/openssl/bio.h` is absent and no copy exists in the
preserved private host-prefix or Buildroot toolchain host tree.

The build was not retried. There is no `vmlinux`, `Image`, or `zImage`, and no
build/compiler process remained running.

## Preserved evidence and limits

Private logs remain under `c2b2a2_20261017/logs/`:

| File | SHA-256 |
| --- | --- |
| `defconfig.log` | `743339714b7ec4c794d8269e208a35cf47353ab5a3e53a151ec4ecbccca635c4` |
| `prepare.log` | `cf5d9b00abe2efddc2afb0f1b60aab43d4ee86e4714a29a9cd8f41ab302ea25b` |
| `build.log` | `0e40d72570bca34acf302c243bdf996d5230157d1dd2a3a243d48e7fce3bcbd2` |
| `build.time` | `f8985352cbe0e1b7d407fbeed62daeaca8697c011deef0579611a7948e0fc732` |

These private files and generated objects are evidence for this exact host/input
combination and are deliberately not committed. Passing the DTC stage and
creating one ARM helper object do not prove that the generic kernel will link,
boot, support `IPC_523128M8MP`, or be lawfully redistributable.

## Next bounded task

**C2b-2a-3, only after explicit authorization:** add a provenance-recorded,
reusable host OpenSSL development-header/library input without changing the
camera or private source archive; verify that it supplies `openssl/bio.h` and a
compatible host `libcrypto`; then resume the existing configured private tree
with one further `-j1` build attempt. Stop at success or the next exact blocker.
C2b-2b rootfs work remains premature.
