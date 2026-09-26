#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination.materialized_unit_authority_admission_v0 import (
    materialized_unit_authority_coordinates,
    try_materialized_unit_verified_authority_atomic_admission,
)
from src.coordination.successor_work_unit_materialization_v0 import (
    materialize_successor_work_unit,
)
from src.coordination import workcycle_v0 as wc
from src.runtime.local_authority_consumption_v0 import LocalAuthorityStateStore
from tests.coordination.test_materialized_unit_authority_admission_v0 import (
    alternate_spec,
    envelope_for,
)
from tests.coordination.test_successor_work_unit_materialization_v0 import (
    partial_successor,
    work_spec,
)
from tests.coordination.test_verified_authority_admission_v0 import control_on

OUT = ROOT / "materialized_unit_authority_binding_repair_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def attempt(
    *,
    root: Path,
    store: LocalAuthorityStateStore,
    env: dict,
    successor: dict,
    spec: dict,
    unit: dict,
    attempt_id: str,
) -> dict:
    return try_materialized_unit_verified_authority_atomic_admission(
        store_dir=root / "atomic",
        authority_store=store,
        authority_envelope=env,
        attempting_principal_id="CODEX_PRINCIPAL_001",
        successor_candidate=successor,
        work_spec=spec,
        materialized_unit=unit,
        work_attempt_id=attempt_id,
        seat_id="LABBOIB",
        occupant_id=f"occupant-{attempt_id}",
        wake_generation=1,
        dependency_satisfied=True,
        frame_current=True,
        no_hold=True,
        control=control_on(),
        initial_budget=wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001"),
    )


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "remove existing materialized_unit_authority_binding_repair_observation.json first"
        )

    successor = partial_successor()
    spec_a = work_spec(successor)
    spec_b = alternate_spec(successor)
    unit_a = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec_a,
    )
    unit_b = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec_b,
    )

    coords_a = materialized_unit_authority_coordinates(
        successor_candidate=successor,
        work_spec=spec_a,
        materialized_unit=unit_a,
    )
    coords_b = materialized_unit_authority_coordinates(
        successor_candidate=successor,
        work_spec=spec_b,
        materialized_unit=unit_b,
    )

    env_a = envelope_for(
        successor,
        spec_a,
        unit_a,
        capability="CAP.MATERIALIZED.REPAIR.001",
    )

    with TemporaryDirectory() as tmp_a:
        root_a = Path(tmp_a)
        store_a = LocalAuthorityStateStore(root_a / "authority")
        before_a = store_a.issue(env_a)
        exact_a = attempt(
            root=root_a,
            store=store_a,
            env=env_a,
            successor=successor,
            spec=spec_a,
            unit=unit_a,
            attempt_id="REPAIR-EXACT-A",
        )
        after_a = store_a.read(env_a["capability_id"])

    with TemporaryDirectory() as tmp_b:
        root_b = Path(tmp_b)
        store_b = LocalAuthorityStateStore(root_b / "authority")
        store_b.issue(env_a)
        wrong_b = attempt(
            root=root_b,
            store=store_b,
            env=env_a,
            successor=successor,
            spec=spec_b,
            unit=unit_b,
            attempt_id="REPAIR-WRONG-B",
        )

    receipt = exact_a.get("receipt") or {}
    assertions = {
        "same_successor_id": (
            unit_a["identity"]["work_item_id"] == successor["successor_id"]
            and unit_b["identity"]["work_item_id"] == successor["successor_id"]
        ),
        "work_specs_differ": spec_a["work_spec_id"] != spec_b["work_spec_id"],
        "materialized_units_differ": (
            unit_a["integrity_sha256"] != unit_b["integrity_sha256"]
        ),
        "authority_coordinates_differ_by_materialized_work": coords_a != coords_b,
        "authority_input_binds_exact_unit_a": (
            coords_a["input_sha256"] == unit_a["integrity_sha256"]
        ),
        "authority_input_does_not_bind_unit_b": (
            coords_a["input_sha256"] != unit_b["integrity_sha256"]
        ),
        "exact_unit_a_admitted": exact_a.get("admitted") is True,
        "same_successor_wrong_unit_b_blocked": (
            wrong_b.get("admitted") is False
            and "authority_request_materialized_work_mismatch"
            in (wrong_b.get("blockers") or [])
        ),
        "receipt_binds_exact_materialized_unit": (
            receipt.get("materialized_unit_integrity_sha256")
            == unit_a["integrity_sha256"]
        ),
        "receipt_binds_exact_work_spec": (
            receipt.get("work_spec_id") == spec_a["work_spec_id"]
            and receipt.get("work_spec_integrity_sha256")
            == spec_a["integrity_sha256"]
        ),
        "receipt_binds_exact_successor": (
            receipt.get("successor_id") == successor["successor_id"]
            and receipt.get("successor_integrity_sha256")
            == successor["integrity_sha256"]
        ),
        "authority_unconsumed": (
            receipt.get("authority_consumed") is False
            and before_a == after_a
        ),
        "no_execution_or_model_invocation": (
            exact_a.get("execution_effect") == "NONE"
            and exact_a.get("model_invocation_effect") == "NONE"
            and receipt.get("execution_performed") is False
        ),
    }

    witness = {
        "object_type": "MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_EXACT_MATERIALIZED_WORK_AUTHORITY_FIXTURE",
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "work_spec_a_id": spec_a["work_spec_id"],
        "work_spec_b_id": spec_b["work_spec_id"],
        "unit_a_integrity_sha256": unit_a["integrity_sha256"],
        "unit_b_integrity_sha256": unit_b["integrity_sha256"],
        "authority_coordinates_a": coords_a,
        "authority_coordinates_b": coords_b,
        "exact_a": {
            "admitted": exact_a.get("admitted"),
            "blockers": exact_a.get("blockers"),
            "receipt": receipt,
        },
        "wrong_b": {
            "admitted": wrong_b.get("admitted"),
            "blockers": wrong_b.get("blockers"),
            "error": wrong_b.get("error"),
        },
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "At the exact supplied repaired source, one current verified one-use "
            "authority envelope can bind the exact sealed successor, exact sealed "
            "externally supplied work spec, and exact sealed materialized workflow "
            "unit before one same-process atomic admission. Authority for one "
            "materialization rejects a different materialization under the same "
            "successor. Authority remains unconsumed and no model invocation or work "
            "execution occurs."
        ),
        "authority_effect": "NONE",
        "consumption_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    OUT.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] all_assertions_pass {witness['all_assertions_pass']}")
    print(f"[OK] exact_unit_a_admitted {assertions['exact_unit_a_admitted']}")
    print(
        "[OK] same_successor_wrong_unit_b_blocked "
        + str(assertions["same_successor_wrong_unit_b_blocked"])
    )
    print(
        "[OK] receipt_binds_exact_materialized_unit "
        + str(assertions["receipt_binds_exact_materialized_unit"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
