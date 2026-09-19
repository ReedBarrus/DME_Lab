from __future__ import annotations

import hashlib
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "atlas_five_node_manifest_v0"
TRANSFER_SCHEMA_VERSION = "atlas_transfer_envelope_v0"
TRANSFER_EFFECT = "TRANSFER_ONLY"
NO_EFFECT = "NONE"


class AtlasValidationError(ValueError):
    """Raised when a candidate Atlas manifest or transfer is malformed."""


@dataclass(frozen=True)
class AtlasNode:
    node_id: str
    coordinate_ref: str
    role_id: str | None
    binding_state: str
    runtime_state: str
    authority_ref: str | None


@dataclass(frozen=True)
class AtlasEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    transition_kind: str
    authority_effect: str
    execution_effect: str


@dataclass(frozen=True)
class AtlasManifest:
    schema_version: str
    manifest_id: str
    nodes: tuple[AtlasNode, ...]
    edges: tuple[AtlasEdge, ...]
    manifest_digest: str


@dataclass(frozen=True)
class Route:
    source_node_id: str
    target_node_id: str
    node_path: tuple[str, ...]
    edge_path: tuple[str, ...]


@dataclass(frozen=True)
class TransferEnvelope:
    schema_version: str
    transfer_id: str
    manifest_id: str
    manifest_digest: str
    source_node_id: str
    target_node_id: str
    source_coordinate_ref: str
    target_coordinate_ref: str
    route_node_path: tuple[str, ...]
    route_edge_path: tuple[str, ...]
    payload_refs: tuple[str, ...]
    authority_changed: bool
    execution_invoked: bool
    standing_changed: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "transfer_id": self.transfer_id,
            "manifest_id": self.manifest_id,
            "manifest_digest": self.manifest_digest,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "source_coordinate_ref": self.source_coordinate_ref,
            "target_coordinate_ref": self.target_coordinate_ref,
            "route_node_path": list(self.route_node_path),
            "route_edge_path": list(self.route_edge_path),
            "payload_refs": list(self.payload_refs),
            "authority_changed": self.authority_changed,
            "execution_invoked": self.execution_invoked,
            "standing_changed": self.standing_changed,
        }


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise AtlasValidationError(f"{field} must be a non-empty string")
    return value


def _require_nullable_nonempty_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_nonempty_string(value, field)


def _require_exact_keys(record: Mapping[str, Any], expected: set[str], where: str) -> None:
    actual = set(record.keys())
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise AtlasValidationError(
            f"{where} keys mismatch; missing={missing}, extra={extra}"
        )


def _parse_node(raw: Mapping[str, Any], index: int) -> AtlasNode:
    expected = {
        "node_id",
        "coordinate_ref",
        "role_id",
        "binding_state",
        "runtime_state",
        "authority_ref",
    }
    _require_exact_keys(raw, expected, f"nodes[{index}]")

    node = AtlasNode(
        node_id=_require_nonempty_string(raw["node_id"], f"nodes[{index}].node_id"),
        coordinate_ref=_require_nonempty_string(
            raw["coordinate_ref"], f"nodes[{index}].coordinate_ref"
        ),
        role_id=_require_nullable_nonempty_string(
            raw["role_id"], f"nodes[{index}].role_id"
        ),
        binding_state=_require_nonempty_string(
            raw["binding_state"], f"nodes[{index}].binding_state"
        ),
        runtime_state=_require_nonempty_string(
            raw["runtime_state"], f"nodes[{index}].runtime_state"
        ),
        authority_ref=_require_nullable_nonempty_string(
            raw["authority_ref"], f"nodes[{index}].authority_ref"
        ),
    )

    if node.binding_state != "UNBOUND":
        raise AtlasValidationError(
            f"{node.node_id}: candidate fixture requires binding_state UNBOUND"
        )
    if node.runtime_state != "NOT_INSTANTIATED":
        raise AtlasValidationError(
            f"{node.node_id}: candidate fixture requires runtime_state NOT_INSTANTIATED"
        )
    if node.role_id is not None:
        raise AtlasValidationError(
            f"{node.node_id}: role binding is outside this candidate surface"
        )
    if node.authority_ref is not None:
        raise AtlasValidationError(
            f"{node.node_id}: authority binding is outside this candidate surface"
        )
    return node


