# RLC-811A PCB inventory and UART candidate map

**Task:** P1 through P1.2b — offline PCB-photo inventory and UART-pad review

**Status:** complete as a preliminary, read-only evidence record

**Target:** owner-confirmed Reolink RLC-811A, hardware `IPC_523128M8MP`

No camera connection, electrical measurement, UART transmission, reboot,
NAND operation or firmware installation was performed. Fifteen source
photographs across three private sets remain ignored by Git; this document contains only
sanitized observations. H1 is unchanged and H2 remains blocked.

## Evidence labels

- **Photo-observed:** visible in the supplied component-side photographs.
- **Owner-confirmed:** supplied by the owner but not independently legible in
  the available photographs.
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
| PCB marking | `N25C06 V100` | Photo-observed in the second set; high |
| PCB date marking | `2020-08-13` | Photo-observed in the second set; high |
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

The first set shows the memory/coin-cell side. Its orientation is main memory
near the center, yellow coin-cell-style component at lower left and a small
cream/yellow connector along the upper edge. The second set shows the
processor/Ethernet side with the Novatek SoC at lower right, Ethernet magnetics
at left and a wide FFC connector along the upper edge.

| Candidate | Location and visible form | Assessment | Prohibited conclusion |
| --- | --- | --- | --- |
| **A** | Unpopulated board-edge footprint immediately right of the cream/yellow connector; several small inline pads with larger end/anchor pads inside a silkscreen outline | Plausible factory/test or optional connector footprint; **low-to-moderate UART-candidate confidence** | No pad is assigned TX, RX, GND or supply; it may be unrelated |
| **B** | Narrow vertical unpopulated pad group inside a white silkscreen rectangle, left of the tall black component in the close views | Approximately three small exposed pads; **low UART-candidate confidence** because it may be an ordinary component footprint | No electrical role or pin order is assigned |
| **C — leading test-area candidate** | Processor/Ethernet side: an irregular L-shaped cluster of approximately six large, heavily tinned round pads between the SoC corner and the right-hand upper mounting hole | **Low-to-moderate UART-area confidence.** Several traces appear to run toward the SoC, making factory debug/test use plausible, but the cluster is not a clean four-pin header and the solder obscures pad geometry | It could be SWD/JTAG, production test, rework or another circuit; no subset or pad is assigned TX, RX, GND or supply |

The close macros correct the earlier four-pad-row interpretation. A separate
compact 2-by-2 group of four small pads in white silkscreen sits directly below
the large tinned cluster. It is visually a distinct footprint and is not merged
into candidate C or promoted to UART without trace or electrical evidence. The
previous red-circle annotation identifies the general area only; it must not be
read as selecting a verified four-pad subset.

Cross-side alignment uses the two upper mounting holes. When the board is
flipped to the memory/coin-cell side, the processor-side right-hand hole becomes
the left-hand hole. Candidate C maps immediately right/below that hole, largely
under or along the left edge of the white factory label. No corresponding
exposed six-pad cluster is visible. The label and multilayer routing prevent
photo-only trace correlation; the label must not be removed for this task.

Other isolated solder points, mounting holes and component-style footprints
are not promoted merely because they are exposed. None of A, B or C has been
probed.

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

The straight-down and oblique same-side macros and reverse-side alignment are
complete. The two reverse-side uploads supplied for P1.2b are byte-identical to
earlier private evidence, so the unique-photo count remains fifteen. No
additional photograph is expected to confirm UART while the mapped area remains
under the intact factory label and inner-layer routes are invisible. Do not
clean, scrape, remove solder or lift the label.

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

- **Completed:** P1.2b correlated candidate C to the reverse side. The mapped
  region is largely under/adjacent to the factory label and has no visible
  matching pad cluster; photo-only UART confirmation is exhausted.
- **Checkpoint:** sanitized documentation only; original photographs and
  proprietary firmware remain outside public Git history.
- **Next task:** none automatically. Any UART electrical-identification plan is
  a new, separately approved task and should preferably use a matching spare;
  no probing is authorized here.
- **Recommended reasoning:** Medium for a future passive-measurement plan; High
  only for a separately approved, safety-reviewed hardware investigation.
- **When to switch:** use High for a specific conflicting component identity or
  trace-routing question; Ultra is unnecessary without a narrowly scoped hard
  recovery question and a prior checkpoint.
- **Usage preparation:** this is the stopping checkpoint before any further
  substantial research. Reliable current account usage is unavailable.
