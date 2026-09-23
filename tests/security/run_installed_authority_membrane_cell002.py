from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


EXPECTED_BRIDGE_SHA256 = (
    "0f86b8499c269ee42ed50285e4429c504ff5e6f93a6e65836128e98ef9d2bb21"
)
EXPECTED_AUTHORITY_MODULE_SHA256 = (
    "bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303"
)
EXPECTED_POLICY_SHA256 = (
    "65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b"
)

TRUST_ROOT = Path.home() / ".dme_lab_bridge"
BRIDGE_PATH = TRUST_ROOT / "bridge.py"
AUTHORITY_MODULE_PATH = TRUST_ROOT / "local_authority_consumption_v0.py"
POLICY_PATH = TRUST_ROOT / "policy.json"

PROMPT_A = b"Return exactly: AUTHORITY_MEMBRANE_CELL_002_CONTROL\n"
PROMPT_B = b"Return exactly: AUTHORITY_MEMBRANE_CELL_002_CONTROK\n"
REMOTE_HEAD = "b" * 40
SOURCE_REF = "a" * 40
REQUEST_PATH = "bridge/requests/AUTHORITY_MEMBRANE_SECURITY_CELL_002.json"
PRINCIPAL_P = "CODEX_PRINCIPAL_001"
PRINCIPAL_Q = "CODEX_PRINCIPAL_002"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_sha256(path: Path, expected: str) -> str:
    if not path.is_file():
        raise RuntimeError(f"required installed file missing: {path}")
    observed = sha256_bytes(path.read_bytes())
    if observed != expected:
        raise RuntimeError(
            f"installed hash mismatch for {path}: expected {expected}, got {observed}"
        )
    return observed


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load installed module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def installed_coordinates() -> dict[str, str]:
    return {
        "installed_bridge_path": str(BRIDGE_PATH),
        "installed_bridge_sha256": exact_sha256(
            BRIDGE_PATH, EXPECTED_BRIDGE_SHA256
        ),
        "installed_authority_module_path": str(AUTHORITY_MODULE_PATH),
        "installed_authority_module_sha256": exact_sha256(
            AUTHORITY_MODULE_PATH, EXPECTED_AUTHORITY_MODULE_SHA256
        ),
        "installed_policy_path": str(POLICY_PATH),
        "installed_policy_sha256": exact_sha256(
            POLICY_PATH, EXPECTED_POLICY_SHA256
        ),
    }


installed_before = installed_coordinates()
authority = load_module("local_authority_consumption_v0", AUTHORITY_MODULE_PATH)
bridge = load_module("dme_installed_cell002_bridge", BRIDGE_PATH)


def clock(*values: str):
    retained = iter(values)
    return lambda: next(retained)


def fixed_ids(index: int) -> tuple[str, str]:
    suffix = f"{index:032d}"
    return f"CELL002.CAP.{suffix}", f"CELL002.APPROVAL.{suffix}"


def build_manifest() -> dict[str, object]:
    return {
        "schema_version": "LOCAL_INVOCATION_REQUEST_V0",
        "request_id": "AUTHORITY_MEMBRANE_SECURITY_CELL_002_INSTALLED",
        "enabled": True,
        "source_ref": SOURCE_REF,
        "input_path": "bridge/prompts/AUTHORITY_MEMBRANE_SECURITY_CELL_002.txt",
        "input_sha256": sha256_bytes(PROMPT_A),
        "principal_id": PRINCIPAL_P,
        "model": "qwen/qwen3-coder-30b",
        "temperature": 0,
        "max_tokens": 64,
        "purpose": "Installed Cell 002 qualification pressure without real HTTP.",
    }


def pressure_coordinates(
    common: dict[str, str],
    *,
    capability_id: str,
    approval_id: str,
    principal_id: str,
    attempting_principal_id: str,
    request_sha256: str,
    input_sha256: str,
    model: str,
    endpoint_identity: str,
) -> dict[str, object]:
    return {
        **common,
        "capability_id": capability_id,
        "approval_id": approval_id,
        "principal_id": principal_id,
        "attempting_principal_id": attempting_principal_id,
        "request_sha256": request_sha256,
        "input_sha256": input_sha256,
        "model": model,
        "endpoint_identity": endpoint_identity,
    }


