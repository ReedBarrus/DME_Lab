from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.coordination import basis_workcycle_v1 as bw


def unit_fixture() -> dict:
    return {
        "identity": {
            "work_item_id": "W-COMPRESS-001",
            "campaign_id": "WORKCYCLE_STABILIZATION_001",
            "parent_work_item_id": None,
            "operative_frame_ref": "HEAD",
            "created_from_event": "PRESSURE_JUSTIFICATION_001",
        },
        "basis": {
            "basis_id": "B-COMPRESSION-001",
            "basis_type": "LOAD_BEARING_UNCERTAINTY",
            "statement": "Current operative context is inflated by redundant hot documentation.",
            "evidence_refs": ["docs/example.md"],
            "desired_consequence": {
                "statement": "Reduce hot representation while retaining exact reconstructability."
            },
            "current_obstruction": {
                "statement": "Redundant prose increases reconstruction and coordination burden."
            },
            "relevance_test": {
                "question": "Would successful compression reduce live context burden?",
                "failure_if_unanswered": True,
            },
            "basis_status": "SUPPORTED",
        },
        "pressure_selection": {
            "pressure_id": "P-COMPRESS-001",
            "target_distinction": {
                "lhs": "COLD_EVIDENCE",
                "rhs": "HOT_OPERATIVE_STATE",
            },
            "selection_basis": (
                "The distinction is required to remove redundant hot prose without "
                "destroying challengeable historical evidence."
            ),
            "expected_information_gain": {
                "statement": "Whether the smaller representation preserves load-bearing relations."
            },
            "application_dependency": (
                "A matched compression candidate can replace redundant hot representation "
                "while exact originals remain cold-retained."
            ),
            "stop_if_resolved_by_existing_evidence": True,
            "priority_basis": "BLOCKS_RECONSTRUCTION",
            "load_bearing_effects": ["RECONSTRUCTION", "OBSERVABILITY", "BASIS"],
        },
        "pressure_contract": {
            "allowed_operations": [
                "OBSERVE",
                "RECONSTRUCT",
                "COMPARE",
                "FALSIFY",
                "ADJUDICATE",
            ],
            "prohibited_operations": [
                "SELF_PROMOTE",
                "CREATE_AUTHORITY",
                "EXPAND_SCOPE_WITHOUT_BASIS",
                "SPAWN_UNBOUNDED_PRESSURES",
            ],
            "success_condition": {
                "statement": "Candidate is smaller and fresh reconstruction preserves the bounded operative posture."
            },
            "failure_condition": {
                "statement": "Load-bearing relation or source lineage is lost."
            },
            "unresolved_condition": {
                "statement": "Fresh reconstruction cannot determine equivalence."
            },
            "pressure_budget": {
                "max_rounds": 1,
                "max_branch_count": 1,
                "max_unresolved_children": 0,
            },
        },
        "result": {
            "source_result_ref": None,
            "distinctions": [],
            "apparatus_failures": [],
            "semantic_failures": [],
        },
        "qualification": {
            "adjudication_ref": None,
            "scientific_standing": "NONE",
            "authority_effect": "NONE",
            "qualification_basis": "",
            "unresolved_load_bearing_questions": [],
        },
        "application": {
            "required": True,
            "target_surface": "ATLAS",
            "proposed_change": {
                "statement": "Use the compact representation as hot state and retain exact originals cold."
            },
            "executable_change_ref": None,
            "application_status": "NOT_YET_ELIGIBLE",
            "withholding_basis": None,
        },
        "consequence_observation": {
            "required_if_applied": True,
            "expected_effect": "Hot context shrinks without reconstruction loss.",
            "observed_effect": None,
            "effect_class": "NOT_YET_OBSERVABLE",
            "evidence_refs": [],
            "regression_detected": False,
        },
        "basis_reconciliation": {
            "original_basis_id": "B-COMPRESSION-001",
            "disposition": None,
            "remaining_gap": None,
            "next_pressure_allowed": False,
            "next_pressure_basis": None,
            "termination_reason": None,
        },
        "sanity_check": {
            "if_this_work_succeeds": {
                "what_changes_in_the_operating_world": (
                    "The seat reconstructs from a smaller hot representation and "
                    "the exact originals move out of the active context burden."
                )
            },
            "if_nothing_would_change": {
                "posture": "DO_NOT_RUN",
            },
        },
    }


