"""Run bounded named wounds against the Cockpit projection adapter v0."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from typing import Any, Iterator

from src.cockpit.projection_adapter import ADAPTER_VERSION, build_projection


PRESSURE_VERSION = "cockpit_projection_adapter_pressure_v0"
PROJECTION_TIME = "2026-09-09T20:00:00Z"

SURVIVES = "SURVIVES"
CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
BASIS_INSUFFICIENT = "BASIS_INSUFFICIENT"
CONTRACT_AMBIGUITY = "CONTRACT_AMBIGUITY"

PREDECLARED_RULE = {
    "survives": (
        "The changed or ambiguous condition remains recoverably visible in "
        "normalized output or diagnostics and is not strengthened."
    ),
    "contract_violation": (
        "The adapter emits a plausible clean projection while materially hiding, "
        "inventing, collapsing, or strengthening the tested source condition."
    ),
    "basis_insufficient": (
        "The committed fixture or retained observation cannot discriminate the "
        "intended behavior."
    ),
}


def _git(root: Path, *args: str, commit_number: int = 0) -> str:
    environment = os.environ.copy()
    timestamp = f"2001-01-01T00:{commit_number:02d}:00+00:00"
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
        _git(root, "config", "user.name", "DME Pressure")
        _git(root, "config", "user.email", "dme-pressure@example.invalid")
        _git(root, "remote", "add", "origin", "https://github.com/example/cockpit-pressure.git")

    def write(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def remove(self, relative_path: str) -> None:
        (self.root / relative_path).unlink()

    def commit(self, message: str) -> str:
        _git(self.root, "add", "-A")
        commit = _git(
            self.root,
            "commit",
            "-m",
            message,
            commit_number=self.commit_number,
        )
        del commit
        self.commit_number += 1
        return _git(self.root, "rev-parse", "HEAD")


@contextmanager
def _specimen(**options: Any) -> Iterator[_Specimen]:
    with TemporaryDirectory() as tmpdir:
        specimen = _Specimen(Path(tmpdir))
        for path, content in _base_files(**options).items():
            specimen.write(path, content)
        yield specimen


def _node(
    pressure_id: str,
    *,
    title: str = "Bounded specimen",
    pressure: str = "Can the bounded source condition remain visible?",
    standing: str = "`BOUNDED_RESOLUTION`",
    standing_line: str | None = None,
    blocked_by: str = "—",
    unlocks: str = "—",
    evidence: str = "[decision](docs/decisions/existing.md)",
    history_heading: str | None = None,
) -> str:
    rendered_standing = standing_line or f"- **Standing:** {standing}"
    value = f"""### {pressure_id} — {title}

- **Pressure:** {pressure}
{rendered_standing}
- **Missing discriminator:** —
- **Resolution so far:** The result remains bounded.
- **Residue:** Generalization remains unearned.
- **Blocked by:** {blocked_by}
- **Unlocks:** {unlocks}
- **Evidence:** {evidence}
"""
    if history_heading is not None:
        value += f"""
#### {pressure_id} — {history_heading}

- **R0 — `BASIS_INSUFFICIENT`:** The first basis did not discriminate.
- **R1 — `BOUNDED_RESOLUTION`:** The second bounded basis discriminated.
"""
    return value


def _constraint(identifier: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "left": f"left_{identifier}",
        "relation": "not_equivalent_to",
        "right": f"right_{identifier}",
        "scope": "cockpit_projection_adapter_pressure_v0",
        "basis": "design_constraint",
        "provenance": ["docs/decisions/existing.md"],
        "standing": "supported",
        "note": "Bounded pressure fixture constraint.",
    }


def _project_state(active: str = "none") -> str:
    return f"""# Project State

## Current Navigation and Development Standing

- Active experimental pressure: {active}.
- PR-018 remains `OPEN` under its bounded blocker.
- No next experimental pressure has been selected.

The DME Cockpit is authorized as read-only projection work. The Controller
remains parked.
"""


def _pressure_map(
    *,
    active: str = "none",
    first_node: str | None = None,
    extra_nodes: str = "",
) -> str:
    return f"""# Pressure / Resolution Map v0

## Current Navigation

Active pressure: {active}

Newly reachable / open:

- PR-018 — prospective bounded question

Shelved:

## A. Bounded adapter pressure fixtures

{first_node or _node('PR-001')}

{_node('PR-002')}

{_node('PR-018', standing='`OPEN`')}

