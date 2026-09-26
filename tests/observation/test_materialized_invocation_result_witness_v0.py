from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.coordination.materialized_admitted_authority_consumption_v0 import (
    consume_materialized_admitted_authority_once,
)
from src.observation.materialized_invocation_result_witness_v0 import (
    MaterializedInvocationResultWitnessError,
    build_materialized_invocation_result_witness,
)
from tests.coordination.test_materialized_admitted_authority_consumption_v0 import (
    exact_fixture,
)


def valid_materialized_consumption():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        successor, spec, unit, env, store, admission = exact_fixture(root)
        ticks = iter([
            "2026-09-26T01:00:01Z",
            "2026-09-26T01:00:02Z",
        ])
        raw = {
            "fixture_result": "SUCCESS",
            "count": 1,
            "work_item_id": unit["identity"]["work_item_id"],
        }
        consumed = consume_materialized_admitted_authority_once(
            admission_receipt=admission,
            successor_candidate=successor,
            work_spec=spec,
            materialized_unit=unit,
            authority_envelope=env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=store,
            invoke=lambda: raw,
            clock=lambda: next(ticks),
        )
        return successor, spec, unit, consumed["receipt"], raw


class MaterializedInvocationResultWitnessV0Tests(unittest.TestCase):
    def build(self, **changes):
        successor, spec, unit, receipt, raw = valid_materialized_consumption()
        args = {
            "consumption_receipt": receipt,
            "raw_output": raw,
            "adapter_identity": "materialized-disposable-callback-adapter-v0",
            "observer_limitations": [
                "callback return does not prove external consequence",
                "raw return is not semantically interpreted",
                "no settlement is performed",
            ],
            "model_identity": None,
        }
        args.update(changes)
        return successor, spec, unit, build_materialized_invocation_result_witness(**args)

    def test_fixed_inputs_are_deterministic(self):
        _, _, _, one = self.build()
        _, _, _, two = self.build()
        self.assertEqual(one, two)

    def test_exact_materialized_lineage_is_bound(self):
        successor, spec, unit, witness = self.build()
        self.assertEqual(witness["successor_id"], successor["successor_id"])
        self.assertEqual(
            witness["successor_integrity_sha256"],
            successor["integrity_sha256"],
        )
        self.assertEqual(witness["work_spec_id"], spec["work_spec_id"])
        self.assertEqual(
            witness["work_spec_integrity_sha256"],
            spec["integrity_sha256"],
        )
        self.assertEqual(
            witness["materialized_work_item_id"],
            unit["identity"]["work_item_id"],
        )
        self.assertEqual(
            witness["materialized_unit_integrity_sha256"],
            unit["integrity_sha256"],
        )

    def test_raw_output_is_preserved_and_identity_bound(self):
        _, _, _, witness = self.build()
        self.assertEqual(
            witness["raw_output"]["fixture_result"],
            "SUCCESS",
        )
        self.assertEqual(len(witness["raw_output_sha256"]), 64)
        self.assertIn(
            '"fixture_result":"SUCCESS"',
            witness["raw_output_canonical_json"],
        )

    def test_output_change_changes_witness_identity(self):
        _, _, _, one = self.build(raw_output={"value": 1})
        _, _, _, two = self.build(raw_output={"value": 2})
        self.assertNotEqual(one["raw_output_sha256"], two["raw_output_sha256"])
        self.assertNotEqual(one["witness_id"], two["witness_id"])

    def test_observer_limitation_change_changes_witness_identity(self):
        _, _, _, one = self.build(
            observer_limitations=["external effect unresolved"]
        )
        _, _, _, two = self.build(
            observer_limitations=["external effect not observed"]
        )
        self.assertNotEqual(one["witness_id"], two["witness_id"])

    def test_missing_model_identity_remains_unresolved(self):
        _, _, _, witness = self.build()
        self.assertIsNone(witness["model_identity"])
        self.assertIn("model_identity", witness["unresolved_fields"])
        self.assertNotIn("model_identity", witness["measured_fields"])

    def test_supplied_model_identity_is_measured(self):
        _, _, _, witness = self.build(model_identity="fixture/model-v0")
        self.assertEqual(witness["model_identity"], "fixture/model-v0")
        self.assertIn("model_identity", witness["measured_fields"])
        self.assertNotIn("model_identity", witness["unresolved_fields"])

    def test_tampered_consumption_receipt_is_rejected(self):
        _, _, _, receipt, raw = valid_materialized_consumption()
        tampered = deepcopy(receipt)
        tampered["work_spec_id"] = "successor-work-spec:sha256:" + "9" * 64
        with self.assertRaisesRegex(
            MaterializedInvocationResultWitnessError,
            "consumption receipt identity mismatch",
        ):
            build_materialized_invocation_result_witness(
                consumption_receipt=tampered,
                raw_output=raw,
                adapter_identity="adapter-v0",
                observer_limitations=["no settlement"],
            )

    def test_unconsumed_receipt_is_rejected(self):
        _, _, _, receipt, raw = valid_materialized_consumption()
        altered = deepcopy(receipt)
        altered["authority_consumed"] = False
        with self.assertRaisesRegex(
            MaterializedInvocationResultWitnessError,
            "authority_consumed=true",
        ):
            build_materialized_invocation_result_witness(
                consumption_receipt=altered,
                raw_output=raw,
                adapter_identity="adapter-v0",
                observer_limitations=["no settlement"],
            )

    def test_non_json_output_is_rejected(self):
        _, _, _, receipt, _ = valid_materialized_consumption()
        with self.assertRaisesRegex(
            MaterializedInvocationResultWitnessError,
            "canonical-JSON serializable",
        ):
            build_materialized_invocation_result_witness(
                consumption_receipt=receipt,
                raw_output={1, 2, 3},
                adapter_identity="adapter-v0",
                observer_limitations=["no settlement"],
            )

    def test_inputs_are_not_mutated(self):
        _, _, _, receipt, raw = valid_materialized_consumption()
        limitations = ["no settlement"]
        before = (deepcopy(receipt), deepcopy(raw), deepcopy(limitations))
        build_materialized_invocation_result_witness(
            consumption_receipt=receipt,
            raw_output=raw,
            adapter_identity="adapter-v0",
            observer_limitations=limitations,
        )
        self.assertEqual(receipt, before[0])
        self.assertEqual(raw, before[1])
        self.assertEqual(limitations, before[2])

    def test_no_interpretation_settlement_or_standing_is_created(self):
        _, _, _, witness = self.build()
        self.assertEqual(witness["semantic_interpretation"], "NONE")
        self.assertEqual(witness["settlement_effect"], "NONE")
        self.assertEqual(witness["authority_effect"], "NONE")
        self.assertEqual(witness["execution_effect"], "NONE")
        self.assertEqual(witness["scientific_standing_effect"], "NONE")
        self.assertFalse(witness["external_effect_inferred"])


if __name__ == "__main__":
    unittest.main()
