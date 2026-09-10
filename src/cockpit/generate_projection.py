from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from src.cockpit.projection_adapter import build_projection


DEFAULT_OUTPUT = Path("generated/cockpit_projection.json")


def generate_projection(
    *,
    repo: str | Path,
    source_ref: str,
    freshness_ref: str | None,
    output: str | Path,
    projection_time: str | None = None,
) -> dict[str, object]:
    """Generate one derived observer model and never retain an older fallback."""
    output_path = Path(output)
    temporary_path = output_path.with_name(output_path.name + ".tmp")

    output_path.unlink(missing_ok=True)
    temporary_path.unlink(missing_ok=True)

    model = build_projection(
        repo,
        source_ref=source_ref,
        freshness_ref=freshness_ref,
        projection_time=projection_time,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        temporary_path.write_text(
            json.dumps(model, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(output_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        raise
    return model


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the derived JSON input for the plain DME Cockpit observer."
    )
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument(
        "--source-ref",
        required=True,
        help="committed source ref; the adapter resolves it to an exact commit",
    )
    parser.add_argument(
        "--freshness-ref",
        default=None,
        help="optional locally available comparison ref",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--projection-time",
        default=None,
        help="optional fixed timestamp for deterministic tests",
    )
    args = parser.parse_args(argv)

    model = generate_projection(
        repo=args.repo,
        source_ref=args.source_ref,
        freshness_ref=args.freshness_ref,
        output=args.output,
        projection_time=args.projection_time,
    )
    state = model["repository_state"]
    print(
        json.dumps(
            {
                "output": str(Path(args.output)),
                "source_commit": state["source_commit"],
                "projection_status": state["projection_status"],
                "freshness": state["freshness"]["status"],
                "pressure_nodes": len(model["pressure_nodes"]),
                "pressure_relations": len(model["pressure_relations"]),
                "constraints": len(model["constraints"]),
                "evidence_refs": len(model["evidence_refs"]),
                "projection_documents": len(model["projection_documents"]),
                "projection_diagnostics": len(model["projection_diagnostics"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
