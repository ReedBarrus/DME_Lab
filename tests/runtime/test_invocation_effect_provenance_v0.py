from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.invocation_effect_provenance_v0 import (
    AdministrationInvalid,
    SyntheticEffectHarness,
    candidate_emit,
    score_observation,
)


class InvocationEffectProvenanceV0Qualification(unittest.TestCase):
    def fixture(
        self,
        cell_id: str,
        *,
        tested: str = "QI1",
        actual: str = "QI1",
        authority: str = "VALID",
        claim_status: str = "ACTIVE",
        claim_invocation: str = "QI1",
        claim_work_unit: str = "QU1",
        candidate_claim_id: str | None = "QC1",
        candidate_work_unit: str = "QU1",
        candidate_mode: str = "EMIT",
        override: dict[str, str] | None = None,
        mutation_payload: str = "Q-STATE-1\n",
        expected_output_payload: str | None = None,
    ) -> dict:
        return {
            "cell_id": cell_id,
            "tested_invocation_id": tested,
            "effect_id": f"{cell_id}-EFFECT",
            "effect_kind": "SYNTHETIC_FILE_TRANSITION",
            "mutation_event_id": f"{cell_id}-MUTATION",
            "actual_actor_invocation_id": actual,
            "seat_id": "Q-SEAT",
            "occupant_id": "WORKSHOP",
            "candidate_claim_id": candidate_claim_id,
            "candidate_work_unit_id": candidate_work_unit,
            "authority_ref": f"{cell_id}-AUTH",
            "authority_state": authority,
            "claim_at_effect_start": {
                "claim_id": "QC1",
                "status": claim_status,
                "invocation_id": claim_invocation,
                "work_unit_id": claim_work_unit,
            },
            "tested_work_unit_id": "QU1",
            "initial_payload": "Q-STATE-0\n",
            "mutation_payload": mutation_payload,
            "entry_witness": f"{cell_id}-OPAQUE-ENTRY-WITNESS-0001",
            "candidate_mode": candidate_mode,
            "candidate_observation_override": override or {},
            "expected_output_payload": expected_output_payload,
            "object_refs": ["Q-TARGET"],
        }

    def execute(self, fixture: dict):
        with tempfile.TemporaryDirectory() as tmp:
            observation = SyntheticEffectHarness(Path(tmp)).execute(fixture)
        derived = score_observation(
            observation["ground_truth"],
            observation["candidate_output"],
        )
        return observation, derived

    def test_dummy_matched_effect_establishes_attribution_and_valid_exercise(self) -> None:
        observation, derived = self.execute(self.fixture("Q_MATCHED"))
        self.assertTrue(derived["EFFECT_EXISTS"])
        self.assertEqual(derived["INVOCATION_EFFECT_ATTRIBUTION"], "ESTABLISHED")
        self.assertEqual(derived["CLAIM_EXERCISE"], "VALID")
        self.assertEqual(derived["AUTHORIZATION_AT_EFFECT_START"], "VALID")
        self.assertEqual(derived["EFFECT_RESULT"], "SUCCESS")
        self.assertNotIn("entry_witness", observation["candidate_output"])
        self.assertNotIn("authority_state", observation["candidate_output"])

    def test_dummy_same_surface_other_invocation_is_unattributed_for_tested_actor(self) -> None:
        _, derived = self.execute(
            self.fixture(
                "Q_OTHER_INVOCATION",
                actual="QI2",
                candidate_claim_id=None,
            )
        )
        self.assertEqual(derived["INVOCATION_EFFECT_ATTRIBUTION"], "UNATTRIBUTED")
        self.assertEqual(derived["CLAIM_EXERCISE"], "UNESTABLISHED")

    def test_dummy_effect_without_candidate_provenance_is_unattributed(self) -> None:
        _, derived = self.execute(
            self.fixture(
                "Q_NO_PROVENANCE",
                actual="Q-UNBOUND",
                candidate_mode="NO_PROVENANCE",
                candidate_claim_id=None,
            )
        )
        self.assertTrue(derived["EFFECT_EXISTS"])
        self.assertEqual(derived["INVOCATION_EFFECT_ATTRIBUTION"], "UNATTRIBUTED")
        self.assertEqual(derived["CLAIM_EXERCISE"], "UNESTABLISHED")

    def test_dummy_wrong_pre_basis_is_invalid(self) -> None:
        _, derived = self.execute(
            self.fixture(
                "Q_WRONG_PRE",
                override={
                    "pre_coordinate": "sha256:fb403b7f4258077a415d973249af0622390526a32a955f1bb7ad4e0501332325"
                },
            )
        )
        self.assertEqual(derived["INVOCATION_EFFECT_ATTRIBUTION"], "INVALID")
        self.assertEqual(derived["CLAIM_EXERCISE"], "UNESTABLISHED")

    def test_dummy_wrong_post_coordinate_is_invalid(self) -> None:
        _, derived = self.execute(
            self.fixture(
                "Q_WRONG_POST",
                override={
                    "post_coordinate": "sha256:b5d415c5ddd48fa3149f1d50f836b4e9852c683ee8c4fd5de852c86ff710b11e"
                },
            )
        )
        self.assertEqual(derived["INVOCATION_EFFECT_ATTRIBUTION"], "INVALID")

    def test_dummy_matching_actor_wrong_claim_unit_is_invalid_exercise(self) -> None:
        _, derived = self.execute(
            self.fixture(
                "Q_WRONG_CLAIM_UNIT",
                claim_work_unit="QU2",
            )
        )
        self.assertEqual(derived["INVOCATION_EFFECT_ATTRIBUTION"], "ESTABLISHED")
        self.assertEqual(derived["CLAIM_EXERCISE"], "INVALID")

    def test_dummy_authority_absent_and_consumed_are_not_strengthened(self) -> None:
        for state in ("ABSENT", "CONSUMED"):
            with self.subTest(state=state):
                _, derived = self.execute(self.fixture(f"Q_AUTH_{state}", authority=state))
                self.assertEqual(derived["INVOCATION_EFFECT_ATTRIBUTION"], "ESTABLISHED")
                self.assertEqual(derived["CLAIM_EXERCISE"], "VALID")
                self.assertEqual(derived["AUTHORIZATION_AT_EFFECT_START"], state)

    def test_dummy_correct_output_by_other_invocation_does_not_validate_tested_claim(self) -> None:
        fixture = self.fixture(
            "Q_CORRECT_OTHER",
            actual="QI2",
            candidate_claim_id=None,
            mutation_payload="Q-EXPECTED\n",
            expected_output_payload="Q-EXPECTED\n",
        )
        _, derived = self.execute(fixture)
        self.assertTrue(derived["OUTPUT_MATCH"])
        self.assertEqual(derived["INVOCATION_EFFECT_ATTRIBUTION"], "UNATTRIBUTED")
        self.assertEqual(derived["CLAIM_EXERCISE"], "UNESTABLISHED")

    def test_candidate_input_rejects_answer_key_fields(self) -> None:
        candidate_input = {
            "schema": "invocation_effect_candidate_input_v0",
            "invocation_binding": {
                "seat_id": "Q-SEAT",
                "occupant_id": "WORKSHOP",
                "invocation_id": "QI1",
                "claim_id": "QC1",
                "work_unit_id": "QU1",
                "authority_ref": "Q-AUTH",
            },
            "effect_observation": {
                "effect_id": "Q-E",
                "effect_kind": "SYNTHETIC_FILE_TRANSITION",
                "mutation_event_id": "Q-M",
                "pre_coordinate": "sha256:" + "0" * 64,
                "post_coordinate": "sha256:" + "1" * 64,
                "object_refs": ["Q-TARGET"],
                "entry_witness": "Q-OPAQUE-ENTRY-WITNESS",
            },
            "expected_attribution": "ESTABLISHED",
        }
        with self.assertRaises(AdministrationInvalid):
            candidate_emit(candidate_input)


if __name__ == "__main__":
    unittest.main()
