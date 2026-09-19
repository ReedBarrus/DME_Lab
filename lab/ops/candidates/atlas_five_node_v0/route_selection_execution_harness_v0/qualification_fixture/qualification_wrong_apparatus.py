from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class Route:
    node_path: tuple[str, ...]
    edge_path: tuple[str, ...]


def parse_manifest(raw: Mapping[str, Any]) -> dict[str, Any]:
    return dict(raw)


def route(manifest: Mapping[str, Any], source_node_id: str, target_node_id: str) -> Route:
    return Route(
        node_path=(source_node_id, "NODE_99", target_node_id),
        edge_path=("WRONG_1", "WRONG_2"),
    )
