#!/usr/bin/env python3
"""LOCAL_SEMANTIC_OPERATOR_001 proposal-only local cognition membrane.

The live provider adapter targets LM Studio's OpenAI-compatible
/v1/chat/completions endpoint with structured JSON output.

The semantic model returns only proposal content. Durable request identity,
basis binding, and NONE effects are controller-side facts, not model claims.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import urllib.error
import urllib.request
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.goblin_pool import GoblinPool
from tools.labboib_controller_binding import bind_labboib

REQUEST_SCHEMA = "local_semantic_request_v0"
PROPOSAL_SCHEMA = "local_semantic_proposal_v0"
AUTHORITY_PATH = "lab/ops/candidates/LOCAL_SEMANTIC_OPERATOR_001/authority_v0.json"
AUTHORITY_ID = "LOCAL_SEMANTIC_OPERATOR_001_AUTHORITY"
SEAT_ID = "LABBOIB"
TASK_TYPE = "TRIAGE_IMPLEMENTATION_RESULT"

MODEL_OUTPUT_FIELDS = {
    "summary",
    "anomaly_flags",
    "suggested_next_step",
    "evidence_refs",
}
NEXT_STEPS = {"NONE", "REVALIDATE", "REPRESSURE", "DISCARD", "REQUEST_REVIEW"}


class LocalSemanticOperatorError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_authority() -> dict[str, Any]:
    authority = json.loads((ROOT / AUTHORITY_PATH).read_text(encoding="utf-8"))
    if authority.get("authority_id") != AUTHORITY_ID:
        raise LocalSemanticOperatorError("unexpected semantic authority identity")
    return authority


def validate_request(request: dict[str, Any]) -> None:
    required = {
        "schema",
        "request_id",
        "seat_id",
        "task_type",
        "seat_basis_version",
        "environment_basis",
        "evidence_refs",
        "input",
        "authority_ref",
    }
    if set(request) != required:
        raise LocalSemanticOperatorError("request fields differ from local_semantic_request_v0")
    if request["schema"] != REQUEST_SCHEMA:
        raise LocalSemanticOperatorError("unexpected semantic request schema")
    if request["seat_id"] != SEAT_ID:
        raise LocalSemanticOperatorError("semantic request seat is not LABBOIB")
    if request["task_type"] != TASK_TYPE:
        raise LocalSemanticOperatorError("unexpected semantic task type")
    if not isinstance(request["request_id"], str) or not request["request_id"]:
        raise LocalSemanticOperatorError("request_id must be non-empty")
    if not isinstance(request["seat_basis_version"], int) or request["seat_basis_version"] < 0:
        raise LocalSemanticOperatorError("seat_basis_version must be a non-negative integer")
    basis = request["environment_basis"]
    if (
        not isinstance(basis, str)
        or len(basis) != 40
        or any(ch not in "0123456789abcdef" for ch in basis)
    ):
        raise LocalSemanticOperatorError("environment_basis must be lowercase 40-hex")
    refs = request["evidence_refs"]
    if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)):
        raise LocalSemanticOperatorError("evidence_refs must be a non-empty unique list")
    if not all(isinstance(ref, str) and ref for ref in refs):
        raise LocalSemanticOperatorError("evidence_refs must contain non-empty strings")
    if not isinstance(request["input"], dict):
        raise LocalSemanticOperatorError("input must be an object")
    required_input = {"realization", "applicability", "mechanical_checks", "scope_status"}
    if not required_input.issubset(request["input"]):
        raise LocalSemanticOperatorError("semantic request input is incomplete")
    if request["authority_ref"] != AUTHORITY_PATH:
        raise LocalSemanticOperatorError("unexpected semantic authority reference")


def authority_allows(request: dict[str, Any], authority: dict[str, Any]) -> bool:
    return bool(
        authority.get("authority_id") == AUTHORITY_ID
        and authority.get("seat_id") == request["seat_id"]
        and authority.get("task_type") == request["task_type"]
        and authority.get("provider_family") == "LM_STUDIO"
        and authority.get("model_family") == "QWEN"
        and authority.get("semantic_invocation_authorized") is True
        and authority.get("seat_state_transition_authorized") is False
        and authority.get("action_selection_authorized") is False
        and authority.get("operator_execution_authorized") is False
        and authority.get("repository_write_authorized") is False
        and authority.get("scientific_promotion_authorized") is False
    )


def validate_model_payload(payload: Any, allowed_refs: set[str]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return False, ["MODEL_PAYLOAD_NOT_OBJECT"]
    if set(payload) != MODEL_OUTPUT_FIELDS:
        errors.append("MODEL_PAYLOAD_FIELDS_INVALID")
    summary = payload.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("SUMMARY_INVALID")
    flags = payload.get("anomaly_flags")
    if not isinstance(flags, list) or not all(isinstance(v, str) and v for v in flags):
        errors.append("ANOMALY_FLAGS_INVALID")
    elif len(flags) != len(set(flags)):
        errors.append("ANOMALY_FLAGS_DUPLICATE")
    step = payload.get("suggested_next_step")
    if step not in NEXT_STEPS:
        errors.append("SUGGESTED_NEXT_STEP_INVALID")
    refs = payload.get("evidence_refs")
    if not isinstance(refs, list) or not all(isinstance(v, str) and v for v in refs):
        errors.append("EVIDENCE_REFS_INVALID")
    elif len(refs) != len(set(refs)):
        errors.append("EVIDENCE_REFS_DUPLICATE")
    elif not set(refs).issubset(allowed_refs):
        errors.append("EVIDENCE_REF_OUTSIDE_REQUEST_BASIS")
    return not errors, errors


def _proposal_json_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "summary",
            "anomaly_flags",
            "suggested_next_step",
            "evidence_refs",
        ],
        "properties": {
            "summary": {"type": "string"},
            "anomaly_flags": {
                "type": "array",
                "items": {"type": "string"},
            },
            "suggested_next_step": {
                "type": "string",
                "enum": sorted(NEXT_STEPS),
            },
            "evidence_refs": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }


def lm_studio_chat_completion(
    *,
    base_url: str,
    model_id: str,
    request: dict[str, Any],
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Invoke one exact LM Studio model via OpenAI-compatible chat completions."""
    endpoint = base_url.rstrip("/") + "/chat/completions"
    user_payload = {
        "task_type": request["task_type"],
        "seat_basis_version": request["seat_basis_version"],
        "environment_basis": request["environment_basis"],
        "evidence_refs": request["evidence_refs"],
        "input": request["input"],
    }
    body = {
        "model": model_id,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only the requested JSON proposal. You are a proposal-only "
                    "semantic transformer. Do not claim authority, execute actions, "
                    "or invent evidence references."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(user_payload, sort_keys=True),
            },
        ],
        "temperature": 0,
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "local_semantic_triage_proposal",
                "schema": _proposal_json_schema(),
            },
        },
    }
    http_request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=timeout_seconds) as response:
            raw = response.read()
            status = response.status
    except Exception as exc:
        raise LocalSemanticOperatorError(
            f"LM Studio invocation failed: {type(exc).__name__}: {exc}"
        ) from exc

    try:
        provider = json.loads(raw.decode("utf-8"))
        content = provider["choices"][0]["message"]["content"]
    except Exception as exc:
        raise LocalSemanticOperatorError(
            "LM Studio response did not contain chat-completion content"
        ) from exc

    return {
        "provider_http_status": status,
        "provider_response": provider,
        "model_content": content,
    }


