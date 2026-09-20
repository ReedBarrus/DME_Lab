from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "branch_registry.py"
SPEC = importlib.util.spec_from_file_location("branch_registry", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
branch_registry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(branch_registry)

BranchInfo = branch_registry.BranchInfo
classify = branch_registry.classify


class BranchRegistryClassificationTests(unittest.TestCase):
    def base(self):
        return {
            "main": BranchInfo("main", "a", 100),
            "frontier": BranchInfo("frontier", "b", 200),
            "old": BranchInfo("old", "c", 150),
            "unique": BranchInfo("unique", "d", 175),
            "pr": BranchInfo("pr", "e", 180),
        }

    def test_bootstrap_deletes_only_reachable_nonregistered_ref(self):
        items = classify(
            self.base(),
            {"main", "frontier"},
            {"old": ("frontier",), "unique": (), "pr": ("main",)},
            open_pr_heads={"pr"},
            protected=set(),
            mode="bootstrap",
            cache_max_refs=5,
            cache_ttl_hours=72,
            now=300,
        )
        states = {x.name: x.state for x in items}
        self.assertEqual(states["main"], "RETAIN_DURABLE")
        self.assertEqual(states["frontier"], "RETAIN_DURABLE")
        self.assertEqual(states["old"], "DELETE_ELIGIBLE")
        self.assertEqual(states["unique"], "RETAIN_ORPHAN_UNIQUE")
        self.assertEqual(states["pr"], "RETAIN_TRANSIENT")

    def test_protected_ref_is_never_delete_eligible(self):
        items = classify(
            self.base(),
            {"main", "frontier"},
            {"old": ("frontier",), "unique": (), "pr": ("main",)},
            open_pr_heads=set(),
            protected={"old"},
            mode="bootstrap",
            cache_max_refs=5,
            cache_ttl_hours=72,
            now=300,
        )
        states = {x.name: x.state for x in items}
        self.assertEqual(states["old"], "RETAIN_PROTECTED")

    def test_steady_cache_is_bounded_by_count_and_ttl(self):
        branches = {
            "main": BranchInfo("main", "a", 100),
            "r1": BranchInfo("r1", "b", 990),
            "r2": BranchInfo("r2", "c", 980),
            "r3": BranchInfo("r3", "d", 970),
        }
        items = classify(
            branches,
            {"main"},
            {"r1": ("main",), "r2": ("main",), "r3": ("main",)},
            open_pr_heads=set(),
            protected=set(),
            mode="steady",
            cache_max_refs=2,
            cache_ttl_hours=1,
            now=1000,
        )
        states = {x.name: x.state for x in items}
        self.assertEqual(states["r1"], "RETAIN_CACHE")
        self.assertEqual(states["r2"], "RETAIN_CACHE")
        self.assertEqual(states["r3"], "DELETE_ELIGIBLE")

    def test_cache_age_expires_even_inside_count_window(self):
        branches = {
            "main": BranchInfo("main", "a", 100),
            "old": BranchInfo("old", "b", 1),
        }
        items = classify(
            branches,
            {"main"},
            {"old": ("main",)},
            open_pr_heads=set(),
            protected=set(),
            mode="steady",
            cache_max_refs=5,
            cache_ttl_hours=1,
            now=10_000,
        )
        states = {x.name: x.state for x in items}
        self.assertEqual(states["old"], "DELETE_ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
