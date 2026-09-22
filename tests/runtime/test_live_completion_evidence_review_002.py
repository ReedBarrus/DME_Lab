from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import lane_lifecycle_disposition_v0 as lifecycle
import live_completion_controller_adapter_v1 as adapter

FIX = ROOT / "fixtures" / "live_completion_evidence_v1"


class LiveCompletionEvidenceReview002(unittest.TestCase):
    def _controller(self):
        registry = adapter._load(ROOT, FIX / "PRODUCER_QUALIFICATION_REGISTRY_002.json")
        return lifecycle.LifecycleController(
            adapter._composed_controller_registry(ROOT, registry),
            adapter._composed_basis_catalog(ROOT),
        )

    def test_evidence_only_mutation_breaks_bridge(self):
        path = FIX / "RAW_WORK_EVIDENCE.json"
        original = path.read_text(encoding="utf-8")
        obj = json.loads(original)
        obj["final_artifacts"][0]["blob"] = "0" * 40
        try:
            path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(adapter.BridgeInvalid, "PIN_MISMATCH:evidence"):
                adapter.evaluate_authoritative_controller(ROOT)
        finally:
            path.write_text(original, encoding="utf-8")

    def test_exact_controller_accepts_self_consistent_unit_renaming_after_adapter(self):
        clean = adapter.evaluate_authoritative_controller(ROOT)
        data = copy.deepcopy(clean["controller_input"])
        renamed = "sha256:" + "f" * 64
        for key in ("claim", "binding", "envelope"):
            data[key]["bounded_unit_id"] = renamed
        data["criterion"]["required_bounded_unit_id"] = renamed
        data["receipt"]["bounded_unit_id"] = renamed
        data["receipt"]["receipt_id"] = "review-receipt:" + renamed
        data["criterion"]["required_receipt_id"] = data["receipt"]["receipt_id"]

        result = self._controller().evaluate_branch(data)
        self.assertTrue(result["admissible"], result)
        self.assertEqual(result["selected_branch"], "COMPLETE")

    def test_exact_controller_accepts_self_consistent_outcome_relabeling_after_adapter(self):
        clean = adapter.evaluate_authoritative_controller(ROOT)
        data = copy.deepcopy(clean["controller_input"])
        data["criterion"]["required_outcome"] = "ARBITRARY_MATCHED_OUTCOME"
        data["receipt"]["outcome"] = "ARBITRARY_MATCHED_OUTCOME"

        result = self._controller().evaluate_branch(data)
        self.assertTrue(result["admissible"], result)
        self.assertEqual(result["selected_branch"], "COMPLETE")

    def test_controller_historical_claim_is_adapter_projection_not_source_claim(self):
        clean = adapter.evaluate_authoritative_controller(ROOT)
        frozen = adapter._load(ROOT, FIX / "FROZEN_LANE_A_SPECIMEN.json")
        source = json.loads(
            adapter._git(ROOT, "show", f"{frozen['lane_a_head']}:{frozen['lane_a_claim_path']}")
        )
        projected = clean["controller_result"]["historical_claim"]

        self.assertNotEqual(projected, source)
        self.assertIn("bounded_unit_id", projected)
        self.assertIn("envelope_id", projected)
        self.assertNotIn("bounded_unit_id", source)
        self.assertNotIn("envelope_id", source)

    def test_clean_adapter_path_still_reaches_admissible_without_execution(self):
        clean = adapter.evaluate_authoritative_controller(ROOT)
        self.assertTrue(clean["controller_result"]["admissible"])
        self.assertFalse(clean["transition_executed"])
        self.assertEqual(clean["live_lane_mutation"], "NONE")


if __name__ == "__main__":
    unittest.main()
