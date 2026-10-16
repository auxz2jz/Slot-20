#!/usr/bin/env python3
"""Deterministic, host-only update and boot-state simulator for Slot-20.

The state names describe logical milestones only. In particular,
``writing_candidate``, ``rolled_back`` and ``recovery_required`` do not imply
that the camera has an A/B layout, a writable target, a boot selector or a
working recovery mechanism. This module performs no device, network or flash
I/O and contains no power-loss/fault-injection machinery.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Any, Mapping

from verify_update_bundle import (
    LOWER_SHA256_RE,
    MAX_SAFE_INTEGER,
    SEMVER_RE,
    TARGET_HARDWARE_PROFILE,
    VerificationResult,
)


STATE_SCHEMA = "slot20.update-state.v2"
STATE_CHECKSUM_DOMAIN = b"SLOT20-UPDATE-STATE-V2\x00"
SIMULATION_AUTHORIZATION_SCOPE = "host-simulation-only"
MAX_STATE_FILE_BYTES = 16_384
MAX_RELEASE_VERSION_BYTES = 64
MAX_APPROVAL_ID_BYTES = 64
MAX_FAILURE_CODE_BYTES = 64

STATE_FIELDS = frozenset(
    {
        "schema",
        "generation",
        "state",
        "known_good",
        "previous_known_good",
        "candidate",
        "verification_passed",
        "simulation_install_authorized",
        "authorization_id",
        "failure",
        "record_sha256",
    }
)
VERSION_FIELDS = frozenset(
    {
        "hardware_profile",
        "release_version",
        "release_sequence",
        "security_epoch",
        "bundle_sha256",
    }
)
FAILURE_FIELDS = frozenset({"phase", "code"})
STATE_NAMES = frozenset(
    {
        "idle",
        "receiving",
        "verifying",
        "verified",
        "staged",
        "writing_candidate",
        "pending_boot",
        "healthy",
        "committed",
        "failed",
        "rolled_back",
        "recovery_required",
    }
)
APPROVAL_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}\Z", re.ASCII)
FAILURE_CODE_RE = re.compile(r"[a-z][a-z0-9._-]{0,63}\Z", re.ASCII)


class StateFormatError(ValueError):
    """Persisted state is malformed, non-canonical or internally inconsistent."""


class StateTransitionError(RuntimeError):
    """A requested state transition is not permitted."""


@dataclass(frozen=True)
class VersionRef:
    """Bounded identity for a simulated release, never a flash target."""

    hardware_profile: str
    release_version: str
    release_sequence: int
    security_epoch: int
    bundle_sha256: str

    def __post_init__(self) -> None:
        if self.hardware_profile != TARGET_HARDWARE_PROFILE:
            raise ValueError("hardware_profile must match the Slot-20 target")
        if (
            not isinstance(self.release_version, str)
            or not 1 <= len(self.release_version) <= MAX_RELEASE_VERSION_BYTES
            or not self.release_version.isascii()
            or SEMVER_RE.fullmatch(self.release_version) is None
        ):
            raise ValueError("release_version must be valid SemVer")
        _validate_counter("release_sequence", self.release_sequence)
        _validate_counter("security_epoch", self.security_epoch)
        if not isinstance(self.bundle_sha256, str) or LOWER_SHA256_RE.fullmatch(
            self.bundle_sha256
        ) is None:
            raise ValueError("bundle_sha256 must be a lowercase SHA-256 digest")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hardware_profile": self.hardware_profile,
            "release_version": self.release_version,
            "release_sequence": self.release_sequence,
            "security_epoch": self.security_epoch,
            "bundle_sha256": self.bundle_sha256,
        }

    @classmethod
    def from_dict(cls, value: Any) -> VersionRef:
        if not isinstance(value, dict) or set(value) != VERSION_FIELDS:
            raise StateFormatError("version record has unexpected fields")
        try:
            return cls(**value)
        except (TypeError, ValueError) as exc:
            raise StateFormatError(f"invalid version record: {exc}") from exc

    @classmethod
    def from_verification(cls, result: VerificationResult) -> VersionRef:
        if not isinstance(result, VerificationResult):
            raise TypeError("result must be a VerificationResult")
        manifest = result.manifest
        if not result.host_verification_passed or not isinstance(manifest, Mapping):
            raise ValueError("verification result is not a passing manifest")
        try:
            return cls(
                hardware_profile=manifest["hardware_profile"],
                release_version=manifest["release_version"],
                release_sequence=manifest["release_sequence"],
                security_epoch=manifest["security_epoch"],
                bundle_sha256=result.bundle_sha256,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("verification result lacks valid release identity") from exc


@dataclass(frozen=True)
class SimulationInstallAuthorization:
    """Explicit authorization usable only by this host simulator."""

    bundle_sha256: str
    approval_id: str
    approved: bool
    scope: str = SIMULATION_AUTHORIZATION_SCOPE

    def __post_init__(self) -> None:
        if not isinstance(self.bundle_sha256, str) or LOWER_SHA256_RE.fullmatch(
            self.bundle_sha256
        ) is None:
            raise ValueError("bundle_sha256 must be a lowercase SHA-256 digest")
        if not isinstance(self.approval_id, str) or APPROVAL_ID_RE.fullmatch(
            self.approval_id
        ) is None:
            raise ValueError("approval_id is invalid or too long")
        if type(self.approved) is not bool:
            raise TypeError("approved must be a boolean")
        if self.scope != SIMULATION_AUTHORIZATION_SCOPE:
            raise ValueError("authorization scope is not host-simulation-only")


class UpdateStateSimulator:
    """Validated single-record state machine persisted as canonical JSON."""

    def __init__(self, path: Path, record: dict[str, Any]) -> None:
        self._path = path
        self._record = record

    @classmethod
    def create(cls, path: str | os.PathLike[str], known_good: VersionRef):
        state_path = Path(path)
        if not isinstance(known_good, VersionRef):
            raise TypeError("known_good must be a VersionRef")
        record = {
            "schema": STATE_SCHEMA,
            "generation": 0,
            "state": "idle",
            "known_good": known_good.to_dict(),
            "previous_known_good": None,
            "candidate": None,
            "verification_passed": False,
            "simulation_install_authorized": False,
            "authorization_id": None,
            "failure": None,
            "record_sha256": "",
        }
        _seal_record(record)
        _validate_record(record)
        _write_record(state_path, record, require_absent=True)
        return cls(state_path, record)

    @classmethod
    def load(
        cls,
        path: str | os.PathLike[str],
        *,
        minimum_generation: int | None = None,
    ):
        state_path = Path(path)
        if minimum_generation is not None:
            try:
                _validate_counter("minimum_generation", minimum_generation)
            except ValueError as exc:
                raise StateFormatError(str(exc)) from exc
        data = _read_bounded_regular_file(state_path)
        try:
            record = json.loads(data, object_pairs_hook=_reject_duplicate_keys)
        except (UnicodeDecodeError, json.JSONDecodeError, StateFormatError) as exc:
            raise StateFormatError("state is not strict JSON") from exc
        _validate_record(record)
        if data != _encode_record(record):
            raise StateFormatError("state is not canonical JSON")
        if (
            minimum_generation is not None
            and record["generation"] < minimum_generation
        ):
            raise StateFormatError("state generation is below the trusted minimum")
        return cls(state_path, record)

    @property
    def state(self) -> str:
        return self._record["state"]

    @property
    def generation(self) -> int:
        return self._record["generation"]

    @property
    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(self._record)

    @property
    def known_good(self) -> VersionRef:
        return VersionRef.from_dict(self._record["known_good"])

    def begin_receiving(self, candidate: VersionRef) -> None:
        if not isinstance(candidate, VersionRef):
            raise TypeError("candidate must be a VersionRef")
        self._advance(
            {"idle", "committed", "rolled_back"},
            state="receiving",
            candidate=candidate.to_dict(),
            verification_passed=False,
            simulation_install_authorized=False,
            authorization_id=None,
            failure=None,
        )

    def begin_verification(self) -> None:
        self._advance({"receiving"}, state="verifying")

    def record_verification(self, result: VerificationResult) -> None:
        self._require_state({"verifying"})
        if not isinstance(result, VerificationResult):
            raise TypeError("result must be a VerificationResult")
        if result.installation_authorized:
            raise StateTransitionError(
                "bundle verification cannot authorize installation"
            )
        try:
            verified_version = VersionRef.from_verification(result)
        except ValueError:
            self._advance(
                {"verifying"},
                state="failed",
                verification_passed=False,
                simulation_install_authorized=False,
                authorization_id=None,
                failure={"phase": "verification", "code": "bundle_rejected"},
            )
            return
        if verified_version.to_dict() != self._record["candidate"]:
            self._advance(
                {"verifying"},
                state="failed",
                verification_passed=False,
                simulation_install_authorized=False,
                authorization_id=None,
                failure={"phase": "verification", "code": "identity_mismatch"},
            )
            return
        self._advance(
            {"verifying"},
            state="verified",
            verification_passed=True,
        )

    def authorize_install(
        self, authorization: SimulationInstallAuthorization
    ) -> None:
        self._require_state({"verified"})
        if not isinstance(authorization, SimulationInstallAuthorization):
            raise TypeError("authorization must be a SimulationInstallAuthorization")
        if not authorization.approved:
            raise StateTransitionError("simulation installation was not approved")
        if authorization.bundle_sha256 != self._record["candidate"]["bundle_sha256"]:
            raise StateTransitionError("authorization does not match the candidate")
        self._advance(
            {"verified"},
            simulation_install_authorized=True,
            authorization_id=authorization.approval_id,
        )

    def stage_candidate(self) -> None:
        self._require_state({"verified"})
        if not self._record["simulation_install_authorized"]:
            raise StateTransitionError(
                "verified bundle lacks separate simulation install authorization"
            )
        self._advance({"verified"}, state="staged")

    def begin_candidate_write(self) -> None:
        self._advance({"staged"}, state="writing_candidate")

    def mark_pending_boot(self) -> None:
        self._advance({"writing_candidate"}, state="pending_boot")

    def confirm_boot_healthy(self) -> None:
        self._advance({"pending_boot"}, state="healthy")

    def commit_healthy_candidate(self) -> None:
        self._require_state({"healthy"})
        next_record = copy.deepcopy(self._record)
        next_record.update(
            state="committed",
            previous_known_good=copy.deepcopy(next_record["known_good"]),
            known_good=copy.deepcopy(next_record["candidate"]),
            candidate=None,
            verification_passed=False,
            simulation_install_authorized=False,
            authorization_id=None,
            failure=None,
        )
        self._commit_next(next_record)

    def record_boot_failure(self, code: str = "boot_unconfirmed") -> None:
        if not isinstance(code, str) or FAILURE_CODE_RE.fullmatch(code) is None:
            raise ValueError("failure code is invalid or too long")
        self._advance(
            {"pending_boot"},
            state="failed",
            failure={"phase": "boot", "code": code},
        )

    def select_known_good(self) -> None:
        self._require_failure_phase("boot")
        self._advance({"failed"}, state="rolled_back")

    def require_external_recovery(self) -> None:
        self._require_failure_phase("boot")
        self._advance({"failed"}, state="recovery_required")

    def discard_rejected_candidate(self) -> None:
        self._require_failure_phase("verification")
        self._advance(
            {"failed"},
            state="idle",
            candidate=None,
            verification_passed=False,
            simulation_install_authorized=False,
            authorization_id=None,
            failure=None,
        )

    def _require_failure_phase(self, phase: str) -> None:
        self._require_state({"failed"})
        failure = self._record["failure"]
        if failure is None or failure["phase"] != phase:
            raise StateTransitionError(f"failure is not from {phase}")

    def _require_state(self, allowed: set[str]) -> None:
        if self.state not in allowed:
            expected = ", ".join(sorted(allowed))
            raise StateTransitionError(
                f"state {self.state!r} does not allow this operation; expected {expected}"
            )

    def _advance(self, allowed: set[str], **changes: Any) -> None:
        self._require_state(allowed)
        next_record = copy.deepcopy(self._record)
        next_record.update(changes)
        self._commit_next(next_record)

    def _commit_next(self, next_record: dict[str, Any]) -> None:
        generation = self._record["generation"]
        if generation >= MAX_SAFE_INTEGER:
            raise StateTransitionError("state generation is exhausted")
        next_record["generation"] = generation + 1
        _seal_record(next_record)
        _validate_record(next_record)
        _write_record(self._path, next_record, require_absent=False)
        self._record = next_record


def _validate_counter(name: str, value: Any) -> None:
    if type(value) is not int or not 0 <= value <= MAX_SAFE_INTEGER:
        raise ValueError(f"{name} must be a non-negative safe integer")


def _validate_record(record: Any) -> None:
    if not isinstance(record, dict) or set(record) != STATE_FIELDS:
        raise StateFormatError("state record has unexpected fields")
    if record["schema"] != STATE_SCHEMA:
        raise StateFormatError("unsupported state schema")
    record_sha256 = record["record_sha256"]
    if not isinstance(record_sha256, str) or LOWER_SHA256_RE.fullmatch(
        record_sha256
    ) is None:
        raise StateFormatError("record checksum is invalid")
    if not hmac.compare_digest(record_sha256, _calculate_record_sha256(record)):
        raise StateFormatError("record checksum mismatch")
    try:
        _validate_counter("generation", record["generation"])
    except ValueError as exc:
        raise StateFormatError(str(exc)) from exc
    state = record["state"]
    if not isinstance(state, str) or state not in STATE_NAMES:
        raise StateFormatError("unknown state")
    VersionRef.from_dict(record["known_good"])
    if record["previous_known_good"] is not None:
        VersionRef.from_dict(record["previous_known_good"])
    if record["candidate"] is not None:
        VersionRef.from_dict(record["candidate"])
    if type(record["verification_passed"]) is not bool:
        raise StateFormatError("verification_passed must be a boolean")
    if type(record["simulation_install_authorized"]) is not bool:
        raise StateFormatError("simulation_install_authorized must be a boolean")
    authorization_id = record["authorization_id"]
    if authorization_id is not None and (
        not isinstance(authorization_id, str)
        or APPROVAL_ID_RE.fullmatch(authorization_id) is None
    ):
        raise StateFormatError("authorization_id is invalid or too long")
    failure = record["failure"]
    if failure is not None:
        if not isinstance(failure, dict) or set(failure) != FAILURE_FIELDS:
            raise StateFormatError("failure record has unexpected fields")
        if not isinstance(failure["phase"], str) or failure["phase"] not in {
            "verification",
            "boot",
        }:
            raise StateFormatError("failure phase is invalid")
        if not isinstance(failure["code"], str) or FAILURE_CODE_RE.fullmatch(
            failure["code"]
        ) is None:
            raise StateFormatError("failure code is invalid or too long")

    candidate_present = record["candidate"] is not None
    verified = record["verification_passed"]
    authorized = record["simulation_install_authorized"]
    auth_present = authorization_id is not None

    if state == "idle":
        valid = not candidate_present and not verified and not authorized and failure is None
    elif state in {"receiving", "verifying"}:
        valid = candidate_present and not verified and not authorized and failure is None
    elif state == "verified":
        valid = candidate_present and verified and failure is None
    elif state in {"staged", "writing_candidate", "pending_boot", "healthy"}:
        valid = candidate_present and verified and authorized and failure is None
    elif state == "committed":
        valid = (
            not candidate_present
            and not verified
            and not authorized
            and failure is None
            and record["previous_known_good"] is not None
        )
    elif state == "failed":
        valid = candidate_present and failure is not None and (
            (failure["phase"] == "verification" and not verified and not authorized)
            or (failure["phase"] == "boot" and verified and authorized)
        )
    else:  # rolled_back or recovery_required
        valid = (
            candidate_present
            and verified
            and authorized
            and failure is not None
            and failure["phase"] == "boot"
        )

    if authorized != auth_present:
        valid = False
    if not valid:
        raise StateFormatError("state record violates transition invariants")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StateFormatError("duplicate JSON member")
        result[key] = value
    return result


def _canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise StateFormatError("state cannot be encoded") from exc


def _calculate_record_sha256(record: Mapping[str, Any]) -> str:
    unsigned = {key: value for key, value in record.items() if key != "record_sha256"}
    payload = STATE_CHECKSUM_DOMAIN + _canonical_json(unsigned)
    return hashlib.sha256(payload).hexdigest()


def _seal_record(record: dict[str, Any]) -> None:
    record["record_sha256"] = _calculate_record_sha256(record)


def _encode_record(record: dict[str, Any]) -> bytes:
    data = _canonical_json(record)
    if len(data) > MAX_STATE_FILE_BYTES:
        raise StateFormatError("state exceeds the bounded file size")
    return data


def _read_bounded_regular_file(path: Path) -> bytes:
    try:
        path_info = path.lstat()
        if not stat.S_ISREG(path_info.st_mode):
            raise StateFormatError("state path is not a regular file")
        with path.open("rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise StateFormatError("state path is not a regular file")
            if info.st_size <= 0 or info.st_size > MAX_STATE_FILE_BYTES:
                raise StateFormatError("state file size is out of bounds")
            data = handle.read(MAX_STATE_FILE_BYTES + 1)
    except OSError as exc:
        raise StateFormatError(f"cannot read state file: {exc}") from exc
    if len(data) > MAX_STATE_FILE_BYTES:
        raise StateFormatError("state file size is out of bounds")
    return data


def _write_record(path: Path, record: dict[str, Any], require_absent: bool) -> None:
    _validate_record(record)
    data = _encode_record(record)
    parent = path.parent
    if not parent.is_dir():
        raise StateFormatError("state parent directory does not exist")
    try:
        existing = path.lstat()
    except FileNotFoundError:
        existing = None
    except OSError as exc:
        raise StateFormatError(f"cannot inspect state path: {exc}") from exc
    if existing is not None:
        if require_absent:
            raise FileExistsError(f"state file already exists: {path}")
        if not stat.S_ISREG(existing.st_mode):
            raise StateFormatError("state path is not a regular file")

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
