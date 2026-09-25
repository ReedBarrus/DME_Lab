from __future__ import annotations

from copy import deepcopy
import unittest

from src.observation.invocation_result_witness_v0 import (
    InvocationResultWitnessError,
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
        "capability_id": "CAP.RESULT.WITNESS.001",
        "work_attempt_id": "ATTEMPT-RESULT-001",
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


class InvocationResultWitnessV0Tests(unittest.TestCase):
    def build(self, **changes):
        args = {
            "consumption_receipt": valid_consumption_receipt(),
            "raw_output": {
                "fixture_result": "SUCCESS",
                "count": 1,
            },
            "adapter_identity": "disposable-callback-adapter-v0",
            "observer_limitations": [
                "callback return does not prove external consequence",
                "no settlement is performed",
            ],
            "model_identity": None,
        }
        args.update(changes)
        return build_invocation_result_witness(**args)

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(self.build(), self.build())

    def test_raw_output_is_preserved_and_identity_bound(self):
        witness = self.build()
        self.assertEqual(
            witness["raw_output"],
            {"fixture_result": "SUCCESS", "count": 1},
        )
        self.assertEqual(
            witness["raw_output_canonical_json"],
            '{"count":1,"fixture_result":"SUCCESS"}',
        )
        self.assertEqual(len(witness["raw_output_sha256"]), 64)

    def test_output_change_changes_witness_identity(self):
        one = self.build(raw_output={"value": 1})
        two = self.build(raw_output={"value": 2})
        self.assertNotEqual(one["raw_output_sha256"], two["raw_output_sha256"])
        self.assertNotEqual(one["witness_id"], two["witness_id"])

    def test_observer_limitation_change_changes_witness_identity(self):
        one = self.build(observer_limitations=["external effect unresolved"])
        two = self.build(observer_limitations=["external effect not observed"])
        self.assertNotEqual(one["witness_id"], two["witness_id"])

    def test_missing_model_identity_remains_unresolved(self):
        witness = self.build()
        self.assertIsNone(witness["model_identity"])
        self.assertIn("model_identity", witness["unresolved_fields"])
        self.assertNotIn("model_identity", witness["measured_fields"])

    def test_supplied_model_identity_is_measured(self):
        witness = self.build(model_identity="fixture/model-v0")
        self.assertEqual(witness["model_identity"], "fixture/model-v0")
        self.assertIn("model_identity", witness["measured_fields"])
        self.assertNotIn("model_identity", witness["unresolved_fields"])

    def test_tampered_consumption_receipt_is_rejected(self):
        receipt = valid_consumption_receipt()
        receipt["work_attempt_id"] = "ATTEMPT-TAMPERED"
        with self.assertRaisesRegex(
            InvocationResultWitnessError,
            "consumption receipt identity mismatch",
        ):
            self.build(consumption_receipt=receipt)

    def test_unconsumed_receipt_is_rejected(self):
        receipt = valid_consumption_receipt()
        receipt["authority_consumed"] = False
        with self.assertRaisesRegex(
            InvocationResultWitnessError,
            "authority_consumed=true",
        ):
            self.build(consumption_receipt=receipt)

    def test_non_json_output_is_rejected(self):
        with self.assertRaisesRegex(
            InvocationResultWitnessError,
            "canonical-JSON serializable",
        ):
            self.build(raw_output={1, 2, 3})

    def test_inputs_are_not_mutated(self):
        receipt = valid_consumption_receipt()
        output = {"nested": ["a", "b"]}
        limitations = ["no external-effect observation"]
        before = (deepcopy(receipt), deepcopy(output), deepcopy(limitations))
        self.build(
            consumption_receipt=receipt,
            raw_output=output,
            observer_limitations=limitations,
        )
        self.assertEqual(receipt, before[0])
        self.assertEqual(output, before[1])
        self.assertEqual(limitations, before[2])

    def test_no_interpretation_settlement_or_standing_is_created(self):
        witness = self.build()
        self.assertEqual(witness["semantic_interpretation"], "NONE")
        self.assertEqual(witness["settlement_effect"], "NONE")
        self.assertEqual(witness["authority_effect"], "NONE")
        self.assertEqual(witness["execution_effect"], "NONE")
        self.assertEqual(witness["scientific_standing_effect"], "NONE")
        self.assertFalse(witness["external_effect_inferred"])


if __name__ == "__main__":
    unittest.main()
