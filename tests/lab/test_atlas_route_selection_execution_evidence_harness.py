from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from lab.ops.candidates.atlas_five_node_v0.route_selection_pressure_v0 import execution_evidence_harness as harness

ROOT = Path(__file__).resolve().parents[2]
QUAL_MANIFEST_ID = "ATLAS_ROUTE_SELECTION_HARNESS_QUALIFICATION_001"


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AtlasRouteSelectionExecutionEvidenceHarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.harness_blob = git_blob(ROOT / harness.HARNESS_REL)
        cls.child_blob = git_blob(ROOT / harness.CHILD_REL)

    def qualification_root(self) -> tuple[tempfile.TemporaryDirectory, Path, harness.InputCoordinates]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "source"
        shutil.copytree(ROOT, root)
        for rel in (harness.A_REL, harness.B_REL):
            path = root / rel
            value = json.loads(path.read_text(encoding="utf-8"))
            value["manifest_id"] = QUAL_MANIFEST_ID
            for node in value["nodes"]:
                node["coordinate_ref"] = node["coordinate_ref"].replace(
                    "atlas://local/", "atlas://qualification/"
                )
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        coords = harness.InputCoordinates(
            git_blob(root / harness.A_REL), sha256(root / harness.A_REL),
            git_blob(root / harness.B_REL), sha256(root / harness.B_REL),
        )
        self.assertNotEqual(coords, harness.FROZEN_INPUTS)
        return temp, root, coords

    def run_qualification(self) -> tuple[Path, dict]:
        temp, root, coords = self.qualification_root()
        output = Path(temp.name) / "output"
        receipt = harness._execute(
            root,
            output,
            expected_harness_blob=self.harness_blob,
            expected_child_blob=self.child_blob,
            inputs=coords,
        )
        return output, receipt

    def test_q1_wrong_atlas_bytes_reject_before_execution(self) -> None:
        temp, root, coords = self.qualification_root()
        with (root / harness.ATLAS_REL).open("a", encoding="utf-8") as fh:
            fh.write("\n# substituted atlas\n")
        output = Path(temp.name) / "output"
        with self.assertRaises(harness.FrozenIdentityMismatch):
            harness._execute(
                root, output,
                expected_harness_blob=self.harness_blob,
                expected_child_blob=self.child_blob,
                inputs=coords,
            )
        self.assertFalse((output / "process_capture.json").exists())

    def test_q2_wrong_producer_or_harness_bytes_reject(self) -> None:
        temp, root, coords = self.qualification_root()
        output = Path(temp.name) / "wrong-harness"
        with self.assertRaises(harness.FrozenIdentityMismatch):
            harness._execute(
                root, output,
                expected_harness_blob="0" * 40,
                expected_child_blob=self.child_blob,
                inputs=coords,
            )
        with (root / harness.PRODUCER_REL).open("a", encoding="utf-8") as fh:
            fh.write("\n# substituted producer\n")
        output2 = Path(temp.name) / "wrong-producer"
        with self.assertRaises(harness.FrozenIdentityMismatch):
            harness._execute(
                root, output2,
                expected_harness_blob=self.harness_blob,
                expected_child_blob=self.child_blob,
                inputs=coords,
            )

    def test_q3_wrong_a_or_b_bytes_reject(self) -> None:
        for rel in (harness.A_REL, harness.B_REL):
            with self.subTest(path=str(rel)):
                temp, root, coords = self.qualification_root()
                with (root / rel).open("a", encoding="utf-8") as fh:
                    fh.write(" ")
                with self.assertRaises(harness.FrozenIdentityMismatch):
                    harness._execute(
                        root, Path(temp.name) / "output",
                        expected_harness_blob=self.harness_blob,
                        expected_child_blob=self.child_blob,
                        inputs=coords,
                    )

    def test_q4_expected_vector_without_execution_cannot_produce_valid_evidence(self) -> None:
        parameters = inspect.signature(harness.run_frozen_execution_evidence).parameters
        self.assertEqual(
            tuple(parameters),
            ("source_root", "output_root", "expected_harness_blob", "expected_child_wrapper_blob"),
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected_only = {
                "A_SELECTED_NODE_PATH": ["NODE_01", "NODE_02", "NODE_04"],
                "A_HOP_COUNT": 2,
                "B_SELECTED_NODE_PATH": ["NODE_01", "NODE_02", "NODE_04"],
                "B_HOP_COUNT": 2,
            }
            (root / "raw_observation.json").write_text(json.dumps(expected_only), encoding="utf-8")
            with self.assertRaises(harness.ReceiptInvalid):
                harness.validate_runtime_receipt(root)

    def test_q5_real_subprocess_expected_output_without_apparatus_witness_rejects(self) -> None:
        payload = {
            "raw_observation": {
                "schema_version": "atlas_route_selection_raw_observation_v0",
                "apparatus_invoked": "parse_manifest + route",
                "source_node_id": "NODE_01",
                "target_node_id": "NODE_04",
                "A_manifest_sha256": harness.A_SHA256,
                "B_manifest_sha256": harness.B_SHA256,
                "A_SELECTED_NODE_PATH": ["NODE_01", "NODE_02", "NODE_04"],
                "A_HOP_COUNT": 2,
                "B_SELECTED_NODE_PATH": ["NODE_01", "NODE_02", "NODE_04"],
                "B_HOP_COUNT": 2,
            },
            "mechanical_result": {
                "schema_version": "atlas_route_selection_mechanical_result_v0",
                "criterion": "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
                "verdict": "PASS",
            },
        }
        with tempfile.TemporaryDirectory() as temp:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", "-c", f"print({json.dumps(json.dumps(payload, sort_keys=True))})"],
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(json.loads(proc.stdout), payload)
            with self.assertRaises(harness.ApparatusWitnessInvalid):
                harness._require_witness_file(Path(temp) / "missing_witness.json")

    def test_q6_substituted_execution_tree_apparatus_rejects(self) -> None:
        temp, root, coords = self.qualification_root()
        exec_root = Path(temp.name) / "exec"
        harness._reconstruct_isolated_tree(root, exec_root)
        with (exec_root / harness.ATLAS_REL).open("a", encoding="utf-8") as fh:
            fh.write("\n# substituted after reconstruction\n")
        witness = Path(temp.name) / "witness.json"
        command = [
            sys.executable, *harness.RUNTIME_FLAGS, str(exec_root / harness.CHILD_REL),
            "--root", str(exec_root), "--witness", str(witness),
            "--atlas-blob", harness.ATLAS_BLOB,
            "--producer-blob", harness.PRODUCER_BLOB,
            "--a-blob", coords.a_blob, "--a-sha256", coords.a_sha256,
            "--b-blob", coords.b_blob, "--b-sha256", coords.b_sha256,
            "--child-blob", self.child_blob,
        ]
        proc = subprocess.run(command, cwd=exec_root, capture_output=True, check=False, env={"PATH": ""})
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse(witness.exists())

    def test_q7_nonzero_producer_exit_writes_no_result_or_receipt(self) -> None:
        temp, root, _ = self.qualification_root()
        b_path = root / harness.B_REL
        b = json.loads(b_path.read_text(encoding="utf-8"))
        b["manifest_id"] = "QUALIFICATION_MISMATCH"
        b_path.write_text(json.dumps(b, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        coords = harness.InputCoordinates(
            git_blob(root / harness.A_REL), sha256(root / harness.A_REL),
            git_blob(root / harness.B_REL), sha256(root / harness.B_REL),
        )
        output = Path(temp.name) / "output"
        with self.assertRaises(harness.ProcessExecutionInvalid):
            harness._execute(
                root, output,
                expected_harness_blob=self.harness_blob,
                expected_child_blob=self.child_blob,
                inputs=coords,
            )
        self.assertTrue((output / "process_capture.json").exists())
        self.assertFalse((output / "mechanical_result.json").exists())
        self.assertFalse((output / "runtime_receipt.json").exists())

    def test_q8_stdout_digest_mismatch_invalidates_receipt(self) -> None:
        output, _ = self.run_qualification()
        with (output / "capture_stdout.bin").open("ab") as fh:
            fh.write(b"tamper")
        with self.assertRaises(harness.ReceiptInvalid):
            harness.validate_runtime_receipt(output)

    def test_q9_reported_result_mismatch_rejects(self) -> None:
        output, _ = self.run_qualification()
        raw = json.loads((output / "raw_observation.json").read_text(encoding="utf-8"))
        wrong = harness._independent_mechanical_result(raw)
        wrong["verdict"] = "PASS" if wrong["verdict"] == "FRACTURE" else "FRACTURE"
        with self.assertRaises(harness.MechanicalResultMismatch):
            harness._validate_reported_result(raw, wrong)

    def test_q10_valid_execution_witnesses_exact_apparatus_calls(self) -> None:
        output, receipt = self.run_qualification()
        harness.validate_runtime_receipt(output)
        self.assertEqual(receipt["status"], "MECHANICALLY_ADMISSIBLE_EXECUTION_EVIDENCE")
        provenance = receipt["runtime_call_provenance"]
        self.assertEqual(provenance["parse_manifest_call_count"], 2)
        self.assertEqual(provenance["route_call_count"], 2)
        self.assertEqual(provenance["route_source_node_id"], "NODE_01")
        self.assertEqual(provenance["route_target_node_id"], "NODE_04")
        self.assertEqual(tuple(provenance["call_sequence"]), harness.EXPECTED_CALL_SEQUENCE)
        self.assertTrue((output / "raw_observation.json").exists())
        self.assertTrue((output / "mechanical_result.json").exists())
        self.assertTrue((output / "runtime_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
