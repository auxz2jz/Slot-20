# Fakeroot `build-aux` Buildroot integration patch

This directory contains the minimal public-source recipe correction used by
Slot-20 task C2b-2b-3. It does not contain fakeroot sources, target binaries,
vendor firmware, or generated build output.

Fakeroot 1.20.2 declares `build-aux` in `Makefile.am` and `configure.ac`, but
the Debian release archive omits that directory. Once a patch touches
`configure.ac`, Buildroot must run autoreconf, whose `aclocal` step fails if
the declared directory is absent.

Buildroot solved the same integration issue by adding a post-patch hook that
runs `mkdir -p $(@D)/build-aux`. The tracked patch backports only that hook to
the C2b-2b-1 recipe, where `HOST_FAKEROOT_AUTORECONF = YES` is already present.

Authoritative records:

- Buildroot `2019.02.x` commit
  `519dd1f6e043809cd5f389d8bff86cb95180390f`, cherry-picked from master commit
  `fd1bcce9894773d7e1c1ca5be0f04b0b32128a1d`.
- Buildroot mailing-list commit record:
  <https://lists.buildroot.org/pipermail/buildroot/2019-November/253483.html>

Apply from a Buildroot tree after the C2b-2b-1 autoreconf change:

```sh
patch -p1 --dry-run < /path/to/0001-fakeroot-create-build-aux-before-autoreconf.patch
patch -p1 < /path/to/0001-fakeroot-create-build-aux-before-autoreconf.patch
```