{extra_nodes}
"""


def _base_files(
    *,
    project_active: str = "none",
    map_active: str = "none",
    first_node: str | None = None,
    extra_nodes: str = "",
    registry_lines: list[str] | None = None,
    controller_extra: str = "",
    omit_map: bool = False,
) -> dict[str, str]:
    registry = registry_lines or [json.dumps(_constraint("D-0001"), sort_keys=True)]
    files = {
        "PROJECT_STATE.md": _project_state(project_active),
        "docs/constraints/README.md": (
            "# Constraint Registry\n\nconstraint != local distinction event\n"
        ),
        "docs/constraints/registry.jsonl": "\n".join(registry) + "\n",
        "docs/decisions/existing.md": "# Existing bounded evidence\n",
        "docs/projection/Controller.md": (
            "# Controller\n\n> Non-authoritative projection.\n\n"
            f"{controller_extra}\n\n## Standing\n\nPARKED.\n"
        ),
        "docs/projection/Persistent_Ecology.md": (
            "# Persistent Ecology\n\n> Non-authoritative projection.\n\n"
            "## Epistemic Status\n\nProjected only.\n"
        ),
        "docs/projection/Persistent_Research_Autonomy.md": (
            "# Persistent Research Autonomy\n\n> Non-authoritative projection.\n\n"
            "## Current Standing\n\nThis question is shelved.\n"
        ),
    }
    if not omit_map:
        files["PRESSURE_RESOLUTION_MAP.md"] = _pressure_map(
            active=map_active,
            first_node=first_node,
            extra_nodes=extra_nodes,
        )
    return files


def _projection(specimen: _Specimen, source_ref: str = "HEAD", freshness_ref: str = "HEAD") -> dict[str, Any]:
    return build_projection(
        specimen.root,
        source_ref=source_ref,
        freshness_ref=freshness_ref,
        projection_time=PROJECTION_TIME,
    )


def _diagnostic_kinds(model: dict[str, Any]) -> list[str]:
    return [item["kind"] for item in model["projection_diagnostics"]]


def _compact_diagnostics(model: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "kind": item["kind"],
            "affected": item["affected"],
            "message": item["message"],
            **({"raw_value": item["raw_value"]} if "raw_value" in item else {}),
        }
        for item in model["projection_diagnostics"]
    ]


def _scenario_result(
    *,
    scenario_id: str,
    title: str,
    mutation: str,
    intended_discriminator: str,
    observed: dict[str, Any],
    diagnostics: list[dict[str, Any]],
    classification: str,
    rationale: str,
) -> dict[str, Any]:
    return {
        "id": scenario_id,
        "title": title,
        "mutation": mutation,
        "intended_discriminator": intended_discriminator,
        "observed": observed,
        "diagnostics": diagnostics,
        "classification": classification,
        "rationale": rationale,
    }


def _p1_missing_required_source() -> dict[str, Any]:
    with _specimen(omit_map=True) as specimen:
        source_commit = specimen.commit("P1 missing required map")
        model = _projection(specimen)
    visible = (
        "missing_required_source" in _diagnostic_kinds(model)
        and model["repository_state"]["projection_status"] in {"partial", "failed"}
        and any(
            item["source_path"] == "PRESSURE_RESOLUTION_MAP.md"
            and item["status"] == "missing"
            for item in model["repository_state"]["source_surfaces"]
        )
    )
    return _scenario_result(
        scenario_id="P1",
        title="missing required source",
        mutation="Omitted PRESSURE_RESOLUTION_MAP.md from the committed tree.",
        intended_discriminator="Missing map must remain visible and projection must not appear complete.",
        observed={
            "source_commit": source_commit,
            "projection_status": model["repository_state"]["projection_status"],
            "pressure_nodes": len(model["pressure_nodes"]),
            "source_surfaces": model["repository_state"]["source_surfaces"],
        },
        diagnostics=_compact_diagnostics(model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "The absent required map remained explicit and the projection was partial."
            if visible
            else "The missing required source was not recoverably exposed."
        ),
    )


def _p2_unknown_standing() -> dict[str, Any]:
    wounded = _node("PR-001", standing="`GOBLIN_PENDING`")
    with _specimen(first_node=wounded) as specimen:
        specimen.commit("P2 unknown standing")
        model = _projection(specimen)
    node = next(item for item in model["pressure_nodes"] if item["id"] == "PR-001")
    visible = (
        node["standing"]["value"] == "GOBLIN_PENDING"
        and node["standing"]["status"] == "unknown_standing"
        and "unknown_standing" in _diagnostic_kinds(model)
    )
    return _scenario_result(
        scenario_id="P2",
        title="unknown pressure standing",
        mutation="Set PR-001 standing to the unrecognized token GOBLIN_PENDING.",
        intended_discriminator="The exact token must survive without nearest-standing substitution.",
        observed={"standing": node["standing"]},
        diagnostics=_compact_diagnostics(model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "The raw unknown token and diagnostic were preserved."
            if visible
            else "The unknown standing was cleaned or lost."
        ),
    )


def _p3_broken_reference() -> dict[str, Any]:
    target = "docs/decisions/not-present.md"
    wounded = _node("PR-001", evidence=f"[missing]({target})")
    with _specimen(first_node=wounded) as specimen:
        specimen.commit("P3 broken evidence reference")
        model = _projection(specimen)
    references = [item for item in model["evidence_refs"] if item["original_target"] == target]
    visible = (
        len(references) == 1
        and references[0]["resolution_status"] == "broken"
        and "broken_reference" in _diagnostic_kinds(model)
    )
    return _scenario_result(
        scenario_id="P3",
        title="broken evidence reference",
        mutation="Pointed PR-001 Evidence to a nonexistent committed decision path.",
        intended_discriminator="The reference must remain navigable residue with broken status and diagnostic.",
        observed={"matching_references": references},
        diagnostics=_compact_diagnostics(model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "The broken occurrence remained represented without warrant inflation."
            if visible
            else "The broken evidence occurrence disappeared or appeared resolved."
        ),
    )


def _p4_source_conflict() -> dict[str, Any]:
    with _specimen(project_active="PR-018", map_active="none") as specimen:
        specimen.commit("P4 current navigation conflict")
        model = _projection(specimen)
    active = model["repository_state"]["current_navigation"]["active_pressure"]
    declaration_values = [item["raw_value"] for item in active["declarations"]]
    visible = (
        active["status"] == "conflicting"
        and active["value"] is None
        and declaration_values == ["none", "PR-018"]
        and "source_conflict" in _diagnostic_kinds(model)
    )
    return _scenario_result(
        scenario_id="P4",
        title="source conflict",
        mutation="Map declared no active pressure while PROJECT_STATE declared PR-018 active.",
        intended_discriminator="Both declarations and unresolved conflict must survive without a selected winner.",
        observed={"active_pressure": active},
        diagnostics=_compact_diagnostics(model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "Both active-pressure claims remained visible and no clean winner was selected."
            if visible
            else "The current-navigation disagreement was hidden or resolved without authority."
        ),
    )


def _p5_relation_looking_prose() -> dict[str, Any]:
    prose_node = _node(
        "PR-001",
        pressure="PR-002 may be relevant historically, without an established relation.",
    )
    with _specimen(first_node=prose_node) as specimen:
        specimen.commit("P5 relation-looking prose")
        wound_model = _projection(specimen)
        explicit_node = _node(
            "PR-001",
            pressure="PR-002 may be relevant historically, without an established relation.",
            blocked_by="PR-002",
        )
        specimen.write("PRESSURE_RESOLUTION_MAP.md", _pressure_map(first_node=explicit_node))
        specimen.commit("P5 explicit relation control")
        control_model = _projection(specimen)
    wound_relations = [
        item for item in wound_model["pressure_relations"] if item["source_pressure_id"] == "PR-001"
    ]
    control_relations = [
        item for item in control_model["pressure_relations"] if item["source_pressure_id"] == "PR-001"
    ]
    visible = (
        wound_relations == []
        and len(control_relations) == 1
        and control_relations[0]["target_pressure_id"] == "PR-002"
    )
    return _scenario_result(
        scenario_id="P5",
        title="relation-looking prose",
        mutation="Mentioned PR-002 in Pressure prose with absent relation fields, then committed an explicit Blocked by control.",
        intended_discriminator="Incidental prose must create no edge while the explicit field creates exactly one.",
        observed={
            "prose_specimen_relations": wound_relations,
            "explicit_control_relations": control_relations,
        },
        diagnostics=_compact_diagnostics(wound_model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "Only the explicit Blocked by field produced a relation."
            if visible
            else "Relation-looking prose affected normalized graph structure."
        ),
    )


def _p6_malformed_pressure_structure() -> dict[str, Any]:
    wounded = _node(
        "PR-001",
        standing_line="- **Standing** `OPEN`",
    )
    with _specimen(first_node=wounded) as specimen:
        specimen.commit("P6 malformed standing field")
        model = _projection(specimen)
    node = next(item for item in model["pressure_nodes"] if item["id"] == "PR-001")
    other = next(item for item in model["pressure_nodes"] if item["id"] == "PR-002")
    visible = (
        node["standing"]["status"] == "missing"
        and node["standing"]["value"] is None
        and "parse_failure" in _diagnostic_kinds(model)
        and other["standing"]["value"] == "BOUNDED_RESOLUTION"
    )
    return _scenario_result(
        scenario_id="P6",
        title="malformed pressure structure",
        mutation="Removed the required colon from the PR-001 Standing field marker.",
        intended_discriminator="Parser narrowness must be visible while PR-002 remains independently projectable.",
        observed={
            "wounded_standing": node["standing"],
            "other_node_standing": other["standing"],
            "projection_status": model["repository_state"]["projection_status"],
        },
        diagnostics=_compact_diagnostics(model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "The malformed field became explicit missingness and did not contaminate the valid node."
            if visible
            else "Malformed structure yielded a plausible standing or vanished silently."
        ),
    )


def _p7_malformed_constraint_record() -> dict[str, Any]:
    lines = [
        json.dumps(_constraint("D-0001"), sort_keys=True),
        "{malformed",
        json.dumps(_constraint("D-0002"), sort_keys=True),
    ]
    with _specimen(registry_lines=lines) as specimen:
        specimen.commit("P7 malformed constraint among valid records")
        model = _projection(specimen)
    identifiers = [item["id"] for item in model["constraints"]]
    visible = (
        identifiers == ["D-0001", "D-0002"]
        and "parse_failure" in _diagnostic_kinds(model)
        and model["repository_state"]["projection_status"] == "partial"
    )
    return _scenario_result(
        scenario_id="P7",
        title="malformed constraint among valid records",
        mutation="Committed valid D-0001, malformed JSON, then valid D-0002.",
        intended_discriminator="Both valid records and malformed-line residue must remain separately visible.",
        observed={
            "constraint_ids": identifiers,
            "projection_status": model["repository_state"]["projection_status"],
        },
        diagnostics=_compact_diagnostics(model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "Both valid constraints survived and the malformed line remained diagnostic residue."
            if visible
            else "The malformed line or neighboring valid records were silently lost."
        ),
    )


def _p8_resolution_history_wound() -> dict[str, Any]:
    healthy_node = _node("PR-001", history_heading="Resolution history")
    with _specimen(first_node=healthy_node) as specimen:
        specimen.commit("P8 healthy resolution history control")
        healthy_model = _projection(specimen)
        damaged_map = _pressure_map(
            first_node=_node("PR-001", history_heading="Prior resolutions")
        )
        specimen.write("PRESSURE_RESOLUTION_MAP.md", damaged_map)
        specimen.commit("P8 damaged resolution history heading")
        damaged_model = _projection(specimen)
    healthy = next(item for item in healthy_model["pressure_nodes"] if item["id"] == "PR-001")
    damaged = next(item for item in damaged_model["pressure_nodes"] if item["id"] == "PR-001")
    historical_wound_hidden = (
        [item["standing"]["value"] for item in healthy["resolution_history"]]
        == ["BASIS_INSUFFICIENT", "BOUNDED_RESOLUTION"]
        and damaged["standing"]["value"] == "BOUNDED_RESOLUTION"
        and damaged["resolution_history"] == []
        and not any(
            item["kind"] in {"parse_failure", "unsupported_structure"}
            and item["affected"].get("object_id") == "PR-001"
            for item in damaged_model["projection_diagnostics"]
        )
    )
    classification = CONTRACT_VIOLATION if historical_wound_hidden else SURVIVES
    return _scenario_result(
        scenario_id="P8",
        title="resolution-history wound",
        mutation="Renamed only the recognized Resolution history heading to Prior resolutions; retained both visible R entries.",
        intended_discriminator="Unrecognized history-like structure must not disappear behind a clean current standing without residue.",
        observed={
            "healthy_current_standing": healthy["standing"],
            "healthy_history": [
                {"id": item["id"], "standing": item["standing"]["value"]}
                for item in healthy["resolution_history"]
            ],
            "damaged_current_standing": damaged["standing"],
            "damaged_history": damaged["resolution_history"],
        },
        diagnostics=_compact_diagnostics(damaged_model),
        classification=classification,
        rationale=(
            "Visible history-like source material was silently omitted while current BOUNDED_RESOLUTION remained clean."
            if historical_wound_hidden
            else "The damaged historical wound remained visibly represented."
        ),
    )


def _p9_stale_projection_basis() -> dict[str, Any]:
    with _specimen(first_node=_node("PR-001", standing="`BOUNDED_RESOLUTION`")) as specimen:
        commit_a = specimen.commit("P9 source commit A")
        specimen.write(
            "PRESSURE_RESOLUTION_MAP.md",
            _pressure_map(first_node=_node("PR-001", standing="`OPEN`")),
        )
        commit_b = specimen.commit("P9 freshness commit B")
        model = _projection(specimen, source_ref=commit_a, freshness_ref=commit_b)
    node = next(item for item in model["pressure_nodes"] if item["id"] == "PR-001")
    freshness = model["repository_state"]["freshness"]
    visible = (
        model["repository_state"]["source_commit"] == commit_a
        and freshness["observed_tail"] == commit_b
        and freshness["status"] == "stale"
        and node["standing"]["value"] == "BOUNDED_RESOLUTION"
    )
    return _scenario_result(
        scenario_id="P9",
        title="stale projection basis",
        mutation="Projected commit A after a later commit B changed PR-001 on the freshness ref.",
        intended_discriminator="Freshness must be stale while normalized source content remains commit A.",
        observed={
            "source_commit": model["repository_state"]["source_commit"],
            "observed_tail": freshness["observed_tail"],
            "freshness_status": freshness["status"],
            "projected_pr001_standing": node["standing"]["value"],
        },
        diagnostics=_compact_diagnostics(model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "The adapter labeled A stale against B and continued to project A's content."
            if visible
            else "Freshness time or tail content displaced the declared source basis."
        ),
    )


def _p10_projection_document_containment() -> dict[str, Any]:
    extra = """### PR-999 — Imaginary Pressure

