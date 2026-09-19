from __future__ import annotations

from dataclasses import FrozenInstanceError
from copy import deepcopy
import inspect
import json
from pathlib import Path
import tempfile
import unittest

from lab.ops.candidates.addressing_001.addressing import (
    AddressedWork,
    AddressingShapeError,
    global_work_ids,
    load_global_work_registry,
    load_role_registry,
    project_available_to_role,
)


DUMMY_BASIS = "ADDRESSING_001-DUMMY-BASIS"


def dummy_work(work_id: str, target_role: str) -> dict[str, object]:
    return {
        "work_id": work_id,
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

    def test_role_registry_is_exact_and_explicit(self) -> None:
        self.assertEqual(self.roles.roles, ("COMMANDER", "WORKSHOP"))

    def test_dummy_pair_holds_nonidentity_content_constant(self) -> None:
        a = dummy_work("DUMMY-A", "WORKSHOP")
        b = deepcopy(a)
        b["work_id"] = "DUMMY-B"
        # Qualification needs distinct durable identities. This is not the held-out
        # sole-discriminator claim; future experimental identity treatment remains unfrozen.
        b["target_role"] = "COMMANDER"
        content_keys = set(a) - {"work_id", "target_role"}
        self.assertEqual({key: a[key] for key in content_keys}, {key: b[key] for key in content_keys})
        self.assertNotEqual(a["target_role"], b["target_role"])

    def test_global_existence_and_role_local_availability_are_separate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.json").write_text(json.dumps(dummy_work("DUMMY-A", "WORKSHOP")), encoding="utf-8")
            (root / "b.json").write_text(json.dumps(dummy_work("DUMMY-B", "COMMANDER")), encoding="utf-8")

            global_registry = load_global_work_registry(root, role_registry=self.roles)
            before = global_work_ids(global_registry)
            workshop = project_available_to_role(global_registry, "WORKSHOP", self.roles)
            after = global_work_ids(global_registry)

            self.assertEqual(before, ("DUMMY-A", "DUMMY-B"))
            self.assertEqual(after, before)
            self.assertEqual(tuple(item.work_id for item in workshop), ("DUMMY-A",))
            self.assertIn("DUMMY-B", after)

    def test_projection_is_role_based_and_does_not_strengthen_authority(self) -> None:
        a = AddressedWork.from_mapping(dummy_work("DUMMY-A", "WORKSHOP"), role_registry=self.roles)
        workshop = project_available_to_role((a,), "WORKSHOP", self.roles)

        self.assertEqual(workshop, (a,))
        self.assertEqual(workshop[0].authority_ceiling, "NO_CONSEQUENCE_AUTHORITY")
        self.assertEqual(
            tuple(inspect.signature(project_available_to_role).parameters),
            ("work_items", "role_id", "role_registry"),
        )
        with self.assertRaises(FrozenInstanceError):
            workshop[0].target_role = "COMMANDER"  # type: ignore[misc]

    def test_unregistered_roles_and_authority_flags_are_rejected(self) -> None:
        unknown = dummy_work("DUMMY-X", "UNKNOWN")
        with self.assertRaises(AddressingShapeError):
            AddressedWork.from_mapping(unknown, role_registry=self.roles)

        injected = dummy_work("DUMMY-Y", "WORKSHOP")
        injected["authorized"] = True
        with self.assertRaises(AddressingShapeError):
            AddressedWork.from_mapping(injected, role_registry=self.roles)

    def test_duplicate_global_work_ids_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = dummy_work("DUPLICATE", "WORKSHOP")
            (root / "a.json").write_text(json.dumps(work), encoding="utf-8")
            (root / "b.json").write_text(json.dumps(work), encoding="utf-8")
            with self.assertRaises(AddressingShapeError):
                load_global_work_registry(root, role_registry=self.roles)


if __name__ == "__main__":
    unittest.main()
