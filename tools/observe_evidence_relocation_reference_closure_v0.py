#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "evidence" / "for_planner" / "ROOT_EVIDENCE_INVENTORY.md"
OUT = ROOT / "docs" / "evidence" / "for_planner" / "evidence_relocation_reference_closure_v0_observation.json"
RELOCATED_PREFIX = "docs/evidence/for_planner/"
EXPECTED_COUNT = 37


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        check=check,
    )


def tracked_files() -> list[str]:
    proc = git("ls-files", "-z")
    return [p.decode("utf-8", errors="strict") for p in proc.stdout.split(b"\0") if p]


def current_blob(path: str) -> str | None:
    proc = git("rev-parse", f"HEAD:{path}", check=False)
    if proc.returncode != 0:
        return None
    value = proc.stdout.decode("ascii", errors="strict").strip()
    return value or None


def parse_inventory() -> list[dict[str, str]]:
    text = INVENTORY.read_text(encoding="utf-8")
    rows = []
    pattern = re.compile(r"^\| `([^`]+)` \| ([0-9]+) \| `([0-9a-f]{40})` \|$", re.MULTILINE)
    for old_path, size, blob in pattern.findall(text):
        rows.append({
            "original_root_path": old_path,
            "size_bytes": size,
            "expected_blob": blob,
            "relocated_path": RELOCATED_PREFIX + old_path,
        })
    if len(rows) != EXPECTED_COUNT:
        raise SystemExit(f"expected {EXPECTED_COUNT} inventory rows, found {len(rows)}")
    return rows


def read_text_file(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def classify_occurrences(rows: list[dict[str, str]]) -> list[dict]:
    files = tracked_files()
    text_cache: dict[str, list[str]] = {}

    for rel in files:
        if rel == str(OUT.relative_to(ROOT)).replace("\\", "/"):
            continue
        text = read_text_file(ROOT / rel)
        if text is None:
            continue
        text_cache[rel] = text.splitlines()

    results = []
    for row in rows:
        basename = row["original_root_path"]
        qualified = row["relocated_path"]
        qualified_hits = []
        bare_hits = []

        for rel, lines in text_cache.items():
            for line_no, line in enumerate(lines, start=1):
                if basename not in line:
                    continue
                hit = {
                    "path": rel,
                    "line": line_no,
                    "text": line[:500],
                }
                if qualified in line:
                    qualified_hits.append(hit)
                else:
                    bare_hits.append(hit)

        relocated_blob = current_blob(qualified)
        results.append({
            **row,
            "relocated_path_current_blob": relocated_blob,
            "relocated_path_present": relocated_blob is not None,
            "relocated_blob_matches_inventory": relocated_blob == row["expected_blob"],
            "qualified_route_occurrence_count": len(qualified_hits),
            "bare_or_root_style_occurrence_count": len(bare_hits),
            "qualified_route_occurrences": qualified_hits,
            "bare_or_root_style_occurrences": bare_hits,
        })

    return results


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"remove existing {OUT.relative_to(ROOT)} first")

    rows = parse_inventory()
    results = classify_occurrences(rows)

    all_present = all(r["relocated_path_present"] for r in results)
    all_match = all(r["relocated_blob_matches_inventory"] for r in results)
    total_qualified = sum(r["qualified_route_occurrence_count"] for r in results)
    total_bare = sum(r["bare_or_root_style_occurrence_count"] for r in results)

    observation = {
        "object_type": "EVIDENCE_RELOCATION_REFERENCE_CLOSURE_V0_OBSERVATION",
        "campaign_id": "EVIDENCE_RELOCATION_REFERENCE_CLOSURE_001",
        "pressure_id": "EVIDENCE_RELOCATION_REFERENCE_CLOSURE_V0_PRESSURE_001",
        "head": git("rev-parse", "HEAD").stdout.decode("ascii").strip(),
        "inventory_path": str(INVENTORY.relative_to(ROOT)).replace("\\", "/"),
        "inventory_rows_parsed": len(rows),
        "tracked_text_scan_posture": "MECHANICAL_OCCURRENCE_INVENTORY_ONLY",
        "artifacts": results,
        "assembly": {
            "inventory_rows_parsed": len(rows),
            "all_relocated_paths_present": all_present,
            "all_relocated_blobs_match_inventory": all_match,
            "total_qualified_route_occurrences": total_qualified,
            "total_bare_or_root_style_occurrences": total_bare,
            "dependency_classification_performed": False,
        },
        "noncollapses": {
            "text_occurrence_ne_live_dependency": True,
            "known_route_repair_ne_all_reference_closure": True,
            "historical_mention_ne_current_route": True,
            "reference_discovery_ne_reference_rewrite_authority": True,
        },
        "effects": {
            "dependency_standing_effect": "NONE",
            "automatic_reference_rewrite_effect": "NONE",
            "generic_relocation_resolver_effect": "NONE",
            "archive_policy_effect": "NONE",
            "cold_storage_admission_effect": "NONE",
            "deletion_permission_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "One tracked-tree mechanical occurrence inventory over the 37 exact "
            "artifacts listed in ROOT_EVIDENCE_INVENTORY.md. Bare/root-style text "
            "occurrences are not classified as live dependencies by this observer."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] inventory rows {len(rows)}")
    print(f"[OK] relocated paths present {all_present}")
    print(f"[OK] relocated blobs exact {all_match}")
    print(f"[INFO] qualified route occurrences {total_qualified}")
    print(f"[INFO] bare/root-style occurrences {total_bare}")
    print("[OK] dependency classification performed False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
