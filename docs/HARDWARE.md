# Confirmed RLC-811A target and static firmware leads

Source: user-provided Reolink app device-info screenshot and offline inspection of the matching firmware. Camera has not been accessed.

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
- Startup: `/init`, `/etc/inittab`, `/etc/init.d/rcS`, `S10_SysInit2`, `start_app`; exact `start_app` invocation pathway remains to be confirmed.
- Main discovered applications: `device`, `rtsp`, `recorder`, `alarmcenter`, `onvif`, `nginx`, `cgiserver.cgi`, `upgrade`.
- Main `device` ELF: 32-bit little-endian ARM EABI5 hard-float.
- Lens leads: `nvt_mtr_an41908.ko`, `lens_zfi.ko`; conditional IMX415 `af_lens=0` config maps SPI-connected zoom/focus motor with 2.7–13.5 mm nominal focal span. **Do not execute these parameters against hardware without validation.**
- AI leads: `kdrv_ai.ko`, `kflow_cnn.ko`, `kflow_nue.ko`, `kflow_nue2.ko`, `kflow_ai_net.ko`, data `ppvd.bin`, `class.bin`; `dvr.xml` indicates `support_ai_area=1`, `support_ai_trace=0`, `support_smartsearch=0`. Flags are not proof of usable APIs/features.

Separate platform **IPC_560B158MP / NA51089** has other supplied releases and is **out of primary scope**.
