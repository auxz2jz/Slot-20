# C2b-2b minimal offline rootfs prototype attempt

**Scope:** freeze a minimal Buildroot 2019.05.2 userspace configuration, reuse
the existing GCC 6.5.0 ARM hard-float toolchain and cached sources, build in a
separate private output tree, and stop at a verified rootfs artifact or the
first exact blocker. This task did not modify the completed kernel, use the
private Reolink FDT, assemble firmware, execute target code, or contact a
camera.

**Result:** COMPLETE WITH ONE REPRODUCIBLE HOST BLOCKER. The normalized minimal
configuration and complete selected source set are frozen and hash-verified.
The single `-j1` build stopped while compiling Buildroot's host-only fakeroot
1.20.2 against Ubuntu glibc 2.39 because `_STAT_VER` is undefined. BusyBox was
not compiled and no rootfs image was created.

## Preserved inputs and isolated workspace

Git began clean at pushed checkpoint `484800c`. The separate private workspace
is `/home/firmware-analysis/slot20_private/c2b2b_20261018/`. It was extracted
from the pinned Buildroot 2019.05.2 archive, SHA-256
`7c0ea9ffc170e19735aed281592fe766e4b698bb139eae851f4f98f024a776b5`,
and reused the existing source cache through hard-linked cache inputs. The
completed kernel directory was neither an input nor an output. Its private
`zImage` and `vmlinux` hashes remain unchanged.

## Frozen minimal configuration

Normalized public defconfig
`configs/c2b2b_minimal_rootfs_defconfig`, SHA-256
`aa78f01fdca1aa1f165185e7d6d9f2483c79a92f2df927fd72efca54914a01a6`,
contains 13 non-default selections. It selects:

- ARM Cortex-A9/ARMv7-A, ARM state, EABI5 hard-float, VFPv3 and NEON;
- the prebuilt external `arm-buildroot-linux-gnueabihf` GCC 6.x/glibc toolchain
  with Linux 4.19 headers, located through the controlled build `PATH`;
- BusyBox 1.30.1 for the shell and init;
- no password-based root login and no getty; and
- an uncompressed rootfs tar, with no Linux kernel or bootloader target.

The resolved `.config`, SHA-256
`ccda34efa8c3f1144ba3d9771c9099eed0ab0ee3299cb1e04439c5ceffd686eb`,
confirms those defaults. The first relative-`O` invocation generated the
out-of-tree wrapper but stopped before `.config`; rerunning configuration with
Buildroot's canonical absolute `O` requirement succeeded. This was a
configuration bootstrap issue, not a rootfs compilation retry. The normalized
defconfig was checkpointed and pushed before source acquisition at `e6f353a`.

## Selected packages, sources, and licenses

No additional target application package is selected beyond BusyBox and
Buildroot's in-tree init/network skeletons. Buildroot `show-info` identified the
following downloaded source packages; each archive passed its Buildroot hash
check:

| Package | Role | Source/origin | License | SHA-256 |
| --- | --- | --- | --- | --- |
| BusyBox 1.30.1 | target userspace | `busybox.net/downloads/busybox-1.30.1.tar.bz2` | GPL-2.0 | `3d1d04a4dbd34048f4794815a5c48ebb9eb53c5277e09ffffc060323b95dfbdc` |
| attr 2.4.48 | host packaging dependency | GNU Savannah `attr-2.4.48.tar.gz` | GPL-2.0+ programs; LGPL-2.1+ libraries | `5ead72b358ec709ed00bbf7a9eaef1654baad937c001c044fe8b74c57f5324e7` |
| acl 2.2.53 | host packaging dependency | GNU Savannah `acl-2.2.53.tar.gz` | GPL-2.0+ programs; LGPL-2.1+ libraries | `06be9865c6f418d851ff4494e12406568353b891ffe1f596b34693c387af26c7` |
| fakeroot 1.20.2 | host rootfs packager | Debian snapshot `fakeroot_1.20.2.orig.tar.bz2` | GPL-3.0+ | `7c0a164d19db3efa9e802e0fc7cdfeff70ec6d26cdbdc4338c9c2823c5ea230c` |
| patchelf 0.9 | host external-toolchain helper | NixOS releases `patchelf-0.9.tar.bz2` | GPL-3.0+ | `a0f65c1ba148890e9f2f7823f4bedf7ecad5417772f64f994004f59a39014f83` |

Buildroot's in-tree `host-makedevs` is GPL-2.0. The in-tree skeleton,
initscripts, ifupdown scripts, and custom-external-toolchain metadata have no
separate download and are reported as `unknown` by this old `show-info`
implementation; Buildroot itself is GPL-2.0-or-later with file-level
exceptions. The previously documented external toolchain retains its glibc,
GCC, binutils, and Linux-header provenance and licensing caveats.

The clean machine-readable `show-info` output is preserved privately, SHA-256
`08c691c69c7f104ac0d8e3f901716c9ed43640e3ce4fb5193bae2826bd9276e6`.
Source acquisition completed once; its stdout and timing log hashes are
`9db5dd5df356c658b7735704d7d2b9f89f61a6c74efd67aff4e7021e2b525e8f`
and `b0308191ad1c604ece9eff8375fa592826a0c731068c2ce213d1112ced23a0f1`.

## Single rootfs build and exact blocker

The configured default target ran exactly once with `-j1`. It reused the
external toolchain and cached archives, completed host skeleton, attr 2.4.48,
and acl 2.2.53, then configured fakeroot 1.20.2. Compilation failed repeatedly
within that one make invocation at the same first cause:

```text
libfakeroot.c:99:40: error: '_STAT_VER' undeclared (first use in this function)
make: *** [.../host-fakeroot-1.20.2/.stamp_built] Error 2
```

The host is Ubuntu glibc 2.39. Buildroot 2019.05.2 supplies only its two older
fakeroot patches, neither of which handles this host ABI change. The build ran
17.04 seconds, peaked at 128,476 KiB resident memory, and exited 2. Private log
hashes are:

| File | SHA-256 |
| --- | --- |
| `rootfs-build.log` | `ee0aecd2598041af8dd09a872105683914681fdeeed17818704b6700da927a1a` |
| `rootfs-build.time` | `854636d4e7c8e863732df477e4ee10e3c4a17e76229acb76dcd9ac199b91889a` |

BusyBox has only its downloaded stamp. The target and images directories have
no rootfs artifact. No patch or retry was attempted, and no build process
remains.

## Reproducibility and limits

The frozen configuration, inputs, hashes, build order, and failure are
reproducible. Artifact-level content, architecture, and independent second-run
reproducibility cannot be assessed because rootfs creation was never reached.
Nothing here establishes camera compatibility, Ethernet behavior, bootability,
redistribution of the private kernel blobs, recovery, or installation safety.

## Next bounded task

**C2b-2b-1, only after explicit authorization:** verify an authoritative
upstream fakeroot/Buildroot compatibility correction for modern glibc, apply it
only to the disposable private Buildroot tree, preserve the original source,
and make one bounded `-j1` continuation attempt. Stop at a verified rootfs tar
or the next exact blocker.
