from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
HARNESS_PATH = ROOT / "tools" / "edge_source_standing_held_out_realization_v0.py"

spec = importlib.util.spec_from_file_location(
    "edge_source_standing_held_out_realization_v0",
    HARNESS_PATH,
)
assert spec is not None
assert spec.loader is not None
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class EdgeSourceStandingHeldOutRealizationHarnessV0Tests(unittest.TestCase):
    """Administrative/static tests only.

    These tests MUST NOT invoke SourceStandingEvaluatorV0.derive and therefore
    MUST NOT consume the held-out scientific cells.
    """

    def test_preflight_does_not_import_or_invoke_evaluator(self):
        with mock.patch.object(
            harness.importlib,
            "import_module",
            side_effect=AssertionError("preflight imported evaluator"),
        ):
            fixture = harness.administration_preflight(ROOT)

        self.assertEqual(
            fixture["scientific_question_id"],
            harness.QUESTION_ID,
        )
        self.assertEqual(
            set(fixture["cells"]),
            set(harness.CELL_ORDER),
        )

    def test_evaluator_kwargs_are_raw_and_oracle_free(self):
        fixture = harness.administration_preflight(ROOT)

        expected_keys = {
            "claim_artifact_bytes",
            "expected_claim_sha256",
            "expected_claim_artifact_id",
            "source_ref",
            "from_ref",
            "relation_type",
            "to_ref",
            "standing_basis_bytes",
            "grounding_signature",
        }

        for label in harness.CELL_ORDER:
            kwargs = harness._derive_kwargs(
                fixture,
                fixture["cells"][label],
            )
            self.assertEqual(set(kwargs), expected_keys)
            self.assertTrue(
                set(kwargs).isdisjoint(
                    harness.FORBIDDEN_EVALUATOR_INPUT_KEYS
                )
            )

    def test_exact_claim_bytes_are_reused_across_all_cells(self):
        fixture = harness.administration_preflight(ROOT)
        claim_bytes = [
            harness._derive_kwargs(
                fixture,
                fixture["cells"][label],
            )["claim_artifact_bytes"]
            for label in harness.CELL_ORDER
        ]

        self.assertTrue(claim_bytes)
        self.assertTrue(all(item == claim_bytes[0] for item in claim_bytes))
        self.assertEqual(
            harness._sha256_hex(claim_bytes[0]),
            harness.CLAIM_SHA256,
        )

    def test_h1_is_the_only_absent_standing_input(self):
        fixture = harness.administration_preflight(ROOT)

        for label in harness.CELL_ORDER:
            kwargs = harness._derive_kwargs(
                fixture,
                fixture["cells"][label],
            )
            if label == "H1":
                self.assertIsNone(kwargs["standing_basis_bytes"])
                self.assertIsNone(kwargs["grounding_signature"])
            else:
                self.assertIsInstance(kwargs["standing_basis_bytes"], bytes)
                self.assertIsInstance(kwargs["grounding_signature"], bytes)

    def test_harness_contains_no_scientific_answer_vector(self):
        source = HARNESS_PATH.read_text(encoding="utf-8")

        self.assertNotIn("SOURCE_STANDING_ESTABLISHED", source)
        self.assertNotIn("SOURCE_STANDING_NOT_ESTABLISHED", source)
        self.assertNotIn('"P1": "ESTABLISHED"', source)
        self.assertNotIn('"H1": "NOT_ESTABLISHED"', source)

    def test_grounding_private_key_is_not_in_grounding_root(self):
        fixture = harness.administration_preflight(ROOT)
        grounding_root = fixture["grounding_root"]

        self.assertIs(grounding_root["private_key_retained"], False)
        self.assertNotIn("private_key_hex", grounding_root)


if __name__ == "__main__":
    unittest.main()
