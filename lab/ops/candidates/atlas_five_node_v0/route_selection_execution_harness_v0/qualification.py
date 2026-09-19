from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

import child_wrapper
import harness


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "qualification_fixture"


def _expect_harness_reject(fn, contains: str | None = None) -> str:
    try:
        fn()
    except harness.HarnessError as exc:
        text = str(exc)
        if contains is not None and contains not in text:
            raise AssertionError(
                f"rejection mismatch; expected substring {contains!r}, got {text!r}"
            )
        return text
    raise AssertionError("expected HarnessError but call succeeded")


def _git_blob_sha1(path: Path) -> str:
    return harness.git_blob_sha1(path)


def _spawn_internal(
    producer: Path,
    apparatus: Path,
    a_path: Path,
    b_path: Path,
) -> subprocess.CompletedProcess[str]:
    env = {
        "PYTHONPATH": str(HERE),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if "SYSTEMROOT" in os.environ:
        env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
    if "WINDIR" in os.environ:
        env["WINDIR"] = os.environ["WINDIR"]
    return subprocess.run(
        [
            sys.executable,
            "-S",
            str(Path(__file__).resolve()),
            "_internal_witness",
            str(producer),
            str(apparatus),
            str(a_path),
            str(b_path),
        ],
        cwd=HERE,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _internal_witness(argv: list[str]) -> int:
    if len(argv) != 6:
        print("internal witness argument error", file=sys.stderr)
        return 64
    _, _, producer, apparatus, a_path, b_path = argv
    try:
        capture = child_wrapper.run_witnessed(
            producer_path=Path(producer),
            apparatus_path=Path(apparatus),
            a_path=Path(a_path),
            b_path=Path(b_path),
        )
    except child_wrapper.ExecutionEvidenceError as exc:
        print(
            json.dumps(
                {"schema_version": "qualification_internal_error_v0", "error": str(exc)},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 65
    print(json.dumps(capture, sort_keys=True, separators=(",", ":")))
    return 0


def _qualification_paths() -> dict[str, Path]:
    return {
        "apparatus": FIXTURE / "qualification_apparatus.py",
        "A": FIXTURE / "A_manifest.json",
        "B": FIXTURE / "B_manifest.json",
        "valid_producer": FIXTURE / "valid_producer.py",
        "counterfeit_producer": FIXTURE / "counterfeit_producer.py",
        "wrong_apparatus": FIXTURE / "qualification_wrong_apparatus.py",
        "wrong_apparatus_producer": FIXTURE / "wrong_apparatus_producer.py",
        "nonzero_producer": FIXTURE / "nonzero_producer.py",
    }


def run_qualification() -> dict[str, Any]:
    paths = _qualification_paths()
    results: dict[str, Any] = {}

    # Q1: wrong apparatus bytes -> refused by exact identity verifier.
    with tempfile.TemporaryDirectory() as td:
        wrong = Path(td) / "qualification_apparatus.py"
        wrong.write_bytes(paths["apparatus"].read_bytes() + b"\n# mutated\n")
        expected = _git_blob_sha1(paths["apparatus"])
        message = _expect_harness_reject(
            lambda: harness.verify_git_blob_identity(wrong, expected, "apparatus"),
            "identity mismatch",
        )
        results["Q1_wrong_apparatus_bytes"] = {"status": "PASS", "rejection": message}

    # Q2: wrong producer bytes and wrong harness bytes -> both refused.
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        wrong_producer = td_path / "valid_producer.py"
        wrong_producer.write_bytes(paths["valid_producer"].read_bytes() + b"\n# mutated\n")
        producer_expected = _git_blob_sha1(paths["valid_producer"])
        producer_rejection = _expect_harness_reject(
            lambda: harness.verify_git_blob_identity(
                wrong_producer, producer_expected, "producer"
            ),
            "identity mismatch",
        )

        wrong_harness = td_path / "harness.py"
        wrong_harness.write_bytes(Path(harness.__file__).read_bytes() + b"\n# mutated\n")
        harness_expected = _git_blob_sha1(Path(harness.__file__))
        harness_rejection = _expect_harness_reject(
            lambda: harness.verify_git_blob_identity(
                wrong_harness, harness_expected, "harness"
            ),
            "identity mismatch",
        )
        results["Q2_wrong_producer_or_harness_bytes"] = {
            "status": "PASS",
            "producer_rejection": producer_rejection,
            "harness_rejection": harness_rejection,
        }

    # Q3: wrong A/B bytes -> refused by exact identity verifier.
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        rejections = {}
        for label in ("A", "B"):
            wrong = td_path / f"{label}_manifest.json"
            wrong.write_bytes(paths[label].read_bytes() + b"\n")
            expected = _git_blob_sha1(paths[label])
            rejections[label] = _expect_harness_reject(
                lambda wrong=wrong, expected=expected, label=label:
                    harness.verify_git_blob_identity(wrong, expected, label),
                "identity mismatch",
            )
        results["Q3_wrong_A_or_B_bytes"] = {
            "status": "PASS",
            "rejections": rejections,
        }

    # Q4: an expected vector supplied to the production harness is rejected
    # before child execution and cannot produce evidence.
    env = {
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if "SYSTEMROOT" in os.environ:
        env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
    if "WINDIR" in os.environ:
        env["WINDIR"] = os.environ["WINDIR"]
    q4 = subprocess.run(
        [
            sys.executable,
            "-S",
            str(Path(harness.__file__).resolve()),
            "--expected-vector",
            "NODE_01,NODE_02,NODE_04",
        ],
        cwd=HERE,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if q4.returncode != 64 or q4.stdout:
        raise AssertionError(
            f"Q4 failed: exit={q4.returncode}, stdout={q4.stdout!r}, stderr={q4.stderr!r}"
        )
    results["Q4_expected_vector_without_invocation"] = {
        "status": "PASS",
        "exit_code": q4.returncode,
        "stdout_empty": True,
    }

    # Q5: a real subprocess can print the expected-looking vector and still
    # fail because exact apparatus calls were not witnessed.
    q5 = _spawn_internal(
        paths["counterfeit_producer"],
        paths["apparatus"],
        paths["A"],
        paths["B"],
    )
    if q5.returncode == 0 or "parse_manifest invocation count not witnessed" not in q5.stderr:
        raise AssertionError(
            f"Q5 failed: exit={q5.returncode}, stdout={q5.stdout!r}, stderr={q5.stderr!r}"
        )
    results["Q5_real_subprocess_without_apparatus_invocation"] = {
        "status": "PASS",
        "exit_code": q5.returncode,
        "rejection": json.loads(q5.stderr)["error"],
    }

    # Q6: a producer may call a substituted apparatus and still fail because
    # no calls into the designated exact apparatus file were witnessed.
    q6 = _spawn_internal(
        paths["wrong_apparatus_producer"],
        paths["apparatus"],
        paths["A"],
        paths["B"],
    )
    if q6.returncode == 0 or "parse_manifest invocation count not witnessed" not in q6.stderr:
        raise AssertionError(
            f"Q6 failed: exit={q6.returncode}, stdout={q6.stdout!r}, stderr={q6.stderr!r}"
        )
    results["Q6_wrong_or_substituted_apparatus"] = {
        "status": "PASS",
        "exit_code": q6.returncode,
        "rejection": json.loads(q6.stderr)["error"],
    }

    # Q7: nonzero producer exit -> no admissible capture.
    q7 = _spawn_internal(
        paths["nonzero_producer"],
        paths["apparatus"],
        paths["A"],
        paths["B"],
    )
    if q7.returncode == 0 or "producer exited nonzero" not in q7.stderr:
        raise AssertionError(
            f"Q7 failed: exit={q7.returncode}, stdout={q7.stdout!r}, stderr={q7.stderr!r}"
        )
    results["Q7_nonzero_process_exit"] = {
        "status": "PASS",
        "exit_code": q7.returncode,
        "rejection": json.loads(q7.stderr)["error"],
    }

    # Q10 first: valid qualification-only producer execution in a fresh
    # qualification fixture. This does NOT execute the scientific A/B cells.
    q10 = _spawn_internal(
        paths["valid_producer"],
        paths["apparatus"],
        paths["A"],
        paths["B"],
    )
    if q10.returncode != 0 or q10.stderr:
        raise AssertionError(
            f"Q10 valid execution failed: exit={q10.returncode}, "
            f"stdout={q10.stdout!r}, stderr={q10.stderr!r}"
        )
    capture = json.loads(q10.stdout)
    qualification_paths = {
        "apparatus": paths["apparatus"],
        "producer": paths["valid_producer"],
        "A": paths["A"],
        "B": paths["B"],
    }
    raw, result = harness._validate_child_capture(
        capture,
        identities={},
        paths=qualification_paths,
    )
    results["Q10_valid_witnessed_apparatus_execution"] = {
        "status": "PASS",
        "child_process_exit_code": q10.returncode,
        "parse_manifest_calls": capture["apparatus_witness"]["parse_manifest_calls"],
        "route_calls": len(capture["apparatus_witness"]["route_calls"]),
        "raw_observation": raw,
        "independent_mechanical_result": result,
        "scientific_cells_consumed": False,
    }

    # Q8: digest mismatch in captured producer stdout is rejected.
    q8_capture = deepcopy(capture)
    q8_capture["producer_stdout_sha256"] = "0" * 64
    q8_rejection = _expect_harness_reject(
        lambda: harness._validate_child_capture(
            q8_capture,
            identities={},
            paths=qualification_paths,
        ),
        "producer stdout digest mismatch",
    )
    results["Q8_captured_output_hash_mismatch"] = {
        "status": "PASS",
        "rejection": q8_rejection,
    }

    # Q9: even with a recomputed stdout digest, a mechanical verdict that
    # disagrees with independent recomputation is rejected.
    q9_capture = deepcopy(capture)
    emitted = json.loads(q9_capture["producer_stdout"])
    emitted["mechanical_result"]["verdict"] = (
        "PASS"
        if emitted["mechanical_result"]["verdict"] == "FRACTURE"
        else "FRACTURE"
    )
    tampered_stdout = json.dumps(emitted, sort_keys=True)
    q9_capture["producer_stdout"] = tampered_stdout
    q9_capture["producer_stdout_sha256"] = harness.sha256_bytes(
        tampered_stdout.encode("utf-8")
    )
    q9_rejection = _expect_harness_reject(
        lambda: harness._validate_child_capture(
            q9_capture,
            identities={},
            paths=qualification_paths,
        ),
        "mechanical result differs from independent recomputation",
    )
    results["Q9_mechanical_result_content_mismatch"] = {
        "status": "PASS",
        "rejection": q9_rejection,
    }

    return {
        "schema_version": "atlas_route_selection_execution_harness_qualification_v0",
        "qualification_scope": (
            "execution-evidence mechanics only; scientific A/B cells were not invoked"
        ),
        "results": results,
        "summary": {
            "passed": sum(1 for item in results.values() if item["status"] == "PASS"),
            "total": len(results),
            "all_pass": all(item["status"] == "PASS" for item in results.values()),
            "scientific_result": "NONE",
            "scientific_promotion": "NONE",
            "runtime_node_instantiation": "NONE",
        },
    }


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "_internal_witness":
        return _internal_witness(sys.argv)

    if len(sys.argv) != 1:
        print("qualification runner accepts no external test-vector arguments", file=sys.stderr)
        return 64

    report = run_qualification()
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["summary"]["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
