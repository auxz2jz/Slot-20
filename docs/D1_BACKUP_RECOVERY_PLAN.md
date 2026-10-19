# D1 matching-spare backup and independent-recovery plan

**Status:** D1 COMPLETE — planning only. No camera has been contacted, opened,
powered, rebooted, connected to UART, read from or written. This document does
not authorize a physical operation or firmware installation.

## Objective and evidence boundary

D1 converts the completed A1–A5 static evidence into a non-destructive,
approval-gated plan for selecting a matching sacrificial RLC-811A, preserving
every device-specific flash byte needed for recovery, and eventually proving a
recovery route independent of the experimental Linux/web stack. Generic
Novatek capabilities and ordinary U-Boot documentation remain leads, not
evidence that the matching hardware exposes or accepts a method.

The completed private kernel and two rootfs workspaces and the C3 host-only
management demonstration are immutable inputs to this planning task. They are
not combined, rebuilt or copied into a firmware image.

## Bounded D1 outputs

| ID | Output | Completion criterion |
| --- | --- | --- |
| D1.1 | Matching-spare and evidence checklist | Required exact matches, acceptable pre-purchase evidence and internal unknowns are explicit |
| D1.2 | Backup acquisition/verification specification | Raw data/OOB/ECC/bad-block/factory-data requirements and multiple-read acceptance rules are explicit |
| D1.3 | Recovery candidate and spare-test protocol | Independence boundaries, required equipment, costs, staged proofs, aborts and approval gates are explicit |
| D1.4 | Safety review and handoff | No operational camera command, unsupported recovery claim, proprietary data or secret enters Git |

## Design checkpoint

- **Completed:** D1 scope, evidence boundary and four independently verifiable
  planning outputs are frozen.
- **Checkpoint:** commit and push this skeleton before detailed recovery design.
- **Next task:** complete D1.1–D1.3 from existing A5 evidence and authoritative
  public references, then perform the D1.4 safety review.
- **Recommended model and reasoning:** High.
- **Why:** NAND raw-layout preservation and the independence boundary between
  Linux, U-Boot, Boot ROM and an external programmer are safety-critical.
- **When to switch:** Medium is adequate for final documentation checks; Ultra
  only for a later narrowly scoped unresolved BootROM/bootloader question.
- **Usage preparation:** this checkpoint precedes the detailed plan; refresh
  usage before any later expensive or physical work.

## D1.1 — exact matching-spare requirements

An `RLC-811A` product name is necessary but insufficient. Reolink's own
firmware guide requires both model and hardware version when selecting an
image, and its system-information guide exposes model, hardware number and
firmware version. The minimum pre-purchase match is therefore:

1. model exactly `RLC-811A`;
2. hardware number exactly `IPC_523128M8MP` (punctuation normalized only for
   display; a different identifier is a rejection);
3. seller-supplied device-information screenshot showing hardware and firmware
   versions, with UID/serial/MAC redacted before it enters the public project;
4. exterior product-label and connector/housing photographs consistent with
   the target; and
5. return eligibility if later internal inspection reveals another board.

The target reference firmware is `v3.1.0.1643_2402219117`. A spare may have a
different build only if Reolink lists it for the exact same model/hardware
pair; firmware version alone never establishes a hardware match. The public
product specification confirms 802.3af 48 V active PoE, optional 12 V/1 A DC,
10/100 Ethernet and removable microSD, but none of those product-level facts
proves board, bootloader, NAND or Boot-ROM equivalence.

### Match matrix

