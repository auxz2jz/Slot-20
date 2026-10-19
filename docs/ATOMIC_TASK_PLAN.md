# Slot-20 — Small-task execution plan and interruption-safe handoff

**Status:** planned tasks, NOT evidence of implementation. **Scope:** Reolink RLC-811A `IPC_523128M8MP`. This file complements `AGENTS.md`, `docs/STATE.md`, `docs/BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`, and the recovery-first roadmap. It does **not** import all Master Instruction Library frameworks.

## Intent

Replace open-ended "analyze the bootloader" or "build the firmware" runs with **one narrow deliverable at a time**. Each task must be independently verifiable, resumable, and small enough to finish and checkpoint before launching another substantial operation. For demanding/research-heavy work, aim for a **2–5 minute logical slice** or a single bounded investigation, not a guaranteed execution time or token quota. If a step proves larger, split it again *before* running a long tool operation. Do not break up an atomic flash/file write in progress; **no camera writes are currently authorized**.

**The user stopped an Ultra session after reported remaining usage fell from ~73% to ~3%.** Its local changes are UNKNOWN until checked on the Windows computer. **Task R0 is required first**, without replaying the interrupted analysis.

## Task sequencing and acceptance criteria

One task should have a specific input, one main output, and a verification criterion. Later tasks are provisional; revise based on real evidence rather than assuming generic Novatek bootloader capabilities.

