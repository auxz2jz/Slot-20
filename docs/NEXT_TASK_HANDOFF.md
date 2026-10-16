# Slot-20 — Current task handoff

**Status:** Task B1 COMPLETE — `docs/UPDATE_BUNDLE_SPEC.md` defines a deterministic, bounded host-only signed bundle. It is a format/security specification only and supplies no flash mapping or installation authority.

**LAST TASK ID / STATUS:** B1 host-only signed update-bundle specification — **VERIFIED COMPLETE (documentation only)**. No B2 parser/verifier, flashable image, production key, target execution or camera access was created.

**EVIDENCE AND TESTS:**

- Container: 32-byte big-endian fixed header, bounded canonical manifest, uncompressed path-free component concatenation and one raw 64-byte Ed25519 signature. Exact EOF is mandatory.
- Bounds: 64 KiB manifest, 16 components, 64 MiB per component and 128 MiB aggregate payload. These are parser safety caps, not available-NAND claims.
- Compatibility: exact deny-by-default profile `reolink.rlc-811a.ipc_523128m8mp`; no alias, wildcard or cross-revision list. The trusted profile, not the bundle, must eventually define allowed component types and targets.
- Manifest: strict UTF-8 I-JSON whose original bytes must equal RFC 8785 serialization. Unknown/duplicate/missing fields, floats and out-of-range integers are rejected.
- Versions: Semantic Versioning is display/audit metadata; `(security_epoch, release_sequence)` plus external trusted policy controls upgrade/reinstall/downgrade. A bundle cannot authorize its own downgrade.
- Authentication: signed SHA-256 component lengths/digests bind ordered payload bytes. Pure Ed25519 signs the exact domain-separated header-plus-canonical-manifest transcript. Full-bundle SHA-256 is the external artifact identity.
- Trust: public keys come only from an independently authenticated, hardware-scoped trust store; private keys never enter the repository/bundle. Rotation requires prior authenticated provisioning and overlap. The single-signature v1 does not silently add multi-signature semantics.
- Rejection/security sections specify checked arithmetic, exact file length, strict schema/canonicalization, trust scope, streaming payload hashes, release-policy separation and adversarial cases for B2.
- Focused checks validate header field widths/offsets, cap arithmetic, required topics/standards, matrix/table structure, internal terminology, whitespace, tracked-file scope and absence of private/key material before checkpointing.

**IMPORTANT LIMITS:** B1 proves no software behavior. There is no trusted component-to-partition map, updater, persistent trust/version state, inactive slot, health/rollback protocol, full backup or demonstrated recovery. A valid bundle is not an installable or flashable image.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; parent checkpoint `7c63b0e`. The B1 checkpoint is the commit containing this file and is pushed to `origin/main` after focused verification; use `git log -1 --oneline` for its immutable ID.

**LOCAL UNTRACKED OR PRIVATE WORK (NO SECRETS):** proprietary firmware/FDT/U-Boot, bounded helpers, extracted trees and isolated WSL analyzer/upstream environments remain local/private and are not Git-backed. No signing private key exists in this work. Do not delete or upload private artifacts.

**WHAT REMAINS UNFINISHED:** B2 implementation/tests; a signed trust-policy format; production key custody; trusted release-catalog persistence; device-side hardware identity; component installation mapping; atomic staging/writes; durable version/health state; rollback; full device backup; and every matching-spare recovery demonstration.

**NEXT SINGLE TASK ID + INPUT:** **B2** — implement a host-only parser/verifier for `docs/UPDATE_BUNDLE_SPEC.md` and bounded synthetic positive/negative tests. Use synthetic payloads and test-only keys; perform no extraction, flash logic or device access. Do not begin B3.

**PASS CRITERION FOR NEXT TASK:** the verifier separately reports structure, signature/hash, exact-profile compatibility and version-policy results; reads with bounded memory; rejects the specified malformed/truncated/oversized/mismatched/tampered/downgrade cases; passes focused tests; and contains no production key, proprietary payload, camera code or flash-write path.

**RECOMMENDED REASONING + WHY:** **High** for B2. It is security-sensitive untrusted-input parsing and cryptographic verification with adversarial boundary cases; implementation and negative-test review warrant High.

**WHEN TO SWITCH:** Medium is sufficient once core parsing, signature verification and adversarial tests pass and only routine documentation remains. Consider Ultra only for a narrowly scoped security failure that persists after two materially different hypotheses; none is currently known.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** reliable Codex telemetry at 2026-10-16 03:11 PDT reported 12% used in the five-hour window and 34% used in the weekly window (88% and 66% remaining respectively). This is a timestamped snapshot, not continuous monitoring.

**USAGE PREPARATION:** B1 is committed and pushed before B2. Recheck telemetry at the next task boundary and checkpoint before adding a cryptographic dependency or generated fixtures; test keys must be explicitly non-production.

**CONTINUE OR STOP + REASON:** **STOP after B1**, as explicitly requested. Do not start B2 automatically.

**CAMERA CONTACT/FLASH:** NONE. No discovery, connection, reboot, modification or flash was performed or authorized.
