from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.cockpit.workcycle_qualification import (
    build_workcycle_qualification_readiness,
)


class WorkcycleQualificationReadinessTests(unittest.TestCase):
    def test_empty_repo_is_held_without_creating_standing(self):
        with TemporaryDirectory() as temporary:
            result = build_workcycle_qualification_readiness(Path(temporary))
        self.assertEqual(
            result["bounded_workcycle"]["qualification_readiness"],
            "HELD",
        )
        self.assertEqual(
            result["self_moving_workcycle"]["qualification_readiness"],
            "HELD",
        )
        self.assertEqual(result["scientific_standing_effect"], "NONE")
        self.assertTrue(result["bounded_workcycle"]["blockers"])
        self.assertTrue(result["self_moving_workcycle"]["blockers"])

    def test_second_successor_repair_result_counts_as_ready(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = (
                root
                / "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
                "SECOND_SUCCESSOR_FROM_RECONCILIATION_REPAIR_RESULT_001.md"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "DISPOSITION:\n"
                "SECOND_SUCCESSOR_FROM_RECONCILIATION_REPAIR_MATCHED\n",
                encoding="utf-8",
            )
            result = build_workcycle_qualification_readiness(root)
        self.assertTrue(result["second_successor_from_reconciliation"]["ready"])
        self.assertEqual(
            result["second_successor_from_reconciliation"]["repair_disposition"],
            "SECOND_SUCCESSOR_FROM_RECONCILIATION_REPAIR_MATCHED",
        )


    def test_self_moving_readiness_is_stricter_than_bounded_readiness(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = build_workcycle_qualification_readiness(root)
        bounded = set(result["bounded_workcycle"]["blockers"])
        self_moving = set(result["self_moving_workcycle"]["blockers"])
        self.assertTrue(bounded.issubset(self_moving))
        self.assertTrue(any(item.startswith("ONE_SUCCESSOR:") for item in self_moving))
        self.assertTrue(any(item.startswith("ATOMIC_ADMISSION:") for item in self_moving))
        self.assertTrue(any(item.startswith("AUTHORITY_BINDING:") for item in self_moving))
        self.assertTrue(any(item.startswith("SUCCESSOR_IDENTITY:") for item in self_moving))
        self.assertTrue(any(item.startswith("BASIS_RECONCILIATION:") for item in self_moving))
        self.assertTrue(
            any(
                item.startswith("VERIFIED_AUTHORITY_ATOMIC_ADMISSION:")
                for item in self_moving
            )
        )
        self.assertTrue(
            any(
                item.startswith("ADMITTED_AUTHORITY_CONSUMPTION:")
                for item in self_moving
            )
        )
        self.assertTrue(
            any(
                item.startswith("INVOCATION_RESULT_WITNESS:")
                for item in self_moving
            )
        )
        self.assertTrue(
            any(
                item.startswith("INVOCATION_RESULT_SETTLEMENT:")
                for item in self_moving
            )
        )
        self.assertTrue(
            any(
                item.startswith("SETTLEMENT_CONSEQUENCE_RECONCILIATION:")
                for item in self_moving
            )
        )
        self.assertTrue(
            any(
                item.startswith("SECOND_SUCCESSOR_FROM_RECONCILIATION:")
                for item in self_moving
            )
        )
        self.assertTrue(
            any(
                item.startswith("SUCCESSOR_WORK_UNIT_MATERIALIZATION:")
                for item in self_moving
            )
        )
        self.assertTrue(any(item.startswith("REPEATED_METABOLIC_LOOP:") for item in self_moving))


if __name__ == "__main__":
    unittest.main()
