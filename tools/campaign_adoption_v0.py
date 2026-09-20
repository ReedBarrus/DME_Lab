#!/usr/bin/env python3
"""CAMPAIGN_ADOPTION_001 — explicit human developmental commitment.

This membrane records an explicit REED adoption/release declaration for one
exact immutable campaign. It does not establish applicability; it consumes the
read-only CAMPAIGN_APPLICABILITY_PROJECTION_001 result when admitting a new
ADOPTED event and when deriving current live state.

ADOPTION != APPLICABILITY != SELECTION != AUTHORITY != EXECUTION.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from tools.campaign_applicability_projection_v0 import (
    CURRENT_BY_HISTORICAL_BASIS,
    CURRENT_BY_REVALIDATION,
    NOT_CURRENT,
    CampaignApplicabilityProjector,
)
from tools.development_campaign_v0 import object_sha256, validate_campaign


SCHEMA = "CAMPAIGN_ADOPTION_v0"
ADOPTED = "ADOPTED"
ADOPTION_RELEASED = "ADOPTION_RELEASED"
KINDS = {ADOPTED, ADOPTION_RELEASED}

CURRENT_ADOPTED = "ADOPTED"
CURRENT_NOT_ADOPTED = "NOT_ADOPTED"

LIVE = "LIVE"
NOT_LIVE = "NOT_LIVE"
BLOCKED_NOT_CURRENT = "BLOCKED_NOT_CURRENT"

DECLARES = "DECLARES_DEVELOPMENTAL_COMMITMENT"
RELEASES = "RELEASES_DEVELOPMENTAL_COMMITMENT"

_STORAGE_METADATA = {"_seq", "_rowid", "_inserted_at"}

_FORBIDDEN_INPUT_FIELDS = {
    "priority",
    "selected",
    "selection",
    "assignment",
    "authority_granted",
    "standing",
    "wake_now",
    "execute",
    "effective_applicability",
    "historical_basis_status",
    "revalidation_status",
    "revalidation_id",
    "revalidation_sha256",
    "current_basis_refs",
    "current_basis_sha256",
}


class CampaignAdoptionError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )


def _validate_nonempty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CampaignAdoptionError(f"{name} must be a non-empty string")
    return value


def _validate_effects(event: dict[str, Any]) -> None:
    expected = {
        "selection_effect": "NONE",
        "assignment_effect": "NONE",
        "priority_effect": "NONE",
        "standing_effect": "NONE",
        "authority_effect": "NONE",
        "scheduler_effect": "NONE",
        "wake_effect": "NONE",
        "execution_effect": "NONE",
    }
    for key, value in expected.items():
        if event.get(key) != value:
            raise CampaignAdoptionError(f"{key} must be NONE")


def validate_event(event: dict[str, Any], campaign: dict[str, Any]) -> None:
    validate_campaign(campaign)
    if not isinstance(event, dict):
        raise CampaignAdoptionError("adoption event must be an object")

    forbidden = sorted(set(event).intersection(_FORBIDDEN_INPUT_FIELDS))
    if forbidden:
        raise CampaignAdoptionError(
            "adoption event attempts to smuggle neighboring state: "
            + ",".join(forbidden)
        )

    required = {
        "schema",
        "adoption_id",
        "campaign_id",
        "campaign_sha256",
        "actor_id",
        "adoption_kind",
        "target_adoption_id",
        "target_adoption_sha256",
        "gesture_ref",
        "reason",
        "adoption_effect",
        "selection_effect",
        "assignment_effect",
        "priority_effect",
        "standing_effect",
        "authority_effect",
        "scheduler_effect",
        "wake_effect",
        "execution_effect",
    }
    if set(event) != required:
        missing = sorted(required - set(event))
        extra = sorted(set(event) - required)
        raise CampaignAdoptionError(
            f"adoption event keys mismatch missing={missing} extra={extra}"
        )

    if event["schema"] != SCHEMA:
        raise CampaignAdoptionError("wrong adoption schema")
    _validate_nonempty(event["adoption_id"], "adoption_id")
    if event["campaign_id"] != campaign["campaign_id"]:
        raise CampaignAdoptionError("campaign_id mismatch")
    if event["campaign_sha256"] != object_sha256(campaign):
        raise CampaignAdoptionError("campaign identity mismatch")
    if event["actor_id"] != "REED":
        raise CampaignAdoptionError("v0 adopter must be REED")
    _validate_nonempty(event["gesture_ref"], "gesture_ref")
    _validate_nonempty(event["reason"], "reason")

    kind = event["adoption_kind"]
    if kind not in KINDS:
        raise CampaignAdoptionError("invalid adoption_kind")

    if kind == ADOPTED:
        if event["target_adoption_id"] is not None:
            raise CampaignAdoptionError("ADOPTED must not target prior adoption")
        if event["target_adoption_sha256"] is not None:
            raise CampaignAdoptionError("ADOPTED must not target prior adoption")
        if event["adoption_effect"] != DECLARES:
            raise CampaignAdoptionError("wrong ADOPTED adoption_effect")
    else:
        _validate_nonempty(event["target_adoption_id"], "target_adoption_id")
        _validate_nonempty(event["target_adoption_sha256"], "target_adoption_sha256")
        if event["adoption_effect"] != RELEASES:
            raise CampaignAdoptionError("wrong ADOPTION_RELEASED adoption_effect")

    _validate_effects(event)


def build_event(
    *,
    campaign: dict[str, Any],
    adoption_id: str,
    actor_id: str,
    adoption_kind: str,
    gesture_ref: str,
    reason: str,
    target_adoption_id: str | None = None,
    target_adoption_sha256: str | None = None,
) -> dict[str, Any]:
    event = {
        "schema": SCHEMA,
        "adoption_id": adoption_id,
        "campaign_id": campaign["campaign_id"],
        "campaign_sha256": object_sha256(campaign),
        "actor_id": actor_id,
        "adoption_kind": adoption_kind,
        "target_adoption_id": target_adoption_id,
        "target_adoption_sha256": target_adoption_sha256,
        "gesture_ref": gesture_ref,
        "reason": reason,
        "adoption_effect": DECLARES if adoption_kind == ADOPTED else RELEASES,
        "selection_effect": "NONE",
        "assignment_effect": "NONE",
        "priority_effect": "NONE",
        "standing_effect": "NONE",
        "authority_effect": "NONE",
        "scheduler_effect": "NONE",
        "wake_effect": "NONE",
        "execution_effect": "NONE",
    }
    validate_event(event, campaign)
    return event


class CampaignAdoptionStore:
    """Append-only adoption/release history with read-only live projection."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS campaign_adoption_events(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    adoption_id TEXT UNIQUE NOT NULL,
                    event_sha256 TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    campaign_sha256 TEXT NOT NULL,
                    adoption_kind TEXT NOT NULL,
                    event_json TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def durable_object(history_row: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(history_row, dict):
            raise CampaignAdoptionError("history row must be an object")
        return {
            key: value
            for key, value in history_row.items()
            if key not in _STORAGE_METADATA
        }

    def history(self, campaign_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT seq,event_json
                FROM campaign_adoption_events
                WHERE campaign_id=?
                ORDER BY seq
                """,
                (campaign_id,),
            ).fetchall()
        finally:
            conn.close()

        result: list[dict[str, Any]] = []
        for row in rows:
            event = json.loads(row["event_json"])
            event["_seq"] = row["seq"]
            result.append(event)
        return result

    def _load_exact(self, adoption_id: str) -> tuple[dict[str, Any], str] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                """
                SELECT event_sha256,event_json
                FROM campaign_adoption_events
                WHERE adoption_id=?
                """,
                (adoption_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        event = json.loads(row["event_json"])
        digest = object_sha256(event)
        if digest != row["event_sha256"]:
            raise CampaignAdoptionError("stored adoption bytes fail identity check")
        return event, digest

    def _released_targets(self, campaign_id: str) -> set[tuple[str, str]]:
        released: set[tuple[str, str]] = set()
        for row in self.history(campaign_id):
            event = self.durable_object(row)
            if event["adoption_kind"] == ADOPTION_RELEASED:
                released.add(
                    (
                        event["target_adoption_id"],
                        event["target_adoption_sha256"],
                    )
                )
        return released

    def append(
        self,
        event: dict[str, Any],
        *,
        campaign: dict[str, Any],
        applicability_projector: CampaignApplicabilityProjector | None = None,
        current_basis_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        validate_event(event, campaign)
        digest = object_sha256(event)
        rendered = _canonical(event)

        existing = self._load_exact(event["adoption_id"])
        if existing is not None:
            _, existing_digest = existing
            if existing_digest != digest:
                raise CampaignAdoptionError(
                    "adoption_id reused with different durable bytes"
                )
            return {
                "adoption_id": event["adoption_id"],
                "event_sha256": digest,
                "idempotent_replay": True,
            }

        if event["adoption_kind"] == ADOPTED:
            if applicability_projector is None or current_basis_refs is None:
                raise CampaignAdoptionError(
                    "new adoption requires current applicability source"
                )
            projection = applicability_projector.project(
                campaign["campaign_id"],
                current_basis_refs=current_basis_refs,
            )
            if projection["campaign_sha256"] != object_sha256(campaign):
                raise CampaignAdoptionError("applicability campaign identity mismatch")
            if projection["effective_applicability"] not in {
                CURRENT_BY_HISTORICAL_BASIS,
                CURRENT_BY_REVALIDATION,
            }:
                raise CampaignAdoptionError(
                    "campaign is not currently applicable for adoption"
                )
        else:
            target = self._load_exact(event["target_adoption_id"])
            if target is None:
                raise CampaignAdoptionError("release target adoption does not exist")
            target_event, target_digest = target
            if target_digest != event["target_adoption_sha256"]:
                raise CampaignAdoptionError("release target adoption identity mismatch")
            if target_event["adoption_kind"] != ADOPTED:
                raise CampaignAdoptionError("release target must be ADOPTED event")
            if target_event["campaign_sha256"] != event["campaign_sha256"]:
                raise CampaignAdoptionError("release target campaign mismatch")
            target_identity = (
                event["target_adoption_id"],
                event["target_adoption_sha256"],
            )
            if target_identity in self._released_targets(event["campaign_id"]):
                raise CampaignAdoptionError("adoption already released")

        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO campaign_adoption_events(
                    adoption_id,event_sha256,campaign_id,campaign_sha256,
                    adoption_kind,event_json
                ) VALUES(?,?,?,?,?,?)
                """,
                (
                    event["adoption_id"],
                    digest,
                    event["campaign_id"],
                    event["campaign_sha256"],
                    event["adoption_kind"],
                    rendered,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return {
            "adoption_id": event["adoption_id"],
            "event_sha256": digest,
            "idempotent_replay": False,
        }

    def current_adoption(self, campaign: dict[str, Any]) -> dict[str, Any]:
        validate_campaign(campaign)
        campaign_sha = object_sha256(campaign)
        events = [
            self.durable_object(row)
            for row in self.history(campaign["campaign_id"])
        ]
        exact = [row for row in events if row["campaign_sha256"] == campaign_sha]

        released = {
            (row["target_adoption_id"], row["target_adoption_sha256"])
            for row in exact
            if row["adoption_kind"] == ADOPTION_RELEASED
        }

        active: list[dict[str, str]] = []
        for row in exact:
            if row["adoption_kind"] != ADOPTED:
                continue
            digest = object_sha256(row)
            if (row["adoption_id"], digest) not in released:
                active.append(
                    {
                        "adoption_id": row["adoption_id"],
                        "adoption_sha256": digest,
                    }
                )

        active.sort(key=lambda item: (item["adoption_id"], item["adoption_sha256"]))
        return {
            "campaign_id": campaign["campaign_id"],
            "campaign_sha256": campaign_sha,
            "current_adoption_state": (
                CURRENT_ADOPTED if active else CURRENT_NOT_ADOPTED
            ),
            "active_adoptions": active,
            "adoption_count": len(active),
            "priority_effect": "NONE",
            "selection_effect": "NONE",
            "assignment_effect": "NONE",
            "standing_effect": "NONE",
            "authority_effect": "NONE",
            "scheduler_effect": "NONE",
            "wake_effect": "NONE",
            "execution_effect": "NONE",
        }

    def live_projection(
        self,
        campaign: dict[str, Any],
        *,
        current_basis_refs: list[str],
        applicability_projector: CampaignApplicabilityProjector,
    ) -> dict[str, Any]:
        adoption = self.current_adoption(campaign)
        applicability = applicability_projector.project(
            campaign["campaign_id"],
            current_basis_refs=current_basis_refs,
        )

        if adoption["current_adoption_state"] != CURRENT_ADOPTED:
            live = NOT_LIVE
        elif applicability["effective_applicability"] in {
            CURRENT_BY_HISTORICAL_BASIS,
            CURRENT_BY_REVALIDATION,
        }:
            live = LIVE
        else:
            live = BLOCKED_NOT_CURRENT

        return {
            "schema": "CAMPAIGN_LIVE_PROJECTION_v0",
            "campaign_id": campaign["campaign_id"],
            "campaign_sha256": object_sha256(campaign),
            "current_adoption_state": adoption["current_adoption_state"],
            "active_adoptions": adoption["active_adoptions"],
            "effective_applicability": applicability["effective_applicability"],
            "historical_basis_status": applicability["historical_basis_status"],
            "revalidation_status": applicability["revalidation_status"],
            "live_developmental_contract": live,
            "priority_effect": "NONE",
            "selection_effect": "NONE",
            "assignment_effect": "NONE",
            "standing_effect": "NONE",
            "authority_effect": "NONE",
            "scheduler_effect": "NONE",
            "wake_effect": "NONE",
            "execution_effect": "NONE",
        }
