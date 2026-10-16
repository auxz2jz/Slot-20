"""Deterministic B4 file-fault tests for the host-only state simulator.

These tests exercise ordinary host filesystem call boundaries. They do not
model NAND programming, controller caches, an A/B layout or camera hardware.
"""

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import update_state_simulator as state  # noqa: E402
from verify_update_bundle import CheckResult, VerificationResult  # noqa: E402


PASS = CheckResult("pass", "ok")


class SimulatedPowerLoss(BaseException):
    """Abrupt test interruption that bypasses ordinary exception cleanup."""


def digest(label):
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def version(label, release_version, sequence):
    return state.VersionRef(
        hardware_profile=state.TARGET_HARDWARE_PROFILE,
        release_version=release_version,
        release_sequence=sequence,
        security_epoch=1,
        bundle_sha256=digest(label),
    )


def passing_verification(candidate):
    return VerificationResult(
        structure=PASS,
        authenticity=PASS,
        compatibility=PASS,
        version_policy=PASS,
        bundle_sha256=candidate.bundle_sha256,
        manifest={
            "hardware_profile": candidate.hardware_profile,
            "release_version": candidate.release_version,
            "release_sequence": candidate.release_sequence,
            "security_epoch": candidate.security_epoch,
        },
        installation_authorized=False,
    )


class UpdateStateFaultTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.path = self.root / "update-state.json"
        self.known_good = version("known-good", "1.0.0", 1)
        self.candidate = version("candidate", "1.1.0", 2)

    def create(self):
        return state.UpdateStateSimulator.create(self.path, self.known_good)

    def authorize(self, simulator):
        simulator.authorize_install(
            state.SimulationInstallAuthorization(
                bundle_sha256=self.candidate.bundle_sha256,
                approval_id="b4-test-approval",
                approved=True,
            )
        )

    def reach_verified(self, simulator):
        simulator.begin_receiving(self.candidate)
        simulator.begin_verification()
        simulator.record_verification(passing_verification(self.candidate))

    def reach_healthy(self, simulator):
        self.reach_verified(simulator)
        self.authorize(simulator)
        simulator.stage_candidate()
        simulator.begin_candidate_write()
        simulator.mark_pending_boot()
        simulator.confirm_boot_healthy()

    def orphan_temporary_files(self):
        return sorted(self.root.glob(f".{self.path.name}.*.tmp"))

    def test_power_loss_before_temporary_fsync_keeps_old_primary(self):
        simulator = self.create()
        old_bytes = self.path.read_bytes()

        with mock.patch.object(state.os, "fsync", side_effect=SimulatedPowerLoss):
            with self.assertRaises(SimulatedPowerLoss):
                simulator.begin_receiving(self.candidate)

        self.assertEqual(simulator.state, "idle")
        self.assertEqual(self.path.read_bytes(), old_bytes)
        self.assertEqual(len(self.orphan_temporary_files()), 1)
        reloaded = state.UpdateStateSimulator.load(self.path)
        self.assertEqual(reloaded.state, "idle")
        self.assertEqual(reloaded.known_good, self.known_good)

    def test_power_loss_before_replace_keeps_old_primary_and_ignores_orphan(self):
        simulator = self.create()
        self.reach_verified(simulator)
        self.authorize(simulator)
        old_bytes = self.path.read_bytes()
        old_generation = simulator.generation

        with mock.patch.object(state.os, "replace", side_effect=SimulatedPowerLoss):
            with self.assertRaises(SimulatedPowerLoss):
                simulator.stage_candidate()

        self.assertEqual(simulator.state, "verified")
        self.assertEqual(simulator.generation, old_generation)
        self.assertEqual(self.path.read_bytes(), old_bytes)
        self.assertEqual(len(self.orphan_temporary_files()), 1)
        reloaded = state.UpdateStateSimulator.load(self.path)
        self.assertEqual(reloaded.state, "verified")
        self.assertEqual(reloaded.known_good, self.known_good)

    def test_power_loss_after_replace_recovers_new_complete_commit(self):
        simulator = self.create()
        self.reach_healthy(simulator)
        old_generation = simulator.generation
        real_replace = state.os.replace

        def replace_then_power_loss(source, destination):
            real_replace(source, destination)
            raise SimulatedPowerLoss

        with mock.patch.object(state.os, "replace", side_effect=replace_then_power_loss):
            with self.assertRaises(SimulatedPowerLoss):
                simulator.commit_healthy_candidate()

        self.assertEqual(simulator.state, "healthy")
        self.assertEqual(simulator.known_good, self.known_good)
        self.assertEqual(self.orphan_temporary_files(), [])

        reloaded = state.UpdateStateSimulator.load(
            self.path, minimum_generation=old_generation + 1
        )
        self.assertEqual(reloaded.state, "committed")
        self.assertEqual(reloaded.known_good, self.candidate)
        self.assertEqual(
            state.VersionRef.from_dict(reloaded.snapshot["previous_known_good"]),
            self.known_good,
        )

    def test_replace_io_error_cleans_temporary_and_keeps_old_primary(self):
        simulator = self.create()
        old_bytes = self.path.read_bytes()

        with mock.patch.object(state.os, "replace", side_effect=OSError("injected")):
            with self.assertRaises(OSError):
                simulator.begin_receiving(self.candidate)

        self.assertEqual(self.path.read_bytes(), old_bytes)
        self.assertEqual(self.orphan_temporary_files(), [])
        self.assertEqual(
            state.UpdateStateSimulator.load(self.path).known_good,
            self.known_good,
        )

    def test_partial_primary_records_fail_closed_at_selected_lengths(self):
        simulator = self.create()
        self.reach_healthy(simulator)
        complete = self.path.read_bytes()
        cuts = (0, 1, len(complete) // 2, len(complete) - 1)

        for cut in cuts:
            with self.subTest(cut=cut):
                self.path.write_bytes(complete[:cut])
                with self.assertRaises(state.StateFormatError):
                    state.UpdateStateSimulator.load(self.path)

    def test_missing_primary_fails_closed_even_with_complete_orphan(self):
        simulator = self.create()
        self.reach_verified(simulator)
        orphan = self.root / f".{self.path.name}.saved.tmp"
        orphan.write_bytes(self.path.read_bytes())
        self.path.unlink()

        with self.assertRaises(state.StateFormatError):
            state.UpdateStateSimulator.load(self.path)
        self.assertTrue(orphan.is_file())

    def test_accidental_known_good_corruption_is_detected_by_checksum(self):
        simulator = self.create()
        self.reach_verified(simulator)
        original = self.path.read_bytes()
        old_digest = self.known_good.bundle_sha256.encode("ascii")
        replacement = (
            (b"0" if old_digest[:1] != b"0" else b"1") + old_digest[1:]
        )
        corrupted = original.replace(old_digest, replacement, 1)
        self.assertNotEqual(corrupted, original)
        self.path.write_bytes(corrupted)

        with self.assertRaisesRegex(state.StateFormatError, "checksum mismatch"):
            state.UpdateStateSimulator.load(self.path)

    def test_checksum_corruption_is_detected(self):
        simulator = self.create()
        data = bytearray(self.path.read_bytes())
        marker = b'"record_sha256":"'
        checksum_start = data.index(marker) + len(marker)
        data[checksum_start] = ord("0") if data[checksum_start] != ord("0") else ord("1")
        self.path.write_bytes(data)

        with self.assertRaisesRegex(state.StateFormatError, "checksum mismatch"):
            state.UpdateStateSimulator.load(self.path)

    def test_checksum_valid_but_semantically_invalid_state_fails_closed(self):
        simulator = self.create()
        self.reach_verified(simulator)
        malformed = simulator.snapshot
        malformed["state"] = "committed"
        state._seal_record(malformed)
        self.path.write_bytes(state._encode_record(malformed))

        with self.assertRaisesRegex(
            state.StateFormatError, "transition invariants"
        ):
            state.UpdateStateSimulator.load(self.path)

    def test_stale_record_requires_external_generation_floor_for_detection(self):
        simulator = self.create()
        self.reach_healthy(simulator)
        stale_bytes = self.path.read_bytes()
        stale_generation = simulator.generation
        simulator.commit_healthy_candidate()
        latest_generation = simulator.generation
        self.assertEqual(simulator.known_good, self.candidate)

        self.path.write_bytes(stale_bytes)
        stale = state.UpdateStateSimulator.load(self.path)
        self.assertEqual(stale.generation, stale_generation)
        self.assertEqual(stale.known_good, self.known_good)
        with self.assertRaisesRegex(state.StateFormatError, "trusted minimum"):
            state.UpdateStateSimulator.load(
                self.path, minimum_generation=latest_generation
            )

    def test_invalid_external_generation_floor_fails_closed(self):
        self.create()
        for invalid in (-1, True, state.MAX_SAFE_INTEGER + 1):
            with self.subTest(minimum_generation=invalid):
                with self.assertRaises(state.StateFormatError):
                    state.UpdateStateSimulator.load(
                        self.path, minimum_generation=invalid
                    )


if __name__ == "__main__":
    unittest.main()
