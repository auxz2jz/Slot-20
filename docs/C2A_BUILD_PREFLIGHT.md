# C2a build-input freeze and configuration preflight

**Scope:** host-only source acquisition, configuration normalization and bounded `prepare` probing. No kernel, root filesystem, firmware image or update package was built. No recovered target program was executed and no camera was accessed.

**Result:** The public source inputs and Buildroot compatibility configuration are frozen and reproducible in two clean private trees. Kernel configuration/`prepare` is blocked before completion by missing host inputs, principally the unmaterialized ARM cross-compiler and `bison`. This is a precise preflight result, not evidence of a bootable or redistributable image.

The machine-readable record is [`configs/c2a_build_inputs.json`](../configs/c2a_build_inputs.json). The normalized compatibility seed is [`configs/c2a_buildroot_2019.05.2_defconfig`](../configs/c2a_buildroot_2019.05.2_defconfig).

## Private workspace and preservation

- New private WSL root: `/home/firmware-analysis/slot20_private/c2a_20261017/`.
- Independent trees: `run-a/{kernel,uboot,buildroot}` and `run-b/{kernel,uboot,buildroot}`. Both came from the same verified cache archives; no Git metadata or private Reolink material was copied into them.
- The existing Windows analysis repositories were not reset, populated or used as download targets. Their HEAD values remained the C1 pins. Their bounded `git status --porcelain=v1 -uno` stream hashes were identical before and after C2a: kernel `180c5d627f93f6bf4285a9aa4c934bc29668ae3771d410b76b5a2ccea1341cad`; U-Boot `0b55d09572d9a4f105c788b2dafd27473aaa658c52a551a17c7a561eb3716fc7`.
- The private directory is not a GitHub backup. It contains only public source/preflight material here, but remains outside the public repository by design.

## Frozen public inputs

| Input | Identity | Frozen archive SHA-256 / size | Clean-tree check |
|---|---|---|---|
| Novatek Linux | commit `1019c2e049f239ba0668ccfd1356e952fde3b29b` | `66aca4fee2663f60ad68f9d3e9500a1475cefa825517cb08e570599821c4b20e`, 163,963,602 bytes | Each run has 62,148 regular files and 34 symlinks, matching the 62,182 tracked-path count from C1. |
| Novatek U-Boot | commit `b23172486e60c2f40729231eae06f48ac3c8d680` | `3f9b2f9b3d475ccbd28f482e904d08ff9bca6db3094994c494865e96243ca3c8`, 21,033,080 bytes | Each run has 15,815 regular files and 24 symlinks, matching the 15,839 tracked-path count from C1. |
| Buildroot | release `2019.05.2` | `7c0ea9ffc170e19735aed281592fe766e4b698bb139eae851f4f98f024a776b5`, 6,351,403 bytes | Each run has 11,082 regular files and 40 symlinks. |

All three archives passed gzip integrity checking. The digests freeze the bytes retrieved over HTTPS for this project and reproduce both extractions; they are not a substitute for an upstream cryptographic signature or independent source-authenticity review.

## Buildroot/toolchain compatibility baseline

The compatibility configuration is intentionally toolchain-only evidence. It selects:

| Setting | Normalized value |
|---|---|
| Architecture/CPU lead | ARMv7-A / Cortex-A9 |
| ABI and floating point | EABI hard-float, VFPv3, NEON, ARM instruction mode |
| C library | glibc |
| Kernel headers | Buildroot 4.19 selection, resolving to 4.19.69 |
| Compiler | GCC 6.5.0 |
| Binutils | 2.31.1 |

The Cortex-A9 setting is supported by the generic BSP's Cortex-A9 SCU reference and is compatible with the static ARMv7-A evidence. It is not proof of the exact CPU implementation in the matching Reolink camera.

The configuration normalized to SHA-256 `2d4d71e0cfc3badd846387a96dff56191654f8834b411a666e460f923b4f875f` in both clean trees. It reports `BR2_GCC_TARGET_CPU="cortex-a9"`, `BR2_GCC_TARGET_FPU="vfpv3"` and `BR2_GCC_TARGET_FLOAT_ABI="hard"`. The seed defconfig SHA-256 is `83d056aa42ad4557f5d6dd481be63c60526c5d01cfdce90040d4ec3150718b9d`.

Buildroot 2019.05.2 has a legacy first-run issue on this GNU Make 4.3 host: direct `defconfig` invocation stopped because `output/.br-external.mk` did not yet exist. Explicitly running its own `support/scripts/br2-external -m -o output/.br-external.mk` first made the configuration deterministic in both trees. This workaround does not download packages or construct a compiler.

## Kernel configuration/prepare probe

The bounded command shape was:

```sh
make -C KERNEL O=KERNEL_OUT \
  ARCH=arm CROSS_COMPILE=arm-buildroot-linux-gnueabihf- \
  NVT_VOS_DIR=EMPTY_VOS NVT_HDAL_DIR=EMPTY_HDAL \
  na51055_evb_defconfig_nand_squash_release
```

The controlled VOS and HDAL paths existed and were empty. Both clean runs stopped before `.config` completion because:

1. `arm-buildroot-linux-gnueabihf-gcc` is not installed; and
2. the kernel's Kconfig generation invokes `bison`, which is not installed.

After run-path normalization, the selected failure lines from both logs have the same SHA-256, `5e10375dfc0a4ae42955d37393a3e07c1984c84d652845037519d5f04bf7a07c`. Consequently `make prepare` was not entered and the Novatek platform symlink recipe was not exercised. `flex`, `cpio` and `unzip` are also absent and would block later kernel/Buildroot stages. WSL otherwise provided Ubuntu 24.04, GNU Make 4.3, host GCC 13.3.0 and binutils 2.42.

An old Linaro GCC 6.5 URL was checked but now returned an HTML response rather than an authenticated toolchain archive. It was rejected. Building Buildroot's internal compiler or installing host packages would be a separate, larger operation and was not started in C2a.

## Remaining blockers and implications

- The compiler configuration is reproduced, but the compiler executable and sysroot are not materialized or digest-verified. No compiler/object compatibility claim is made.
- The C1 licensing blockers remain: binary-only PLL code is required by the generic clock configuration; OTP is binary-only when enabled; no separate redistribution grant or corresponding source was established.
- VOS/HDAL/media/ISP sources and a matching-board kernel DTS/defconfig remain absent. Empty directories are only controlled preflight placeholders and provide no functionality.
- Buildroot 2019.05.2, Linux 4.19.91 and GCC 6.5.0 are legacy compatibility inputs with security debt, not a production support recommendation.
- No compile, link, emulation, rootfs construction, device boot, recovery test or hardware validation occurred.

## Next bounded task

**C2b-1: materialize preflight prerequisites only.** In a fresh checkpointed session, obtain digest-authenticated host `bison`/`flex` prerequisites and either build the frozen Buildroot GCC 6.5.0 toolchain or obtain a provenance-acceptable matching compiler. Then repeat kernel defconfig/`prepare` in two disposable clean trees and stop before kernel compilation or rootfs assembly.

This task passes only if both kernel configuration/`prepare` runs complete with identical relevant generated configuration, or if one new exact blocker is reproduced and recorded. It must not package the private Reolink FDT, build a root filesystem, assemble firmware or access hardware.
