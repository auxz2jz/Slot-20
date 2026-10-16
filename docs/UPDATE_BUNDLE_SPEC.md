# Slot-20 host-only signed update-bundle specification

**Status:** B1 design specification, version 1. B2 implements a host-only verifier and synthetic tests; no production builder, updater, flash layout or camera-side implementation exists. Conformance to this document can establish only host-side bundle validity; it does not establish installability, rollback safety or recovery.

## Scope and non-goals

The version-1 bundle is a small deterministic container for authenticated component bytes and compatibility metadata. It is deliberately independent of NAND offsets, MTD names, slots and the unresolved Reolink update mechanism.

Version 1:

- targets exactly one trusted hardware profile: `reolink.rlc-811a.ipc_523128m8mp`;
- authenticates a strict canonical manifest with Ed25519 and authenticates component bytes with signed SHA-256 digests;
- carries uncompressed, path-free component byte strings;
- separates structural/cryptographic validity from update/downgrade authorization;
- never supplies a public key, flash address, partition name, boot selector or permission to write; and
- is host-only until later tasks implement and test it. A valid bundle is not a flashable image.

The normative standards are UTF-8 (RFC 3629), JSON Canonicalization Scheme/JCS (RFC 8785), SHA-256 (FIPS 180-4), Ed25519 (RFC 8032) and Semantic Versioning 2.0.0. Implementations must use maintained cryptographic libraries rather than custom primitives.

## Binary container

All integer fields are unsigned big-endian. The file is exactly:

```text
fixed header (32 bytes)
canonical manifest (manifest_length bytes)
component payloads (payload_length bytes, concatenated in manifest order)
Ed25519 signature (64 bytes)
EOF
```

| Offset | Size | Field | Version-1 rule |
|---:|---:|---|---|
| `0x00` | 8 | magic | ASCII `S20BNDL1` |
| `0x08` | 2 | format_version | exactly `1` |
| `0x0a` | 2 | header_length | exactly `32` |
| `0x0c` | 4 | manifest_length | `2..65,536` |
| `0x10` | 2 | component_count | `1..16` |
| `0x12` | 2 | signature_length | exactly `64` |
| `0x14` | 8 | payload_length | `1..134,217,728` bytes |
| `0x1c` | 4 | flags | exactly zero; unknown flags are rejected |

The total parser cap is `32 + 65,536 + 134,217,728 + 64 = 134,283,360` bytes. This is an untrusted-input bound, **not** evidence that any amount of NAND is available. Length arithmetic must be checked before allocation or seeking. The sum of component lengths must equal `payload_length`, and the physical file length must equal the calculated total with no padding or trailing data.

Compression and archive entries are intentionally absent in version 1. This avoids decompression bombs, duplicate archive names, path traversal and archive-metadata nondeterminism. A future compression scheme requires a new format version with separate compressed and expanded bounds.

## Canonical manifest

The manifest is UTF-8 JSON without a byte-order mark. It must be valid I-JSON and its bytes must exactly equal the RFC 8785 canonical serialization of the parsed value. Parsers must detect duplicate object names before ordinary object construction. Version 1 rejects unknown, missing or duplicate fields; JSON floats, negative integers, `null`, and numeric values above `9,007,199,254,740,991` are not permitted.

### Top-level fields

| Field | Type and bound | Rule |
|---|---|---|
| `schema` | string | exactly `slot20.update-bundle.v1` |
| `hardware_profile` | ASCII string, 1–64 bytes | exactly `reolink.rlc-811a.ipc_523128m8mp`; no aliases, lists or wildcards |
| `release_version` | ASCII string, 1–64 bytes | valid Semantic Versioning 2.0.0; display/audit label only |
| `release_sequence` | integer, `0..9,007,199,254,740,991` | monotonic release order within a security epoch |
| `security_epoch` | integer, `0..9,007,199,254,740,991` | anti-rollback security generation controlled by trusted policy |
| `signing_key_id` | string, exactly 64 lowercase hexadecimal characters | SHA-256 of the raw 32-byte Ed25519 public key |
| `components` | array | exactly `component_count` entries, in payload order |

No creation timestamp is stored. A release tuple is `(hardware_profile, security_epoch, release_sequence)`; the signing process must never assign the same tuple to different manifest or component content. The SHA-256 of the complete assembled bundle is its external artifact identifier and may be recorded in a trusted release catalog.

### Component fields

Each component object has exactly these fields:

