#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCER = ROOT / "tools" / "observe_horizon_gap_selector_v0.py"
OLD_ROOT_OUTPUT = ROOT / "horizon_gap_selector_v0_observation.json"
RELOCATED_HISTORICAL = (
    ROOT / "docs" / "evidence" / "for_planner" / "horizon_gap_selector_v0_observation.json"
)
OUT = (
    ROOT / "docs" / "evidence" / "for_planner"
    / "evidence_producer_route_alignment_v0_observation.json"
)

EXPECTED_PRODUCER_BLOB = "54891e276f28a3f4fe4d61775d14b706cf56bd1e"
EXPECTED_HISTORICAL_BLOB = "be23eba7c50f1b51a0e3b1412d9f5adc07dee1ff"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def git_blob_at_head(path: Path) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    proc = git("rev-parse", f"HEAD:{rel}", check=False)
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    return value or None


def hash_object(path: Path) -> str:
    return git("hash-object", str(path)).stdout.strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            f"remove existing {OUT.relative_to(ROOT)} first"
        )
    if OLD_ROOT_OUTPUT.exists():
        raise SystemExit(
            f"old root output must be absent before pressure: "
            f"{OLD_ROOT_OUTPUT.relative_to(ROOT)}"
        )

    producer_blob = git_blob_at_head(PRODUCER)
    historical_blob_before = git_blob_at_head(RELOCATED_HISTORICAL)

    if producer_blob != EXPECTED_PRODUCER_BLOB:
        raise SystemExit(
            f"producer blob mismatch: expected {EXPECTED_PRODUCER_BLOB}, got {producer_blob}"
        )
    if historical_blob_before != EXPECTED_HISTORICAL_BLOB:
        raise SystemExit(
            "relocated historical blob mismatch: "
            f"expected {EXPECTED_HISTORICAL_BLOB}, got {historical_blob_before}"
        )

    proc = subprocess.run(
        [sys.executable, str(PRODUCER)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    created = OLD_ROOT_OUTPUT.exists()
    generated_git_blob = hash_object(OLD_ROOT_OUTPUT) if created else None
    generated_sha256 = sha256(OLD_ROOT_OUTPUT) if created else None
    generated_size = OLD_ROOT_OUTPUT.stat().st_size if created else None

    historical_blob_after = git_blob_at_head(RELOCATED_HISTORICAL)
    historical_file_sha256_after = sha256(RELOCATED_HISTORICAL)

    cleanup_attempted = False
    cleanup_root_absent = False
    if created:
        cleanup_attempted = True
        OLD_ROOT_OUTPUT.unlink()
        cleanup_root_absent = not OLD_ROOT_OUTPUT.exists()

    observation = {
        "object_type": "EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_OBSERVATION",
        "campaign_id": "EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_001",
        "pressure_id": "EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_PRESSURE_001",
        "repo_head": git("rev-parse", "HEAD").stdout.strip(),
        "producer": {
            "path": PRODUCER.relative_to(ROOT).as_posix(),
            "expected_blob": EXPECTED_PRODUCER_BLOB,
            "actual_blob": producer_blob,
            "blob_matched": producer_blob == EXPECTED_PRODUCER_BLOB,
            "declared_output_path": "horizon_gap_selector_v0_observation.json",
        },
        "historical_evidence": {
            "relocated_path": RELOCATED_HISTORICAL.relative_to(ROOT).as_posix(),
            "expected_blob": EXPECTED_HISTORICAL_BLOB,
            "blob_before": historical_blob_before,
            "blob_after": historical_blob_after,
            "blob_preserved": (
                historical_blob_before
                == historical_blob_after
                == EXPECTED_HISTORICAL_BLOB
            ),
            "file_sha256_after": historical_file_sha256_after,
        },
        "producer_run": {
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "old_root_output_created": created,
            "generated_root_git_blob": generated_git_blob,
            "generated_root_sha256": generated_sha256,
            "generated_root_size_bytes": generated_size,
            "generated_root_blob_ne_historical_blob": (
                generated_git_blob is not None
                and generated_git_blob != EXPECTED_HISTORICAL_BLOB
            ),
        },
        "cleanup": {
            "attempted": cleanup_attempted,
            "old_root_output_absent_after_cleanup": cleanup_root_absent,
            "relocated_historical_path_still_exists": RELOCATED_HISTORICAL.exists(),
        },
        "assembly": {
            "precondition_old_root_absent": True,
            "producer_run_succeeded": proc.returncode == 0,
            "old_root_path_reoccupied_by_fresh_output": created,
            "relocated_historical_blob_preserved": (
                historical_blob_before
                == historical_blob_after
                == EXPECTED_HISTORICAL_BLOB
            ),
            "producer_output_route_migrated": False if created else "UNRESOLVED",
            "stored_evidence_relocation_ne_producer_output_route_migration": (
                "YES"
                if (
                    proc.returncode == 0
                    and created
                    and historical_blob_before
                    == historical_blob_after
                    == EXPECTED_HISTORICAL_BLOB
                )
                else "UNRESOLVED"
            ),
            "pressure_cleanup_complete": cleanup_root_absent,
        },
        "effects": {
            "producer_repair_effect": "NONE",
            "consumer_repair_effect": "NONE",
            "generic_intake_router_effect": "NONE",
            "archive_policy_effect": "NONE",
            "cold_storage_admission_effect": "NONE",
            "deletion_permission_effect": "NONE",
            "automatic_reference_rewrite_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "One bounded execution of tools/observe_horizon_gap_selector_v0.py. "
            "The pressure tests whether relocating its historical observation changes "
            "the unchanged producer's output route. A temporary root output is captured "
            "and deleted after observation; the relocated historical artifact remains "
            "unchanged. No generic routing, archive, cold-storage, repair, deletion, "
            "planning, authority, execution, or scientific-standing claim is created."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] producer exit code {proc.returncode}")
    print(f"[OK] old root output created {created}")
    print(
        "[OK] relocated historical blob preserved "
        + str(observation["assembly"]["relocated_historical_blob_preserved"])
    )
    print(
        "[INFO] generated root blob != historical blob "
        + str(observation["producer_run"]["generated_root_blob_ne_historical_blob"])
    )
    print(f"[OK] pressure cleanup complete {cleanup_root_absent}")
    print(
        "[OK] target relation "
        + str(
            observation["assembly"][
                "stored_evidence_relocation_ne_producer_output_route_migration"
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
