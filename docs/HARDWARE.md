# Confirmed RLC-811A target and static firmware leads

Source: user-provided Reolink app device-info screenshot and offline inspection of the matching firmware. Camera has not been accessed.

## Development role and safety status

This owner-confirmed unit is the project's **primary development reference**.
It is an older camera but remains in active security service, so it is not a
sacrificial test or independent-recovery platform. Previously supplied
screenshots may be used for the offline H0 evidence baseline. Any new live
query, connection, diagnostic, reboot, configuration change, actuation,
opening, electrical work or storage operation still requires separate explicit
approval. Firmware installation and destructive testing remain prohibited
until the device-specific full-backup gate and independent recovery proof on a
matching spare are satisfied. See `HARDWARE_DEVELOPMENT_PLAN.md`.

## Confirmed identification
- Model: RLC-811A
- Hardware: **IPC_523128M8MP**
- Installed version: **v3.1.0.1643_2402219117**
- Matching reference file: `IPC_523128M8MP.1643_2402219117.RLC-811A.IMX415.8MP.AF.REOLINK.pak`
- SHA-256: `f62a68d21397da9bb2aadefc66edfdbe91f35270b2cc64857a9082ed17e6a2e9`
- Device Tree compatible: `novatek,na51055`
- Firmware kernel image: Linux 4.19.91
- Device Tree declares 112 MiB Linux-visible memory and 128 MiB NAND address space. **Not independent physical chip measurements.**
- Sony IMX415: suggested by firmware filename and sensor driver; **not live-confirmed**.

## Preliminary physical PCB evidence

Ten owner-supplied private photographs across both PCB sides now add a
preliminary physical inventory. The source images remain ignored and outside
public Git history.

- Main processor marking: **`NT98523MBG`** (photo-observed and
  owner-confirmed).
- PCB marking **`N25C06 V100`** and date **`2020-08-13`** are directly legible
  in the second photo set.
- DRAM marking appears to be Nanya **`NT5CC128M16JR-EK`**, a 2-Gbit x16 DDR3L
  part according to Nanya; the full suffix still needs a sharper macro.
- A `JWT 12.000C22` can is consistent with a 12 MHz reference oscillator.
- The physical NAND chip is **not identified**. The Device Tree's 128 MiB NAND
  address space is not a chip identity or physical measurement.
- The leading UART candidate is a row of approximately four exposed round pads
  immediately right of the right-hand upper mounting hole and above-right of
  the SoC on the processor/Ethernet side. It could instead be another factory
  test interface. No pad has been labeled TX, RX, GND or supply and no voltage
  is known.

See `PCB_HARDWARE_INVENTORY_AND_UART.md` for the evidence classes, candidate
map, firmware/BSP comparison, Boot ROM research boundary and required next
photographs. No camera connection, probing, UART activity, reboot or NAND
operation occurred.

## Device Tree flash partitions (static; never use as blind write offsets)

| Partition | Start | Declared size | In update payload? |
|---|---:|---:|---|
| loader | 0x00000000 | 0.25 MiB | yes |
| fdt | 0x00040000 | 0.25 MiB | yes |
| fdt.restore | 0x00080000 | 0.25 MiB | no |
| uboot | 0x000c0000 | 1.5 MiB | yes |
| uenv | 0x00240000 | 0.25 MiB | no |
| kernel | 0x00280000 | 4.5 MiB | yes |
| rootfs | 0x00700000 | 32 MiB | yes |
| app | 0x02700000 | 21 MiB | yes |
| para | 0x03c00000 | 8 MiB | no |
| sp | 0x04400000 | 0.5 MiB | no |
| ext_para | 0x04480000 | 0.5 MiB | no |
| download | 0x04500000 | 59 MiB | no |

The update file is **not** a full flash backup. Preserve user/device-specific partitions and bad-block information in any eventual backup design.

## Extracted firmware observations
- Payload sections: loader, FDT, U-Boot, kernel, rootfs, app; rootfs and app use UBI/UBIFS.
- Rootfs: 760 discovered paths, 13,513 CRC-validated UBIFS nodes, 8 incomplete files.
- App: 275 discovered paths, 7,707 CRC-validated UBIFS nodes, 2 incomplete files.
- A custom offline parser recovered 1,035 directory entries overall; it is *not* a complete journal-replayed forensic mount or verified flash image.
- Independent native-Linux inspection with `ubi-reader` 0.8.16 reports 2,048-byte minimum I/O, 131,072-byte PEBs and 126,976-byte LEBs. It found 197 rootfs and 124 app data blocks with no unknown blocks, matching the custom parser.
- The independent trees contain exactly the same 760 rootfs and 275 app paths after excluding each extraction root. `ubi-reader` recovered 299 rootfs and 255 app regular files; the custom parser hashed 291 and 253, so the 8/2 difference exactly matches its recorded incomplete reconstructions. A deterministic sample of 32 regular files per volume matched SHA-256 in all 64 cases.
- Startup: `/init`, `/etc/inittab`, `/etc/init.d/rcS`, `S10_SysInit2`, `start_app`; exact `start_app` invocation pathway remains to be confirmed.
- Main discovered applications: `device`, `rtsp`, `recorder`, `alarmcenter`, `onvif`, `nginx`, `cgiserver.cgi`, `upgrade`.
- Main `device` ELF: 32-bit little-endian ARM EABI5 hard-float.
- Lens leads: `nvt_mtr_an41908.ko`, `lens_zfi.ko`; conditional IMX415 `af_lens=0` config maps SPI-connected zoom/focus motor with 2.7–13.5 mm nominal focal span. **Do not execute these parameters against hardware without validation.**
- AI leads: `kdrv_ai.ko`, `kflow_cnn.ko`, `kflow_nue.ko`, `kflow_nue2.ko`, `kflow_ai_net.ko`, data `ppvd.bin`, `class.bin`; `dvr.xml` indicates `support_ai_area=1`, `support_ai_trace=0`, `support_smartsearch=0`. Flags are not proof of usable APIs/features.

Separate platform **IPC_560B158MP / NA51089** has other supplied releases and is **out of primary scope**.