| Layer | Evidence required before destructive recovery tests | Current target evidence | Result if different/unknown |
| --- | --- | --- | --- |
| Product identity | RLC-811A plus exact `IPC_523128M8MP` device-info record | Confirmed from owner's prior screenshot | Different hardware number: reject; unknown: do not buy for this role |
| PCB assembly | Same main-PCB part number, revision, artwork and populated-option code; high-resolution photos of both sides | Unknown | May be used only for observation, never cross-flash |
| SoC | Physical package marking and ID consistent with NA51055; boot banner/SoC ID if later read non-destructively | Matching package/FDT and BSP lead only | Reject as recovery surrogate until reconciled |
| NAND | Same manufacturer, exact part number, package, density, page/OOB/erase geometry, dies/planes, voltage and JEDEC/parameter-page response | FDT declares SPI NAND and 128 MiB address space; physical part unknown | No raw clone or programmer selection |
| DRAM | Same part/configuration and physical size; later boot evidence must agree with memory map | FDT exposes 112 MiB to Linux, not a physical measurement | No RAM-load address or RAM-boot test |
| Boot chain | Hash/size of loader, active FDT and U-Boot; bootloader version/config; secure-boot/OTP/fuse state; partition map | Package hashes/offsets only, not installed bytes | No assumption that recovery commands or images transfer |
| Board support | Same Ethernet PHY, PMIC, reset/strap network, oscillator and UART/test-pad routing | Unknown | Recovery transport remains unverified |
| Camera peripherals | Same sensor, lens/motor driver, audio, IR/spotlight and microSD routing | IMX415/lens facts are firmware leads | Not required for an early rescue-only test, but required before claiming a full compatible firmware target |

### Match classes

- **Class A — exact test surrogate:** all boot-critical rows match. Only Class A
  is eligible for deliberate failure/recovery testing intended to satisfy the
  project's matching-hardware gate.
- **Class B — observation donor:** product/hardware number matches but at least
  one internal row is unknown or different. It may provide photographs or
  separately approved passive observations, but cannot validate a clone,
  restore, or firmware image.
- **Rejected:** wrong/unknown hardware number, inaccessible device-information
  evidence, incompatible PCB/NAND/SoC, or seller forbids the planned opening.

Private inventory must assign each physical unit a local opaque ID. Serial,
UID, MAC, certificates, keys and label photographs remain in encrypted private
storage. The public record contains only hashes, redacted facts and the match
class.

## D1.2 — complete backup specification

The manufacturer `.pak`, filesystem extraction and ordinary partition dumps
are not full-device backups. NAND bad-block markers and some ECC/metadata live
in the out-of-band area; Linux documentation also notes that NAND eraseblocks
can become bad and that UBI hides that behavior behind its volume abstraction.
The backup must preserve both the physical representation and useful
controller-corrected views.

### Preconditions for any future read

Each item requires its own later owner approval; D1 grants none of them.

- A Class A candidate has been acquired and removed from production duty.
- The exact NAND datasheet and programmer/tool support entry are archived.
- Supply voltage, I/O voltage, grounding, board power domains and bus isolation
  are measured without attaching a driving probe.
- The selected acquisition path is demonstrably read-only. Any utility mode
  that can erase, mark bad, update BBT, write OOB, change OTP/fuses or reset
  configuration is disabled and treated as an abort if unexpectedly requested.
- The PC writes only into a new encrypted private capture directory on a disk
  with at least three times the expected capture size plus logs and replicas.
- A second protected destination is ready before the camera or chip is touched.

### Required private backup set

