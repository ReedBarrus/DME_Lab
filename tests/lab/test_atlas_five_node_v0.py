import copy
import json
from pathlib import Path

import pytest

from lab.ops.candidates.atlas_five_node_v0.atlas import (
    AtlasValidationError,
    build_transfer,
    load_manifest,
    parse_manifest,
    route,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    ROOT
    / "lab"
    / "ops"
    / "candidates"
    / "atlas_five_node_v0"
    / "five_node_fixture_v0.json"
)


def _raw_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_contains_exactly_five_unbound_uninstantiated_nodes():
    manifest = load_manifest(FIXTURE)

    assert len(manifest.nodes) == 5
    assert {node.node_id for node in manifest.nodes} == {
        "NODE_01",
        "NODE_02",
        "NODE_03",
        "NODE_04",
        "NODE_05",
    }
    assert all(node.role_id is None for node in manifest.nodes)
    assert all(node.authority_ref is None for node in manifest.nodes)
    assert all(node.binding_state == "UNBOUND" for node in manifest.nodes)
    assert all(node.runtime_state == "NOT_INSTANTIATED" for node in manifest.nodes)


def test_node_coordinates_are_unique():
    manifest = load_manifest(FIXTURE)
    coordinates = [node.coordinate_ref for node in manifest.nodes]
    assert len(coordinates) == len(set(coordinates))


def test_declared_multi_hop_route_is_recoverable():
    manifest = load_manifest(FIXTURE)

    selected = route(manifest, "NODE_01", "NODE_05")

    assert selected.node_path == (
        "NODE_01",
        "NODE_02",
        "NODE_03",
        "NODE_04",
        "NODE_05",
    )
    assert selected.edge_path == (
        "EDGE_01_02",
        "EDGE_02_03",
        "EDGE_03_04",
        "EDGE_04_05",
    )


def test_reverse_route_uses_independent_declared_edges():
    manifest = load_manifest(FIXTURE)

    selected = route(manifest, "NODE_05", "NODE_01")

    assert selected.edge_path == (
        "EDGE_05_04",
        "EDGE_04_03",
        "EDGE_03_02",
        "EDGE_02_01",
    )


def test_unknown_node_is_not_inferred():
    manifest = load_manifest(FIXTURE)

    with pytest.raises(AtlasValidationError, match="unknown node_id"):
        route(manifest, "NODE_01", "NODE_99")


def test_edge_cannot_mint_authority():
    raw = _raw_fixture()
    raw["edges"][0]["authority_effect"] = "GRANT"

    with pytest.raises(AtlasValidationError, match="may not mint authority"):
        parse_manifest(raw)


def test_edge_cannot_invoke_execution():
    raw = _raw_fixture()
    raw["edges"][0]["execution_effect"] = "RUN"

    with pytest.raises(AtlasValidationError, match="may not invoke execution"):
        parse_manifest(raw)


def test_duplicate_coordinate_is_rejected():
    raw = _raw_fixture()
    raw["nodes"][1]["coordinate_ref"] = raw["nodes"][0]["coordinate_ref"]

    with pytest.raises(AtlasValidationError, match="duplicate coordinate_ref"):
        parse_manifest(raw)


def test_transfer_identity_is_deterministic_and_manifest_bound():
    manifest = load_manifest(FIXTURE)

    first = build_transfer(
        manifest,
        source_node_id="NODE_01",
        target_node_id="NODE_05",
        payload_refs=("commit:abc123", "artifact:def456"),
    )
    second = build_transfer(
        manifest,
        source_node_id="NODE_01",
        target_node_id="NODE_05",
        payload_refs=("commit:abc123", "artifact:def456"),
    )

    assert first.transfer_id == second.transfer_id
    assert first.manifest_digest == manifest.manifest_digest


def test_transfer_has_no_authority_execution_or_standing_effect():
    manifest = load_manifest(FIXTURE)

    transfer = build_transfer(
        manifest,
        source_node_id="NODE_02",
        target_node_id="NODE_04",
        payload_refs=("ref:one",),
    )

    assert transfer.authority_changed is False
    assert transfer.execution_invoked is False
    assert transfer.standing_changed is False


def test_reverse_transfer_is_not_same_coordinate_identity():
    manifest = load_manifest(FIXTURE)

    forward = build_transfer(
        manifest,
        source_node_id="NODE_01",
        target_node_id="NODE_02",
    )
    reverse = build_transfer(
        manifest,
        source_node_id="NODE_02",
        target_node_id="NODE_01",
    )

    assert forward.transfer_id != reverse.transfer_id
    assert forward.source_coordinate_ref == reverse.target_coordinate_ref
    assert forward.target_coordinate_ref == reverse.source_coordinate_ref


def test_role_binding_is_outside_candidate_surface():
    raw = copy.deepcopy(_raw_fixture())
    raw["nodes"][0]["role_id"] = "COMMANDER"

    with pytest.raises(AtlasValidationError, match="role binding"):
        parse_manifest(raw)
