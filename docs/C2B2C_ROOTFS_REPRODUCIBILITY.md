# C2b-2c rootfs reproducibility and legal-info verification

**Status:** COMPLETE — one clean, bounded, single-threaded reproduction build
generated the same normalized minimal ARM hard-float filesystem as C2b-2b-3.
The two raw tar hashes differ only through expected build timestamps, including
four bytes in BusyBox's generated version banner. Buildroot legal-info was
generated and inspected; its remaining compliance gaps are recorded below.

**Scope:** host-only Buildroot verification. This task did not rebuild the
kernel, combine kernel/rootfs/FDT artifacts, assemble firmware, execute an ARM
target binary, or contact a camera.

## Frozen inputs and checkpoint

Git began clean at pushed checkpoint `d63c138`. Before compilation, the new
output configuration was proven byte-identical to the original and the input
state was pushed as checkpoint `1ad67c4`.

| Input | Verified value |
| --- | --- |
| Buildroot source | 2019.05.2 corrected private tree from C2b-2b-3 |
| Frozen public defconfig | `configs/c2b2b_minimal_rootfs_defconfig` |
| Original and reproduced resolved `.config` | SHA-256 `ccda34efa8c3f1144ba3d9771c9099eed0ab0ee3299cb1e04439c5ceffd686eb` |
| Existing toolchain | GCC 6.5.0 ARMv7-A/EABI5 hard-float from C2b-1 |
| Private source cache and patches | Reused unchanged from C2b-2b-3 |
| Original output | `/home/firmware-analysis/slot20_private/c2b2b_20261018/rootfs-out/` |
| Clean reproduction output | `/home/firmware-analysis/slot20_private/c2b2c_20261018/rootfs-out/` |

Buildroot's already documented new-output bootstrap behavior made the first
lightweight `defconfig` invocation create `.br-external.mk` and stop. The
second invocation succeeded. Those were configuration steps, not rootfs build
attempts. Their private log SHA-256 values are
`4b5aca5504abbc8f31865efe864f553fe993efb0b306a16ac035ca6e7621dd66`
and `e891ac096d48fe3cc2bdee7462d25c905c2e10f5f48fa0945513972e3acc59e5`.

## Controlled reproduction build

Exactly one rootfs build was run with `-j1` under a 1,800-second timeout. It
completed with exit status zero in 3 minutes 10.17 seconds and used 162,992
KiB peak resident memory. No make or compiler process remained afterward.

| Property | Original C2b-2b-3 | Clean C2b-2c reproduction |
| --- | --- | --- |
| Artifact size | 3,696,640 bytes | 3,696,640 bytes |
| Tar entries | 374 | 374 |
| SHA-256 | `df413f6a805fb7c860b1ae1043416f225ffe18bfd32f5ffdf09be491e650e06a` | `b039fa2476051258dce8e4fb0977925be64d3ef84e19c591a1cbfe4ccd1cf635` |
| Complete `tar -tf` scan | Passed | Passed |
| Build configuration | `ccda34ef...686eb` | `ccda34ef...686eb` |

The original artifact's size and hash were checked before and after the task;
it was not modified. The reproduction build log and time-record hashes are
`7c9c25509163140127039d08575c608bf5401959599da7b4f8863f18e071aa98`
and `5702bc555097205ae7fcf73c3540a326526594f2f8cd0b8637457d4f8a39a97b`.

## Filesystem comparison

The comparison used sorted archive path lists, regular-file SHA-256 manifests,
and full numeric-owner tar listings. Timestamps were removed only from a
second pair of metadata listings; the original archives were not rewritten.

| Check | Result |
| --- | --- |
| Paths and order | All 374 entries identical; both lists hash to `07d42b358a184e86546c8584341c013f15260a0cd1cbc495c68345dac3d1f966` |
| Types, permissions, numeric UID/GID, sizes, links and device metadata | Identical after timestamp normalization; both manifests hash to `d02c1847fd7bc0dd0597e7f8dfbc2ec2ab85a58f4a5baf28d36560443bde3010` |
| Timestamp comparison | 337 entries differ and 37 retain identical raw metadata, as expected from independent builds and copied inputs |
| Regular files | 41 compared; 40 byte-identical and only `bin/busybox` initially differs |
| Dynamic loader | Identical SHA-256 `fcd7690fbd7780eda4fabf65641e99dc7ac81b2a15d98f9a9c41e77205b74034` |

Original BusyBox SHA-256 is
`1b5d8379d0694c8f0e1ab716b83a0a26e68c754ed6f8442f024cf6396856240f`;
the reproduction is
`92fa336b1f86e9a8dc5852275014a7bb0161696a7915ffeff74171825ec0c718`.
`cmp -l` finds exactly four differing bytes, all within these banners:

```text
BusyBox v1.30.1 (2026-10-18 15:37:48 PDT)
BusyBox v1.30.1 (2026-10-18 15:56:33 PDT)
```

