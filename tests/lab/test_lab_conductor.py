import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "lab_conductor.py"
spec = importlib.util.spec_from_file_location("lab_conductor", MODULE_PATH)
lab_conductor = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["lab_conductor"] = lab_conductor
spec.loader.exec_module(lab_conductor)


class LabConductorTests(unittest.TestCase):
    def make_root(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / "lab/events").mkdir(parents=True)
        (root / "lab/state").mkdir(parents=True)
        (root / "lab/processes").mkdir(parents=True)
        (root / "lab/events/events.jsonl").write_text("", encoding="utf-8")
        process = json.loads(
            (
                Path(__file__).resolve().parents[2]
                / "lab/processes/LP001_CONDUCTOR_FIXTURE_v0.json"
            ).read_text()
        )
        (root / "lab/processes/p.json").write_text(
            json.dumps(process), encoding="utf-8"
        )
        paths = lab_conductor.Paths(
            root / "lab/events/events.jsonl",
            root / "lab/state/LAB_STATE_v0.json",
            root / "lab/processes",
        )
        return tmp, root, paths

    def test_mechanical_advance_stops_at_role_judgment(self):
        tmp, _, paths = self.make_root()
        self.addCleanup(tmp.cleanup)
        state = lab_conductor.advance("LP-001-CONDUCTOR-FIXTURE", paths, set())
        proc = state["processes"]["LP-001-CONDUCTOR-FIXTURE"]
        self.assertEqual(proc["phase"], "CONTRACT_AVAILABLE")
        self.assertEqual(proc["status"], "ROLE_JUDGMENT_REQUIRED")
        self.assertEqual(proc["pending_role"], "COMMANDER")
        self.assertFalse(proc["scientific_standing"]["tracked"])

    def test_replay_reconstructs_state_without_executing_transitions(self):
        tmp, _, paths = self.make_root()
        self.addCleanup(tmp.cleanup)
        lab_conductor.advance("LP-001-CONDUCTOR-FIXTURE", paths, set())
        before = paths.events.read_text(encoding="utf-8")
        state = lab_conductor.replay(paths)
        after = paths.events.read_text(encoding="utf-8")
        self.assertEqual(before, after)
        self.assertEqual(
            state["processes"]["LP-001-CONDUCTOR-FIXTURE"]["phase"],
            "CONTRACT_AVAILABLE",
        )

    def test_event_log_distinguishes_requested_started_succeeded(self):
        tmp, _, paths = self.make_root()
        self.addCleanup(tmp.cleanup)
        lab_conductor.advance("LP-001-CONDUCTOR-FIXTURE", paths, set())
        events = list(lab_conductor.iter_events(paths.events))
        types = [e["event_type"] for e in events]
        self.assertIn("TRANSITION_REQUESTED", types)
        self.assertIn("TRANSITION_STARTED", types)
        self.assertIn("TRANSITION_SUCCEEDED", types)

    def test_packet_validation_never_accepts_claim(self):
        packet = {
            "schema_version": "lab_packet_v0",
            "packet_id": "P-1",
            "packet_type": "ROLE_OUTPUT",
            "process_id": "X",
            "sender_role": "SOL_B",
            "recipient_role": "SOL_A",
            "basis": {"repo": "R", "ref": "abc", "inputs": []},
            "requested_transition": "COMPRESS",
            "authority": {
                "required": False,
                "present": False,
                "decision_id": None,
            },
            "status": "PROPOSED",
            "claim_status": "UNADJUDICATED",
            "payload": {"claim": "something"},
            "receipts": [],
        }
        self.assertEqual(lab_conductor.validate_packet(packet), [])
        packet["claim_status"] = "ACCEPTED"
        self.assertTrue(lab_conductor.validate_packet(packet))

    def test_human_decision_object_is_self_contained(self):
        tmp, _, paths = self.make_root()
        self.addCleanup(tmp.cleanup)
        lab_conductor.ensure_registered("LP-001-CONDUCTOR-FIXTURE", paths)
        lab_conductor.append_event(
            paths.events,
            {
                "event_type": "TRANSITION_SUCCEEDED",
                "process_id": "LP-001-CONDUCTOR-FIXTURE",
                "transition_id": "COMMANDER_FREEZE_REVIEW",
                "to_phase": "READY_FOR_AUTHORIZATION",
            },
        )
        state = lab_conductor.advance("LP-001-CONDUCTOR-FIXTURE", paths, set())
        decision = state["processes"]["LP-001-CONDUCTOR-FIXTURE"][
            "pending_decision"
        ]
        self.assertEqual(
            decision["decision_id"], "DEC-LP001-FIXTURE-EXECUTION"
        )
        self.assertIn("authority_requested", decision)
        self.assertIn("allowed_choices", decision)
        self.assertIn("consequences", decision)
        self.assertIn("unchanged", decision)

    def test_missing_capability_blocks_without_side_effect_execution(self):
        tmp, _, paths = self.make_root()
        self.addCleanup(tmp.cleanup)
        lab_conductor.ensure_registered("LP-001-CONDUCTOR-FIXTURE", paths)
        lab_conductor.append_event(
            paths.events,
            {
                "event_type": "TRANSITION_SUCCEEDED",
                "process_id": "LP-001-CONDUCTOR-FIXTURE",
                "transition_id": "COMMANDER_FREEZE_REVIEW",
                "to_phase": "READY_FOR_AUTHORIZATION",
            },
        )
        lab_conductor.advance("LP-001-CONDUCTOR-FIXTURE", paths, set())
        lab_conductor.record_decision(
            "LP-001-CONDUCTOR-FIXTURE",
            "DEC-LP001-FIXTURE-EXECUTION",
            "APPROVE",
            paths,
        )
        state = lab_conductor.advance("LP-001-CONDUCTOR-FIXTURE", paths, set())
        proc = state["processes"]["LP-001-CONDUCTOR-FIXTURE"]
        self.assertEqual(proc["status"], "BLOCKED")
        self.assertEqual(
            proc["blocker"]["missing_capability"], "isolated_gpt_5_6_sol_high"
        )


if __name__ == "__main__":
    unittest.main()
