# Offline boot, update and recovery analysis

**Checkpoint:** 2026-10-16 (atomic tasks A1–A3). **Evidence class:** static package/source inspection only. No camera, flash dump, UART console or matching spare has been accessed.

This document keeps observations from the matching Reolink package separate from capabilities found in generic Novatek source code. A generic BSP feature is not proof that the shipped RLC-811A binary enables it or that the board exposes the required pins, port or recovery trigger.

## Confirmed from the matching package

- Target package SHA-256: `f62a68d21397da9bb2aadefc66edfdbe91f35270b2cc64857a9082ed17e6a2e9`.
- The package contains `loader`, `fdt`, `uboot`, `kernel`, `rootfs` and `app`, in that order. It therefore updates early boot components as well as Linux filesystems.
- The package does not contain the declared `fdt.restore`, `uenv`, `para`, `sp`, `ext_para` or `download` partitions. It is not a complete flash backup.
- The package FDT declares a 128 MiB NAND map and the partition table recorded in `docs/HARDWARE.md`. Those values are static firmware declarations, not live chip measurements.
- `rootfs` and `app` are UBI/UBIFS images. The package's kernel identifies itself as Linux 4.19.91 and its FDT is compatible with `novatek,na51055`.
- Nothing in the package establishes a working A/B layout, a factory fallback image, a rescue button, or a safe use for the 59 MiB `download` partition.

### A1 — actual packaged U-Boot inventory

The input is the preserved private `firmware_workspace/analysis/sections/uboot.bin` extracted from the matching package. It remains ignored and is not committed. The table records only bounded metadata and structure checks; it does not claim that the installed camera contains identical bytes or that any recovery mechanism works.

| Item | Verified evidence | Classification / limit |
|---|---|---|
| Artifact identity | Size 572,344 bytes (`0x8bbb8`); SHA-256 `f2d4fe401c28d5be792b6e559ffc7cc14627ad69ed0f873672fbeca2cda7dc6b` | Direct file metadata/hash from the private section |
| Format | File offset `0x0` is little-endian word `0xea0003fe`, not ELF magic or legacy-uImage magic; it decodes as an ARM branch | Flat/raw executable section at its start; absence of a wrapper at offset zero does not describe every embedded data structure |
| Architecture | ARM-mode little-endian decoding yields a coherent vector table; compiled strings `arch=arm` and `cpu=armv7` occur at file offsets `0x6c1df` and `0x6c1e8`. The U-Boot 2019.04 version string begins at `0x7abeb` | Direct static decode plus binary self-identification; not a live CPU query |
| Linked base and reset entry | With linked base `0x06000000`, the first instruction branches to `0x06001000`. Vector literals at file offsets `0x20..0x38` contain addresses `0x06000060..0x060002a0`, and relocation offsets occupy the same `0x06000000` address window | Strongly corroborated static link-address inference; not proof of the Boot ROM's runtime load action |
| Runtime-image region | File offsets `0x00000..0x7ffff`, length `0x80000` (524,288 bytes) | Strong structural boundary inference from the relocation-shaped tail and its address coverage; the raw file has no section headers |
| Relocation region | File offsets `0x80000..0x8bbb7`, length `0xbbb8` (48,056 bytes), exactly 6,007 eight-byte `<r_offset,r_info>` records. `r_offset` is monotonic from `0x06000020` through `0x0607ffb4`; every `r_info` is `0x17` (ARM relocation type 23, `R_ARM_RELATIVE`) | Direct structural parse; naming it the stripped `.rel.dyn` content is an ARM ABI/U-Boot layout inference because this raw file has no ELF section headers |

Bounded verification commands used for A1 (run from the repository root; they read only the private section and never execute target code):

```powershell
$image = 'firmware_workspace\analysis\sections\uboot.bin'
Get-Item -LiteralPath $image | Select-Object Length
Get-FileHash -Algorithm SHA256 -LiteralPath $image
```

