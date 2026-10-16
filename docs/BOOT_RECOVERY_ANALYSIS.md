# Offline boot, update and recovery analysis

**Checkpoint:** 2026-10-16 (atomic tasks A1–A5). **Evidence class:** static package/source inspection only. No camera, flash dump, UART console or matching spare has been accessed.

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

### A4 — environment, boot arguments and flash ownership

The matching binary does not use its declared `uenv` partition as a persistent U-Boot environment. Its environment linker list is exactly one 20-byte entry at file offsets `0x7fe0c..0x7fe1f`: the name points to `"nowhere"`, the load and save slots are null, and the initializer is `0x060425f0`. That initializer points U-Boot at the compiled default blob at linked address `0x0606c0b8` and marks it invalid/default, matching the behavior of the pinned generic `env/nowhere.c`. This is stronger evidence than the `uenv` label or generic configuration options.

| Environment stage | Confirmed matching-binary evidence | Consequence / limit |
|---|---|---|
| Compiled defaults | File offsets `0x6c0b8..0x6c23e` form a 391-byte, 15-entry default blob. Relevant entries are `bootargs=earlyprintk console=ttyS0,115200 rootwait nprofile_irq_duration=on root=ubi0:rootfs rootfstype=ubifs ubi.fm_autoconvert=1 init=/linuxrc ` at `0x6c0b8`, `bootcmd=nvt_boot` at `0x6c14a`, `bootdelay=0` at `0x6c15b`, and `baudrate=115200` at `0x6c167`. | Defaults are actual packaged-binary data, not proof of values read from installed flash. |
| Persistence backend | The sole `nowhere` entry and `0x060425f0` initializer provide defaults only. No `saveenv` token or registered command exists in the bounded image. | U-Boot environment changes are volatile in this binary. This does not prove that the earlier loader or Linux never uses the separate `uenv` bytes for some other purpose. |
| FDT-derived partition variables | Early boot calls `0x0600acc8`. At `0x0600ad58..0x0600ad74` it sets `mtdids=nand0=spi_nand.0`; at `0x0600ad9c` it begins `mtdparts=spi_nand.0:`; and at `0x0600b434..0x0600b440` it stores the generated partition list in the in-memory environment. Format strings include `uenv` at file offset `0x66778` and translate the FDT `partition_kernel` role to the runtime name `linux` at `0x6678c`. | A generated `uenv` MTD name does not imply an environment storage driver. The exact generated string is runtime data and was not observed on hardware. |
| Rootfs argument | The actual helper at `0x06005750` walks `/nand` child nodes until `partition_rootfs`; in this FDT it counts rootfs as MTD index 6. The caller at `0x0600b3d4..0x0600b40c` appends the compiled literal ` ubi.mtd=%d ro `, yielding the static expected addition `ubi.mtd=6 ro`. | The index is confirmed by actual code plus this package FDT, but not by a live kernel command line. The `ro` literal applies to UBI attachment; filesystem/write behavior was not tested. |
| Bootargs ownership | The package FDT `/chosen/bootargs` value is only a single space. Early boot gets the compiled U-Boot `bootargs`, adds the FDT-derived rootfs argument, and writes it back at `0x06001314..0x06001354`; A3 then appends `bootts`, `resume_addr` and `user_debug` before `bootm`. | The effective command line is assembled in volatile U-Boot state. The FDT does not own the base command line in this package. Runtime timestamp/resume values remain unknown. |

The package FDT declares the following 128 MiB map. “In package” describes update payload coverage only; it is not evidence that installed bytes match or that an omitted region is unused.

