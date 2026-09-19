from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class Route:
    node_path: tuple[str, ...]
    edge_path: tuple[str, ...]


def parse_manifest(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ValueError("manifest must be a mapping")
    return dict(raw)


def route(manifest: Mapping[str, Any], source_node_id: str, target_node_id: str) -> Route:
    branch = manifest["qualification_branch"]
    if branch == "LEFT":
        return Route(
            node_path=(source_node_id, "NODE_02", target_node_id),
            edge_path=("Q_EDGE_1", "Q_EDGE_2"),
        )
    if branch == "RIGHT":
        return Route(
            node_path=(source_node_id, "NODE_03", target_node_id),
            edge_path=("Q_EDGE_3", "Q_EDGE_4"),
        )
    raise ValueError(f"unknown qualification_branch: {branch!r}")
