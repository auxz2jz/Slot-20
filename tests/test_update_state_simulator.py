import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import update_state_simulator as state  # noqa: E402
from verify_update_bundle import CheckResult, VerificationResult  # noqa: E402


PASS = CheckResult("pass", "ok")
FAIL = CheckResult("fail", "rejected")


def digest(label):
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def version(label, release_version, sequence, epoch=1):
    return state.VersionRef(
        hardware_profile=state.TARGET_HARDWARE_PROFILE,
        release_version=release_version,
        release_sequence=sequence,
        security_epoch=epoch,
        bundle_sha256=digest(label),
    )


def verification(candidate, passed=True, installation_authorized=False):
    check = PASS if passed else FAIL
    return VerificationResult(
        structure=check,
        authenticity=check,
        compatibility=check,
        version_policy=check,
        bundle_sha256=candidate.bundle_sha256,
        manifest={
            "hardware_profile": candidate.hardware_profile,
            "release_version": candidate.release_version,
            "release_sequence": candidate.release_sequence,
            "security_epoch": candidate.security_epoch,
        },
        installation_authorized=installation_authorized,
    )


class SimulatorTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "update-state.json"
        self.known_good = version("known-good", "1.0.0", 1)
        self.candidate = version("candidate", "1.1.0", 2)

    def create(self):
        return state.UpdateStateSimulator.create(self.path, self.known_good)

    def authorize(self, simulator, candidate=None):
        selected = candidate or self.candidate
        simulator.authorize_install(
            state.SimulationInstallAuthorization(
                bundle_sha256=selected.bundle_sha256,
                approval_id="test-approval-1",
                approved=True,
            )
        )

    def reach_verified(self, simulator):
        simulator.begin_receiving(self.candidate)
        simulator.begin_verification()
        simulator.record_verification(verification(self.candidate))

    def reach_pending(self, simulator):
        self.reach_verified(simulator)
        self.authorize(simulator)
        simulator.stage_candidate()
        simulator.begin_candidate_write()
        simulator.mark_pending_boot()

    def test_deterministic_successful_normal_transition(self):
        simulator = self.create()
        self.reach_pending(simulator)
        self.assertEqual(simulator.known_good, self.known_good)
        simulator.confirm_boot_healthy()
        simulator.commit_healthy_candidate()

        self.assertEqual(simulator.state, "committed")
        self.assertEqual(simulator.known_good, self.candidate)
        self.assertEqual(
            state.VersionRef.from_dict(simulator.snapshot["previous_known_good"]),
            self.known_good,
        )
        self.assertIsNone(simulator.snapshot["candidate"])
        self.assertFalse(simulator.snapshot["simulation_install_authorized"])
        self.assertEqual(state.UpdateStateSimulator.load(self.path).snapshot, simulator.snapshot)

        second_path = Path(self.temporary.name) / "second-state.json"
        second = state.UpdateStateSimulator.create(second_path, self.known_good)
        self.reach_pending(second)
        second.confirm_boot_healthy()
        second.commit_healthy_candidate()
        self.assertEqual(self.path.read_bytes(), second_path.read_bytes())
        self.assertLess(len(self.path.read_bytes()), state.MAX_STATE_FILE_BYTES)

    def test_verified_bundle_requires_separate_authorization(self):
        simulator = self.create()
        self.reach_verified(simulator)
        before = self.path.read_bytes()
        generation = simulator.generation

        with self.assertRaises(state.StateTransitionError):
            simulator.stage_candidate()

        self.assertEqual(simulator.state, "verified")
        self.assertEqual(simulator.generation, generation)
        self.assertEqual(self.path.read_bytes(), before)
        self.authorize(simulator)
        simulator.stage_candidate()
        self.assertEqual(simulator.state, "staged")

    def test_verifier_cannot_smuggle_install_authorization(self):
        simulator = self.create()
        simulator.begin_receiving(self.candidate)
        simulator.begin_verification()
        before = self.path.read_bytes()

        with self.assertRaises(state.StateTransitionError):
            simulator.record_verification(
                verification(self.candidate, installation_authorized=True)
            )

        self.assertEqual(simulator.state, "verifying")
        self.assertEqual(self.path.read_bytes(), before)

    def test_mismatched_or_unapproved_authorization_is_rejected(self):
        simulator = self.create()
        self.reach_verified(simulator)
        generation = simulator.generation

        with self.assertRaises(state.StateTransitionError):
            simulator.authorize_install(
                state.SimulationInstallAuthorization(
                    bundle_sha256=digest("different"),
                    approval_id="wrong-bundle",
                    approved=True,
                )
            )
        with self.assertRaises(state.StateTransitionError):
            simulator.authorize_install(
                state.SimulationInstallAuthorization(
                    bundle_sha256=self.candidate.bundle_sha256,
                    approval_id="not-approved",
                    approved=False,
                )
            )

        self.assertEqual(simulator.generation, generation)
        self.assertFalse(simulator.snapshot["simulation_install_authorized"])

    def test_failed_verification_preserves_known_good_and_can_be_discarded(self):
        simulator = self.create()
        simulator.begin_receiving(self.candidate)
        simulator.begin_verification()
        simulator.record_verification(verification(self.candidate, passed=False))

        self.assertEqual(simulator.state, "failed")
        self.assertEqual(simulator.snapshot["failure"]["phase"], "verification")
        self.assertEqual(simulator.known_good, self.known_good)
        with self.assertRaises(state.StateTransitionError):
            simulator.select_known_good()

        simulator.discard_rejected_candidate()
        self.assertEqual(simulator.state, "idle")
        self.assertEqual(simulator.known_good, self.known_good)
        self.assertIsNone(simulator.snapshot["candidate"])

    def test_identity_mismatch_fails_closed(self):
        simulator = self.create()
        simulator.begin_receiving(self.candidate)
        simulator.begin_verification()
        other = version("other", "1.2.0", 3)
        simulator.record_verification(verification(other))

        self.assertEqual(simulator.state, "failed")
        self.assertEqual(simulator.snapshot["failure"]["code"], "identity_mismatch")
        self.assertEqual(simulator.known_good, self.known_good)

    def test_boot_failure_can_select_known_good_symbolically(self):
        simulator = self.create()
        self.reach_pending(simulator)
        simulator.record_boot_failure("health_timeout")
        self.assertEqual(simulator.state, "failed")
        self.assertEqual(simulator.known_good, self.known_good)

        simulator.select_known_good()
        self.assertEqual(simulator.state, "rolled_back")
        self.assertEqual(simulator.known_good, self.known_good)
        self.assertEqual(
            state.UpdateStateSimulator.load(self.path).state, "rolled_back"
        )

    def test_boot_failure_can_record_unresolved_recovery_requirement(self):
        simulator = self.create()
        self.reach_pending(simulator)
        simulator.record_boot_failure()
        simulator.require_external_recovery()

        self.assertEqual(simulator.state, "recovery_required")
        self.assertEqual(simulator.known_good, self.known_good)
        self.assertEqual(
            state.VersionRef.from_dict(simulator.snapshot["candidate"]),
            self.candidate,
        )

    def test_invalid_transition_does_not_modify_persisted_state(self):
        simulator = self.create()
        before = self.path.read_bytes()
        with self.assertRaises(state.StateTransitionError):
            simulator.mark_pending_boot()
        self.assertEqual(simulator.generation, 0)
        self.assertEqual(self.path.read_bytes(), before)

    def test_reopen_mid_sequence_and_continue(self):
        simulator = self.create()
        self.reach_verified(simulator)
        self.authorize(simulator)

        reopened = state.UpdateStateSimulator.load(self.path)
        reopened.stage_candidate()
        reopened.begin_candidate_write()
        reopened.mark_pending_boot()
        reopened.confirm_boot_healthy()
        reopened.commit_healthy_candidate()
        self.assertEqual(reopened.known_good, self.candidate)

    def test_existing_file_is_not_overwritten_by_create(self):
        self.path.write_text("preserve-me", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            state.UpdateStateSimulator.create(self.path, self.known_good)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "preserve-me")

    def test_load_rejects_noncanonical_duplicate_and_oversized_state(self):
        simulator = self.create()
        canonical = simulator.snapshot

        self.path.write_text(json.dumps(canonical, indent=2), encoding="utf-8")
        with self.assertRaises(state.StateFormatError):
            state.UpdateStateSimulator.load(self.path)

        duplicate = self.path.read_text(encoding="utf-8")
        duplicate = duplicate.replace(
            '"schema": "slot20.update-state.v1",',
            '"schema": "slot20.update-state.v1", "schema": "slot20.update-state.v1",',
            1,
        )
        self.path.write_text(duplicate, encoding="utf-8")
        with self.assertRaises(state.StateFormatError):
            state.UpdateStateSimulator.load(self.path)

        self.path.write_bytes(b"x" * (state.MAX_STATE_FILE_BYTES + 1))
        with self.assertRaises(state.StateFormatError):
            state.UpdateStateSimulator.load(self.path)

    def test_load_rejects_unknown_fields_and_inconsistent_flags(self):
        simulator = self.create()
        record = simulator.snapshot
        record["unknown"] = 1
        self.path.write_bytes(state._encode_record(record))
        with self.assertRaises(state.StateFormatError):
            state.UpdateStateSimulator.load(self.path)

        del record["unknown"]
        record["simulation_install_authorized"] = True
        self.path.write_bytes(state._encode_record(record))
        with self.assertRaises(state.StateFormatError):
            state.UpdateStateSimulator.load(self.path)

    def test_generation_exhaustion_fails_closed(self):
        simulator = self.create()
        record = simulator.snapshot
        record["generation"] = state.MAX_SAFE_INTEGER
        state._seal_record(record)
        self.path.write_bytes(state._encode_record(record))
        simulator = state.UpdateStateSimulator.load(self.path)

        with self.assertRaises(state.StateTransitionError):
            simulator.begin_receiving(self.candidate)
        self.assertEqual(simulator.state, "idle")

    def test_version_and_record_strings_are_bounded(self):
        with self.assertRaises(ValueError):
            state.VersionRef(
                hardware_profile=state.TARGET_HARDWARE_PROFILE,
                release_version="not-semver",
                release_sequence=1,
                security_epoch=1,
                bundle_sha256=digest("x"),
            )
        with self.assertRaises(ValueError):
            state.VersionRef(
                hardware_profile=state.TARGET_HARDWARE_PROFILE,
                release_version="1.0.0+" + "a" * state.MAX_RELEASE_VERSION_BYTES,
                release_sequence=1,
                security_epoch=1,
                bundle_sha256=digest("x"),
            )
        with self.assertRaises(ValueError):
            state.SimulationInstallAuthorization(
                bundle_sha256=digest("x"),
                approval_id="a" * (state.MAX_APPROVAL_ID_BYTES + 1),
                approved=True,
            )
        simulator = self.create()
        self.reach_pending(simulator)
        with self.assertRaises(ValueError):
            simulator.record_boot_failure("x" * (state.MAX_FAILURE_CODE_BYTES + 1))


if __name__ == "__main__":
    unittest.main()
