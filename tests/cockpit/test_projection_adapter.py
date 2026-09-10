from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from src.cockpit.projection_adapter import ADAPTER_VERSION, build_projection


PROJECTION_TIME = "2026-09-09T12:00:00Z"


def run_git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
    ).strip()


def pressure_node(
    pressure_id: str,
    *,
    standing: str = "BOUNDED_RESOLUTION",
    blocked_by: str = "—",
    evidence: str = "[decision](docs/decisions/existing.md)",
    history: bool = False,
) -> str:
    value = f"""### {pressure_id} — Bounded specimen

- **Pressure:** Can the bounded specimen preserve its declared fields?
- **Standing:** `{standing}`
- **Missing discriminator:** —
- **Resolution so far:** The declared result remains bounded.
- **Residue:** Generalization remains unearned.
- **Blocked by:** {blocked_by}
- **Unlocks:** —
- **Evidence:** {evidence}
"""
    if history:
        value += f"""
#### {pressure_id} — Resolution history

- **R0 — `BASIS_INSUFFICIENT`:** The first basis did not discriminate.
- **R1 — `BOUNDED_RESOLUTION`:** The second bounded basis discriminated.
"""
    return value


class ProjectionAdapterTest(unittest.TestCase):
    def make_repo(
        self,
        *,
        standing: str = "BOUNDED_RESOLUTION",
        blocked_by: str = "—",
        evidence: str = "[decision](docs/decisions/existing.md)",
        history: bool = False,
    ) -> Path:
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        run_git(root, "init", "-b", "main")
        run_git(root, "config", "user.name", "DME Test")
        run_git(root, "config", "user.email", "dme-test@example.invalid")
        run_git(root, "remote", "add", "origin", "https://github.com/example/specimen.git")

        project_state = """# Project State

## Current Navigation and Development Standing

- Active experimental pressure: none.
- No next experimental pressure has been selected.

The DME Cockpit is authorized as read-only projection work. The Controller
remains parked.
"""
        pressure_map = f"""# Pressure / Resolution Map v0

## Current Navigation

Active pressure: none

Newly reachable / open:

Shelved:

## A. Test pressures

{pressure_node('PR-001', standing=standing, blocked_by=blocked_by, evidence=evidence, history=history)}

{pressure_node('PR-002')}
"""
        constraint = {
            "id": "D-0001",
            "left": "constraint",
            "relation": "not_equivalent_to",
            "right": "local_distinction_event",
            "scope": "cockpit_adapter_test",
            "basis": "design_constraint",
            "provenance": ["docs/decisions/existing.md"],
            "standing": "supported",
            "note": "The adapter preserves registry records as constraints.",
        }
        files = {
            "PROJECT_STATE.md": project_state,
            "PRESSURE_RESOLUTION_MAP.md": pressure_map,
            "docs/constraints/README.md": "# Constraints\n\nconstraint != local distinction event\n",
            "docs/constraints/registry.jsonl": json.dumps(constraint) + "\n",
            "docs/decisions/existing.md": "# Existing evidence\n",
            "docs/projection/Controller.md": "# Controller\n\n> Non-authoritative projection.\n\n## Standing\n\nPARKED.\n",
            "docs/projection/Persistent_Ecology.md": "# Persistent Ecology\n\n> Non-authoritative projection.\n\n## Epistemic Status\n\nProjected only.\n",
            "docs/projection/Persistent_Research_Autonomy.md": "# Persistent Research Autonomy\n\n> Non-authoritative projection.\n\n## Current Standing\n\nThis question is shelved.\n",
        }
        for relative_path, content in files.items():
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        run_git(root, "add", ".")
        run_git(root, "commit", "-m", "bounded projection specimen")
        return root

    def project(self, root: Path) -> dict[str, object]:
        return build_projection(
            root,
            source_ref="HEAD",
            freshness_ref="HEAD",
            projection_time=PROJECTION_TIME,
        )

    def test_committed_tree_boundary_ignores_dirty_working_tree(self) -> None:
        root = self.make_repo(standing="BOUNDED_RESOLUTION")
        path = root / "PRESSURE_RESOLUTION_MAP.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "`BOUNDED_RESOLUTION`", "`OPEN`", 1
            ),
            encoding="utf-8",
        )

        model = self.project(root)

        self.assertEqual(model["pressure_nodes"][0]["standing"]["value"], "BOUNDED_RESOLUTION")
        self.assertIn("PRESSURE_RESOLUTION_MAP.md", run_git(root, "status", "--short"))

    def test_basic_pressure_node_preserves_fields_and_provenance(self) -> None:
        root = self.make_repo()
        model = self.project(root)
        node = model["pressure_nodes"][0]

        self.assertEqual(node["id"], "PR-001")
        self.assertEqual(node["title"], "Bounded specimen")
        self.assertEqual(node["standing"]["value"], "BOUNDED_RESOLUTION")
        self.assertIn("preserve its declared fields", node["pressure"]["value"])
        self.assertEqual(node["provenance"]["source_path"], "PRESSURE_RESOLUTION_MAP.md")
        self.assertEqual(node["provenance"]["source_commit"], run_git(root, "rev-parse", "HEAD"))
        self.assertEqual(node["provenance"]["source_anchor"], "PR-001 — Bounded specimen")

    def test_resolution_history_remains_distinct_from_current_standing(self) -> None:
        model = self.project(self.make_repo(history=True))
        node = model["pressure_nodes"][0]

        self.assertEqual(node["standing"]["value"], "BOUNDED_RESOLUTION")
        self.assertEqual(
            [entry["standing"]["value"] for entry in node["resolution_history"]],
            ["BASIS_INSUFFICIENT", "BOUNDED_RESOLUTION"],
        )

    def test_relations_come_only_from_explicit_non_absent_fields(self) -> None:
        model = self.project(self.make_repo(blocked_by="PR-002"))

        self.assertEqual(len(model["pressure_relations"]), 1)
        relation = model["pressure_relations"][0]
        self.assertEqual(relation["relation_kind"], "blocked_by")
        self.assertEqual(relation["source_pressure_id"], "PR-001")
        self.assertEqual(relation["target_pressure_id"], "PR-002")
        self.assertNotIn(
            "PR-002",
            [
                item["source_pressure_id"]
                for item in model["pressure_relations"]
                if item["relation_kind"] == "blocked_by"
            ],
        )

    def test_constraint_record_is_not_promoted_to_distinction_event(self) -> None:
        model = self.project(self.make_repo())
        constraint = model["constraints"][0]

        self.assertEqual(constraint["id"], "D-0001")
        self.assertEqual(constraint["classification"], "constraint")
        self.assertEqual(constraint["provenance"], ["docs/decisions/existing.md"])
        self.assertEqual(
            constraint["adapter_provenance"]["source_path"],
            "docs/constraints/registry.jsonl",
        )
        self.assertNotIn("distinctions", model)

    def test_malformed_constraint_line_remains_diagnostic_residue(self) -> None:
        root = self.make_repo()
        registry = root / "docs/constraints/registry.jsonl"
        registry.write_text(
            registry.read_text(encoding="utf-8") + "{malformed\n",
            encoding="utf-8",
        )
        run_git(root, "add", "docs/constraints/registry.jsonl")
        run_git(root, "commit", "-m", "add malformed constraint residue")

        model = self.project(root)

        self.assertEqual(len(model["constraints"]), 1)
        self.assertEqual(model["constraints"][0]["id"], "D-0001")
        self.assertEqual(model["repository_state"]["projection_status"], "partial")
        self.assertIn(
            "parse_failure",
            [item["kind"] for item in model["projection_diagnostics"]],
        )

    def test_broken_reference_remains_visible_with_diagnostic(self) -> None:
        model = self.project(
            self.make_repo(evidence="[missing](docs/decisions/not-there.md)")
        )
        broken = [
            item
            for item in model["evidence_refs"]
            if item["original_target"] == "docs/decisions/not-there.md"
        ]

        self.assertEqual(len(broken), 1)
        self.assertEqual(broken[0]["resolution_status"], "broken")
        self.assertIn(
            "broken_reference",
            [item["kind"] for item in model["projection_diagnostics"]],
        )

    def test_unknown_standing_is_preserved_verbatim(self) -> None:
        model = self.project(self.make_repo(standing="NEW_FUTURE_STATUS"))
        standing = model["pressure_nodes"][0]["standing"]

        self.assertEqual(standing["value"], "NEW_FUTURE_STATUS")
        self.assertEqual(standing["status"], "unknown_standing")
        self.assertIn(
            "unknown_standing",
            [item["kind"] for item in model["projection_diagnostics"]],
        )

    def test_same_commit_version_and_runtime_time_are_deterministic(self) -> None:
        root = self.make_repo(history=True, blocked_by="PR-002")

        first = self.project(root)
        second = self.project(root)

        self.assertEqual(first, second)
        self.assertEqual(first["repository_state"]["adapter_version"], ADAPTER_VERSION)


if __name__ == "__main__":
    unittest.main()
