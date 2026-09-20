#!/usr/bin/env python3
"""WAKE_SOURCE_001 — one exact manual bell to one exact wake opportunity."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from tools.bounded_reentry_v0 import ReentryStore, build_wake_opportunity
from tools.development_campaign_v0 import object_sha256
from tools.preparation_assignment_v0 import AssignmentStore


class WakeSourceError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"


def build_manual_bell(
    *,
    assignment: dict[str, Any],
    bell_id: str,
    bell_basis_refs: list[str],
) -> dict[str, Any]:
    if not bell_id:
        raise WakeSourceError("bell_id required")
    if not bell_basis_refs or len(bell_basis_refs) != len(set(bell_basis_refs)):
        raise WakeSourceError("bell basis refs must be non-empty and unique")
    if assignment.get("assignment_kind") != "ASSIGNED":
        raise WakeSourceError("manual bell requires ASSIGNED event")
    return {
        "schema": "manual_bell_v0",
        "bell_id": bell_id,
        "assignment_id": assignment["assignment_id"],
        "assignment_sha256": object_sha256(assignment),
        "campaign_id": assignment["campaign_id"],
        "campaign_sha256": assignment["campaign_sha256"],
        "request_id": assignment["request_id"],
        "request_sha256": assignment["request_sha256"],
        "selection_ref": assignment["selection_ref"],
        "selection_sha256": assignment["selection_sha256"],
        "seat_id": assignment["seat_id"],
        "preparation_kind": assignment["preparation_kind"],
        "bell_basis_refs": list(bell_basis_refs),
        "bell_basis_sha256": object_sha256(bell_basis_refs),
        "wake_source_kind": "MANUAL_BELL",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "standing_effect": "NONE",
        "priority_effect": "NONE",
        "scheduler_effect": "NONE",
    }


class WakeSourceStore:
    def __init__(
        self,
        *,
        assignment_store: AssignmentStore,
        reentry_store: ReentryStore,
        db_path: str | Path,
    ):
        self.assignment_store = assignment_store
        self.reentry_store = reentry_store
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS manual_bells(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    bell_id TEXT NOT NULL UNIQUE,
                    bell_sha256 TEXT NOT NULL,
                    assignment_id TEXT NOT NULL,
                    assignment_sha256 TEXT NOT NULL,
                    bell_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS bell_emissions(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    bell_id TEXT NOT NULL UNIQUE,
                    bell_sha256 TEXT NOT NULL,
                    opportunity_id TEXT NOT NULL UNIQUE,
                    opportunity_sha256 TEXT NOT NULL,
                    emission_json TEXT NOT NULL
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def bell(self, bell_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT bell_json FROM manual_bells WHERE bell_id=?",
                (bell_id,),
            ).fetchone()
        finally:
            conn.close()
        return json.loads(row["bell_json"]) if row is not None else None

    def emission(self, bell_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT emission_json FROM bell_emissions WHERE bell_id=?",
                (bell_id,),
            ).fetchone()
        finally:
            conn.close()
        return json.loads(row["emission_json"]) if row is not None else None

    def _validate_bell(self, bell: dict[str, Any]) -> dict[str, Any]:
        required = {
            "schema",
            "bell_id",
            "assignment_id",
            "assignment_sha256",
            "campaign_id",
            "campaign_sha256",
            "request_id",
            "request_sha256",
            "selection_ref",
            "selection_sha256",
            "seat_id",
            "preparation_kind",
            "bell_basis_refs",
            "bell_basis_sha256",
            "wake_source_kind",
            "authority_effect",
            "execution_effect",
            "standing_effect",
            "priority_effect",
            "scheduler_effect",
        }
        if set(bell) != required or bell["schema"] != "manual_bell_v0":
            raise WakeSourceError("manual bell fields are not exact")
        if bell["wake_source_kind"] != "MANUAL_BELL":
            raise WakeSourceError("unsupported wake source kind")
        for field in (
            "authority_effect",
            "execution_effect",
            "standing_effect",
            "priority_effect",
            "scheduler_effect",
        ):
            if bell[field] != "NONE":
                raise WakeSourceError(f"{field} must remain NONE")
        if bell["bell_basis_sha256"] != object_sha256(bell["bell_basis_refs"]):
            raise WakeSourceError("bell basis identity mismatch")

        assignment = self.assignment_store._load_assignment(bell["assignment_id"])
        if bell["assignment_sha256"] != object_sha256(assignment):
            raise WakeSourceError("assignment identity mismatch")
        for field in (
            "campaign_id",
            "campaign_sha256",
            "request_id",
            "request_sha256",
            "selection_ref",
            "selection_sha256",
            "seat_id",
            "preparation_kind",
        ):
            if bell[field] != assignment[field]:
                raise WakeSourceError(f"bell {field} does not bind assignment")
        return assignment

    def emit(
        self,
        bell: dict[str, Any],
        *,
        current_basis_refs: list[str],
        opportunity_id: str,
        opportunity_basis: str,
        campaign: dict[str, Any],
        request: dict[str, Any],
        selection: dict[str, Any],
        max_consumed_events: int = 8,
    ) -> dict[str, Any]:
        assignment = self._validate_bell(bell)
        bell_sha = object_sha256(bell)

        existing_bell = self.bell(bell["bell_id"])
        existing_emission = self.emission(bell["bell_id"])
        if existing_bell is not None:
            if object_sha256(existing_bell) != bell_sha:
                raise WakeSourceError("bell_id reused with different bytes")
            if existing_emission is not None:
                return {
                    **existing_emission,
                    "idempotent_replay": True,
                }

        if bell["bell_id"] == opportunity_id:
            raise WakeSourceError(
                "manual bell identity must remain distinct from wake opportunity identity"
            )
        if bell["bell_basis_refs"] != current_basis_refs:
            raise WakeSourceError(
                "bell basis must equal basis used for current assignment projection"
            )
        if f"git:{opportunity_basis}" not in current_basis_refs:
            raise WakeSourceError(
                "wake opportunity Git basis must be present in exact bell basis"
            )

        projection = self.assignment_store.projection(
            bell["campaign_id"],
            current_basis_refs=current_basis_refs,
        )
        current = next(
            (
                row
                for row in projection["assignment_projection"]
                if row["assignment_id"] == bell["assignment_id"]
                and row["assignment_sha256"] == bell["assignment_sha256"]
            ),
            None,
        )
        if (
            current is None
            or current["assignment_state"] != "OUTSTANDING"
            or current["wake_eligible"] is not True
        ):
            state = (
                current["assignment_state"]
                if current is not None
                else "MISSING"
            )
            raise WakeSourceError(
                f"assignment is not bell-eligible: {state}"
            )

        if assignment["preparation_kind"] != "RESOLVE_REFS":
            raise WakeSourceError(
                "v0 wake source only rings units currently implemented by bounded reentry"
            )

        if campaign["campaign_id"] != bell["campaign_id"]:
            raise WakeSourceError("campaign does not match bell")
        if object_sha256(campaign) != bell["campaign_sha256"]:
            raise WakeSourceError("campaign identity mismatch")
        if request["request_id"] != bell["request_id"]:
            raise WakeSourceError("request does not match bell")
        if object_sha256(request) != bell["request_sha256"]:
            raise WakeSourceError("request identity mismatch")
        if selection["selection_id"] != bell["selection_ref"]:
            raise WakeSourceError("selection does not match bell")
        if object_sha256(selection) != bell["selection_sha256"]:
            raise WakeSourceError("selection identity mismatch")

        if existing_bell is None:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    INSERT INTO manual_bells(
                        bell_id,bell_sha256,assignment_id,
                        assignment_sha256,bell_json
                    ) VALUES(?,?,?,?,?)
                    """,
                    (
                        bell["bell_id"],
                        bell_sha,
                        bell["assignment_id"],
                        bell["assignment_sha256"],
                        _canonical(bell),
                    ),
                )
                conn.commit()
            finally:
                conn.close()

        opportunity = build_wake_opportunity(
            campaign=campaign,
            seat_id=bell["seat_id"],
            opportunity_id=opportunity_id,
            opportunity_basis=opportunity_basis,
            max_consumed_events=max_consumed_events,
            request=request,
            selection=selection,
            preparation_kind=bell["preparation_kind"],
            assignment=assignment,
            manual_bell=bell,
            wake_source_kind="MANUAL_BELL",
        )
        post = self.reentry_store.post_opportunity(opportunity)
        emission = {
            "schema": "manual_bell_emission_v0",
            "bell_id": bell["bell_id"],
            "bell_sha256": bell_sha,
            "opportunity_id": opportunity["opportunity_id"],
            "opportunity_sha256": object_sha256(opportunity),
            "assignment_id": bell["assignment_id"],
            "assignment_sha256": bell["assignment_sha256"],
            "wake_source_effect": "ONE_WAKE_OPPORTUNITY",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "standing_effect": "NONE",
            "priority_effect": "NONE",
            "scheduler_effect": "NONE",
        }

        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT emission_json FROM bell_emissions WHERE bell_id=?",
                (bell["bell_id"],),
            ).fetchone()
            if row is None:
                conn.execute(
                    """
                    INSERT INTO bell_emissions(
                        bell_id,bell_sha256,opportunity_id,
                        opportunity_sha256,emission_json
                    ) VALUES(?,?,?,?,?)
                    """,
                    (
                        bell["bell_id"],
                        bell_sha,
                        opportunity["opportunity_id"],
                        object_sha256(opportunity),
                        _canonical(emission),
                    ),
                )
                conn.commit()
            else:
                retained = json.loads(row["emission_json"])
                if retained != emission:
                    raise WakeSourceError(
                        "bell already names a different opportunity relation"
                    )
        finally:
            conn.close()

        return {
            **emission,
            "idempotent_replay": bool(post["idempotent_replay"]),
        }
