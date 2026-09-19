from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from lab.ops.candidates.handling_001 import runtime_evidence_harness as harness


ROOT = Path(__file__).parents[2]
QUAL_A = "HANDLING_001-HARNESS-QUAL-A"
QUAL_B = "HANDLING_001-HARNESS-QUAL-B"
QUAL_B_CLAIM = {
    "claim_event_id": "HANDLING_001-HARNESS-QUAL-B-CLAIM",
    "event_type": "CLAIM_FOR_HANDLING",
    "work_record_id": harness.CONTROLLED_RECORD_ID,
}


class Handling001RuntimeEvidenceHarnessTest(unittest.TestCase):
    def produce(self, *, cell_id: str, claims: tuple[dict[str, str], ...]):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        output = Path(temp.name) / "raw.json"
        artifact = harness._produce_qualification_raw_observation(
            ROOT,
            qualification_cell_id=cell_id,
            claim_events=claims,
            output_path=output,
        )
        self.assertTrue(output.exists())
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), artifact)
        return artifact

    def copied_frozen_root(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for rel in (
            harness.ADDRESSING_PATH,
            harness.HANDLING_PATH,
            harness.ROLE_REGISTRY_PATH,
            harness.CONTROLLED_WORK_PATH,
        ):
            destination = root / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, destination)
        return root

    def test_q1_a_input_actual_invocation_produces_raw_a_observation(self) -> None:
        artifact = self.produce(cell_id=QUAL_A, claims=())
        self.assertTrue(artifact["WORK_EXISTS"])
        self.assertTrue(artifact["WORK_AVAILABLE_TO_ROLE"])
        self.assertFalse(artifact["WORK_CLAIMED_FOR_HANDLING"])
        self.assertFalse(artifact["AUTHORITY_STATE_CHANGED"])
        self.assertFalse(artifact["CONSEQUENCE_PATH_INVOKED"])
        self.assertEqual(
            tuple(artifact["_execution_provenance"]["invoked_functions"]),
            harness.INVOKED_FUNCTIONS,
        )

    def test_q2_b_input_actual_invocation_produces_raw_b_observation(self) -> None:
        artifact = self.produce(cell_id=QUAL_B, claims=(QUAL_B_CLAIM,))
        self.assertTrue(artifact["WORK_EXISTS"])
        self.assertTrue(artifact["WORK_AVAILABLE_TO_ROLE"])
        self.assertTrue(artifact["WORK_CLAIMED_FOR_HANDLING"])
        self.assertFalse(artifact["AUTHORITY_STATE_CHANGED"])
        self.assertFalse(artifact["CONSEQUENCE_PATH_INVOKED"])

    def test_q3_expected_pass_vector_is_not_an_input(self) -> None:
        parameters = inspect.signature(harness.produce_recovery_raw_observation).parameters
        self.assertEqual(tuple(parameters), ("repo_root", "cell_label", "claim_events"))
        self.assertNotIn("expected_observation", parameters)
        self.assertNotIn("expected_vector", parameters)

    def test_q4_raw_observation_without_invocation_provenance_is_invalid(self) -> None:
        raw = {
            "WORK_EXISTS": True,
            "WORK_AVAILABLE_TO_ROLE": True,
            "WORK_CLAIMED_FOR_HANDLING": False,
            "AUTHORITY_STATE_CHANGED": False,
            "CONSEQUENCE_PATH_INVOKED": False,
        }
        with self.assertRaises(harness.RawObservationInvalid):
            harness.validate_raw_observation(raw)

    def test_q5_wrong_apparatus_identity_is_rejected(self) -> None:
        root = self.copied_frozen_root()
        with (root / harness.HANDLING_PATH).open("a", encoding="utf-8") as fh:
            fh.write("\n# wrong identity\n")
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaises(harness.FrozenIdentityMismatch):
                harness._produce_qualification_raw_observation(
                    root,
                    qualification_cell_id=QUAL_A,
                    claim_events=(),
                    output_path=Path(out) / "raw.json",
                )

    def test_q6_wrong_controlled_specimen_identity_is_rejected(self) -> None:
        root = self.copied_frozen_root()
        specimen_path = root / harness.CONTROLLED_WORK_PATH
        specimen = json.loads(specimen_path.read_text(encoding="utf-8"))
        specimen["record_id"] = "WRONG"
        specimen_path.write_text(json.dumps(specimen), encoding="utf-8")
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaises(harness.FrozenIdentityMismatch):
                harness._produce_qualification_raw_observation(
                    root,
                    qualification_cell_id=QUAL_A,
                    claim_events=(),
                    output_path=Path(out) / "raw.json",
                )

    def test_q7_wrong_recovery_b_claim_identity_or_bytes_is_rejected_before_invocation(self) -> None:
        wrong = {
            "claim_event_id": "WRONG",
            "event_type": "CLAIM_FOR_HANDLING",
            "work_record_id": harness.CONTROLLED_RECORD_ID,
        }
        recovery_output = ROOT / harness.RECOVERY_B_OUTPUT_PATH
        self.assertFalse(recovery_output.exists())
        with self.assertRaises(harness.FrozenCellInputMismatch):
            harness.produce_recovery_raw_observation(
                ROOT,
                cell_label="B",
                claim_events=(wrong,),
            )
        self.assertFalse(recovery_output.exists())

    def test_q8_output_schema_is_observation_plus_minimal_execution_provenance(self) -> None:
        artifact = self.produce(cell_id=QUAL_A, claims=())
        self.assertEqual(
            set(artifact),
            set(harness.OBSERVATION_FIELDS) | {"_execution_provenance"},
        )
        self.assertEqual(
            set(artifact["_execution_provenance"]),
            set(harness.PROVENANCE_FIELDS),
        )


if __name__ == "__main__":
    unittest.main()
