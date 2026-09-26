from __future__ import annotations

from copy import deepcopy
import unittest

from src.coordination.materialized_invocation_result_settlement_v0 import (
    CANDIDATE_ACCEPTED,
    CANDIDATE_HELD,
    CANDIDATE_REJECTED,
    UNRESOLVED,
    MaterializedResultSettlementError,
    build_materialized_candidate_settlement,
)
from src.observation.materialized_invocation_result_witness_v0 import (
    build_materialized_invocation_result_witness,
)
from tests.observation.test_materialized_invocation_result_witness_v0 import (
    valid_materialized_consumption,
)


def valid_materialized_witness() -> dict:
    _, _, _, receipt, raw = valid_materialized_consumption()
    return build_materialized_invocation_result_witness(
        consumption_receipt=receipt,
        raw_output=raw,
        adapter_identity="materialized-disposable-callback-adapter-v0",
        observer_limitations=[
            "callback return does not prove external consequence",
            "raw callback output is not semantically interpreted",
            "no settlement is performed by the source witness",
        ],
        model_identity=None,
    )


def dispositions() -> dict[str, str]:
    return {
        "fixture_result": CANDIDATE_ACCEPTED,
        "count": CANDIDATE_HELD,
        "work_item_id": CANDIDATE_ACCEPTED,
    }


def bases() -> dict[str, str]:
    return {
        "fixture_result": "explicit fixture return field retained without truth promotion",
        "count": "count is observed but carries no semantic consequence standing",
        "work_item_id": "exact work-item identity matches the bound witness lineage",
    }


