from __future__ import annotations
import copy
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
import run_live_completion_evidence_pressure_v1 as runner

FIX=ROOT/"fixtures"/"live_completion_evidence_v1"

def load(name):
    return json.loads((FIX/name).read_text(encoding="utf-8"))

class LiveCompletionEvidenceV1Tests(unittest.TestCase):
    def setUp(self):
        self.frozen=load("FROZEN_LANE_A_SPECIMEN.json")
        self.binding=load("RAW_LIVE_WORK_BINDING.json")
        self.criterion=load("RAW_COMPLETION_CRITERION.json")
        self.evidence=load("RAW_WORK_EVIDENCE.json")
        self.scope=load("RAW_BLOCKER_SCOPE.json")
        self.candidates=load("PRODUCER_CANDIDATES.json")

    def test_canonical_bounded_unit_identity(self):
        p05=raw.derive_p05(ROOT,self.frozen,self.binding)
        self.assertEqual(p05["status"],"MATCHES")
        renamed=copy.deepcopy(self.binding)
        renamed["bounded_unit_id"]="sha256:"+"0"*64
        self.assertEqual(raw.derive_p05(ROOT,self.frozen,renamed)["status"],"DOES_NOT_MATCH")
        self.assertIn("bounded_unit_id",raw.derive_p05(ROOT,self.frozen,renamed)["mismatches"])

    def test_criterion_semantics_are_source_derived(self):
        clean=raw.derive_p06(ROOT,self.frozen,self.binding,self.criterion,self.evidence)
        self.assertEqual(clean["status"],"SATISFIED")
        attack=copy.deepcopy(self.criterion)
        attack["allowed_mutation_paths"]=["docs/candidates/live_two_lane_trial_lane_a_v0/RESULT_OBSERVED_ONLY.md"]
        attack["required_final_artifacts"]=list(attack["allowed_mutation_paths"])
        with self.assertRaisesRegex(raw.AdministrationInvalid,"CRITERION_SEMANTICS_NOT_SOURCE_DERIVED"):
            raw.derive_p06(ROOT,self.frozen,self.binding,attack,self.evidence)

    def test_work_interval_is_derived_from_git_not_criterion(self):
        self.assertNotIn("required_work_commits",self.criterion)
        self.assertNotIn("final_work_head",self.criterion)
        clean=raw.derive_p06(ROOT,self.frozen,self.binding,self.criterion,self.evidence)
        self.assertEqual(clean["observed_work_commits"],self.evidence["work_commits"])

    def test_candidate_declaration_is_not_runtime_qualification(self):
        p05=raw.derive_p05(ROOT,self.frozen,self.binding)
        p06=raw.derive_p06(ROOT,self.frozen,self.binding,self.criterion,self.evidence)
        self.assertEqual(p07.candidate_produce(ROOT,self.candidates,self.binding,p05,p06)["status"],"ESTABLISHED")
        self.assertEqual(p07.produce(ROOT,{},self.binding,p05,p06)["status"],"NOT_ESTABLISHED")

    def test_p08_derives_blockers_from_raw_basis(self):
        clean=p08.candidate_produce(ROOT,self.candidates,self.frozen,self.binding,self.criterion,self.evidence,self.scope)
        self.assertEqual(clean["relation"]["standing"],"NONE_ESTABLISHED")
        self.assertTrue(all(v is False for v in clean["derived_evaluations"].values()))

        attack=copy.deepcopy(self.binding)
        attack["claim_id"]="DIFFERENT-CLAIM"
        blocked=p08.candidate_produce(ROOT,self.candidates,self.frozen,attack,self.criterion,self.evidence,self.scope)
        self.assertEqual(blocked["relation"]["standing"],"FORBIDS_COMPLETION")
        self.assertTrue(blocked["derived_evaluations"]["WORK_UNIT_IDENTITY_MISMATCH"])

    def test_candidate_pressure(self):
        result=runner.evaluate_candidate()
        self.assertTrue(result["pass"],result)
        self.assertTrue(all(result["cell_checks"].values()),result["cells"])
        self.assertEqual(result["lifecycle_execution"],"NONE")
        self.assertEqual(result["lane_mutation"],"NONE")

    def test_deterministic_candidate_evidence(self):
        self.assertEqual(runner.pretty_bytes(runner.evaluate_candidate()),runner.pretty_bytes(runner.evaluate_candidate()))

if __name__=="__main__":
    unittest.main()
