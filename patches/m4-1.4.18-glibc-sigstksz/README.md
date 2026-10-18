# GNU m4 1.4.18 modern-glibc compatibility patch

This is the same official Buildroot backport previously verified and used by
Slot-20 Task C2b-1. It is public source and contains no vendor firmware or
private device data.

- Buildroot commit: `5a9504831f3fa1ef3be334036c93da30150fde55`
- Buildroot source URL:
  <https://gitlab.com/buildroot.org/buildroot/-/raw/5a9504831f3fa1ef3be334036c93da30150fde55/package/m4/0003-c-stack-stop-using-SIGSTKSZ.patch>
- Backported gnulib change: `f9e2b20a12a230efa30f1d479563ae07d276a94b`
- Patch SHA-256:
  `a659db8cd9cad78130f3732ecd369fdfdcdbf0c1cf23821b1c44ea8661e65c4e`

The correction removes `SIGSTKSZ` from preprocessor expressions and uses a
fixed, aligned 64 KiB alternate-signal-stack buffer. This is required because
modern glibc no longer guarantees that `SIGSTKSZ` is an integer constant.
