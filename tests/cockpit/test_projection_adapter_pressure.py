from __future__ import annotations

from pathlib import Path
import unittest

from src.runtime.cockpit_projection_adapter_pressure import (
    CONTRACT_AMBIGUITY,
    CONTRACT_VIOLATION,
    SURVIVES,
    run,
)


class CockpitProjectionAdapterPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run(Path(__file__).resolve().parents[2])
        cls.scenarios = {item["id"]: item for item in cls.result["scenarios"]}

    def test_healthy_baseline_is_retained(self) -> None:
        baseline = self.result["baseline"]
        self.assertRegex(baseline["source_commit"], r"^[0-9a-f]{40}$")
        self.assertGreater(baseline["pressure_node_count"], 0)
        self.assertGreater(baseline["constraint_count"], 0)

    def test_P1_missing_required_source_survives(self) -> None:
        self.assertEqual(self.scenarios["P1"]["classification"], SURVIVES)

    def test_P2_unknown_standing_survives(self) -> None:
        self.assertEqual(self.scenarios["P2"]["classification"], SURVIVES)

    def test_P3_broken_reference_survives(self) -> None:
        self.assertEqual(self.scenarios["P3"]["classification"], SURVIVES)

    def test_P4_source_conflict_survives(self) -> None:
        self.assertEqual(self.scenarios["P4"]["classification"], SURVIVES)

    def test_P5_relation_looking_prose_survives(self) -> None:
        self.assertEqual(self.scenarios["P5"]["classification"], SURVIVES)

    def test_P6_malformed_pressure_structure_survives(self) -> None:
        self.assertEqual(self.scenarios["P6"]["classification"], SURVIVES)

    def test_P7_malformed_constraint_record_survives(self) -> None:
        self.assertEqual(self.scenarios["P7"]["classification"], SURVIVES)

    def test_P8_resolution_history_wound_is_now_visible_regression_residue(self) -> None:
        self.assertEqual(
            self.scenarios["P8"]["classification"], SURVIVES
        )
        self.assertEqual(self.scenarios["P8"]["observed"]["damaged_history"], [])
        self.assertIn(
            "unsupported_structure",
            [item["kind"] for item in self.scenarios["P8"]["diagnostics"]],
        )

    def test_P9_stale_projection_basis_survives(self) -> None:
        self.assertEqual(self.scenarios["P9"]["classification"], SURVIVES)

    def test_P10_projection_document_containment_survives(self) -> None:
        self.assertEqual(self.scenarios["P10"]["classification"], SURVIVES)

    def test_P11_duplicate_pressure_id_is_contract_ambiguity(self) -> None:
        self.assertEqual(
            self.scenarios["P11"]["classification"], CONTRACT_AMBIGUITY
        )
        self.assertIn(
            "duplicate_pressure_id",
            [item["kind"] for item in self.scenarios["P11"]["diagnostics"]],
        )

    def test_pressure_completion_does_not_require_all_semantic_survivals(self) -> None:
        counts = self.result["classification_counts"]
        self.assertEqual(counts[SURVIVES], 10)
        self.assertEqual(counts[CONTRACT_VIOLATION], 0)
        self.assertEqual(counts[CONTRACT_AMBIGUITY], 1)
        self.assertFalse(self.result["adjudication"]["adapter_remediated"])


if __name__ == "__main__":
    unittest.main()
