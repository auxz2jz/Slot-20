# C2b-2b-3 fakeroot build-aux correction and rootfs continuation

**Scope:** preserve the failed fakeroot 1.20.2 source, add Buildroot's accepted
`build-aux` post-patch hook to the disposable private Buildroot 2019.05.2
workspace, and make no more than one single-threaded rootfs continuation. This
task does not modify the completed kernel, use the private Reolink FDT,
assemble firmware, execute target code, or contact a camera.

## Pre-build checkpoint

Git began clean at pushed checkpoint `17c64d7`.

The fakeroot 1.20.2 release archive contains generated autotools files but no
`build-aux` directory. Its `Makefile.am` declares
`ACLOCAL_AMFLAGS = -I build-aux`, and `configure.ac` declares
`AC_CONFIG_MACRO_DIR([build-aux])`. C2b-2b-1 had to enable autoreconf because
an accepted glibc compatibility patch changes `configure.ac`; consequently,
`aclocal` now requires the directory that the release archive omits.

Buildroot fixed this exact integration issue with a post-patch hook that runs
`mkdir -p $(@D)/build-aux`. The authoritative `2019.02.x` commit is
`519dd1f6e043809cd5f389d8bff86cb95180390f`, cherry-picked from master commit
`fd1bcce9894773d7e1c1ca5be0f04b0b32128a1d`. The accepted recipe hunk is
recorded at:

<https://lists.buildroot.org/pipermail/buildroot/2019-November/253483.html>

The tracked minimal backport is
`patches/buildroot-2019.05.2-fakeroot-build-aux/0001-fakeroot-create-build-aux-before-autoreconf.patch`,
SHA-256 `1a156d3b7b44c4388012c3fae06c2ecb1902515c25d82144cf65605b945be0c7`.
It adds only the accepted `HOST_FAKEROOT_BUILD_AUX` post-patch hook; a dry run
against the current private recipe passed.

Before applying the recipe patch, the failed source tree was moved intact to:

`/home/firmware-analysis/slot20_private/c2b2b_20261018/rootfs-out/build/host-fakeroot-1.20.2.pre-c2b2b3/`

The original private recipe is preserved as `fakeroot.mk.pre-c2b2b3`. Its
SHA-256 is `0ed2ea7a0c9ed8a3e95c95cb7d5a1492eb1d56144fcb548f48e4ac7b988e83df`;
the corrected recipe is
`a00314db79d6fafb86e86b12a26a11069aed60fec184bf3ab52a7db0b4d2b8bc`.
The preserved failed `Makefile.am` and `configure.ac` hashes remain
`239c646499a715fe89ef230b0a53c8c9faad9f8ed398ed7fe2c38f7a498f8d77`
and `9324ae80c498a0003763bdf6fd49f8143596c9a2518277961fc3db1e07314c43`.

At this checkpoint, the continuation build has **not** started. The next and
only build action authorized by C2b-2b-3 is one bounded `-j1` continuation,
after a reliable usage check. It must stop at a verified rootfs tar or the next
exact reproducible blocker.

## Single continuation result

Pre-build checkpoint `b838711` was pushed. Reliable telemetry immediately
before compilation showed 67% of the five-hour window and 71% of the weekly
window remaining. The preserved configuration then ran exactly once with
`-j1` under a 30-minute timeout.

Buildroot freshly extracted fakeroot, applied all five preserved patches, ran
the new post-patch hook, and created `build-aux` before autoreconf. Fakeroot
configured, built and installed successfully; all expected stamps through
`.stamp_host_installed` exist. The installed host wrapper reports fakeroot
1.20.2 and has SHA-256
`b49b9b5aa596330b8bf062179504a984ffba28fc10c10498798b926284b1a653`.

The same invocation continued through BusyBox and target finalization and
exited zero after 126.10 seconds, with peak resident memory of 162,960 KiB.
It generated one image:

| Property | Verified value |
| --- | --- |
| Private path | `rootfs-out/images/rootfs.tar` |
| Format | POSIX tar archive; full `tar -tf` integrity scan passed |
| Size | 3,696,640 bytes |
| SHA-256 | `df413f6a805fb7c860b1ae1043416f225ffe18bfd32f5ffdf09be491e650e06a` |
| Archive entries | 374 |
| Resolved Buildroot configuration | `ccda34efa8c3f1144ba3d9771c9099eed0ab0ee3299cb1e04439c5ceffd686eb` |

Static inspection of the archived `./bin/busybox` reports ELF32
little-endian ARM EABI5, Cortex-A9/ARMv7, hard-float VFP-register arguments,
dynamic interpreter `/lib/ld-linux-armhf.so.3`, and Linux 4.19 ABI tagging. It
identifies itself as BusyBox 1.30.1. Its SHA-256 is
`1b5d8379d0694c8f0e1ab716b83a0a26e68c754ed6f8442f024cf6396856240f`;
the loader hash is
`fcd7690fbd7780eda4fabf65641e99dc7ac81b2a15d98f9a9c41e77205b74034`.
The archive contains `sbin/init`, `etc/inittab`, account files and the expected
`dev`, `proc` and `sys` mount points. Numeric ownership is root except the
intentional `var/www` ownership `33:33`. No kernel image, `vmlinux`, DTS or DTB
entry is present.

The private build/stdout and stderr/time logs have SHA-256 values
`dea3247f92a906321276eea619ee890dbe0414b70728cee45e2a6632fca83777`
and `1e61cb71fcec6ad947893628ff34e8e33240c4bbda0a4b4b8389a413cc4d2017`.
The logs retain non-fatal legacy host-fakeroot type/format warnings, generic
configure-option warnings, one stale BusyBox `FEATURE_FLOAT_SLEEP` assignment,
and finalization probes for absent optional paths. They contain no failed build
step, and the timed command's exit status is zero.

## Limits and next bounded task

This is one verified generic rootfs build, not an independent clean rebuild.
Build timestamps appear in BusyBox and the tar metadata, so byte-for-byte
reproducibility has not been demonstrated. The ARM binary was inspected but
never executed. The tar was not combined with the generic kernel or private
Reolink FDT and is not a bootable-camera or compatibility claim.

**C2b-2c, only after explicit authorization:** reproduce the frozen minimal
rootfs in a second clean private output directory, compare normalized contents
and hashes, and generate/check Buildroot legal-info using only the preserved
source cache and toolchain. Do not assemble firmware or access hardware.
