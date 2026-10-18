# C2b-2b-2 host-m4 correction and rootfs continuation

**Scope:** reuse the official GNU m4 1.4.18 compatibility patch already
verified in C2b-1, preserve the failed host-m4 tree, and make exactly one
single-threaded continuation in the existing private Buildroot workspace. This
task did not modify the completed kernel, use the private Reolink FDT, assemble
firmware, execute ARM target code, or contact a camera.

**Result:** COMPLETE WITH THE NEXT EXACT REPRODUCIBLE BLOCKER. The m4
`SIGSTKSZ` correction compiled and installed successfully. The one `-j1`
continuation then stopped while autoreconfiguring host fakeroot 1.20.2 because
its declared `build-aux` macro directory does not exist. No target files or
rootfs tar were produced.

## Reused authoritative patch

No new investigation was performed. C2b-1's preserved patch was found at:

`/home/firmware-analysis/slot20_private/c2b1_20261017/buildroot-src/package/m4/0003-c-stack-stop-using-SIGSTKSZ.patch`

It matches the C2b-1 record and official Buildroot commit
`5a9504831f3fa1ef3be334036c93da30150fde55` at SHA-256
`a659db8cd9cad78130f3732ecd369fdfdcdbf0c1cf23821b1c44ea8661e65c4e`.
The patch header identifies the backported gnulib change
`f9e2b20a12a230efa30f1d479563ae07d276a94b`. The tracked copy under
`patches/m4-1.4.18-glibc-sigstksz/` is byte-identical to the preserved C2b-1
file and is public source, not vendor firmware.

The patch removes `SIGSTKSZ` from preprocessor expressions and replaces the
alternate signal stack with an aligned 64 KiB array. A dry run against the
failed private source passed for both `lib/c-stack.c` and `lib/c-stack.h`.

## Private preservation and application

The failed source tree was moved intact to:

`/home/firmware-analysis/slot20_private/c2b2b_20261018/rootfs-out/build/host-m4-1.4.18.pre-c2b2b2/`

Its unmodified source hashes are:

| File | SHA-256 |
| --- | --- |
| `lib/c-stack.c` | `34286fa24484ee8eefc3e768c97b444b5a22963752d45be7acae9ccab7cae6aa` |
| `lib/c-stack.h` | `02c57886ba8b59b5183c1a6777a1d619b726ecab7ece0daa32a15a96a890872a` |

The verified patch was copied into the private Buildroot `package/m4/`
directory. Buildroot then re-extracted m4 1.4.18, applied all three patches,
built it, and installed the host tool. Verification after the build:

| Output | SHA-256 |
| --- | --- |
| Patched `lib/c-stack.c` | `c43899dd5bd6da727bf2ed3567a7f8b8fddb1f44adb0689db8d0c5dd56a12203` |
| Patched `lib/c-stack.h` | `35ab8de7d5aa6750771b623a97bb366143494d0006fcb4177a3d5cb09109f8b3` |
| Installed host `bin/m4` | `5a17d1859a74c6d93543baedf5e22c99167c4275ca17bbe0c415162bf2e0d0b3` |

The installed executable reports GNU M4 1.4.18. The patched source contains no
`SIGSTKSZ`, contains the expected aligned 64 KiB buffer, and has built plus
host-installed stamps. This verifies the C2b-2b-1 blocker is resolved.

## Single continuation and next blocker

Pre-build checkpoint `f3f020e` was pushed before the build. Reliable usage at
that checkpoint was 91% remaining in the five-hour window and 74% remaining in
the weekly window. The preserved configuration then ran exactly once with
`make ... -j1`.

The continuation built the host autoreconf dependency chain, re-extracted
fakeroot, and applied all five expected fakeroot patches. It stopped before
fakeroot configuration or compilation at:

```text
>>> host-fakeroot 1.20.2 Autoreconfiguring
aclocal: error: couldn't open directory 'build-aux': No such file or directory
autoreconf: .../host/bin/aclocal failed with exit status: 1
```

The missing directory is explicitly referenced by `Makefile.am` as
`ACLOCAL_AMFLAGS = -I build-aux` and by `configure.ac` as
`AC_CONFIG_MACRO_DIR([build-aux])`. The extracted package's `bootstrap` and
`preroll` helper scripts can create it, but Buildroot's generic autoreconf step
did not run those helpers. The directory is absent. No fix or retry was
attempted.

The build exited 2 after 55.83 seconds and peaked at 128,392 KiB RSS.

| Private log | SHA-256 |
| --- | --- |
| `logs/rootfs-build-c2b2b2.log` | `bddb74d66fd6d6554d117e833d18b4957056b67df126d7e635fe336a785c7750` |
| `logs/rootfs-build-c2b2b2.time` | `3df217b86058423a3ac43b5b01452ca19b394d425ae300ece246d37a247e592d` |

No make or compiler process remains. Both `rootfs-out/target` and
`rootfs-out/images` contain zero regular files. The completed kernel is
unchanged: `zImage` remains SHA-256
`21cb120f49a2028ffef04e3fdf43a0cc9b91a45c86f03807545f6c24b515231b`
and `vmlinux` remains
`cdad3126f41b07bc147cfc83132b18999bf628b0cf7f0cfe8fbc755917328913`.

## Limits and next bounded task

Fakeroot was patched but not configured or compiled. No rootfs exists, so its
contents, target architecture, integrity and reproducibility remain unverified.
Nothing here proves camera compatibility, bootability, recovery, or
installation safety.

**C2b-2b-3, only after explicit authorization:** preserve the current failed
fakeroot tree, verify the smallest reproducible Buildroot-compatible correction
for the missing declared `build-aux` directory, checkpoint it, and make one
bounded `-j1` continuation. Stop at a verified rootfs tar or the next exact
blocker.
