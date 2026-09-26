from __future__ import annotations

from copy import deepcopy
import unittest

from src.coordination.invocation_result_settlement_v0 import (
    CANDIDATE_ACCEPTED,
    CANDIDATE_HELD,
    CANDIDATE_REJECTED,
    UNRESOLVED,
    ResultSettlementError,
    build_candidate_settlement,
)
from src.observation.invocation_result_witness_v0 import (
    build_invocation_result_witness,
)
from src.runtime.local_authority_consumption_v0 import canonical_sha256


def valid_consumption_receipt() -> dict:
    chain = {
        "composition_id": "verified-authority-atomic-admission:sha256:" + "1" * 64,
        "atomic_admission_id": "atomic-admission:sha256:" + "2" * 64,
        "successor_id": "successor:sha256:" + "3" * 64,
        "successor_integrity_sha256": "4" * 64,
        "authority_binding_id": "current-authority-binding:sha256:" + "5" * 64,
        "authority_consumption_receipt_id": "receipt:sha256:" + "6" * 64,
        "authority_reservation_id": "reservation:sha256:" + "7" * 64,
        "capability_id": "CAP.SETTLEMENT.001",
        "work_attempt_id": "ATTEMPT-SETTLEMENT-001",
    }
    return {
        "object_type": "ADMITTED_AUTHORITY_CONSUMPTION_RECEIPT_V0",
        **chain,
        "consumption_id": (
            "admitted-authority-consumption:sha256:" + canonical_sha256(chain)
        ),
        "authority_status_after": "CONSUMED",
        "authority_remaining_uses_after": 0,
        "authority_consumed": True,
        "invocation_performed": True,
        "invocation_count": 1,
        "authority_effect": "NONE",
        "consumption_effect": "CONSUMED_ONE_USE",
        "scientific_standing_effect": "NONE",
    }


def valid_witness() -> dict:
    return build_invocation_result_witness(
        consumption_receipt=valid_consumption_receipt(),
        raw_output={
            "supported_value": 17,
            "useful_but_unverified": "candidate",
            "overclaim": "external effect definitely happened",
            "unknown": None,
        },
        adapter_identity="disposable-callback-adapter-v0",
        observer_limitations=[
            "callback return does not prove external consequence",
            "no settlement was performed by the source witness",
        ],
        model_identity=None,
    )


def dispositions() -> dict[str, str]:
    return {
        "supported_value": CANDIDATE_ACCEPTED,
        "useful_but_unverified": CANDIDATE_HELD,
        "overclaim": CANDIDATE_REJECTED,
        "unknown": UNRESOLVED,
    }


def bases() -> dict[str, str]:
    return {
        "supported_value": "explicit field retained in supplied witness",
        "useful_but_unverified": "useful candidate lacks qualification",
        "overclaim": "source witness explicitly infers no external effect",
        "unknown": "supplied field remains unresolved",
    }


class InvocationResultSettlementV0Tests(unittest.TestCase):
    def build(self, **changes):
        args = {
            "result_witness": valid_witness(),
            "field_dispositions": dispositions(),
            "settlement_basis": bases(),
            "settlement_actor_identity": "independent-settler-fixture-v0",
        }
        args.update(changes)
        return build_candidate_settlement(**args)

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(self.build(), self.build())

    def test_field_dispositions_remain_distinct(self):
        settlement = self.build()
        self.assertEqual(settlement["accepted_fields"], ["supported_value"])
        self.assertEqual(settlement["held_fields"], ["useful_but_unverified"])
        self.assertEqual(settlement["rejected_fields"], ["overclaim"])
        self.assertEqual(settlement["unresolved_fields"], ["unknown"])

    def test_accepted_does_not_create_qualification(self):
        settlement = self.build()
        self.assertIn("supported_value", settlement["accepted_fields"])
        self.assertEqual(settlement["qualification_effect"], "NONE")
        self.assertFalse(settlement["scientific_admission_created"])

    def test_settlement_does_not_mutate_witness(self):
        witness = valid_witness()
        before = deepcopy(witness)
        settlement = self.build(result_witness=witness)
        self.assertEqual(witness, before)
        self.assertTrue(settlement["source_witness_preserved"])

    def test_disposition_change_changes_settlement_identity(self):
        changed = dispositions()
        changed["useful_but_unverified"] = CANDIDATE_ACCEPTED
        self.assertNotEqual(
            self.build()["settlement_id"],
            self.build(field_dispositions=changed)["settlement_id"],
        )

    def test_tampered_raw_output_is_rejected_even_if_digest_field_is_unchanged(self):
        witness = valid_witness()
        witness["raw_output"]["supported_value"] = 999
        with self.assertRaisesRegex(
            ResultSettlementError,
            "raw output digest mismatch",
        ):
            self.build(result_witness=witness)

    def test_tampered_witness_identity_is_rejected(self):
        witness = valid_witness()
        witness["witness_id"] = "invocation-result-witness:sha256:" + "9" * 64
        with self.assertRaisesRegex(
            ResultSettlementError,
            "result witness identity mismatch",
        ):
            self.build(result_witness=witness)

    def test_unknown_field_is_rejected(self):
        changed = dispositions()
        changed["not_in_output"] = CANDIDATE_HELD
        changed_basis = bases()
        changed_basis["not_in_output"] = "fixture"
        with self.assertRaisesRegex(
            ResultSettlementError,
            "settled field not present",
        ):
            self.build(
                field_dispositions=changed,
                settlement_basis=changed_basis,
            )

    def test_unsupported_disposition_is_rejected(self):
        changed = dispositions()
        changed["supported_value"] = "QUALIFIED"
        with self.assertRaisesRegex(
            ResultSettlementError,
            "unsupported field disposition",
        ):
            self.build(field_dispositions=changed)

    def test_each_classified_field_requires_basis(self):
        changed_basis = bases()
        del changed_basis["overclaim"]
        with self.assertRaisesRegex(
            ResultSettlementError,
            r"settlement_basis\[overclaim\]",
        ):
            self.build(settlement_basis=changed_basis)

    def test_extra_basis_is_rejected(self):
        changed_basis = bases()
        changed_basis["ghost"] = "not classified"
        with self.assertRaisesRegex(
            ResultSettlementError,
            "settlement basis supplied for unclassified fields",
        ):
            self.build(settlement_basis=changed_basis)

    def test_no_authority_execution_or_atlas_mutation_effect(self):
        settlement = self.build()
        self.assertEqual(settlement["authority_effect"], "NONE")
        self.assertEqual(settlement["execution_effect"], "NONE")
        self.assertEqual(settlement["atlas_mutation_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