ACTIVE PIPELINE
SUPER_CONTROLLER
RUNNING
"""
    with _specimen(controller_extra=extra) as specimen:
        specimen.commit("P10 speculative projection content")
        model = _projection(specimen)
    controller = next(
        item
        for item in model["projection_documents"]
        if item["source_path"] == "docs/projection/Controller.md"
    )
    generated_999 = any(item["id"] == "PR-999" for item in model["pressure_nodes"])
    relation_999 = any(
        item["source_pressure_id"] == "PR-999" or item["target_pressure_id"] == "PR-999"
        for item in model["pressure_relations"]
    )
    active = model["repository_state"]["current_navigation"]["active_pressure"]
    visible = (
        controller["classification"] == "projection_document"
        and controller["standing"]["value"] == "PARKED"
        and not generated_999
        and not relation_999
        and active["semantic_status"] == "explicit_none"
    )
    return _scenario_result(
        scenario_id="P10",
        title="projection document containment",
        mutation="Inserted PR-999, ACTIVE PIPELINE, SUPER_CONTROLLER, and RUNNING prose into the non-authoritative Controller projection.",
        intended_discriminator="Speculative projection text must create no earned pressure, relation, active state, or authority.",
        observed={
            "controller_classification": controller["classification"],
            "controller_standing": controller["standing"],
            "pr999_node_created": generated_999,
            "pr999_relation_created": relation_999,
            "active_pressure": active,
        },
        diagnostics=_compact_diagnostics(model),
        classification=SURVIVES if visible else CONTRACT_VIOLATION,
        rationale=(
            "The allowlisted document remained a parked projection and its internal prose was contained."
            if visible
            else "Projection prose crossed the evidence horizon into earned normalized state."
        ),
    )


def _p11_duplicate_pressure_id() -> dict[str, Any]:
    duplicate = _node(
        "PR-001",
        title="Conflicting duplicate",
        standing="`OPEN`",
        pressure="Does a duplicate pressure identity remain visible?",
    )
    with _specimen(extra_nodes=duplicate) as specimen:
        specimen.commit("P11 duplicate pressure identity")
        model = _projection(specimen)
    duplicates = [item for item in model["pressure_nodes"] if item["id"] == "PR-001"]
    visible = len(duplicates) == 2
    if visible:
        classification = CONTRACT_AMBIGUITY
        rationale = (
            "Both duplicate nodes remain visible, but the contract does not define duplicate-ID "
            "validity, conflict diagnostics, or consumer semantics."
        )
    else:
        classification = CONTRACT_VIOLATION
        rationale = "Duplicate identity collapsed into a single plausible node without residue."
    return _scenario_result(
        scenario_id="P11",
        title="duplicate pressure ID",
        mutation="Committed two explicit PR-001 headings with different titles and standings.",
        intended_discriminator="Duplicate identity must not silently collapse; unspecified handling remains contract ambiguity.",
        observed={
            "matching_node_count": len(duplicates),
            "matching_nodes": [
                {"title": item["title"], "standing": item["standing"]}
                for item in duplicates
            ],
        },
        diagnostics=_compact_diagnostics(model),
        classification=classification,
        rationale=rationale,
    )


def _baseline_summary(model: dict[str, Any]) -> dict[str, Any]:
    by_id = {item["id"]: item for item in model["pressure_nodes"]}
    controller = next(
        (
            item
            for item in model["projection_documents"]
            if item["source_path"] == "docs/projection/Controller.md"
        ),
        None,
    )
    active = model["repository_state"]["current_navigation"]["active_pressure"]
    pr018 = by_id.get("PR-018")
    pr019 = by_id.get("PR-019")
    diagnostics_by_kind: dict[str, int] = {}
    for diagnostic in model["projection_diagnostics"]:
        kind = diagnostic["kind"]
        diagnostics_by_kind[kind] = diagnostics_by_kind.get(kind, 0) + 1
    return {
        "source_commit": model["repository_state"]["source_commit"],
        "freshness": model["repository_state"]["freshness"],
        "active_pressure": active,
        "pressure_node_count": len(model["pressure_nodes"]),
        "pressure_relation_count": len(model["pressure_relations"]),
        "constraint_count": len(model["constraints"]),
        "evidence_reference_count": len(model["evidence_refs"]),
        "projection_document_count": len(model["projection_documents"]),
        "diagnostic_counts": diagnostics_by_kind,
        "pr018": (
            {
                "standing": pr018["standing"],
                "active": active["value"] == "PR-018",
            }
            if pr018
            else None
        ),
        "pr019": (
            {
                "standing": pr019["standing"],
                "resolution_history": [
                    {"id": item["id"], "standing": item["standing"]}
                    for item in pr019["resolution_history"]
                ],
            }
            if pr019
            else None
        ),
        "controller": (
            {
                "classification": controller["classification"],
                "standing": controller["standing"],
            }
            if controller
            else None
        ),
    }


def run(
    repo_root: str | Path,
    *,
    source_ref: str = "HEAD",
    freshness_ref: str | None = "origin/main",
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    baseline_model = build_projection(
        root,
        source_ref=source_ref,
        freshness_ref=freshness_ref,
        projection_time=PROJECTION_TIME,
    )
    scenarios = [
        _p1_missing_required_source(),
        _p2_unknown_standing(),
        _p3_broken_reference(),
        _p4_source_conflict(),
        _p5_relation_looking_prose(),
        _p6_malformed_pressure_structure(),
        _p7_malformed_constraint_record(),
        _p8_resolution_history_wound(),
        _p9_stale_projection_basis(),
        _p10_projection_document_containment(),
        _p11_duplicate_pressure_id(),
    ]
    counts = {
        classification: sum(
            item["classification"] == classification for item in scenarios
        )
        for classification in (
            SURVIVES,
            CONTRACT_VIOLATION,
            BASIS_INSUFFICIENT,
            CONTRACT_AMBIGUITY,
        )
    }
    return {
        "pressure_version": PRESSURE_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "predeclared_semantic_rule": deepcopy(PREDECLARED_RULE),
        "baseline": _baseline_summary(baseline_model),
        "scenarios": scenarios,
        "classification_counts": counts,
        "adjudication": {
            "status": "bounded_adapter_pressure_exposed_unresolved_wound",
            "strongest_supported": (
                "Across the named bounded specimens, the adapter preserved required-source "
                "absence, unknown standing, broken links, explicit source conflict, explicit-only "
                "relations, malformed fields and JSONL residue, stale commit basis, and projection "
                "document containment."
            ),
            "strongest_not_supported": (
                "The adapter is not generally contract-safe: an unrecognized but visibly "
                "history-like section can disappear while leaving a plausible clean current "
                "standing, and duplicate pressure-ID semantics remain unspecified."
            ),
            "adapter_remediated": False,
            "projection_contract_changed": False,
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
