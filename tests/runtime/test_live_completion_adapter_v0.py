from __future__ import annotations
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/"tools"
if str(TOOLS) not in sys.path: sys.path.insert(0,str(TOOLS))

import live_completion_controller_adapter_v2 as adapter
import run_live_completion_adapter_pressure_v0 as pressure

class AdapterQualificationTests(unittest.TestCase):
    def test_public_api_accepts_only_repo_root(self):
        self.assertEqual(adapter.public_signature(),"(repo_root: 'str | Path') -> 'dict[str, Any]'")

    def test_clean_path_exact_controller_and_no_execution(self):
        out=adapter.evaluate(ROOT)
        self.assertEqual(out["authoritative_controller"]["blob"],adapter.CONTROLLER_BLOB)
        self.assertTrue(out["controller_result"]["admissible"])
        self.assertEqual(out["controller_result"]["selected_branch"],"COMPLETE")
        self.assertFalse(out["transition_executed"])
        self.assertEqual(out["lane_mutation"],"NONE")
        self.assertEqual(out["claim_mutation"],"NONE")
        self.assertEqual(out["occupant_mutation"],"NONE")

    def test_historical_claim_separated_from_projection(self):
        out=adapter.evaluate(ROOT)
        self.assertNotEqual(out["historical_claim_object"],out["controller_claim_projection"])
        self.assertNotIn("bounded_unit_id",out["historical_claim_object"])
        self.assertIn("bounded_unit_id",out["controller_claim_projection"])
        self.assertNotIn("historical_claim",out["controller_result"])
        self.assertEqual(out["controller_returned_claim_projection"],out["controller_claim_projection"])

    def test_exact_consumed_projection_digest_is_stable(self):
        out=adapter.evaluate(ROOT)
        self.assertEqual(adapter._digest(out["controller_input_projection"]),out["controller_input_digest"])

    def test_all_a_l_pressure_cells(self):
        result=pressure.evaluate()
        self.assertEqual(set(result["cell_checks"]),set("ABCDEFGHIJKL"))
        self.assertTrue(all(result["cell_checks"].values()),result["cells"])
        self.assertTrue(result["pass"])

    def test_receipt_schema_required_fields(self):
        schema=json.loads((ROOT/"schemas/live_completion_adapter_receipt_v0.schema.json").read_text())
        out=adapter.evaluate(ROOT)
        for key in schema["required"]:
            self.assertIn(key,out)

if __name__=="__main__": unittest.main()
