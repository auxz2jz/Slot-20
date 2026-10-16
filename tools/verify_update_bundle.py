#!/usr/bin/env python3
"""Bounded, host-only verifier for Slot-20 update bundles.

This module implements docs/UPDATE_BUNDLE_SPEC.md version 1. It verifies an
already assembled file and returns separate structure, authenticity,
compatibility, and version-policy decisions. It has no extraction, device I/O,
partition mapping, installation, or flash-writing functionality.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat
import struct
from types import MappingProxyType
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


MAGIC = b"S20BNDL1"
FORMAT_VERSION = 1
HEADER_SIZE = 32
SIGNATURE_SIZE = 64
MAX_MANIFEST_BYTES = 65_536
MAX_COMPONENTS = 16
MAX_COMPONENT_BYTES = 67_108_864
MAX_PAYLOAD_BYTES = 134_217_728
MAX_BUNDLE_BYTES = HEADER_SIZE + MAX_MANIFEST_BYTES + MAX_PAYLOAD_BYTES + SIGNATURE_SIZE
MAX_SAFE_INTEGER = 9_007_199_254_740_991
READ_CHUNK_SIZE = 1024 * 1024
TARGET_HARDWARE_PROFILE = "reolink.rlc-811a.ipc_523128m8mp"
SCHEMA = "slot20.update-bundle.v1"
SIGNATURE_DOMAIN = b"SLOT20-BUNDLE-SIGNATURE-V1\x00"
HEADER_STRUCT = struct.Struct(">8sHHIHHQI")

TOP_LEVEL_FIELDS = frozenset(
    {
        "schema",
        "hardware_profile",
        "release_version",
        "release_sequence",
        "security_epoch",
        "signing_key_id",
        "components",
    }
)
COMPONENT_FIELDS = frozenset({"id", "type", "length", "sha256"})
IDENTIFIER_RE = re.compile(r"[a-z][a-z0-9._-]{0,31}\Z", re.ASCII)
PROFILE_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z", re.ASCII)
LOWER_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
SEMVER_RE = re.compile(
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?\Z",
    re.ASCII,
)


@dataclass(frozen=True)
class CheckResult:
    """One verification layer's concise, data-free outcome."""

    status: str
    code: str

    @property
    def passed(self) -> bool:
        return self.status == "pass"


NOT_CHECKED = CheckResult("not_checked", "not_checked")


@dataclass(frozen=True)
class VerificationResult:
    """Host verification result; never an installation authorization."""

    structure: CheckResult
    authenticity: CheckResult
    compatibility: CheckResult
    version_policy: CheckResult
    bundle_sha256: str | None = None
    manifest: Mapping[str, Any] | None = None
    installation_authorized: bool = False

    @property
    def host_verification_passed(self) -> bool:
        return all(
            check.passed
            for check in (
                self.structure,
                self.authenticity,
                self.compatibility,
                self.version_policy,
            )
        )


@dataclass(frozen=True)
class TrustedKeyRecord:
    """One independently provisioned public-key trust record."""

    public_key: Ed25519PublicKey
    hardware_profiles: frozenset[str]
    status: str = "active"
    minimum_security_epoch: int = 0
    maximum_security_epoch: int = MAX_SAFE_INTEGER

    def __post_init__(self) -> None:
        if not isinstance(self.public_key, Ed25519PublicKey):
            raise TypeError("public_key must be an Ed25519 public key")
        profiles = frozenset(self.hardware_profiles)
        if not profiles or any(not _valid_profile_syntax(value) for value in profiles):
            raise ValueError("hardware_profiles must contain valid profile identifiers")
        if self.status not in {"active", "retired", "revoked"}:
            raise ValueError("invalid key status")
        _require_safe_integer(self.minimum_security_epoch, "minimum_security_epoch")
        _require_safe_integer(self.maximum_security_epoch, "maximum_security_epoch")
        if self.minimum_security_epoch > self.maximum_security_epoch:
            raise ValueError("key security-epoch bounds are reversed")
        object.__setattr__(self, "hardware_profiles", profiles)

    @property
    def key_id(self) -> str:
        raw = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return hashlib.sha256(raw).hexdigest()


