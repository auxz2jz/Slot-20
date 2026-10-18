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
