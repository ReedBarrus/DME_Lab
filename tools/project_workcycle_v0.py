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
    projection = build_workcycle_projection(Path(args.repo))
    print(json.dumps(projection, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