def run_installed_qualification() -> dict[str, object]:
    common = installed_coordinates()
    manifest = build_manifest()
    raw_manifest = json.dumps(
        manifest,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    request_sha256 = sha256_bytes(raw_manifest)
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="dme-cell002-installed-") as temporary:
        temporary_root = Path(temporary)
        policy["_repo_root_resolved"] = str(temporary_root / "repo")
        policy["_result_dir_resolved"] = str(temporary_root / "results")
        Path(policy["_repo_root_resolved"]).mkdir()
        Path(policy["_result_dir_resolved"]).mkdir()

        def run_bridge_case(
            *,
            index: int,
            attempting_principal_id: str,
            execution_candidate: bytes,
        ) -> dict[str, object]:
            capability_id, approval_id = fixed_ids(index)
            store = authority.LocalAuthorityStateStore(
                temporary_root / f"authority-state-{index}"
            )
            result_path = temporary_root / f"result-{index}.json"
            approved: list[dict[str, object]] = []
            envelopes: list[dict[str, object]] = []
            revalidations: list[dict[str, object]] = []
            denials: list[dict[str, object]] = []
            reservation_seen_before_invocation: list[dict[str, object]] = []
            installed_approve = bridge.approve

            def git_show(repo: Path, ref: str, path: str) -> bytes:
                del repo
                if (ref, path) == (REMOTE_HEAD, REQUEST_PATH):
                    return raw_manifest
                if (ref, path) == (SOURCE_REF, manifest["input_path"]):
                    return PROMPT_A
                raise AssertionError((ref, path))

            def approve(
                observed_manifest: dict[str, object],
                prompt: bytes,
                approval_candidate: dict[str, object],
            ) -> bool:
                assert observed_manifest == manifest
                assert prompt == PROMPT_A
                approved.append(approval_candidate)
                with mock.patch("builtins.input", return_value="y") as input_mock:
                    decision = installed_approve(
                        observed_manifest,
                        prompt,
                        approval_candidate,
                    )
                input_mock.assert_called_once_with("Authorize this invocation? [y/N] ")
                return decision

            def consume(envelope: dict[str, object], **kwargs: object):
                envelopes.append(envelope)
                return authority.consume_authority_once(envelope, **kwargs)

            def invoke(*args: object, **kwargs: object) -> dict[str, object]:
                del args, kwargs
                state = store.read(capability_id)
                assert state["envelope"]["status"] == authority.CONSUMING
                assert state["envelope"]["remaining_uses"] == 0
                reservations = [
                    record
                    for record in state["history"]
                    if record.get("object_type") == authority.RESERVATION_TYPE
                ]
                assert len(reservations) == 1
                reservation_seen_before_invocation.append(reservations[0])
                return {
                    "object_type": "LOCAL_LMSTUDIO_INVOCATION_WITNESS_V0",
                    "request_id": manifest["request_id"],
                }

            invoke_mock = mock.Mock(side_effect=invoke)
            approve_mock = mock.Mock(side_effect=approve)
            output = io.StringIO()
            with (
                mock.patch.object(bridge, "fetch_remote", return_value=REMOTE_HEAD),
                mock.patch.object(
                    bridge, "list_request_paths", return_value=[REQUEST_PATH]
                ),
                mock.patch.object(bridge, "git_show", side_effect=git_show),
                mock.patch.object(
                    bridge, "result_path_for", return_value=result_path
                ),
                mock.patch.object(bridge, "approve", approve_mock),
                mock.patch.object(bridge, "invoke_lmstudio", invoke_mock),
                redirect_stdout(output),
            ):
                executed = bridge.process_once(
                    policy,
                    attempting_principal_id,
                    execution_candidate_provider=lambda observed, prompt: execution_candidate,
                    revalidation_witness_sink=revalidations.append,
                    authority_decision_sink=denials.append,
                    authority_store=store,
                    authority_clock=clock(
                        f"2026-09-22T20:00:0{index}+00:00",
                        f"2026-09-22T20:01:0{index}+00:00",
                        f"2026-09-22T20:02:0{index}+00:00",
                    ),
                    authority_id_factory=lambda: (capability_id, approval_id),
                    authority_consumer=consume,
                )

            return {
                "capability_id": capability_id,
                "approval_id": approval_id,
                "store": store,
                "result_path": result_path,
                "approved": approved,
                "envelopes": envelopes,
                "revalidations": revalidations,
                "denials": denials,
                "reservation_seen_before_invocation": reservation_seen_before_invocation,
                "approval_calls": approve_mock.call_count,
                "invoke_calls": invoke_mock.call_count,
                "executed": executed,
                "stdout": output.getvalue(),
            }

        control_run = run_bridge_case(
            index=1,
            attempting_principal_id=PRINCIPAL_P,
            execution_candidate=PROMPT_A,
        )
        assert control_run["approval_calls"] == 1
        assert control_run["invoke_calls"] == 1
        assert control_run["executed"] == 1
        assert len(control_run["envelopes"]) == 1
        assert len(control_run["reservation_seen_before_invocation"]) == 1
        control_envelope = control_run["envelopes"][0]
        control_store = control_run["store"]
        control_state = control_store.read(control_run["capability_id"])
        assert control_state["envelope"]["remaining_uses"] == 0
        assert control_state["envelope"]["status"] == authority.CONSUMED
        control_receipt = control_state["history"][-1]
        control_reservation = control_run["reservation_seen_before_invocation"][0]

        control = {
            "pressure_object": "CONTROL",
            **pressure_coordinates(
                common,
                capability_id=control_envelope["capability_id"],
                approval_id=control_envelope["approval_id"],
                principal_id=control_envelope["principal_id"],
                attempting_principal_id=PRINCIPAL_P,
                request_sha256=control_envelope["request_sha256"],
                input_sha256=control_envelope["input_sha256"],
                model=control_envelope["model"],
                endpoint_identity=control_envelope["endpoint_identity"],
            ),
            "approval_calls": 1,
            "approval_input_fixture": "LOCAL_YES",
            "authority_issued": True,
            "reservation_id": control_reservation["reservation_id"],
            "reservation_before_invocation": True,
            "remaining_uses_before": 1,
            "remaining_uses_after": 0,
            "status_before": authority.ACTIVE,
            "status_after": authority.CONSUMED,
            "current_authority": authority.NONE,
            "invocation_count": 1,
            "decision": "INVOKED",
            "reason": None,
            "receipt_id": control_receipt["receipt_id"],
            "denial_id": None,
            "pass": True,
        }

        reservation_count_before = sum(
            record.get("object_type") == authority.RESERVATION_TYPE
            for record in control_state["history"]
        )
        replay_invoke = mock.Mock(
            side_effect=AssertionError("exact replay crossed invocation boundary")
        )
        exact_same_capability_instance = control_envelope
        replay_result = authority.consume_authority_once(
            exact_same_capability_instance,
            attempting_principal_id=PRINCIPAL_P,
            store=control_store,
            invoke=replay_invoke,
            clock=clock("2026-09-22T20:03:01+00:00"),
        )
        replay_invoke.assert_not_called()
        replay_state = control_store.read(control_run["capability_id"])
        reservation_count_after = sum(
            record.get("object_type") == authority.RESERVATION_TYPE
            for record in replay_state["history"]
        )
        replay_denial = replay_result["witness"]
        historical_receipt = next(
            record
            for record in replay_state["history"]
            if record.get("object_type") == authority.RECEIPT_TYPE
        )
        assert exact_same_capability_instance is control_envelope
        assert reservation_count_after == reservation_count_before
        assert replay_result["decision"] == "DENY"
        assert replay_denial["reason"] == "AUTHORITY_EXHAUSTED"
        assert historical_receipt["receipt_id"] == control_receipt["receipt_id"]

        replay = {
            "pressure_object": "EXACT_REPLAY",
            **pressure_coordinates(
                common,
                capability_id=control_envelope["capability_id"],
                approval_id=control_envelope["approval_id"],
                principal_id=control_envelope["principal_id"],
                attempting_principal_id=PRINCIPAL_P,
                request_sha256=control_envelope["request_sha256"],
                input_sha256=control_envelope["input_sha256"],
                model=control_envelope["model"],
                endpoint_identity=control_envelope["endpoint_identity"],
            ),
            "same_capability_object_reference_reused": True,
            "new_approval_count": 0,
            "approval_input_fixture": None,
            "new_capability_count": 0,
            "new_reservation_count": 0,
            "reservation_id": None,
            "historical_reservation_id": control_reservation["reservation_id"],
            "remaining_uses_before": 0,
            "remaining_uses_after": 0,
            "status_before": authority.CONSUMED,
            "status_after": authority.CONSUMED,
            "current_authority": authority.NONE,
            "invocation_count": 0,
            "decision": replay_result["decision"],
            "reason": replay_denial["reason"],
            "receipt_id": historical_receipt["receipt_id"],
            "denial_id": replay_denial["denial_id"],
            "historical_receipt_readable": True,
            "pass": True,
        }

        wrong_run = run_bridge_case(
            index=2,
            attempting_principal_id=PRINCIPAL_Q,
            execution_candidate=PROMPT_A,
        )
        assert wrong_run["approval_calls"] == 1
        assert wrong_run["invoke_calls"] == 0
        assert wrong_run["executed"] == 0
        wrong_envelope = wrong_run["envelopes"][0]
        wrong_store = wrong_run["store"]
        wrong_state = wrong_store.read(wrong_run["capability_id"])
        wrong_denial = wrong_run["denials"][0]
        wrong_reservations = [
            record
            for record in wrong_state["history"]
            if record.get("object_type") == authority.RESERVATION_TYPE
        ]
        assert wrong_reservations == []
        assert wrong_state["envelope"]["remaining_uses"] == 1
        assert wrong_state["envelope"]["status"] == authority.ACTIVE
        assert wrong_denial["reason"] == "PRINCIPAL_MISMATCH"

        wrong_principal = {
            "pressure_object": "WRONG_DECLARED_PRINCIPAL",
            **pressure_coordinates(
                common,
                capability_id=wrong_envelope["capability_id"],
                approval_id=wrong_envelope["approval_id"],
                principal_id=wrong_envelope["principal_id"],
                attempting_principal_id=PRINCIPAL_Q,
                request_sha256=wrong_envelope["request_sha256"],
                input_sha256=wrong_envelope["input_sha256"],
                model=wrong_envelope["model"],
                endpoint_identity=wrong_envelope["endpoint_identity"],
            ),
            "approval_calls": 1,
            "approval_input_fixture": "LOCAL_YES",
            "authority_issued": True,
            "reservation_id": None,
            "remaining_uses_before": 1,
            "remaining_uses_after": 1,
            "status_before": authority.ACTIVE,
            "status_after": authority.ACTIVE,
            "invocation_count": 0,
            "decision": wrong_denial["decision"],
            "reason": wrong_denial["reason"],
            "receipt_id": None,
            "denial_id": wrong_denial["denial_id"],
            "declared_principal_correspondence_enforced": True,
            "principal_authentication_established": False,
            "pass": True,
        }

        cell001_run = run_bridge_case(
            index=3,
            attempting_principal_id=PRINCIPAL_P,
            execution_candidate=PROMPT_B,
        )
        assert cell001_run["approval_calls"] == 1
        assert cell001_run["invoke_calls"] == 0
        assert cell001_run["executed"] == 0
        assert cell001_run["envelopes"] == []
        assert not cell001_run["store"].state_path(
            cell001_run["capability_id"]
        ).exists()
        cell001_revalidation = cell001_run["revalidations"][0]
        approved = cell001_run["approved"][0]
        assert cell001_revalidation["reason"] == (
            "POST_APPROVAL_INPUT_SHA256_MISMATCH"
        )

        cell001 = {
            "pressure_object": "CELL_001_REGRESSION",
            **pressure_coordinates(
                common,
                capability_id=approved["capability_id"],
                approval_id=approved["approval_id"],
                principal_id=approved["principal_id"],
                attempting_principal_id=PRINCIPAL_P,
                request_sha256=approved["request_sha256"],
                input_sha256=approved["input_sha256"],
                model=approved["model"],
                endpoint_identity=approved["endpoint_identity"],
            ),
            "execution_candidate_sha256": sha256_bytes(PROMPT_B),
            "approval_calls": 1,
            "approval_input_fixture": "LOCAL_YES",
            "authority_issued": False,
            "authority_consumption_count": 0,
            "reservation_id": None,
            "remaining_uses_before": None,
            "remaining_uses_after": None,
            "status_before": "NOT_ISSUED",
            "status_after": "NOT_ISSUED",
            "invocation_count": 0,
            "decision": cell001_revalidation["decision"],
            "reason": cell001_revalidation["reason"],
            "receipt_id": None,
            "denial_id": None,
            "pass": True,
        }

    installed_after = installed_coordinates()
    assert installed_after == installed_before
    return {
        "object_type": "AUTHORITY_MEMBRANE_SECURITY_CELL_002_INSTALLED_QUALIFICATION_RESULT",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "installed_coordinates_before": installed_before,
        "installed_coordinates_after": installed_after,
        "installed_trust_root_mutation": "NONE",
        "authority_state_surface": "TEMPORARY_ONLY",
        "real_lmstudio_http_calls": 0,
        "control": control,
        "exact_replay": replay,
        "wrong_declared_principal": wrong_principal,
        "cell001_regression": cell001,
        "all_four_pressures_passed": True,
        "standing_candidate": {
            "cell002_installed_executor": "BOUNDEDLY_QUALIFIED",
            "claim_ceiling": (
                "At the tested installed bridge / policy / authority-module / "
                "temporary authority-state coordinates, the governed "
                "single-process path enforced declared-principal-bound one-shot "
                "model invocation authority, rejected exact sequential replay "
                "after consumption, rejected a mismatched declared principal "
                "before reservation or invocation, and preserved Cell-001 "
                "post-approval input revalidation before authority issuance."
            ),
        },
        "not_established": [
            "principal authentication",
            "crash-safe exactly-once",
            "concurrency safety",
            "multi-process safety",
            "distributed replay resistance",
            "local-state tamper resistance",
            "bridge-wide bypass resistance beyond the governed path",
            "network / process / filesystem containment",
            "revocation / freeze correctness",
        ],
    }


def main() -> int:
    print(json.dumps(run_installed_qualification(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
