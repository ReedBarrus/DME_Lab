from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/"tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0,str(TOOLS))

import live_completion_raw_evaluator_v1 as raw
import live_unit_completion_standing_producer_v1 as p07
import live_completion_blocker_status_producer_v1 as p08
import live_completion_controller_adapter_v1 as adapter

FIX=ROOT/"fixtures"/"live_completion_evidence_v1"

def load(name):
    return json.loads((FIX/name).read_text(encoding="utf-8"))

class LiveCompletionEvidenceV1IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.frozen=load("FROZEN_LANE_A_SPECIMEN.json")
        self.binding=load("RAW_LIVE_WORK_BINDING.json")
        self.criterion=load("RAW_COMPLETION_CRITERION.json")
        self.evidence=load("RAW_WORK_EVIDENCE.json")
        self.scope=load("RAW_BLOCKER_SCOPE.json")
        self.candidates=load("PRODUCER_CANDIDATES.json")
        self.qualified=load("PRODUCER_QUALIFICATION_REGISTRY_002.json")

    def test_candidate_registry_cannot_drive_runtime_production(self):
        p05=raw.derive_p05(ROOT,self.frozen,self.binding)
        p06=raw.derive_p06(ROOT,self.frozen,self.binding,self.criterion,self.evidence)
        self.assertEqual(p07.produce(ROOT,self.candidates,self.binding,p05,p06)["status"],"NOT_ESTABLISHED")
        self.assertEqual(
            p08.produce(ROOT,self.candidates,self.frozen,self.binding,self.criterion,self.evidence,self.scope)["status"],
            "NOT_ESTABLISHED",
        )

    def test_receipt_backed_registry_drives_runtime_production(self):
        p05=raw.derive_p05(ROOT,self.frozen,self.binding)
        p06=raw.derive_p06(ROOT,self.frozen,self.binding,self.criterion,self.evidence)
        r7=p07.produce(ROOT,self.qualified,self.binding,p05,p06)
        r8=p08.produce(ROOT,self.qualified,self.frozen,self.binding,self.criterion,self.evidence,self.scope)
        self.assertEqual(r7["status"],"ESTABLISHED")
        self.assertEqual(r7["relation"]["standing"],"QUALIFIED")
        self.assertEqual(r8["status"],"ESTABLISHED")
        self.assertEqual(r8["relation"]["standing"],"NONE_ESTABLISHED")

    def test_relation_bases_pin_every_consumed_surface(self):
        b7=adapter.verify_relation_basis(ROOT,str(FIX/"P07_RELATION_BASIS_001.json"),p07.BASIS_REF)
        b8=adapter.verify_relation_basis(ROOT,str(FIX/"P08_RELATION_BASIS_001.json"),p08.BASIS_REF)
        self.assertIn("qualification_registry",b7["pinned_inputs"])
        self.assertIn("qualification_registry",b8["pinned_inputs"])
        self.assertIn("blocker_scope",b8["pinned_inputs"])
        reproduced=adapter.reproduce_relations(ROOT)
        self.assertEqual(reproduced["P07"]["relation"]["standing"],"QUALIFIED")
        self.assertEqual(reproduced["P08"]["relation"]["standing"],"NONE_ESTABLISHED")

    def test_exact_authoritative_controller_consumes_repaired_bridge(self):
        observed=adapter.evaluate_authoritative_controller(ROOT)
        self.assertEqual(observed["controller_blob"],adapter.AUTHORITATIVE_CONTROLLER_BLOB)
        self.assertFalse(observed["transition_executed"])
        self.assertEqual(observed["live_lane_mutation"],"NONE")
        result=observed["controller_result"]
        self.assertTrue(result["admissible"],result)
        self.assertEqual(result["selected_branch"],"COMPLETE")
        self.assertEqual(result["predicates_consulted"]["admissibility"],["P01","P02","P03","P04","P05","P06","P07","P08"])
        self.assertEqual(result["resulting_state"],{
            "claim_status":"COMPLETED",
            "lane_status":"READY_UNCLAIMED",
            "occupant_binding":None,
        })

    def test_controller_input_is_projection_not_historical_claim_mutation(self):
        inp=adapter.build_controller_input(ROOT)
        self.assertEqual(set(inp["claim"]),{"claim_id","status","envelope_id","bounded_unit_id"})
        historical=json.loads(
            adapter._git(ROOT,"show",f"{self.frozen['lane_a_head']}:{self.frozen['lane_a_claim_path']}")
        )
        self.assertNotIn("envelope_id",historical)
        self.assertNotIn("bounded_unit_id",historical)
        self.assertEqual(historical["consequence_envelope_id"],inp["claim"]["envelope_id"])

if __name__=="__main__":
    unittest.main()