| FDT region | Range | In package | Matching evidence and ownership classification |
|---|---:|---:|---|
| `loader` | `0x00000000..0x0003ffff` | Yes | Early-boot component. Not environment storage; must remain protected. |
| `fdt` | `0x00040000..0x0007ffff` | Yes | Board configuration. A3 found a compiled raw-NAND FDT reader at this offset, but the confirmed direct initialization path consumes a loader-supplied memory FDT. |
| `fdt.restore` | `0x00080000..0x000bffff` | No | Declared but absent from the update package; no restore-selection behavior is proved. Preserve as unknown. |
| `uboot` | `0x000c0000..0x0023ffff` | Yes | Packaged bootloader region. Not environment storage. |
| `uenv` | `0x00240000..0x0027ffff` | No | Declared and emitted into runtime `mtdparts`, but the matching U-Boot registers only the `nowhere` backend. Owner/content/restore semantics remain unknown; preserve. |
| `kernel` | `0x00280000..0x006fffff` | Yes | Packaged kernel region; actual U-Boot translates `partition_kernel` to MTD name `linux` and A3 reads that name. This alias is not a second partition. |
| `rootfs` | `0x00700000..0x026fffff` | Yes | Packaged UBI/UBIFS rootfs; actual static boot construction selects MTD index 6 and UBI volume `rootfs`. |
| `app` | `0x02700000..0x03bfffff` | Yes | Packaged UBI/UBIFS application filesystem. No environment role found. |
| `para` | `0x03c00000..0x043fffff` | No | Prior bounded analysis found a reset/update path touching part of this region. Exact contents and ownership remain unknown; preserve the whole partition. |
| `sp` | `0x04400000..0x0447ffff` | No | No environment ownership established. Possible factory/service data remain unclassified; preserve. |
| `ext_para` | `0x04480000..0x044fffff` | No | No environment ownership established. Preserve as unknown. |
| `download` | `0x04500000..0x07ffffff` | No | Prior static evidence ties its base to a staged `upgrade all` input. It is not free space and not a persistent environment. Exact lifecycle remains for A5. |
| `all` | `0x00000000..0x07ffffff` | No | Whole-device alias in the FDT, not additional storage. Never treat it as an independently writable partition. |

#### Matching binary versus pinned generic BSP

| Topic | Matching Reolink evidence | Generic Novatek evidence at commit `b23172486e60c2f40729231eae06f48ac3c8d680` | Safe conclusion |
|---|---|---|---|
| Environment backend | One `nowhere` driver; null load/save; defaults-only initializer; no `saveenv` command | `include/configs/nvt-na51055-evb.h` conditionally selects NAND/NOR/MMC storage, otherwise `CONFIG_ENV_IS_NOWHERE`; `env/nowhere.c` supplies only the default environment | The generic header describes build choices, not the shipped selection. The actual binary is volatile/default-only. |
| NAND environment address | No matching-binary NAND environment driver; package FDT reserves `uenv` at `0x00240000` for `0x40000` bytes | When `_NVT_UBOOT_ENV_IN_STORG_SUPPORT_NAND_` is defined, the generic header uses offset `0x002c0000`, size `0x20000`, range `0x40000` | The generic NAND range `0x002c0000..0x002fffff` lies inside this package's `kernel` partition. Copying it would risk kernel corruption and is forbidden. |
| Save command | No registered `saveenv` in the 61-entry matching command table | The published `configs/nvt-na51055_nand_defconfig` says `CONFIG_CMD_SAVEENV=y` even though storage selection also depends on legacy/generated macros | This public defconfig is not the Reolink build configuration and cannot override actual-binary evidence. |
| Base bootargs | Actual default is the UBIFS string above; FDT `/chosen/bootargs` contains only one space; actual code adds `ubi.mtd=6 ro` | The generic header contains the same base string under `_NVT_ROOTFS_TYPE_NAND_UBI_` and generic code derives `ubi.mtd` from the FDT | The common source explains the mechanism, while the matching binary/FDT establish this package's selected values. |
| Partition naming | FDT node/label `kernel`; runtime MTD name `linux`. FDT includes `uenv` even though persistence is disabled | Generic translation maps `partition_kernel` to `EMBTYPE_LINUX` and `partition_uenv` to `EMBTYPE_UENV` | Runtime MTD labels, update-component names and environment backends are separate concepts; none establishes ownership alone. |

