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
log. It is limited to 16 KiB and contains a monotonic safe-integer generation,
bounded release identities, state flags and at most one bounded failure code.
Every load validates exact fields, value syntax, state-dependent invariants,
regular-file type and canonical encoding. Every accepted transition validates
and synchronously writes a same-directory temporary record before replacing
the prior file; a rejected transition changes neither memory nor disk.

This normal atomic-replacement path is not a power-loss guarantee. B4 must
separately test interrupted writes and recovery from damaged/stale records.
The simulator deliberately defines no redundant boot metadata, attempt counter,
NAND geometry, inactive-slot mapping, or physical recovery action.

## Focused verification

Run:

```powershell
python -m unittest tests.test_update_state_simulator -v
```

The tests use only synthetic release identities and manually constructed B2
results. They cover deterministic success, rejection, independent simulation
authorization, boot failure outcomes, known-good preservation, invalid
transitions, mid-sequence reload, bounded/canonical persistence and generation
exhaustion. Power-loss and interrupted-write fault injection remain B4.
