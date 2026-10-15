import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import compare_manifest_sample as compare  # noqa: E402


class CompareManifestSampleTests(unittest.TestCase):
    @staticmethod
    def make_tree(root, count):
        files = []
        hashes = {}
        for index in range(count):
            relative = f"files/file-{index:02d}.bin"
            content = f"sample-{index}".encode("ascii")
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            files.append({"path": relative, "kind": "regular"})
            hashes[relative] = hashlib.sha256(content).hexdigest()
        return {"files": files, "file_sha256": hashes}

    def test_evenly_spaced_includes_first_and_last(self):
        self.assertEqual(compare.evenly_spaced(list(range(10)), 4), [0, 3, 6, 9])
        self.assertEqual(compare.evenly_spaced(list(range(5)), 1), [2])

    def test_clean_sample_matches(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self.make_tree(root, 10)
            result = compare.compare_sample(manifest, root, sample_count=4)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["eligible_regular_files"], 10)
        self.assertEqual(result["sampled_files"], 4)
        self.assertEqual(result["matched_files"], 4)
        self.assertEqual(result["issues"], [])

    def test_missing_and_mismatch_fail_without_content_in_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self.make_tree(root, 3)
            (root / "files" / "file-00.bin").unlink()
            secret_content = b"do-not-print-this"
            (root / "files" / "file-02.bin").write_bytes(secret_content)
            result = compare.compare_sample(manifest, root, sample_count=3)

        rendered = json.dumps(result)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["missing_files"], 1)
        self.assertEqual(result["mismatched_files"], 1)
        self.assertNotIn(secret_content.decode("ascii"), rendered)
        self.assertNotIn("file-00.bin", rendered)
        self.assertNotIn("file-02.bin", rendered)

    def test_insufficient_candidates_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = compare.compare_sample(self.make_tree(root, 2), root, sample_count=3)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["sampled_files"], 2)
        self.assertIn({"type": "insufficient_sample"}, result["issues"])

    def test_unsafe_manifest_path_fails_without_reading_outside_root(self):
        digest = hashlib.sha256(b"outside").hexdigest()
        manifest = {
            "files": [{"path": "../outside.bin", "kind": "regular"}],
            "file_sha256": {"../outside.bin": digest},
        }
        with tempfile.TemporaryDirectory() as temp:
            result = compare.compare_sample(manifest, temp, sample_count=1)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["eligible_regular_files"], 0)
        self.assertEqual(result["invalid_manifest_entries"], 1)
        self.assertNotIn("outside.bin", json.dumps(result))

    def test_symlink_target_is_rejected_without_hashing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self.make_tree(root, 1)
            target = root / "files" / "file-00.bin"
            target.unlink()
            outside = root / "outside.bin"
            outside.write_bytes(b"do-not-read-this")
            try:
                target.symlink_to(outside)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")
            with mock.patch.object(
                compare, "sha256_file", side_effect=AssertionError("symlink was hashed")
            ):
                result = compare.compare_sample(manifest, root, sample_count=1)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["invalid_targets"], 1)
        self.assertIn({"type": "symlink_target"}, result["issues"])

    def test_oversized_target_is_rejected_without_hashing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self.make_tree(root, 1)
            with (
                mock.patch.object(compare, "MAX_HASH_BYTES", 1),
                mock.patch.object(
                    compare, "sha256_file", side_effect=AssertionError("large file was hashed")
                ),
            ):
                result = compare.compare_sample(manifest, root, sample_count=1)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["invalid_targets"], 1)
        self.assertIn({"type": "oversized_target"}, result["issues"])

    def test_omitted_issue_count_includes_all_invalid_manifest_entries(self):
        digest = hashlib.sha256(b"outside").hexdigest()
        files = [
            {"path": f"../outside-{index}.bin", "kind": "regular"}
            for index in range(compare.MAX_REPORTED_ISSUES + 3)
        ]
        hashes = {record["path"]: digest for record in files}
        with tempfile.TemporaryDirectory() as temp:
            result = compare.compare_sample(
                {"files": files, "file_sha256": hashes}, temp, sample_count=1
            )

        self.assertEqual(result["invalid_manifest_entries"], compare.MAX_REPORTED_ISSUES + 3)
        # Three invalid-entry reports and the insufficient-sample report exceed
        # the eight-entry output cap.
        self.assertEqual(result["issues_omitted"], 4)

    def test_cli_returns_nonzero_for_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self.make_tree(root, 1)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (root / "files" / "file-00.bin").write_bytes(b"changed")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                return_code = compare.main([str(manifest_path), str(root), "--sample-count", "1"])

        self.assertEqual(return_code, 1)
        self.assertEqual(json.loads(output.getvalue())["mismatched_files"], 1)

    def test_cli_rejects_oversized_manifest_before_reading(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "manifest.json"
            manifest_path.write_text("{}", encoding="utf-8")
            output = io.StringIO()
            with (
                mock.patch.object(compare, "MAX_MANIFEST_BYTES", 1),
                mock.patch.object(
                    Path, "read_text", side_effect=AssertionError("manifest was read")
                ),
                contextlib.redirect_stdout(output),
            ):
                return_code = compare.main([str(manifest_path), temp])

        result = json.loads(output.getvalue())
        self.assertEqual(return_code, 1)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "ValueError")


if __name__ == "__main__":
    unittest.main()
