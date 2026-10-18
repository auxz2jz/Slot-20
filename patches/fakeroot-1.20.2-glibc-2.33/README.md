# fakeroot 1.20.2 host-glibc compatibility series

This directory preserves the smallest complete compatibility series that
Buildroot accepted for fakeroot on glibc 2.33 and later. The three fakeroot
patches are byte-for-byte copies from Buildroot tag `2020.02.11`; they are
public GPL-3.0+ source changes and contain no vendor firmware or private data.

Upstream references:

- Buildroot commit: <https://git.buildroot.net/buildroot/commit/?id=f45925a951318e9e53bead80b363e004301adc6f>
- Buildroot backport discussion: <https://lists.buildroot.org/pipermail/buildroot/2021-February/291740.html>
- Accepted fakeroot merge request: <https://salsa.debian.org/clint/fakeroot/-/merge_requests/10>

Verified SHA-256 values:

| File | SHA-256 |
|---|---|
| `0003-libfakeroot.c-define-_STAT_VER-if-not-already-defined.patch` | `7a4da76f086b6b80943fc36d1bee72de1b5e3a5f94b0bf88211d4cc15e8537ed` |
| `0004-libfakeroot.c-add-wrappers-for-new-glibc-2.33-symbol.patch` | `7eed80a49e454893c49fb4bc210cddb6a5533a0f5a00443204b61823d445d6f8` |
| `0005-configure.ac-fix-__xmknod-at-pointer-argument.patch` | `b2125fe3e8afb69223700e08462f0a4c5cdcde718d14c32a13b75648e22302b1` |
| `buildroot-2019.05.2-enable-fakeroot-autoreconf.patch` | `867de5e1b7920406ec3adf7f1601cc05c0eb03e8e8543344e2f9134529f2b1f0` |

The fourth file is the local Buildroot 2019.05.2 integration change. It enables
autoreconf because the accepted series modifies `configure.ac`; otherwise an
already generated `configure` script would retain the incompatible probe.

To reproduce in a clean Buildroot 2019.05.2 tree, copy the three numbered
patches into `package/fakeroot/`, then apply the integration patch from the
Buildroot top-level directory with `patch -p1`. Existing extracted fakeroot
trees must be preserved or removed from the active output path so Buildroot can
extract, patch, autoreconf, configure, and build the package again.