class TrustStore:
    """Immutable lookup of independently trusted public keys."""

    def __init__(self, records: list[TrustedKeyRecord] | tuple[TrustedKeyRecord, ...]):
        indexed: dict[str, TrustedKeyRecord] = {}
        for record in records:
            if not isinstance(record, TrustedKeyRecord):
                raise TypeError("trust store entries must be TrustedKeyRecord values")
            if record.key_id in indexed:
                raise ValueError("duplicate trusted key ID")
            indexed[record.key_id] = record
        self._records = MappingProxyType(indexed)

    def get(self, key_id: str) -> TrustedKeyRecord | None:
        return self._records.get(key_id)


ReleaseTuple = tuple[str, int, int]


@dataclass(frozen=True)
class VersionPolicy:
    """Authenticated host policy/state used after bundle verification."""

    hardware_profile: str
    current_security_epoch: int
    current_release_sequence: int
    current_bundle_sha256: str
    minimum_security_epoch: int
    supported_releases: Mapping[ReleaseTuple, str]
    allow_reinstall: bool = False
    allow_downgrade: bool = False
    recovery_ready: bool = False

    def __post_init__(self) -> None:
        if self.hardware_profile != TARGET_HARDWARE_PROFILE:
            raise ValueError("B2 policy must target the exact Slot-20 hardware profile")
        _require_safe_integer(self.current_security_epoch, "current_security_epoch")
        _require_safe_integer(self.current_release_sequence, "current_release_sequence")
        _require_safe_integer(self.minimum_security_epoch, "minimum_security_epoch")
        if self.minimum_security_epoch > self.current_security_epoch:
            raise ValueError("minimum security epoch exceeds current epoch")
        if not _valid_sha256(self.current_bundle_sha256):
            raise ValueError("current bundle SHA-256 must be lowercase hexadecimal")
        for value, name in (
            (self.allow_reinstall, "allow_reinstall"),
            (self.allow_downgrade, "allow_downgrade"),
            (self.recovery_ready, "recovery_ready"),
        ):
            if type(value) is not bool:
                raise TypeError(f"{name} must be boolean")

        catalog: dict[ReleaseTuple, str] = {}
        for release, digest in self.supported_releases.items():
            if not isinstance(release, tuple) or len(release) != 3:
                raise ValueError("release catalog keys must be three-item tuples")
            profile, epoch, sequence = release
            if profile != self.hardware_profile:
                raise ValueError("release catalog contains another hardware profile")
            _require_safe_integer(epoch, "catalog security_epoch")
            _require_safe_integer(sequence, "catalog release_sequence")
            if not _valid_sha256(digest):
                raise ValueError("release catalog digest must be lowercase SHA-256")
            catalog[(profile, epoch, sequence)] = digest
        object.__setattr__(self, "supported_releases", MappingProxyType(catalog))


class _Reject(Exception):
    def __init__(self, stage: str, code: str):
        super().__init__(code)
        self.stage = stage
        self.code = code


class _DuplicateName(ValueError):
    pass


def verify_bundle(
    bundle_path: str | os.PathLike[str],
    trust_store: TrustStore,
    policy: VersionPolicy,
) -> VerificationResult:
    """Verify one bundle from a single bounded file handle.

    Failures are returned as concise codes. Unauthenticated manifest data is
    never returned. ``installation_authorized`` is always false by design.
    """

    if not isinstance(trust_store, TrustStore):
        raise TypeError("trust_store must be a TrustStore")
    if not isinstance(policy, VersionPolicy):
        raise TypeError("policy must be a VersionPolicy")

    path = Path(bundle_path)
    try:
        path_stat = path.lstat()
        if not stat.S_ISREG(path_stat.st_mode):
            raise _Reject("structure", "bundle_not_regular_file")
        with path.open("rb") as handle:
            return _verify_open_bundle(handle, trust_store, policy)
    except _Reject as rejection:
        return _failure_result(rejection.stage, rejection.code)
    except OSError:
        return _failure_result("structure", "bundle_io_error")


