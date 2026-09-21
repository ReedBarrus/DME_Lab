from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path
import unittest

from tools import seat_engagement_handshake_v0 as seh


ROOT = Path(__file__).parents[2]
FIXTURES = (
    ROOT
    / "docs"
    / "candidates"
    / "seat_engagement_handshake_v0"
    / "fixtures"
    / "RAW_FIXTURES_v0.json"
)
KEY = (
    ROOT
    / "docs"
    / "candidates"
    / "seat_engagement_handshake_v0"
    / "fixtures"
    / "EVALUATION_KEY_v0.json"
)


class SeatEngagementHandshake001Pressure(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = seh.load_json(FIXTURES)
        self.key = seh.load_json(KEY)
        seh.validate_fixture_manifest(self.fixture)
        seh.validate_evaluation_key(self.key)

    def result(self, cell_id: str) -> dict:
        return seh.run_cell(self.fixture, cell_id)

    def test_contract_cells_are_exact_and_raw_key_are_separate(self) -> None:
        self.assertEqual(
            tuple(self.fixture["cells"]),
            ("A", "B", "C1", "C2", "D", "E", "F", "G", "G2", "H", "I"),
        )
        self.assertEqual(tuple(self.key["cells"]), tuple(self.fixture["cells"]))
        self.assertEqual(
            tuple(inspect.signature(seh.run_cell).parameters),
            ("fixture", "cell_id"),
        )
        source = inspect.getsource(seh.run_cell)
        self.assertNotIn("evaluation_key", source)
        for cell in self.fixture["cells"].values():
            rendered = json.dumps(cell, sort_keys=True)
            self.assertNotIn('"expected_', rendered)
            self.assertNotIn('"pass"', rendered)

    def test_schema_files_preserve_closed_grammars(self) -> None:
        schema_root = ROOT / "schemas"
        schemas = {
            "seat_engagement_envelope_v0.schema.json": "seat_engagement_envelope_v0",
            "seat_engagement_decision_v0.schema.json": "seat_engagement_decision_v0",
            "seat_engagement_work_unit_binding_v0.schema.json": "seat_engagement_work_unit_binding_v0",
            "seat_engagement_pre_mutation_disposition_v0.schema.json": "seat_engagement_pre_mutation_disposition_v0",
        }
        for name, schema_id in schemas.items():
            value = json.loads((schema_root / name).read_text(encoding="utf-8"))
            self.assertEqual(value["type"], "object")
            self.assertFalse(value["additionalProperties"])
            self.assertEqual(value["properties"]["schema"]["const"], schema_id)
        decision = json.loads(
            (schema_root / "seat_engagement_decision_v0.schema.json").read_text()
        )
        self.assertEqual(
            decision["properties"]["decision"]["enum"],
            ["ACCEPT", "DECLINE", "REFUSE", "CONTEXT_REQUEST"],
        )
        disposition = json.loads(
            (
                schema_root
                / "seat_engagement_pre_mutation_disposition_v0.schema.json"
            ).read_text()
        )
        self.assertEqual(
            disposition["properties"]["disposition"]["enum"],
            list(seh.PRE_MUTATION_DISPOSITIONS),
        )

    def test_a_clean_engagement_executes_exactly_one_successful_unit(self) -> None:
        result = self.result("A")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["engagement_decision"], "ACCEPT")
        self.assertEqual(obs["pre_mutation_disposition"], "READY_FOR_AUTHORIZED_UNIT")
        self.assertTrue(obs["effect_started"])
        self.assertEqual(obs["grant_state"], "CONSUMED")
        self.assertEqual(obs["terminal_receipt"], "SUCCESS")
        self.assertTrue(obs["checkpointed"])
        self.assertTrue(obs["released"])
        self.assertFalse(obs["second_unit_started"])

    def test_b_decline_stops_before_binding(self) -> None:
        result = self.result("B")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["engagement_decision"], "DECLINE")
        self.assertFalse(obs["binding_present"])
        self.assertFalse(obs["work_claim_present"])
        self.assertFalse(obs["effect_started"])

    def test_c1_wrong_seat_refuses(self) -> None:
        result = self.result("C1")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["engagement_decision"], "REFUSE")
        self.assertEqual(obs["engagement_reason"], "TARGET_SEAT_MISMATCH")
        self.assertFalse(obs["binding_present"])

    def test_c2_invalid_candidate_relation_refuses(self) -> None:
        result = self.result("C2")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["engagement_decision"], "REFUSE")
        self.assertEqual(obs["engagement_reason"], "EVALUATOR_BINDING_INVALID")
        self.assertFalse(obs["binding_present"])

    def test_d_established_collision_requests_coordination_without_inference(self) -> None:
        result = self.result("D")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["engagement_decision"], "ACCEPT")
        self.assertEqual(obs["pre_mutation_disposition"], "COORDINATION_REQUEST")
        self.assertFalse(obs["effect_started"])
        peer = next(e for e in result["events"] if e["event_type"] == "PEER_EVIDENCE")
        self.assertEqual(peer["payload"]["state"], "ESTABLISHED_COLLISION")
        self.assertEqual(
            peer["payload"]["established_relation"],
            "SEMANTIC_OR_PROVENANCE_COLLISION",
        )
        self.assertFalse(peer["payload"]["inference_performed_by_seat"])

    def test_e_missing_authority_requests_authority(self) -> None:
        result = self.result("E")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["pre_mutation_disposition"], "AUTHORITY_REQUEST")
        self.assertEqual(obs["grant_state"], "ABSENT")
        self.assertFalse(obs["effect_started"])

    def test_f_missing_basis_requests_context_before_binding(self) -> None:
        result = self.result("F")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["engagement_decision"], "CONTEXT_REQUEST")
        self.assertEqual(obs["engagement_reason"], "MISSING_REQUIRED_BASIS")
        self.assertFalse(obs["binding_present"])
        self.assertFalse(obs["work_claim_present"])
        self.assertFalse(obs["effect_started"])
        self.assertFalse(
            any(e["event_type"] == "PRE_MUTATION_DISPOSITION" for e in result["events"])
        )

    def test_g_grant_consumes_at_effect_start_before_success_receipt(self) -> None:
        result = self.result("G")
        self.assertTrue(seh.score_cell(result, self.key))
        types = [event["event_type"] for event in result["events"]]
        start = types.index("EFFECT_BEARING_UNIT_START")
        consumed = types.index("ONE_UNIT_AUTHORITY_CONSUMED")
        receipt = types.index("TERMINAL_RECEIPT")
        self.assertLess(start, consumed)
        self.assertLess(consumed, receipt)
        self.assertEqual(result["observables"]["grant_state"], "CONSUMED")
        self.assertFalse(result["observables"]["second_unit_started"])
        self.assertIn("SECOND_UNIT_BLOCKED", types)

    def test_validation_failure_before_effect_does_not_consume_grant(self) -> None:
        envelope = copy.deepcopy(self.fixture["base_envelope"])
        candidate = copy.deepcopy(self.fixture["base_candidate"])
        decision = seh.evaluate_engagement(envelope, candidate)
        binding = seh.materialize_binding(envelope, candidate, decision)
        claim = seh.materialize_work_claim(envelope, binding)
        grant = copy.deepcopy(self.fixture["valid_grant"])
        disposition = seh.pre_mutation_disposition(
            envelope=envelope,
            candidate=candidate,
            binding=binding,
            work_claim=claim,
            peer_state="CLEAR",
            grant=grant,
            basis_state="INSUFFICIENT",
        )
        self.assertEqual(disposition["disposition"], "CONTEXT_REQUEST")
        self.assertEqual(grant["state"], "AVAILABLE")
        with self.assertRaises(seh.HandshakeError):
            seh.begin_effect(
                envelope=envelope,
                binding=binding,
                disposition=disposition,
                grant=grant,
            )
        self.assertEqual(grant["state"], "AVAILABLE")

    def test_g2_failure_preserves_consumed_authority_and_failure_history(self) -> None:
        result = self.result("G2")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["terminal_receipt"], "FAILURE")
        self.assertEqual(obs["grant_state"], "CONSUMED")
        self.assertTrue(obs["checkpointed"])
        self.assertTrue(obs["released"])
        replay = seh.replay_events(result["events"])
        self.assertEqual(replay["terminal_receipt"], "FAILURE")
        self.assertEqual(replay["grant_state"], "CONSUMED")
        self.assertTrue(replay["checkpointed"])
        self.assertTrue(replay["released"])

    def test_h_recovery_does_not_inherit_historical_authority(self) -> None:
        raw_h = self.fixture["cells"]["H"]["recovery"]
        self.assertEqual(raw_h["historical_authority_ref"], "HISTORICAL-ONE-UNIT-GRANT")
        result = self.result("H")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["engagement_decision"], "ACCEPT")
        self.assertEqual(obs["pre_mutation_disposition"], "AUTHORITY_REQUEST")
        self.assertEqual(obs["grant_state"], "ABSENT")
        self.assertFalse(obs["effect_started"])
        self.assertTrue(obs["checkpointed"])
        recovery = next(
            e for e in result["events"] if e["event_type"] == "RECOVERY_BASIS_RETAINED"
        )
        self.assertEqual(recovery["payload"]["authority_effect"], "NONE")

    def test_i_momentum_does_not_start_second_unit(self) -> None:
        result = self.result("I")
        self.assertTrue(seh.score_cell(result, self.key))
        obs = result["observables"]
        self.assertEqual(obs["grant_state"], "CONSUMED")
        self.assertTrue(obs["checkpointed"])
        self.assertTrue(obs["released"])
        self.assertFalse(obs["second_unit_started"])
        self.assertIn(
            result["secondary_observables"]["authority_request_emitted"],
            {True, False},
        )
        self.assertEqual(
            self.key["secondary_observables"]["I"]["authority_request_emitted"],
            "UNSCORED",
        )

    def test_binding_claim_and_ready_do_not_manufacture_authority(self) -> None:
        result = self.result("E")
        binding = next(e for e in result["events"] if e["event_type"] == "WORK_UNIT_BINDING")
        claim = next(e for e in result["events"] if e["event_type"] == "WORK_CLAIM")
        disp = next(
            e for e in result["events"] if e["event_type"] == "PRE_MUTATION_DISPOSITION"
        )
        self.assertEqual(binding["payload"]["authority_effect"], "NONE")
        self.assertEqual(claim["payload"]["authority_effect"], "NONE")
        self.assertEqual(disp["payload"]["authority_effect"], "NONE")
        self.assertEqual(disp["payload"]["execution_effect"], "NONE")

    def test_ready_disposition_requires_separate_corresponding_grant(self) -> None:
        envelope = copy.deepcopy(self.fixture["base_envelope"])
        candidate = copy.deepcopy(self.fixture["base_candidate"])
        decision = seh.evaluate_engagement(envelope, candidate)
        binding = seh.materialize_binding(envelope, candidate, decision)
        claim = seh.materialize_work_claim(envelope, binding)
        no_grant = seh.pre_mutation_disposition(
            envelope=envelope,
            candidate=candidate,
            binding=binding,
            work_claim=claim,
            peer_state="CLEAR",
            grant=None,
        )
        self.assertEqual(no_grant["disposition"], "AUTHORITY_REQUEST")
        grant = copy.deepcopy(self.fixture["valid_grant"])
        ready = seh.pre_mutation_disposition(
            envelope=envelope,
            candidate=candidate,
            binding=binding,
            work_claim=claim,
            peer_state="CLEAR",
            grant=grant,
        )
        self.assertEqual(ready["disposition"], "READY_FOR_AUTHORIZED_UNIT")
        self.assertEqual(ready["authority_effect"], "NONE")

    def test_revalidation_precedes_coordination_and_authority(self) -> None:
        envelope = copy.deepcopy(self.fixture["base_envelope"])
        candidate = copy.deepcopy(self.fixture["base_candidate"])
        decision = seh.evaluate_engagement(envelope, candidate)
        binding = seh.materialize_binding(envelope, candidate, decision)
        claim = seh.materialize_work_claim(envelope, binding)
        result = seh.pre_mutation_disposition(
            envelope=envelope,
            candidate=candidate,
            binding=binding,
            work_claim=claim,
            peer_state="ESTABLISHED_COLLISION",
            grant=None,
            coordinate_changed=True,
        )
        self.assertEqual(result["disposition"], "REVALIDATION_REQUIRED")

    def test_replay_reconstructs_primary_transition_state(self) -> None:
        for cell_id in self.fixture["cells"]:
            result = self.result(cell_id)
            replay = seh.replay_events(result["events"])
            obs = result["observables"]
            for field in (
                "engagement_decision",
                "binding_present",
                "work_claim_present",
                "pre_mutation_disposition",
                "effect_started",
                "grant_state",
                "terminal_receipt",
                "checkpointed",
                "released",
                "second_unit_started",
            ):
                self.assertEqual(replay[field], obs[field], (cell_id, field))

    def test_all_cells_match_frozen_primary_key(self) -> None:
        evidence = seh.qualify(self.fixture, self.key)
        self.assertTrue(evidence["all_primary_cells_pass"])
        self.assertEqual(evidence["model_invocations"], 0)
        self.assertEqual(evidence["real_seat_effect"], "NONE")
        self.assertEqual(evidence["real_occupant_effect"], "NONE")
        self.assertEqual(evidence["live_authority_effect"], "NONE")
        self.assertEqual(evidence["external_effect"], "NONE")
        self.assertTrue(all(row["pass"] for row in evidence["cells"].values()))

    def test_key_tamper_does_not_change_apparatus_output(self) -> None:
        baseline = self.result("D")
        bad_key = copy.deepcopy(self.key)
        bad_key["cells"]["D"]["pre_mutation_disposition"] = "READY_FOR_AUTHORIZED_UNIT"
        self.assertFalse(seh.score_cell(baseline, bad_key))
        self.assertEqual(
            baseline["observables"]["pre_mutation_disposition"],
            "COORDINATION_REQUEST",
        )

    def test_qualification_evidence_is_deterministic(self) -> None:
        a = seh.qualify(self.fixture, self.key)
        b = seh.qualify(self.fixture, self.key)
        self.assertEqual(seh.canonical_bytes(a), seh.canonical_bytes(b))
        for cell_id, row in a["cells"].items():
            self.assertEqual(
                row["events_sha256"],
                seh.sha256_bytes(seh.canonical_bytes(row["events"])),
                cell_id,
            )

    def test_no_model_network_scheduler_or_wake_surface(self) -> None:
        source = Path(seh.__file__).read_text(encoding="utf-8").lower()
        for forbidden in (
            "import openai",
            "import anthropic",
            "import requests",
            "import httpx",
            "import socket",
            "urllib.request",
            "chat.completions",
            "responses.create",
            "messages.create",
            "scheduler",
            "wake_opportunity",
            "leader election",
        ):
            self.assertNotIn(forbidden, source)

    def test_malformed_envelope_refuses_without_downstream_state(self) -> None:
        envelope = copy.deepcopy(self.fixture["base_envelope"])
        del envelope["target_seat_id"]
        candidate = copy.deepcopy(self.fixture["base_candidate"])
        decision = seh.evaluate_engagement(envelope, candidate)
        self.assertEqual(decision["decision"], "REFUSE")
        self.assertEqual(decision["reason_code"], "MALFORMED_ENVELOPE")
        with self.assertRaises(seh.HandshakeError):
            seh.materialize_binding(envelope, candidate, decision)

    def test_missing_required_capability_refuses(self) -> None:
        envelope = copy.deepcopy(self.fixture["base_envelope"])
        candidate = copy.deepcopy(self.fixture["base_candidate"])
        candidate["capabilities"] = ["CAP-SEAT-EVALUATE"]
        decision = seh.evaluate_engagement(envelope, candidate)
        self.assertEqual(decision["decision"], "REFUSE")
        self.assertEqual(decision["reason_code"], "REQUIRED_CAPABILITY_MISSING")


if __name__ == "__main__":
    unittest.main()
