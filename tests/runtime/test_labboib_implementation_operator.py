from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.labboib_implementation_operator_v0 import (
    AUTHORITY_PATH,
    ImplementationHarness,
    ImplementationOperatorError,
    load_authority,
)


def _run(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class LabboibImplementationOperatorPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_tmp = tempfile.TemporaryDirectory()
        self.state_tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.repo_tmp.name)
        self.state = Path(self.state_tmp.name)

        _run(self.repo, "init")
        _run(self.repo, "config", "user.name", "DME Test")
        _run(self.repo, "config", "user.email", "dme@example.invalid")

        (self.repo / "foo.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.repo / "bar.py").write_text('EXTRA = "original"\n', encoding="utf-8")
        _run(self.repo, "add", "foo.py", "bar.py")
        _run(self.repo, "commit", "-m", "H1 implementation basis")
        self.h1 = _run(self.repo, "rev-parse", "HEAD")

        self.harness = ImplementationHarness(self.repo, self.state)

    def tearDown(self) -> None:
        self.state_tmp.cleanup()
        self.repo_tmp.cleanup()

    def request(
        self,
        request_id: str,
        *,
        allowed_paths: list[str] | None = None,
        requested_effect: str = "Set VALUE from 1 to 2 with no other requested change.",
    ) -> dict:
        return {
            "schema": "implementation_request_v0",
            "request_id": request_id,
            "seat_id": "LABBOIB",
            "repository": "fixture://implementation-repo",
            "basis_commit": self.h1,
            "allowed_paths": list(allowed_paths or ["foo.py"]),
            "requested_effect": requested_effect,
            "qualification_contract": {
                "exact_file_sha256": {
                    "foo.py": _sha256_text("VALUE = 2\n"),
                },
                "declared_check_ids": ["PY_COMPILE_FOO"],
            },
            "operator_id": "ISOLATED_IMPLEMENTATION_FIXTURE",
            "authority_ref": AUTHORITY_PATH,
        }

    def assert_canonical_foo_untouched(self) -> None:
        self.assertEqual(
            (self.repo / "foo.py").read_text(encoding="utf-8"),
            "VALUE = 1\n",
        )

    def test_i1_exact_bounded_realization(self) -> None:
        result = self.harness.execute_request(
            self.request("R-I1"),
            fixture_mode="EXACT",
        )
        d1 = result["realization"]

        self.assertEqual(result["status"], "REALIZED")
        self.assertTrue(result["operator_invoked"])
        self.assertEqual(d1["touched_paths"], ["foo.py"])
        self.assertEqual(d1["scope_status"], "VALID")
        self.assertEqual(d1["effect_contract_status"], "VALID")
        self.assertEqual(d1["mechanical_result"], "PASS")
        self.assertEqual(result["applicability"]["result"], "APPLICABLE")
        self.assertEqual(result["admission"], "NOT_ADMITTED_NO_CONSEQUENCE_AUTHORITY")
        self.assertEqual(d1["commit_effect"], "NONE")
        self.assertEqual(d1["merge_effect"], "NONE")
        self.assertEqual(d1["scientific_standing_effect"], "NONE")
        self.assertGreater(d1["diff_bytes"], 0)
        self.assert_canonical_foo_untouched()

        worktree = self.state / d1["worktree_ref"]
        self.assertTrue(worktree.exists())
        self.assertEqual((worktree / "foo.py").read_text(), "VALUE = 2\n")

    def test_i2_out_of_scope_touch_retained_but_invalid(self) -> None:
        result = self.harness.execute_request(
            self.request("R-I2"),
            fixture_mode="OUT_OF_SCOPE",
        )
        d1 = result["realization"]

        self.assertIn("foo.py", d1["touched_paths"])
        self.assertIn("bar.py", d1["touched_paths"])
        self.assertEqual(d1["scope_status"], "INVALID")
        self.assertEqual(d1["mechanical_result"], "PASS")
        self.assertEqual(result["admission"], "NOT_ADMITTED_SCOPE")
        self.assert_canonical_foo_untouched()

    def test_i3_useful_but_wrong_fails_effect_contract(self) -> None:
        result = self.harness.execute_request(
            self.request("R-I3"),
            fixture_mode="USEFUL_BUT_WRONG",
        )
        d1 = result["realization"]

        self.assertEqual(d1["touched_paths"], ["foo.py"])
        self.assertEqual(d1["scope_status"], "VALID")
        self.assertEqual(d1["effect_contract_status"], "INVALID")
        self.assertEqual(d1["mechanical_result"], "PASS")
        self.assertEqual(
            result["admission"],
            "NOT_ADMITTED_EFFECT_CONTRACT",
        )
        self.assert_canonical_foo_untouched()

    def test_i4_partial_failure_retains_dirty_realization(self) -> None:
        result = self.harness.execute_request(
            self.request("R-I4"),
            fixture_mode="PARTIAL_FAILURE",
        )
        d1 = result["realization"]

        self.assertGreater(d1["diff_bytes"], 0)
        self.assertEqual(d1["process_exit"], 17)
        self.assertEqual(d1["mechanical_result"], "FAIL")
        self.assertEqual(result["admission"], "NOT_ADMITTED_MECHANICAL")
        self.assertTrue((self.state / d1["worktree_ref"]).exists())
        self.assert_canonical_foo_untouched()

    def test_i5_world_moves_realization_becomes_stale(self) -> None:
        def move_world() -> None:
            (self.repo / "world.txt").write_text("H2\n", encoding="utf-8")
            _run(self.repo, "add", "world.txt")
            _run(self.repo, "commit", "-m", "H2 external environment event")

        result = self.harness.execute_request(
            self.request("R-I5"),
            fixture_mode="EXACT",
            environment_intervention=move_world,
        )
        d1 = result["realization"]

        self.assertEqual(d1["realization_basis"], self.h1)
        self.assertNotEqual(result["canonical_head_at_return"], self.h1)
        self.assertEqual(result["applicability"]["result"], "STALE")
        self.assertEqual(result["admission"], "NOT_ADMITTED_STALE")
        self.assertEqual(d1["effect_contract_status"], "VALID")
        self.assertEqual(d1["mechanical_result"], "PASS")

    def test_i6_claimed_success_without_delta_fails_mechanically(self) -> None:
        result = self.harness.execute_request(
            self.request("R-I6"),
            fixture_mode="CLAIM_ONLY",
        )
        d1 = result["realization"]

        self.assertEqual(d1["operator_claimed_status"], "DONE")
        self.assertEqual(d1["diff_bytes"], 0)
        self.assertEqual(d1["effect_contract_status"], "INVALID")
        self.assertEqual(d1["mechanical_result"], "FAIL")
        self.assertEqual(result["admission"], "NOT_ADMITTED_EFFECT_CONTRACT")
        self.assert_canonical_foo_untouched()

    def test_i7_mechanical_check_pass_does_not_override_scope_failure(self) -> None:
        result = self.harness.execute_request(
            self.request("R-I7"),
            fixture_mode="OUT_OF_SCOPE",
        )
        d1 = result["realization"]

        self.assertTrue(d1["mechanical_checks"])
        self.assertTrue(all(c["result"] == "PASS" for c in d1["mechanical_checks"]))
        self.assertEqual(d1["mechanical_result"], "PASS")
        self.assertEqual(d1["scope_status"], "INVALID")
        self.assertEqual(result["admission"], "NOT_ADMITTED_SCOPE")

    def test_i8_authority_absent_prevents_invocation_and_worktree(self) -> None:
        authority = copy.deepcopy(load_authority())
        authority["invocation_authorized"] = False

        result = self.harness.execute_request(
            self.request("R-I8"),
            fixture_mode="EXACT",
            authority_override=authority,
        )

        self.assertEqual(result["status"], "AUTHORITY_REQUIRED")
        self.assertFalse(result["operator_invoked"])
        self.assertFalse(result["worktree_created"])
        self.assertIsNone(result["realization"])
        self.assertEqual(list((self.state / "worktrees").iterdir()), [])
        self.assert_canonical_foo_untouched()

    def test_i9_duplicate_request_reuses_realization_not_operator(self) -> None:
        request = self.request("R-I9")
        first = self.harness.execute_request(request, fixture_mode="EXACT")
        second = self.harness.execute_request(request, fixture_mode="EXACT")

        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertTrue(first["operator_invoked"])
        self.assertFalse(second["operator_invoked"])
        self.assertEqual(
            first["realization"]["realization_id"],
            second["realization"]["realization_id"],
        )
        self.assertEqual(
            first["realization"]["diff_sha256"],
            second["realization"]["diff_sha256"],
        )
        self.assertEqual(len(list((self.state / "worktrees").iterdir())), 1)

        changed = copy.deepcopy(request)
        changed["requested_effect"] = "Different request bytes"
        with self.assertRaises(ImplementationOperatorError):
            self.harness.execute_request(changed, fixture_mode="EXACT")


if __name__ == "__main__":
    unittest.main()