| Artifact | Required content | Why it is separate |
| --- | --- | --- |
| Physical raw reads A/B/C | Entire addressed chip in physical page order, including every OOB/spare byte and bad/reserved block; never skip or compact bad blocks | Only representation capable of preserving original ECC/BBM/OOB layout if the acquisition route exposes it |
| ECC-corrected reads A/B | Entire logical data area through the known controller/ECC configuration, with corrected/uncorrectable counts by page or eraseblock | Provides stable readable content and exposes marginal pages; it is not a raw clone |
| Geometry/identity | JEDEC/chip ID, parameter page if supported, exact data bytes/page, OOB bytes/page, pages/block, blocks/die, die count, total bytes, voltage and package | Prevents applying a dump with the wrong geometry |
| Bad-block evidence | Factory and runtime bad-block map, reserved-block map, raw BBM bytes/locations and BBT location/version if present | A skipped-block dump destroys physical addressing and is unacceptable |
| Controller/ECC record | Controller path, driver/tool versions and hashes, ECC mode/strength/step/layout, read-retry state and all invocation settings | Raw bytes cannot be interpreted or restored safely without the same semantics |
| Partition views | Full-chip offset map plus separate logical dumps of all declared regions, including gaps and padding | Allows comparison without pretending partitions cover the whole chip |
| Factory/unique regions | Unmodified `fdt.restore`, `uenv`, `para`, `sp`, `ext_para`, `download`, calibration, lens/motor data, MAC/UID, keys/certificates and unknown records | These regions are absent from the update `.pak` or have unresolved ownership |
| Boot evidence | Loader/FDT/U-Boot hashes, partition table, boot banner and read-only environment/configuration observations | Binds the backup to the tested boot chain |
| Acquisition record | Opaque device ID, UTC timestamps, wiring photographs, tool binaries/config hashes, commands, exit codes and complete logs | Makes the capture reproducible and auditable |

No secret or binary in this set belongs in Git. Store the set encrypted at two
physically separate locations; keep a small offline printed recovery index with
only opaque IDs and manifest hashes. A repository commit is not a backup of
these private artifacts.

### Size and layout invariants

Do not hard-code the FDT's 128 MiB declaration as physical truth. After exact
geometry is established:

```text
page_count       = physical_data_bytes / data_bytes_per_page
raw_capture_size = page_count * (data_bytes_per_page + oob_bytes_per_page)
```

Every raw file must have exactly `raw_capture_size` bytes. The capture format
must state whether bytes are interleaved `data || OOB` per page. Any header,
padding, skipped bad block or tool-specific trailer must be separately
documented and removed only into a derivative copy, never from the original.

`mtd-utils` is a possible future acquisition component, not a selected camera
procedure. Its `nanddump` source exposes explicit `--noecc`, `--oob` and bad
block handling modes (`padbad`, `dumpbad`, `skipbad`), and warns that OOB
defaults change between releases. Therefore an eventual command must pin the
exact binary hash and use explicit options; `skipbad` can never create the
physical master. No command is supplied or executed by D1.

### Multiple-read acceptance protocol

1. Capture raw read **A**, reset only the host-side acquisition session, then
   capture raw read **B** without any write/erase/mark-bad operation.
2. Remove all power, reinitialize the verified reader independently, and
   capture raw read **C**. This detects stateful tool/setup mistakes.
3. Compute SHA-256 over each complete file and over a deterministic manifest of
   page/eraseblock SHA-256 values. NIST FIPS 180-4 defines SHA-256 for change
   detection; hashes complement, but do not replace, byte/geometry checks.
4. Separately repeat the ECC-corrected full read twice and hash it. Record ECC
   correction counts and uncorrectable pages for each pass.
5. Accept the raw master only when at least two independent complete raw+OOB
   reads are byte-identical, all three bad/reserved-block maps agree, sizes and
   geometry agree, and no unexplained read error exists. Prefer all three raw
   hashes to match.
6. If any raw byte differs, preserve every original, localize differences by
   page/OOB field and take no write action. A majority-voted image is diagnostic
   only and must not be labeled verified. Marginal/uncorrectable pages require
   another read method or professional recovery assessment.
7. Compare logical partition derivatives against the raw master using the
   documented mapping. Validate known structures offline and confirm all
   declared ranges plus gaps cover the measured chip exactly.
8. Copy the accepted set to the second protected location, re-hash both copies,
   make them read-only, and sign/date the manifest. Quarterly media checks are
   prudent while the project remains active.

A backup is **acquired** after steps 1–4, **verified** only after steps 5–8, and
**restorable** only after a byte/geometry-appropriate restore to sacrificial
matching media has been independently demonstrated. Those labels must never be
interchanged.

## D1.3 — recovery method decision matrix

This matrix inherits A5's matching-binary offsets and does not repeat its
disassembly. `Independent of Linux` is weaker than `independent of U-Boot and
on-flash contents`.