Focused A4 reproduction commands (read-only; private outputs remain ignored):

```bash
ANALYZER_PY=/home/firmware-analysis/slot20_private/venv-capstone-5.0.9/bin/python
IMAGE=firmware_workspace/analysis/sections/uboot.bin
FDT=firmware_workspace/analysis/sections/fdt.bin
DISASM=firmware_workspace/disasm_arm_ranges.py
od -Ax -tx4 -j 0x7fe0c -N 0x14 "$IMAGE"
strings -a -t x "$IMAGE" | grep -E 'nowhere|bootargs=|bootcmd=|bootdelay=|baudrate='
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x60  "$IMAGE" 0x0604190c
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x20  "$IMAGE" 0x060425f0
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x1a0 "$IMAGE" 0x06005750
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x110 "$IMAGE" 0x0600acc8
"$ANALYZER_PY" "$DISASM" --base 0x06000000 --bytes 0x140 "$IMAGE" 0x0600b334
dtc -q -I dtb -O dts "$FDT"
```

The generic comparison used only the pinned public Git objects and focused paths `include/configs/nvt-na51055-evb.h`, `configs/nvt-na51055_nand_defconfig`, `env/nowhere.c`, `board/novatek/common/nvt_ivot_fw_update_utils.c`, and `board/novatek/common/nvt_ivot_soc_utils.c`. No generic offset is promoted to a camera instruction.

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

A4 confirms that the generic optional NAND environment range would overlap the matching package's kernel partition, while the matching binary actually selects the volatile `nowhere` backend. Generic offsets, default environment, commands and partition names must never be copied onto this camera. The actual package U-Boot and exact board FDT are the only current board-specific static evidence.

## A5 — independent-recovery candidate matrix

Every row remains **unverified on hardware**. “Linux-independent” means the route might remain available when the experimental kernel/rootfs or web service fails; it does not mean the route can repair a damaged loader/U-Boot. Only a demonstrated route that remains outside the component under test can satisfy the independent-recovery gate for that component.

Evidence labels in this table are deliberate: **actual** means static evidence from the matching package U-Boot/FDT, **generic** means capability in the pinned Novatek BSP only, and **hypothesis** means no matching-package implementation has been established.

