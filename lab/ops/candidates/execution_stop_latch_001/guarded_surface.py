"""Bounded consequence-bearing paths for EXECUTION_STOP_LATCH_001 pressure.

These are specimen-local pressure surfaces, not generalized Workshop operations.
Both consume the same identity-bound ExecutionStopLatch state.
"""
from __future__ import annotations

import json
from pathlib import Path

from .stop_latch import ExecutionStopLatch


def create_held_out_condition_root(
    latch: ExecutionStopLatch, target_root: Path
) -> Path:
    latch.require_active("create_held_out_condition_root")
    target_root = Path(target_root)
    if target_root.exists():
        raise ValueError("target_root must be fresh")
    target_root.mkdir(parents=True)
    marker = target_root / "condition_root.json"
    marker.write_text(
        json.dumps(
            {
                "execution_envelope_id": latch.execution_envelope_id,
                "surface": "HELD_OUT_CONDITION_ROOT",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return marker


def emit_experimental_score(
    latch: ExecutionStopLatch, output_path: Path
) -> Path:
    latch.require_active("emit_experimental_score")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "execution_envelope_id": latch.execution_envelope_id,
                "surface": "EXPERIMENTAL_SCORE",
                "value": "TEST_REACHABLE",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return output_path
