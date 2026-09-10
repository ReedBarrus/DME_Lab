from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.runtime.cockpit_projection_adapter_repressure import SURVIVES, run


class CockpitProjectionAdapterRepressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.result = run(
            cls.root,
            source_ref="HEAD",
            freshness_ref="HEAD",
        )
        cls.scenarios = {item["id"]: item for item in cls.result["scenarios"]}

    def test_R1_original_P8_wound_survives(self) -> None:
        scenario = self.scenarios["R1"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(scenario["observed"]["node"]["resolution_history"], [])
        self.assertEqual(len(scenario["observed"]["history_residue"]), 2)

    def test_R2_nearby_history_heading_survives(self) -> None:
        scenario = self.scenarios["R2"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertNotIn("Prior resolutions", scenario["mutation"])
        self.assertEqual(len(scenario["observed"]["history_residue"]), 2)

    def test_R3_healthy_history_control_survives(self) -> None:
        scenario = self.scenarios["R3"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(scenario["diagnostics"], [])
        self.assertEqual(scenario["observed"]["projection_status"], "complete")

    def test_R4_loose_prose_does_not_trigger_detector(self) -> None:
        scenario = self.scenarios["R4"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(scenario["diagnostics"], [])

    def test_R5_original_P11_duplicate_survives(self) -> None:
        scenario = self.scenarios["R5"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(len(scenario["observed"]["nodes"]), 2)
        self.assertIn(
            "duplicate_pressure_id",
            [item["kind"] for item in scenario["diagnostics"]],
        )

    def test_R6_identical_headings_have_distinct_lines(self) -> None:
        scenario = self.scenarios["R6"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(len(set(scenario["observed"]["source_lines"])), 2)

    def test_R7_duplicate_target_remains_one_ambiguous_relation(self) -> None:
        scenario = self.scenarios["R7"]
        relations = scenario["observed"]["matching_relations"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(len(relations), 1)
        self.assertEqual(
            relations[0]["target_resolution"],
            {"status": "ambiguous", "candidate_count": 2},
        )

    def test_R8_duplicate_detection_does_not_require_relation(self) -> None:
        scenario = self.scenarios["R8"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(scenario["observed"]["relation_count"], 0)
        self.assertIn(
            "duplicate_pressure_id",
            [item["kind"] for item in scenario["diagnostics"]],
        )

    def test_R9_unique_control_has_no_ambiguity_metadata(self) -> None:
        scenario = self.scenarios["R9"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(scenario["diagnostics"], [])
        self.assertIsNone(
            scenario["observed"]["relations"][0]["target_resolution"]
        )

    def test_R10_combined_wounds_remain_independent(self) -> None:
        scenario = self.scenarios["R10"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(scenario["observed"]["duplicate_diagnostic_count"], 1)
        self.assertEqual(
            scenario["observed"]["unsupported_history_diagnostic_count"], 1
        )

    def test_R11_current_repository_smoke_survives(self) -> None:
        scenario = self.scenarios["R11"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(scenario["diagnostics"], [])
        self.assertEqual(scenario["observed"]["projection_status"], "complete")
        self.assertEqual(scenario["observed"]["freshness"]["status"], "current")

    def test_R12_three_way_duplicate_survives(self) -> None:
        scenario = self.scenarios["R12"]
        self.assertEqual(scenario["classification"], SURVIVES)
        self.assertEqual(len(scenario["observed"]["nodes"]), 3)
        self.assertEqual(
            scenario["observed"]["relations"][0]["target_resolution"],
            {"status": "ambiguous", "candidate_count": 3},
        )

    def test_all_named_scenarios_survive_without_other_classifications(self) -> None:
        self.assertEqual(
            self.result["classification_counts"],
            {
                "SURVIVES": 12,
                "CONTRACT_VIOLATION": 0,
                "REGRESSION": 0,
                "CONTRACT_AMBIGUITY": 0,
                "BASIS_INSUFFICIENT": 0,
            },
        )
        self.assertTrue(self.result["adjudication"]["ui_authorized_next"])
        self.assertFalse(self.result["adjudication"]["adapter_changed"])

    def test_committed_trace_preserves_observed_classifications(self) -> None:
        trace_path = (
            self.root / "traces/cockpit_projection_adapter_repressure_v0.json"
        )
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        self.assertEqual(
            trace["classification_counts"],
            self.result["classification_counts"],
        )
        self.assertEqual(
            [(item["id"], item["classification"]) for item in trace["scenarios"]],
            [
                (item["id"], item["classification"])
                for item in self.result["scenarios"]
            ],
        )
        traced_smoke = next(item for item in trace["scenarios"] if item["id"] == "R11")
        self.assertEqual(
            traced_smoke["observed"]["source_commit"],
            "6f65398e9e1b01952126e2a2456974356231df75",
        )


if __name__ == "__main__":
    unittest.main()
