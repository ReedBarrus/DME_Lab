from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.capture import compare_snapshots, make_repo_snapshot, observe_git_state
from src.capture import repo_snapshot
from src.ledger import JsonlLedger, validate_ledger_record
from src.runtime.repo_provenance_pressure import json_domain_result, make_snapshot_ingest_envelope


def entry_facts(snapshot: dict[str, object]) -> list[tuple[str, str]]:
    return [
        (entry["path"], entry["sha256"])
        for entry in snapshot["entries"]  # type: ignore[index]
    ]


class RepoSnapshotTest(unittest.TestCase):
    def test_unchanged_directory_repeats_structural_file_hash_facts(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            (root / "b.txt").write_text("bravo", encoding="utf-8")

            first = make_repo_snapshot(root)
            second = make_repo_snapshot(root)

        self.assertEqual(entry_facts(first), entry_facts(second))

    def test_added_removed_and_changed_files_are_detected(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "kept.txt").write_text("same", encoding="utf-8")
            (root / "removed.txt").write_text("remove", encoding="utf-8")
            (root / "changed.txt").write_text("before", encoding="utf-8")
            before = make_repo_snapshot(root)

            (root / "added.txt").write_text("add", encoding="utf-8")
            (root / "removed.txt").unlink()
            (root / "changed.txt").write_text("after", encoding="utf-8")
            after = make_repo_snapshot(root)

        comparison = compare_snapshots(before, after)
        self.assertEqual([item["path"] for item in comparison["added_paths"]], ["added.txt"])
        self.assertEqual([item["path"] for item in comparison["removed_paths"]], ["removed.txt"])
        self.assertEqual([item["path"] for item in comparison["changed_paths"]], ["changed.txt"])
        self.assertIn("kept.txt", comparison["unchanged_paths"])

    def test_excluded_paths_remain_outside_observation_scope(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "visible.txt").write_text("visible", encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "hidden").write_text("git", encoding="utf-8")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "hidden.pyc").write_bytes(b"cache")
            (root / "traces").mkdir()
            (root / "traces" / "hidden.json").write_text("trace", encoding="utf-8")

            snapshot = make_repo_snapshot(root)

        paths = [entry["path"] for entry in snapshot["entries"]]
        self.assertEqual(paths, ["visible.txt"])
        self.assertEqual(snapshot["scope"]["excluded_dirs"], [".git", "__pycache__", "traces"])

    def test_capture_error_remains_visible_when_hashing_fails(self) -> None:
        original = repo_snapshot._hash_file

        def failing_hash(path: Path, relative: str, errors: list[dict[str, str]]) -> str | None:
            errors.append({"path": relative, "stage": "hash", "error": "synthetic_disappeared"})
            return None

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "unstable.txt").write_text("unstable", encoding="utf-8")
            try:
                repo_snapshot._hash_file = failing_hash  # type: ignore[assignment]
                snapshot = make_repo_snapshot(root)
            finally:
                repo_snapshot._hash_file = original  # type: ignore[assignment]

        self.assertEqual(snapshot["entries"], [])
        self.assertEqual(snapshot["capture_errors"][0]["error"], "synthetic_disappeared")

    def test_entries_are_deterministically_ordered(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "z.txt").write_text("z", encoding="utf-8")
            (root / "a.txt").write_text("a", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "m.txt").write_text("m", encoding="utf-8")

            snapshot = make_repo_snapshot(root)

        self.assertEqual([entry["path"] for entry in snapshot["entries"]], ["a.txt", "nested/m.txt", "z.txt"])

    def test_observation_start_and_finish_times_remain_separate(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.txt").write_text("alpha", encoding="utf-8")

            snapshot = make_repo_snapshot(root)

        self.assertIn("observation_started_at", snapshot)
        self.assertIn("observation_finished_at", snapshot)
        self.assertNotEqual(snapshot["observation_started_at"], "")
        self.assertNotEqual(snapshot["observation_finished_at"], "")

    def test_git_and_filesystem_observations_are_separate_structures(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.txt").write_text("alpha", encoding="utf-8")

            snapshot = make_repo_snapshot(root)
            git_state = observe_git_state(root)

        self.assertEqual(snapshot["observer"], "repo_snapshot")
        self.assertEqual(git_state["observer"], "git_state")
        self.assertIn("entries", snapshot)
        self.assertIn("status_porcelain", git_state)
        self.assertTrue(git_state["capture_errors"])

    def test_candidate_live_envelope_is_shadow_validated_not_enforced(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            snapshot = make_repo_snapshot(root)
            envelope = make_snapshot_ingest_envelope(snapshot)

            self.assertTrue(json_domain_result(envelope)["valid"])
            ledger = JsonlLedger(root / "experimental.jsonl")
            record = ledger.append(envelope)
            validation = validate_ledger_record(record)
            verification = ledger.verify()

            self.assertTrue(validation.valid)
            self.assertTrue(verification.ok)


if __name__ == "__main__":
    unittest.main()
