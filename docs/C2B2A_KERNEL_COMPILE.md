# C2b-2a bounded generic kernel compile/link attempt

**Scope:** one host-only build attempt against the pinned public Novatek Linux tree. The task reused the C2b-1 tools, used a new disposable private tree, and stopped at the first deterministic blocker. It did not build a root filesystem, use the private Reolink FDT, assemble firmware, execute target code or contact a camera.

**Result:** BLOCKED at the host device-tree-compiler link. The default kernel target never reached an ARM kernel compile or link, and no `vmlinux`, `Image` or `zImage` was produced.

## Frozen inputs and pre-build checkpoint

| Item | Verified evidence |
| --- | --- |
| Git recovery point | Clean `main` at pushed commit `7c1a8d0` before the build |
| Free private-build storage | 945 GiB available on `/home/firmware-analysis` before extraction |
| Linux source archive | Pinned commit `1019c2e049f239ba0668ccfd1356e952fde3b29b`; archive SHA-256 `66aca4fee2663f60ad68f9d3e9500a1475cefa825517cb08e570599821c4b20e` |
| Cross-compiler | Buildroot 2019.05.2 GCC 6.5.0, target `arm-buildroot-linux-gnueabihf`; GCC-wrapper SHA-256 `c04c34d6014b183f08559d95c16c98f47622db9bf11a5007d1b4acc46adc3df3` |
| Linker/sysroot baseline | target binutils 2.31.1, glibc 2.29 and Linux 4.19.69 headers, as frozen by C2b-1 |
| Toolchain freshness | `make -q toolchain` returned zero when run with the preserved private host-tool prefix; nothing was rebuilt or downloaded |
| Disposable tree | `/home/firmware-analysis/slot20_private/c2b2a_20261017/`; 929 MiB after the stopped attempt; private and outside Git |

The fresh tree used the same corrected configuration sequence as C2b-1:

```text
make -C SOURCE O=OUT ARCH=arm \
  KBUILD_DEFCONFIG=na51055_evb_defconfig_nand_squash_release \
  CROSS_COMPILE=TOOLCHAIN/bin/arm-buildroot-linux-gnueabihf- \
  NVT_VOS_DIR=EMPTY_VOS NVT_HDAL_DIR=EMPTY_HDAL defconfig
make -C SOURCE O=OUT ARCH=arm \
  CROSS_COMPILE=TOOLCHAIN/bin/arm-buildroot-linux-gnueabihf- \
  NVT_VOS_DIR=EMPTY_VOS NVT_HDAL_DIR=EMPTY_HDAL prepare
```

`defconfig`/`prepare` passed, and `.config` again had SHA-256 `9a9c7ac6ecddd7900dcce61715c45507d02f0f510f6ea93fc46e33fe2c9ddbf5`. The controlled VOS and HDAL directories remained empty.

## The one compile/link attempt

The default kernel target was invoked exactly once with the same `ARCH`, `CROSS_COMPILE`, VOS and HDAL inputs and `-j1`. Single-threaded operation makes the first failure ordering deterministic. `/usr/bin/time -v` recorded exit status 2 after 6.30 seconds; the build log has 34 lines.

The first fatal diagnostic was:

```text
/usr/bin/ld: scripts/dtc/dtc-parser.tab.o:(.bss+0x10): multiple definition of `yylloc'; scripts/dtc/dtc-lexer.lex.o:(.bss+0x0): first defined here
collect2: error: ld returned 1 exit status
make[3]: *** [scripts/Makefile.host:99: scripts/dtc/dtc] Error 1
```

This is a **host DTC linker blocker**, not an ARM target compiler, shipped-object ABI or kernel linker result:

- `HOSTCC` resolved to Ubuntu GCC 13.3.0 and `/usr/bin/ld` 2.42. GCC reports `-fcommon` disabled.
- Source `scripts/dtc/dtc-lexer.l:41` contains a tentative `YYLTYPE yylloc;` definition. Bison's generated `dtc-parser.tab.c` contains another definition.
- `nm` reports global BSS symbol `yylloc` in both `dtc-lexer.lex.o` and `dtc-parser.tab.o`, matching the linker diagnostic.
- The failure occurred while linking the x86-64 host utility `scripts/dtc/dtc`, before the logged build reached ARM kernel objects. Therefore C2b-2a did not test the target GCC 6.5.0 link, PLL/OTP object compatibility or missing VOS/HDAL behavior.

The evidence is consistent with a legacy DTC source incompatibility with a modern host compiler's no-common default. A remediation was deliberately not applied in this task; its upstream provenance and exact effect must be checked separately before another build.

## Additional bounded observation

The vendor platform Makefile forms `OTP_O_DIR` as `$(MYKERNEL_PATH)/$(O)/...`. With an absolute `O`, it copied four OTP files into a nested `SOURCE/home/.../OUT/...` path rather than the external output directory. This affected only the disposable public-source copy and was not the fatal error. A follow-up must either use a verified relative out-of-tree layout or apply a provenance-recorded build-only correction; it must not use the existing analysis repository as a build tree.

The pre-existing non-fatal `/bin/sh: [: /bin/sh: unexpected operator` warning also recurred. Neither observation changes the DTC failure classification.

## Preserved evidence and limits

Private logs remain under `c2b2a_20261017/logs/`:

| File | SHA-256 |
| --- | --- |
| `build.log` | `f4a916b87b9f2a590391ca4a9934af487aea6514eab1c1b074b08c0b3a26c7a1` |
| `build.time` | `ff3cefcc4c4f1397f567845e88880209ec838aa9075ce6ba97aaced6d0d4f24c` |
| `defconfig.log` | `c627610e186b40b84fac334881387694888e02c7d8a55c1e87021ff51ab458cb` |
| `prepare.log` | `09d9c4521c3adfa4b531ea6a7b681993dcdf28c1bea9426eb8ced29717ee96da` |

The logs and generated files are reproducible evidence for this exact host/input combination, but only one compile attempt was authorized and performed. No second build was used to test a workaround. The result says nothing about the generic kernel's eventual ability to link or boot, still less about compatibility with `IPC_523128M8MP`, lawful redistribution, recovery or installation safety.

## Next bounded task

**C2b-2a-2, only after explicit authorization:** in another fresh disposable tree, verify the minimal host-DTC compatibility change against an authoritative upstream source, correct the vendor absolute-`O` path assumption without touching the pinned archive, and make one more single-threaded generic compile/link attempt. Stop at success or the next exact blocker. C2b-2b rootfs work remains premature.
