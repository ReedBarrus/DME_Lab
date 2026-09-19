from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect
import json
from pathlib import Path
import tempfile
import unittest

from lab.ops.candidates.addressing_001.addressing import (
    AddressedWork,
    AddressingShapeError,
    DurableWorkRecord,
    global_record_ids,
    load_global_work_registry,
    load_role_registry,
    project_available_to_role,
)


DUMMY_BASIS = "ADDRESSING_001-DUMMY-BASIS"


def dummy_work(target_role: str) -> dict[str, object]:
    return {
        "source_role": "COMMANDER",
        "target_role": target_role,
        "created_against_basis": DUMMY_BASIS,
        "task_type": "DUMMY_ROUTING_TASK",
        "payload_refs": ["sha256:dummy-payload"],
        "authority_ceiling": "NO_CONSEQUENCE_AUTHORITY",
        "required_output_type": "DUMMY_OUTPUT",
        "depends_on": [],
        "supersedes": None,
    }


def dummy_record(record_id: str, target_role: str) -> dict[str, object]:
    return {"record_id": record_id, "work_payload": dummy_work(target_role)}


class Addressing001ApparatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.registry_path = (
            Path(__file__).parents[2]
            / "lab"
            / "ops"
            / "candidates"
            / "addressing_001"
            / "role_registry_v0.json"
        )
        self.roles = load_role_registry(self.registry_path)

    def parse(self, record_id: str, target_role: str) -> DurableWorkRecord:
        return DurableWorkRecord.from_mapping(
            dummy_record(record_id, target_role), role_registry=self.roles
        )

    def test_role_registry_is_exact_and_explicit(self) -> None:
        self.assertEqual(self.roles.roles, ("COMMANDER", "WORKSHOP"))

    def test_record_identity_is_outside_work_payload(self) -> None:
        raw = dummy_record("DUMMY-A", "WORKSHOP")
        self.assertEqual(set(raw), {"record_id", "work_payload"})
        self.assertNotIn("work_id", raw["work_payload"])
        record = DurableWorkRecord.from_mapping(raw, role_registry=self.roles)
        self.assertEqual(record.record_id, "DUMMY-A")
        self.assertEqual(record.work_payload.target_role, "WORKSHOP")

    def test_q1_record_id_change_does_not_change_role_local_availability(self) -> None:
        work = dummy_work("WORKSHOP")
        a = DurableWorkRecord.from_mapping(
            {"record_id": "DUMMY-A", "work_payload": deepcopy(work)},
            role_registry=self.roles,
        )
        b = DurableWorkRecord.from_mapping(
            {"record_id": "DUMMY-B", "work_payload": deepcopy(work)},
            role_registry=self.roles,
        )

        a_available = project_available_to_role((a,), "WORKSHOP", self.roles)
        b_available = project_available_to_role((b,), "WORKSHOP", self.roles)

        self.assertEqual(a.work_payload, b.work_payload)
        self.assertNotEqual(a.record_id, b.record_id)
        self.assertEqual(bool(a_available), bool(b_available))
        self.assertTrue(a_available)

    def test_q2_target_role_change_changes_role_local_availability(self) -> None:
        a = self.parse("DUMMY-SAME-RECORD", "WORKSHOP")
        b = self.parse("DUMMY-SAME-RECORD", "COMMANDER")

        a_available = project_available_to_role((a,), "WORKSHOP", self.roles)
        b_available = project_available_to_role((b,), "WORKSHOP", self.roles)

        self.assertEqual(a.record_id, b.record_id)
        a_payload = a.work_payload.as_mapping()
        b_payload = b.work_payload.as_mapping()
        self.assertEqual(
            {key: value for key, value in a_payload.items() if key != "target_role"},
            {key: value for key, value in b_payload.items() if key != "target_role"},
        )
        self.assertEqual(tuple(record.record_id for record in a_available), ("DUMMY-SAME-RECORD",))
        self.assertEqual(b_available, ())

    def test_global_existence_and_role_local_availability_are_separate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.json").write_text(
                json.dumps(dummy_record("DUMMY-A", "WORKSHOP")), encoding="utf-8"
            )
            (root / "b.json").write_text(
                json.dumps(dummy_record("DUMMY-B", "COMMANDER")), encoding="utf-8"
            )

            global_registry = load_global_work_registry(root, role_registry=self.roles)
            before = global_record_ids(global_registry)
            workshop = project_available_to_role(global_registry, "WORKSHOP", self.roles)
            after = global_record_ids(global_registry)

            self.assertEqual(before, ("DUMMY-A", "DUMMY-B"))
            self.assertEqual(after, before)
            self.assertEqual(tuple(record.record_id for record in workshop), ("DUMMY-A",))
            self.assertIn("DUMMY-B", after)

    def test_projection_signature_has_no_record_identity_or_seat_input(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(project_available_to_role).parameters),
            ("records", "role_id", "role_registry"),
        )
        source = inspect.getsource(project_available_to_role)
        for forbidden in (
            "record_id",
            "filename",
            "registry_key",
            "insertion_order",
            "timestamp",
            "serialization_position",
            "seat_instance",
        ):
            self.assertNotIn(forbidden, source)

    def test_projection_does_not_strengthen_authority_and_records_are_immutable(self) -> None:
        record = self.parse("DUMMY-A", "WORKSHOP")
        workshop = project_available_to_role((record,), "WORKSHOP", self.roles)

        self.assertEqual(workshop, (record,))
        self.assertEqual(workshop[0].work_payload.authority_ceiling, "NO_CONSEQUENCE_AUTHORITY")
        with self.assertRaises(FrozenInstanceError):
            workshop[0].work_payload.target_role = "COMMANDER"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            workshop[0].record_id = "OTHER"  # type: ignore[misc]

    def test_unregistered_roles_and_injected_authority_flags_are_rejected(self) -> None:
        unknown = dummy_record("DUMMY-X", "UNKNOWN")
        with self.assertRaises(AddressingShapeError):
            DurableWorkRecord.from_mapping(unknown, role_registry=self.roles)

        injected_payload = dummy_work("WORKSHOP")
        injected_payload["authorized"] = True
        with self.assertRaises(AddressingShapeError):
            AddressedWork.from_mapping(injected_payload, role_registry=self.roles)

        injected_record = dummy_record("DUMMY-Y", "WORKSHOP")
        injected_record["authorized"] = True
        with self.assertRaises(AddressingShapeError):
            DurableWorkRecord.from_mapping(injected_record, role_registry=self.roles)

    def test_duplicate_global_record_ids_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.json").write_text(
                json.dumps(dummy_record("DUPLICATE", "WORKSHOP")), encoding="utf-8"
            )
            (root / "b.json").write_text(
                json.dumps(dummy_record("DUPLICATE", "COMMANDER")), encoding="utf-8"
            )
            with self.assertRaises(AddressingShapeError):
                load_global_work_registry(root, role_registry=self.roles)


if __name__ == "__main__":
    unittest.main()