| Field | Type and bound | Rule |
|---|---|---|
| `id` | ASCII string matching `[a-z][a-z0-9._-]{0,31}` | unique within the bundle; identifies the manifest entry, not a filesystem path |
| `type` | ASCII string matching `[a-z][a-z0-9._-]{0,31}` | symbolic role interpreted only by a separate trusted hardware profile |
| `length` | integer, `1..67,108,864` | exact uncompressed byte count |
| `sha256` | string, exactly 64 lowercase hexadecimal characters | SHA-256 of exactly this component's bytes |

The payload is the exact concatenation of the listed component byte strings. There are no filenames, offsets, alignment gaps, links or executable directives. Component IDs must be unique. Component types may repeat only if a future trusted profile explicitly permits it; the current profile has no installation map, so B1 establishes no allowed write target.

## Hardware compatibility

Compatibility is exact, deny-by-default equality between the manifest `hardware_profile` and a locally trusted profile selected from independently verified device identity. Model-name similarity, a package Device Tree, a user-supplied alias or another Reolink/Novatek revision is insufficient. A multi-revision release must be emitted as separate bundles with separate manifests.

The trusted profile—not the bundle—must eventually define permitted component types, maximum installed sizes, destination semantics and boot/update prerequisites. For `IPC_523128M8MP` those mappings remain undefined. A host verifier can therefore report a structurally valid and correctly signed B1 bundle, but no current software may translate its component types into NAND writes.

## Version and downgrade policy

Cryptographic validity and installation authorization are separate results. A verifier takes trusted local policy and current device state as inputs; the manifest cannot grant itself an exception.

Required local state/policy inputs are:

- exact hardware profile;
- current `security_epoch`, `release_sequence` and committed bundle identifier;
- minimum permitted security epoch;
- trusted signing-key records and revocations;
- a trusted supported-release catalog mapping each release tuple to an expected bundle identifier; and
- explicit authenticated user intent for reinstall or downgrade, when applicable.

Policy rules:

1. Reject any bundle below the locally stored minimum security epoch, regardless of signature or user request.
2. A higher security epoch is an upgrade. Its floor must not become permanent until the candidate is healthy and rollback consequences are understood.
3. Within the same epoch, a higher sequence is a normal upgrade.
4. An equal tuple is a reinstall and requires explicit authenticated user intent plus an exact trusted-catalog bundle match.
5. A lower sequence in the same epoch is a downgrade. It requires explicit authenticated user intent, an exact trusted-catalog bundle match, an epoch at or above the security floor, and preservation of a known-good recovery/rollback target.
6. A display `release_version` never overrides the numeric policy. Prerelease/build labels do not authorize downgrade.
7. A valid signature from an otherwise trusted key does not make a retired, revoked, unsupported or wrong-profile release installable.

Durable storage and power-fail-safe updates of this policy state are unresolved. B1 defines the decision inputs but does not claim the camera can preserve them.

## Hashing and signature

Version 1 has no algorithm negotiation:

- component hashes and key IDs use SHA-256;
- the signature algorithm is pure Ed25519, not Ed25519ph; and
- the signature is the raw 64-byte Ed25519 result.

The exact signature transcript is:

```text
ASCII("SLOT20-BUNDLE-SIGNATURE-V1") || 0x00 || header[0:32] || canonical_manifest
```

The signature does not repeat the potentially large payload. It authenticates the canonical manifest, whose signed component lengths and SHA-256 values bind every payload byte and its order. A verifier must still stream and compare every component hash and reject any payload-length or EOF mismatch.

## Trusted keys and rotation

The bundle's `signing_key_id` selects—but never supplies or authorizes—a key in an independently authenticated local trust store. Each trust record must contain the raw Ed25519 public key, its computed key ID, exact hardware-profile scope, status (`active`, `retired` or `revoked`), and any security-epoch bounds. Unknown, incorrectly scoped or revoked keys are rejected. Private signing keys stay offline or in an appropriate signing service/HSM and never enter this repository, a bundle or the camera image.

Version 1 carries one signature. Safe rotation therefore requires overlap in the trust store:

1. provision the new public key through a separately authenticated trust-policy update authorized by an active old key;
2. verify that all supported verifiers trust the new key before releases rely on it exclusively;
3. sign subsequent bundles with the new key; and
4. retire or revoke the old key through another authenticated policy update, raising the minimum security epoch when compromise requires blocking older artifacts.

A bundle cannot add its own key. Trust-store atomicity, recovery and the format of signed trust-policy updates are outside B1 and must be designed before device use. If simultaneous multi-signature bundles become necessary, they require a new container version rather than an ambiguous extension.

## Deterministic production

For fixed component bytes, manifest values and private key, compliant production yields identical bundle bytes:

