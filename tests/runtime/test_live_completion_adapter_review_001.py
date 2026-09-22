from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import live_completion_controller_adapter_v2 as adapter

CONTRACT = ROOT / "fixtures" / "live_completion_adapter_v0" / "PROJECTION_CONTRACT_001.json"


class LiveCompletionAdapterReview001(unittest.TestCase):
    def test_clean_qualified_path_still_admissible_without_execution(self):
        out = adapter.evaluate(ROOT)
        self.assertTrue(out["controller_result"]["admissible"])
        self.assertEqual(out["controller_result"]["selected_branch"], "COMPLETE")
        self.assertFalse(out["transition_executed"])
        self.assertEqual(out["lane_mutation"], "NONE")

    def test_contract_only_outcome_mapping_mutation_reaches_controller(self):
        original = CONTRACT.read_text(encoding="utf-8")
        obj = json.loads(original)
        obj["projection_rules"]["p06_outcome_mapping"]["SATISFIED"] = "ARBITRARY_MATCHED_OUTCOME"
        try:
            CONTRACT.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            out = adapter.evaluate(ROOT)
            self.assertTrue(out["controller_result"]["admissible"], out)
            self.assertEqual(
                out["controller_input_projection"]["criterion"]["required_outcome"],
                "ARBITRARY_MATCHED_OUTCOME",
            )
            self.assertEqual(
                out["controller_input_projection"]["receipt"]["outcome"],
                "ARBITRARY_MATCHED_OUTCOME",
            )
        finally:
            CONTRACT.write_text(original, encoding="utf-8")

    def test_contract_only_receipt_prefix_mutation_reaches_controller(self):
        original = CONTRACT.read_text(encoding="utf-8")
        obj = json.loads(original)
        obj["projection_rules"]["receipt_id_prefix"] = "arbitrary-review-prefix:"
        try:
            CONTRACT.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            out = adapter.evaluate(ROOT)
            self.assertTrue(out["controller_result"]["admissible"], out)
            self.assertTrue(
                out["controller_input_projection"]["receipt"]["receipt_id"].startswith(
                    "arbitrary-review-prefix:"
                )
            )
        finally:
            CONTRACT.write_text(original, encoding="utf-8")

    def test_frozen_coordinate_metadata_is_not_enforced_by_adapter(self):
        original = CONTRACT.read_text(encoding="utf-8")
        obj = json.loads(original)
        obj["frozen_coordinates"]["lane_a"] = "0" * 40
        obj["frozen_coordinates"]["lane_b"] = "f" * 40
        try:
            CONTRACT.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            out = adapter.evaluate(ROOT)
            self.assertTrue(out["controller_result"]["admissible"], out)
        finally:
            CONTRACT.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
