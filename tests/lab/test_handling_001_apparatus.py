from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect
import unittest

from lab.ops.candidates.addressing_001.addressing import (
    DurableWorkRecord,
    RoleRegistry,
    global_record_ids,
    project_available_to_role,
)
from lab.ops.candidates.handling_001.handling import (
    CLAIM_FOR_HANDLING,
    HandlingClaimEvent,
    HandlingClaimShapeError,
    corresponds,
    work_claimed_for_handling,
)


def dummy_record(record_id: str = "WORK-001") -> DurableWorkRecord:
    roles = RoleRegistry(("COMMANDER", "WORKSHOP"))
    return DurableWorkRecord.from_mapping(
        {
            "record_id": record_id,
            "work_payload": {
                "source_role": "COMMANDER",
                "target_role": "WORKSHOP",
                "created_against_basis": "HANDLING_001-DUMMY-BASIS",
                "task_type": "DUMMY_HANDLING_TASK",
                "payload_refs": ["sha256:dummy"],
                "authority_ceiling": "NO_CONSEQUENCE_AUTHORITY",
                "required_output_type": "DUMMY_OUTPUT",
                "depends_on": [],
                "supersedes": None,
            },
        },
        role_registry=roles,
    )


def claim(event_id: str, event_type: str, work_record_id: str) -> dict[str, str]:
    return {
        "claim_event_id": event_id,
        "event_type": event_type,
        "work_record_id": work_record_id,
    }


class Handling001ApparatusTest(unittest.TestCase):
    def test_q1_no_claim_is_false(self) -> None:
        self.assertFalse(work_claimed_for_handling(dummy_record(), ()))

    def test_q2_exact_corresponding_claim_is_true(self) -> None:
        work = dummy_record()
        raw = claim("CLAIM-001", CLAIM_FOR_HANDLING, work.record_id)
        self.assertTrue(work_claimed_for_handling(work, (raw,)))
        self.assertTrue(corresponds(HandlingClaimEvent.from_mapping(raw), work))

    def test_q3_claim_for_other_work_is_false(self) -> None:
        work = dummy_record("WORK-001")
        raw = claim("CLAIM-001", CLAIM_FOR_HANDLING, "WORK-OTHER")
        self.assertFalse(work_claimed_for_handling(work, (raw,)))

    def test_q4_wrong_event_type_for_this_work_is_false(self) -> None:
        work = dummy_record()
        raw = claim("CLAIM-001", "SOMETHING_ELSE", work.record_id)
        parsed = HandlingClaimEvent.from_mapping(raw)
        self.assertFalse(corresponds(parsed, work))
        self.assertFalse(work_claimed_for_handling(work, (raw,)))

    def test_q5_malformed_claim_is_rejected_and_not_counted(self) -> None:
        work = dummy_record()
        malformed = {
            "claim_event_id": "CLAIM-001",
            "event_type": CLAIM_FOR_HANDLING,
        }
        with self.assertRaises(HandlingClaimShapeError):
            HandlingClaimEvent.from_mapping(malformed)
        self.assertFalse(work_claimed_for_handling(work, (malformed,)))

    def test_claim_event_shape_is_exact_and_immutable(self) -> None:
        raw = claim("CLAIM-001", CLAIM_FOR_HANDLING, "WORK-001")
        event = HandlingClaimEvent.from_mapping(raw)
        self.assertEqual(
            set(event.as_mapping()),
            {"claim_event_id", "event_type", "work_record_id"},
        )
        with self.assertRaises(FrozenInstanceError):
            event.work_record_id = "OTHER"  # type: ignore[misc]
        with self.assertRaises(HandlingClaimShapeError):
            HandlingClaimEvent.from_mapping({**raw, "claimant": "WORKSHOP"})

    def test_handling_evaluation_preserves_addressing_existence_availability_and_authority(self) -> None:
        roles = RoleRegistry(("COMMANDER", "WORKSHOP"))
        work = dummy_record()
        before_mapping = deepcopy(work.as_mapping())
        before_global = global_record_ids((work,))
        before_available = project_available_to_role((work,), "WORKSHOP", roles)
        before_authority = work.work_payload.authority_ceiling

        self.assertTrue(
            work_claimed_for_handling(
                work,
                (claim("CLAIM-001", CLAIM_FOR_HANDLING, work.record_id),),
            )
        )

        self.assertEqual(work.as_mapping(), before_mapping)
        self.assertEqual(global_record_ids((work,)), before_global)
        self.assertEqual(
            project_available_to_role((work,), "WORKSHOP", roles),
            before_available,
        )
        self.assertEqual(work.work_payload.authority_ceiling, before_authority)
        self.assertEqual(before_authority, "NO_CONSEQUENCE_AUTHORITY")

    def test_handling_predicate_has_no_execution_or_consequence_input(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(work_claimed_for_handling).parameters),
            ("work", "claim_events"),
        )
        source = inspect.getsource(work_claimed_for_handling)
        for forbidden in (
            "execute",
            "authorize",
            "consequence",
            "complete",
            "acknowledge",
            "seat",
            "cursor",
            "route",
        ):
            self.assertNotIn(forbidden, source.lower())


if __name__ == "__main__":
    unittest.main()
