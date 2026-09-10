"""Independently re-pressure the remediated Cockpit projection adapter."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from typing import Any, Iterator

from src.cockpit.projection_adapter import ADAPTER_VERSION, build_projection


REPRESSURE_VERSION = "cockpit_projection_adapter_repressure_v0"
PROJECTION_TIME = "2026-09-10T04:00:00Z"

SURVIVES = "SURVIVES"
CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
REGRESSION = "REGRESSION"
CONTRACT_AMBIGUITY = "CONTRACT_AMBIGUITY"
BASIS_INSUFFICIENT = "BASIS_INSUFFICIENT"

CLASSIFICATIONS = (
    SURVIVES,
    CONTRACT_VIOLATION,
    REGRESSION,
    CONTRACT_AMBIGUITY,
    BASIS_INSUFFICIENT,
)

PREDECLARED_CLASSIFICATION = {
    "survives": (
        "The tested wound remains visible and no stronger clean interpretation appears."
    ),
    "contract_violation": (
        "The adapter produces a plausible clean projection while materially hiding, "
        "collapsing, inventing, or strengthening the tested source condition."
    ),
    "regression": (
        "A healthy currently supported source shape degrades, misparses, or emits a "
        "new unjustified diagnostic because of Stage 4B."
    ),
    "contract_ambiguity": (
        "The pressure exposes behavior not currently specified enough to adjudicate."
    ),
    "basis_insufficient": (
        "The fixture does not actually discriminate the intended question."
    ),
}


def _git(root: Path, *args: str, commit_number: int = 0) -> str:
    environment = os.environ.copy()
    timestamp = f"2001-02-01T00:{commit_number:02d}:00+00:00"
    environment.update(
        {
            "GIT_AUTHOR_DATE": timestamp,
            "GIT_COMMITTER_DATE": timestamp,
        }
    )
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
        env=environment,
    ).strip()


class _Specimen:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.commit_number = 0
        _git(root, "init", "-b", "main")
        _git(root, "config", "user.name", "DME Re-pressure")
        _git(root, "config", "user.email", "dme-repressure@example.invalid")
        _git(
            root,
            "remote",
            "add",
            "origin",
            "https://github.com/example/cockpit-repressure.git",
        )

    def write(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit(self, message: str) -> str:
        _git(self.root, "add", "-A")
        _git(
            self.root,
            "commit",
            "-m",
            message,
            commit_number=self.commit_number,
        )
        self.commit_number += 1
        return _git(self.root, "rev-parse", "HEAD")


def _node(
    pressure_id: str,
    *,
    title: str = "Bounded specimen",
    pressure: str = "Can the bounded source condition remain visible?",
    standing: str = "BOUNDED_RESOLUTION",
    blocked_by: str = "—",
    unlocks: str = "—",
    history_heading: str | None = None,
) -> str:
    value = f"""### {pressure_id} — {title}

- **Pressure:** {pressure}
- **Standing:** `{standing}`
- **Missing discriminator:** —
- **Resolution so far:** The result remains bounded.
- **Residue:** Generalization remains unearned.
- **Blocked by:** {blocked_by}
- **Unlocks:** {unlocks}
- **Evidence:** [decision](docs/decisions/existing.md)
"""
    if history_heading is not None:
        value += f"""
#### {pressure_id} — {history_heading}

- **R0 — `BASIS_INSUFFICIENT`:** The first basis did not discriminate.
- **R1 — `BOUNDED_RESOLUTION`:** The second bounded basis discriminated.
"""
    return value


def _base_files(nodes: list[str]) -> dict[str, str]:
    constraint = {
        "id": "D-0001",
        "left": "constraint",
        "relation": "not_equivalent_to",
        "right": "local_distinction_event",
        "scope": "cockpit_projection_adapter_repressure_v0",
        "basis": "design_constraint",
        "provenance": ["docs/decisions/existing.md"],
        "standing": "supported",
    }
    return {
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

## A. Re-pressure specimens

"""
        + "\n\n".join(nodes)
        + "\n",
        "docs/constraints/README.md": (
            "# Constraint Registry\n\nconstraint != local distinction event\n"
        ),
        "docs/constraints/registry.jsonl": json.dumps(constraint) + "\n",
        "docs/decisions/existing.md": "# Existing bounded evidence\n",
    }


