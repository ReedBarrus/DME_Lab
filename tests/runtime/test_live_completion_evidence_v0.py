from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import live_completion_raw_evaluator_v0 as raw
import live_unit_completion_standing_producer_v0 as p07
import live_completion_blocker_status_producer_v0 as p08
import run_live_completion_evidence_pressure_v0 as runner


FIX = ROOT / "fixtures" / "live_completion_evidence_v0"


def load(name: str):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


class LiveCompletionEvidenceV0Tests(unittest.TestCase):
    def setUp(self):
        self.frozen = load("FROZEN_LANE_A_SPECIMEN.json")
        self.binding = load("RAW_LIVE_WORK_BINDING.json")
        self.criterion = load("RAW_COMPLETION_CRITERION.json")
        self.evidence = load("RAW_WORK_EVIDENCE.json")
        self.scope = load("RAW_BLOCKER_SCOPE.json")
        self.registry = load("PRODUCER_CANDIDATES.json")
        self.cells = load("PRESSURE_CELLS_A_K.json")["cells"]

    def test_schema_required_fields_match_raw_fixtures(self):
        pairs = [
            ("live_work_unit_binding_v0.schema.json", "RAW_LIVE_WORK_BINDING.json"),
            ("live_completion_criterion_v0.schema.json", "RAW_COMPLETION_CRITERION.json"),
            ("live_work_evidence_bundle_v0.schema.json", "RAW_WORK_EVIDENCE.json"),
            ("live_completion_blocker_scope_v0.schema.json", "RAW_BLOCKER_SCOPE.json"),
        ]
        for schema_name, fixture_name in pairs:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text())
            fixture = load(fixture_name)
            self.assertEqual(set(schema["required"]), set(fixture))
            self.assertFalse(schema["additionalProperties"])

    def test_raw_fixtures_have_no_lifecycle_answer_fields(self):
        findings = runner.forbidden_raw_answer_fields()
        self.assertTrue(all(not hits for hits in findings.values()), findings)

    def test_p05_clean_and_identity_mismatch(self):
        clean = raw.derive_p05(ROOT, self.frozen, self.binding)
        self.assertEqual(clean["status"], "MATCHES")

        changed = copy.deepcopy(self.binding)
        changed["claim_id"] = "DIFFERENT-CLAIM"
        bad = raw.derive_p05(ROOT, self.frozen, changed)
        self.assertEqual(bad["status"], "DOES_NOT_MATCH")
        self.assertEqual(bad["mismatches"], ["claim_id"])

    def test_p06_clean_missing_stale_and_posthoc_criterion(self):
        clean = raw.derive_p06(
            ROOT, self.frozen, self.binding, self.criterion, self.evidence
        )
        self.assertEqual(clean["status"], "SATISFIED")

        missing = raw.derive_p06(
            ROOT, self.frozen, self.binding, None, self.evidence
        )
        self.assertEqual(missing["status"], "NOT_ESTABLISHED")
        self.assertEqual(missing["reason"], "MISSING_CRITERION")

        stale = copy.deepcopy(self.evidence)
        stale["lane_head"] = self.frozen["initial_work_commit"]
        with self.assertRaisesRegex(raw.AdministrationInvalid, "STALE_LIVE_BASIS"):
            raw.derive_p06(
                ROOT, self.frozen, self.binding, self.criterion, stale
            )

        posthoc = copy.deepcopy(self.criterion)
        posthoc["criterion_basis_commit"] = self.frozen["lane_a_head"]
        with self.assertRaisesRegex(
            raw.AdministrationInvalid, "CRITERION_PROVENANCE_INVALID"
        ):
            raw.derive_p06(
                ROOT, self.frozen, self.binding, posthoc, self.evidence
            )

    def test_p07_requires_exact_candidate_identity_and_live_raw_basis(self):
        p05 = raw.derive_p05(ROOT, self.frozen, self.binding)
        p06 = raw.derive_p06(
            ROOT, self.frozen, self.binding, self.criterion, self.evidence
        )
        good = p07.produce(ROOT, self.registry, self.binding, p05, p06)
        self.assertEqual(good["status"], "ESTABLISHED")
        self.assertEqual(good["relation"]["standing"], "QUALIFIED")

        tampered = copy.deepcopy(self.registry)
        tampered["producer_candidates"][
            "LIVE_UNIT_COMPLETION_STANDING_PRODUCER@v0"
        ]["implementation_blob"] = "0" * 40
        bad = p07.produce(ROOT, tampered, self.binding, p05, p06)
        self.assertEqual(bad["status"], "NOT_ESTABLISHED")
        self.assertIsNone(bad["relation"])

    def test_p08_missing_input_does_not_become_none_established(self):
        missing = p08.produce(ROOT, self.registry, self.scope, None)
        self.assertEqual(missing["status"], "NOT_ESTABLISHED")
        self.assertIsNone(missing["relation"])

        clear = p08.produce(
            ROOT, self.registry, self.scope, self.cells["I"]["blocker_evaluations"]
        )
        self.assertEqual(clear["relation"]["standing"], "NONE_ESTABLISHED")

        blocker = p08.produce(
            ROOT, self.registry, self.scope, self.cells["H"]["blocker_evaluations"]
        )
        self.assertEqual(blocker["relation"]["standing"], "FORBIDS_COMPLETION")

    def test_all_basis_refs_recoverable(self):
        result = runner.evaluate()
        self.assertTrue(all(result["basis_recovery"].values()), result["basis_recovery"])

    def test_a_through_k_and_clean_composition(self):
        result = runner.evaluate()
        self.assertEqual(set(result["cells"]), set("ABCDEFGHIJK"))
        self.assertTrue(all(result["cell_checks"].values()), result["cells"])
        self.assertTrue(result["producer_qualification"]["P07"]["pass"])
        self.assertTrue(result["producer_qualification"]["P08"]["pass"])
        self.assertEqual(result["cells"]["J"]["composition"], "COMPLETE_EVALUABLE")
        self.assertFalse(result["cells"]["J"]["transition_executed"])
        self.assertEqual(result["lifecycle_effect"], "NONE")
        self.assertEqual(result["lane_mutation"], "NONE")
        self.assertTrue(result["pass"])

    def test_evidence_serialization_is_byte_identical(self):
        first = runner.pretty_bytes(runner.evaluate())
        second = runner.pretty_bytes(runner.evaluate())
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