| Candidate | Independence boundary | First future non-writing proof | Proof needed to count as recovery | D1 disposition |
| --- | --- | --- | --- | --- |
| External SPI-NAND reader/programmer | Potentially independent of Linux, U-Boot and all NAND contents | Exact chip identification; powered-off/off-board or electrically isolated raw ID plus three full raw/OOB reads | Restore the verified image to a replacement chip/clone, boot the Class A spare, then recover a controlled early-boot failure without relying on original NAND | **Preferred strongest candidate**, but exact chip/tool/OOB support and in-circuit isolation are unknown |
| SoC Boot ROM downloader | Potentially independent of Linux/U-Boot/NAND if immutable ROM and security policy permit | Documented entry trigger and transport; identify device and perform bounded RAM transfer/readback only | Repeatably restore all required regions, including loader/U-Boot, from verified private backup after a controlled failure | Strong theoretical candidate; protocol, straps, authentication/eFuses and tools wholly unverified |
| Preserved U-Boot + UART | Independent of Linux only | Measure pad voltage/passively capture boot TX; later demonstrate repeatable console interruption without issuing a storage command | Recover a deliberately unusable Linux region while U-Boot remains intact, using verified backup/target hashes | Plausible secondary route; `bootdelay=0`, pinout and RX acceptance unverified; cannot cover damaged U-Boot |
| U-Boot TFTP/Ethernet | Independent of Linux, dependent on U-Boot/UART or another trigger | Isolated-link bring-up and bounded TFTP-to-RAM with before/after hash | RAM-boot rescue and restore controlled Linux damage; repeat cold | Useful transport if reached; not a complete independent route and cannot repair U-Boot |
| U-Boot MMC/FAT | Independent of Linux, dependent on U-Boot and physical media routing | Read-only media detection plus bounded FAT-to-RAM/hash test | RAM-boot rescue and restore controlled Linux damage; repeat cold | Useful alternative transport; microSD product presence does not prove U-Boot pinmux/boot support |
| Reset/staged `download` updater | Dependent on loader/U-Boot, staged data and unresolved GPIO/partition behavior | Passive mapping only; do not press/trigger until all erase/write semantics are known | Full change map, power-loss tests and restoration across every affected region | **Not trusted**; observed code can erase part of `para`; not an independent baseline |
| Future protected rescue/A/B | Dependent on whatever selector and storage it uses | Offline capacity/ownership/selector design only | Bad image, failed health, lost network and interrupted write repeatedly select a protected known-good target, while a separate deeper route still works | Architecture option only after backup/recovery proof; no free partition or persistent selector is established |

Official U-Boot documentation confirms only generic semantics: `fatload` reads
a bounded file into RAM; `bootm <kernel> - <fdt>` can boot without a ramdisk;
TFTP variables/commands can load network data. The actual Reolink command table
contains corresponding names, but those manuals do not prove pads, media,
Ethernet, safe RAM ranges or successful execution on this board.

### Recommended route order

1. Resolve the physical NAND identity and determine whether a professional
   tool explicitly supports its SPI-NAND raw data+OOB/BBT semantics. Prefer an
   off-board read or an isolation fixture; never allow a programmer and SoC to
   drive the bus simultaneously.
2. In parallel only after approval, use passive UART observation to determine
   whether the preserved U-Boot route is reachable. Keep adapter TX and its
   power lead disconnected during receive-only discovery.
3. If console control is later approved and proven, evaluate TFTP-to-RAM and
   MMC/FAT-to-RAM solely as reversible transports. Do not combine a load test
   with NAND erase/write.
4. Pursue Boot ROM only with authoritative SoC/board documentation or a
   lawfully obtained, provenance-checked tool. Unknown straps or vendor tools
   are not experiments.
5. Do not use the reset/staged updater or design A/B storage until every
   partition's ownership and the deeper recovery route are established.

## Matching-spare test protocol

Every stage stops for a written evidence review and fresh approval before the
next stage. Approval of one stage never implies approval of another.

