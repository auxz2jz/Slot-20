# NA51055 BSP build-input audit

**Scope:** Atomic task C1, host-side source and ABI inspection only. No firmware was built, no recovered target binary was executed, and no camera or camera storage was accessed.

**Decision:** The pinned Novatek trees are useful bring-up references, but they are not yet a complete, independently redistributable or reproducible build input for `IPC_523128M8MP`. A bounded configuration/toolchain preflight is safe; producing or distributing a target image is premature.

## Pinned inputs and role

| Input | Pinned evidence | Required role | C1 conclusion |
|---|---|---|---|
| Novatek Linux | `Novatek-OSS/kernel`, branch `oss/linux-4.19.91`, commit `1019c2e049f239ba0668ccfd1356e952fde3b29b`; Makefile reports 4.19.91 | Kernel and NA51055 platform drivers | Required bring-up base. The repository contains generic NA51055 support, not a complete Reolink board build. |
| Novatek U-Boot | `Novatek-OSS/u-boot`, branch `oss/u-boot-2019.04`, commit `b23172486e60c2f40729231eae06f48ac3c8d680`; Makefile reports 2019.04 | Host image tools and reference source | Do not replace the matching Reolink bootloader. The generic `nvt-na51055_nand_defconfig`/`nvt-na51055-evb.dts` do not reproduce the packaged Reolink configuration. |
| Matching package FDT | Private `fdt.bin`, 17,399 bytes, SHA-256 `62a2b0f96262702f7ec97c6df2423a4abc8ed47e881db1248ceab66e763c9a8c` | Board/partition reference | The public kernel tree has 1,834 tracked `arch/arm/boot/dts` paths and no Novatek/NA51055 match. A lawful, reviewable matching-board DTS source is missing. Keep the recovered FDT private. |
| Root-filesystem builder | No Buildroot source, release hash, defconfig, board overlay or package lock is present | Toolchain and minimal userspace | Missing. Buildroot 2019.05.2 is only a compatibility lead from object metadata, not yet a pinned project input or long-term security choice. |
| Board integration | No `IPC_523128M8MP` kernel defconfig/DTS or public board overlay is present | Pinmux, clocks, Ethernet PHY, NAND geometry and reserved-memory integration | Missing. The generic EVB configuration must not be represented as the Reolink board configuration. |

The existing local upstream directories are partial analysis clones whose working trees intentionally do not contain every file. C2 must use a separate, clean materialized checkout or verified source archive, not repair or repurpose those analysis directories.

## Architecture, ABI and toolchain evidence

| Property | Verified evidence | Build requirement |
|---|---|---|
| CPU/ISA | Kernel defconfig selects `CONFIG_ARM`, `CONFIG_CPU_V7`, VFPv3 and NEON. The U-Boot config selects 32-bit ARM, ARMv7-A. | Little-endian 32-bit ARMv7-A compiler/binutils. Kernel code is ARM mode in the inspected configs; target userspace may use ARM/Thumb-2 as supported by the selected toolchain. |
| ABI | The preserved matching rootfs BusyBox is ELF32 little-endian ARM, EABI5, interpreter `/lib/ld-linux-armhf.so.3`, with hard-float VFP register arguments and ARMv7-A/VFPv3/Thumb-2 attributes. This was inspected statically with `file`/`readelf`, not executed. | Use an `arm-linux-gnueabihf`-class EABI5 hard-float userspace ABI when compatibility with recovered userspace is required. A wholly independent rootfs may choose its libc, but its loader, libraries and programs must use one consistent ABI. |
| Kernel ABI controls | Generic NAND/SquashFS defconfig enables AEABI, VFP, VFPv3 and NEON and disables OABI compatibility. | Preserve AEABI and the NA51055 CPU/FPU assumptions during the first compile preflight. Kernel ABI does not itself select a userspace libc. |
| Compiler provenance | Required `pll.o_shipped` and OTP objects contain `GCC: (Buildroot 2019.05.2) 6.5.0` (one OTP variant includes Buildroot suffix `-00003-g3ccc130`). All inspected objects are ARM ELF relocatables with EABI5 flags; their flags do not independently assert hard-float. | Safest compatibility baseline is GNU GCC 6.5.0/binutils from a reproducibly pinned Buildroot 2019.05.2 configuration. This is a lead, not proof that another compiler cannot link the objects. Test before changing compiler generation. |
| Host tools | Kernel `Documentation/process/changes.rst` declares minima including GCC 4.6, GNU make 3.81, binutils 2.20, flex 2.5.35, bison 2.0, OpenSSL/libcrypto 1.0.0, Perl 5 and `bc` 1.06.95. | Pin a Linux host/container and actual package versions above these historical minima. Add Git, Bash, Python, cpio, patch, rsync, file, device-tree compiler and the Buildroot host prerequisites to the build manifest. Historical minima do not guarantee the vendor tree works on a modern host. |

