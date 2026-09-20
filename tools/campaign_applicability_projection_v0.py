#!/usr/bin/env python3
"""CAMPAIGN_APPLICABILITY_PROJECTION_001 — consume revalidation warrants operationally."""

from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3
from typing import Any

from tools.campaign_basis_revalidation_v0 import (
    CURRENTLY_APPLICABLE,
    INSUFFICIENT_BASIS,
    NOT_APPLICABLE,
    CampaignBasisRevalidationError,
    CampaignBasisRevalidationStore,
    validate_revalidation,
)
from tools.development_campaign_v0 import CampaignStore, object_sha256


SCHEMA = "CAMPAIGN_APPLICABILITY_PROJECTION_v0"

CURRENT_BY_HISTORICAL_BASIS = "CURRENT_BY_HISTORICAL_BASIS"
CURRENT_BY_REVALIDATION = "CURRENT_BY_REVALIDATION"
NOT_CURRENT = "NOT_CURRENT"

REVALIDATION_NONE = "NONE"
REVALIDATION_STALE = "STALE_REVALIDATION"
REVALIDATION_UNAVAILABLE = "UNAVAILABLE"


class CampaignApplicabilityProjectionError(RuntimeError):
    pass


def _validate_basis_refs(value: Any) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(ref, str) and ref for ref in value)
        or len(value) != len(set(value))
    ):
        raise CampaignApplicabilityProjectionError(
            "current basis refs must be a non-empty unique string list"
        )
    return list(value)


@dataclass(frozen=True)
class WarrantIdentity:
    revalidation_id: str
    revalidation_sha256: str

    def as_dict(self) -> dict[str, str]:
        return {
            "revalidation_id": self.revalidation_id,
            "revalidation_sha256": self.revalidation_sha256,
        }


class CampaignApplicabilityProjector:
    """Read-only composition of historical basis truth and revalidation evidence."""

    def __init__(
        self,
        campaign_store: CampaignStore,
        revalidation_store: CampaignBasisRevalidationStore | None,
    ):
        self.campaign_store = campaign_store
        self.revalidation_store = revalidation_store

    def project(
        self,
        campaign_id: str,
        *,
        current_basis_refs: list[str],
    ) -> dict[str, Any]:
        refs = _validate_basis_refs(current_basis_refs)
        campaign = self.campaign_store.get_campaign(campaign_id)
        campaign_sha = object_sha256(campaign)
        basis_sha = object_sha256(refs)
        historical = self.campaign_store.snapshot(
            campaign_id,
            current_basis_refs=refs,
        )

        result: dict[str, Any] = {
            "schema": SCHEMA,
            "campaign_id": campaign_id,
            "campaign_sha256": campaign_sha,
            "queried_current_basis_refs": refs,
            "queried_current_basis_sha256": basis_sha,
            "historical_basis_status": historical["basis_status"],
            "revalidation_status": REVALIDATION_NONE,
            "effective_applicability": NOT_CURRENT,
            "revalidation_id": None,
            "revalidation_sha256": None,
            "matching_warrants": [],
            "diagnostics": [],
            "warrant_selection_rule": "NONE",
            "authority_effect": "NONE",
            "adoption_effect": "NONE",
            "selection_effect": "NONE",
            "assignment_effect": "NONE",
            "priority_effect": "NONE",
            "standing_effect": "NONE",
            "scheduler_effect": "NONE",
            "wake_effect": "NONE",
            "execution_effect": "NONE",
        }

        if historical["basis_status"] == "CURRENT":
            result["effective_applicability"] = CURRENT_BY_HISTORICAL_BASIS
            return result

        if self.revalidation_store is None:
            result["revalidation_status"] = REVALIDATION_UNAVAILABLE
            result["diagnostics"].append("REVALIDATION_SOURCE_UNAVAILABLE")
            return result

        if not self.revalidation_store.db_path.exists():
            result["revalidation_status"] = REVALIDATION_UNAVAILABLE
            result["diagnostics"].append("REVALIDATION_SOURCE_UNAVAILABLE:MISSING_DB")
            return result

        try:
            conn = sqlite3.connect(self.revalidation_store.db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT
                    seq,
                    revalidation_id,
                    result_sha256,
                    campaign_id,
                    campaign_sha256,
                    candidate_current_basis_sha256,
                    disposition,
                    result_json
                FROM campaign_basis_revalidations
                WHERE campaign_id=?
                ORDER BY seq
                """,
                (campaign_id,),
            ).fetchall()
        except Exception as exc:
            result["revalidation_status"] = REVALIDATION_UNAVAILABLE
            result["diagnostics"].append(
                f"REVALIDATION_SOURCE_UNAVAILABLE:{type(exc).__name__}"
            )
            return result
        finally:
            try:
                conn.close()
            except Exception:
                pass

        valid_rows: list[dict[str, Any]] = []
        invalid_rows: list[str] = []
        for row in rows:
            try:
                durable = json.loads(row["result_json"])
            except Exception:
                invalid_rows.append(str(row["revalidation_id"]))
                continue
            durable_sha = object_sha256(durable)
            columns_match = (
                row["result_sha256"] == durable_sha
                and row["revalidation_id"] == durable.get("revalidation_id")
                and row["campaign_id"] == durable.get("campaign_id")
                and row["campaign_sha256"] == durable.get("campaign_sha256")
                and row["candidate_current_basis_sha256"]
                    == durable.get("candidate_current_basis_sha256")
                and row["disposition"] == durable.get("disposition")
            )
            if not columns_match:
                invalid_rows.append(str(row["revalidation_id"]))
                continue
            try:
                validate_revalidation(durable, campaign)
            except CampaignBasisRevalidationError:
                invalid_rows.append(str(durable.get("revalidation_id", "UNKNOWN")))
                continue
            valid_rows.append(durable)

        if invalid_rows:
            result["diagnostics"].append(
                "INVALID_REVALIDATION_IDENTITY:" + ",".join(sorted(set(invalid_rows)))
            )

        exact_basis = [
            row
            for row in valid_rows
            if row["candidate_current_basis_sha256"] == basis_sha
            and row["candidate_current_basis_refs"] == refs
        ]

        positive = [
            row
            for row in exact_basis
            if row["disposition"] == CURRENTLY_APPLICABLE
        ]
        if positive:
            warrants = sorted(
                (
                    WarrantIdentity(
                        row["revalidation_id"],
                        object_sha256(row),
                    )
                    for row in positive
                ),
                key=lambda item: (item.revalidation_id, item.revalidation_sha256),
            )
            result["revalidation_status"] = CURRENTLY_APPLICABLE
            result["effective_applicability"] = CURRENT_BY_REVALIDATION
            result["matching_warrants"] = [w.as_dict() for w in warrants]
            result["revalidation_id"] = warrants[0].revalidation_id
            result["revalidation_sha256"] = warrants[0].revalidation_sha256
            result["warrant_selection_rule"] = (
                "LEXICOGRAPHIC_DURABLE_IDENTITY_NON_SEMANTIC"
            )
            return result

        dispositions = {row["disposition"] for row in exact_basis}
        if NOT_APPLICABLE in dispositions:
            result["revalidation_status"] = NOT_APPLICABLE
            return result
        if INSUFFICIENT_BASIS in dispositions:
            result["revalidation_status"] = INSUFFICIENT_BASIS
            return result

        stale_positive = any(
            row["disposition"] == CURRENTLY_APPLICABLE
            and row["candidate_current_basis_sha256"] != basis_sha
            for row in valid_rows
        )
        if stale_positive:
            result["revalidation_status"] = REVALIDATION_STALE

        return result