Replacing only that fixed-length timestamp text in private comparison copies
makes both BusyBox files byte-identical at SHA-256
`9bd2c66613c0d14122192a11529385bd9ca678ad0f4e93106d27374edbd6514c`.
The differing raw tar hashes are therefore explained by archive timestamps and
this embedded build-time banner; normalized filesystem content is reproduced.

The reproduced BusyBox remains an ELF32 little-endian ARM EABI5 executable,
ARMv7, dynamically linked through `/lib/ld-linux-armhf.so.3`, with hard-float
VFP register arguments. This is static architecture evidence, not evidence of
camera compatibility or successful target execution.

## Buildroot legal-info

`make -j1 legal-info` ran separately after the build and exited zero in 8.68
seconds. It did not change the reproduced rootfs hash. The generated records
remain private under `rootfs-out/legal-info/`.

| Set | Version and declared license | Source record |
| --- | --- | --- |
| Target BusyBox | 1.30.1, GPL-2.0 | Archive, three Buildroot patches and license copied |
| Buildroot | 2019.05.2, GPL-2.0+ | License copied; source tree not copied into legal-info |
| patchelf | 0.9, GPL-3.0+ | Source and four patches copied |
| acl | 2.2.53, GPL-2.0+/LGPL-2.1+ | Source/patch copied; license files copied without package-hash entries |
| attr | 2.4.48, GPL-2.0+/LGPL-2.1+ | Source/two patches copied; license files copied without package-hash entries |
| autoconf | 2.69, GPL-3.0+ with exceptions | Source/patch and licenses copied |
| libtool | 2.4.6, GPL-2.0+/LGPL-2.1+ | Source and licenses copied |
| m4 | 1.4.18, GPL-3.0+ | Source and three patches copied |
| automake | 1.15.1, GPL-2.0+ | Source/patch and license copied |
| fakeroot | 1.20.2, GPL-3.0+ | Source/five patches and license copied |

The target manifest contains BusyBox; the host manifest contains Buildroot and
eight versioned host packages. Five target-source files, 32 host-source files,
one target license and 13 host-license files were collected. Key hashes are:

- `manifest.csv`: `8f09c76e97560edc26e855cdae0e3259c89b05b4ef4c3ec0080d572198e7bee3`
- `host-manifest.csv`: `1c8886b46406b59bba0bcfae410277271f9d85b0509b28024db27ed7f672f8ec`
- `buildroot.config`: `ccda34efa8c3f1144ba3d9771c9099eed0ab0ee3299cb1e04439c5ceffd686eb`
- `legal-info.sha256`: `e198a368fe038c01d92b91349cc58ab956a322a989dce953bb258701409ee96f`
- legal-info log/time: `56f41bf28cd9e0c514a687d71c254e344a9d9404bdb488d430ca738e09357828` /
  `b236d88303ad802cefb882f46ea33665c4b93a0c4b55e30bdb9a621d3f0894be`

Legal-info is useful evidence, but it is not a complete redistribution bundle.
It warns that Buildroot's own source was not saved, lists the external custom
toolchain only as an unknown dependency rather than collecting its sources and
licenses, and reports that the legacy acl/attr license files lack package hash
entries. The C2b-1 manifest separately records toolchain origins and hashes,
but a future distributable system must close these legal-info gaps and review
all licenses; this document is not legal advice.

## Conclusion and boundaries

The frozen configuration and compatibility patches reproducibly generate the
same normalized minimal userspace in a clean output directory. Exact raw-byte
reproducibility is not yet configured because timestamps are not normalized
and BusyBox embeds its build time. No missing file, architecture, permission,
ownership, link, or unexplained content discrepancy was found.

Both private build trees, tar files, logs, normalized comparison copies and
legal-info outputs must be preserved. None is committed to the public
repository. No private Reolink FDT, proprietary camera binary, camera data,
kernel artifact or firmware package was used or produced by this task.

## Next-stage recommendation

- **Completed:** C2b-2c independently reproduced and compared the frozen
  rootfs and generated/inspected Buildroot legal-info.
- **Checkpoint:** pre-build commit `1ad67c4` is pushed; the final sanitized
  documentation/result commit is the completion checkpoint. Both private
  rootfs trees and all logs remain preserved off-Git.
- **Next task:** C3 — build and demonstrate the local browser management UI
  against the host-only update simulator, including clearly labeled status,
  validation/update, rollback/error and recovery-explanation screens.
- **Recommended model and reasoning:** Medium.
- **Why:** C3 is routine host-only application/UI implementation against an
  existing deterministic simulator; it does not require another Linux build
  or bootloader reverse engineering.
- **When to switch:** Use High if authentication, signed-bundle integration or
  simulator state handling exposes a non-routine implementation/debugging
  problem. Ultra is not indicated unless a later recovery-critical hardware
  uncertainty must be resolved.
- **Usage preparation:** the expensive build is complete and checkpointed.
  Create a small C3 design/source checkpoint before implementing substantial
  UI behavior; do not begin C3 in this task.