| Stage/gate | Planned activity on the dedicated spare | Pass evidence | Mandatory stop/abort |
| --- | --- | --- | --- |
| G0 — purchase approval | Review redacted seller evidence and cost/return terms; acquire no unit until approved | Exact model/hardware screenshot and label; local opaque inventory ID reserved | Any hardware-number ambiguity or non-returnable mismatch risk |
| G1 — acceptance approval | Isolated stock functional baseline and device-info capture; no update/reset | Redacted hardware/firmware record and ordinary function baseline | Unit is linked to production, wrong revision, damaged, or account privacy cannot be isolated |
| G2 — opening approval | Depower/disassemble under ESD control; photograph only | PCB revisions and chip markings; seals/thermal/weatherproof parts documented | Unknown stored energy, inaccessible fastener, conformal coat/potting or damage risk |
| G3 — passive electrical approval | Map ground and rail/pad idle levels with high-impedance instruments; receive-only UART observation | Stable voltage/baud/boot log across cold starts; zero driven target pins | Unknown I/O level, unstable current, heat, smell, reset loop or probe-slip risk |
| G4 — read-only backup approval | Use the selected verified path for raw/OOB and corrected reads | D1.2 complete backup set; repeated hashes/maps accepted; two protected copies | Tool lacks raw OOB/BBT support, geometry/ID mismatch, read differences, ECC failure or any prompted write/erase |
| G5 — RAM-only recovery approval | Interrupt U-Boot if proven; load a tiny bounded signed/test artifact to a verified non-overlapping RAM window; do not write storage | Hash-matched transfer and clean return/power-cycle; then optional maintenance RAM boot | RAM map/security policy unresolved, automatic flash action, network exposure or unexplained reset |
| G6 — restore-media approval | Preserve original chip untouched; restore verified backup to an exact replacement/clone where feasible | Programmer readback equals intended raw layout; Class A spare boots stock and unique-data policy is respected | Only original chip available, tool rewrites BBM/ECC unexpectedly, or clone identity handling unresolved |
| G7 — Linux-failure proof approval | On the replacement/clone only, create one controlled failure limited to the Linux target; recover without experimental Linux/web | Recorded failure, independent restore, hashes and at least three repeat cold boots | Recovery uses the component under test, changes bootloader/factory data, or cannot restore deterministically |
| G8 — early-boot proof approval | Only if external/ROM route is already repeatable, create a controlled loader/U-Boot failure on replacement media | Restore without working NAND boot chain, verify full stock behavior and repeat | Any dependence on damaged U-Boot, original factory chip, or unverified write mapping |
| G9 — production review | Present backup, restore, UI, update/rollback and remaining-risk evidence to owner | Every mandatory checkbox reviewed; exact operation receives separate approval | Any unresolved gate; no production action is requested by D1 |

The preferred destructive-test medium is a verified replacement NAND clone or
socket/adapter on the spare, leaving the spare's original factory chip
untouched. Whether that is electrically/mechanically feasible is unknown until
G2–G4. A successful logical Linux recovery at G7 does not prove early-boot
recovery; G8 is the independent-recovery proof for damaged U-Boot.

### Global abort conditions

Stop, depower safely if applicable, preserve logs and reassess whenever:

- any identity, geometry, voltage, pinout, RAM range or partition ownership
  differs from the approved record;
- current rises unexpectedly, a component heats, power becomes unstable, a
  probe slips, or bus contention is suspected;
- a tool proposes erase/program/mark-bad/BBT update/OTP/fuse/security-state
  change during a read stage;
- raw/OOB exposure is unavailable, a programmer silently remaps bad blocks, or
  read hashes/maps disagree;
- ECC reports an uncorrectable page or correction behavior changes across
  reads;
- a command or reset path has side effects not predicted by the reviewed plan;
- secure boot/authentication status is unknown for the proposed RAM image;
- the original NAND, unique identity/calibration or both protected backup
  copies would be the only remaining recovery source; or
