# Static interface reverse-engineering plan

Scope: offline analysis of the matching RLC-811A `IPC_523128M8MP` package. This
plan does not authorize camera access, execution of recovered ARM programs, or
firmware installation. Vendor artifacts and detailed private analysis databases
remain outside Git.

## Evidence labels

Every finding should be marked as one of:

- **Verified-package:** directly established from the matching package or its
  hash-identified sections.
- **Recovered-static:** observed in a successfully reconstructed file, ELF,
  module, configuration, or disassembly.
- **Inferred:** a proposed relationship based on names, imports, strings, or a
  likely Novatek architecture; it still needs stronger evidence.
- **Hardware-unverified:** would require a separately approved test on matching
  spare hardware. Do not promote this label during the current phase.

## Stage B0: complete and corroborate extraction

1. Run `tools/unpack_reolink_offline.py` on Linux with `liblzo2.so.2`, without
   `--write-files` first. Confirm package hash, six section hashes, 760 rootfs
   paths, 275 app paths, 13,513 plus 7,707 CRC-valid UBIFS nodes, and the prior
   8-rootfs/2-app incomplete-file result.
2. Materialize files only in the ignored private workspace when static tools
   require them. Never create live symlinks or execute recovered programs.
3. Compare UBI volume geometry, inode/dentry counts, and a sampled path/hash set
   with a maintained `mtd-utils`/`ubireader` workflow. Treat differences as
   journal/parser questions, not as evidence that either output is bootable.
4. Keep a small sanitized run summary: tool commits/hashes, host/tool versions,
   package/section hashes, counts, and failure categories. Do not commit raw
   manifests because filenames or contents may later prove sensitive.

Exit gate: repeatable Linux extraction with explained discrepancies and no
proprietary outputs visible to Git.

## Stage B1: boot, module, and process map

Recover and read the startup chain, module-loading scripts, symlink targets, and
service launch arguments. Build one ordered table containing process/module,
loader, arguments, dependencies, IPC endpoints, and evidence label. Begin with
`/init`, `rcS`, `S10_SysInit2`, `start_app`, `device`, `rtsp`, `recorder`,
`alarmcenter`, `onvif`, `nginx`, and `cgiserver.cgi`.

Static tools only: `file`, `readelf`, `objdump`, `nm`, `modinfo`, bounded string
searches, and a private Ghidra project if needed. Record architecture, dynamic
dependencies, exported/imported symbols, relocations, module aliases and
parameters. Do not emulate or run the ARM binaries.

Exit gate: an evidence-backed startup/dependency graph with unresolved edges
listed explicitly.

## Stage B2: subsystem interface maps

| Area | Package leads | Questions to answer | Sanitized deliverable |
|---|---|---|---|
| Sensor / ISP / video | `nvt_sen_imx415.ko`, `nvt_isp.ko`, `kdrv_videocapture.ko`, `kflow_videocapture.ko`, `kdrv_videoprocess.ko`, `kflow_videoprocess.ko`, `kdrv_h26x.ko`, `kflow_videoenc.ko`; IMX415 sensor/ISP configs; Novatek sample video tools | Module load order; exported HDAL entry points; `/dev`, sysfs, procfs and ioctl surfaces; buffer formats; capture-to-ISP-to-encoder ownership; which service owns stream setup | Symbol/import matrix, interface table, and capture-to-RTSP/recording call graph |
| Streaming / recording | `device`, `rtsp`, `recorder`, `onvif`, `cgiserver.cgi`, `dvr.xml` | Process boundaries; sockets/shared memory/message queues; codec/profile configuration; stream/session control; recorder event coupling | Service/IPC graph and minimal stream-control contract |
| Lens / autofocus | `lens_zfi.ko`, `nvt_mtr_an41908.ko`, IMX415 motor configs | Driver registration and bus binding; motor/lens ioctls; focus/zoom position units and bounds; autofocus ownership; callers in `device`/CGI | Static lens-control ABI table with all motion values marked unsafe/unverified |
| AI / zones / events | `kdrv_ai.ko`, `kflow_ai_net.ko`, `kflow_cnn.ko`, `kflow_nue*.ko`, `ppvd.bin`, `class.bin`, `device`, `alarmcenter`, CGI/UI files | Model loader and tensor metadata; inference submission/completion ABI; detection/event structures; zone coordinate system; whether `support_ai_area=1` reaches an implemented API | AI dependency graph, candidate data structures, and zone/event API map |

For each ELF/module, capture only metadata needed to reproduce conclusions:
SHA-256, ELF header, imports/exports, module metadata, and selected xref notes.
Avoid publishing decompiled vendor code, complete string dumps, or model files.

## Stage B3: prioritize independent seams

After the maps exist, define independent adapters at the narrowest replaceable
boundaries:

1. encoded-frame/RTSP ingestion for the PC-side prototype;
2. normalized detections plus polygon/tripwire evaluation;
3. event/snapshot handoff to interchangeable ALPR engines;
4. an abstract lens interface whose hardware backend remains disabled until a
   recovery-tested spare is available.

Test these contracts with synthetic metadata and prerecorded, non-personal
fixtures. Keep vendor ABI compatibility research separate from independently
written application logic.

## Exact next checkpoint

Complete B0 on a Linux environment with LZO, then perform B1 only far enough to
produce the ordered module/process map and a per-binary ELF metadata inventory.
Stop and update `docs/STATE.md` before deeper decompilation. This creates a
reviewable checkpoint and prevents simultaneous speculation across video, AI,
and lens control.
