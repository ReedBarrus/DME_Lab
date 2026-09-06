from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.capture import make_repo_snapshot
from src.runtime.repo_transition_pressure import (
    filesystem_transition,
    git_history_between,
    git_observation_transition,
    git_visible_filesystem_out_of_scope,
    make_git_ingest_envelope,
    metadata_only_pressure,
    multi_source_ledger_handshake,
    path_correspondence,
    repeated_identity_pressure,
    same_bytes_later_committed,
    status_path,
)
from src.runtime.repo_provenance_pressure import json_domain_result


class RepoTransitionPressureTest(unittest.TestCase):
    def test_repeated_observation_identity_exposes_state_and_occurrence_split(self) -> None:
        result = repeated_identity_pressure()

        self.assertTrue(result["same_snapshot_id"])
        self.assertTrue(result["same_envelope_identity"])
        self.assertTrue(result["different_observation_interval"])

    def test_metadata_only_change_can_shift_snapshot_id_without_changed_paths(self) -> None:
        result = metadata_only_pressure()

        self.assertTrue(result["snapshot_id_changed"])
        self.assertEqual(result["changed_paths_count"], 0)
        self.assertEqual(result["unchanged_paths"], ["same-bytes.txt"])

    def test_filesystem_excluded_scope_is_not_treated_as_path_absence(self) -> None:
        s0 = {
            "snapshot_id": "s0",
            "entries": [{"path": "visible.txt", "sha256": "a", "size_bytes": 1}],
            "capture_errors": [],
            "observation_started_at": "t0",
            "observation_finished_at": "t1",
        }
        s1 = {
            "snapshot_id": "s1",
            "entries": [{"path": "visible.txt", "sha256": "a", "size_bytes": 1}],
            "capture_errors": [],
            "observation_started_at": "t2",
            "observation_finished_at": "t3",
        }
        fs_delta = filesystem_transition(s0, s1)
        git_delta = {
            "status_removed": ["?? traces/generated.json"],
            "status_added": [],
            "status_current": [],
        }
        correspondence = path_correspondence(fs_delta, git_delta, [], s0, s1)

        out_of_scope = git_visible_filesystem_out_of_scope(correspondence)

        self.assertEqual(out_of_scope[0]["path"], "traces/generated.json")
        self.assertFalse(next(row for row in correspondence if row["path"] == "traces/generated.json")["filesystem"]["in_scope"])

    def test_path_surfaces_correlate_without_asserting_equivalence(self) -> None:
        s0 = {
            "snapshot_id": "s0",
            "entries": [{"path": "a.txt", "sha256": "same", "size_bytes": 1}],
            "capture_errors": [],
            "observation_started_at": "t0",
            "observation_finished_at": "t1",
        }
        s1 = {
            "snapshot_id": "s1",
            "entries": [{"path": "a.txt", "sha256": "same", "size_bytes": 1}],
            "capture_errors": [],
            "observation_started_at": "t2",
            "observation_finished_at": "t3",
        }
        history = [{"sha": "abc", "changed_paths": [{"status": "A", "path": "a.txt"}]}]
        correspondence = path_correspondence(filesystem_transition(s0, s1), {"status_removed": [], "status_added": [], "status_current": []}, history, s0, s1)

        row = correspondence[0]

        self.assertEqual(row["path"], "a.txt")
        self.assertFalse(row["filesystem"]["content_changed"])
        self.assertEqual(row["git_historical"]["commit_touches"], ["abc"])
        self.assertNotIn("same_change", row)
        self.assertEqual(len(same_bytes_later_committed(correspondence)), 1)

    def test_git_candidate_envelope_is_json_domain_valid(self) -> None:
        git_state = {
            "observation_id": "git-state-v0:t",
            "observer": "git_state",
            "observer_version": "git_state_v0",
            "observed_at": "t",
            "root_identity": {"kind": "repository_working_tree", "name": ""},
            "head_sha": "abc",
            "branch": "main",
            "status_porcelain": [],
            "capture_errors": [],
        }

        envelope = make_git_ingest_envelope(git_state)

        self.assertTrue(json_domain_result(envelope)["valid"])
        self.assertEqual(envelope["signal"]["payload"]["observer"], "git_state")

    def test_filesystem_and_git_envelopes_coexist_in_temporary_ledger(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            snapshot = make_repo_snapshot(root)
        git_state = {
            "observation_id": "git-state-v0:t",
            "observer": "git_state",
            "observer_version": "git_state_v0",
            "observed_at": "t",
            "root_identity": {"kind": "repository_working_tree", "name": ""},
            "head_sha": "abc",
            "branch": "main",
            "status_porcelain": [],
            "capture_errors": [],
        }

        result = multi_source_ledger_handshake(snapshot, git_state)

        self.assertTrue(result["integrity_ok"])
        self.assertEqual(result["replayed_payload_observers"], ["repo_snapshot", "git_state"])
        self.assertTrue(all(record["schema_shadow_validation"]["valid"] for record in result["records"]))
        self.assertEqual([record["commit_index"] for record in result["records"]], [1, 2])

    def test_append_order_remains_distinct_from_observation_time(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            snapshot = make_repo_snapshot(root)
        git_state = {
            "observation_id": "git-state-v0:earlier",
            "observer": "git_state",
            "observer_version": "git_state_v0",
            "observed_at": "earlier-than-filesystem",
            "root_identity": {"kind": "repository_working_tree", "name": ""},
            "head_sha": "abc",
            "branch": "main",
            "status_porcelain": [],
            "capture_errors": [],
        }

        result = multi_source_ledger_handshake(snapshot, git_state)

        self.assertEqual(result["append_order"], ["filesystem", "git"])
        self.assertEqual(result["append_order_claim"], "experimental handling order, not source chronology")
        self.assertEqual([record["commit_index"] for record in result["records"]], [1, 2])

    def test_historical_git_evidence_is_labeled_retrospective(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._git(root, ["init"])
            self._git(root, ["config", "user.email", "test@example.invalid"])
            self._git(root, ["config", "user.name", "DME Test"])
            (root / "a.txt").write_text("one", encoding="utf-8")
            self._git(root, ["add", "a.txt"])
            self._git(root, ["commit", "-m", "base"])
            base = self._git(root, ["rev-parse", "HEAD"])
            (root / "a.txt").write_text("two", encoding="utf-8")
            self._git(root, ["commit", "-am", "change"])
            head = self._git(root, ["rev-parse", "HEAD"])

            history = git_history_between(root, base, head)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["evidence_basis"], "retrospective_git_history")
        self.assertEqual(history[0]["changed_paths"], [{"status": "M", "path": "a.txt"}])

    def test_git_observation_delta_keeps_status_entries_mechanical(self) -> None:
        g0 = {"head_sha": "a", "branch": "main", "observed_at": "t0", "status_porcelain": ["?? a.txt"], "capture_errors": []}
        g1 = {"head_sha": "b", "branch": "main", "observed_at": "t1", "status_porcelain": [], "capture_errors": []}

        delta = git_observation_transition(g0, g1)

        self.assertTrue(delta["head_changed"])
        self.assertEqual(delta["status_removed"], ["?? a.txt"])
        self.assertEqual(delta["status_current"], [])

    def test_status_path_handles_preserved_and_stripped_porcelain_forms(self) -> None:
        self.assertEqual(status_path(" M docs/contracts/capture.md"), "docs/contracts/capture.md")
        self.assertEqual(status_path("M PROJECT_STATE.md"), "PROJECT_STATE.md")
        self.assertEqual(status_path("?? traces/generated.json"), "traces/generated.json")

    @staticmethod
    def _git(root: Path, args: list[str]) -> str:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()


if __name__ == "__main__":
    unittest.main()
