"""Explicit foreground coordination of the earned repository observation stack."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from src.capture import make_repo_snapshot, observe_git_state
from src.ingest import COMPARATOR_V0, append_admission, append_observation
from src.ledger import JsonlLedger, verify_continuity
from src.reconstruction import (
    derive_admitted_projection,
    derive_non_admitted_decision_states,
    reconstruct_admission_relationships,
)
from src.runtime.repo_provenance_pressure import make_snapshot_ingest_envelope
from src.runtime.repo_transition_pressure import make_git_ingest_envelope


class ForegroundRepositoryObservationCoordinator:
    """Compose one explicitly requested filesystem/Git observation round."""

    def __init__(self, root: Path | str, ledger_path: Path | str) -> None:
        self.root = Path(root)
        self.ledger_path = Path(ledger_path)
        self._closed = False

    @classmethod
    def open(
        cls, root: Path | str, ledger_path: Path | str
    ) -> ForegroundRepositoryObservationCoordinator:
        """Create a fresh coordinator over an existing or new ledger path."""
        return cls(root, ledger_path)

    def capture_round(self) -> dict[str, Any]:
        """Capture both earned repository sources and return derived current state."""
        self._require_open()
        snapshot = make_repo_snapshot(self.root)
        git_state = observe_git_state(self.root)
        filesystem_candidate = make_snapshot_ingest_envelope(snapshot)
        git_candidate = make_git_ingest_envelope(git_state)
        ledger = JsonlLedger(self.ledger_path)

        filesystem_observation = append_observation(
            ledger,
            filesystem_candidate,
            source=filesystem_candidate["source"],
            provenance=_capture_provenance(filesystem_candidate, snapshot),
        )
        git_observation = append_observation(
            ledger,
            git_candidate,
            source=git_candidate["source"],
            provenance=_capture_provenance(git_candidate, git_state),
        )
        filesystem_admission = append_admission(
            ledger, filesystem_observation, comparator_version=COMPARATOR_V0
        )
        git_admission = append_admission(
            ledger, git_observation, comparator_version=COMPARATOR_V0
        )
        return self._result(
            [
                filesystem_observation,
                git_observation,
                filesystem_admission,
                git_admission,
            ],
            {"filesystem": snapshot, "git": git_state},
        )

    def current_result(self) -> dict[str, Any]:
        """Rebuild the current derived state without appending or capturing."""
        self._require_open()
        return self._result([], None)

    def close(self) -> None:
        """End this process-local coordinator lifetime without writing metadata."""
        self._closed = True

    def _result(
        self,
        new_records: list[dict[str, Any]],
        captured_observations: dict[str, Any] | None,
    ) -> dict[str, Any]:
        ledger = JsonlLedger(self.ledger_path)
        records_a = ledger.replay()
        records_b = JsonlLedger(self.ledger_path).replay()
        integrity = ledger.verify()
        continuity = verify_continuity(records_a, require_start_at_one=True)
        reconstruction_a = reconstruct_admission_relationships(records_a)
        reconstruction_b = reconstruct_admission_relationships(deepcopy(records_b))
        projection_a = derive_admitted_projection(reconstruction_a)
        projection_b = derive_admitted_projection(reconstruction_b)
        companion_a = derive_non_admitted_decision_states(
            reconstruction_a, projection_a
        )
        companion_b = derive_non_admitted_decision_states(
            reconstruction_b, projection_b
        )
        observation_sources = [
            item["source"] for item in reconstruction_a["observations"]
        ]
        return {
            "authoritative": False,
            "capture_mode": "explicit_foreground_invocation",
            "round_number": None,
            "new_records": [_record_summary(record) for record in new_records],
            "captured_observations": deepcopy(captured_observations),
            "ledger": {
                "record_count": len(records_a),
                "integrity_ok": integrity.ok,
                "integrity_failures": list(integrity.failures),
                "continuity_ok": continuity.ok,
                "continuity_failures": list(continuity.failures),
                "canonical_replay_reproducible": records_a == records_b,
                "commit_indices": [record["commit_index"] for record in records_a],
            },
            "derived": {
                "reconstruction_reproducible": reconstruction_a
                == reconstruction_b,
                "observation_count": len(reconstruction_a["observations"]),
                "admission_relation_count": sum(
                    len(item["admissions"])
                    for item in reconstruction_a["observations"]
                ),
                "orphan_admission_count": len(reconstruction_a["orphan_admissions"]),
                "projection_reproducible": projection_a == projection_b,
                "projection": projection_a,
                "companion_reproducible": companion_a == companion_b,
                "companion": companion_a,
                "source_provenance_separate": (
                    set(observation_sources)
                    == {"repository_filesystem_snapshot", "repository_git_state"}
                    if observation_sources
                    else True
                ),
            },
        }

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("foreground coordinator is closed")


def _capture_provenance(
    candidate: dict[str, Any], raw: dict[str, Any]
) -> dict[str, Any]:
    return {
        "capture_mode": "explicit_foreground_invocation",
        "source_envelope_identity": candidate["envelope_identity"],
        "observer": raw["observer"],
        "observer_version": raw["observer_version"],
    }


def _record_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "record_type": record["envelope"]["record_type"],
        "source": record["envelope"].get("source"),
        "subject_record_id": record["envelope"].get("subject_record_id"),
        "decision": record["envelope"].get("decision"),
        "digest": record["integrity"]["digest"],
    }