class LocalSemanticHarness:
    def __init__(self, pool: GoblinPool, state_db: str | Path):
        self.pool = pool
        self.state_db = Path(state_db)
        self.state_db.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.state_db)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS model_resources(
                    resource_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model_family TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    status TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS model_leases(
                    lease_id TEXT PRIMARY KEY,
                    resource_id TEXT NOT NULL,
                    seat_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    status TEXT NOT NULL
                );

                CREATE UNIQUE INDEX IF NOT EXISTS one_active_lease_per_resource
                ON model_leases(resource_id)
                WHERE status = 'ACTIVE';

                CREATE TABLE IF NOT EXISTS semantic_runs(
                    request_id TEXT PRIMARY KEY,
                    request_sha256 TEXT NOT NULL,
                    status TEXT NOT NULL,
                    outcome_json TEXT
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

    def register_resource(
        self,
        *,
        resource_id: str,
        model_id: str,
        base_url: str,
        status: str = "AVAILABLE",
    ) -> None:
        if status not in {"AVAILABLE", "OFFLINE"}:
            raise LocalSemanticOperatorError("unsupported resource status")
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO model_resources(
                    resource_id, provider, model_family, model_id, base_url, status
                ) VALUES(?,?,?,?,?,?)
                ON CONFLICT(resource_id) DO UPDATE SET
                    provider=excluded.provider,
                    model_family=excluded.model_family,
                    model_id=excluded.model_id,
                    base_url=excluded.base_url,
                    status=excluded.status
                """,
                (resource_id, "LM_STUDIO", "QWEN", model_id, base_url, status),
            )
            conn.commit()
        finally:
            conn.close()

    def resource_snapshot(self, resource_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM model_resources WHERE resource_id = ?",
                (resource_id,),
            ).fetchone()
            active = conn.execute(
                """
                SELECT * FROM model_leases
                WHERE resource_id = ? AND status = 'ACTIVE'
                """,
                (resource_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise LocalSemanticOperatorError(f"unknown resource {resource_id!r}")
        return {
            "resource_id": row["resource_id"],
            "provider": row["provider"],
            "model_family": row["model_family"],
            "model_id": row["model_id"],
            "status": row["status"],
            "active_lease_id": active["lease_id"] if active is not None else None,
            "leased_to": active["seat_id"] if active is not None else None,
        }

    def _prior_outcome(self, request: dict[str, Any]) -> dict[str, Any] | None:
        digest = _sha256(request)
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM semantic_runs WHERE request_id = ?",
                (request["request_id"],),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        if row["request_sha256"] != digest:
            raise LocalSemanticOperatorError(
                "request_id already names different semantic request bytes"
            )
        if row["status"] != "COMPLETE":
            raise LocalSemanticOperatorError("semantic request is not complete")
        outcome = json.loads(row["outcome_json"])
        outcome["idempotent_replay"] = True
        outcome["model_invoked"] = False
        return outcome

    def _register_run(self, request: dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO semantic_runs(request_id, request_sha256, status)
                VALUES(?,?,?)
                """,
                (request["request_id"], _sha256(request), "STARTED"),
            )
            conn.commit()
        finally:
            conn.close()

    def _complete_run(self, request_id: str, outcome: dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE semantic_runs
                SET status='COMPLETE', outcome_json=?
                WHERE request_id=?
                """,
                (json.dumps(outcome, sort_keys=True), request_id),
            )
            conn.commit()
        finally:
            conn.close()

    def _acquire_lease(self, resource_id: str, request: dict[str, Any]) -> dict[str, Any]:
        lease_id = f"L-{request['request_id']}-{resource_id}"
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            resource = conn.execute(
                "SELECT * FROM model_resources WHERE resource_id = ?",
                (resource_id,),
            ).fetchone()
            if resource is None:
                raise LocalSemanticOperatorError("model resource not registered")
            if resource["status"] != "AVAILABLE":
                raise LocalSemanticOperatorError("model resource not available")
            active = conn.execute(
                """
                SELECT lease_id FROM model_leases
                WHERE resource_id=? AND status='ACTIVE'
                """,
                (resource_id,),
            ).fetchone()
            if active is not None:
                raise LocalSemanticOperatorError("model resource already leased")
            conn.execute(
                """
                INSERT INTO model_leases(
                    lease_id, resource_id, seat_id, request_id, status
                ) VALUES(?,?,?,?, 'ACTIVE')
                """,
                (
                    lease_id,
                    resource_id,
                    request["seat_id"],
                    request["request_id"],
                ),
            )
            conn.commit()
            return {
                "lease_id": lease_id,
                "resource_id": resource_id,
                "seat_id": request["seat_id"],
                "request_id": request["request_id"],
                "status": "ACTIVE",
                "provider": resource["provider"],
                "model_family": resource["model_family"],
                "model_id": resource["model_id"],
                "base_url": resource["base_url"],
            }
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def _release_lease(self, lease_id: str) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE model_leases SET status='RELEASED' WHERE lease_id=?",
                (lease_id,),
            )
            conn.commit()
        finally:
            conn.close()

    def invoke(
        self,
        *,
        wake_id: str,
        request: dict[str, Any],
        resource_id: str,
        provider: Callable[..., dict[str, Any]],
        current_basis: Callable[[], tuple[int, str]],
    ) -> dict[str, Any]:
        validate_request(request)

        prior = self._prior_outcome(request)
        if prior is not None:
            current_seat_version, current_environment_basis = current_basis()
            prior["current_basis_status"] = (
                "CURRENT"
                if current_seat_version == request["seat_basis_version"]
                and current_environment_basis == request["environment_basis"]
                else "STALE"
            )
            prior["accepted"] = bool(
                prior.get("proposal_valid")
                and prior.get("proposal") is not None
                and prior["current_basis_status"] == "CURRENT"
            )
            return prior

        authority = _load_authority()
        if not authority_allows(request, authority):
            return {
                "status": "AUTHORITY_REQUIRED",
                "request_id": request["request_id"],
                "model_invoked": False,
                "proposal": None,
                "seat_state_effect": "NONE",
                "action_selection_effect": "NONE",
                "authority_effect": "NONE",
            }

        seat_before = self.pool.seat_snapshot(request["seat_id"])
        if seat_before["state_version"] != request["seat_basis_version"]:
            raise LocalSemanticOperatorError("request seat basis is already stale")

        self._register_run(request)
        self.pool.emit_semantic_request(
            wake_id,
            request["request_id"],
            json.dumps(
                {
                    "task_type": request["task_type"],
                    "environment_basis": request["environment_basis"],
                    "evidence_refs": request["evidence_refs"],
                },
                sort_keys=True,
            ),
        )

        lease = self._acquire_lease(resource_id, request)
        raw_provider: dict[str, Any] | None = None
        model_payload: Any = None
        provider_error: str | None = None

        try:
            raw_provider = provider(
                base_url=lease["base_url"],
                model_id=lease["model_id"],
                request=request,
            )
            content = raw_provider.get("model_content")
            if not isinstance(content, str):
                raise LocalSemanticOperatorError("provider model_content is not text")
            try:
                model_payload = json.loads(content)
            except json.JSONDecodeError:
                model_payload = None
                provider_error = "MODEL_CONTENT_NOT_JSON"
        except Exception as exc:
            provider_error = f"{type(exc).__name__}: {exc}"
        finally:
            self._release_lease(lease["lease_id"])

        proposal_valid = False
        validation_errors: list[str] = []
        durable_proposal: dict[str, Any] | None = None

        if provider_error is None:
            proposal_valid, validation_errors = validate_model_payload(
                model_payload,
                set(request["evidence_refs"]),
            )
            if proposal_valid:
                proposal_id = f"P-{request['request_id']}-{_sha256(model_payload)[:16]}"
                durable_proposal = {
                    "schema": PROPOSAL_SCHEMA,
                    "proposal_id": proposal_id,
                    "request_id": request["request_id"],
                    "seat_id": request["seat_id"],
                    "seat_basis_version": request["seat_basis_version"],
                    "environment_basis": request["environment_basis"],
                    "summary": model_payload["summary"],
                    "anomaly_flags": model_payload["anomaly_flags"],
                    "suggested_next_step": model_payload["suggested_next_step"],
                    "evidence_refs": model_payload["evidence_refs"],
                    "authority_effect": "NONE",
                    "action_selection_effect": "NONE",
                    "seat_state_effect": "NONE",
                }

        current_seat_version, current_environment_basis = current_basis()
        current_basis_status = (
            "CURRENT"
            if current_seat_version == request["seat_basis_version"]
            and current_environment_basis == request["environment_basis"]
            else "STALE"
        )

        if durable_proposal is not None:
            self.pool.submit_semantic_proposal(
                request["request_id"],
                durable_proposal["proposal_id"],
                durable_proposal,
            )

        seat_after = self.pool.seat_snapshot(request["seat_id"])
        seat_state_unchanged = (
            seat_before["state_version"] == seat_after["state_version"]
            and seat_before["cursor_event_id"] == seat_after["cursor_event_id"]
            and seat_before["working_state"] == seat_after["working_state"]
            and seat_before["occupancy_state"] == seat_after["occupancy_state"]
            and seat_before["current_wake_id"] == seat_after["current_wake_id"]
        )

        accepted = bool(
            durable_proposal is not None
            and proposal_valid
            and current_basis_status == "CURRENT"
        )

        outcome = {
            "status": "PROPOSAL_RETAINED" if durable_proposal is not None else "NO_VALID_PROPOSAL",
            "request_id": request["request_id"],
            "resource_id": resource_id,
            "lease_id": lease["lease_id"],
            "lease_status": "RELEASED",
            "provider": lease["provider"],
            "model_family": lease["model_family"],
            "model_id": lease["model_id"],
            "model_invoked": True,
            "provider_error": provider_error,
            "raw_provider_evidence": raw_provider,
            "model_payload": model_payload,
            "proposal_valid": proposal_valid,
            "validation_errors": validation_errors,
            "proposal": durable_proposal,
            "current_basis_status": current_basis_status,
            "accepted": accepted,
            "seat_state_unchanged": seat_state_unchanged,
            "seat_state_effect": "NONE",
            "action_selection_effect": "NONE",
            "authority_effect": "NONE",
            "idempotent_replay": False,
        }
        self._complete_run(request["request_id"], outcome)
        return outcome


def fixture_provider(
    *,
    base_url: str,
    model_id: str,
    request: dict[str, Any],
    mode: str = "VALID",
) -> dict[str, Any]:
    del base_url
    del model_id
    refs = request["evidence_refs"]
    if mode == "VALID":
        payload: Any = {
            "summary": "Realization is mechanically legible under the supplied basis.",
            "anomaly_flags": [],
            "suggested_next_step": "REQUEST_REVIEW",
            "evidence_refs": refs[:2],
        }
        content = json.dumps(payload)
    elif mode == "MALFORMED":
        content = "{not-json"
    elif mode == "EXTRA_FIELD":
        payload = {
            "summary": "Typed shape plus unsupported field.",
            "anomaly_flags": [],
            "suggested_next_step": "NONE",
            "evidence_refs": refs[:1],
            "execute_now": True,
        }
        content = json.dumps(payload)
    elif mode == "UNAUTHORIZED_SUGGESTION":
        payload = {
            "summary": "Suggest revalidation; do not execute it.",
            "anomaly_flags": ["STALE_RISK"],
            "suggested_next_step": "REVALIDATE",
            "evidence_refs": refs[:1],
        }
        content = json.dumps(payload)
    elif mode == "FALSE_EVIDENCE":
        payload = {
            "summary": "Cites evidence that was not supplied.",
            "anomaly_flags": ["EVIDENCE_GAP"],
            "suggested_next_step": "REQUEST_REVIEW",
            "evidence_refs": ["EVIDENCE://INVENTED"],
        }
        content = json.dumps(payload)
    elif mode == "FAIL":
        raise LocalSemanticOperatorError("synthetic provider failure")
    else:
        raise LocalSemanticOperatorError(f"unknown fixture provider mode {mode!r}")

    return {
        "provider_http_status": 200,
        "provider_response": {"fixture": True, "mode": mode},
        "model_content": content,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller-db", required=True)
    parser.add_argument("--semantic-db", required=True)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--seat-source-ref", default="HEAD")
    parser.add_argument("--request", required=True)
    parser.add_argument("--resource-id", default="QWEN_LOCAL_PRIMARY")
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--wake-id", default="W-LOCAL-SEMANTIC-PROBE")
    args = parser.parse_args(argv)

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    if not isinstance(request, dict):
        raise LocalSemanticOperatorError("request must be a JSON object")

    pool = GoblinPool(args.controller_db, args.workspace)
    bind_labboib(pool, args.workspace, args.seat_source_ref)
    pool.start_wake(SEAT_ID, args.wake_id)

    harness = LocalSemanticHarness(pool, args.semantic_db)
    harness.register_resource(
        resource_id=args.resource_id,
        model_id=args.model_id,
        base_url=args.base_url,
        status="AVAILABLE",
    )

    def current_basis() -> tuple[int, str]:
        seat = pool.seat_snapshot(SEAT_ID)
        return seat["state_version"], _repo_head_for_cli(Path(args.workspace))

    result = harness.invoke(
        wake_id=args.wake_id,
        request=request,
        resource_id=args.resource_id,
        provider=lm_studio_chat_completion,
        current_basis=current_basis,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _repo_head_for_cli(repo: Path) -> str:
    import subprocess
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise LocalSemanticOperatorError(
            "cannot resolve live repository HEAD: " + result.stderr.strip()
        )
    return result.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