| ID | Next small task | Deliverable and completion check | Suggested reasoning |
| --- | --- | --- | --- |
| **R0 (FIRST)** | Recover interrupted Ultra session from local Git/files and existing output | Identify tracked/untracked changes, preserve useful findings safely, record exact next action, and push sanitized, **verified** content; do not re-run bootloader analysis | **Medium** |
| A1 | Inventory **actual packaged Reolink** U-Boot section and its verified offsets, size, hashes, architecture and entry-point clues | Small evidence table with exact artifact hash and bounded commands; no execution of recovered firmware | High |
| A2 | Inspect only bounded U-Boot strings/command table candidates for boot, UART, network recovery and flash operations | Evidence-backed list: present / absent in inspected region / uncertain, with offsets or references; no inference that exposed commands are usable | High |
| A3 | Trace the actual boot image selection and validation code along ONE focused path | Narrow static-analysis report with cited binary offsets/disassembly and verified vs hypothesized steps; split again if needed | High; Ultra only for a **specific unresolved control-flow question** |
| A4 | Analyze actual environment location/boot arguments relative to package FDT and generic BSP | Explicit mismatch/partition ownership report; never copy generic U-Boot offsets into camera instructions | High |
| A5 | Review possible independent rescue routes and identify minimum missing evidence | Recovery candidate matrix and specific test-hardware requirements; **not** proof of working UART/TFTP/ROM/programmer | High; Ultra only for a narrowly scoped hard question |
| B1 | Define a **host-only** compatible signed update-bundle format | Minimal schema with board ID, size bounds, versions, signature and hashes; security assumptions stated | Medium–High |
| B2 | Implement **host-only** bundle verification and negative unit tests | Reject bad signatures, truncated payloads, mismatched hardware and over-limit sizes without writing flash | High |
| B3 | Implement small file-backed boot/update-state simulator | Deterministic state transitions and basic tests; no real NAND or camera access | High |
| B4 | Add bounded interrupted-write/power-loss fault tests to simulator | Recorded pass/fail evidence for selected transitions; simulator results explicitly not hardware proof | High |
| C1 | Audit required Novatek BSP build inputs, shipped binary objects, licensing and cross-compiler ABI | Dependency/toolchain decision with licensing and reproducibility caveats | High |
| C2a | Freeze BSP/Buildroot/toolchain inputs and run a disposable configuration/`prepare` preflight | Repeatable input manifest and preflight, or one exact blocker; no rootfs or image assembly | High |
| C2b-1 | Materialize the pinned cross-toolchain/host prerequisites and repeat kernel configuration/`prepare`, only after C2a | Two matching preflight passes or one new exact blocker; no kernel/rootfs assembly | High |
| C2b-2a | Attempt one generic Novatek kernel compile/link pass with the verified C2b-1 inputs | Reproducible compile result or one exact source/blob/link blocker; no rootfs, package or hardware claim | High |
| C2b-2a-2 | Resolve C2b-2a's host-DTC `yylloc` blocker with an upstream-provenance compatibility change, correct the disposable output layout, then make one further bounded compile/link attempt | Host fix and layout evidence plus a compile result or one next exact blocker; no rootfs, package or hardware claim | High |
| C2b-2a-3 | Supply a provenance-recorded host OpenSSL development input and resume the configured C2b-2a-2 tree for one further compile attempt | Verify `openssl/bio.h` plus compatible host `libcrypto`, then one `-j1` result or one next exact blocker; no rootfs, package or hardware claim | High |
| C2b-2a-4 | Correct the vendor `nvtversion.h` rule's non-POSIX shell behavior in the private tree and make one further bounded compile attempt | Valid regenerated header plus one `-j1` result or one next exact blocker; determine whether later `pci_iomap` diagnostics persist | High |
| C2b-2a-5 | Correct the NA51055 shipped-PLL Kbuild object name privately and make one further bounded compile attempt | Verify `pll.o` materialization/archive membership and symbol provider, then one `-j1` result or one next exact blocker; binary blob remains non-redistributable | High |
| C2b-2a-6 | Supply a provenance-recorded host `lz4c` and resume the preserved linked kernel tree for one bounded compression/build attempt | Verify host utility version/hash, then one `-j1` result producing generic `zImage` or one next exact blocker; no rootfs, package or hardware claim | High |
| C2b-2b | Produce a **minimal offline** rootfs prototype only after the kernel compile boundary is understood | Reproducible host-side rootfs artifact and license inventory; no firmware assembly, device boot, flashing or recovery claim | High |
| C2b-2b-1 | Resolve C2b-2b's host-fakeroot/glibc compatibility blocker with an authoritative patch in the disposable private tree, then make one continuation attempt | Verified rootfs tar or one next exact blocker; preserve frozen config/source hashes and keep kernel/FDT separate | High |
| C2b-2b-2 | Resolve C2b-2b-1's host-m4 1.4.18 `SIGSTKSZ` compatibility blocker with an authoritative public-source correction, then make one continuation attempt | Verified rootfs tar or one next exact blocker; preserve completed host work and keep kernel/FDT separate | High |
| C2b-2b-3 | Resolve C2b-2b-2's fakeroot autoreconf failure caused by the missing declared `build-aux` directory, then make one continuation attempt | Verified rootfs tar or one next exact blocker; preserve the patched fakeroot tree and keep kernel/FDT separate | High |
| C2b-2c | Reproduce the frozen minimal rootfs in a second clean private output tree and generate/check Buildroot legal-info | Normalized content comparison, artifact/hash variance explanation and complete license/source record; no kernel/FDT combination or firmware assembly | High |
| C3 (COMPLETE) | Implement and demonstrate local browser management UI **against simulator only** | PC-hosted screenshots for status, firmware validation/update, rollback/errors and recovery explanation; label offline demo | Medium–High |
| C3.1 (COMPLETE) | Freeze the host-only UI architecture, security/evidence boundary, API and tests | Design checkpoint pushed before application implementation | Medium |
| C3.2 (COMPLETE) | Implement loopback authentication/status server and static dashboard shell | Authentication, session and CSRF boundary tests pass | Medium |
| C3.3 (COMPLETE) | Integrate B2 verification and B3 simulated update/rollback/recovery actions | Synthetic success, rejection and transition tests pass; no installer/device path | Medium–High |
| C3.4 (COMPLETE) | Run browser demonstration and capture labeled screenshots, then finalize handoff | Required UI states shown, regression tests pass and sanitized completion is pushed | Medium |
| D1 (COMPLETE; PLANNING ONLY) | Define a non-destructive matching-spare, complete-backup and independent-recovery plan | Written plan only; no camera contact, opening, UART, NAND access, reboot or write | High |
| D1.1 (COMPLETE) | Freeze matching-spare requirements and the evidence inventory | Acquisition/inspection checklist separates seller evidence, read-only observations and still-unknown internals | High |
| D1.2 (COMPLETE) | Specify complete NAND/data backup and verification | Data/OOB/ECC/bad-block/factory-data preservation plus multiple-read/hash acceptance criteria | High |
| D1.3 (COMPLETE) | Rank independent-recovery candidates and define the spare test protocol | Independence boundaries, equipment, costs, aborts and approval gates; no route called proven | High |
| D1.4 (COMPLETE) | Review safety/evidence boundaries and close D1 | Focused doc checks, sanitized pushed checkpoint and exact next approval-gated task | Medium |
| D2a (BLOCKED) | Locate a returnable exact-revision spare and request redacted seller evidence | **Explicit fresh user authorization** for sourcing; no purchase or device contact implied | Medium |
| D2b+ (BLOCKED) | Acquire/open/contact a matching spare and begin approved observations | **Explicit fresh user approval** for each physical stage; complete plan and abort conditions reviewed first | High/Ultra for specific questions |

