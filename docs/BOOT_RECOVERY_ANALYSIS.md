# Offline boot, update and recovery analysis

**Checkpoint:** 2026-10-13. **Evidence class:** static package/source inspection only. No camera, flash dump, UART console or matching spare has been accessed.

This document keeps observations from the matching Reolink package separate from capabilities found in generic Novatek source code. A generic BSP feature is not proof that the shipped RLC-811A binary enables it or that the board exposes the required pins, port or recovery trigger.

## Confirmed from the matching package

- Target package SHA-256: `f62a68d21397da9bb2aadefc66edfdbe91f35270b2cc64857a9082ed17e6a2e9`.
- The package contains `loader`, `fdt`, `uboot`, `kernel`, `rootfs` and `app`, in that order. It therefore updates early boot components as well as Linux filesystems.
- The package does not contain the declared `fdt.restore`, `uenv`, `para`, `sp`, `ext_para` or `download` partitions. It is not a complete flash backup.
- The package FDT declares a 128 MiB NAND map and the partition table recorded in `docs/HARDWARE.md`. Those values are static firmware declarations, not live chip measurements.
- `rootfs` and `app` are UBI/UBIFS images. The package's kernel identifies itself as Linux 4.19.91 and its FDT is compatible with `novatek,na51055`.
- Nothing in the package establishes a working A/B layout, a factory fallback image, a rescue button, or a safe use for the 59 MiB `download` partition.

## Confirmed from official Novatek source

Novatek's public repositories contain branches matching the versions observed in the package:

| Component | Branch | Inspected commit |
|---|---|---|
| Linux | [`oss/linux-4.19.91`](https://github.com/Novatek-OSS/kernel/tree/oss/linux-4.19.91) | `1019c2e049f239ba0668ccfd1356e952fde3b29b` |
| U-Boot | [`oss/u-boot-2019.04`](https://github.com/Novatek-OSS/u-boot/tree/oss/u-boot-2019.04) | `b23172486e60c2f40729231eae06f48ac3c8d680` |

The specific generic configurations inspected were `arch/arm/configs/na51055_evb_defconfig_nand_squash_release` and `configs/nvt-na51055_nand_defconfig`. They are reproducibility pointers, not claims that Reolink built its binaries with those files unchanged.

Source inspection confirms generic NA51055 support for ARMv7, SPI NAND, MTD/UBI/UBIFS, Ethernet MAC/PHY, UART, USB, GPIO, clocks and a watchdog. The generic NAND kernel configuration enables the NA51055 Ethernet and PHY drivers as modules, DHCP boot configuration support, SPI NAND hardware ECC, UBI/UBIFS, SquashFS and the watchdog module. This materially improves the feasibility of a maintenance-only Linux prototype, but board pinmux, PHY wiring and the exact RLC-811A configuration remain unverified.

The generic NA51055 NAND U-Boot configuration provides the Novatek firmware-update path plus NAND, DHCP, TFTP download and ping commands. Its published all-in-one updater:

- bounds components against declared partition sizes;
- accounts for NAND bad blocks in its NAND write helpers;
- validates the NVTPACK container with its additive package checksum;
- applies per-component checksum checks where configured;
- reads partitions back after writing and compares an MD5 of the reconstructed package buffer;
- can contain RSA/SHA-256 secure-boot paths behind separate build options.

The inspected generic NAND defconfig does **not** enable FIT images, RSA/Novatek crypto commands, U-Boot boot-count rollback, DFU, USB mass storage or USB commands. The source's secure-boot code being present does not prove it is enabled on the RLC-811A. Package checksums and post-write MD5 detect accidental corruption; they do not authenticate an update source.

The published updater erases and rewrites named partitions in place. Read-back verification happens after destructive writes and is not a rollback mechanism. The generic source therefore must not be treated as a safe updater for the first custom installation.

The BSP is also not yet a proven fully source-buildable replacement: the inspected Linux tree contains shipped binary objects for NA51055 PLL/OTP support. Their necessity, source availability, licensing and redistribution constraints must be resolved before a reproducible independent image can be claimed.

## Important mismatch warning

The generic U-Boot header conditionally places a NAND environment at `0x002c0000`; the matching Reolink FDT declares `uenv` at `0x00240000`. Generic offsets, default environment, commands and partition names must never be copied onto this camera. The actual package U-Boot and exact board FDT are the only current board-specific static evidence.

## Recovery candidates, not proven mechanisms

1. **SoC Boot ROM or external NAND programmer.** Potentially independent of Linux and U-Boot, but no RLC-811A pinout, electrical procedure, compatible tool or spare-hardware restore has been demonstrated.
2. **Preserved shipped U-Boot with UART and/or TFTP.** The generic BSP supports TFTP, but console access, interruption, Ethernet initialization and usable commands in the Reolink build are not proven.
3. **Protected recovery Linux selected by the bootloader.** Plausible only if immutable selection logic, protected storage, watchdog/reset handling and a power-fail-safe boot-state store can be demonstrated.
4. **A/B kernel and root filesystem.** Desirable, but space, partition ownership, boot selection and health marking are unresolved. The `download` partition cannot be assigned to this design until its factory role is understood.
5. **Vendor web update or reset button.** Neither is independent recovery from an unbootable system and neither counts toward the recovery gate.

## Evidence still required before hardware work

- Identify the physical NAND part, page/OOB/erase geometry, ECC scheme and bad-block behavior.
- Determine the real boot sequence, actual U-Boot command set/environment, boot interruption method, watchdog/reset reason handling and whether secure boot/eFuses are active.
- Determine whether a ROM downloader, UART recovery, USB device recovery, TFTP recovery or programmer can restore every required region on matching spare hardware.
- Acquire and verify a complete per-device backup including OOB/bad-block information and unique factory/calibration/identity regions.
- Explain the purpose and restore semantics of `fdt.restore`, `uenv`, `para`, `sp`, `ext_para` and `download` without repurposing them.
- Demonstrate recovery and bad-boot rollback on matching spare hardware before requesting any production-camera action.

Until those points are resolved, every recovery route above remains a hypothesis and no image is eligible for persistent installation.