```bash
# From WSL at the repository root; the helper caps the image at 8 MiB and this request at 64 bytes.
ANALYZER_PY=/home/firmware-analysis/slot20_private/venv-capstone-5.0.9/bin/python
IMAGE=firmware_workspace/analysis/sections/uboot.bin
"$ANALYZER_PY" firmware_workspace/disasm_arm_ranges.py "$IMAGE" 0x06000000 --bytes 0x40
```

```bash
ANALYZER_PY=/home/firmware-analysis/slot20_private/venv-capstone-5.0.9/bin/python
IMAGE=firmware_workspace/analysis/sections/uboot.bin
"$ANALYZER_PY" -c '
from pathlib import Path
import hashlib, struct, sys
p = Path(sys.argv[1])
assert p.stat().st_size <= 8 * 1024 * 1024
b = p.read_bytes()
w = struct.unpack_from("<I", b, 0)[0]
imm = w & 0xffffff
if imm & (1 << 23):
    imm -= 1 << 24
tail = b[0x80000:]
assert len(tail) % 8 == 0
records = [struct.unpack_from("<II", tail, i) for i in range(0, len(tail), 8)]
print(len(b), hashlib.sha256(b).hexdigest(), hex(w), hex(0x06000008 + (imm << 2)))
print(hex(b.find(b"arch=arm")), hex(b.find(b"cpu=armv7")), hex(b.find(b"U-Boot 2019.04")))
print(hex(len(tail)), len(records), hex(records[0][0]), hex(records[-1][0]))
print(sorted({info for _, info in records}), all(records[i][0] <= records[i+1][0] for i in range(len(records)-1)))
' "$IMAGE"
```

The structural command caps input at 8 MiB, decodes only the first branch, locates three fixed identity strings, reads the `0xbbb8`-byte tail as little-endian pairs, asserts an 8-byte record boundary, counts records, checks monotonic offsets, and prints the complete `r_info` set. These focused checks replace no broader bootloader analysis and disclose no proprietary payload bytes.

### A2 — actual command and recovery surface

The preserved command-table probe found one contiguous 61-entry run at file offsets `0x7f5ac..0x7fc57` (end-exclusive `0x7fc58`), with 28-byte entries. Entry offsets and handler addresses below come directly from that run. “Present” means a named handler is compiled and registered in this package binary; it does **not** prove the production board exposes the interface, initializes the required hardware, accepts an image, or can recover from a broken bootloader.

