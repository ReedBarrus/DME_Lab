"""Execute the first bounded PR-006 Q_OPERATION confirmatory pressure.

This fixture compares controlled stasis with one same-byte overwrite while
reusing the already-qualified NTFS USN observation basis.  It is not a general
filesystem observer and does not pressure logical hidden-content traversal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.runtime.ntfs_usn_observation_basis_qualification import (
    CONTENT_A,
    FILE_SHARE_READ,
    FILE_SHARE_WRITE,
    GENERIC_READ,
    QualificationError,
    SOURCE_INFO_POLICY,
    USN_REASON_CLOSE,
    Win32,
    _baseline,
    _endpoint_for_path,
    _i64,
    _journal_int,
    _same_volume,
    _u64,
    _volume_device,
    _volume_root,
    probe_read_mode,
    query_journal,
    read_interval,
    record_acceptance,
    run_arm,
)


EXPERIMENT_ID = "ntfs_usn_q_operation_pressure_v0"
DEFAULT_TRACE = Path("traces") / f"{EXPERIMENT_ID}.json"


def frozen_read_parameters(journal_id: int) -> dict[str, Any]:
    return {
        "request_structure": "READ_USN_JOURNAL_DATA_V1",
        "ReasonMask": {
            "decimal": str(USN_REASON_CLOSE),
            "hex": f"0x{USN_REASON_CLOSE:08X}",
            "name": "USN_REASON_CLOSE",
        },
        "ReturnOnlyOnClose": 1,
        "Timeout": 0,
        "BytesToWaitFor": 0,
        "UsnJournalID": _u64(journal_id),
        "MinMajorVersion": 2,
        "MaxMajorVersion": 2,
        "acceptance_reason_conjunction": [
            "USN_REASON_CLOSE",
            "USN_REASON_DATA_OVERWRITE",
        ],
        "SourceInfo_policy": SOURCE_INFO_POLICY,
    }


def _accepted_records(
    records: list[dict[str, Any]], *, start_usn: int, end_usn: int, file_id64: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    candidates: list[dict[str, Any]] = []
    qualifying: list[dict[str, Any]] = []
    source_policy_ambiguity = False
    for record in records:
        acceptance = record_acceptance(
            record, start_usn=start_usn, end_usn=end_usn, file_id64=file_id64
        )
        annotated = {**record, "acceptance": acceptance}
        checks = acceptance["checks"]
        if (
            checks["within_frozen_interval"]
            and checks["file_reference_matches_complete_file_id64"]
        ):
            candidates.append(annotated)
            if (
                checks["major_version_is_2"]
                and checks["reason_contains_close"]
                and checks["reason_contains_data_overwrite"]
                and not checks["source_info_policy_satisfied"]
            ):
                source_policy_ambiguity = True
        if acceptance["accepted"]:
            qualifying.append(annotated)
    return candidates, qualifying, source_policy_ambiguity


def run_stasis_arm(
    win32: Win32,
    volume_handle: Any,
    volume_root: str,
    fixture_path: Path,
) -> dict[str, Any]:
    arm: dict[str, Any] = {
        "arm_identity": "S",
        "controlled_history": {
            "classification_basis": "controlled fixture declaration",
            "declared_history": "A -------------------- A",
            "selected_file_mutations_between_S_and_E": 0,
            "write_issued": False,
            "prohibited_mutations_issued": False,
        },
    }
    try:
        _baseline(fixture_path)
        c0 = _endpoint_for_path(win32, fixture_path, len(CONTENT_A))
        before_volume = win32.volume_identity(volume_root)
        before_journal = query_journal(win32, volume_handle)
        start_usn = _journal_int(before_journal, "NextUsn")
        journal_id = int(before_journal["UsnJournalID"]["decimal"])

        # The frozen control contains no selected-file operation here.
        after_journal = query_journal(win32, volume_handle)
        end_usn = _journal_int(after_journal, "NextUsn")
        after_volume = win32.volume_identity(volume_root)
        continuity = {
            "same_volume_identity": _same_volume(before_volume, after_volume),
            "filesystem_is_ntfs": before_volume["filesystem"].upper() == "NTFS",
            "same_UsnJournalID": (
                before_journal["UsnJournalID"] == after_journal["UsnJournalID"]
            ),
            "S_not_below_final_FirstUsn": start_usn
            >= _journal_int(after_journal, "FirstUsn"),
            "S_not_below_final_LowestValidUsn": start_usn
            >= _journal_int(after_journal, "LowestValidUsn"),
            "valid_interval": end_usn >= start_usn,
        }
        if not all(continuity.values()):
            raise QualificationError(
                "invalid", "stasis journal continuity", json.dumps(continuity, sort_keys=True)
            )

        acquisition = read_interval(
            win32,
            volume_handle,
            start_usn=start_usn,
            end_usn=end_usn,
            journal_id=journal_id,
        )
        c1 = _endpoint_for_path(win32, fixture_path, len(CONTENT_A))
        c0_id = int(c0["identity"]["fileID64"]["decimal"])
        c1_id = int(c1["identity"]["fileID64"]["decimal"])
        expected_hash = hashlib.sha256(CONTENT_A).hexdigest()
        identity_checks = {
            "C0_C1_complete_fileID64_equal": c0_id == c1_id,
            "file_identity_volume_matches_selected_volume": (
                c0["identity"]["volume_serial_number"]
                == c1["identity"]["volume_serial_number"]
                == before_volume["volume_serial_number"]
            ),
        }
        endpoint_checks = {
            "C0_is_A": c0["sha256"] == expected_hash,
            "C1_is_A": c1["sha256"] == expected_hash,
            "C0_equals_C1": c0["sha256"] == c1["sha256"],
            "length_preserved": c0["byte_length"] == c1["byte_length"] == len(CONTENT_A),
        }
        if not all(identity_checks.values()) or not all(endpoint_checks.values()):
            raise QualificationError(
                "invalid",
                "stasis endpoint or identity",
                json.dumps(
                    {"identity": identity_checks, "endpoint": endpoint_checks},
                    sort_keys=True,
                ),
            )
        candidates, qualifying, source_ambiguity = _accepted_records(
            acquisition["records"],
            start_usn=start_usn,
            end_usn=end_usn,
            file_id64=c0_id,
        )
        arm.update(
            {
                "endpoint_content_observation": {
                    "C0": c0,
                    "C1": c1,
                    "checks": endpoint_checks,
                    "endpoint_equivalent": all(endpoint_checks.values()),
                },
                "file_identity": {
                    "C0": c0["identity"],
                    "C1": c1["identity"],
                    "checks": identity_checks,
                    "continuous": all(identity_checks.values()),
                },
                "volume_and_journal": {
                    "before_volume": before_volume,
                    "after_volume": after_volume,
                    "before_journal": before_journal,
                    "after_journal": after_journal,
                    "S": _i64(start_usn),
                    "E": _i64(end_usn),
                    "continuity": continuity,
                },
                "usn_operation_observation": {
                    "read_parameters": frozen_read_parameters(journal_id),
                    "acquisition": acquisition,
                    "continuation_cursors": [
                        call["returned_continuation_usn"] for call in acquisition["calls"]
                    ],
                    "candidate_records": candidates,
                    "qualifying_records": qualifying,
                    "qualifying_record_observed": bool(qualifying),
                },
                "lifecycle": {
                    "baseline_handles_closed_before_S": True,
                    "no_selected_file_mutation_between_S_and_E": True,
                    "bounded_read_completed": acquisition["acquisition_complete"],
                    "endpoint_observed_after_E": True,
                    "valid": acquisition["acquisition_complete"],
                },
            }
        )
        if source_ambiguity and not qualifying:
            arm["verdict"] = "UNRESOLVED"
            arm["verdict_reason"] = (
                "A candidate record failed the frozen SourceInfo == 0 realization."
            )
        elif qualifying:
            arm["verdict"] = "QUALIFYING RECORD"
            arm["verdict_reason"] = (
                "A qualifying operation record appeared in the controlled-stasis arm and is not reinterpreted away."
            )
        else:
            arm["verdict"] = "NO QUALIFYING RECORD"
            arm["verdict_reason"] = (
                "No qualifying operation witness was observed; controlled stasis comes from fixture control, not absence."
            )
    except QualificationError as exc:
        arm["verdict"] = "INVALID" if exc.category == "invalid" else "UNRESOLVED"
        arm["error"] = exc.as_dict()
    return arm


def structure_operation_arm(raw: dict[str, Any]) -> dict[str, Any]:
    arm: dict[str, Any] = {
        "arm_identity": "O",
        "controlled_history": {
            "classification_basis": "controlled fixture declaration",
            "declared_history": "A ------ overwrite A ------ A",
            "write_issued": True,
            "write_calls": raw.get("controlled_write", {}).get("write_calls"),
            "same_length": raw.get("same_length"),
            "synchronous": raw.get("controlled_write", {}).get("synchronous"),
            "flushed": raw.get("controlled_write", {}).get("flush_completed"),
            "writer_closed_before_E": raw.get("controlled_write", {}).get(
                "handle_closed_before_E"
            ),
        },
        "verdict": raw["verdict"],
        "verdict_reason": raw.get("verdict_reason"),
    }
    if raw["verdict"] in ("INVALID", "UNRESOLVED") and "before" not in raw:
        arm["error"] = raw.get("error")
        return arm
    before = raw["before"]
    after = raw["after"]
    acquisition = raw["bounded_acquisition"]
    c0 = raw["baseline_endpoint"]
    c1 = raw["final_endpoint"]
    journal_id = int(before["journal"]["UsnJournalID"]["decimal"])
    arm.update(
        {
            "endpoint_content_observation": {
                "C0": c0,
                "C1": c1,
                "checks": {
                    "C0_is_A": c0["sha256"] == hashlib.sha256(CONTENT_A).hexdigest(),
                    "C1_is_A": c1["sha256"] == hashlib.sha256(CONTENT_A).hexdigest(),
                    "C0_equals_C1": c0["sha256"] == c1["sha256"],
                },
                "endpoint_equivalent": c0["sha256"] == c1["sha256"],
            },
            "file_identity": {
                "C0": c0["identity"],
                "writer": raw["controlled_write"]["identity"],
                "C1": c1["identity"],
                "checks": raw["identity_and_endpoint_checks"],
                "continuous": raw["identity_and_endpoint_checks"][
                    "baseline_writer_final_fileID64_equal"
                ],
            },
            "volume_and_journal": {
                "before_volume": before["volume_identity"],
                "after_volume": after["volume_identity"],
                "before_journal": before["journal"],
                "after_journal": after["journal"],
                "S": before["S"],
                "E": after["E"],
                "continuity": raw["journal_continuity"],
            },
            "usn_operation_observation": {
                "read_parameters": frozen_read_parameters(journal_id),
                "acquisition": acquisition,
                "continuation_cursors": [
                    call["returned_continuation_usn"] for call in acquisition["calls"]
                ],
                "candidate_records": raw["selected_file_records"],
                "qualifying_records": raw["qualifying_records"],
                "qualifying_record_observed": bool(raw["qualifying_records"]),
            },
            "lifecycle": raw["lifecycle_association"],
        }
    )
    if "error" in raw:
        arm["error"] = raw["error"]
    return arm


def adjudicate_pressure(stasis: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    for arm in (stasis, operation):
        if arm["verdict"] == "INVALID":
            return {
                "endpoint_collision": False,
                "usn_differential": False,
                "distinction_recovery_verdict": "INVALID",
            }
        if arm["verdict"] == "UNRESOLVED":
            return {
                "endpoint_collision": False,
                "usn_differential": False,
                "distinction_recovery_verdict": "UNRESOLVED",
            }
    s_endpoint = stasis["endpoint_content_observation"]
    o_endpoint = operation["endpoint_content_observation"]
    endpoint_collision = (
        s_endpoint["endpoint_equivalent"]
        and o_endpoint["endpoint_equivalent"]
        and s_endpoint["C0"]["sha256"]
        == s_endpoint["C1"]["sha256"]
        == o_endpoint["C0"]["sha256"]
        == o_endpoint["C1"]["sha256"]
    )
    s_positive = stasis["usn_operation_observation"]["qualifying_record_observed"]
    o_positive = operation["usn_operation_observation"]["qualifying_record_observed"]
    usn_differential = not s_positive and o_positive
    if not endpoint_collision:
        verdict = "INVALID"
    elif usn_differential:
        verdict = "DISTINCTION RECOVERED"
    elif s_positive and not o_positive:
        verdict = "UNRESOLVED"
    else:
        verdict = "DISTINCTION NOT RECOVERED"
    return {
        "endpoint_collision": endpoint_collision,
        "usn_differential": usn_differential,
        "distinction_recovery_verdict": verdict,
    }


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def run(output: Path) -> tuple[dict[str, Any], int]:
    trace: dict[str, Any] = {
        "experiment": EXPERIMENT_ID,
        "consumer_question": (
            "Between equivalent endpoint captures, did the selected file undergo at least "
            "one qualifying NTFS unnamed-data overwrite-category operation?"
        ),
        "Q_CONTENT_not_pressured": True,
        "not_a_general_observer": True,
        "repository": {
            "HEAD": _git("rev-parse", "HEAD"),
            "origin_main": _git("rev-parse", "origin/main"),
        },
    }
    exit_code = 1
    fixture_dir: Path | None = None
    volume_handle: Any = None
    win32: Win32 | None = None
    try:
        win32 = Win32()
        root = _volume_root(Path.cwd())
        volume = win32.volume_identity(root)
        preflight: dict[str, Any] = {
            "platform": sys.platform,
            "elevated": bool(win32.shell32.IsUserAnAdmin()),
            "volume_identity": volume,
            "journal_was_not_created_enabled_resized_or_deleted": True,
        }
        trace["preflight"] = preflight
        if volume["filesystem"].upper() != "NTFS":
            raise QualificationError("invalid", "filesystem pre-flight", volume["filesystem"])
        if not preflight["elevated"]:
            raise QualificationError("invalid", "privilege pre-flight", "process is not elevated")
        volume_handle = win32.open_handle(
            _volume_device(root),
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            "open selected NTFS volume",
        )
        initial_journal = query_journal(win32, volume_handle)
        journal_id = int(initial_journal["UsnJournalID"]["decimal"])
        probe = probe_read_mode(
            win32,
            volume_handle,
            start_usn=_journal_int(initial_journal, "NextUsn"),
            journal_id=journal_id,
        )
        preflight.update(
            {
                "journal_query": initial_journal,
                "qualified_read_mode_probe": probe,
                "qualified_to_mutate_fixture": True,
            }
        )

        fixture_dir = Path(tempfile.mkdtemp(prefix="dme_q_operation_", dir=Path.cwd()))
        fixture_path = fixture_dir / "selected_file.bin"
        trace["fixture"] = {
            "directory": str(fixture_dir),
            "same_selected_volume_as_repository": _volume_root(fixture_dir) == root,
            "same_selected_file_object_between_arms_required": True,
            "content_A_length": len(CONTENT_A),
            "content_A_sha256": hashlib.sha256(CONTENT_A).hexdigest(),
        }
        stasis = run_stasis_arm(win32, volume_handle, root, fixture_path)
        operation = structure_operation_arm(
            run_arm(win32, volume_handle, root, fixture_path, "O", CONTENT_A)
        )
        trace["arms"] = {"S": stasis, "O": operation}

        if (
            stasis["verdict"] not in ("INVALID", "UNRESOLVED")
            and operation["verdict"] not in ("INVALID", "UNRESOLVED")
        ):
            s_id = stasis["file_identity"]["C0"]["fileID64"]
            o_id = operation["file_identity"]["C0"]["fileID64"]
            trace["fixture"]["cross_arm_identity"] = {
                "S_fileID64": s_id,
                "O_fileID64": o_id,
                "same_complete_fileID64": s_id == o_id,
            }
            if s_id != o_id:
                operation["verdict"] = "INVALID"
                operation["verdict_reason"] = "Selected file object changed between arms."
        trace["cross_arm"] = adjudicate_pressure(stasis, operation)
        exit_code = (
            0
            if trace["cross_arm"]["distinction_recovery_verdict"]
            == "DISTINCTION RECOVERED"
            else 2
        )
    except QualificationError as exc:
        trace.setdefault("preflight", {})["qualified_to_mutate_fixture"] = False
        trace["execution_error"] = exc.as_dict()
        trace["cross_arm"] = {
            "endpoint_collision": False,
            "usn_differential": False,
            "distinction_recovery_verdict": (
                "INVALID" if exc.category == "invalid" else "UNRESOLVED"
            ),
        }
    finally:
        if volume_handle is not None and win32 is not None:
            try:
                win32.close_handle(volume_handle, "close selected NTFS volume")
            except QualificationError as exc:
                trace["volume_close_error"] = exc.as_dict()
                trace["cross_arm"]["distinction_recovery_verdict"] = "INVALID"
                exit_code = 2
        cleanup: dict[str, Any] = {"attempted": fixture_dir is not None}
        if fixture_dir is not None:
            try:
                shutil.rmtree(fixture_dir)
                cleanup["completed"] = True
            except OSError as exc:
                cleanup.update({"completed": False, "error": str(exc)})
        trace["fixture_cleanup"] = cleanup
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    return trace, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_TRACE)
    args = parser.parse_args()
    trace, exit_code = run(args.output)
    print(json.dumps({"trace": str(args.output), "result": trace["cross_arm"]}, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
