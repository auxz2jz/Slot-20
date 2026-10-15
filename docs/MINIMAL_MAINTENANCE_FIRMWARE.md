# Minimal independent maintenance firmware plan

**Status:** offline architecture and acceptance criteria, not an installable image. This plan implements the requirements in `BOOT_UPDATE_RECOVERY_REQUIREMENTS.md`; it does not authorize camera access or flashing.

## Objective

The first persistent custom image must be maintainable even when an update fails. Video, ISP, zoom, audio and AI are deliberately out of scope. The first milestone is a small Linux system that provides predictable Ethernet, authenticated local web management, signed compatible-image updating, boot health confirmation and a separately proven rescue route.

## Proposed foundation

- Use a pinned Buildroot release and checked-in defconfig/board overlay to produce a reproducible ARMv7 hard-float toolchain, kernel, root filesystem and host-side image tools.
- Begin with Novatek's published Linux 4.19.91 NA51055 BSP because it contains the required platform, NAND, Ethernet and watchdog drivers. Treat it as a bring-up base, not a long-term security answer; it is old and contains shipped binary objects that must be audited.
- Reconstruct a board-specific DTS from the matching package, then reduce it to the nodes required for boot, UART diagnostics, NAND, Ethernet and watchdog. A decompiled FDT is evidence, not automatically correct source.
- Keep the root filesystem read-only (for example SquashFS) with a narrowly scoped writable state/configuration volume. Storage format and volume layout are not frozen until NAND geometry and recovery design are proven.
- Build Ethernet, PHY, NAND/UBI and watchdog support into the kernel for the maintenance baseline so recovery-critical startup does not depend on a mutable module filesystem.

A prior private Ubuntu/WSL verification environment recorded `make`, `dtc`, `mkfs.ubifs`, `ubinize`, `dumpimage` and `mkimage`, but no ARM GNU cross-compiler or `qemu-system-arm`. Its availability must be rechecked before a build; no packages were installed during this checkpoint. The exact compiler must be pinned after the BSP's build requirements and ABI are confirmed.

## Runtime components

1. **Early boot and health service**
   - Mount the system read-only, start the watchdog, identify the selected slot/recovery mode, and expose a bounded boot-status record.
   - Mark a candidate image healthy only after local filesystem checks, Ethernet initialization, the management service and the updater service are all ready.
   - Never mark an image healthy merely because the kernel reached userspace.

2. **Predictable Ethernet**
   - DHCP first, with a documented deterministic local fallback after a bounded timeout.
   - Show link, address, board profile and firmware version in the UI without exposing device secrets.
   - No cloud dependency, automatic port forwarding or remote automatic update.

3. **Web management**
   - Run the network-facing service without raw flash privileges. A small privileged updater daemon owns the narrow flash/update API.
   - Require initial credential enrollment or unique credentials; no shared default password. Store a memory-hard password hash using target-benchmarked parameters.
   - Use TLS with a device-unique local certificate, secure session cookies, CSRF protection, request/body limits and login rate limiting.
   - Provide dashboard, version/board identity, upload validation, install progress, pending-boot/health state, previous-version selection and explicit recovery instructions.

4. **Updater**
   - Evaluate SWUpdate first because its upstream design supports Buildroot, UBI/NAND handlers, hardware compatibility, signed descriptions plus component hashes, transaction markers and standalone recovery workflows. RAUC remains a candidate if a genuine redundant-slot layout and compatible boot-selection interface are proven.
   - The web process may stream an upload only to a bounded staging area. It must not choose device nodes or invoke arbitrary scripts.
   - Verify container structure, exact board identifier `IPC_523128M8MP`, image-format version, component size limits, supported upgrade/downgrade relationship, signed manifest and every component hash **before** any erase/write.
   - Keep private signing keys off the camera and out of Git. Embed only the update-verification public key in the protected maintenance/recovery trust base.
   - A locally authenticated rollback may select only a previously verified, still-supported signed image. Never label an arbitrary downgrade safe.

## Update state machine

```text
receiving -> verified -> staged -> writing-inactive -> pending-boot
                                                     |          |
                                                     |          +-> healthy -> committed
                                                     +-> failed/unconfirmed -> rollback or recovery
```

- `receiving`: bounded upload, no flash writes.
- `verified`: signature, hashes, board profile, versions and size limits accepted.
- `staged`: complete durable candidate exists and its hash was rechecked.
- `writing-inactive`: only a proven inactive slot/volume is touched; active and rescue copies remain unchanged.
- `pending-boot`: bootloader gives the candidate a limited number of attempts.
- `healthy`: the new OS explicitly reports all maintenance-critical services ready.
- `committed`: boot metadata is atomically updated.
- `failed/unconfirmed`: bootloader selects the known-good slot or independent recovery without needing the failed Linux/web stack.

Boot metadata needs redundant, CRC-protected records with a monotonic generation number or an equally power-fail-safe bootloader mechanism. The existing `uenv` must not be rewritten until its format, redundancy and ownership are proven. Standard U-Boot `bootcount`/`bootlimit` behavior is only a design reference; it is disabled in the inspected generic NA51055 NAND defconfig and unverified in the Reolink binary.

## Storage layouts to evaluate

| Layout | Advantage | Blocking evidence |
|---|---|---|
| Kernel+rootfs A/B | Simple whole-system rollback | Need space, boot selection, protected metadata and bad-block budget |
| Protected recovery + one active/candidate pair | Rescue remains independent of main Linux | Need immutable recovery selection and enough protected NAND |
| Single main image + external programmer/ROM rescue | Lowest on-device capacity | Not automatic rollback; exact restore process and equipment must be demonstrated |

No layout may consume `download` or device-specific partitions based only on apparent free space.

## Offline verification before any spare-hardware test

- Reproducible Buildroot/kernel/rootfs build with source/toolchain hashes and license manifest.
- Host-side signed-bundle builder and verifier with malformed, truncated, oversized, mismatched-board and bad-signature tests.
- File-backed NAND/slot simulator that models erase blocks, one-way programming, bad blocks, interrupted uploads/writes and power loss at every state transition.
- Updater integration tests proving the active/rescue slots cannot be selected as write targets.
- Boot-state tests for first boot, no health mark, watchdog reset, exhausted attempts, successful commit and rollback.
- PC-hosted management UI demonstration with the mandatory owner-review screens clearly labeled as an offline implementation until hardware-tested.
- Size/RAM/startup measurements against the declared 128 MiB NAND and 112 MiB Linux-visible memory, with a bad-block reserve.

## Next implementation checkpoint

1. Finish board-specific boot/image-validation analysis and resolve whether the shipped U-Boot can safely select a candidate without replacing the bootloader.
2. Audit the official BSP's build dependencies and shipped binary objects; pin a lawful, reproducible toolchain.
3. Define a host-only signed bundle schema and file-backed update-state simulator with fault-injection tests.
4. Build a maintenance-only Buildroot root filesystem and kernel offline. A successful build is not a boot claim.
5. Create the real local web UI and connect it only to the simulator until backup/recovery on a matching spare is authorized and proven.

The independent rescue decision remains the gating item. A working web uploader cannot satisfy that gate by itself.
