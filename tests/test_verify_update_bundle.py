import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import verify_update_bundle as bundle  # noqa: E402


@dataclass
class BuiltBundle:
    data: bytes
    manifest: dict
    manifest_bytes: bytes
    payload_offset: int
    signature_offset: int


class SyntheticBundleFactory:
    def __init__(self):
        self.private_key = Ed25519PrivateKey.generate()
        public_raw = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.key_id = hashlib.sha256(public_raw).hexdigest()

    @staticmethod
    def canonical(value):
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def build(
        self,
        components=None,
        mutate=None,
        canonical=True,
        header_changes=None,
        signing_key=None,
    ):
        if components is None:
            components = [("kernel", "kernel", b"synthetic-kernel")]
        manifest_components = [
            {
                "id": component_id,
                "type": component_type,
                "length": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
            for component_id, component_type, payload in components
        ]
        manifest = {
            "schema": bundle.SCHEMA,
            "hardware_profile": bundle.TARGET_HARDWARE_PROFILE,
            "release_version": "1.2.3",
            "release_sequence": 5,
            "security_epoch": 1,
            "signing_key_id": self.key_id,
            "components": manifest_components,
        }
        if mutate is not None:
            mutate(manifest)
        if canonical:
            manifest_bytes = self.canonical(manifest)
        else:
            manifest_bytes = json.dumps(manifest, sort_keys=False).encode("utf-8")
        payload = b"".join(item[2] for item in components)
        if isinstance(manifest.get("components"), list):
            component_count = len(manifest["components"])
        else:
            component_count = len(components)
        return self.assemble(
            manifest,
            manifest_bytes,
            payload,
            component_count,
            header_changes=header_changes,
            signing_key=signing_key,
        )

    def assemble(
        self,
        manifest,
        manifest_bytes,
        payload,
        component_count,
        header_changes=None,
        signing_key=None,
    ):
        fields = {
            "magic": bundle.MAGIC,
            "format_version": bundle.FORMAT_VERSION,
            "header_length": bundle.HEADER_SIZE,
            "manifest_length": len(manifest_bytes),
            "component_count": component_count,
            "signature_length": bundle.SIGNATURE_SIZE,
            "payload_length": len(payload),
            "flags": 0,
        }
        fields.update(header_changes or {})
        header = bundle.HEADER_STRUCT.pack(
            fields["magic"],
            fields["format_version"],
            fields["header_length"],
            fields["manifest_length"],
            fields["component_count"],
            fields["signature_length"],
            fields["payload_length"],
            fields["flags"],
        )
        key = signing_key or self.private_key
        signature = key.sign(bundle.SIGNATURE_DOMAIN + header + manifest_bytes)
        payload_offset = len(header) + len(manifest_bytes)
        signature_offset = payload_offset + len(payload)
        return BuiltBundle(
            data=header + manifest_bytes + payload + signature,
            manifest=manifest,
            manifest_bytes=manifest_bytes,
            payload_offset=payload_offset,
            signature_offset=signature_offset,
        )

    def raw_manifest(self, manifest_bytes, payload=b"x", component_count=1):
        return self.assemble(
            {}, manifest_bytes, payload, component_count, signing_key=self.private_key
        )

    def trust_store(self, status="active", profiles=None, minimum=0, maximum=None):
        if profiles is None:
            profiles = {bundle.TARGET_HARDWARE_PROFILE}
        if maximum is None:
            maximum = bundle.MAX_SAFE_INTEGER
        return bundle.TrustStore(
            [
                bundle.TrustedKeyRecord(
                    self.private_key.public_key(),
                    frozenset(profiles),
                    status=status,
                    minimum_security_epoch=minimum,
                    maximum_security_epoch=maximum,
                )
            ]
        )


class VerifyUpdateBundleTests(unittest.TestCase):
    def setUp(self):
        self.factory = SyntheticBundleFactory()

    def policy(
        self,
        built,
        current_epoch=1,
        current_sequence=4,
        minimum_epoch=1,
        catalog_digest=None,
        include_release=True,
        allow_reinstall=False,
        allow_downgrade=False,
        recovery_ready=False,
    ):
        digest = hashlib.sha256(built.data).hexdigest()
        if catalog_digest is None:
            catalog_digest = digest
        epoch = built.manifest.get("security_epoch", 1)
        sequence = built.manifest.get("release_sequence", 5)
        if type(epoch) is not int or not 0 <= epoch <= bundle.MAX_SAFE_INTEGER:
            epoch = 1
        if type(sequence) is not int or not 0 <= sequence <= bundle.MAX_SAFE_INTEGER:
            sequence = 5
        release = (bundle.TARGET_HARDWARE_PROFILE, epoch, sequence)
        catalog = {release: catalog_digest} if include_release else {}
        return bundle.VersionPolicy(
            hardware_profile=bundle.TARGET_HARDWARE_PROFILE,
            current_security_epoch=current_epoch,
            current_release_sequence=current_sequence,
            current_bundle_sha256="0" * 64,
            minimum_security_epoch=minimum_epoch,
            supported_releases=catalog,
            allow_reinstall=allow_reinstall,
            allow_downgrade=allow_downgrade,
            recovery_ready=recovery_ready,
        )

    def verify(self, built, trust_store=None, policy=None):
        if trust_store is None:
            trust_store = self.factory.trust_store()
        if policy is None:
            policy = self.policy(built)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic.s20b"
            path.write_bytes(built.data)
            return bundle.verify_bundle(path, trust_store, policy)

    def assert_structure_failure(self, built, code=None):
        result = self.verify(built)
        self.assertEqual(result.structure.status, "fail")
        if code is not None:
            self.assertEqual(result.structure.code, code)
        self.assertEqual(result.authenticity.status, "not_checked")
        self.assertFalse(result.installation_authorized)

    def test_valid_upgrade_reports_separate_layers(self):
        built = self.factory.build(
            components=[
                ("kernel", "kernel", b"synthetic-kernel"),
                ("rootfs", "rootfs", b"synthetic-rootfs"),
            ]
        )
        result = self.verify(built)

        self.assertTrue(result.host_verification_passed)
        self.assertEqual(result.structure.code, "structure_valid")
        self.assertEqual(result.authenticity.code, "signature_and_hashes_valid")
        self.assertEqual(result.compatibility.code, "hardware_profile_match")
        self.assertEqual(result.version_policy.code, "upgrade_authorized")
        self.assertEqual(result.bundle_sha256, hashlib.sha256(built.data).hexdigest())
        self.assertEqual(result.manifest["release_version"], "1.2.3")
        self.assertFalse(result.installation_authorized)

    def test_synthetic_build_is_deterministic_for_fixed_inputs_and_key(self):
        first = self.factory.build()
        second = self.factory.build()
        self.assertEqual(first.data, second.data)

    def test_component_hashing_uses_chunked_path(self):
        built = self.factory.build(
            components=[("rootfs", "rootfs", b"x" * 10_003)]
        )
        with mock.patch.object(bundle, "READ_CHUNK_SIZE", 7):
            result = self.verify(built)
        self.assertTrue(result.host_verification_passed)

    def test_non_regular_bundle_is_rejected(self):
        built = self.factory.build()
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target.s20b"
            link = Path(temp) / "link.s20b"
            target.write_bytes(built.data)
            try:
                link.symlink_to(target)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")
            result = bundle.verify_bundle(
                link, self.factory.trust_store(), self.policy(built)
            )
        self.assertEqual(result.structure.code, "bundle_not_regular_file")

    def test_total_file_cap_is_enforced_before_parsing(self):
        built = self.factory.build()
        with mock.patch.object(bundle, "MAX_BUNDLE_BYTES", len(built.data) - 1):
            result = self.verify(built)
        self.assertEqual(result.structure.code, "bundle_size_limit")
        self.assertEqual(result.authenticity.status, "not_checked")

    def test_header_rejections(self):
        cases = {
            "bad_magic": {"magic": b"BADMAGIC"},
            "unsupported_format_version": {"format_version": 2},
            "bad_header_length": {"header_length": 31},
            "manifest_length_limit": {"manifest_length": 1},
            "component_count_zero": {"component_count": 0},
            "component_count_large": {"component_count": bundle.MAX_COMPONENTS + 1},
            "bad_signature_length": {"signature_length": 63},
            "payload_length_zero": {"payload_length": 0},
            "payload_length_large": {"payload_length": bundle.MAX_PAYLOAD_BYTES + 1},
            "unknown_flags": {"flags": 1},
        }
        for name, changes in cases.items():
            with self.subTest(name=name):
                built = self.factory.build(header_changes=changes)
                self.assert_structure_failure(built)

    def test_truncation_at_each_section_and_trailing_data_are_rejected(self):
        built = self.factory.build()
        positions = [
            0,
            bundle.HEADER_SIZE - 1,
            bundle.HEADER_SIZE,
            built.payload_offset - 1,
            built.signature_offset - 1,
            len(built.data) - 1,
        ]
        for position in positions:
            with self.subTest(position=position):
                truncated = copy.copy(built)
                truncated.data = built.data[:position]
                self.assert_structure_failure(truncated)

        trailing = copy.copy(built)
        trailing.data = built.data + b"x"
        self.assert_structure_failure(trailing, "trailing_data")

    def test_invalid_utf8_duplicate_names_and_noncanonical_json_are_rejected(self):
        invalid_utf8 = self.factory.raw_manifest(b"\xff{}")
        self.assert_structure_failure(invalid_utf8, "invalid_manifest_json")

        duplicate = self.factory.raw_manifest(
            b'{"schema":"slot20.update-bundle.v1","schema":"duplicate"}'
        )
        self.assert_structure_failure(duplicate, "duplicate_json_name")

        noncanonical = self.factory.build(canonical=False)
        self.assert_structure_failure(noncanonical, "noncanonical_manifest")

    def test_manifest_field_and_number_rejections(self):
        mutators = {
            "missing": lambda value: value.pop("schema"),
            "extra": lambda value: value.update({"unexpected": 1}),
            "wrong_components_type": lambda value: value.update({"components": {}}),
            "float": lambda value: value.update({"release_sequence": 1.0}),
            "negative": lambda value: value.update({"release_sequence": -1}),
            "too_large": lambda value: value.update(
                {"release_sequence": bundle.MAX_SAFE_INTEGER + 1}
            ),
            "unicode_profile": lambda value: value.update({"hardware_profile": "camerá"}),
        }
        for name, mutate in mutators.items():
            with self.subTest(name=name):
                built = self.factory.build(mutate=mutate)
                self.assert_structure_failure(built)

    def test_semver_rejections(self):
        for version in ("1", "01.2.3", "1.02.3", "1.2.03", "1.2.3-01", "v1.2.3"):
            with self.subTest(version=version):
                built = self.factory.build(
                    mutate=lambda value, version=version: value.update(
                        {"release_version": version}
                    )
                )
                self.assert_structure_failure(built, "invalid_release_version")

    def test_component_metadata_rejections(self):
        two = [
            ("kernel", "kernel", b"k"),
            ("rootfs", "rootfs", b"r"),
        ]

        def duplicate_id(value):
            value["components"][1]["id"] = value["components"][0]["id"]

        def duplicate_type(value):
            value["components"][1]["type"] = value["components"][0]["type"]

        cases = (
            self.factory.build(mutate=lambda value: value["components"][0].update({"id": "../x"})),
            self.factory.build(mutate=lambda value: value["components"][0].update({"type": "Kernel"})),
            self.factory.build(mutate=lambda value: value["components"][0].update({"length": 0})),
            self.factory.build(mutate=lambda value: value["components"][0].update({"length": bundle.MAX_COMPONENT_BYTES + 1})),
            self.factory.build(mutate=lambda value: value["components"][0].update({"sha256": "A" * 64})),
            self.factory.build(mutate=lambda value: value["components"][0].update({"extra": 1})),
            self.factory.build(components=two, mutate=duplicate_id),
            self.factory.build(components=two, mutate=duplicate_type),
            self.factory.build(header_changes={"component_count": 2}),
            self.factory.build(mutate=lambda value: value["components"][0].update({"length": 1})),
        )
        for index, built in enumerate(cases):
            with self.subTest(case=index):
                self.assert_structure_failure(built)

    def test_wrong_hardware_profile_is_separate_compatibility_failure(self):
        built = self.factory.build(
            mutate=lambda value: value.update({"hardware_profile": "reolink.other"})
        )
        result = self.verify(built, policy=self.policy(built, include_release=False))
        self.assertTrue(result.structure.passed)
        self.assertEqual(result.compatibility.code, "hardware_profile_mismatch")
        self.assertEqual(result.authenticity.status, "not_checked")

    def test_unknown_inactive_scope_and_epoch_keys_are_rejected(self):
        built = self.factory.build()
        stores = {
            "unknown": bundle.TrustStore([]),
            "retired": self.factory.trust_store(status="retired"),
            "revoked": self.factory.trust_store(status="revoked"),
            "scope": self.factory.trust_store(profiles={"reolink.other"}),
            "epoch": self.factory.trust_store(minimum=2),
        }
        for name, store in stores.items():
            with self.subTest(name=name):
                result = self.verify(built, trust_store=store)
                self.assertTrue(result.structure.passed)
                self.assertTrue(result.compatibility.passed)
                self.assertEqual(result.authenticity.status, "fail")
                self.assertIsNone(result.manifest)

    def test_key_rotation_overlap_accepts_a_second_pretrusted_key(self):
        next_factory = SyntheticBundleFactory()
        built = next_factory.build()
        store = bundle.TrustStore(
            [
                bundle.TrustedKeyRecord(
                    self.factory.private_key.public_key(),
                    frozenset({bundle.TARGET_HARDWARE_PROFILE}),
                ),
                bundle.TrustedKeyRecord(
                    next_factory.private_key.public_key(),
                    frozenset({bundle.TARGET_HARDWARE_PROFILE}),
                ),
            ]
        )
        result = self.verify(built, trust_store=store, policy=self.policy(built))
        self.assertTrue(result.host_verification_passed)

    def test_signature_manifest_and_payload_tampering_are_rejected(self):
        built = self.factory.build()

        bad_signature = copy.copy(built)
        data = bytearray(built.data)
        data[-1] ^= 1
        bad_signature.data = bytes(data)
        self.assertEqual(self.verify(bad_signature).authenticity.code, "invalid_signature")

        bad_manifest = copy.copy(built)
        data = bytearray(built.data)
        start = bundle.HEADER_SIZE
        end = start + len(built.manifest_bytes)
        changed = built.manifest_bytes.replace(b'"1.2.3"', b'"1.2.4"')
        self.assertEqual(len(changed), len(built.manifest_bytes))
        data[start:end] = changed
        bad_manifest.data = bytes(data)
        self.assertEqual(self.verify(bad_manifest).authenticity.code, "invalid_signature")

        bad_payload = copy.copy(built)
        data = bytearray(built.data)
        data[built.payload_offset] ^= 1
        bad_payload.data = bytes(data)
        self.assertEqual(
            self.verify(bad_payload).authenticity.code, "component_hash_mismatch"
        )

    def test_signature_from_another_key_is_rejected(self):
        other = Ed25519PrivateKey.generate()
        built = self.factory.build(signing_key=other)
        result = self.verify(built)
        self.assertEqual(result.authenticity.code, "invalid_signature")

    def test_release_catalog_is_mandatory_and_digest_bound(self):
        built = self.factory.build()
        missing = self.verify(built, policy=self.policy(built, include_release=False))
        self.assertEqual(missing.version_policy.code, "release_not_in_trusted_catalog")
        self.assertTrue(missing.authenticity.passed)

        mismatched = self.verify(
            built, policy=self.policy(built, catalog_digest="f" * 64)
        )
        self.assertEqual(
            mismatched.version_policy.code, "release_catalog_digest_mismatch"
        )

    def test_security_floor_and_cross_epoch_downgrade_are_rejected(self):
        built = self.factory.build()
        below_floor = self.verify(
            built,
            policy=self.policy(
                built, current_epoch=2, current_sequence=1, minimum_epoch=2
            ),
        )
        self.assertEqual(below_floor.version_policy.code, "below_security_floor")

        cross_epoch = self.verify(
            built,
            policy=self.policy(
                built, current_epoch=2, current_sequence=1, minimum_epoch=1
            ),
        )
        self.assertEqual(
            cross_epoch.version_policy.code, "cross_epoch_downgrade_forbidden"
        )

    def test_reinstall_requires_explicit_authorization(self):
        built = self.factory.build()
        denied = self.verify(
            built, policy=self.policy(built, current_sequence=5)
        )
        self.assertEqual(
            denied.version_policy.code, "reinstall_requires_explicit_authorization"
        )

        allowed = self.verify(
            built,
            policy=self.policy(built, current_sequence=5, allow_reinstall=True),
        )
        self.assertEqual(allowed.version_policy.code, "reinstall_authorized")
        self.assertTrue(allowed.host_verification_passed)

    def test_downgrade_requires_intent_and_recovery(self):
        built = self.factory.build()
        denied = self.verify(
            built, policy=self.policy(built, current_sequence=6)
        )
        self.assertEqual(
            denied.version_policy.code, "downgrade_requires_explicit_authorization"
        )

        no_recovery = self.verify(
            built,
            policy=self.policy(built, current_sequence=6, allow_downgrade=True),
        )
        self.assertEqual(
            no_recovery.version_policy.code, "downgrade_requires_recovery_ready"
        )

        allowed = self.verify(
            built,
            policy=self.policy(
                built,
                current_sequence=6,
                allow_downgrade=True,
                recovery_ready=True,
            ),
        )
        self.assertEqual(allowed.version_policy.code, "downgrade_authorized")
        self.assertTrue(allowed.host_verification_passed)

    def test_higher_security_epoch_is_upgrade(self):
        built = self.factory.build(
            mutate=lambda value: value.update(
                {"security_epoch": 2, "release_sequence": 0}
            )
        )
        result = self.verify(
            built,
            policy=self.policy(
                built, current_epoch=1, current_sequence=99, minimum_epoch=1
            ),
        )
        self.assertEqual(result.version_policy.code, "upgrade_authorized")
        self.assertTrue(result.host_verification_passed)

    def test_policy_and_trust_inputs_are_validated(self):
        with self.assertRaises(ValueError):
            bundle.VersionPolicy(
                hardware_profile="reolink.other",
                current_security_epoch=1,
                current_release_sequence=1,
                current_bundle_sha256="0" * 64,
                minimum_security_epoch=1,
                supported_releases={},
            )
        with self.assertRaises(ValueError):
            bundle.TrustStore(
                [
                    bundle.TrustedKeyRecord(
                        self.factory.private_key.public_key(),
                        frozenset({bundle.TARGET_HARDWARE_PROFILE}),
                    ),
                    bundle.TrustedKeyRecord(
                        self.factory.private_key.public_key(),
                        frozenset({bundle.TARGET_HARDWARE_PROFILE}),
                    ),
                ]
            )


if __name__ == "__main__":
    unittest.main()