| Candidate | Existing evidence and possible independence boundary | Unknowns and principal risks | Required matching-spare hardware | Minimum eventual verification |
|---|---|---|---|---|
| UART into preserved U-Boot | **Actual:** `console=ttyS0,115200` at U-Boot offset `0x6c0cd`, `baudrate=115200` at `0x6c167`, `Hit ctrl + c` at `0x6b4ce`, and registered `nvt_uart_disable` at `0x7fa44`. `bootdelay=0` makes interruption timing uncertain; no `loadx`/`loady`/`loads` command is registered. If accessible, this could be Linux-independent but remains loader/U-Boot-dependent. | Pinout, I/O voltage, pad mux, output enable, input acceptance and a reliable interrupt window are unknown. Wrong voltage can damage the board; unsafe commands can erase flash or program OTP. Corrupted early boot would remove this route. | Matching sacrificial camera/board; board documentation or traced pads; high-impedance scope/logic analyzer; correctly level-shifted, current-limited UART adapter; isolated power and capture setup. | With separate explicit approval, identify voltage and observe receive-only output first, then repeat non-writing console interruption across cold boots. Prove only bounded RAM inspection/loading before any storage test. To qualify for Linux recovery, restore a deliberately damaged disposable Linux test region after a verified full backup; it still would not prove recovery from damaged U-Boot. |
| U-Boot TFTP/Ethernet | **Actual:** registered `bootp`, `dhcp`, `ping`, `tftpboot` and `bootm` entries at `0x7f61c`, `0x7f6a8`, `0x7fa98`, `0x7fb5c` and `0x7f600`. **Generic:** NA51055 Ethernet/PHY and network-loader support. This could be Linux-independent but depends on loader/U-Boot, RAM, board Ethernet initialization and a way to issue commands. | MAC/PHY wiring and clocks, link initialization, MAC-address source, command reachability, safe RAM windows and image-authentication policy are unknown. Network exposure, a wrong load address, or following a load with a destructive NAND command are material risks. | Matching spare; proven UART control or other non-persistent command trigger; isolated lab switch; bounded DHCP/TFTP server; packet capture; controlled power. | First demonstrate link and a bounded TFTP-to-RAM transfer on an isolated network, verify the received hash, and perform a reversible RAM-only boot if policy permits. Only after the backup/approval gates, demonstrate restoration of a disposable Linux test region and repeat after cold boots. This route cannot qualify for loader/U-Boot loss. |
| U-Boot MMC/FAT | **Actual:** registered `fatinfo`/`fatload` through `fatwrite` at `0x7f718..0x7f7c0`, plus `mmc` and `mmcinfo` at `0x7f884` and `0x7f8a0`. No matching evidence shows an exposed slot or direct ROM boot. Manual FAT loading could be Linux-independent but remains U-Boot-dependent; a Boot-ROM MMC path is only a hypothesis. | Controller pin mux, accessible pads/slot, voltage, media format, boot straps, command usability, safe RAM destinations and secure-boot policy are unknown. Wiring or strap errors can damage hardware or change the boot source; write-capable commands are unsafe. | Matching spare; verified pinout or socket/adapter; known-good removable media; logic analyzer; UART observation/control; isolated power. | Start with card detection and bounded read-only FAT-to-RAM plus hash comparison, then a reversible RAM-only boot. Claim an early-stage independent path only if a documented ROM/strap path is separately demonstrated when U-Boot is unavailable; command-table presence cannot establish that. |
| SoC Boot ROM downloader | **Hypothesis:** no matching-package command or board trigger establishes a ROM downloader. Absence of U-Boot `usb`/DFU/UMS/fastboot commands does not exclude immutable ROM functionality. If accessible and authorized by the device security state, this could be independent of Linux, U-Boot and NAND contents. | Protocol, transport pins, entry straps/timing, accepted loader format, authentication/eFuse policy, RAM access and flash support are all unknown. Incorrect straps/electrical assumptions or an untrusted vendor tool could damage hardware or overwrite unique data. | Matching spare; authoritative SoC/board documentation or a lawfully obtained known-good tool/protocol; verified USB/UART/strap access; logic analyzer; controlled reset/power; protected backup storage. | Begin with non-writing ROM identification and, if supported, a harmless bounded RAM upload/readback. Then acquire repeatable full raw reads including OOB/bad-block data. Final proof would restore a controlled early-boot failure on the spare after the full-backup and explicit-approval gates; until then this is not a recovery method. |
| External SPI-NAND programming | **Actual:** the FDT declares SPI NAND and a 128 MiB map; **generic:** the BSP has SPI-NAND hardware-ECC support. The exact installed chip and raw geometry have not been observed. A correctly implemented off-board/in-circuit programmer could be independent of all on-flash software. | Chip identity/package, voltage, bus contention, in-circuit feasibility, page/OOB/erase geometry, ECC layout, bad-block mapping, OTP and device-unique calibration/identity ownership are unknown. This is the most invasive route: soldering, raw-layout or cloned-identity errors can permanently damage the spare or destroy factory data. | Matching spare; microscope and validated rework or isolated in-circuit fixture; exact chip datasheet; programmer proven to preserve raw data/OOB/bad-block semantics; voltage/current protection; encrypted storage for private dumps. | Read chip ID, obtain at least two identical complete raw reads including OOB and a bad-block map, and independently validate the backup parser. After explicit approval, restore a controlled change to the same spare or sacrificial replacement and prove boot. Recovery from an intentionally unavailable U-Boot would be the decisive independent test. |
| Existing reset/staged-update path | **Actual:** a recovered boot-time path associates GPIO 43 (`reset_key`) with erase of `0x03c00000..0x03efffff` and `upgrade all 0x1800000 0x4500000`; the latter is the declared `download` base. Package/update code has bounds, checksums and post-write MD5 evidence, but no proved authentication, atomicity or rollback. This might be Linux-independent but remains loader/U-Boot- and staged-image-dependent. | Physical GPIO mapping/semantics, trigger timing, staged image provenance/completeness, overwritten components, secure policy and power-loss behavior are unknown. The erase overlaps part of `para`; treating `download` as free or assuming a reset repairs boot could destroy state or strand the board. | Matching spare; complete verified flash/OOB backup; UART capture; known-good staged image provenance; controlled power interruption; non-destructive GPIO observation before any trigger test. | First map the button/GPIO and staged contents without writing. Under later explicit approval, exercise the path on the spare, record every changed region, interrupt power at defined phases, and prove repeatable restoration. It does not count as recovery until those tests pass, and cannot recover a damaged loader/U-Boot. |
| Proposed protected rescue Linux or A/B slots | **Hypothesis:** no implemented rescue system is shown. **Actual negative scope:** the binary has no exact `bootcount`, `bootlimit`, `altbootcmd`, `upgrade_available`, `rollback`, `fallback`, `rescue`, `recovery` or `fdt.restore` token; environment persistence is `nowhere`. The FDT declares `fdt.restore`, but its contents/selector are unknown; `download` is already tied to staging. | No verified spare capacity, immutable selector, protected image, authenticated update policy, watchdog/reset-reason flow, persistent health state, atomic switching or rollback target exists. Repartitioning unknown factory regions or relying on the experimental Linux/web service would defeat independence. | Matching spare; full verified backup; validated independent rescue route from another row; UART/power control; fault-injection power switch; storage-trace/test instrumentation as feasible. | Offline simulation must precede hardware. On a spare and only after separate approval, prove bad image, failed first boot, lost network/service and interrupted-write cases repeatedly revert to a known-good protected target. Then demonstrate rescue while the experimental Linux/web stack is unusable. It remains U-Boot-dependent unless an earlier immutable selector is proved. |

