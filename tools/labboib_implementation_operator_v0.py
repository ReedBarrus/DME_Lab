#!/usr/bin/env python3
"""LABBOIB_IMPLEMENTATION_OPERATOR_001 bounded implementation membrane.

This executable candidate qualifies an isolated implementation workspace and a
fixture implementer. It intentionally does not invoke Codex, commit, merge, or
admit a realization into the canonical repository.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
import subprocess
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.causal_applicability_v0 import judge as judge_applicability

REQUEST_SCHEMA = "implementation_request_v0"
REALIZATION_SCHEMA = "implementation_realization_v0"
SEAT_ID = "LABBOIB"
OPERATOR_ID = "ISOLATED_IMPLEMENTATION_FIXTURE"
AUTHORITY_PATH = (
    "lab/ops/candidates/LABBOIB_IMPLEMENTATION_OPERATOR_001/authority_v0.json"
)
AUTHORITY_ID = "LABBOIB_IMPLEMENTATION_OPERATOR_001_FIXTURE_AUTHORITY"
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")

DECLARED_CHECKS: dict[str, list[str]] = {
    "PY_COMPILE_FOO": [sys.executable, "-m", "py_compile", "foo.py"],
}


class ImplementationOperatorError(RuntimeError):
    pass


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise ImplementationOperatorError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result


def _git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise ImplementationOperatorError(
            f"git {' '.join(args)} failed: "
            + result.stderr.decode("utf-8", errors="replace").strip()
        )
    return result.stdout


def _repo_head(repo: Path) -> str:
    head = _git(repo, "rev-parse", "HEAD").stdout.strip().lower()
    if _SHA1_RE.fullmatch(head) is None:
        raise ImplementationOperatorError("repository HEAD is not a 40-hex commit")
    return head


def _resolve_commit(repo: Path, ref: str) -> str:
    commit = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").stdout.strip().lower()
    if _SHA1_RE.fullmatch(commit) is None:
        raise ImplementationOperatorError("basis did not resolve to a 40-hex commit")
    return commit


def _safe_relpath(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ImplementationOperatorError("path must be non-empty")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
        raise ImplementationOperatorError(f"unsafe repository path {value!r}")
    normalized = path.as_posix()
    if normalized in {".", ""}:
        raise ImplementationOperatorError("path must name a file")
    return normalized


def validate_request(request: dict[str, Any]) -> None:
    required = {
        "schema",
        "request_id",
        "seat_id",
        "repository",
        "basis_commit",
        "allowed_paths",
        "requested_effect",
        "qualification_contract",
        "operator_id",
        "authority_ref",
    }
    if set(request) != required:
        raise ImplementationOperatorError("request fields differ from implementation_request_v0")
    if request["schema"] != REQUEST_SCHEMA:
        raise ImplementationOperatorError("unexpected request schema")
    if request["seat_id"] != SEAT_ID:
        raise ImplementationOperatorError("request seat_id is not LABBOIB")
    if request["operator_id"] != OPERATOR_ID:
        raise ImplementationOperatorError("unexpected operator_id")
    if not isinstance(request["request_id"], str) or not request["request_id"]:
        raise ImplementationOperatorError("request_id must be non-empty")
    if not isinstance(request["repository"], str) or not request["repository"]:
        raise ImplementationOperatorError("repository must be non-empty")
    if _SHA1_RE.fullmatch(request["basis_commit"]) is None:
        raise ImplementationOperatorError("basis_commit must be lowercase 40-hex")
    if not isinstance(request["requested_effect"], str) or not request["requested_effect"]:
        raise ImplementationOperatorError("requested_effect must be non-empty")
    if not isinstance(request["authority_ref"], str) or not request["authority_ref"]:
        raise ImplementationOperatorError("authority_ref must be non-empty")

    allowed = request["allowed_paths"]
    if not isinstance(allowed, list) or not allowed:
        raise ImplementationOperatorError("allowed_paths must be a non-empty list")
    normalized = [_safe_relpath(v) for v in allowed]
    if len(normalized) != len(set(normalized)):
        raise ImplementationOperatorError("allowed_paths must be unique")

    contract = request["qualification_contract"]
    if not isinstance(contract, dict) or set(contract) != {
        "exact_file_sha256",
        "declared_check_ids",
    }:
        raise ImplementationOperatorError("invalid qualification_contract")
    expected_files = contract["exact_file_sha256"]
    if not isinstance(expected_files, dict):
        raise ImplementationOperatorError("exact_file_sha256 must be an object")
    for path, digest in expected_files.items():
        normalized_path = _safe_relpath(path)
        if normalized_path not in normalized:
            raise ImplementationOperatorError(
                "effect-contract paths must be inside allowed_paths"
            )
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ImplementationOperatorError("file digest must be lowercase SHA-256")
    checks = contract["declared_check_ids"]
    if not isinstance(checks, list) or len(checks) != len(set(checks)):
        raise ImplementationOperatorError("declared_check_ids must be a unique list")
    for check_id in checks:
        if check_id not in DECLARED_CHECKS:
            raise ImplementationOperatorError(f"undeclared mechanical check {check_id!r}")


def load_authority(authority_override: dict[str, Any] | None = None) -> dict[str, Any]:
    if authority_override is not None:
        authority = copy.deepcopy(authority_override)
    else:
        authority = json.loads((ROOT / AUTHORITY_PATH).read_text(encoding="utf-8"))
    if authority.get("authority_id") != AUTHORITY_ID:
        raise ImplementationOperatorError("unexpected implementation authority identity")
    return authority


def authority_allows(
    request: dict[str, Any],
    authority: dict[str, Any],
) -> bool:
    return bool(
        request["authority_ref"] == AUTHORITY_PATH
        and authority.get("seat_id") == SEAT_ID
        and authority.get("operator_id") == OPERATOR_ID
        and authority.get("invocation_authorized") is True
        and authority.get("canonical_workspace_write_authorized") is False
        and authority.get("commit_authorized") is False
        and authority.get("merge_authorized") is False
        and authority.get("admission_authorized") is False
        and authority.get("scientific_promotion_authorized") is False
    )


def fixture_implement(
    worktree: Path,
    mode: str,
    environment_intervention: Callable[[], None] | None = None,
) -> tuple[int, str]:
    """Deterministic stand-in for the future semantic implementation operator."""
    foo = worktree / "foo.py"
    bar = worktree / "bar.py"

    if mode == "EXACT":
        foo.write_text("VALUE = 2\n", encoding="utf-8")
        if environment_intervention is not None:
            environment_intervention()
        return 0, "DONE"

    if mode == "OUT_OF_SCOPE":
        foo.write_text("VALUE = 2\n", encoding="utf-8")
        bar.write_text('EXTRA = "changed"\n', encoding="utf-8")
        if environment_intervention is not None:
            environment_intervention()
        return 0, "DONE"

    if mode == "USEFUL_BUT_WRONG":
        foo.write_text("VALUE = 2\n# additional helpful change\n", encoding="utf-8")
        if environment_intervention is not None:
            environment_intervention()
        return 0, "DONE"

    if mode == "PARTIAL_FAILURE":
        foo.write_text("VALUE = 2\n", encoding="utf-8")
        if environment_intervention is not None:
            environment_intervention()
        return 17, "FAILED_AFTER_PARTIAL_EDIT"

    if mode == "CLAIM_ONLY":
        if environment_intervention is not None:
            environment_intervention()
        return 0, "DONE"

    raise ImplementationOperatorError(f"unknown fixture mode {mode!r}")


class ImplementationHarness:
    def __init__(self, canonical_repo: str | Path, state_dir: str | Path):
        self.canonical_repo = Path(canonical_repo).resolve()
        self.state_dir = Path(state_dir).resolve()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        (self.state_dir / "worktrees").mkdir(exist_ok=True)
        (self.state_dir / "artifacts").mkdir(exist_ok=True)
        self.db_path = self.state_dir / "implementation_operator.sqlite3"
        self._initialize_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requests(
                    request_id TEXT PRIMARY KEY,
                    request_sha256 TEXT NOT NULL,
                    status TEXT NOT NULL,
                    realization_json TEXT,
                    result_json TEXT
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def _request_digest(self, request: dict[str, Any]) -> str:
        return _sha256_bytes(_canonical_json_bytes(request))

    def _retained(self, request: dict[str, Any]) -> dict[str, Any] | None:
        digest = self._request_digest(request)
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM requests WHERE request_id = ?",
                (request["request_id"],),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        if row["request_sha256"] != digest:
            raise ImplementationOperatorError(
                "request_id already names different request bytes"
            )
        if row["status"] != "REALIZED":
            raise ImplementationOperatorError("request exists without retained realization")
        realization = json.loads(row["realization_json"])
        current_head = _repo_head(self.canonical_repo)
        applicability = self._judge_applicability(
            realization,
            current_head,
            suffix="REPLAY",
        )
        retained = json.loads(row["result_json"])
        retained["idempotent_replay"] = True
        retained["operator_invoked"] = False
        retained["applicability"] = applicability
        retained["canonical_head_at_replay"] = current_head
        return retained

    def _register_started(self, request: dict[str, Any]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO requests(request_id, request_sha256, status)
                VALUES(?,?,?)
                """,
                (request["request_id"], self._request_digest(request), "STARTED"),
            )
            conn.commit()
        finally:
            conn.close()

    def _retain_result(
        self,
        request_id: str,
        realization: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE requests
                SET status = 'REALIZED',
                    realization_json = ?,
                    result_json = ?
                WHERE request_id = ?
                """,
                (
                    json.dumps(realization, sort_keys=True),
                    json.dumps(result, sort_keys=True),
                    request_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _create_worktree(
        self,
        request: dict[str, Any],
    ) -> tuple[Path, str, str]:
        basis = _resolve_commit(self.canonical_repo, request["basis_commit"])
        if basis != request["basis_commit"]:
            raise ImplementationOperatorError("request basis did not resolve exactly")
        request_digest = self._request_digest(request)
        rel = Path("worktrees") / request_digest[:20]
        worktree = self.state_dir / rel
        if worktree.exists():
            raise ImplementationOperatorError("isolated worktree already exists")
        _git(
            self.canonical_repo,
            "worktree",
            "add",
            "--detach",
            str(worktree),
            basis,
        )
        observed = _repo_head(worktree)
        if observed != basis:
            raise ImplementationOperatorError("isolated worktree did not bind exact basis")
        identity = _sha256_bytes(
            f"{request['request_id']}\n{basis}\n{request_digest}\n".encode("utf-8")
        )
        return worktree, rel.as_posix(), identity

    def _run_checks(
        self,
        worktree: Path,
        check_ids: list[str],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for check_id in check_ids:
            argv = DECLARED_CHECKS[check_id]
            process = subprocess.run(
                argv,
                cwd=worktree,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=30,
            )
            results.append(
                {
                    "check_id": check_id,
                    "argv": argv,
                    "returncode": process.returncode,
                    "result": "PASS" if process.returncode == 0 else "FAIL",
                }
            )
        return results

    def _stage_and_derive_delta(
        self,
        worktree: Path,
    ) -> tuple[bytes, list[str], list[str], list[str], list[str]]:
        _git(worktree, "add", "-A")
        diff = _git_bytes(
            worktree,
            "diff",
            "--cached",
            "--binary",
            "--full-index",
            "HEAD",
            "--",
        )
        names = _git(
            worktree,
            "diff",
            "--cached",
            "--name-status",
            "HEAD",
            "--",
        ).stdout.splitlines()

        touched: list[str] = []
        added: list[str] = []
        modified: list[str] = []
        deleted: list[str] = []
        for line in names:
            if not line.strip():
                continue
            parts = line.split("\t")
            status = parts[0]
            path = parts[-1]
            touched.append(path)
            if status.startswith("A"):
                added.append(path)
            elif status.startswith("D"):
                deleted.append(path)
            else:
                modified.append(path)

        return (
            diff,
            sorted(touched),
            sorted(added),
            sorted(modified),
            sorted(deleted),
        )

    def _effect_contract_status(
        self,
        worktree: Path,
        request: dict[str, Any],
    ) -> str:
        expected = request["qualification_contract"]["exact_file_sha256"]
        for rel, digest in expected.items():
            path = worktree / rel
            if not path.is_file():
                return "INVALID"
            if _sha256_bytes(path.read_bytes()) != digest:
                return "INVALID"
        return "VALID"

    def _judge_applicability(
        self,
        realization: dict[str, Any],
        comparison_head: str,
        *,
        suffix: str,
    ) -> dict[str, Any]:
        realization_bytes = _canonical_json_bytes(realization)
        envelope = {
            "schema": "causal_applicability_realization_v0",
            "realization_id": realization["realization_id"],
            "realization_kind": "IMPLEMENTATION_REALIZATION",
            "realization_basis": realization["realization_basis"],
            "mechanical_result": realization["mechanical_result"],
            "payload_ref": "sha256:" + _sha256_bytes(realization_bytes),
        }
        return judge_applicability(
            envelope,
            comparison_head,
            f"J-{realization['realization_id']}-{suffix}-{comparison_head[:12]}",
        )

    def execute_request(
        self,
        request: dict[str, Any],
        *,
        fixture_mode: str,
        authority_override: dict[str, Any] | None = None,
        environment_intervention: Callable[[], None] | None = None,
    ) -> dict[str, Any]:
        validate_request(request)

        retained = self._retained(request)
        if retained is not None:
            return retained

        authority = load_authority(authority_override)
        authority_sha256 = _sha256_bytes(_canonical_json_bytes(authority))
        if not authority_allows(request, authority):
            return {
                "status": "AUTHORITY_REQUIRED",
                "request_id": request["request_id"],
                "operator_id": request["operator_id"],
                "operator_invoked": False,
                "worktree_created": False,
                "realization": None,
                "authority_sha256": authority_sha256,
                "admission": "NONE",
            }

        self._register_started(request)

        canonical_head_before = _repo_head(self.canonical_repo)
        worktree, worktree_ref, worktree_identity = self._create_worktree(request)

        process_exit, claimed_status = fixture_implement(
            worktree,
            fixture_mode,
            environment_intervention=environment_intervention,
        )

        checks = self._run_checks(
            worktree,
            request["qualification_contract"]["declared_check_ids"],
        )
        diff, touched, added, modified, deleted = self._stage_and_derive_delta(worktree)

        allowed = set(request["allowed_paths"])
        scope_status = "VALID" if set(touched).issubset(allowed) else "INVALID"
        effect_status = self._effect_contract_status(worktree, request)

        checks_pass = all(item["result"] == "PASS" for item in checks)
        mechanical_result = (
            "PASS"
            if process_exit == 0 and len(diff) > 0 and checks_pass
            else "FAIL"
        )

        diff_sha = _sha256_bytes(diff)
        realization_id = f"D-{request['request_id']}-{diff_sha[:16]}"
        realization = {
            "schema": REALIZATION_SCHEMA,
            "realization_id": realization_id,
            "request_id": request["request_id"],
            "realization_basis": request["basis_commit"],
            "worktree_ref": worktree_ref,
            "worktree_identity": worktree_identity,
            "diff_sha256": diff_sha,
            "diff_bytes": len(diff),
            "touched_paths": touched,
            "added_paths": added,
            "modified_paths": modified,
            "deleted_paths": deleted,
            "process_exit": process_exit,
            "operator_claimed_status": claimed_status,
            "mechanical_checks": checks,
            "scope_status": scope_status,
            "effect_contract_status": effect_status,
            "mechanical_result": mechanical_result,
            "canonical_workspace_mutation_effect": "NONE_BY_OPERATOR",
            "commit_effect": "NONE",
            "merge_effect": "NONE",
            "scientific_standing_effect": "NONE",
        }

        diff_path = self.state_dir / "artifacts" / f"{realization_id}.diff"
        realization_path = self.state_dir / "artifacts" / f"{realization_id}.json"
        diff_path.write_bytes(diff)
        realization_path.write_bytes(_canonical_json_bytes(realization))

        canonical_head_after = _repo_head(self.canonical_repo)
        applicability = self._judge_applicability(
            realization,
            canonical_head_after,
            suffix="RETURN",
        )

        if applicability["result"] == "STALE":
            admission = "NOT_ADMITTED_STALE"
        elif scope_status == "INVALID":
            admission = "NOT_ADMITTED_SCOPE"
        elif effect_status == "INVALID":
            admission = "NOT_ADMITTED_EFFECT_CONTRACT"
        elif mechanical_result == "FAIL":
            admission = "NOT_ADMITTED_MECHANICAL"
        else:
            admission = "NOT_ADMITTED_NO_CONSEQUENCE_AUTHORITY"

        result = {
            "status": "REALIZED",
            "request_id": request["request_id"],
            "operator_id": request["operator_id"],
            "operator_invoked": True,
            "worktree_created": True,
            "authority_sha256": authority_sha256,
            "canonical_head_at_start": canonical_head_before,
            "canonical_head_at_return": canonical_head_after,
            "realization": realization,
            "realization_artifact_ref": realization_path.relative_to(self.state_dir).as_posix(),
            "diff_artifact_ref": diff_path.relative_to(self.state_dir).as_posix(),
            "applicability": applicability,
            "admission": admission,
            "idempotent_replay": False,
        }
        self._retain_result(request["request_id"], realization, result)
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument(
        "--fixture-mode",
        required=True,
        choices=[
            "EXACT",
            "OUT_OF_SCOPE",
            "USEFUL_BUT_WRONG",
            "PARTIAL_FAILURE",
            "CLAIM_ONLY",
        ],
    )
    args = parser.parse_args(argv)

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    if not isinstance(request, dict):
        raise ImplementationOperatorError("request must be a JSON object")

    harness = ImplementationHarness(args.repo, args.state_dir)
    result = harness.execute_request(request, fixture_mode=args.fixture_mode)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