- remaining usage, lab time or operator attention is insufficient to complete
  the current atomic operation and save its evidence safely.

## Equipment and cost envelope

Prices below are public examples checked on 2026-10-19, excluding tax,
shipping and the matching spare. They are planning anchors, not purchase
recommendations or proof of compatibility.

| Item | Purpose and minimum property | Evidence / current cost | Decision |
| --- | --- | --- | --- |
| Exact Class A spare | Sacrificial platform; seller must prove `IPC_523128M8MP` before purchase | No reliable first-party price was exposed; cost remains TBD | Request seller evidence and approval; do not substitute another RLC-811A revision |
| High-impedance meter/logic capture | Measure idle voltage and receive-only UART/SPI timing before driving | Saleae lists Logic 8 at USD 499 with digital/analog capture; cheaper tools may exist but require independent input-threshold/protection review | Optional professional reference; equipment already owned may be used if specifications pass |
| USB-UART adapter | Later console RX/TX only after voltage is known | Adafruit lists a CP2102/PL2303 3.3 V logic cable at USD 9.95; its red lead supplies 5 V | The 5 V lead must remain disconnected; 3.3 V must not be assumed until measured |
| Current-limited isolated supply / PoE fixture | Controlled power and fault-safe cutoff | Exact safe bench/PoE equipment and price remain TBD; ordinary adjustable adapters without current limiting are inadequate for board work | Select only after board power topology is known |
| SPI-NAND-capable programmer | Raw data+OOB read/write, bad-block preservation, exact-device support and readback verify | DediProg lists SF100 at USD 275 but labels the product SPI **NOR**; therefore it is not qualified for the unknown target NAND. A WSON socket example is USD 255 and is package-specific | Do not buy until the exact chip appears in the supported-device list and raw OOB/BBT semantics are demonstrated |
| Rework/fixture/microscope/ESD tools | Safe board opening, isolation or off-board chip handling | Package and board are unknown; obtain a professional quote after G2 | Prefer professional rework over in-circuit contention or improvised clipping |
| Encrypted storage | Two protected copies plus working space and logs | Capacity is small relative to modern media, but encryption/physical separation matter more than price; use existing approved storage if available | Must exist before G4; never cloud-sync unique dumps by default |

The honest budget is therefore **spare price + existing lab equipment or a
professional lab quote**. The only defensible public examples span USD 9.95
for a UART cable, USD 499 for a professional logic analyzer, and USD 275 plus a
package adapter for a programmer that is not yet proven suitable. Quoting a
low all-in recovery price before the NAND package/support and rework method are
known would be misleading.

## Required unknowns before D2 can be proposed

- Exact main-board revision, SoC marking, DRAM part/capacity, NAND
  manufacturer/part/package and measured geometry.
- NAND ECC strength/step/layout, OOB allocation, factory/runtime BBM and BBT
  semantics, read-retry behavior and whether an external tool can preserve all
  of them.
- UART pad map, logic level, boot output, RX acceptance and reliable
  interruption timing.
- Ethernet PHY/pinmux/MAC source and whether TFTP is usable from the shipped
  U-Boot on an isolated network.
- microSD electrical routing/pinmux and whether shipped U-Boot can use it.
- Boot-ROM entry method, transport/protocol, secure-boot/eFuse/OTP state and
  accepted loader authentication.
- Ownership and restore semantics of `fdt.restore`, `uenv`, `para`, `sp`,
  `ext_para`, `download`, calibration, keys and device identity.
- Feasibility of preserving the original NAND while testing an exact clone.
- A professional rework/programmer quote and a verified exact-revision spare
  offer.

## Authoritative references

