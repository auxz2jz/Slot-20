# RLC-811A PCB inventory and UART candidate map

**Task:** P1 — offline PCB-photo inventory and UART research

**Status:** complete as a preliminary, read-only evidence record

**Target:** owner-confirmed Reolink RLC-811A, hardware `IPC_523128M8MP`

No camera connection, electrical measurement, UART transmission, reboot,
NAND operation or firmware installation was performed. The five source
photographs remain private and ignored by Git; this document contains only
sanitized observations. H1 is unchanged and H2 remains blocked.

## Evidence labels

- **Photo-observed:** visible in the supplied component-side photographs.
- **Owner-confirmed:** supplied by the owner but not independently legible in
  this five-photo subset.
- **Matching-package static:** derived offline from the exact matching firmware
  package; not a physical-board measurement.
- **Generic official source:** capability in Novatek's public NA51055 source;
  not proof of this board's routing or enabled behavior.
- **External corroboration:** secondary evidence from another RLC-811A; useful
  only as a lead because production BOMs may vary.
- **Unknown:** evidence is insufficient to assign an identity or function.

## Preliminary component inventory

| Item | Sanitized observation | Evidence / confidence |
| --- | --- | --- |
| Camera identity | RLC-811A / `IPC_523128M8MP` | Owner-confirmed; high |
| PCB marking | `N25C06 V100` | Owner-confirmed; exact text is not independently legible in this photo subset |
| PCB date marking | `2020-08-13` | Owner-confirmed; exact text is not independently legible in this photo subset |
| Main processor | `NT98523MBG` | Photo-observed and owner-confirmed; high |
| Firmware platform identity | Device Tree compatible `novatek,na51055` | Matching-package static; high for the package, not a board-silkscreen observation |
| DRAM | Marking appears to be Nanya `NT5CC128M16JR-EK` | Photo-observed candidate; moderate-high pending a perpendicular macro. Nanya documents that part as 2-Gbit x16 DDR3L, so one confirmed chip would be 256 MiB physical capacity |
| Main reference can | `JWT 12.000C22`, consistent with a 12 MHz oscillator | Photo-observed; high for the marking, function inferred from package/form |
| Backup component | Yellow-wrapped coin-cell-style component beside a board `+` mark | Photo-observed; type, chemistry and circuit role unverified |
| NAND flash | **Unknown** | No readable flash top marking or package-to-net proof in the supplied views |
| Lens/motor-control IC | **Unknown** | Firmware contains lens/motor driver leads, but no photographed IC is assigned to them |
| Other small power/interface ICs | **Unknown** | Top markings are incomplete or blurred; no speculative identities assigned |

The apparent 256 MiB DRAM capacity, if the complete part marking is confirmed,
is compatible with the firmware exposing only 112 MiB to Linux while reserving
substantial memory for media/ISP functions. It does not prove the reservation
layout or replace a board schematic.

A published teardown of another RLC-811A reports the same processor but a
different DRAM vendor and a 128 MiB GigaDevice flash. That is useful
corroboration for the platform family and evidence that BOM variation exists;
it is **not** evidence identifying this board's NAND.

## Firmware and BSP comparison

The photographed `NT98523MBG` is consistent with the exact package's
`novatek,na51055` Device Tree identity and with the project's pinned official
Novatek NA51055 Linux/U-Boot sources. This is a cross-source consistency result,
not a claim that `NT98523MBG` and every NA51055 package have identical ballouts.

The matching package's decoded Device Tree declares three 16550-compatible
UART instances at `0xf0290000`, `0xf0300000` and `0xf0310000`, all configured
for 115200 baud. The actual packaged U-Boot contains `console=ttyS0,115200`,
`baudrate=115200`, an immediate Ctrl+C path and `nvt_uart_disable`. These static
facts make a preserved boot-console route plausible. They do not identify a
physical pad, prove that output is enabled on this unit, or establish safe I/O
voltage.

Novatek's official generic NA51055 Linux source defines four UART controller
bases, a 16550-like serial driver and multiple selectable GPIO routes. The GPIO
route names in generic pinmux code are neither BGA ball numbers nor this PCB's
test-pad map. They must not be projected onto the photographs without trace,
schematic or continuity evidence.

## UART candidate map

Orientation for this text map: component side facing the viewer, main SoC near
the center, yellow coin-cell-style component at lower left, and the small
cream/yellow connector along the upper edge.

| Candidate | Location and visible form | Assessment | Prohibited conclusion |
| --- | --- | --- | --- |
| **A** | Unpopulated board-edge footprint immediately right of the cream/yellow connector; several small inline pads with larger end/anchor pads inside a silkscreen outline | Plausible factory/test or optional connector footprint; **low-to-moderate UART-candidate confidence** | No pad is assigned TX, RX, GND or supply; it may be unrelated |
| **B** | Narrow vertical unpopulated pad group inside a white silkscreen rectangle, left of the tall black component in the close views | Approximately three small exposed pads; **low UART-candidate confidence** because it may be an ordinary component footprint | No electrical role or pin order is assigned |

