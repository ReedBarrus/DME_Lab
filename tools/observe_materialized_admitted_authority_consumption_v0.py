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

from src.coordination.materialized_admitted_authority_consumption_v0 import (
    consume_materialized_admitted_authority_once,
)
from src.coordination.successor_work_unit_materialization_v0 import (
    materialize_successor_work_unit,
)
from tests.coordination.test_materialized_admitted_authority_consumption_v0 import (
    exact_fixture,
)
from tests.coordination.test_materialized_unit_authority_admission_v0 import (
    alternate_spec,
)

OUT = ROOT / "materialized_admitted_authority_consumption_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "remove existing materialized_admitted_authority_consumption_observation.json first"
        )

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        successor, spec_a, unit_a, env, store, admission = exact_fixture(root)

        callback_calls: list[str] = []
        ticks = iter([
            "2026-09-26T00:40:01Z",
            "2026-09-26T00:40:02Z",
        ])
        raw_return = {
            "fixture_result": "SUCCESS",
            "count": 1,
            "work_item_id": unit_a["identity"]["work_item_id"],
        }
        exact = consume_materialized_admitted_authority_once(
            admission_receipt=admission,
            successor_candidate=successor,
            work_spec=spec_a,
            materialized_unit=unit_a,
            authority_envelope=env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=store,
            invoke=lambda: callback_calls.append("exact") or raw_return,
            clock=lambda: next(ticks),
        )
        state_after = store.read(env["capability_id"])

        replay_calls: list[str] = []
        replay = consume_materialized_admitted_authority_once(
            admission_receipt=admission,
            successor_candidate=successor,
            work_spec=spec_a,
            materialized_unit=unit_a,
            authority_envelope=env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=store,
            invoke=lambda: replay_calls.append("replay") or {"bad": True},
            clock=lambda: "2026-09-26T00:40:03Z",
        )

    with TemporaryDirectory() as tmp_wrong:
        wrong_root = Path(tmp_wrong)
        successor_w, spec_w, unit_w, env_w, store_w, admission_w = exact_fixture(
            wrong_root
        )
        spec_b = alternate_spec(successor_w)
        unit_b = materialize_successor_work_unit(
            successor_candidate=successor_w,
            work_spec=spec_b,
        )
        wrong_calls: list[str] = []
        wrong = consume_materialized_admitted_authority_once(
            admission_receipt=admission_w,
            successor_candidate=successor_w,
            work_spec=spec_b,
            materialized_unit=unit_b,
            authority_envelope=env_w,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=store_w,
            invoke=lambda: wrong_calls.append("wrong") or {"bad": True},
            clock=lambda: "2026-09-26T00:41:01Z",
        )
        wrong_state_after = store_w.read(env_w["capability_id"])

    receipt = exact.get("receipt") or {}
    assertions = {
        "exact_consumed": exact.get("consumed") is True,
        "exact_callback_once": callback_calls == ["exact"],
        "invocation_performed_once": (
            exact.get("invocation_performed") is True
            and receipt.get("invocation_count") == 1
        ),
        "raw_return_preserved": exact.get("invocation_result") == raw_return,
        "receipt_binds_exact_successor": (
            receipt.get("successor_id") == successor["successor_id"]
            and receipt.get("successor_integrity_sha256")
            == successor["integrity_sha256"]
        ),
        "receipt_binds_exact_work_spec": (
            receipt.get("work_spec_id") == spec_a["work_spec_id"]
            and receipt.get("work_spec_integrity_sha256")
            == spec_a["integrity_sha256"]
        ),
        "receipt_binds_exact_materialized_unit": (
            receipt.get("materialized_unit_integrity_sha256")
            == unit_a["integrity_sha256"]
            and receipt.get("materialized_work_item_id")
            == unit_a["identity"]["work_item_id"]
        ),
        "authority_consumed_once": (
            receipt.get("authority_consumed") is True
            and receipt.get("authority_status_after") == "CONSUMED"
            and receipt.get("authority_remaining_uses_after") == 0
            and state_after["envelope"]["status"] == "CONSUMED"
            and state_after["envelope"]["remaining_uses"] == 0
        ),
        "replay_blocked_without_callback": (
            replay.get("consumed") is False
            and replay.get("blockers") == ["authority_verification_failed"]
            and replay_calls == []
        ),
        "wrong_materialization_blocked_before_consumption": (
            wrong.get("consumed") is False
            and wrong_calls == []
            and wrong_state_after["envelope"]["status"] == "ACTIVE"
            and wrong_state_after["envelope"]["remaining_uses"] == 1
        ),
        "no_work_execution_or_standing_created": (
            receipt.get("execution_effect") == "NONE"
            and receipt.get("scientific_standing_effect") == "NONE"
            and exact.get("execution_effect") == "NONE"
            and exact.get("scientific_standing_effect") == "NONE"
        ),
    }

    witness = {
        "object_type": "MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_EXACT_MATERIALIZED_WORK_CONSUMPTION_FIXTURE",
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "work_spec_id": spec_a["work_spec_id"],
        "work_spec_integrity_sha256": spec_a["integrity_sha256"],
        "materialized_work_item_id": unit_a["identity"]["work_item_id"],
        "materialized_unit_integrity_sha256": unit_a["integrity_sha256"],
        "admission_composition_id": admission["composition_id"],
        "authority_capability_id": env["capability_id"],
        "consumption_receipt": receipt,
        "raw_callback_return": raw_return,
        "replay": {
            "consumed": replay.get("consumed"),
            "blockers": replay.get("blockers"),
            "callback_calls": replay_calls,
        },
        "wrong_materialization": {
            "consumed": wrong.get("consumed"),
            "blockers": wrong.get("blockers"),
            "callback_calls": wrong_calls,
            "authority_status_after": wrong_state_after["envelope"]["status"],
            "authority_remaining_uses_after": wrong_state_after["envelope"][
                "remaining_uses"
            ],
        },
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "At the exact supplied source, one exact admitted materialized-work "
            "object can be rebound to the same current one-use local authority and "
            "cross one caller-supplied callback exactly once under one-shot "
            "consumption while conserving exact successor, work-spec, and "
            "materialized-unit identities. Replay is denied and a different "
            "materialization is blocked before consumption. The raw callback return "
            "is preserved only as an un-interpreted return value; no result witness, "
            "settlement, external consequence, work execution, or scientific "
            "standing is established."
        ),
        "authority_effect": "NONE",
        "consumption_effect": "CONSUMED_ONE_USE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    OUT.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] all_assertions_pass {witness['all_assertions_pass']}")
    print(f"[OK] exact_consumed {assertions['exact_consumed']}")
    print(f"[OK] exact_callback_once {assertions['exact_callback_once']}")
    print(
        "[OK] wrong_materialization_blocked_before_consumption "
        + str(assertions["wrong_materialization_blocked_before_consumption"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
