#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.cockpit.workcycle_projection import build_workcycle_projection
from src.cockpit.temporal_horizon_closure import derive_temporal_horizon_closure
from src.cockpit.workcycle_qualification import build_workcycle_qualification_readiness
from src.cockpit.pressure_justification import build_basis_record, build_pressure_justification


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the read-only WORKCYCLE_STABILIZATION_001 Cockpit projection."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="repository root (default: current directory)",
    )
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    projection = build_workcycle_projection(repo)
    temporal_path = repo / "generated" / "repository_temporal_lineage.json"
    try:
        temporal = json.loads(temporal_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        temporal = {}
    projection["temporal_horizon_closure"] = derive_temporal_horizon_closure(
        temporal_lineage=temporal,
        workcycle=projection,
    )
    projection["qualification_readiness"] = build_workcycle_qualification_readiness(
        repo
    )
    projection["basis_record"] = build_basis_record(
        workcycle=projection,
        horizon_closure=projection["temporal_horizon_closure"],
        qualification=projection["qualification_readiness"],
    )
    projection["pressure_justification"] = build_pressure_justification(
        workcycle=projection,
        horizon_closure=projection["temporal_horizon_closure"],
        qualification=projection["qualification_readiness"],
    )
    print(json.dumps(projection, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
