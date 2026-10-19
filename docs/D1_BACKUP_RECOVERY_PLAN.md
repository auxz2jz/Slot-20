# D1 matching-spare backup and independent-recovery plan

**Status:** DESIGN CHECKPOINT — planning only. No camera has been contacted,
opened, powered, rebooted, connected to UART, read from or written. This
document will not authorize a physical operation or firmware installation.

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
