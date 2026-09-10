from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from src.cockpit.projection_adapter import build_projection


PROJECTION_TIME = "2026-09-10T03:00:00Z"


def run_git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
    ).strip()


def pressure_node(
    pressure_id: str,
    *,
    title: str = "Bounded specimen",
    pressure: str = "Can this occurrence remain independently inspectable?",
    standing: str = "BOUNDED_RESOLUTION",
    blocked_by: str = "—",
    history_heading: str | None = None,
) -> str:
    value = f"""### {pressure_id} — {title}

- **Pressure:** {pressure}
- **Standing:** `{standing}`
- **Missing discriminator:** —
- **Resolution so far:** The bounded result remains explicit.
- **Residue:** Generalization remains unearned.
- **Blocked by:** {blocked_by}
- **Unlocks:** —
- **Evidence:** [decision](docs/decisions/existing.md)
"""
    if history_heading is not None:
        value += f"""
#### {pressure_id} — {history_heading}

- **R0 — `BASIS_INSUFFICIENT`:** The first basis did not discriminate.
- **R1 — `BOUNDED_RESOLUTION`:** The second bounded basis discriminated.
"""
    return value


class ProjectionAdapterRemediationTest(unittest.TestCase):
    def project_nodes(self, nodes: list[str]) -> dict[str, object]:
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        run_git(root, "init", "-b", "main")
        run_git(root, "config", "user.name", "DME Remediation Test")
        run_git(root, "config", "user.email", "dme-remediation@example.invalid")
        run_git(root, "remote", "add", "origin", "https://github.com/example/specimen.git")

        constraint = {
            "id": "D-0001",
            "left": "constraint",
            "relation": "not_equivalent_to",
            "right": "local_distinction_event",
            "scope": "cockpit_adapter_remediation_test",
            "basis": "design_constraint",
            "provenance": ["docs/decisions/existing.md"],
            "standing": "supported",
        }
        files = {
            "PROJECT_STATE.md": """# Project State

## Current Navigation and Development Standing

- Active experimental pressure: none.
- No next experimental pressure has been selected.

The DME Cockpit is authorized as read-only projection work. The Controller
remains parked.
""",
            "PRESSURE_RESOLUTION_MAP.md": """# Pressure / Resolution Map v0

## Current Navigation

Active pressure: none

Newly reachable / open:

Shelved:

## A. Remediation specimens

"""
            + "\n\n".join(nodes)
            + "\n",
            "docs/constraints/README.md": (
                "# Constraint Registry\n\nconstraint != local distinction event\n"
            ),
            "docs/constraints/registry.jsonl": json.dumps(constraint) + "\n",
            "docs/decisions/existing.md": "# Existing bounded evidence\n",
        }
        for relative_path, content in files.items():
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        run_git(root, "add", ".")
        run_git(root, "commit", "-m", "bounded remediation specimen")
        return build_projection(
            root,
            source_ref="HEAD",
            freshness_ref="HEAD",
            projection_time=PROJECTION_TIME,
        )

    def test_unsupported_history_shape_remains_residue_not_valid_history(self) -> None:
        model = self.project_nodes(
            [pressure_node("PR-101", history_heading="Earlier adjudications")]
        )
        node = model["pressure_nodes"][0]
        diagnostics = [
            item
            for item in model["projection_diagnostics"]
            if item["kind"] == "unsupported_structure"
            and item["affected"].get("object_id") == "PR-101"
            and item["affected"].get("field") == "resolution_history"
        ]

        self.assertEqual(node["standing"]["value"], "BOUNDED_RESOLUTION")
        self.assertEqual(node["resolution_history"], [])
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(
            [item["text"] for item in diagnostics[0]["raw_value"]],
            [
                "- **R0 — `BASIS_INSUFFICIENT`:** The first basis did not discriminate.",
                "- **R1 — `BOUNDED_RESOLUTION`:** The second bounded basis discriminated.",
            ],
        )
        self.assertEqual(model["repository_state"]["projection_status"], "partial")

    def test_supported_exact_history_heading_remains_healthy(self) -> None:
        model = self.project_nodes(
            [pressure_node("PR-102", history_heading="Resolution history")]
        )
        node = model["pressure_nodes"][0]

        self.assertEqual(
            [item["standing"]["value"] for item in node["resolution_history"]],
            ["BASIS_INSUFFICIENT", "BOUNDED_RESOLUTION"],
        )
        self.assertFalse(
            any(
                item["kind"] == "unsupported_structure"
                and item["affected"].get("object_id") == "PR-102"
                for item in model["projection_diagnostics"]
            )
        )
        self.assertEqual(model["repository_state"]["projection_status"], "complete")

    def test_duplicate_identity_and_relation_target_remain_ambiguous(self) -> None:
        model = self.project_nodes(
            [
                pressure_node(
                    "PR-201",
                    pressure="Can the first occurrence retain its own fields?",
                ),
                pressure_node(
                    "PR-201",
                    pressure="Can the second occurrence retain its own fields?",
                    standing="OPEN",
                ),
                pressure_node("PR-203", blocked_by="PR-201"),
            ]
        )
        duplicates = [item for item in model["pressure_nodes"] if item["id"] == "PR-201"]
        duplicate_diagnostics = [
            item
            for item in model["projection_diagnostics"]
            if item["kind"] == "duplicate_pressure_id"
            and item["affected"].get("object_id") == "PR-201"
        ]
        relations = [
            item
            for item in model["pressure_relations"]
            if item["source_pressure_id"] == "PR-203"
            and item["target_pressure_id"] == "PR-201"
        ]

        self.assertEqual(len(duplicates), 2)
        self.assertEqual(
            [item["standing"]["value"] for item in duplicates],
            ["BOUNDED_RESOLUTION", "OPEN"],
        )
        self.assertEqual(
            [item["pressure"]["value"] for item in duplicates],
            [
                "Can the first occurrence retain its own fields?",
                "Can the second occurrence retain its own fields?",
            ],
        )
        self.assertEqual(
            len({item["provenance"]["source_line"] for item in duplicates}),
            2,
        )
        self.assertTrue(
            all(
                item["identity_resolution"]
                == {"status": "ambiguous", "candidate_count": 2}
                for item in duplicates
            )
        )
        self.assertEqual(len(duplicate_diagnostics), 1)
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0]["raw_source_field"], "PR-201")
        self.assertEqual(
            relations[0]["target_resolution"],
            {"status": "ambiguous", "candidate_count": 2},
        )
        self.assertFalse(any("canonical" in item for item in duplicates))
        self.assertFalse(
            any(
                item["source_pressure_id"] == "PR-201"
                for item in model["pressure_relations"]
            )
        )


if __name__ == "__main__":
    unittest.main()