| Area | Classification | Matching-binary evidence | Limit / unresolved point |
|---|---|---|---|
| Normal booting | **Present (compiled); runtime uncertain** | `bootm` entry `0x7f600`, handler `0x0600efb4`; `nboot` `0x7f910` / `0x060147a0`; `nvt_boot` `0x7f948` / `0x0600d600`. Exact strings: `bootcmd=nvt_boot` at `0x6c14a`, `bootdelay=0` at `0x6c15b` | Establishes commands/default strings; A3 documents the static normal flow below, but no live boot was observed |
| UART / serial console | **Present clues; serial loaders absent; hardware uncertain** | Exact strings `console=ttyS0,115200` at `0x6c0cd`, `baudrate=115200` at `0x6c167`, and `Hit ctrl + c` at `0x6b4ce`; registered `nvt_uart_disable` at `0x7fa44`, handler `0x0600ef34`. No registered `serial`, `loadx`, `loady`, or `loads` command | Does not establish pinout, voltage, pad mux, fuse state, readable output, or a usable interrupt window. Never invoke the UART-disable command |
| Ethernet / DHCP / TFTP | **Present (compiled); hardware uncertain** | `bootp` `0x7f61c` / `0x06014c84`; `dhcp` `0x7f6a8` / `0x06014c90`; `ping` `0x7fa98` / `0x06014cdc`; `tftpboot` `0x7fb5c` / `0x06014c9c`. No separate registered `eth` diagnostic command | Network stack commands are present, but MAC/PHY initialization, link, board wiring, RAM destinations, and image acceptance are untested |
| NAND / UBI | **Present (compiled); device geometry uncertain** | `chpart` at `0x7f638`; `mtdparts` `0x7f8bc`; `nand` `0x7f8f4`; `nboot` `0x7f910`; `ubi` `0x7fb94`; `ubifsload`, `ubifsls`, `ubifsmount`, `ubifsumount` at `0x7fbb0..0x7fc04` | Command presence does not identify the physical NAND, ECC/OOB scheme, bad blocks, safe partition bounds, or restore correctness |
| Firmware updating | **Present (compiled); authentication and rollback uncertain** | `crc32` at `0x7f68c`; `md5sum` `0x7f84c`; `nvt_update_all` `0x7fa60`, handler `0x0600d9a0`; `upgrade` `0x7fc20`, handler `0x0601ebe8`. Security/OTP-related commands include `nvt_encrypt` at `0x7f964`, `nvt_secure_en` at `0x7fa28`, and `nvt_write_key` at `0x7fa7c` | Checksums and security-command presence do not prove signed-update enforcement, fuse state, power-fail safety, or rollback. OTP/security commands are dangerous and must not be invoked |
| Alternate-load recovery candidates | **Present as commands; recovery unverified** | MMC/FAT surface includes `fatinfo`/`fatload` through `fatwrite` at `0x7f718..0x7f7c0`, plus `mmc` `0x7f884` and `mmcinfo` `0x7f8a0`. Network-load commands plus `bootm` could form a RAM-boot path | SD/MMC slot wiring, boot-source straps, Ethernet readiness, safe RAM layout, console control, and secure-boot policy are unknown. These are leads, not recovery methods |
| USB / serial-download recovery | **Absent in the inspected command table** | No registered `usb`, `dfu`, `ums`, `fastboot`, `loadx`, `loady`, or `loads` command among all 61 entries | This excludes those command names from the parsed table, not all dormant code or SoC Boot ROM capabilities |
| Automatic rollback / named rescue | **Absent as inspected names/strings; overall capability uncertain** | No registered `saveenv`; exact lower-case ASCII searches over the complete bounded image found no `bootcount`, `bootlimit`, `altbootcmd`, `upgrade_available`, `rollback`, `fallback`, `rescue`, `recovery`, or `fdt.restore` token | Absence of these names is not formal proof that no unnamed state machine exists. No A/B or independent recovery path is demonstrated |

Bounded A2 verification commands (run from WSL at the repository root; neither executes target code):

```bash
ANALYZER_PY=/home/firmware-analysis/slot20_private/venv-capstone-5.0.9/bin/python
IMAGE=firmware_workspace/analysis/sections/uboot.bin
"$ANALYZER_PY" firmware_workspace/probe_uboot_tables.py "$IMAGE" --base 0x06000000
```

```bash
ANALYZER_PY=/home/firmware-analysis/slot20_private/venv-capstone-5.0.9/bin/python
IMAGE=firmware_workspace/analysis/sections/uboot.bin
"$ANALYZER_PY" -c '
from pathlib import Path
import sys
p = Path(sys.argv[1])
assert p.stat().st_size <= 8 * 1024 * 1024
b = p.read_bytes()
present = (b"bootcmd=nvt_boot", b"bootdelay=0", b"baudrate=115200", b"console=ttyS0,115200", b"Hit ctrl + c")
absent = (b"bootcount", b"bootlimit", b"altbootcmd", b"upgrade_available", b"rollback", b"fallback", b"rescue", b"recovery", b"fdt.restore")
for value in present + absent:
    offset = b.find(value)
    print(value.decode(), hex(offset) if offset >= 0 else -1)
' "$IMAGE"
```

The probe caps input at 8 MiB and reports only plausible command records whose pointers remain inside the image. The targeted string command scans the known 572,344-byte input for the listed exact tokens; `-1` supports only “absent as that exact string,” not absence of all equivalent code.

### A3 — normal `nvt_boot` control flow

This trace follows the actual packaged binary's registered `nvt_boot` handler. Runtime addresses below use the A1 linked base `0x06000000`; for addresses inside the first `0x80000` bytes, the corresponding file offset is the address minus that base. Names such as `env_get`, `env_set` and `run_command` describe behavior inferred from their call sites and arguments because this is a stripped flat image.