Round soldered points, mounting holes and unlabeled isolated pads are not
promoted to UART candidates. Neither candidate has been probed.

## UART and Boot ROM recovery finding

Official public source supports the existence of NA51055 UART controllers and
shows that generic U-Boot has an early serial path. The official U-Boot board
source also contains an `ub51055` head-information structure described as being
parsed by a loader. None of those sources documents an NT98523 Boot ROM serial
download protocol, recovery strap table, authentication/eFuse policy, ROM
command framing or package ballout.

No authoritative public NT98523MBG datasheet or Boot ROM recovery manual was
located during this task. Therefore:

- a U-Boot UART console is a supported **static lead**, not a demonstrated
  recovery method;
- Boot ROM recovery over UART remains **unverified**;
- generic U-Boot command presence cannot satisfy the independent-recovery gate;
  and
- no voltage, connector, pad order or safe adapter can yet be specified.

## Evidence needed next

The next authorized task can remain photography-only. Useful additions are:

1. A perpendicular, high-resolution full component-side image with a ruler or
   known scale and the board orientation kept consistent.
2. A matching full-board underside image.
3. Sharp perpendicular and oblique-light macros of candidates A and B showing
   their silkscreen labels and visible trace fan-out on both sides.
4. Macros of every plausible flash/memory package, especially the small
   WSON/SOIC/QFN devices on the right half, with complete top markings readable.
5. A macro that independently shows `N25C06 V100` and `2020-08-13`.
6. A sharper DRAM macro sufficient to confirm the complete suffix.

No further disassembly, cleaning, scraping, soldering or powering is implied.
If a later, separately approved task uses a matching spare, the passive
electrical evidence sequence should be: unpowered ground-plane continuity
first; then only after a reviewed plan, high-impedance voltage/idle/boot-output
measurement. TX/RX must remain unnamed until trace or signal evidence supports
them. An adapter supply pin must never be connected merely because a pad group
resembles UART. Those measurements are **not authorized by this document**.

## Sources and coverage limits

- Matching proprietary package: exact local package and extracted artifacts
  already recorded in `HARDWARE.md`; binaries remain private.
- Novatek official Linux source, pinned commit:
  <https://github.com/Novatek-OSS/kernel/tree/1019c2e049f239ba0668ccfd1356e952fde3b29b>
  Relevant files include
  [`hardware.h`](https://github.com/Novatek-OSS/kernel/blob/1019c2e049f239ba0668ccfd1356e952fde3b29b/arch/arm/plat-novatek/include/plat-na51055/hardware.h),
  [`nvt_serial.h`](https://github.com/Novatek-OSS/kernel/blob/1019c2e049f239ba0668ccfd1356e952fde3b29b/arch/arm/plat-novatek/include/plat-na51055/nvt_serial.h),
  [`nvt_serial.c`](https://github.com/Novatek-OSS/kernel/blob/1019c2e049f239ba0668ccfd1356e952fde3b29b/drivers/tty/serial/nvt_serial.c)
  and the
  [NA51055 pinmux source](https://github.com/Novatek-OSS/kernel/blob/1019c2e049f239ba0668ccfd1356e952fde3b29b/drivers/pinctrl/novatek/na51055/na51055_pinmux_host.c).
- Novatek official U-Boot source, pinned commit:
  <https://github.com/Novatek-OSS/u-boot/tree/b23172486e60c2f40729231eae06f48ac3c8d680>
  Relevant files include
  [`nvt_headinfo.c`](https://github.com/Novatek-OSS/u-boot/blob/b23172486e60c2f40729231eae06f48ac3c8d680/board/novatek/nvt-na51055/nvt_headinfo.c)
  and
  [`soc.c`](https://github.com/Novatek-OSS/u-boot/blob/b23172486e60c2f40729231eae06f48ac3c8d680/arch/arm/mach-novatek/nvt_na51055_a32/soc.c).
- Nanya official part page:
  <https://www.nanya.com/en/Product/4115/NT5CC128M16JR-EK>
- Secondary same-model teardown, used only for BOM-variation context:
  <https://www.mbreviews.com/reolink-rlc-811a-camera-review/>

The public Novatek repositories are generic BSP evidence rather than a Reolink
schematic, and the secondary teardown is not exact-unit evidence. Absence of a
publicly located Boot ROM manual is not proof that no vendor-only recovery
facility exists.

## Checkpoint and next safe task

- **Completed:** P1 preliminary board inventory, source comparison, UART
  candidate map and Boot ROM evidence boundary.
- **Checkpoint:** sanitized documentation only; original photographs and
  proprietary firmware remain outside public Git history.
- **Next task:** **P1.1 — review additional private PCB photographs only** and
  refine the inventory/candidate map without probing or starting H2.
- **Recommended reasoning:** Medium for photo transcription and documentation;
  High only if new readable markings require focused datasheet/pinmux tracing.
- **When to switch:** use High for a specific conflicting component identity or
  trace-routing question; Ultra is unnecessary without a narrowly scoped hard
  recovery question and a prior checkpoint.
- **Usage preparation:** this is the stopping checkpoint before any further
  substantial research. Reliable current account usage is unavailable.