1. validate component count and sizes; compute each SHA-256 in manifest order;
2. construct only the allowed manifest fields, with no timestamp or host metadata;
3. serialize once with RFC 8785 and verify the manifest limit;
4. encode the fixed header with lengths derived from those exact bytes;
5. sign the exact domain-separated transcript with deterministic Ed25519;
6. concatenate header, manifest, components in order and signature; and
7. compute and record the final bundle SHA-256 as the release artifact identifier.

Signing must fail closed if a release tuple already exists with a different artifact, if a component changes during hashing/assembly, or if the final file does not reproduce from pinned inputs.

## Verification and rejection order

A B2 verifier must operate on one already-open file handle and perform no extraction or writes:

1. enforce the total file cap, read the fixed header and reject bad magic/version/header size/flags or out-of-range counts and lengths;
2. calculate all offsets with checked arithmetic and require the exact physical file length;
3. read the bounded manifest, reject invalid UTF-8/I-JSON, duplicate or unknown fields, and require byte-for-byte JCS reserialization equality;
4. validate every field, regex, uniqueness rule, numeric bound, component count and sum of lengths;
5. require exact hardware-profile equality and find an active, correctly scoped local key by the manifest key ID;
6. read and verify the 64-byte signature over the exact transcript;
7. stream each component from the same handle with bounded memory, compare its length and SHA-256, and require exact payload end and EOF;
8. compute the full bundle SHA-256 and compare the release tuple/artifact against trusted policy; and
9. return separate structural, cryptographic, compatibility and version-policy results. None authorizes a flash write in B2.

At minimum, rejection tests must cover truncation at every section; trailing bytes; integer overflow; oversized manifest/payload/component/count; invalid UTF-8; duplicate JSON names; noncanonical JSON; missing/extra/wrong-type fields; malformed SemVer, IDs or hashes; duplicate component IDs; zero or inconsistent lengths; wrong profile; unknown/revoked/wrong-scope key; altered header/manifest/signature/payload; component-hash mismatch; release-tuple reuse; and every upgrade/reinstall/downgrade boundary.

## Security assumptions and limitations

- Ed25519 and SHA-256 remain cryptographically sound and are provided by a vetted library.
- The host verifier, trusted profile, trust store, supported-release catalog and current-version state are authentic and uncompromised.
- Signing private keys are protected. Key compromise permits malicious bundles within that key's trusted scope until revocation state is distributed and durable.
- Hardware identity is obtained independently and cannot be replaced by manifest claims.
- The verifier avoids time-of-check/time-of-use substitution by using one file handle and binding the decision to the final bundle hash.
- The format provides authenticity and integrity, not confidentiality; payload bytes are visible.
- Signature success does not prove that component bytes boot, fit a real partition, preserve factory data, survive power loss or can be rolled back.

## Recovery and rollback blockers

The following remain explicitly unresolved after B1:

- no trusted component-to-flash/slot mapping or writable-size budget exists;
- ownership of `fdt.restore`, `uenv`, `para`, `sp`, `ext_para` and `download` remains unresolved, and none is available for this design;
- there is no proved inactive slot, protected rescue image, atomic boot-state store, health-mark protocol or previous-version target;
- trust-store, version-floor and release-catalog persistence have no demonstrated power-fail-safe location;
- no full per-device NAND/OOB/bad-block backup or restoration has been demonstrated;
- UART/TFTP/MMC, Boot ROM, external programmer and staged-reset recovery remain unverified on a matching spare; and
- installation, interrupted-write recovery and rollback still require matching-spare demonstration and fresh explicit approval.

Consequently, this format and its B2 verifier are eligible only for host-side validation. They do not satisfy any physical recovery gate and authorize no camera access or flash operation.

## B2 reference verifier

`tools/verify_update_bundle.py` implements this format as a read-only Python API. It uses the maintained `cryptography` package for Ed25519, reads one regular file handle, holds at most the bounded manifest plus a 1 MiB payload chunk, and returns separate structure, authenticity, hardware-compatibility and version-policy results. Its `installation_authorized` result is always false.

The accepted manifest schema contains only fixed ASCII object names, bounded ASCII values, arrays and non-negative integers. For that deliberately narrow domain, the verifier's sorted, separator-free UTF-8 JSON serialization is byte-equivalent to RFC 8785; all other JSON shapes, duplicate names, floats, Unicode field values and noncanonical encodings are rejected. This is not a general-purpose JCS implementation.

`tests/test_verify_update_bundle.py` creates temporary in-memory Ed25519 keys and synthetic payloads only. It does not serialize a private key or retain a generated bundle. The tests cover valid upgrades and rotation overlap plus malformed framing/JSON/metadata, truncation/trailing data, size limits, profile/key scope, signature and payload tampering, release-catalog binding, security floors, reinstall and downgrade policy. `requirements.txt` pins the tested cryptographic dependency; no network, extraction, device or flash API is present.