@contextmanager
def _specimen(nodes: list[str]) -> Iterator[_Specimen]:
    with TemporaryDirectory() as tmpdir:
        specimen = _Specimen(Path(tmpdir))
        for path, content in _base_files(nodes).items():
            specimen.write(path, content)
        specimen.commit("bounded re-pressure specimen")
        yield specimen


def _project_nodes(nodes: list[str]) -> dict[str, Any]:
    with _specimen(nodes) as specimen:
        return build_projection(
            specimen.root,
            source_ref="HEAD",
            freshness_ref="HEAD",
            projection_time=PROJECTION_TIME,
        )


def _diagnostics(model: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "kind": item["kind"],
            "affected": item["affected"],
            "severity": item["severity"],
            "message": item["message"],
            "provenance": item["provenance"],
            **({"raw_value": item["raw_value"]} if "raw_value" in item else {}),
        }
        for item in model["projection_diagnostics"]
    ]


def _diagnostics_for(
    model: dict[str, Any],
    *,
    kind: str,
    object_id: str | None = None,
    field: str | None = None,
) -> list[dict[str, Any]]:
    return [
        item
        for item in model["projection_diagnostics"]
        if item["kind"] == kind
        and (object_id is None or item["affected"].get("object_id") == object_id)
        and (field is None or item["affected"].get("field") == field)
    ]


def _node_summary(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node["id"],
        "title": node["title"],
        "pressure": node["pressure"]["value"],
        "standing": node["standing"],
        "resolution_history": [
            {
                "id": item["id"],
                "standing": item["standing"],
                "summary": item["summary"],
                "provenance": item["provenance"],
            }
            for item in node["resolution_history"]
        ],
        "identity_resolution": node.get("identity_resolution"),
        "provenance": node["provenance"],
    }


def _relation_summary(relation: dict[str, Any]) -> dict[str, Any]:
    return {
        "relation_kind": relation["relation_kind"],
        "source_pressure_id": relation["source_pressure_id"],
        "target_kind": relation["target_kind"],
        "target_pressure_id": relation["target_pressure_id"],
        "condition_text": relation["condition_text"],
        "raw_source_field": relation["raw_source_field"],
        "target_resolution": relation.get("target_resolution"),
        "provenance": relation["provenance"],
    }


def _scenario(
    *,
    scenario_id: str,
    title: str,
    mutation: str,
    expected_discriminator: str,
    observed: dict[str, Any],
    diagnostics: list[dict[str, Any]],
    classification: str,
    rationale: str,
) -> dict[str, Any]:
    return {
        "id": scenario_id,
        "title": title,
        "mutation": mutation,
        "expected_discriminator": expected_discriminator,
        "observed": observed,
        "diagnostics": diagnostics,
        "classification": classification,
        "rationale": rationale,
    }


