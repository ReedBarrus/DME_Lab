#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "docs" / "campaigns" / "sca001"

RULES = [
    ("CONVERSATION_", "conversation_candidates"),
    ("RELATIONAL_HORIZON_", "relational_horizons"),
    ("ATLAS_", "atlas"),
]


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def classify(path: Path) -> str | None:
    name = path.name
    for prefix, dest in RULES:
        if name.startswith(prefix):
            return dest
    return None


def tracked_top_level_files() -> list[Path]:
    proc = run_git("ls-files", str(CAMPAIGN.relative_to(ROOT)))
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or "git ls-files failed")

    out: list[Path] = []
    for line in proc.stdout.splitlines():
        p = ROOT / line
        if p.parent == CAMPAIGN and p.is_file():
            out.append(p)
    return sorted(out)


def plan_moves() -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    for src in tracked_top_level_files():
        dest_dir = classify(src)
        if dest_dir is None:
            continue
        dst = CAMPAIGN / dest_dir / src.name
        moves.append((src, dst))
    return moves


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministically organize the operative Atlas campaign root."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform git mv operations; default is dry-run",
    )
    args = parser.parse_args()

    status = run_git("status", "--porcelain")
    if status.returncode != 0:
        raise SystemExit(status.stderr.strip() or "git status failed")

    if status.stdout.strip():
        print("REFUSING: working tree is not clean.")
        print("Save current work first, then rerun.")
        print(status.stdout, end="")
        return 2

    moves = plan_moves()
    if not moves:
        print("NOOP: no top-level campaign files match the organization rules.")
        return 0

    print(f"Planned moves: {len(moves)}")
    counts: dict[str, int] = {}
    for src, dst in moves:
        rel_src = src.relative_to(ROOT)
        rel_dst = dst.relative_to(ROOT)
        counts[dst.parent.name] = counts.get(dst.parent.name, 0) + 1
        print(f"{rel_src} -> {rel_dst}")

    print("\nCounts:")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")

    if not args.apply:
        print("\nDRY RUN ONLY. Re-run with --apply after reviewing.")
        return 0

    for _, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)

    for src, dst in moves:
        proc = run_git("mv", str(src.relative_to(ROOT)), str(dst.relative_to(ROOT)))
        if proc.returncode != 0:
            raise SystemExit(
                f"git mv failed for {src.name}:\n{proc.stderr.strip()}"
            )

    print("\nAPPLIED. Review with:")
    print("  git status")
    print("  git diff --cached --summary")
    print("  git diff --cached --stat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