def _parse_edge(raw: Mapping[str, Any], index: int) -> AtlasEdge:
    expected = {
        "edge_id",
        "source_node_id",
        "target_node_id",
        "transition_kind",
        "authority_effect",
        "execution_effect",
    }
    _require_exact_keys(raw, expected, f"edges[{index}]")

    edge = AtlasEdge(
        edge_id=_require_nonempty_string(raw["edge_id"], f"edges[{index}].edge_id"),
        source_node_id=_require_nonempty_string(
            raw["source_node_id"], f"edges[{index}].source_node_id"
        ),
        target_node_id=_require_nonempty_string(
            raw["target_node_id"], f"edges[{index}].target_node_id"
        ),
        transition_kind=_require_nonempty_string(
            raw["transition_kind"], f"edges[{index}].transition_kind"
        ),
        authority_effect=_require_nonempty_string(
            raw["authority_effect"], f"edges[{index}].authority_effect"
        ),
        execution_effect=_require_nonempty_string(
            raw["execution_effect"], f"edges[{index}].execution_effect"
        ),
    )

    if edge.source_node_id == edge.target_node_id:
        raise AtlasValidationError(f"{edge.edge_id}: self-edge is not allowed")
    if edge.transition_kind != TRANSFER_EFFECT:
        raise AtlasValidationError(
            f"{edge.edge_id}: transition_kind must be {TRANSFER_EFFECT}"
        )
    if edge.authority_effect != NO_EFFECT:
        raise AtlasValidationError(
            f"{edge.edge_id}: transfer edge may not mint authority"
        )
    if edge.execution_effect != NO_EFFECT:
        raise AtlasValidationError(
            f"{edge.edge_id}: transfer edge may not invoke execution"
        )
    return edge


def parse_manifest(raw: Mapping[str, Any]) -> AtlasManifest:
    expected = {"schema_version", "manifest_id", "nodes", "edges"}
    _require_exact_keys(raw, expected, "manifest")

    if raw["schema_version"] != SCHEMA_VERSION:
        raise AtlasValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )

    manifest_id = _require_nonempty_string(raw["manifest_id"], "manifest_id")

    nodes_raw = raw["nodes"]
    edges_raw = raw["edges"]
    if not isinstance(nodes_raw, list):
        raise AtlasValidationError("nodes must be a list")
    if not isinstance(edges_raw, list):
        raise AtlasValidationError("edges must be a list")
    if len(nodes_raw) != 5:
        raise AtlasValidationError(
            f"candidate fixture requires exactly five nodes; got {len(nodes_raw)}"
        )

    nodes = tuple(
        _parse_node(node, index)
        for index, node in enumerate(nodes_raw)
        if isinstance(node, Mapping)
    )
    if len(nodes) != len(nodes_raw):
        raise AtlasValidationError("every node must be an object")

    node_ids = [node.node_id for node in nodes]
    coordinate_refs = [node.coordinate_ref for node in nodes]
    if len(set(node_ids)) != len(node_ids):
        raise AtlasValidationError("duplicate node_id")
    if len(set(coordinate_refs)) != len(coordinate_refs):
        raise AtlasValidationError("duplicate coordinate_ref")

    edges = tuple(
        _parse_edge(edge, index)
        for index, edge in enumerate(edges_raw)
        if isinstance(edge, Mapping)
    )
    if len(edges) != len(edges_raw):
        raise AtlasValidationError("every edge must be an object")

    edge_ids = [edge.edge_id for edge in edges]
    if len(set(edge_ids)) != len(edge_ids):
        raise AtlasValidationError("duplicate edge_id")

    known_nodes = set(node_ids)
    seen_pairs: set[tuple[str, str]] = set()
    for edge in edges:
        if edge.source_node_id not in known_nodes:
            raise AtlasValidationError(
                f"{edge.edge_id}: unknown source node {edge.source_node_id!r}"
            )
        if edge.target_node_id not in known_nodes:
            raise AtlasValidationError(
                f"{edge.edge_id}: unknown target node {edge.target_node_id!r}"
            )
        pair = (edge.source_node_id, edge.target_node_id)
        if pair in seen_pairs:
            raise AtlasValidationError(
                f"duplicate directed transfer pair {pair!r}"
            )
        seen_pairs.add(pair)

    manifest_digest = _sha256_text(_canonical_json(dict(raw)))
    return AtlasManifest(
        schema_version=SCHEMA_VERSION,
        manifest_id=manifest_id,
        nodes=nodes,
        edges=edges,
        manifest_digest=manifest_digest,
    )


def load_manifest(path: str | Path) -> AtlasManifest:
    source = Path(path)
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AtlasValidationError(f"missing Atlas manifest: {source}") from exc
    except json.JSONDecodeError as exc:
        raise AtlasValidationError(f"invalid Atlas manifest JSON: {exc}") from exc

    if not isinstance(raw, Mapping):
        raise AtlasValidationError("Atlas manifest root must be an object")
    return parse_manifest(raw)