def _unsupported_history_scenario(
    *,
    scenario_id: str,
    title: str,
    heading: str,
) -> dict[str, Any]:
    model = _project_nodes([_node("PR-001", history_heading=heading)])
    node = model["pressure_nodes"][0]
    residue = _diagnostics_for(
        model,
        kind="unsupported_structure",
        object_id="PR-001",
        field="resolution_history",
    )
    raw_entries = residue[0].get("raw_value", []) if len(residue) == 1 else []
    survives = (
        node["standing"]["value"] == "BOUNDED_RESOLUTION"
        and node["resolution_history"] == []
        and len(residue) == 1
        and len(raw_entries) == 2
        and all(isinstance(item.get("line"), int) for item in raw_entries)
        and all(item.get("text", "").startswith("- **R") for item in raw_entries)
        and model["repository_state"]["projection_status"] == "partial"
    )
    return _scenario(
        scenario_id=scenario_id,
        title=title,
        mutation=(
            f"Used unsupported heading {heading!r} above intact strongly structured "
            "R0/R1 entries."
        ),
        expected_discriminator=(
            "Current standing survives, history remains unaccepted, and raw R-entry "
            "lines plus committed coordinates remain visible in a partial projection."
        ),
        observed={
            "node": _node_summary(node),
            "history_residue": raw_entries,
            "projection_status": model["repository_state"]["projection_status"],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else CONTRACT_VIOLATION,
        rationale=(
            "Unsupported structured history remained rejected and visible."
            if survives
            else "Unsupported structured history was promoted, hidden, or lost its residue."
        ),
    )


def _r1_original_history_wound() -> dict[str, Any]:
    return _unsupported_history_scenario(
        scenario_id="R1",
        title="P8 original wound replay",
        heading="Prior resolutions",
    )


def _r2_nearby_history_heading() -> dict[str, Any]:
    return _unsupported_history_scenario(
        scenario_id="R2",
        title="P8 nearby heading variant",
        heading="Earlier outcomes",
    )


def _r3_healthy_history_control() -> dict[str, Any]:
    model = _project_nodes([_node("PR-001", history_heading="Resolution history")])
    node = model["pressure_nodes"][0]
    history_standings = [
        item["standing"]["value"] for item in node["resolution_history"]
    ]
    unsupported = _diagnostics_for(
        model,
        kind="unsupported_structure",
        object_id="PR-001",
        field="resolution_history",
    )
    survives = (
        node["standing"]["value"] == "BOUNDED_RESOLUTION"
        and history_standings == ["BASIS_INSUFFICIENT", "BOUNDED_RESOLUTION"]
        and unsupported == []
        and model["repository_state"]["projection_status"] == "complete"
    )
    return _scenario(
        scenario_id="R3",
        title="P8 healthy control",
        mutation="Used the exact supported Resolution history heading with valid R0/R1 entries.",
        expected_discriminator=(
            "Supported history parses normally with no unsupported diagnostic or partial status."
        ),
        observed={
            "node": _node_summary(node),
            "projection_status": model["repository_state"]["projection_status"],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else REGRESSION,
        rationale=(
            "The exact supported history shape remained healthy."
            if survives
            else "The Stage 4B detector degraded a supported history shape."
        ),
    )


def _r4_history_like_prose() -> dict[str, Any]:
    prose = "R0 was discussed previously, without a structured history declaration."
    model = _project_nodes([_node("PR-001", pressure=prose)])
    node = model["pressure_nodes"][0]
    unsupported = _diagnostics_for(
        model,
        kind="unsupported_structure",
        object_id="PR-001",
        field="resolution_history",
    )
    survives = (
        node["pressure"]["value"] == prose
        and node["resolution_history"] == []
        and unsupported == []
        and model["repository_state"]["projection_status"] == "complete"
    )
    return _scenario(
        scenario_id="R4",
        title="history-like prose false positive",
        mutation="Mentioned 'R0 was discussed previously' in ordinary Pressure prose.",
        expected_discriminator=(
            "Loose prose remains ordinary copied text and emits no unsupported-history diagnostic."
        ),
        observed={
            "pressure": node["pressure"],
            "resolution_history": node["resolution_history"],
            "projection_status": model["repository_state"]["projection_status"],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else REGRESSION,
        rationale=(
            "Loose prose did not trigger the structural wound detector."
            if survives
            else "Ordinary prose triggered an unjustified history diagnostic or parse change."
        ),
    )


def _duplicate_observation(model: dict[str, Any], pressure_id: str) -> dict[str, Any]:
    nodes = [node for node in model["pressure_nodes"] if node["id"] == pressure_id]
    diagnostics = _diagnostics_for(
        model,
        kind="duplicate_pressure_id",
        object_id=pressure_id,
    )
    return {
        "nodes": nodes,
        "diagnostics": diagnostics,
        "source_lines": [node["provenance"].get("source_line") for node in nodes],
    }


def _duplicates_survive(
    observation: dict[str, Any],
    *,
    expected_count: int,
    expected_standings: list[str],
) -> bool:
    nodes = observation["nodes"]
    return (
        len(nodes) == expected_count
        and [node["standing"]["value"] for node in nodes] == expected_standings
        and len(set(observation["source_lines"])) == expected_count
        and None not in observation["source_lines"]
        and len(observation["diagnostics"]) == 1
        and all(
            node.get("identity_resolution")
            == {"status": "ambiguous", "candidate_count": expected_count}
            for node in nodes
        )
        and all("canonical" not in node for node in nodes)
    )


def _r5_original_duplicate_replay() -> dict[str, Any]:
    model = _project_nodes(
        [
            _node("PR-001", title="Occurrence A", standing="BOUNDED_RESOLUTION"),
            _node("PR-001", title="Occurrence B", standing="OPEN"),
        ]
    )
    observation = _duplicate_observation(model, "PR-001")
    survives = _duplicates_survive(
        observation,
        expected_count=2,
        expected_standings=["BOUNDED_RESOLUTION", "OPEN"],
    )
    return _scenario(
        scenario_id="R5",
        title="P11 original duplicate replay",
        mutation="Created two current PR-001 nodes with different titles and standings.",
        expected_discriminator=(
            "Both occurrences and fields survive with distinct provenance, one duplicate "
            "diagnostic, and no canonical winner."
        ),
        observed={
            "nodes": [_node_summary(node) for node in observation["nodes"]],
            "source_lines": observation["source_lines"],
            "projection_status": model["repository_state"]["projection_status"],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else CONTRACT_VIOLATION,
        rationale=(
            "Duplicate identity remained occurrence-preserving and unresolved."
            if survives
            else "Duplicate identity collapsed, merged, lost provenance, or gained a winner."
        ),
    )


def _r6_identical_duplicate_headings() -> dict[str, Any]:
    model = _project_nodes(
        [
            _node(
                "PR-001",
                title="Same title",
                pressure="Can the first identical heading remain local?",
            ),
            _node(
                "PR-001",
                title="Same title",
                pressure="Can the second identical heading remain local?",
                standing="OPEN",
            ),
        ]
    )
    observation = _duplicate_observation(model, "PR-001")
    pressures = [node["pressure"]["value"] for node in observation["nodes"]]
    survives = (
        _duplicates_survive(
            observation,
            expected_count=2,
            expected_standings=["BOUNDED_RESOLUTION", "OPEN"],
        )
        and pressures
        == [
            "Can the first identical heading remain local?",
            "Can the second identical heading remain local?",
        ]
    )
    return _scenario(
        scenario_id="R6",
        title="identical duplicate headings",
        mutation="Created two textually identical PR-001 headings with different bodies.",
        expected_discriminator=(
            "Committed source lines distinguish the occurrences without title-based uniqueness."
        ),
        observed={
            "nodes": [_node_summary(node) for node in observation["nodes"]],
            "source_lines": observation["source_lines"],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else CONTRACT_VIOLATION,
        rationale=(
            "Identical headings remained distinguishable by occurrence-local coordinates."
            if survives
            else "Identical headings collapsed or lost occurrence-local provenance."
        ),
    )


def _r7_duplicate_relation_target() -> dict[str, Any]:
    model = _project_nodes(
        [
            _node("PR-001", title="Occurrence A"),
            _node("PR-001", title="Occurrence B", standing="OPEN"),
            _node("PR-003", blocked_by="PR-001"),
        ]
    )
    observation = _duplicate_observation(model, "PR-001")
    target_relations = [
        relation
        for relation in model["pressure_relations"]
        if relation["source_pressure_id"] == "PR-003"
        and relation["target_pressure_id"] == "PR-001"
    ]
    invented_relations = [
        relation
        for relation in model["pressure_relations"]
        if relation["source_pressure_id"] == "PR-001"
    ]
    survives = (
        _duplicates_survive(
            observation,
            expected_count=2,
            expected_standings=["BOUNDED_RESOLUTION", "OPEN"],
        )
        and len(target_relations) == 1
        and target_relations[0]["raw_source_field"] == "PR-001"
        and target_relations[0].get("target_resolution")
        == {"status": "ambiguous", "candidate_count": 2}
        and invented_relations == []
    )
    return _scenario(
        scenario_id="R7",
        title="duplicate relation target",
        mutation="Referenced two current PR-001 occurrences once from PR-003 Blocked by.",
        expected_discriminator=(
            "One explicit relation survives with target PR-001 and ambiguous two-candidate "
            "resolution; no duplicate or invented edges appear."
        ),
        observed={
            "matching_relations": [
                _relation_summary(relation) for relation in target_relations
            ],
            "invented_duplicate_source_relations": [
                _relation_summary(relation) for relation in invented_relations
            ],
            "duplicate_source_lines": observation["source_lines"],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else CONTRACT_VIOLATION,
        rationale=(
            "The explicit relation survived once and unique target resolution remained ambiguous."
            if survives
            else "The relation was lost, duplicated, resolved to a winner, or supplemented."
        ),
    )


def _r8_duplicate_without_relation() -> dict[str, Any]:
    model = _project_nodes(
        [_node("PR-001", title="A"), _node("PR-001", title="B", standing="OPEN")]
    )
    observation = _duplicate_observation(model, "PR-001")
    survives = (
        _duplicates_survive(
            observation,
            expected_count=2,
            expected_standings=["BOUNDED_RESOLUTION", "OPEN"],
        )
        and model["pressure_relations"] == []
    )
    return _scenario(
        scenario_id="R8",
        title="duplicate ID without relation",
        mutation="Created duplicate PR-001 nodes with no explicit incoming or outgoing relation.",
        expected_discriminator=(
            "Duplicate identity is diagnosed independently of graph usage."
        ),
        observed={
            "node_count": len(observation["nodes"]),
            "source_lines": observation["source_lines"],
            "relation_count": len(model["pressure_relations"]),
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else CONTRACT_VIOLATION,
        rationale=(
            "Duplicate detection did not depend on an explicit relation."
            if survives
            else "Duplicate identity was hidden when no graph relation used it."
        ),
    )


def _r9_unique_control() -> dict[str, Any]:
    model = _project_nodes([_node("PR-001"), _node("PR-002", blocked_by="PR-001")])
    duplicate_diagnostics = _diagnostics_for(model, kind="duplicate_pressure_id")
    relations = [
        relation
        for relation in model["pressure_relations"]
        if relation["source_pressure_id"] == "PR-002"
        and relation["target_pressure_id"] == "PR-001"
    ]
    nodes = model["pressure_nodes"]
    survives = (
        len(nodes) == 2
        and duplicate_diagnostics == []
        and all("identity_resolution" not in node for node in nodes)
        and len(relations) == 1
        and "target_resolution" not in relations[0]
        and model["repository_state"]["projection_status"] == "complete"
    )
    return _scenario(
        scenario_id="R9",
        title="unique identity control",
        mutation="Created unique PR-001 and PR-002 nodes with one explicit relation.",
        expected_discriminator=(
            "No duplicate diagnostic or ambiguity metadata leaks into healthy unique identity."
        ),
        observed={
            "nodes": [_node_summary(node) for node in nodes],
            "relations": [_relation_summary(relation) for relation in relations],
            "projection_status": model["repository_state"]["projection_status"],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else REGRESSION,
        rationale=(
            "Unique identity and its explicit relation remained clean."
            if survives
            else "Duplicate-remediation ambiguity leaked into a healthy unique fixture."
        ),
    )


def _r10_combined_wound() -> dict[str, Any]:
    model = _project_nodes(
        [
            _node(
                "PR-001",
                title="Same title",
                history_heading="Earlier outcomes",
            ),
            _node(
                "PR-001",
                title="Same title",
                pressure="Can the cleaner occurrence remain non-canonical?",
                standing="OPEN",
            ),
        ]
    )
    observation = _duplicate_observation(model, "PR-001")
    unsupported = _diagnostics_for(
        model,
        kind="unsupported_structure",
        object_id="PR-001",
        field="resolution_history",
    )
    survives = (
        _duplicates_survive(
            observation,
            expected_count=2,
            expected_standings=["BOUNDED_RESOLUTION", "OPEN"],
        )
        and len(unsupported) == 1
        and len(unsupported[0].get("raw_value", [])) == 2
        and all(node["resolution_history"] == [] for node in observation["nodes"])
        and model["repository_state"]["projection_status"] == "partial"
    )
    return _scenario(
        scenario_id="R10",
        title="combined P8 and P11 wound",
        mutation=(
            "Combined duplicate PR-001 occurrences with unsupported structured history "
            "residue on one occurrence."
        ),
        expected_discriminator=(
            "Both diagnostics survive independently and neither occurrence becomes canonical."
        ),
        observed={
            "nodes": [_node_summary(node) for node in observation["nodes"]],
            "duplicate_diagnostic_count": len(observation["diagnostics"]),
            "unsupported_history_diagnostic_count": len(unsupported),
            "projection_status": model["repository_state"]["projection_status"],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else CONTRACT_VIOLATION,
        rationale=(
            "Both wounds remained independently visible without winner selection."
            if survives
            else "One wound suppressed the other or cleaner structure acquired authority."
        ),
    )


def _r11_current_repository_smoke(
    repo_root: Path,
    *,
    source_ref: str,
    freshness_ref: str | None,
) -> dict[str, Any]:
    model = build_projection(
        repo_root,
        source_ref=source_ref,
        freshness_ref=freshness_ref,
        projection_time=PROJECTION_TIME,
    )
    nodes_by_id = {node["id"]: node for node in model["pressure_nodes"]}
    active = model["repository_state"]["current_navigation"]["active_pressure"]
    pr018 = nodes_by_id.get("PR-018")
    pr019 = nodes_by_id.get("PR-019")
    controller = next(
        (
            document
            for document in model["projection_documents"]
            if document["source_path"] == "docs/projection/Controller.md"
        ),
        None,
    )
    history = (
        [
            {"id": item["id"], "standing": item["standing"]["value"]}
            for item in pr019["resolution_history"]
        ]
        if pr019 is not None
        else []
    )
    diagnostic_kinds = [item["kind"] for item in model["projection_diagnostics"]]
    ambiguous_relations = [
        relation
        for relation in model["pressure_relations"]
        if "target_resolution" in relation
    ]
    survives = (
        model["repository_state"]["projection_status"] == "complete"
        and model["repository_state"]["freshness"]["status"] == "current"
        and active["value"] is None
        and active["status"] == "agreement"
        and active["semantic_status"] == "explicit_none"
        and pr018 is not None
        and pr018["standing"]["value"] == "OPEN"
        and active["value"] != "PR-018"
        and pr019 is not None
        and pr019["standing"]["value"] == "BOUNDED_RESOLUTION"
        and history
        == [
            {"id": "R0", "standing": "BASIS_INSUFFICIENT"},
            {"id": "R1", "standing": "BOUNDED_RESOLUTION"},
        ]
        and len(model["constraints"]) == 46
        and controller is not None
        and controller["classification"] == "projection_document"
        and controller["standing"]["value"] == "PARKED"
        and "duplicate_pressure_id" not in diagnostic_kinds
        and not any(
            item["kind"] == "unsupported_structure"
            and item["affected"].get("field") == "resolution_history"
            for item in model["projection_diagnostics"]
        )
        and "parse_failure" not in diagnostic_kinds
        and ambiguous_relations == []
    )
    return _scenario(
        scenario_id="R11",
        title="current repository smoke",
        mutation="Projected the exact authoritative starting commit against origin/main.",
        expected_discriminator=(
            "The healthy current specimen remains complete, current, semantically unchanged, "
            "and free of remediation diagnostics or relation ambiguity."
        ),
        observed={
            "source_commit": model["repository_state"]["source_commit"],
            "freshness": model["repository_state"]["freshness"],
            "projection_status": model["repository_state"]["projection_status"],
            "active_pressure": active,
            "pressure_node_count": len(model["pressure_nodes"]),
            "pressure_relation_count": len(model["pressure_relations"]),
            "constraint_count": len(model["constraints"]),
            "evidence_reference_count": len(model["evidence_refs"]),
            "projection_document_count": len(model["projection_documents"]),
            "pr018": (
                {
                    "standing": pr018["standing"],
                    "active": active["value"] == "PR-018",
                }
                if pr018 is not None
                else None
            ),
            "pr019": (
                {"standing": pr019["standing"], "resolution_history": history}
                if pr019 is not None
                else None
            ),
            "controller": (
                {
                    "classification": controller["classification"],
                    "standing": controller["standing"],
                }
                if controller is not None
                else None
            ),
            "relations_with_target_resolution": [
                _relation_summary(relation) for relation in ambiguous_relations
            ],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else REGRESSION,
        rationale=(
            "The authoritative healthy repository projection remained clean."
            if survives
            else "The current supported repository specimen regressed or became ambiguous."
        ),
    )


def _r12_three_way_duplicate() -> dict[str, Any]:
    model = _project_nodes(
        [
            _node("PR-001", title="Occurrence A"),
            _node("PR-001", title="Occurrence B", standing="OPEN"),
            _node("PR-001", title="Occurrence C", standing="PARTIAL_RESOLUTION"),
            _node("PR-003", blocked_by="PR-001"),
        ]
    )
    observation = _duplicate_observation(model, "PR-001")
    relations = [
        relation
        for relation in model["pressure_relations"]
        if relation["source_pressure_id"] == "PR-003"
        and relation["target_pressure_id"] == "PR-001"
    ]
    survives = (
        _duplicates_survive(
            observation,
            expected_count=3,
            expected_standings=[
                "BOUNDED_RESOLUTION",
                "OPEN",
                "PARTIAL_RESOLUTION",
            ],
        )
        and len(relations) == 1
        and relations[0].get("target_resolution")
        == {"status": "ambiguous", "candidate_count": 3}
    )
    return _scenario(
        scenario_id="R12",
        title="three-way duplicate",
        mutation="Created three current PR-001 occurrences and one explicit reference from PR-003.",
        expected_discriminator=(
            "All three occurrences survive, one duplicate condition remains, and the explicit "
            "target reports three candidates without a winner."
        ),
        observed={
            "nodes": [_node_summary(node) for node in observation["nodes"]],
            "source_lines": observation["source_lines"],
            "relations": [_relation_summary(relation) for relation in relations],
        },
        diagnostics=_diagnostics(model),
        classification=SURVIVES if survives else CONTRACT_VIOLATION,
        rationale=(
            "Three-way ambiguity remained occurrence-preserving and unresolved."
            if survives
            else "Three-way ambiguity collapsed, multiplied conditions, or selected a winner."
        ),
    )


def run(
    repo_root: str | Path,
    *,
    source_ref: str = "HEAD",
    freshness_ref: str | None = "origin/main",
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    scenarios = [
        _r1_original_history_wound(),
        _r2_nearby_history_heading(),
        _r3_healthy_history_control(),
        _r4_history_like_prose(),
        _r5_original_duplicate_replay(),
        _r6_identical_duplicate_headings(),
        _r7_duplicate_relation_target(),
        _r8_duplicate_without_relation(),
        _r9_unique_control(),
        _r10_combined_wound(),
        _r11_current_repository_smoke(
            root,
            source_ref=source_ref,
            freshness_ref=freshness_ref,
        ),
        _r12_three_way_duplicate(),
    ]
    counts = {
        classification: sum(
            scenario["classification"] == classification for scenario in scenarios
        )
        for classification in CLASSIFICATIONS
    }
    required_survived = all(
        scenario["classification"] == SURVIVES for scenario in scenarios
    )
    return {
        "repressure_version": REPRESSURE_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "predeclared_classification": PREDECLARED_CLASSIFICATION,
        "scenarios": scenarios,
        "classification_counts": counts,
        "adjudication": {
            "status": (
                "bounded_repressure_survived"
                if required_survived
                else "bounded_repressure_exposed_unresolved_wound"
            ),
            "strongest_supported": (
                "The remediated adapter survived the named original and nearby P8/P11 "
                "re-pressure specimens without silent loss, winner selection, or "
                "healthy-source regression."
                if required_survived
                else "Only the scenarios individually classified SURVIVES are supported."
            ),
            "strongest_not_supported": (
                "General projection safety, general Markdown robustness, arbitrary malformed-"
                "input safety, generalized graph correctness, and generalized identity "
                "correctness remain unsupported."
            ),
            "ui_authorized_next": required_survived,
            "ui_scope": (
                "first bounded plain read-only observer specimen over the normalized model"
                if required_survived
                else None
            ),
            "adapter_changed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--source-ref", default="HEAD")
    parser.add_argument("--freshness-ref", default="origin/main")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    result = run(
        args.repo,
        source_ref=args.source_ref,
        freshness_ref=args.freshness_ref,
    )
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