| Stage | Verified static evidence in the matching binary | Boundary / unresolved behavior |
|---|---|---|
| Command entry | The A2 command-table entry at file offset `0x7f948` points `nvt_boot` to `0x0600d600` (file offset `0xd600`). The handler clears bounded local command/argument buffers, reads `bootargs` via `0x06016764` at `0x0600d694`, and preserves that string for later extension. | `bootcmd=nvt_boot` and `bootdelay=0` make this the compiled default path, not proof that the installed camera ran it. |
| FDT preparation before `nvt_boot` | The only direct `bl 0x06003c90` found by a complete instruction scan is at `0x060012c8` (file offset `0x12c8`), immediately after `r0=0`. In this memory-source branch, `0x06003c90` obtains a loader-supplied FDT pointer through global `0x060802bc`, checks the header, derives the big-endian total size, and copies exactly that size to the buffer referenced by global `0x060802c8`. | The code that originally assigns the loader-temporary pointer is not yet identified. The direct-call result does not exclude an indirect caller. Thus the FDT is verified as already prepared when `nvt_boot` begins, but its normal flash provenance is unresolved. |
| Compiled FDT NAND branch | When `0x06003c90` is called with a nonzero argument, it allocates at most `0x80000` bytes, constructs an initial `nand read` from raw flash offset `0x00040000` for `0x20000` bytes, rejects an invalid header or total size over `0x80000`, and if necessary reads the remainder beginning at `0x00060000`. It then copies the exact FDT to the `0x060802c8` destination. | This branch is **present but not established as the normal path**: the only direct caller found passes zero. The raw offsets must not be treated as a partition map, recovery procedure, or hardware-verified location. |
| Firmware-selection wrapper | At `0x0600d6d4`, the handler calls `0x0600d550`. That wrapper passes the prepared FDT (`[0x060802c8]`) to `0x0600c984`, which looks up `/nvt_memory_cfg/rtos` and reads its `reg` property. Parse failure, a zero second returned cell, or global `0x060802d0 == 1` selects `0x0600cacc`; otherwise it selects the alternate function `0x0600ce5c`. | The exact meanings of the two `reg` cells and `0x060802d0` are not proved. A3 follows `0x0600cacc`, the branch that visibly reads the named `linux` NAND partition; `0x0600ce5c` is deliberately left unresolved. |
| Linux load | `0x0600cacc` first queries `0x060043c4`. Its NAND branch builds and executes `nand read 0x5800000 linux 0x40`, reads the big-endian legacy-image data-size word at RAM `0x05800000 + 0x0c`, adds the `0x40`-byte header, and issues a second `nand read 0x5800000 linux <derived-total>`. It records address `0x05800000` and the derived size in globals `0x060802d4`/`0x060802d8`. | A nonzero result from `0x060043c4` selects another path involving address `0x03800000`; its boot-source semantics are unknown. A local selector is initialized to zero, so the visible `0x80` preload/decrypt alternative is not selected within this function in this build. The two command return values are not checked here. |
| Optional packaged-kernel transform | The loader then calls `0x0600c618` with source `0x05800000` and workspace/destination `0x01100000`. Preserved bounded analysis identifies the conditional `BCL1` (`0x314c4342`) path, its 8 MiB bound, decompression workspace and legacy-image reconstruction. A negative return is diagnosed as an unzip failure. | This is static code behavior, not proof that every packaged kernel takes the compressed branch. The precise accepted-image/authentication policy inside standard `bootm` remains outside this narrow trace. |
| Boot arguments and limits | After the loader wrapper returns, `0x0600d718..0x0600d784` appends `bootts=%lu,%lu resume_addr=0x%08lx user_debug=0xff ` to the saved boot arguments and writes `bootargs` via `0x06016514`. The same setter installs `fdt_high`, `bootm_size` and `bootm_mapsize` as `0x07000000`, and `bootm_low` as zero (`0x0600d7a8..0x0600d84c`). | The two timestamps and resume address are runtime globals; their values and hardware meaning were not inferred. Environment persistence is A4, not part of A3. |
| Final handoff | `0x0600d850..0x0600d8c0` constructs `bootm 5800000 - <fdt-address>`, where the FDT address is read from `[0x060802c8]`; the literal `-` omits a ramdisk. At `0x0600d920`, that buffer is passed with flags zero to the command executor at `0x0601d7b4`. | This verifies command construction and dispatch only. It does not prove that `bootm` succeeded, Linux reached its entry point, or the physical board used these bytes. |

