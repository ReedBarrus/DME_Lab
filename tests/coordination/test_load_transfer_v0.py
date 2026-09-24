from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.coordination import load_transfer_v0 as lt


def sealed_frame(frame_id: str = "FRAME-LT001-001", *, status: str = lt.FRAME_OPERATIVE):
    frame = {
        "object_type": lt.FRAME_TYPE,
        "frame_id": frame_id,
        "created_at": "2026-09-24T12:30:00Z",
        "repo_ref": "draci-v0-candidate-basis",
        "repo_head": "1fe16a8d5c7566397b9d2474d43cb43786589fdc",
        "target": "Transfer one bounded development handoff out of Reed.",
        "qualified_standing": "CANDIDATE_ONLY",
        "active_horizon": "LOAD_TRANSFER_001",
        "unresolved_load": [
            "Run first two-seat handoff pressure.",
            "Legacy bridge manifest mismatch remains unresolved and out of scope.",
        ],
        "authority_posture": "Reed retains all human approval/promotion authority.",
        "available_surfaces": [
            "repository-carried coordination state",
            "bounded repo-local candidate work",
            "read-only source inspection",
        ],
        "current_work_item_ids": ["LT001-W1"],
        "explicitly_noncurrent": [
            "automatic scheduler",
            "automatic qualification",
            "automatic authority",
        ],
        "source_handles": [
            "PROJECT_STATE.md",
            "OPERATIVE_SURFACE_MAP.md",
            "LOAD_TRANSFER_001 implementation packet",
        ],
        "claim_ceiling": "One bounded repo-local coordination handoff only.",
        "status": status,
        "superseded_by": None,
        "integrity_sha256": "",
    }
    if status == lt.FRAME_SUPERSEDED:
        frame["superseded_by"] = "FRAME-LT001-002"
    return lt.seal_object(frame)


def sealed_work(
    *,
    frame_id: str = "FRAME-LT001-001",
    role: str = "IMPLEMENTER",
    status: str = "QUEUED",
):
    item = {
        "object_type": lt.WORK_ITEM_TYPE,
        "work_item_id": "LT001-W1",
        "created_at": "2026-09-24T12:31:00Z",
        "created_from_frame_id": frame_id,
        "status": status,
        "role": role,
        "source_objects": [
            "docs/campaigns/load_transfer_001/CURRENT_OPERATIVE_FRAME_V0.json"
        ],
        "required_handoff_ids": [],
        "requested_transformation": (
            "Create one bounded candidate note describing the exact observed "
            "coordination load and no more."
        ),
        "allowed_consequences": [
            "create or edit one repository-local candidate artifact"
        ],
        "forbidden_consequences": [
            "trust-root mutation",
            "authority issuance",
            "scientific promotion",
            "automatic next-seat invocation",
            "automatic retry",
        ],
        "required_evidence": [
            "operative frame",
            "work-item contract",
        ],
        "required_output": "one sealed repository-local candidate artifact",
        "claim_ceiling": "Candidate artifact only; no standing or authority effect.",
        "stop_condition": "Stop immediately after bounded output and handoff receipt.",
        "authority_requirement": "NONE",
        "budget_requirement": "ONE_BOUNDED_REPO_TRANSFORMATION",
        "next_destination_if_complete": "LT001-W2-REVIEWER",
        "next_destination_if_unresolved": "UNRESOLVED",
        "claimed_by": None,
        "claimed_at": None,
        "completed_at": None,
        "result_posture": None,
        "output_object_identities": [],
        "integrity_sha256": "",
    }
    return lt.seal_object(item)


def sealed_output(text: str = "bounded output"):
    return lt.seal_object(
        {
            "object_type": "LOAD_TRANSFER_001_CANDIDATE_OUTPUT",
            "content": text,
            "integrity_sha256": "",
        }
    )


