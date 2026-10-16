# Host-only update-state simulator

`tools/update_state_simulator.py` is the Task B3 logical state model. It has no
camera, network, device-node, partition or flash-writing interface. Its
`writing_candidate`, `rolled_back` and `recovery_required` names are simulated
decisions only: they do not prove an A/B layout, a working boot selector, or an
independent recovery method.

## Normal paths

```text
idle -> receiving -> verifying -> verified -> staged
     -> writing_candidate -> pending_boot -> healthy -> committed

pending_boot -> failed -> rolled_back
                       -> recovery_required

verifying -> failed -> idle (rejected candidate discarded)
```

The known-good release remains unchanged through receive, verification,
staging, candidate-write, pending-boot and failure states. A healthy candidate
becomes the new known-good release only at `committed`; the former known-good
identity is retained as `previous_known_good`. Selecting `rolled_back` records
the logical choice of the known-good version but does not claim the camera can
perform that selection.

## Verification and authorization boundary

A passing B2 `VerificationResult` may move `verifying` to `verified` only when
its bundle digest and signed release identity match the candidate record. The
B2 result cannot grant installation permission. Staging additionally requires
a separate `SimulationInstallAuthorization` with:

- the exact candidate bundle SHA-256;
- an explicit approval boolean and bounded approval identifier; and
- the literal `host-simulation-only` scope.

This object authorizes a simulator transition only. It is not a production
policy, user approval for camera access, or permission to write firmware.

## Persisted record

The simulator keeps one canonical JSON record rather than an unbounded event
log. Version 2 is limited to 16 KiB and contains a monotonic safe-integer
generation, bounded release identities, state flags, at most one bounded
failure code, and a domain-separated SHA-256 checksum over the other record
fields. The checksum detects accidental corruption; it is unkeyed and is not
authentication against an attacker who can rewrite the record.

Every load validates exact fields, checksum, value syntax, state-dependent
invariants, regular-file type and canonical encoding. A caller that maintains
a trusted generation floor outside this single file may pass it as
`minimum_generation`; older records are then rejected. Without that external
anchor, a stale but otherwise valid record cannot be distinguished from the
latest record.

Every accepted transition validates and synchronously writes a same-directory
temporary record before replacing the prior file; a rejected transition changes
neither memory nor disk. The simulator deliberately defines no redundant boot
metadata, attempt counter, NAND geometry, inactive-slot mapping, or physical
recovery action.

## B4 file-fault results

These are deterministic host-filesystem simulations, not power-loss guarantees
for NAND, a bootloader, controller caches, or camera hardware.

| Simulated failure | Observed result | Simulator classification |
| --- | --- | --- |
| Abrupt interruption before temporary-file `fsync` | Prior primary remains valid; orphan temporary data is ignored | Recoverable by loading the prior primary |
| Abrupt interruption after temporary `fsync` but before replacement | Prior primary and known-good identity remain valid; orphan is ignored | Recoverable by loading the prior primary |
| Interruption immediately after replacement | Replacement is a complete checksummed record; process memory may be stale | Recoverable by restarting and loading the new primary |
| Ordinary replacement I/O error | Temporary file is removed and prior primary remains valid | Recoverable by loading the prior primary |
| Truncated, checksum-corrupt, or checksum-valid but invariant-invalid primary | Load is rejected | External trusted state/recovery is required |
| Missing primary, including when an orphan temporary exists | Load is rejected; orphan is never promoted automatically | External trusted state/recovery is required |
| Older complete primary | Accepted without an external floor; rejected when below a supplied trusted floor | External generation anchor/reconciliation is required to detect staleness |

“External recovery” here means restoring or reconstructing a separately trusted
state and known-good identity outside this simulator. No such storage or action
is implemented, and these results do not prove that the physical camera can
select or restore any firmware image. The post-replacement test models a call
boundary only; the implementation does not claim portable directory-entry
`fsync` semantics or persistence across a real host or device power failure.

## Focused verification

Run:

```powershell
python -m unittest tests.test_update_state_simulator tests.test_update_state_faults -v
```

The tests use only synthetic release identities and manually constructed B2
results. The B3 tests cover deterministic success, rejection, independent
simulation authorization, boot failure outcomes, known-good preservation,
invalid transitions, mid-sequence reload, bounded/canonical persistence and
generation exhaustion. `tests/test_update_state_faults.py` adds deterministic
B4 interruptions, partial/missing/stale/corrupt records, checksum enforcement,
external generation-floor checks and the recovery classifications above.