No exact compiler command line, Buildroot defconfig, sysroot hash or binutils version has been recovered. Reproducibility therefore remains unproved.

## Source and binary dependency inventory

| Capability/input | Availability | Evidence and consequence |
|---|---|---|
| ARM platform, reset, preload, SRAM control | Source present | NA51055 platform C/header sources are tracked. Platform Makefile creates source-tree symlinks during `prepare`, which is non-hermetic and must be contained in a disposable checkout. |
| Ethernet MAC/MDIO/PHY | Source present | NA51055 DWC Ethernet QoS, MDIO and PHY sources are tracked. Generic config builds the MAC and PHY as modules. This is compile-time evidence only; matching-board PHY address, reset GPIO, clocks and live link remain unverified. |
| SPI NAND, MTD, UBI/UBIFS, SquashFS | Source present | Generic NAND/SquashFS config enables these subsystems. It does not establish the actual NAND chip, ECC/OOB policy, bad-block handling or safe write ownership. |
| UART, GPIO/pinctrl, MMC, watchdog | Source present | Corresponding NA51055 drivers are tracked. Presence and compilation do not prove matching-board wiring or operation. |
| Clock/PLL | **Binary-only required input** | With `CONFIG_COMMON_CLK_NA51055=y`, Kbuild links `drivers/clk/novatek/na51055/pll.o_shipped` (Git blob `196153bd8231ae38297e09ac04ba80daf1a2a539`, 25,892 bytes). No corresponding PLL source was found. A fully source-built redistributable kernel is blocked until this is lawfully sourced or independently replaced and validated. |
| OTP | **Binary-only under generic config** | `CONFIG_NVT_OTP_SUPPORT=y` links `drivers/soc/nvt/otp/na51055/otp_protected.o_shipped` (blob `2138f2bf9f14a22c35e88b39e681626c7c68c6be`, 19,764 bytes). The `no_l2` and `no_tracer` paths carry the same blob. Determine whether a minimal maintenance kernel can disable OTP without affecting boot; do not assume it can. |
| Older platform OTP objects | Prebuilt, linkage uncertain/not selected by inspected Kbuild | `arch/arm/plat-novatek/plat-na51055/otp_protected.o_shipped` (blob `96a8a3364c2e2d623c3d3613bb02a9e12cd46f30`, 45,772 bytes) and `.obj` (blob `47d633d0c9a736b1a03b3d031b37fa95a1e3f462`, 14,868 bytes) are tracked, but the inspected NA51055 platform Makefile does not link them. Keep them in the provenance inventory. |
| VOS/HDAL/media/ISP | Source absent from the public kernel tree | Only `drivers/soc/nvt/nvt_hdal/{Kconfig,Makefile,README}` are tracked. The README locates actual code under SDK path `sdk/code/hdal`. The platform `prepare` recipe derives symlink targets from external `NVT_VOS_DIR` and `NVT_HDAL_DIR` even when built-in HDAL is disabled. Empty controlled directories may be sufficient for a configuration preflight, but this must be tested; camera video/audio/ISP functionality remains blocked without lawful sources or replacements. |
| U-Boot logo object | Prebuilt but not required by inspected generic config | `board/novatek/common/nvt_logo/jpg.o_shipped` (blob `716a7d137f05d23f1ba91675e2befbdeed23ea03`, 35,836 bytes) is tracked. The common Makefile builds `jpg.o` from present `jpg.c`, and the generic NA51055 config does not enable the logo. |
| Reolink applications/libraries | Proprietary/private only | They are analysis references, not inputs to independent firmware and must not be committed or redistributed. Sensor/ISP/video/zoom support cannot be claimed from them. |

## Licensing and redistribution boundary

- The pinned kernel reports `GPL-2.0 WITH Linux-syscall-note`; individual files may carry other SPDX expressions. The U-Boot tree describes the overall project as GPLv2, with many GPL-2.0-or-later files and per-file exceptions or dual licenses. Redistribution requires a generated per-file/package license inventory and satisfaction of the applicable source and notice obligations.
- The HDAL README says GPLv2, but the referenced HDAL/VOS source directories are absent. That statement does not provide the missing code or establish licenses for every omitted SDK component.
- No corresponding source or separate redistribution grant was located for the required PLL and OTP ELF objects. Public availability inside a source repository is not by itself evidence that a combined kernel can lawfully be redistributed without corresponding source. Treat public distribution of a linked image as **blocked pending license review or source replacement**. This is an engineering risk assessment, not legal advice.
- The matching Reolink FDT, firmware contents, libraries and other vendor artifacts remain private. Do not publish a derived board source or combined image until provenance and redistribution permission are resolved.
- A future Buildroot build must retain `legal-info`, package source archives, patches, license texts, source-offer material where required, and hashes for every downloaded input. Private keys and proprietary artifacts remain outside that record.