- [Reolink device system-information guide](https://support.reolink.com/articles/360011977034-How-to-Find-out-Reolink-Device-System-Information/) — model, hardware number and firmware-version evidence.
- [Reolink firmware update guide](https://support.reolink.com/articles/900004568363-Reolink-Firmware-Update-Guide/) — firmware selection requires model plus hardware version.
- [Reolink RLC-811A product specification](https://reolink.com/us/product/rlc-811a/) — product-level power, Ethernet, microSD and lens facts only.
- [Linux MTD NAND interface](https://docs.kernel.org/6.4/driver-api/mtdnand.html) — OOB operations, ECC and bad/reserved-block semantics.
- [Linux UBIFS/UBI overview](https://docs.kernel.org/filesystems/ubifs.html) — NAND eraseblocks, wear/bad-block behavior and UBI abstraction.
- [`mtd-utils` `nanddump` source](https://git.infraroot.at/mtd-utils.git/tree/nanddump.c?h=v2.1.0&id=d8b8f780ec3c916f3990e9227d6bfbb22bf42ef8) — explicit ECC/OOB/bad-block mode behavior and version warning.
- [U-Boot `bootm`](https://docs.u-boot.org/en/stable/usage/cmd/bootm.html), [`fatload`](https://docs.u-boot.org/en/stable/usage/cmd/fatload.html), and [environment/network variables](https://docs.u-boot.org/en/latest/usage/environment.html) — generic load/boot behavior, not board proof.
- [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) — SHA-256 integrity standard.
- [Saleae Logic 8](https://store.saleae.com/products/logic-8), [Adafruit USB-TTL cable](https://www.adafruit.com/product/954), and [DediProg SF100](https://dediprog.com/product/SF100) — dated capability/price examples, not purchasing approvals.

## D1 completion decision

D1 selects no recovery mechanism because no physical interface or NAND part is
verified. The strongest intended independence boundary is an exact-device raw
external programmer or authenticated Boot-ROM route; U-Boot UART plus TFTP/MMC
is a useful Linux-independent secondary path but cannot recover damaged U-Boot.
The next safe action is not hardware access: it is an owner review of this plan
and, if desired, explicit authorization for **D2a acquisition research only**
to locate a returnable exact-hardware spare and obtain redacted seller proof.

## D1.4 focused verification

- The machine-readable JSON parses and contains the exact target, ten ordered
  approval gates, minimum two identical independent raw reads, and false values
  for recovery proof, camera contact, flash read and flash write.
- All local Markdown links in the D1 plan, roadmap and recovery requirements
  resolve. External facts were checked against the authoritative references
  listed above on 2026-10-19.
- The plan contains no camera address, credential, UID, MAC, private key,
  proprietary binary, dump or device-specific secret.
- `git diff --check` passes. No application or firmware source changed, so the
  previously passing 77-test C3 baseline was preserved rather than rerun.
- No camera, other network device or firmware binary was accessed or executed.

## D1 completion recommendation

- **Completed:** exact spare-match criteria, full raw/OOB backup specification,
  multiple-read/hash acceptance rules, recovery-candidate priorities, a
  nine-gate spare protocol, abort conditions, unknowns and bounded costs.
- **Checkpoint:** the design checkpoint is `0ba4303`; commit and push this
  completed sanitized plan, machine-readable checklist, state and handoff.
  Private kernel/rootfs/UI work remains unchanged.
- **Next task:** **D2a acquisition research only**, if explicitly authorized —
  identify a returnable `RLC-811A / IPC_523128M8MP` spare offer and request
  redacted device-info/label evidence. No purchase or hardware contact is
  implied.
- **Recommended model and reasoning:** Medium.
- **Why:** D2a is bounded sourcing and evidence collection against the fixed
  checklist, not yet hardware reverse engineering.
- **When to switch:** High is appropriate for G1–G5 electrical/backup planning;
  Ultra only for a narrowly scoped persistent Boot-ROM or recovery-architecture
  uncertainty after checkpoint and explicit selection.
- **Usage preparation:** D1 is a complete safe checkpoint. Reliable closeout
  telemetry on 2026-10-19 showed 62% five-hour usage (38% remaining) and 47%
  weekly usage (53% remaining). Refresh before D2a or any physical stage and
  checkpoint again before each separately approved gate.
