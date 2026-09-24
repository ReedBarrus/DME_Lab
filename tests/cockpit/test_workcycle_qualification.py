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

    def test_self_moving_readiness_is_stricter_than_bounded_readiness(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = build_workcycle_qualification_readiness(root)
        bounded = set(result["bounded_workcycle"]["blockers"])
        self_moving = set(result["self_moving_workcycle"]["blockers"])
        self.assertTrue(bounded.issubset(self_moving))
        self.assertTrue(any(item.startswith("ONE_SUCCESSOR:") for item in self_moving))
        self.assertTrue(any(item.startswith("ATOMIC_ADMISSION:") for item in self_moving))


if __name__ == "__main__":
    unittest.main()