def _verify_open_bundle(handle, trust_store: TrustStore, policy: VersionPolicy) -> VerificationResult:
    initial_stat = os.fstat(handle.fileno())
    if not stat.S_ISREG(initial_stat.st_mode):
        raise _Reject("structure", "bundle_not_regular_file")
    if initial_stat.st_size > MAX_BUNDLE_BYTES:
        raise _Reject("structure", "bundle_size_limit")

    header = _read_exact(handle, HEADER_SIZE, "truncated_header")
    try:
        (
            magic,
            format_version,
            header_length,
            manifest_length,
            component_count,
            signature_length,
            payload_length,
            flags,
        ) = HEADER_STRUCT.unpack(header)
    except struct.error as error:
        raise _Reject("structure", "invalid_header") from error

    if magic != MAGIC:
        raise _Reject("structure", "bad_magic")
    if format_version != FORMAT_VERSION:
        raise _Reject("structure", "unsupported_format_version")
    if header_length != HEADER_SIZE:
        raise _Reject("structure", "bad_header_length")
    if not 2 <= manifest_length <= MAX_MANIFEST_BYTES:
        raise _Reject("structure", "manifest_length_limit")
    if not 1 <= component_count <= MAX_COMPONENTS:
        raise _Reject("structure", "component_count_limit")
    if signature_length != SIGNATURE_SIZE:
        raise _Reject("structure", "bad_signature_length")
    if not 1 <= payload_length <= MAX_PAYLOAD_BYTES:
        raise _Reject("structure", "payload_length_limit")
    if flags != 0:
        raise _Reject("structure", "unknown_flags")

    expected_size = HEADER_SIZE + manifest_length + payload_length + signature_length
    if expected_size > MAX_BUNDLE_BYTES:
        raise _Reject("structure", "bundle_size_limit")
    if initial_stat.st_size < expected_size:
        raise _Reject("structure", "truncated_bundle")
    if initial_stat.st_size > expected_size:
        raise _Reject("structure", "trailing_data")

    manifest_bytes = _read_exact(handle, manifest_length, "truncated_manifest")
    manifest = _decode_manifest(manifest_bytes)
    components = _validate_manifest(manifest, component_count, payload_length)
    if _canonical_json(manifest) != manifest_bytes:
        raise _Reject("structure", "noncanonical_manifest")

    if manifest["hardware_profile"] != policy.hardware_profile:
        raise _Reject("compatibility", "hardware_profile_mismatch")

    key_record = trust_store.get(manifest["signing_key_id"])
    if key_record is None:
        raise _Reject("authenticity", "unknown_signing_key")
    if key_record.status != "active":
        raise _Reject("authenticity", "inactive_signing_key")
    if manifest["hardware_profile"] not in key_record.hardware_profiles:
        raise _Reject("authenticity", "signing_key_scope_mismatch")
    security_epoch = manifest["security_epoch"]
    if not key_record.minimum_security_epoch <= security_epoch <= key_record.maximum_security_epoch:
        raise _Reject("authenticity", "signing_key_epoch_mismatch")

    payload_offset = HEADER_SIZE + manifest_length
    signature_offset = payload_offset + payload_length
    handle.seek(signature_offset)
    signature = _read_exact(handle, SIGNATURE_SIZE, "truncated_signature")
    try:
        key_record.public_key.verify(signature, SIGNATURE_DOMAIN + header + manifest_bytes)
    except InvalidSignature as error:
        raise _Reject("authenticity", "invalid_signature") from error

    handle.seek(payload_offset)
    bundle_digest = hashlib.sha256()
    bundle_digest.update(header)
    bundle_digest.update(manifest_bytes)
    for component in components:
        component_digest = hashlib.sha256()
        remaining = component["length"]
        while remaining:
            chunk = handle.read(min(READ_CHUNK_SIZE, remaining))
            if not chunk:
                raise _Reject("structure", "truncated_payload")
            remaining -= len(chunk)
            component_digest.update(chunk)
            bundle_digest.update(chunk)
        if not hmac.compare_digest(component_digest.hexdigest(), component["sha256"]):
            raise _Reject("authenticity", "component_hash_mismatch")

    repeated_signature = _read_exact(handle, SIGNATURE_SIZE, "truncated_signature")
    if not hmac.compare_digest(signature, repeated_signature):
        raise _Reject("structure", "bundle_changed_during_verification")
    if handle.read(1):
        raise _Reject("structure", "trailing_data")
    if _stat_identity(os.fstat(handle.fileno())) != _stat_identity(initial_stat):
        raise _Reject("structure", "bundle_changed_during_verification")

    bundle_digest.update(signature)
    bundle_sha256 = bundle_digest.hexdigest()
    version_check = _evaluate_version_policy(manifest, bundle_sha256, policy)
    if not version_check.passed:
        return VerificationResult(
            structure=CheckResult("pass", "structure_valid"),
            authenticity=CheckResult("pass", "signature_and_hashes_valid"),
            compatibility=CheckResult("pass", "hardware_profile_match"),
            version_policy=version_check,
            bundle_sha256=bundle_sha256,
            manifest=MappingProxyType(manifest),
        )

    return VerificationResult(
        structure=CheckResult("pass", "structure_valid"),
        authenticity=CheckResult("pass", "signature_and_hashes_valid"),
        compatibility=CheckResult("pass", "hardware_profile_match"),
        version_policy=version_check,
        bundle_sha256=bundle_sha256,
        manifest=MappingProxyType(manifest),
    )


