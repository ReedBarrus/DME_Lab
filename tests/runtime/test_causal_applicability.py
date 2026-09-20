from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.causal_applicability_v0 import judge, realization_sha256


def _run(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


class CausalApplicabilityPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        _run(self.repo, "init")
        _run(self.repo, "config", "user.name", "DME Test")
        _run(self.repo, "config", "user.email", "dme@example.invalid")

        specimen = self.repo / "specimen.txt"
        specimen.write_text("H1\n", encoding="utf-8")
        _run(self.repo, "add", "specimen.txt")
        _run(self.repo, "commit", "-m", "H1")
        self.h1 = _run(self.repo, "rev-parse", "HEAD")

        self.realization = {
            "schema": "causal_applicability_realization_v0",
            "realization_id": "D1",
            "realization_kind": "OPERATOR_RESULT",
            "realization_basis": self.h1,
            "mechanical_result": "PASS",
            "payload_ref": "fixture://D1",
        }
        self.d1_bytes = json.dumps(
            self.realization, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.d1_sha = realization_sha256(self.realization)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _head(self) -> str:
        return _run(self.repo, "rev-parse", "HEAD")

    def _advance_h2(self) -> str:
        (self.repo / "specimen.txt").write_text("H2\n", encoding="utf-8")
        _run(self.repo, "add", "specimen.txt")
        _run(self.repo, "commit", "-m", "H2")
        return self._head()

    def _assert_d1_unchanged(self) -> None:
        now = json.dumps(
            self.realization, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(now, self.d1_bytes)
        self.assertEqual(realization_sha256(self.realization), self.d1_sha)
        self.assertEqual(self.realization["mechanical_result"], "PASS")

    def test_a1_unchanged_basis_is_applicable(self) -> None:
        j1 = judge(self.realization, self.h1, "J1")
        self.assertEqual(j1["result"], "APPLICABLE")
        self.assertEqual(j1["authority_effect"], "NONE")
        self.assertEqual(j1["admission_effect"], "NONE")
        self._assert_d1_unchanged()

    def test_a2_world_moves_realization_survives_as_stale(self) -> None:
        h2 = self._advance_h2()
        j2 = judge(self.realization, h2, "J2")
        self.assertNotEqual(h2, self.h1)
        self.assertEqual(j2["result"], "STALE")
        self._assert_d1_unchanged()

    def test_a3_seat_unaware_does_not_make_world_unchanged(self) -> None:
        seat_state = {"observed_repo_head": self.h1, "consumed_event": "E1"}
        before = copy.deepcopy(seat_state)
        h2 = self._advance_h2()

        j2 = judge(self.realization, h2, "J2-SEAT-UNAWARE")

        self.assertEqual(seat_state, before)
        self.assertEqual(seat_state["observed_repo_head"], self.h1)
        self.assertEqual(j2["comparison_basis"], h2)
        self.assertEqual(j2["result"], "STALE")
        self._assert_d1_unchanged()

    def test_a4_event_consumption_changes_seat_not_realization(self) -> None:
        h2 = self._advance_h2()
        seat_state = {"observed_repo_head": self.h1, "consumed_event": "E1"}

        seat_state["observed_repo_head"] = h2
        seat_state["consumed_event"] = "E2"

        self.assertEqual(seat_state["observed_repo_head"], h2)
        self._assert_d1_unchanged()

    def test_a5_rejudgment_creates_new_judgment_not_new_realization(self) -> None:
        h2 = self._advance_h2()
        j1 = judge(self.realization, self.h1, "J1")
        j2 = judge(self.realization, h2, "J2")

        self.assertNotEqual(j1["judgment_id"], j2["judgment_id"])
        self.assertEqual(j1["realization_sha256"], self.d1_sha)
        self.assertEqual(j2["realization_sha256"], self.d1_sha)
        self.assertEqual(j1["result"], "APPLICABLE")
        self.assertEqual(j2["result"], "STALE")
        self._assert_d1_unchanged()

    def test_a6_same_tree_different_commit_is_stale_in_v0(self) -> None:
        self._advance_h2()
        (self.repo / "specimen.txt").write_text("H1\n", encoding="utf-8")
        _run(self.repo, "add", "specimen.txt")
        _run(self.repo, "commit", "-m", "H3 restore H1 tree content")
        h3 = self._head()

        tree_h1 = _run(self.repo, "rev-parse", f"{self.h1}^{{tree}}")
        tree_h3 = _run(self.repo, "rev-parse", f"{h3}^{{tree}}")
        self.assertEqual(tree_h1, tree_h3)
        self.assertNotEqual(self.h1, h3)

        j3 = judge(self.realization, h3, "J3-SAME-TREE")
        self.assertEqual(j3["result"], "STALE")
        self._assert_d1_unchanged()

    def test_a7_exact_basis_can_become_applicable_again(self) -> None:
        h2 = self._advance_h2()
        stale = judge(self.realization, h2, "J2")
        self.assertEqual(stale["result"], "STALE")

        _run(self.repo, "reset", "--hard", self.h1)
        self.assertEqual(self._head(), self.h1)

        restored = judge(self.realization, self._head(), "J3")
        self.assertEqual(restored["result"], "APPLICABLE")
        self.assertEqual(restored["realization_sha256"], stale["realization_sha256"])
        self._assert_d1_unchanged()


if __name__ == "__main__":
    unittest.main()