**Not yet authorized / not eligible for a persistent camera image:** video/ISP/zoom/ALPR features; modifying production camera; altering bootloader/calibration/factory data; claiming A/B, TFTP or factory fallback as proven. All physical work remains behind documented consent and recovery gates.

## Execution contract for each small task

1. Inspect only `AGENTS.md`, the compact current handoff, `docs/STATE.md` sections relevant to this task, and `git status --short`/`git log -1`. If working tree is dirty, reconcile and preserve first. Avoid reading all prior chats.
2. Select **one** task ID. State the exact output and minimal pass criterion. Treat stored artifacts and previous tests as reusable evidence. Before expensive binary analysis or build, create a quick safe checkpoint.
3. Perform focused work; bound output and avoid broad recursive searches, parallel agents or repeating extraction. Stop after two equivalent failures and log blocker.
4. Perform the smallest meaningful verification. Clearly label VERIFIED / PARTIAL / UNVERIFIED, including when hardware is **never tested**.
5. Update the project handoff file `docs/NEXT_TASK_HANDOFF.md` (and `docs/STATE.md` only for significant new facts), preserve meaningful verified code/docs with a safe Git checkpoint/push, and record any untracked/private items requiring a separate protected backup. Do not commit proprietary binaries, secrets or full flash dumps.
6. Give a **brief output**: completed task ID; result/tests; Git commit + push status; exact next task ID; recommended reasoning; and continue/stop decision. No long transcript.

## Reliable-usage gate before launching another task

- **If an actual current remaining account-usage percentage is reliably visible to the agent:** above 50% = small tasks may continue sequentially after verified checkpoint; 30–50% = prefer routine/High tasks, with a saved checkpoint before each; 15–30% = finish current safe operation, checkpoint, then **do not launch a substantial new task**; under 15% = **checkpoint and stop**. Never auto-start another Ultra task when usage is at or below 50%.
- **If usage cannot be observed reliably (common):** do **not** invent an estimate based on time, token count, context-window size, number of turns, or the user's earlier percentage. Treat usage as UNKNOWN. **Stop after one costly analysis/build/Ultra-sized task**, or after at most two genuinely small Medium/High tasks, saving a checkpoint first. Ask the user to check the usage meter before further expensive work. A user-provided percentage is a snapshot, not live telemetry.
- **Before any Ultra task:** require a narrowly scoped question, a prior checkpoint, and explicit user selection of that reasoning level; never open an unlimited investigation and assume an instruction can enforce a time/token cap. Prefer High for initial focused static analysis.
- **If the limit is reached mid-task:** no fake success, no retries, no automatic scheduled continuation claim. Next session starts with handoff + real Git status, preserving any partial work.
- These thresholds are conservative **workflow decisions, not platform-enforced usage controls**; one heavy operation may still consume substantial allowance before it can be stopped.

## Handoff format (write to docs/NEXT_TASK_HANDOFF.md; update, do not append forever)

```text
LAST TASK ID / STATUS:
EVIDENCE AND TESTS:
GIT BRANCH / COMMIT / PUSHED?:
LOCAL UNTRACKED OR PRIVATE WORK (NO SECRETS):
NEXT SINGLE TASK ID + INPUT:
PASS CRITERION FOR NEXT TASK:
RECOMMENDED REASONING + WHY:
USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:
CONTINUE OR STOP + REASON:
CAMERA CONTACT/FLASH: NONE (unless separately approved and accurately recorded)
```

**Hand off, not handshake:** a durable, minimal written record telling the next agent exactly where to resume. When restarting, compare that note to actual Git/local evidence; it may be stale if a quota interruption happened before the final save. Updating this plan never retroactively certifies unpublished work done by the interrupted Ultra session.