## Reproducibility blockers

1. No pinned Buildroot archive/commit, defconfig, rootfs package selection, board overlay, sysroot, toolchain archive or container/host manifest exists.
2. GCC 6.5.0/Buildroot 2019.05.2 is inferred from ELF comments, not from a preserved toolchain or exact build configuration. That release is obsolete and unsuitable as an unreviewed production userspace.
3. The public kernel tree requires binary PLL code and, under the generic config, binary OTP code. Exact compiler/linker compatibility has not been tested.
4. Kernel `prepare` mutates the source checkout with symlinks and depends on external `NVT_VOS_DIR`/`NVT_HDAL_DIR`; the referenced SDK sources are absent.
5. No NA51055 DTS is present in the pinned kernel tree, and the generic U-Boot EVB DTS/config is not the Reolink board. The private package FDT is evidence, not a public source input.
6. Matching-board clocks, PHY/reset wiring, pinmux, reserved-memory layout, NAND ECC/OOB geometry and driver/module selections have not been converted into a reviewed independent board configuration.
7. There has been no clean compile/link test, reproducible second build, artifact comparison, emulator test or hardware boot. C1 does not change those facts.
8. Kernel 4.19.91 and Buildroot 2019.05.2 are historical bring-up choices with substantial security-maintenance debt. A newer long-term baseline can be evaluated only after basic NA51055 support is reproducibly understood.

## Safest next bounded step

Split C2 so its first unit is **C2a: build-input freeze and configuration preflight**:

1. In a new disposable, private Linux build directory, materialize complete clean source trees at the two commits above; record archive/commit hashes without modifying the preserved analysis clones.
2. Pin a Buildroot 2019.05.2 compatibility configuration that targets ARMv7-A, EABI5 and hard-float with GCC 6.5.0, plus a digest-pinned host environment. Keep it explicitly separate from any eventual supported/secure production userspace decision.
3. Add empty, controlled VOS/HDAL directories and pass their absolute paths only to test `olddefconfig`/`prepare` behavior with HDAL built-in disabled. Record every source-tree mutation. Do not import private SDK code.
4. Run configuration and compiler/object-compatibility checks only. If a local compile is attempted, keep all artifacts private and unpackageable; do not combine them with the Reolink FDT, make an update bundle or call the result device-ready.
5. Produce a machine-readable input manifest and a short pass/fail report. Stop before C2b rootfs/image assembly.

C2a passes when a second clean directory can reproduce the same configuration/preflight result from pinned inputs, or when it records one exact blocker with commands and logs. It does not prove a bootable kernel, working Ethernet, redistributable firmware or recovery.

## Bounded verification commands

Run from the repository root; these inspect Git metadata or private files and do not execute ARM code:

```powershell
git -C firmware_workspace/upstream/novatek-kernel-4.19.91 rev-parse HEAD
git -C firmware_workspace/upstream/novatek-uboot-2019.04 rev-parse HEAD
git -C firmware_workspace/upstream/novatek-kernel-4.19.91 show HEAD:arch/arm/configs/na51055_evb_defconfig_nand_squash_release
git -C firmware_workspace/upstream/novatek-kernel-4.19.91 show HEAD:arch/arm/plat-novatek/Makefile
git -C firmware_workspace/upstream/novatek-kernel-4.19.91 show HEAD:drivers/clk/novatek/Makefile
git -C firmware_workspace/upstream/novatek-kernel-4.19.91 show HEAD:drivers/soc/nvt/otp/Makefile
git -C firmware_workspace/upstream/novatek-kernel-4.19.91 ls-tree -r HEAD | Select-String '\.(o_shipped|obj)$'
git -C firmware_workspace/upstream/novatek-kernel-4.19.91 ls-tree -r --name-only HEAD arch/arm/boot/dts | Select-String 'na51055|novatek|nvt|98520'
```

Use `file` and `readelf -h -A` only on private copies of the preserved BusyBox and shipped objects. Avoid `ls-tree -l` in the partial clones unless network retrieval is intentionally allowed: requesting missing blob sizes can trigger lazy fetches.
