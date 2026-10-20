# H0 primary hardware baseline

**Status:** H0 complete from existing records only. No new camera session,
network contact, authentication, query, reboot, setting change, actuation,
opening, build, NAND operation or firmware installation occurred.

## Purpose and evidence boundary

This record identifies the owner's in-service development reference without
publishing device-instance data. The original evidence was an owner-provided
Reolink Device Info screenshot. That private screenshot is not tracked in this
repository, and H0 relies on the identity fields already verified and recorded
in `HARDWARE.md`, the D1 plan, the roadmap and the current project state.

The accessible project record does not state when the screenshot was captured.
Its capture date is therefore **unknown**. The date-like portion of the firmware
version is not treated as a screenshot timestamp.

## Verified public identity baseline

| Field | Public value | Evidence class | H0 status |
| --- | --- | --- | --- |
| Manufacturer | Reolink | Existing verified project record derived from owner-provided Device Info evidence | Confirmed for project targeting |
| Model | `RLC-811A` | Owner-provided Device Info screenshot, normalized in existing records | Confirmed |
| Hardware version | `IPC_523128M8MP` | Owner-provided Device Info screenshot, normalized in existing records | Confirmed exact revision |
| Installed firmware | `v3.1.0.1643_2402219117` | Owner-provided Device Info screenshot, normalized in existing records | Previously identified/confirmed |
| Screenshot capture date | Unknown | Not present in the accessible verified record | Explicitly unresolved |
| Target role | Primary in-service development reference | Owner direction dated 2026-10-19 | Confirmed role; not a sacrificial spare |

The matching offline package is
`IPC_523128M8MP.1643_2402219117.RLC-811A.IMX415.8MP.AF.REOLINK.pak`,
46,376,279 bytes, SHA-256
`f62a68d21397da9bb2aadefc66edfdbe91f35270b2cc64857a9082ed17e6a2e9`.
Package compatibility is corroborating offline evidence; it does not prove the
physical internals of the camera.

## Static leads that remain unverified on the camera

| Area | Offline lead | What remains unverified |
| --- | --- | --- |
| Processor / architecture | Matching package FDT declares compatible `novatek,na51055`; recovered executables and U-Boot are 32-bit little-endian ARM/ARMv7 EABI5 hard-float evidence | Physical SoC marking/ID, silicon revision, fuses/security state, clocking and actual board wiring |
| Memory | Package FDT declares 112 MiB Linux-visible memory | Physical DRAM manufacturer, part number, total installed capacity, bus geometry, reserved regions and stability on this unit |
| NAND | Package FDT declares a 128 MiB address space; offline UBI evidence uses 2,048-byte minimum I/O, 131,072-byte PEB and 126,976-byte LEB geometry | Physical chip manufacturer/part/capacity, page and OOB layout, ECC algorithm/strength, controller behavior, bad/reserved-block map, BBT policy and actual partition contents |
| PCB | No public H0 board image or board marking is available | PCB revision, layout, test pads, UART voltage/pinout, power/PoE design, NAND package/routing and component population |
| Image sensor | `IMX415` appears in the matching package filename and static sensor/driver evidence | Physical sensor marking, exact module revision, bus/address, clocks, calibration and live operation |
| Boot/platform drivers | Package/BSP analysis contains Novatek NAND, Ethernet, GPIO, MMC, watchdog and other platform support | Exact enabled driver set, PHY model/wiring, pinctrl, kernel configuration and behavior on this camera |
| Lens/motor drivers | Package contains `nvt_mtr_an41908.ko` and `lens_zfi.ko` leads | Actual motor-controller population, lens module, pin mapping, calibration and safe control semantics |
| ISP/media/AI drivers | Package contains ISP/media services and AI-related modules/data | Hardware accelerator revision, proprietary ABI, sensor/ISP compatibility, encoder behavior and usable feature set |

Firmware filenames, compiled modules, Device Tree nodes and BSP source are
**static leads**, not live component identification. No item in this table may
be converted into a probing, write or actuation instruction without a later
review and explicit approval.

## Privacy and publication review

The public H0 records intentionally contain no:

- UID, serial number, MAC address, IP address, QR code or account identifier;
- username, password, session token, private key or certificate;
- location, recording, image from the camera or network topology;
- unredacted Device Info screenshot; or
- device-specific calibration data, NAND contents or bad-block map.

The original screenshot and any private instance identifiers remain outside
Git. The machine-readable companion is
`../configs/h0_primary_hardware_baseline.json`; it contains only the sanitized
fields shown here and explicit Boolean safety/gate states.

## Safety and eligibility state

- The camera remains an in-service stock-firmware reference.
- No live behavior or physical component was verified by H0.
- No full-device raw/OOB backup has been acquired or verified.
- No independent recovery method has been demonstrated on a matching spare.
- The device is not eligible for firmware installation, destructive testing or
  deliberate failure injection.
- D2a-1 seller outreach remains on hold, while its prior research is preserved.

## H0 completion recommendation

- **Completed:** Normalized the three confirmed identity fields, recorded the
  source and unknown capture date, classified processor/memory/NAND/PCB/sensor/
  driver leads, and produced privacy-safe human and machine records.
- **Checkpoint:** Commit and push this document, its JSON companion, updated
  state and handoff. No screenshot, private identifier, build artifact or camera
  state changed.
- **Next task:** **H1 live-observation protocol planning only** — design one
  exact, read-only Device Info/status observation proposal without connecting
  to the camera.
- **Recommended model and reasoning:** Medium.
- **Why:** H1 is a bounded safety/procedure and privacy-review task; it does not
  require reverse engineering or live hardware access.
- **When to switch:** High is appropriate for H2 only after the owner explicitly
  approves the exact live-device actions. Ultra is unnecessary unless a later
  narrowly scoped recovery blocker persists after High reasoning.
- **Usage preparation:** H0 is the safe checkpoint. Refresh reliable usage at
  closeout and checkpoint H1 before requesting any H2 approval.
