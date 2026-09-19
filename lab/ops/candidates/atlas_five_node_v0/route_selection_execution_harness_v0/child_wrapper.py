from __future__ import annotations

import contextlib
import hashlib
import io
import json
import runpy
import sys
from pathlib import Path
from types import FrameType
from typing import Any, Callable


SCHEMA_VERSION = "atlas_route_selection_child_capture_v0"
IDENTITY_MANIFEST_NAME = "frozen_identities_v0.json"


class ExecutionEvidenceError(RuntimeError):
    """Raised when execution occurred but the evidence chain is not admissible."""


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ExecutionEvidenceError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ExecutionEvidenceError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExecutionEvidenceError(f"JSON root must be an object: {path}")
    return value


def _verify_blob(path: Path, expected_sha1: str, label: str) -> None:
    observed = git_blob_sha1(path)
    if observed != expected_sha1:
        raise ExecutionEvidenceError(
            f"{label} identity mismatch: expected {expected_sha1}, observed {observed}"
        )


def run_witnessed(
    *,
    producer_path: Path,
    apparatus_path: Path,
    a_path: Path,
    b_path: Path,
) -> dict[str, Any]:
    """Execute producer code under a trace witness and bind stdout to route returns.

    This function deliberately accepts no expected observation vector and no
    expected mechanical verdict.
    """

    apparatus_resolved = apparatus_path.resolve()
    trace_events: list[dict[str, Any]] = []
    route_calls: list[dict[str, Any]] = []
    route_returns: list[dict[str, Any]] = []
    parse_manifest_calls = 0
    parse_manifest_returns = 0

    def tracer(frame: FrameType, event: str, arg: Any) -> Callable | None:
        nonlocal parse_manifest_calls, parse_manifest_returns
        try:
            filename = Path(frame.f_code.co_filename).resolve()
        except OSError:
            return tracer

        if filename != apparatus_resolved:
            return tracer

        name = frame.f_code.co_name
        if name not in {"parse_manifest", "route"}:
            return tracer

        if event == "call":
            trace_events.append({"function": name, "event": "call"})
            if name == "parse_manifest":
                parse_manifest_calls += 1
            elif name == "route":
                call = {
                    "source_node_id": frame.f_locals.get("source_node_id"),
                    "target_node_id": frame.f_locals.get("target_node_id"),
                }
                manifest = frame.f_locals.get("manifest")
                if manifest is not None:
                    call["manifest_id"] = getattr(manifest, "manifest_id", None)
                    call["manifest_digest"] = getattr(manifest, "manifest_digest", None)
                route_calls.append(call)

        elif event == "return":
            trace_events.append({"function": name, "event": "return"})
            if name == "parse_manifest":
                parse_manifest_returns += 1
            elif name == "route":
                node_path = getattr(arg, "node_path", None)
                edge_path = getattr(arg, "edge_path", None)
                if node_path is None or edge_path is None:
                    raise ExecutionEvidenceError(
                        "route returned an object without node_path / edge_path"
                    )
                route_returns.append(
                    {
                        "node_path": list(node_path),
                        "hop_count": len(edge_path),
                    }
                )
        return tracer

    producer_stdout_buffer = io.StringIO()
    producer_stderr_buffer = io.StringIO()

    old_argv = sys.argv[:]
    old_trace = sys.gettrace()
    try:
        sys.argv = [str(producer_path)]
        sys.settrace(tracer)
        with contextlib.redirect_stdout(producer_stdout_buffer), contextlib.redirect_stderr(
            producer_stderr_buffer
        ):
            try:
                runpy.run_path(str(producer_path), run_name="__main__")
            except SystemExit as exc:
                code = exc.code
                if code not in (None, 0):
                    raise ExecutionEvidenceError(
                        f"producer exited nonzero: {code!r}"
                    ) from exc
    finally:
        sys.settrace(old_trace)
        sys.argv = old_argv

    producer_stdout = producer_stdout_buffer.getvalue()
    producer_stderr = producer_stderr_buffer.getvalue()

    if producer_stderr:
        raise ExecutionEvidenceError(
            "producer wrote to stderr; refusing to create admissible capture"
        )

    if parse_manifest_calls != 2 or parse_manifest_returns != 2:
        raise ExecutionEvidenceError(
            "required parse_manifest invocation count not witnessed: "
            f"calls={parse_manifest_calls}, returns={parse_manifest_returns}"
        )
    if len(route_calls) != 2 or len(route_returns) != 2:
        raise ExecutionEvidenceError(
            "required route invocation count not witnessed: "
            f"calls={len(route_calls)}, returns={len(route_returns)}"
        )

    for index, call in enumerate(route_calls):
        if call.get("source_node_id") != "NODE_01":
            raise ExecutionEvidenceError(
                f"route call {index} source mismatch: {call.get('source_node_id')!r}"
            )
        if call.get("target_node_id") != "NODE_04":
            raise ExecutionEvidenceError(
                f"route call {index} target mismatch: {call.get('target_node_id')!r}"
            )

    try:
        emitted = json.loads(producer_stdout)
    except json.JSONDecodeError as exc:
        raise ExecutionEvidenceError(
            f"producer stdout is not one JSON object: {exc}"
        ) from exc

    if not isinstance(emitted, dict):
        raise ExecutionEvidenceError("producer stdout JSON root must be an object")
    raw = emitted.get("raw_observation")
    if not isinstance(raw, dict):
        raise ExecutionEvidenceError("producer stdout lacks raw_observation object")

    expected_from_returns = {
        "A_SELECTED_NODE_PATH": route_returns[0]["node_path"],
        "A_HOP_COUNT": route_returns[0]["hop_count"],
        "B_SELECTED_NODE_PATH": route_returns[1]["node_path"],
        "B_HOP_COUNT": route_returns[1]["hop_count"],
    }
    for field, witnessed in expected_from_returns.items():
        if raw.get(field) != witnessed:
            raise ExecutionEvidenceError(
                f"producer observation is not apparatus-derived for {field}: "
                f"stdout={raw.get(field)!r}, witnessed={witnessed!r}"
            )

    a_sha256 = sha256_bytes(a_path.read_bytes())
    b_sha256 = sha256_bytes(b_path.read_bytes())
    if raw.get("A_manifest_sha256") != a_sha256:
        raise ExecutionEvidenceError("producer A_manifest_sha256 does not match frozen A bytes")
    if raw.get("B_manifest_sha256") != b_sha256:
        raise ExecutionEvidenceError("producer B_manifest_sha256 does not match frozen B bytes")

    return {
        "schema_version": SCHEMA_VERSION,
        "producer_stdout": producer_stdout,
        "producer_stderr": producer_stderr,
        "producer_stdout_sha256": sha256_bytes(producer_stdout.encode("utf-8")),
        "producer_stderr_sha256": sha256_bytes(producer_stderr.encode("utf-8")),
        "apparatus_witness": {
            "apparatus_path": str(apparatus_resolved),
            "parse_manifest_calls": parse_manifest_calls,
            "parse_manifest_returns": parse_manifest_returns,
            "route_calls": route_calls,
            "route_returns": route_returns,
            "trace_events": trace_events,
        },
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _main() -> int:
    harness_dir = Path(__file__).resolve().parent
    identity_manifest_path = harness_dir / IDENTITY_MANIFEST_NAME
    identities = _load_json(identity_manifest_path)

    root = _repo_root()
    required = {
        "child_wrapper": Path(__file__).resolve(),
        "apparatus": root / identities["apparatus"]["path"],
        "producer": root / identities["producer"]["path"],
        "A": root / identities["A"]["path"],
        "B": root / identities["B"]["path"],
    }
    for key, path in required.items():
        _verify_blob(path, identities[key]["blob_sha1"], key)

    capture = run_witnessed(
        producer_path=required["producer"],
        apparatus_path=required["apparatus"],
        a_path=required["A"],
        b_path=required["B"],
    )
    print(json.dumps(capture, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print(
            json.dumps(
                {
                    "schema_version": "atlas_route_selection_child_error_v0",
                    "error": "child wrapper accepts no caller-supplied observation or verdict inputs",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(64)

    try:
        raise SystemExit(_main())
    except ExecutionEvidenceError as exc:
        print(
            json.dumps(
                {
                    "schema_version": "atlas_route_selection_child_error_v0",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(65)
