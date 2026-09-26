#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "config" / "artifact_topology_rules_v0.json"


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def load_rules() -> dict:
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def tracked_files(scope: Path) -> list[Path]:
    proc = git("ls-files", str(scope.relative_to(ROOT)))
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")
    return [ROOT / line for line in proc.stdout.splitlines() if line.strip()]


def plan() -> tuple[list[tuple[Path, Path, str]], list[str]]:
    cfg = load_rules()
    moves: list[tuple[Path, Path, str]] = []
    notes: list[str] = []

    for family in cfg["families"]:
        scope = ROOT / family["scope"]
        prefix = family["match_prefix"]
        dest_dir = scope / family["canonical_folder"]

        family_files = [
            p for p in tracked_files(scope)
            if p.is_file()
            and p.name.startswith(prefix)
            and p.parent == scope
        ]

        already_batched = [
            p for p in tracked_files(dest_dir)
            if p.is_file() and p.name.startswith(prefix)
        ] if dest_dir.exists() else []

        total = len(family_files) + len(already_batched)
        if total >= int(cfg["soft_review_threshold"]):
            notes.append(
                f"{prefix}: {total} total family files; "
                f"{len(family_files)} still at scope root"
            )

        for src in sorted(family_files):
            dst = dest_dir / src.name
            moves.append((src, dst, family["relation"]))

    return moves, notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    moves, notes = plan()

    for note in notes:
        print("[AUDIT]", note)

    if not moves:
        print("PASS: declared topology families are already canonical")
        return 0

    print(f"PLANNED_MOVES: {len(moves)}")
    for src, dst, relation in moves:
        print(f"{src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
        print(f"  relation: {relation}")

    if not args.apply:
        print("DRY_RUN: no files moved")
        return 1

    status = git("status", "--porcelain")
    if status.returncode != 0:
        raise RuntimeError(status.stderr.strip() or "git status failed")
    if status.stdout.strip():
        print("REFUSING: working tree is not clean")
        return 2

    for src, dst, _ in moves:
        if dst.exists():
            raise RuntimeError(f"destination collision: {dst.relative_to(ROOT)}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        proc = git("mv", str(src.relative_to(ROOT)), str(dst.relative_to(ROOT)))
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or f"git mv failed: {src}")

    print("APPLIED: review git diff --cached --summary before commit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