Two error-flow details remain important. First, `0x0600d550` discards the selected loader's return value and returns zero, so the caller's `"boot firmware init failed"` branch does not receive a negative result from `0x0600cacc` through this wrapper. Second, `nvt_boot` also returns zero after invoking the constructed command without checking the command executor's return. These observations are direct static control flow, not a live failure test.

Bounded A3 reproduction commands (read-only; they disassemble bytes but never execute the ARM image):

```bash
ANALYZER_PY=/home/firmware-analysis/slot20_private/venv-capstone-5.0.9/bin/python
IMAGE=firmware_workspace/analysis/sections/uboot.bin
DISASM=firmware_workspace/disasm_arm_ranges.py
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x110 "$IMAGE" 0x06001270
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x3c0 "$IMAGE" 0x06003c90
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x148 "$IMAGE" 0x0600c984
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x220 "$IMAGE" 0x0600cacc
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0xb0  "$IMAGE" 0x0600d550
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x340 "$IMAGE" 0x0600d600
```

The direct-call check is intentionally capped at 8 MiB and prints only call-site addresses:

```bash
"$ANALYZER_PY" -c '
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
import sys
p = Path(sys.argv[1]); assert p.stat().st_size <= 8 * 1024 * 1024
m = Cs(CS_ARCH_ARM, CS_MODE_ARM)
for insn in m.disasm(p.read_bytes(), 0x06000000):
    if insn.mnemonic in ("bl", "blx") and insn.op_str == "#0x6003c90":
        print(hex(insn.address), insn.mnemonic, insn.op_str)
' "$IMAGE"
```

These ranges cover the early FDT call, both FDT source branches, the FDT property selector, the normal named-partition Linux loader, the firmware-selection wrapper, and the complete `nvt_boot` handler. They intentionally do not trace the alternate loader, environment backend, updater, or recovery mechanisms assigned to later atomic tasks.

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
2. **Preserved shipped U-Boot with UART and/or TFTP.** The matching binary registers console/network clues and TFTP-related commands, but physical console access, reliable interruption, Ethernet initialization and actual command usability are not proven.
3. **Protected recovery Linux selected by the bootloader.** Plausible only if immutable selection logic, protected storage, watchdog/reset handling and a power-fail-safe boot-state store can be demonstrated.
4. **A/B kernel and root filesystem.** Desirable, but space, partition ownership, boot selection and health marking are unresolved. The `download` partition cannot be assigned to this design until its factory role is understood.
5. **Vendor web update or reset button.** Neither is independent recovery from an unbootable system and neither counts toward the recovery gate.

## Evidence still required before hardware work

- Identify the physical NAND part, page/OOB/erase geometry, ECC scheme and bad-block behavior.
- Observe the documented normal boot sequence on matching spare hardware; determine environment persistence/partition ownership, practical boot interruption, watchdog/reset-reason handling and whether secure boot/eFuses are active. The static command and normal-flow paths are now inventoried, but hardware usability remains unverified.
- Determine whether a ROM downloader, UART recovery, USB device recovery, TFTP recovery or programmer can restore every required region on matching spare hardware.
- Acquire and verify a complete per-device backup including OOB/bad-block information and unique factory/calibration/identity regions.
- Explain the purpose and restore semantics of `fdt.restore`, `uenv`, `para`, `sp`, `ext_para` and `download` without repurposing them.
- Demonstrate recovery and bad-boot rollback on matching spare hardware before requesting any production-camera action.

Until those points are resolved, every recovery route above remains a hypothesis and no image is eligible for persistent installation.
