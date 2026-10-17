# C2b-1 prerequisite and kernel-prepare preflight

**Scope:** host-only prerequisite acquisition, a Buildroot `toolchain` target, synthetic ABI inspection, and two generic Novatek kernel `defconfig`/`prepare` runs. No complete kernel, root filesystem image, firmware package or camera operation was performed.

**Result:** PASS. The frozen Buildroot 2019.05.2 configuration produced GCC 6.5.0/binutils 2.31.1/glibc 2.29 for `arm-buildroot-linux-gnueabihf`. Two independently extracted Novatek Linux trees then produced byte-identical relevant configuration/prepare outputs. This is a reproducible host preflight, not evidence of a matching-board build, bootable image, redistributability or recovery.

The machine-readable evidence is [`configs/c2b1_build_inputs.json`](../configs/c2b1_build_inputs.json). C2a's frozen sources and seed configuration remain authoritative inputs.

## Private workspace and preservation

- C2b-1 used `/home/firmware-analysis/slot20_private/c2b1_20261017/`, separate from the C2a trees and the existing analysis repositories.
- Public source archives, toolchain objects, logs and synthetic probes remain private/off-Git. The public repository contains only hashes, origins, commands and conclusions.
- The partial analysis repositories retained their pinned HEADs and prior line-oriented status-stream hashes: Linux `1019c2e049f239ba0668ccfd1356e952fde3b29b` / `180c5d627f93f6bf4285a9aa4c934bc29668ae3771d410b76b5a2ccea1341cad`; U-Boot `b23172486e60c2f40729231eae06f48ac3c8d680` / `0b55d09572d9a4f105c788b2dafd27473aaa658c52a551a17c7a561eb3716fc7`.

## Host prerequisites

Passwordless `sudo` was unavailable, so the four requested Ubuntu packages were downloaded from the signed Noble repositories, SHA-256 recorded, and extracted with `dpkg-deb` into a disposable private prefix. The WSL system package database was not modified.

| Package | Verified runtime | `.deb` SHA-256 |
|---|---|---|
| `bison` `2:3.8.2+dfsg-1ubuntu0.24.04.1` | GNU Bison 3.8.2 | `9d75084d1293f68f3c1a2ee677dea5baa4e010bac2d4c455d8e23177e97aa353` |
| `flex` `2.6.4-8.2build1` | flex 2.6.4 | `c5604f55827b50e3f568b4731b7799f86b147454c867be02bc141d9d8ce561ff` |
| `cpio` `2.15+dfsg-1ubuntu2.1` | GNU cpio 2.15 | `fbac731755302d218d785b4c391530e7773527f553e24946f9580636a47641b2` |
| `unzip` `6.0-28ubuntu4.1` | Info-ZIP UnZip 6.00 | `a505b9d491386167bd8e14e3383315a4a7d6539e4406745901ccf009a7988271` |

Buildroot's dependency target passed after adding a private `python` compatibility link to the existing Python 3.12.3. The extracted Bison expects `/usr/bin/m4`; the controlled kernel environment instead sets `M4` to Buildroot's private host-m4. A synthetic grammar probe passed before the kernel runs.

## Toolchain provenance and compatibility

The toolchain came from the frozen Buildroot archive/configuration, not the rejected legacy Linaro URL. Buildroot downloaded and hash-checked eleven public source archives. The complete filename/origin/digest list is in the machine-readable manifest; principal inputs are:

| Input | SHA-256 |
|---|---|
| GCC 6.5.0 | `7ef1796ce497e89479183702635b14bb7a46b53249209a5e0f999bebf4740945` |
| binutils 2.31.1 | `5d20086ecf5752cc7d9134246e9588fa201740d540f7eb84d795b1f7a93bca86` |
| glibc commit `2d3fefd7ce64ac1015701c96916fffacc073a877` | `bd9fa9932c374b5256a976b543992c20de23338d08879df70a0a2502d17e671d` |
| Linux headers 4.19.69 | `c091760b520a4e4a4c7034a8329cc2689a0ea3f81a377b694ed196d623e2d987` |

Buildroot 2019.05.2's host-m4 1.4.18 failed against modern glibc because `SIGSTKSZ` is no longer a preprocessor constant. The exact official Buildroot backport from commit `5a9504831f3fa1ef3be334036c93da30150fde55` was added only to the disposable Buildroot tree; its SHA-256 is `a659db8cd9cad78130f3732ecd369fdfdcdbf0c1cf23821b1c44ea8661e65c4e`. After that bounded compatibility fix, `make toolchain` completed and `make -q toolchain` reported up to date.

Verified outputs:

- GCC: `arm-buildroot-linux-gnueabihf-gcc.br_real (Buildroot 2019.05.2) 6.5.0`.
- linker: GNU binutils 2.31.1.
- target/sysroot: `arm-buildroot-linux-gnueabihf`, glibc, loader family `ld-linux-armhf`.
- synthetic object: ELF32, little-endian ARM, EABI5, Cortex-A9/ARMv7 application profile, ARM ISA, VFPv3 and `Tag_ABI_VFP_args: VFP registers`. It was inspected, not executed.
- compiler wrapper/real/linker SHA-256 values are recorded in the manifest. The frozen configuration enables NEON, but the trivial probe does not itself prove Advanced SIMD code generation.

This is acceptable provenance for the historical compatibility preflight. GCC 6.5.0, glibc 2.29 and Buildroot 2019.05.2 remain obsolete and are not a production security baseline.

## Two clean kernel configuration/prepare runs

Each run was freshly extracted from the C2a Linux archive and used separate output and empty VOS/HDAL directories. The correct bounded command shape is:

```sh
make -C KERNEL O=KERNEL_OUT \
  ARCH=arm \
  KBUILD_DEFCONFIG=na51055_evb_defconfig_nand_squash_release \
  CROSS_COMPILE=PRIVATE_TOOLCHAIN/bin/arm-buildroot-linux-gnueabihf- \
  NVT_VOS_DIR=EMPTY_VOS NVT_HDAL_DIR=EMPTY_HDAL \
  defconfig

make -C KERNEL O=KERNEL_OUT \
  ARCH=arm \
  CROSS_COMPILE=PRIVATE_TOOLCHAIN/bin/arm-buildroot-linux-gnueabihf- \
  NVT_VOS_DIR=EMPTY_VOS NVT_HDAL_DIR=EMPTY_HDAL \
  prepare
```

The vendor config filename contains `_defconfig_` but does not end in Kbuild's recognized `*_defconfig` suffix. Calling the filename directly as a make target is invalid; `KBUILD_DEFCONFIG=<filename> defconfig` is required.

Both runs completed and matched byte-for-byte for all compared outputs:

| Output | SHA-256 |
|---|---|
| `.config` | `9a9c7ac6ecddd7900dcce61715c45507d02f0f510f6ea93fc46e33fe2c9ddbf5` |
| `include/generated/autoconf.h` | `87a324966409e85dea170649fb1eb378a1600b978dd793b8c7dc909bda149d44` |
| `include/config/auto.conf` | `6c194c08512026956cea95654177b953bd82f8c462b17a2583c206dfef83ad59` |
| `include/generated/utsrelease.h` | `a48bac31c3e0cb9b939e1275caa5baca812f6da1d6655ebc01536b195739288e` |
| `include/generated/nvtversion.h` | `7520d5cf5cfad5012ce2be5e295ad22e107af2cc98846d4b02434511c08bd0c0` |
| `include/generated/bounds.h` | `56b3a4056c7588bd1306802bd061be2fa0d8337ee414bd26563edd88ca8c9be8` |
| `include/generated/asm-offsets.h` | `2609ba2c2b8e40db128ed886cad3ae17bddc6d4fa03fc7a0d57e3db617e0c58e` |

Each `prepare` added the same four source-tree symlinks: `arch/arm/plat-novatek/{include/plat,plat}` point to the NA51055 platform directories, while `drivers/soc/nvt/nvt_hdal/{hdal,vos}` point to that run's controlled empty directories. Both external directories remained empty. This proves the prepare mechanism, not the availability of missing HDAL/VOS sources.

Both runs also emitted the same non-fatal `/bin/sh: [: unexpected operator` warning while generating `nvtversion.h`. The output matched, but the legacy shell expression remains a portability issue to correct or contain before a broader build.

## Limits and next gate

- Buildroot created only its toolchain/sysroot and internal target staging; its `images` directory is absent.
- Kernel `prepare` compiled only required probes such as `bounds.s` and `asm-offsets.s`; no `vmlinux`, `zImage`, root filesystem, firmware or update package exists.
- The C1 blockers remain unchanged: binary-only PLL and enabled OTP objects, unresolved redistribution terms, absent VOS/HDAL/media sources, and no matching-board DTS/defconfig.
- Nothing here proves hardware compatibility, Ethernet, camera functions, boot, rollback or recovery. No camera was discovered, contacted or modified.

The next separately authorized task is **C2b-2a**: attempt one generic-kernel compile/link pass in a fresh private tree, inventory the first exact source/blob/link blocker, and stop without rootfs or firmware assembly. Use High reasoning and checkpoint before the compile.