class LoadTransferV0Tests(unittest.TestCase):
    def test_t01_valid_frame_parses(self):
        frame = sealed_frame()
        observed = lt.read_current_frame(frame)
        self.assertEqual(observed["frame_id"], "FRAME-LT001-001")

    def test_t02_missing_load_bearing_frame_field_fails_closed(self):
        frame = sealed_frame()
        del frame["authority_posture"]
        with self.assertRaises(lt.CoordinationError):
            lt.read_current_frame(frame)

    def test_t03_queued_work_item_can_be_claimed_once(self):
        frame = sealed_frame()
        item = sealed_work()
        claimed = lt.claim_work_item(
            frame,
            item,
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        self.assertEqual(claimed["status"], "CLAIMED")
        with self.assertRaises(lt.WorkItemRejected):
            lt.claim_work_item(
                frame,
                claimed,
                seat_id="SEAT-A",
                seat_role="IMPLEMENTER",
                claimed_at="2026-09-24T12:33:00Z",
            )

    def test_t04_stale_frame_id_rejects_claim(self):
        with self.assertRaisesRegex(lt.WorkItemRejected, "STALE_FRAME_ID"):
            lt.claim_work_item(
                sealed_frame(),
                sealed_work(frame_id="FRAME-OLD"),
                seat_id="SEAT-A",
                seat_role="IMPLEMENTER",
                claimed_at="2026-09-24T12:32:00Z",
            )

    def test_t05_second_seat_cannot_claim_claimed_item(self):
        frame = sealed_frame()
        claimed = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        with self.assertRaises(lt.WorkItemRejected):
            lt.claim_work_item(
                frame,
                claimed,
                seat_id="SEAT-B",
                seat_role="IMPLEMENTER",
                claimed_at="2026-09-24T12:33:00Z",
            )

    def test_reviewer_item_waits_for_exact_predecessor_handoff(self):
        frame = sealed_frame()
        frame["current_work_item_ids"].append("LT001-W2")
        frame = lt.seal_object(frame)
        reviewer = sealed_work(role="REVIEWER")
        reviewer["work_item_id"] = "LT001-W2"
        reviewer["required_handoff_ids"] = ["LT001-H1"]
        reviewer = lt.seal_object(reviewer)

        with self.assertRaisesRegex(lt.WorkItemRejected, "REQUIRED_HANDOFF_UNAVAILABLE"):
            lt.claim_work_item(
                frame,
                reviewer,
                seat_id="SEAT-B",
                seat_role="REVIEWER",
                claimed_at="2026-09-24T12:35:00Z",
            )

        implementer = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        _, h1 = lt.complete_work_item(
            frame,
            implementer,
            seat_id="SEAT-A",
            completed_at="2026-09-24T12:34:00Z",
            result_posture="COMPLETED",
            output_objects=[sealed_output()],
            unresolved=[],
            stop_reason="done",
            handoff_id="LT001-H1",
        )
        claimed_reviewer = lt.claim_work_item(
            frame,
            reviewer,
            seat_id="SEAT-B",
            seat_role="REVIEWER",
            claimed_at="2026-09-24T12:35:00Z",
            available_handoffs=[h1],
        )
        self.assertEqual(claimed_reviewer["status"], "CLAIMED")

    def test_t06_completion_emits_exact_input_output_identities(self):
        frame = sealed_frame()
        claimed = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        output = sealed_output()
        completed, receipt = lt.complete_work_item(
            frame,
            claimed,
            seat_id="SEAT-A",
            completed_at="2026-09-24T12:34:00Z",
            result_posture="COMPLETED",
            output_objects=[output],
            unresolved=[],
            challenge_handles=["artifact://LT001-O1"],
            stop_reason="bounded transformation complete",
            handoff_id="LT001-H1",
        )
        self.assertEqual(
            completed["output_object_identities"], [output["integrity_sha256"]]
        )
        self.assertEqual(
            receipt["output_object_identities"], [output["integrity_sha256"]]
        )
        self.assertIn(frame["integrity_sha256"], receipt["input_object_identities"])
        self.assertIn(claimed["integrity_sha256"], receipt["input_object_identities"])

    def test_t07_handoff_grants_no_authority(self):
        frame = sealed_frame()
        claimed = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        _, receipt = lt.complete_work_item(
            frame,
            claimed,
            seat_id="SEAT-A",
            completed_at="2026-09-24T12:34:00Z",
            result_posture="COMPLETED",
            output_objects=[sealed_output()],
            unresolved=[],
            stop_reason="done",
            handoff_id="LT001-H1",
        )
        self.assertEqual(receipt["authority_effect"], "NONE")
        tampered = copy.deepcopy(receipt)
        tampered["authority_effect"] = "GRANTED"
        tampered = lt.seal_object(tampered)
        with self.assertRaises(lt.HandoffUnresolved):
            lt.validate_handoff(tampered)

    def test_t08_unresolved_next_destination_remains_unresolved(self):
        frame = sealed_frame()
        claimed = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        completed, receipt = lt.complete_work_item(
            frame,
            claimed,
            seat_id="SEAT-A",
            completed_at="2026-09-24T12:34:00Z",
            result_posture="HELD",
            output_objects=[sealed_output()],
            unresolved=["missing evidence"],
            stop_reason="held",
            handoff_id="LT001-H1",
        )
        self.assertEqual(lt.resolve_next_destination(completed, receipt), "UNRESOLVED")

    def test_t09_role_mismatch_rejects_operation(self):
        with self.assertRaisesRegex(lt.WorkItemRejected, "ROLE_MISMATCH"):
            lt.claim_work_item(
                sealed_frame(),
                sealed_work(),
                seat_id="SEAT-B",
                seat_role="REVIEWER",
                claimed_at="2026-09-24T12:32:00Z",
            )

    def test_handoff_preserves_claimed_and_terminal_work_identities(self):
        frame = sealed_frame()
        claimed = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        claimed_identity = claimed["integrity_sha256"]
        output = sealed_output()
        completed, receipt = lt.complete_work_item(
            frame,
            claimed,
            seat_id="SEAT-A",
            completed_at="2026-09-24T12:34:00Z",
            result_posture="COMPLETED",
            output_objects=[output],
            unresolved=[],
            stop_reason="done",
            handoff_id="LT001-H1",
        )
        self.assertEqual(receipt["input_work_item_identity"], claimed_identity)
        self.assertEqual(
            receipt["terminal_work_item_identity"],
            completed["integrity_sha256"],
        )
        self.assertNotEqual(
            receipt["input_work_item_identity"],
            receipt["terminal_work_item_identity"],
        )
        reconstructed = lt.reconstruct_handoff(
            frame, completed, receipt, output_objects=[output]
        )
        self.assertEqual(reconstructed["work_item_id"], "LT001-W1")

    def test_t10_live_chat_context_not_required_by_reconstruction(self):
        frame = sealed_frame()
        claimed = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        output = sealed_output()
        completed, receipt = lt.complete_work_item(
            frame,
            claimed,
            seat_id="SEAT-A",
            completed_at="2026-09-24T12:34:00Z",
            result_posture="COMPLETED",
            output_objects=[output],
            unresolved=[],
            stop_reason="done",
            handoff_id="LT001-H1",
        )
        reconstructed = lt.reconstruct_handoff(
            frame, completed, receipt, output_objects=[output]
        )
        self.assertFalse(reconstructed["live_chat_context_required"])

    def test_t11_superseded_frame_cannot_silently_remain_current(self):
        frame = lt.supersede_frame(
            sealed_frame(), successor_frame_id="FRAME-LT001-002"
        )
        with self.assertRaises(lt.FrameUnresolved):
            lt.read_current_frame(frame)

    def test_t12_no_automatic_next_seat_invocation_exists(self):
        source = Path(lt.__file__).read_text(encoding="utf-8")
        forbidden = [
            "urllib",
            "requests.",
            "subprocess",
            "openai",
            "lmstudio",
            "chat/completions",
            "invoke_model",
            "spawn",
        ]
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_t13_no_automatic_retry_exists(self):
        source = Path(lt.__file__).read_text(encoding="utf-8").lower()
        self.assertNotIn("retry(", source)
        self.assertNotIn("automatic_retry", source)

    def test_t14_result_or_handoff_mutation_is_detectable(self):
        frame = sealed_frame()
        claimed = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        output = sealed_output()
        completed, receipt = lt.complete_work_item(
            frame,
            claimed,
            seat_id="SEAT-A",
            completed_at="2026-09-24T12:34:00Z",
            result_posture="COMPLETED",
            output_objects=[output],
            unresolved=[],
            stop_reason="done",
            handoff_id="LT001-H1",
        )

        mutated_output = copy.deepcopy(output)
        mutated_output["content"] = "changed"
        with self.assertRaises(lt.CoordinationError):
            lt.reconstruct_handoff(
                frame, completed, receipt, output_objects=[mutated_output]
            )

        mutated_receipt = copy.deepcopy(receipt)
        mutated_receipt["stop_reason"] = "changed"
        with self.assertRaises(lt.CoordinationError):
            lt.validate_handoff(mutated_receipt)

    def test_artifact_descriptor_detects_byte_mutation(self):
        descriptor = lt.artifact_descriptor(
            "docs/campaigns/load_transfer_001/pressure_runs/O1.md",
            b"original\n",
        )
        lt.verify_artifact_descriptor(descriptor, b"original\n")
        with self.assertRaises(lt.CoordinationError):
            lt.verify_artifact_descriptor(descriptor, b"mutated\n")

    def test_t15_fresh_reconstruction_from_serialized_repo_state_succeeds(self):
        frame = sealed_frame()
        claimed = lt.claim_work_item(
            frame,
            sealed_work(),
            seat_id="SEAT-A",
            seat_role="IMPLEMENTER",
            claimed_at="2026-09-24T12:32:00Z",
        )
        output = sealed_output()
        completed, receipt = lt.complete_work_item(
            frame,
            claimed,
            seat_id="SEAT-A",
            completed_at="2026-09-24T12:34:00Z",
            result_posture="COMPLETED",
            output_objects=[output],
            unresolved=[],
            stop_reason="done",
            handoff_id="LT001-H1",
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frame_path = root / "frame.json"
            queue_path = root / "queue.jsonl"
            handoff_path = root / "handoffs.jsonl"
            output_path = root / "output.json"
            lt.write_json(frame_path, frame)
            lt.append_jsonl(queue_path, completed)
            lt.append_jsonl(handoff_path, receipt)
            lt.write_json(output_path, output)

            fresh_frame = lt.load_json(frame_path)
            fresh_work = lt.read_jsonl(queue_path)[0]
            fresh_handoff = lt.read_jsonl(handoff_path)[0]
            fresh_output = lt.load_json(output_path)
            reconstructed = lt.reconstruct_handoff(
                fresh_frame,
                fresh_work,
                fresh_handoff,
                output_objects=[fresh_output],
            )
            self.assertEqual(reconstructed["next_eligible_destination"], "LT001-W2-REVIEWER")


if __name__ == "__main__":
    unittest.main()
