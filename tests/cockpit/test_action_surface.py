from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from src.cockpit.action_surface import ActionSurfaceError, build_action_surfaces


PROCESS = {
    "schema_version": "lab_process_v0",
    "process_id": "P-ACTION-SURFACE-TEST",
    "description": "Synthetic routing process for Action Surface tests.",
    "scientific_standing": {"tracked": False, "value": None},
    "initial_phase": "SEEDED",
    "transitions": {
        "SEEDED": {
            "transition_id": "LOAD",
            "kind": "MECHANICAL",
            "to_phase": "WAITING",
        },
        "WAITING": {
            "transition_id": "AUTHORIZE",
            "kind": "HUMAN_DECISION",
            "decision": {
                "decision_id": "D-TEST",
                "question": "Authorize synthetic transition?",
                "allowed_choices": ["APPROVE", "REJECT"],
            },
        },
    },
}


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class ActionSurfaceTest(unittest.TestCase):
    def make_repo(self) -> tuple[TemporaryDirectory, Path]:
        temporary = TemporaryDirectory()
        root = Path(temporary.name)
        run_git(root, "init")
        run_git(root, "config", "user.email", "test@example.invalid")
        run_git(root, "config", "user.name", "Action Surface Test")
        (root / "lab" / "processes").mkdir(parents=True)
        (root / "lab" / "events").mkdir(parents=True)
        (root / "lab" / "processes" / "process.json").write_text(
            json.dumps(PROCESS, indent=2) + "\n",
            encoding="utf-8",
        )
        (root / "lab" / "events" / "events.jsonl").write_text("", encoding="utf-8")
        run_git(root, "add", ".")
        run_git(root, "commit", "-m", "fixture")
        return temporary, root

    def test_process_spec_does_not_imply_runtime_registration(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        surface = build_action_surfaces(root, "HEAD")[0]

        self.assertEqual(surface["runtime_registration"], "ABSENT")
        self.assertEqual(surface["routing_status"], "UNREGISTERED")
        self.assertEqual(surface["phase"], "SEEDED")
        self.assertEqual(
            surface["declared_next_action"]["eligibility"],
            "SPEC_ONLY_UNREGISTERED",
        )
        self.assertEqual(
            surface["declared_next_action"]["transition_id"],
            "LOAD",
        )
        self.assertFalse(surface["projection_boundary"]["creates_authority"])
        self.assertFalse(surface["projection_boundary"]["performs_execution"])
        self.assertRegex(
            surface["provenance"]["source_commit"],
            r"^[0-9a-f]{40}$",
        )

    def test_committed_events_reconstruct_human_decision_gate_without_authorizing_it(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        events = [
            {
                "event_type": "PROCESS_REGISTERED",
                "process_id": "P-ACTION-SURFACE-TEST",
                "initial_phase": "SEEDED",
            },
            {
                "event_type": "TRANSITION_SUCCEEDED",
                "process_id": "P-ACTION-SURFACE-TEST",
                "transition_id": "LOAD",
                "to_phase": "WAITING",
            },
            {
                "event_type": "HUMAN_DECISION_REQUIRED",
                "process_id": "P-ACTION-SURFACE-TEST",
                "transition_id": "AUTHORIZE",
                "decision": PROCESS["transitions"]["WAITING"]["decision"],
            },
        ]
        event_path = root / "lab" / "events" / "events.jsonl"
        event_path.write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
            encoding="utf-8",
        )
        run_git(root, "add", str(event_path.relative_to(root)))
        run_git(root, "commit", "-m", "routing events")

        surface = build_action_surfaces(root, "HEAD")[0]

        self.assertEqual(surface["runtime_registration"], "PRESENT")
        self.assertEqual(surface["routing_status"], "HUMAN_DECISION_REQUIRED")
        self.assertEqual(surface["phase"], "WAITING")
        self.assertEqual(
            surface["declared_next_action"]["eligibility"],
            "REQUIRES_EXPLICIT_HUMAN_DECISION",
        )
        self.assertTrue(surface["declared_next_action"]["authority_required"])
        self.assertEqual(
            surface["declared_next_action"]["authority_effect"],
            "NONE_BY_ACTION_SURFACE",
        )
        self.assertEqual(surface["event_count_consumed"], 3)

    def test_unknown_routing_event_fails_legibly(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        event_path = root / "lab" / "events" / "events.jsonl"
        event_path.write_text(
            json.dumps(
                {
                    "event_type": "MAGICAL_AUTO_EXECUTE",
                    "process_id": "P-ACTION-SURFACE-TEST",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        run_git(root, "add", str(event_path.relative_to(root)))
        run_git(root, "commit", "-m", "invalid routing event")

        with self.assertRaisesRegex(
            ActionSurfaceError,
            "unknown conductor event_type",
        ):
            build_action_surfaces(root, "HEAD")


    def test_transition_lifecycle_is_observational_until_success(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        event_path = root / "lab" / "events" / "events.jsonl"

        cells = [
            [
                {
                    "event_type": "PROCESS_REGISTERED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "initial_phase": "SEEDED",
                },
            ],
            [
                {
                    "event_type": "PROCESS_REGISTERED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "initial_phase": "SEEDED",
                },
                {
                    "event_type": "TRANSITION_REQUESTED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "transition_id": "LOAD",
                },
            ],
            [
                {
                    "event_type": "PROCESS_REGISTERED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "initial_phase": "SEEDED",
                },
                {
                    "event_type": "TRANSITION_REQUESTED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "transition_id": "LOAD",
                },
                {
                    "event_type": "TRANSITION_STARTED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "transition_id": "LOAD",
                },
            ],
            [
                {
                    "event_type": "PROCESS_REGISTERED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "initial_phase": "SEEDED",
                },
                {
                    "event_type": "TRANSITION_REQUESTED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "transition_id": "LOAD",
                },
                {
                    "event_type": "TRANSITION_STARTED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "transition_id": "LOAD",
                },
                {
                    "event_type": "TRANSITION_SUCCEEDED",
                    "process_id": "P-ACTION-SURFACE-TEST",
                    "transition_id": "LOAD",
                    "to_phase": "WAITING",
                },
            ],
        ]

        observed = []
        for index, events in enumerate(cells, start=1):
            event_path.write_text(
                "".join(
                    json.dumps(event, sort_keys=True) + "\n"
                    for event in events
                ),
                encoding="utf-8",
            )
            run_git(root, "add", str(event_path.relative_to(root)))
            run_git(root, "commit", "-m", f"lifecycle cell {index}")
            surface = build_action_surfaces(root, "HEAD")[0]
            observed.append(
                (
                    surface["phase"],
                    surface["routing_status"],
                    surface["last_event_type"],
                    surface["declared_next_action"]["transition_id"],
                    surface["declared_next_action"]["eligibility"],
                    surface["event_count_consumed"],
                )
            )

        self.assertEqual(
            observed,
            [
                (
                    "SEEDED",
                    "REGISTERED",
                    "PROCESS_REGISTERED",
                    "LOAD",
                    "MECHANICAL_ROUTING_AVAILABLE",
                    1,
                ),
                (
                    "SEEDED",
                    "REGISTERED",
                    "TRANSITION_REQUESTED",
                    "LOAD",
                    "MECHANICAL_ROUTING_AVAILABLE",
                    2,
                ),
                (
                    "SEEDED",
                    "REGISTERED",
                    "TRANSITION_STARTED",
                    "LOAD",
                    "MECHANICAL_ROUTING_AVAILABLE",
                    3,
                ),
                (
                    "WAITING",
                    "ACTIVE",
                    "TRANSITION_SUCCEEDED",
                    "AUTHORIZE",
                    "REQUIRES_EXPLICIT_HUMAN_DECISION",
                    4,
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
