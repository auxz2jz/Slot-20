# C2b-2b-1 fakeroot correction and rootfs continuation

**Scope:** resolve C2b-2b's host fakeroot 1.20.2 failure using an
authoritative public-source correction, then make exactly one single-threaded
continuation attempt in the preserved private Buildroot workspace. This task
did not modify the completed kernel, use the private Reolink FDT, assemble
firmware, execute ARM target code, or contact a camera.

**Result:** COMPLETE WITH THE NEXT EXACT REPRODUCIBLE BLOCKER. The accepted
fakeroot/glibc compatibility series is frozen and installed in the disposable
Buildroot source tree. The one `-j1` continuation stopped earlier in the new
autoreconf dependency chain while compiling host GNU m4 1.4.18. No rootfs tar
or target files were produced.

## Authoritative fakeroot correction

glibc 2.33 removed `_STAT_VER`, but the accepted correction is not only a
constant definition. Buildroot's upstream commit
`f45925a951318e9e53bead80b363e004301adc6f` imports three accepted fakeroot
changes: define the version when absent, wrap the newly exported glibc 2.33
stat symbols, and correct the `__xmknod{,at}` pointer probes. Because the third
patch changes `configure.ac`, Buildroot must run autoreconf.

The three numbered files under
`patches/fakeroot-1.20.2-glibc-2.33/` are byte-for-byte copies from Buildroot
tag `2020.02.11`. Their repository hashes match direct HTTPS retrieval from:

`https://gitlab.com/buildroot.org/buildroot/-/raw/2020.02.11/package/fakeroot/`

| Patch | SHA-256 |
| --- | --- |
| `_STAT_VER` definition | `7a4da76f086b6b80943fc36d1bee72de1b5e3a5f94b0bf88211d4cc15e8537ed` |
| glibc 2.33 stat wrappers | `7eed80a49e454893c49fb4bc210cddb6a5533a0f5a00443204b61823d445d6f8` |
| `__xmknod{,at}` configure correction | `b2125fe3e8afb69223700e08462f0a4c5cdcde718d14c32a13b75648e22302b1` |
| Buildroot 2019.05.2 autoreconf integration | `867de5e1b7920406ec3adf7f1601cc05c0eb03e8e8543344e2f9134529f2b1f0` |

Primary provenance is the Buildroot commit/backport discussion and accepted
fakeroot merge request linked in the patch-directory README. The public
fakeroot source and patches are GPL-3.0+; no vendor binary is included.

## Private preservation and application

The original cached fakeroot archive remains unchanged at SHA-256
`7c0a164d19db3efa9e802e0fc7cdfeff70ec6d26cdbdc4338c9c2823c5ea230c`.
The failed extracted tree was moved intact to:

`/home/firmware-analysis/slot20_private/c2b2b_20261018/rootfs-out/build/host-fakeroot-1.20.2.pre-c2b2b1/`

Its unmodified `libfakeroot.c` is SHA-256
`234e19560ecfa5e7be79945f0baebaf27ed7b54fefe0dd9035187286543d5a31`.
The three verified patches were copied to the private Buildroot
`package/fakeroot/` directory, and the autoreconf integration patch applied
with a successful dry run first. The resulting private `fakeroot.mk` is
SHA-256 `0ed2ea7a0c9ed8a3e95c95cb7d5a1492eb1d56144fcb548f48e4ac7b988e83df`.
The active fakeroot build directory does not yet exist: Buildroot stopped in a
new prerequisite before it could re-extract or compile fakeroot. Therefore the
patch series is source- and integration-verified, but not yet compile- or
runtime-verified in this workspace.

## Single continuation and next blocker

After pushing pre-build checkpoint `a4256b2`, the preserved configuration was
resumed exactly once using `make ... -j1`. Enabling fakeroot autoreconf caused
Buildroot to materialize its private host GNU m4 1.4.18 dependency. Compilation
stopped at:

```text
lib/c-stack.c:55:26: error: missing binary operator before token "("
#elif HAVE_LIBSIGSEGV && SIGSTKSZ < 16384
make: *** [.../host-m4-1.4.18/.stamp_built] Error 2
```

The host is Ubuntu glibc 2.39. The preprocessor expression requires
`SIGSTKSZ` to be an integer constant, which modern glibc no longer guarantees.
This is a host-tool compatibility failure, not ARM compilation evidence.

The cached `m4-1.4.18.tar.xz` matches Buildroot's recorded SHA-256
`f2c1e86ca0a404ff281631bdc8377638992744b175afb806e25871a24a934e07`.
The extracted failing `lib/c-stack.c` is SHA-256
`34286fa24484ee8eefc3e768c97b444b5a22963752d45be7acae9ccab7cae6aa`.
Host m4 completed extraction, patching and configuration but has no built
stamp. The attempt exited 2 after 25.95 seconds and peaked at 128,216 KiB RSS.

| Private log | SHA-256 |
| --- | --- |
| `logs/rootfs-build-c2b2b1.log` | `2fad154fe292f5f38cc95ea45eea7b8604548867f57d2af99d16aa95838be774` |
| `logs/rootfs-build-c2b2b1.time` | `2dc4459deef425f9e456eb5c67c2f9df2bd56bed32e2717eb070a67a4feb69fb` |

No compiler or make process remains. Both `rootfs-out/target` and
`rootfs-out/images` contain zero regular files. The separate generic kernel is
unchanged: `zImage` remains SHA-256
`21cb120f49a2028ffef04e3fdf43a0cc9b91a45c86f03807545f6c24b515231b`
and `vmlinux` remains
`cdad3126f41b07bc147cfc83132b18999bf628b0cf7f0cfe8fbc755917328913`.

## Limits and next bounded task

No fakeroot binary or rootfs was produced, so package operation, rootfs
contents, target architecture, artifact integrity and reproducibility remain
unverified. Nothing here proves camera compatibility, bootability, recovery,
or installation safety.

**C2b-2b-2, only after explicit authorization:** find an authoritative
upstream gnulib/GNU m4 correction for the m4 1.4.18 `SIGSTKSZ` preprocessor
failure, preserve the current host-m4 tree, apply the smallest public-source
correction only in the disposable Buildroot environment, then make one bounded
`-j1` continuation. Stop at a verified rootfs tar or the next exact blocker.

