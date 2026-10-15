#!/usr/bin/env python3
"""Compare a deterministic sample of manifest hashes with an extracted tree.

This helper is deliberately read-only. It selects regular files that have a
SHA-256 entry, spreads the requested sample across their sorted paths, and
hashes only those files. It never reads through symlinks or prints file data.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys


DEFAULT_SAMPLE_COUNT = 32
MAX_REPORTED_ISSUES = 8
MAX_MANIFEST_BYTES = 64 * 1024 * 1024
MAX_HASH_BYTES = 250_000_000
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def evenly_spaced(items, count):
    """Return *count* deterministic entries spanning an already-sorted list."""
    if count < 1:
        raise ValueError("sample count must be positive")
    if len(items) < count:
        raise ValueError("not enough eligible files for requested sample")
    if count == 1:
        return [items[(len(items) - 1) // 2]]
    return [items[index * (len(items) - 1) // (count - 1)] for index in range(count)]


def safe_manifest_parts(path):
    """Convert a canonical relative POSIX path into safe host path parts."""
    if not isinstance(path, str) or not path or "\0" in path or "\\" in path:
        raise ValueError("unsafe manifest path")
    pure = PurePosixPath(path)
    if pure.is_absolute() or pure.as_posix() != path:
        raise ValueError("unsafe manifest path")
    if any(part in ("", ".", "..") or ":" in part for part in pure.parts):
        raise ValueError("unsafe manifest path")
    return pure.parts


def manifest_candidates(manifest):
    """Return sorted ``(path, expected_hash)`` candidates and bounded issues."""
    files = manifest.get("files") if isinstance(manifest, dict) else None
    hashes = manifest.get("file_sha256") if isinstance(manifest, dict) else None
    if not isinstance(files, list) or not isinstance(hashes, dict):
        raise ValueError("manifest must contain files and file_sha256 collections")

    candidates = {}
    issues = []
    issue_count = 0
    for record in files:
        if not isinstance(record, dict) or record.get("kind") != "regular":
            continue
        path = record.get("path")
        expected = hashes.get(path) if isinstance(path, str) else None
        if expected is None:
            continue
        try:
            safe_manifest_parts(path)
            if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
                raise ValueError("invalid SHA-256")
            if path in candidates:
                raise ValueError("duplicate regular-file path")
        except ValueError as error:
            issue_count += 1
            if len(issues) < MAX_REPORTED_ISSUES:
                issues.append({"type": "invalid_manifest_entry", "detail": str(error)})
            continue
        candidates[path] = expected.lower()

    return sorted(candidates.items()), issues, issue_count


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path):
    """Load a bounded regular JSON file without following a manifest symlink."""
    manifest_stat = path.lstat()
    if not stat.S_ISREG(manifest_stat.st_mode):
        raise ValueError("manifest must be a regular file")
    if manifest_stat.st_size > MAX_MANIFEST_BYTES:
        raise ValueError("manifest exceeds size limit")
    return json.loads(path.read_text(encoding="utf-8"))


def compare_sample(manifest, extracted_root, sample_count=DEFAULT_SAMPLE_COUNT):
    """Compare one deterministic sample and return a concise result mapping."""
    if sample_count < 1:
        raise ValueError("sample count must be positive")

    candidates, issues, manifest_issue_count = manifest_candidates(manifest)
    result = {
        "status": "failed",
        "eligible_regular_files": len(candidates),
        "requested_samples": sample_count,
        "sampled_files": 0,
        "matched_files": 0,
        "missing_files": 0,
        "mismatched_files": 0,
        "invalid_targets": 0,
        "invalid_manifest_entries": manifest_issue_count,
        "issues": issues,
        "_total_issues": manifest_issue_count,
    }

    root = Path(extracted_root)
    try:
        root = root.resolve(strict=True)
    except (OSError, RuntimeError):
        root = None
    if root is None or not root.is_dir():
        result["invalid_targets"] = 1
        _add_issue(result, {"type": "invalid_extracted_root"})
        _finish_issues(result)
        return result

    insufficient = len(candidates) < sample_count
    selected_count = min(sample_count, len(candidates))
    selected = evenly_spaced(candidates, selected_count) if selected_count else []
    result["sampled_files"] = len(selected)
    if insufficient:
        _add_issue(result, {"type": "insufficient_sample"})

    for manifest_path, expected in selected:
        target = root.joinpath(*safe_manifest_parts(manifest_path))
        try:
            target.lstat()
        except FileNotFoundError:
            result["missing_files"] += 1
            _add_issue(result, {"type": "missing"})
            continue
        except (OSError, RuntimeError):
            result["invalid_targets"] += 1
            _add_issue(result, {"type": "unreadable_target"})
            continue

        if _contains_symlink(root, target):
            result["invalid_targets"] += 1
            _add_issue(result, {"type": "symlink_target"})
            continue

        try:
            resolved = target.resolve(strict=True)
            target_stat = resolved.stat()
        except (OSError, RuntimeError):
            result["invalid_targets"] += 1
            _add_issue(result, {"type": "unreadable_target"})
            continue
        if not resolved.is_relative_to(root) or not stat.S_ISREG(target_stat.st_mode):
            result["invalid_targets"] += 1
            _add_issue(result, {"type": "non_regular_target"})
            continue
        if target_stat.st_size > MAX_HASH_BYTES:
            result["invalid_targets"] += 1
            _add_issue(result, {"type": "oversized_target"})
            continue

        try:
            actual = sha256_file(resolved)
        except OSError:
            result["invalid_targets"] += 1
            _add_issue(result, {"type": "unreadable_target"})
            continue
        if actual != expected:
            result["mismatched_files"] += 1
            _add_issue(result, {"type": "hash_mismatch"})
        else:
            result["matched_files"] += 1

    failed = (
        insufficient
        or manifest_issue_count
        or result["missing_files"]
        or result["mismatched_files"]
        or result["invalid_targets"]
    )
    result["status"] = "failed" if failed else "ok"
    _finish_issues(result)
    return result


def _contains_symlink(root, target):
    relative = target.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _add_issue(result, issue):
    result.setdefault("_total_issues", len(result["issues"]))
    result["_total_issues"] += 1
    if len(result["issues"]) < MAX_REPORTED_ISSUES:
        result["issues"].append(issue)


def _finish_issues(result):
    total = result.pop("_total_issues", len(result["issues"]))
    result["issues_omitted"] = max(0, total - len(result["issues"]))


def positive_int(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("extracted_root", type=Path)
    parser.add_argument("--sample-count", type=positive_int, default=DEFAULT_SAMPLE_COUNT)
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
        result = compare_sample(manifest, args.extracted_root, args.sample_count)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        result = {
            "status": "error",
            "error": "unable to load or compare inputs",
            "error_type": type(error).__name__,
        }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