def _decode_manifest(manifest_bytes: bytes) -> dict[str, Any]:
    try:
        text = manifest_bytes.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_object_without_duplicates,
            parse_int=_bounded_json_integer,
            parse_float=_reject_json_number,
            parse_constant=_reject_json_number,
        )
    except _DuplicateName as error:
        raise _Reject("structure", "duplicate_json_name") from error
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        raise _Reject("structure", "invalid_manifest_json") from error
    if not isinstance(value, dict):
        raise _Reject("structure", "manifest_not_object")
    return value


def _validate_manifest(
    manifest: dict[str, Any], component_count: int, payload_length: int
) -> list[dict[str, Any]]:
    if set(manifest) != TOP_LEVEL_FIELDS:
        raise _Reject("structure", "manifest_fields_mismatch")
    if manifest["schema"] != SCHEMA:
        raise _Reject("structure", "unsupported_manifest_schema")
    if not _valid_profile_syntax(manifest["hardware_profile"]):
        raise _Reject("structure", "invalid_hardware_profile")

    release_version = manifest["release_version"]
    if (
        not isinstance(release_version, str)
        or not 1 <= len(release_version) <= 64
        or not release_version.isascii()
        or SEMVER_RE.fullmatch(release_version) is None
    ):
        raise _Reject("structure", "invalid_release_version")
    for field in ("release_sequence", "security_epoch"):
        if type(manifest[field]) is not int or not 0 <= manifest[field] <= MAX_SAFE_INTEGER:
            raise _Reject("structure", f"invalid_{field}")
    if not _valid_sha256(manifest["signing_key_id"]):
        raise _Reject("structure", "invalid_signing_key_id")

    components = manifest["components"]
    if not isinstance(components, list) or len(components) != component_count:
        raise _Reject("structure", "component_count_mismatch")

    component_ids: set[str] = set()
    component_types: set[str] = set()
    total_length = 0
    for component in components:
        if not isinstance(component, dict) or set(component) != COMPONENT_FIELDS:
            raise _Reject("structure", "component_fields_mismatch")
        component_id = component["id"]
        component_type = component["type"]
        if not isinstance(component_id, str) or IDENTIFIER_RE.fullmatch(component_id) is None:
            raise _Reject("structure", "invalid_component_id")
        if not isinstance(component_type, str) or IDENTIFIER_RE.fullmatch(component_type) is None:
            raise _Reject("structure", "invalid_component_type")
        if component_id in component_ids:
            raise _Reject("structure", "duplicate_component_id")
        if component_type in component_types:
            raise _Reject("structure", "duplicate_component_type")
        component_ids.add(component_id)
        component_types.add(component_type)

        length = component["length"]
        if type(length) is not int or not 1 <= length <= MAX_COMPONENT_BYTES:
            raise _Reject("structure", "component_length_limit")
        if not _valid_sha256(component["sha256"]):
            raise _Reject("structure", "invalid_component_sha256")
        total_length += length
        if total_length > MAX_PAYLOAD_BYTES:
            raise _Reject("structure", "payload_length_limit")

    if total_length != payload_length:
        raise _Reject("structure", "payload_length_mismatch")
    return components