Vendor web update is intentionally absent as a candidate: if the experimental OS or web service must run, it is an update interface rather than independent recovery. Likewise, a reset button is not recovery proof; only the bounded staged-update evidence above is established.

### A5 decision

No candidate presently satisfies the project recovery gate. The shortest plausible Linux-independent routes are preserved U-Boot plus UART/TFTP or MMC/FAT, but each still needs physical-interface and repeatable matching-spare proof and cannot repair U-Boot. Boot ROM and external NAND programming have the strongest potential independence boundary, but also the largest evidence gap or hardware risk. A protected rescue/A-B design cannot be selected until partition ownership, an immutable selector and a separate proven rescue route are established.

A5 was verified by cross-checking each matrix claim against the bounded A2 command/string offsets, A3 normal-boot dependencies, A4 environment/partition evidence, the pinned generic-source limits, and the project recovery-gate checklist. No firmware was re-extracted or executed, no private artifact was published, and no hardware was accessed.

## Evidence still required before hardware work

- Identify the physical NAND part, page/OOB/erase geometry, ECC scheme and bad-block behavior.
- Observe the documented normal boot sequence on matching spare hardware; verify the static volatile-environment result, resolve ownership of omitted partitions, and determine practical boot interruption, watchdog/reset-reason handling and whether secure boot/eFuses are active. Static command, normal-flow and environment paths are now inventoried, but hardware usability remains unverified.
- Determine whether a ROM downloader, UART recovery, USB device recovery, TFTP recovery or programmer can restore every required region on matching spare hardware.
- Acquire and verify a complete per-device backup including OOB/bad-block information and unique factory/calibration/identity regions.
- Explain the purpose and restore semantics of `fdt.restore`, `uenv`, `para`, `sp`, `ext_para` and `download` without repurposing them.
- Demonstrate recovery and bad-boot rollback on matching spare hardware before requesting any production-camera action.

Until those points are resolved, every recovery route above remains a hypothesis and no image is eligible for persistent installation.