def node_by_id(manifest: AtlasManifest, node_id: str) -> AtlasNode:
    for node in manifest.nodes:
        if node.node_id == node_id:
            return node
    raise AtlasValidationError(f"unknown node_id {node_id!r}")


def coordinate_by_node_id(manifest: AtlasManifest, node_id: str) -> str:
    return node_by_id(manifest, node_id).coordinate_ref


def _adjacency(manifest: AtlasManifest) -> dict[str, list[AtlasEdge]]:
    adjacency = {node.node_id: [] for node in manifest.nodes}
    for edge in manifest.edges:
        adjacency[edge.source_node_id].append(edge)
    for edge_list in adjacency.values():
        edge_list.sort(key=lambda edge: edge.edge_id)
    return adjacency


def route(manifest: AtlasManifest, source_node_id: str, target_node_id: str) -> Route:
    node_by_id(manifest, source_node_id)
    node_by_id(manifest, target_node_id)

    if source_node_id == target_node_id:
        return Route(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            node_path=(source_node_id,),
            edge_path=(),
        )

    adjacency = _adjacency(manifest)
    queue: deque[str] = deque([source_node_id])
    visited = {source_node_id}
    parent_node: dict[str, str] = {}
    parent_edge: dict[str, str] = {}

    while queue:
        current = queue.popleft()
        for edge in adjacency[current]:
            neighbor = edge.target_node_id
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent_node[neighbor] = current
            parent_edge[neighbor] = edge.edge_id
            if neighbor == target_node_id:
                queue.clear()
                break
            queue.append(neighbor)

    if target_node_id not in visited:
        raise AtlasValidationError(
            f"no declared transfer route from {source_node_id!r} "
            f"to {target_node_id!r}"
        )

    nodes_reversed = [target_node_id]
    edges_reversed: list[str] = []
    cursor = target_node_id
    while cursor != source_node_id:
        edges_reversed.append(parent_edge[cursor])
        cursor = parent_node[cursor]
        nodes_reversed.append(cursor)

    return Route(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        node_path=tuple(reversed(nodes_reversed)),
        edge_path=tuple(reversed(edges_reversed)),
    )


def _normalize_payload_refs(payload_refs: Iterable[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for index, ref in enumerate(payload_refs):
        normalized.append(_require_nonempty_string(ref, f"payload_refs[{index}]"))
    if len(normalized) != len(set(normalized)):
        raise AtlasValidationError("payload_refs must not contain duplicates")
    return tuple(normalized)


def build_transfer(
    manifest: AtlasManifest,
    *,
    source_node_id: str,
    target_node_id: str,
    payload_refs: Sequence[str] = (),
) -> TransferEnvelope:
    """Construct a deterministic transfer envelope.

    This function performs no network I/O, process invocation, role binding,
    authority change, standing change, or execution. A route is addressability,
    not permission.
    """

    source = node_by_id(manifest, source_node_id)
    target = node_by_id(manifest, target_node_id)
    selected_route = route(manifest, source_node_id, target_node_id)
    refs = _normalize_payload_refs(payload_refs)

    body = {
        "schema_version": TRANSFER_SCHEMA_VERSION,
        "manifest_id": manifest.manifest_id,
        "manifest_digest": manifest.manifest_digest,
        "source_node_id": source.node_id,
        "target_node_id": target.node_id,
        "source_coordinate_ref": source.coordinate_ref,
        "target_coordinate_ref": target.coordinate_ref,
        "route_node_path": list(selected_route.node_path),
        "route_edge_path": list(selected_route.edge_path),
        "payload_refs": list(refs),
        "authority_changed": False,
        "execution_invoked": False,
        "standing_changed": False,
    }
    transfer_id = _sha256_text(_canonical_json(body))

    return TransferEnvelope(
        schema_version=TRANSFER_SCHEMA_VERSION,
        transfer_id=transfer_id,
        manifest_id=manifest.manifest_id,
        manifest_digest=manifest.manifest_digest,
        source_node_id=source.node_id,
        target_node_id=target.node_id,
        source_coordinate_ref=source.coordinate_ref,
        target_coordinate_ref=target.coordinate_ref,
        route_node_path=selected_route.node_path,
        route_edge_path=selected_route.edge_path,
        payload_refs=refs,
        authority_changed=False,
        execution_invoked=False,
        standing_changed=False,
    )
