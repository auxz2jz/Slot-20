# C2b-2a-6 host LZ4 input and successful generic zImage build

**Scope:** supply one provenance-recorded host `lz4c` without modifying system
packages or existing build dependencies, verify the compression format expected
by the pinned Linux 4.19 tree, and resume the preserved kernel build exactly once
with `-j1`. This task did not build a root filesystem, use the private Reolink
FDT, assemble firmware, execute target code, or contact a camera.

**Result:** COMPLETE. The private generic build produced a Linux ARM zImage and
completed the default target successfully. This is a host build result only; it
does not establish camera compatibility, bootability, redistribution rights, or
recovery safety.

## Preserved inputs and host utility provenance

Git began clean at pushed checkpoint `6e285df`. The existing source, configured
output tree, linked kernel, GCC 6.5.0 ARM hard-float toolchain, OpenSSL input,
host utilities, and intermediate objects were reused. No working prerequisite
or toolchain component was reinstalled or rebuilt.

No `lz4` or `lz4c` command or cached package existed in the inspected build
paths. Signed Ubuntu APT metadata selected:

| Field | Value |
| --- | --- |
| Repository | Ubuntu Noble updates, `universe`, `amd64` |
| Package | `lz4` |
| Version | `1.9.4-1build1.1` |
| Archive path | `pool/universe/l/lz4/lz4_1.9.4-1build1.1_amd64.deb` |
| Package bytes | 93,790 |
| Metadata/package SHA-256 | `6322e77aaee1975c5517892a39f63e80b3e2fe65219bf693192a564b1b9fc7aa` |

The exact package was downloaded and extracted under the private dependency
directory; it was not installed. Its `lz4c` is a symlink to the 202,992-byte
x86-64 `lz4` executable, SHA-256
`87c0d5d060fd36c685b98a38611b7bd6c4614d40b36d29be84edcd6c173f8160`.
The executable reports LZ4 CLI 1.9.4 and links only the host C runtime.

## Compression-format check

The kernel source's `scripts/Makefile.lib` invokes `lz4c -l -c1`, while
`lib/decompress_unlz4.c` identifies legacy archive magic `0x184C2102`.
A synthetic 4,096-byte input compressed with those exact options produced a
34-byte stream beginning `02 21 4c 18`, the little-endian representation of
that constant. Decompression reproduced the input byte-for-byte:

| Synthetic file | SHA-256 |
| --- | --- |
| Input | `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7` |
| Legacy LZ4 output | `c5918b3a3ce0190db28ff51de3a54200c0066e28a8e6720634fef7c8941769bf` |
| Decompressed output | `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7` |

The synthetic files and package remain private/off-Git.

## The one resumed build

The extracted utility directory was prepended to the preserved build `PATH`.
The default kernel target was invoked exactly once with the prior toolchain,
OpenSSL settings, relative `O=../out`, and `-j1`. It exited zero after 13.93
seconds and peaked at 45,620 KiB resident memory. The log records:

```text
LZ4     arch/arm/boot/compressed/piggy_data
LD      arch/arm/boot/compressed/vmlinux
OBJCOPY arch/arm/boot/zImage
Kernel: arch/arm/boot/zImage is ready
```

It then completed stage-two module processing for 86 modules. `modpost` emitted
one section-mismatch warning; this task did not expand into an unrequested
debug-section rebuild.

## Verified private outputs

| Output | Bytes | Format / evidence | SHA-256 |
| --- | ---: | --- | --- |
| `out/vmlinux` | 7,663,316 | ELF32 little-endian ARM EABI5 | `cdad3126f41b07bc147cfc83132b18999bf628b0cf7f0cfe8fbc755917328913` |
| `out/System.map` | 1,198,837 | kernel symbol map | `1c51ceba0fcb76846d671c86fa7b9cabf9415f56f279c9cfe764deb0d529db0c` |
| `out/arch/arm/boot/Image` | 7,577,616 | uncompressed ARM image | `04c6f8cf7061a8b00947c0e38a5a3227ad2c0faa499f6043ead86f13319ea040` |
| `out/arch/arm/boot/zImage` | 2,878,408 | `file`: Linux kernel ARM boot executable zImage, little-endian; header word at `0x24`: `0x016f2818` | `21cb120f49a2028ffef04e3fdf43a0cc9b91a45c86f03807545f6c24b515231b` |

Private log evidence:

| File | Lines | SHA-256 |
| --- | ---: | --- |
| `build-c2b2a6.log` | 208 | `fcb3550cf307906e3c48a5fb015bb40c1bdfbc1eb12831e30806af53a414741b` |
| `build-c2b2a6.time` | 23 | `e30372a251b8c5b810964356480fd340099c18cf007b493b1a93b5787f06b27d` |

No compiler process remains. All generated binaries, modules, logs, synthetic
data, and the downloaded package remain private and are not part of Git.

## Limits and next bounded task

The generic configuration has no matching Reolink board device tree and still
depends on binary-only Novatek PLL/OTP objects whose redistribution rights are
unresolved. It has never been run on hardware, and no boot, peripheral,
recovery, update, or installation claim follows from this successful build.

**C2b-2b, only after explicit authorization:** produce a minimal offline rootfs
prototype with a frozen Buildroot configuration and package/license inventory.
Keep it host-only and separate from this kernel; do not assemble firmware, use
the private Reolink FDT, or access hardware.
