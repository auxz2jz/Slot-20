# C2b-2c rootfs reproducibility and legal-info verification

**Scope:** independently rebuild the frozen minimal Buildroot root filesystem
in a second clean private output directory, compare both filesystem artifacts,
and inspect Buildroot legal-info. This task does not rebuild the kernel,
combine kernel/rootfs/FDT artifacts, assemble firmware, execute ARM target
code, or contact a camera.

## Pre-build checkpoint

Git began clean at pushed checkpoint `d63c138`.

The original successful artifact remains at
`/home/firmware-analysis/slot20_private/c2b2b_20261018/rootfs-out/images/rootfs.tar`.
It was rechecked before creating the reproduction tree:

| Property | Preserved value |
| --- | --- |
| Size | 3,696,640 bytes |
| SHA-256 | `df413f6a805fb7c860b1ae1043416f225ffe18bfd32f5ffdf09be491e650e06a` |
| Resolved `.config` SHA-256 | `ccda34efa8c3f1144ba3d9771c9099eed0ab0ee3299cb1e04439c5ceffd686eb` |

The separate clean output tree is:

`/home/firmware-analysis/slot20_private/c2b2c_20261018/rootfs-out/`

It reuses the corrected Buildroot 2019.05.2 source tree, cached source
archives, existing GCC 6.5.0 ARM hard-float toolchain, host utility paths and
the frozen public defconfig. It does not reuse the original task's output
directory.

Buildroot's known new-output bootstrap behavior caused the first lightweight
`defconfig` invocation to create `.br-external.mk` and stop because that file
did not exist when Make evaluated dependencies. A second `defconfig`
invocation then succeeded. This reproduces the already documented C2b-2b
configuration-bootstrap behavior and is not a rootfs build retry. The failed
and successful configuration logs are preserved at SHA-256
`4b5aca5504abbc8f31865efe864f553fe993efb0b306a16ac035ca6e7621dd66`
and `e891ac096d48fe3cc2bdee7462d25c905c2e10f5f48fa0945513972e3acc59e5`.

The reproduction `.config` is byte-identical to the original and has SHA-256
`ccda34efa8c3f1144ba3d9771c9099eed0ab0ee3299cb1e04439c5ceffd686eb`.
At this checkpoint, no C2b-2c rootfs build or legal-info target has started.
The next authorized operation is one bounded `-j1` rootfs build after a
reliable usage check.