class BasisWorkcycleV1Tests(unittest.TestCase):
    def test_load_bearing_supported_basis_is_pressure_admissible(self):
        result = bw.pressure_admissibility(unit_fixture())
        self.assertTrue(result["admissible"])
        self.assertEqual(result["blockers"], [])
        self.assertIn("RECONSTRUCTION", result["material_effects"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")

    def test_non_load_bearing_question_is_held(self):
        unit = unit_fixture()
        unit["pressure_selection"]["load_bearing_effects"] = ["CURIOSITY"]
        result = bw.pressure_admissibility(unit)
        self.assertFalse(result["admissible"])
        self.assertIn("NO_LOAD_BEARING_EFFECT", result["blockers"])
        posture = bw.derive_next_work_posture(unit, admissibility=result)
        self.assertEqual(posture["posture"], "HOLD_NO_JUSTIFIED_WORK")

    def test_existing_qualified_evidence_blocks_redundant_pressure(self):
        unit = unit_fixture()
        result = bw.pressure_admissibility(
            unit,
            qualified_result_already_resolves=True,
        )
        self.assertFalse(result["admissible"])
        self.assertIn("EXISTING_QUALIFIED_RESULT_RESOLVES", result["blockers"])

    def test_no_operating_change_blocks_pressure(self):
        unit = unit_fixture()
        unit["sanity_check"]["if_this_work_succeeds"][
            "what_changes_in_the_operating_world"
        ] = "NONE"
        result = bw.pressure_admissibility(unit)
        self.assertFalse(result["admissible"])
        self.assertIn("NO_OPERATING_CHANGE", result["blockers"])

    def test_qualified_application_eligible_routes_to_apply(self):
        unit = unit_fixture()
        unit["qualification"]["scientific_standing"] = "QUALIFIED"
        unit["application"]["application_status"] = "ELIGIBLE"
        admissibility = bw.pressure_admissibility(unit)
        posture = bw.derive_next_work_posture(unit, admissibility=admissibility)
        self.assertEqual(posture["posture"], "APPLY_QUALIFIED_RESULT")
        self.assertFalse(posture["creates_work_item"])

    def test_applied_change_routes_to_consequence_observation(self):
        unit = unit_fixture()
        unit["qualification"]["scientific_standing"] = "QUALIFIED"
        unit["application"]["application_status"] = "APPLIED"
        unit["consequence_observation"]["effect_class"] = "NOT_YET_OBSERVABLE"
        admissibility = bw.pressure_admissibility(unit)
        posture = bw.derive_next_work_posture(unit, admissibility=admissibility)
        self.assertEqual(
            posture["posture"],
            "OBSERVE_APPLICATION_CONSEQUENCE",
        )

    def test_satisfied_reconciliation_closes_basis(self):
        unit = unit_fixture()
        admissibility = bw.pressure_admissibility(unit)
        reconciliation = bw.basis_reconciliation(
            unit,
            disposition="SATISFIED",
            remaining_gap=None,
        )
        posture = bw.derive_next_work_posture(
            unit,
            admissibility=admissibility,
            reconciliation=reconciliation,
        )
        self.assertEqual(posture["posture"], "CLOSE_BASIS")

    def test_repository_relational_compression_w2_is_basis_admissible(self):
        repo = Path(__file__).resolve().parents[2]
        path = (
            repo
            / "docs/campaigns/workcycle_stabilization_001/state/"
            "WORKCYCLE_STABILIZATION_001_RELATIONAL_COMPRESSION_W2.json"
        )
        unit = json.loads(path.read_text(encoding="utf-8"))
        bw.validate_workflow_unit(unit)
        admissibility = bw.pressure_admissibility(unit)
        self.assertTrue(admissibility["admissible"], admissibility["blockers"])
        posture = bw.derive_next_work_posture(
            unit,
            admissibility=admissibility,
        )
        self.assertEqual(posture["posture"], "RESOLVE_LOAD_BEARING_GAP")
        self.assertFalse(posture["creates_work_item"])

    def test_local_frame_dependence_cell_is_basis_admissible(self):
        repo = Path(__file__).resolve().parents[2]
        path = (
            repo
            / "docs/campaigns/workcycle_stabilization_001/state/"
            "LOCAL_FRAME_DEPENDENCE_IDENTITY_CELL_001.json"
        )
        unit = json.loads(path.read_text(encoding="utf-8"))
        bw.validate_workflow_unit(unit)
        admissibility = bw.pressure_admissibility(unit)
        self.assertTrue(admissibility["admissible"], admissibility["blockers"])
        self.assertIn("RECONSTRUCTION", admissibility["material_effects"])
        posture = bw.derive_next_work_posture(
            unit,
            admissibility=admissibility,
        )
        self.assertEqual(posture["posture"], "RESOLVE_LOAD_BEARING_GAP")
        self.assertFalse(posture["creates_work_item"])

    def test_remaining_gap_requires_explicit_next_pressure_basis(self):
        unit = unit_fixture()
        with self.assertRaises(bw.BasisWorkcycleError):
            bw.basis_reconciliation(
                unit,
                disposition="STILL_BLOCKED",
                remaining_gap="reconstruction mismatch",
            )
        result = bw.basis_reconciliation(
            unit,
            disposition="STILL_BLOCKED",
            remaining_gap="reconstruction mismatch",
            next_pressure_basis="fresh reconstruction remains load-bearing",
        )
        self.assertTrue(result["next_pressure_allowed"])


if __name__ == "__main__":
    unittest.main()