class MaterializedInvocationResultSettlementV0Tests(unittest.TestCase):
    def build(self, **changes):
        args = {
            "result_witness": valid_materialized_witness(),
            "field_dispositions": dispositions(),
            "settlement_basis": bases(),
            "settlement_actor_identity": "independent-materialized-settler-fixture-v0",
        }
        args.update(changes)
        return build_materialized_candidate_settlement(**args)

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(self.build(), self.build())

    def test_exact_materialized_lineage_is_bound(self):
        witness = valid_materialized_witness()
        settlement = self.build(result_witness=witness)
        self.assertEqual(
            settlement["source_successor_id"],
            witness["successor_id"],
        )
        self.assertEqual(
            settlement["source_work_spec_id"],
            witness["work_spec_id"],
        )
        self.assertEqual(
            settlement["source_materialized_unit_integrity_sha256"],
            witness["materialized_unit_integrity_sha256"],
        )
        self.assertEqual(
            settlement["source_consumption_id"],
            witness["consumption_id"],
        )
        self.assertEqual(
            settlement["source_atomic_admission_id"],
            witness["atomic_admission_id"],
        )

    def test_field_dispositions_remain_distinct(self):
        settlement = self.build()
        self.assertEqual(
            settlement["accepted_fields"],
            ["fixture_result", "work_item_id"],
        )
        self.assertEqual(settlement["held_fields"], ["count"])
        self.assertEqual(settlement["rejected_fields"], [])
        self.assertEqual(settlement["unresolved_fields"], [])

    def test_accepted_does_not_create_qualification_or_consequence(self):
        settlement = self.build()
        self.assertIn("fixture_result", settlement["accepted_fields"])
        self.assertEqual(settlement["qualification_effect"], "NONE")
        self.assertFalse(settlement["scientific_admission_created"])
        self.assertEqual(settlement["external_consequence_effect"], "NONE")
        self.assertEqual(settlement["scientific_standing_effect"], "NONE")

    def test_settlement_does_not_mutate_witness(self):
        witness = valid_materialized_witness()
        before = deepcopy(witness)
        settlement = self.build(result_witness=witness)
        self.assertEqual(witness, before)
        self.assertTrue(settlement["source_witness_preserved"])

    def test_disposition_change_changes_settlement_identity(self):
        changed = dispositions()
        changed["count"] = CANDIDATE_REJECTED
        self.assertNotEqual(
            self.build()["settlement_id"],
            self.build(field_dispositions=changed)["settlement_id"],
        )

    def test_all_four_disposition_classes_are_preserved(self):
        witness = valid_materialized_witness()
        raw = deepcopy(witness["raw_output"])
        raw["held_field"] = "candidate"
        raw["rejected_field"] = "overclaim"
        raw["unknown_field"] = None
        _, _, _, receipt, _ = valid_materialized_consumption()
        expanded_witness = build_materialized_invocation_result_witness(
            consumption_receipt=receipt,
            raw_output=raw,
            adapter_identity="materialized-disposable-callback-adapter-v0",
            observer_limitations=["no external consequence"],
            model_identity=None,
        )
        field_dispositions = {
            "fixture_result": CANDIDATE_ACCEPTED,
            "held_field": CANDIDATE_HELD,
            "rejected_field": CANDIDATE_REJECTED,
            "unknown_field": UNRESOLVED,
        }
        settlement_basis = {
            "fixture_result": "candidate accepted only",
            "held_field": "candidate held only",
            "rejected_field": "candidate rejected only",
            "unknown_field": "candidate unresolved only",
        }
        settlement = build_materialized_candidate_settlement(
            result_witness=expanded_witness,
            field_dispositions=field_dispositions,
            settlement_basis=settlement_basis,
            settlement_actor_identity="fixture-settler-v0",
        )
        self.assertEqual(settlement["accepted_fields"], ["fixture_result"])
        self.assertEqual(settlement["held_fields"], ["held_field"])
        self.assertEqual(settlement["rejected_fields"], ["rejected_field"])
        self.assertEqual(settlement["unresolved_fields"], ["unknown_field"])

    def test_tampered_raw_output_is_rejected_even_if_digest_field_unchanged(self):
        witness = valid_materialized_witness()
        witness["raw_output"]["count"] = 999
        with self.assertRaisesRegex(
            MaterializedResultSettlementError,
            "raw output digest mismatch",
        ):
            self.build(result_witness=witness)

    def test_tampered_exact_lineage_is_rejected(self):
        witness = valid_materialized_witness()
        witness["work_spec_id"] = "successor-work-spec:sha256:" + "9" * 64
        with self.assertRaisesRegex(
            MaterializedResultSettlementError,
            "result witness identity mismatch",
        ):
            self.build(result_witness=witness)

    def test_unknown_field_is_rejected(self):
        changed = dispositions()
        changed["not_in_output"] = CANDIDATE_HELD
        changed_basis = bases()
        changed_basis["not_in_output"] = "fixture"
        with self.assertRaisesRegex(
            MaterializedResultSettlementError,
            "settled field not present",
        ):
            self.build(
                field_dispositions=changed,
                settlement_basis=changed_basis,
            )

    def test_unsupported_disposition_is_rejected(self):
        changed = dispositions()
        changed["fixture_result"] = "QUALIFIED"
        with self.assertRaisesRegex(
            MaterializedResultSettlementError,
            "unsupported field disposition",
        ):
            self.build(field_dispositions=changed)

    def test_each_classified_field_requires_basis(self):
        changed_basis = bases()
        del changed_basis["count"]
        with self.assertRaisesRegex(
            MaterializedResultSettlementError,
            r"settlement_basis\[count\]",
        ):
            self.build(settlement_basis=changed_basis)

    def test_extra_basis_is_rejected(self):
        changed_basis = bases()
        changed_basis["ghost"] = "not classified"
        with self.assertRaisesRegex(
            MaterializedResultSettlementError,
            "settlement basis supplied for unclassified fields",
        ):
            self.build(settlement_basis=changed_basis)

    def test_no_authority_execution_atlas_or_standing_effect(self):
        settlement = self.build()
        self.assertEqual(settlement["authority_effect"], "NONE")
        self.assertEqual(settlement["execution_effect"], "NONE")
        self.assertEqual(settlement["atlas_mutation_effect"], "NONE")
        self.assertEqual(settlement["scientific_standing_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