def _evaluate_version_policy(
    manifest: Mapping[str, Any], bundle_sha256: str, policy: VersionPolicy
) -> CheckResult:
    epoch = manifest["security_epoch"]
    sequence = manifest["release_sequence"]
    if epoch < policy.minimum_security_epoch:
        return CheckResult("fail", "below_security_floor")

    release = (manifest["hardware_profile"], epoch, sequence)
    expected_digest = policy.supported_releases.get(release)
    if expected_digest is None:
        return CheckResult("fail", "release_not_in_trusted_catalog")
    if not hmac.compare_digest(expected_digest, bundle_sha256):
        return CheckResult("fail", "release_catalog_digest_mismatch")

    current = (policy.current_security_epoch, policy.current_release_sequence)
    candidate = (epoch, sequence)
    if epoch > policy.current_security_epoch:
        return CheckResult("pass", "upgrade_authorized")
    if epoch < policy.current_security_epoch:
        return CheckResult("fail", "cross_epoch_downgrade_forbidden")
    if candidate > current:
        return CheckResult("pass", "upgrade_authorized")
    if candidate == current:
        if policy.allow_reinstall:
            return CheckResult("pass", "reinstall_authorized")
        return CheckResult("fail", "reinstall_requires_explicit_authorization")
    if not policy.allow_downgrade:
        return CheckResult("fail", "downgrade_requires_explicit_authorization")
    if not policy.recovery_ready:
        return CheckResult("fail", "downgrade_requires_recovery_ready")
    return CheckResult("pass", "downgrade_authorized")


def _canonical_json(value: Any) -> bytes:
    """Serialize the accepted B1 ASCII/integer subset exactly as RFC 8785."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateName(key)
        result[key] = value
    return result


def _bounded_json_integer(text: str) -> int:
    if text.startswith("-") or len(text) > 16:
        raise ValueError("JSON integer is outside the accepted range")
    value = int(text)
    if value > MAX_SAFE_INTEGER:
        raise ValueError("JSON integer is outside the accepted range")
    return value


def _reject_json_number(_value: str) -> None:
    raise ValueError("only bounded non-negative integers are accepted")


def _read_exact(handle, length: int, code: str) -> bytes:
    chunks = bytearray()
    while len(chunks) < length:
        chunk = handle.read(length - len(chunks))
        if not chunk:
            raise _Reject("structure", code)
        chunks.extend(chunk)
    return bytes(chunks)


def _valid_profile_syntax(value: Any) -> bool:
    return isinstance(value, str) and PROFILE_RE.fullmatch(value) is not None


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and LOWER_SHA256_RE.fullmatch(value) is not None


def _require_safe_integer(value: Any, name: str) -> None:
    if type(value) is not int or not 0 <= value <= MAX_SAFE_INTEGER:
        raise ValueError(f"{name} must be a bounded non-negative integer")


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _failure_result(stage: str, code: str) -> VerificationResult:
    failed = CheckResult("fail", code)
    passed_structure = CheckResult("pass", "structure_valid")
    passed_compatibility = CheckResult("pass", "hardware_profile_match")
    if stage == "structure":
        return VerificationResult(failed, NOT_CHECKED, NOT_CHECKED, NOT_CHECKED)
    if stage == "compatibility":
        return VerificationResult(passed_structure, NOT_CHECKED, failed, NOT_CHECKED)
    if stage == "authenticity":
        return VerificationResult(
            passed_structure, failed, passed_compatibility, NOT_CHECKED
        )
    raise ValueError(f"unsupported failure stage: {stage}")
