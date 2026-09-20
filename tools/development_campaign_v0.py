#!/usr/bin/env python3
"""DEVELOPMENT_CAMPAIGN_001 durable horizon and envelope-request store.

This candidate creates proposal-only campaign packets and candidate execution
envelope requests. It does not create EXECUTION_PACKET_v0, authorize execution,
schedule work, or adjudicate scientific/development standing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any


CAMPAIGN_SCHEMA = "development_campaign_v0"
REQUEST_SCHEMA = "execution_envelope_request_v0"
STANDING_SCHEMA = "campaign_standing_update_v0"

RESOURCE_CLASSES = {"DETERMINISTIC", "LOCAL_CHEAP", "EXTERNAL_STRONG"}
STANDING_VALUES = {"OPEN", "EARNED", "FRACTURED"}


class DevelopmentCampaignError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def object_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _unique_nonempty_strings(values: Any, field: str) -> list[str]:
    if not isinstance(values, list) or not values:
        raise DevelopmentCampaignError(f"{field} must be a non-empty list")
    if not all(isinstance(v, str) and v for v in values):
        raise DevelopmentCampaignError(f"{field} must contain non-empty strings")
    if len(values) != len(set(values)):
        raise DevelopmentCampaignError(f"{field} must be unique")
    return list(values)


def build_campaign(spec: dict[str, Any]) -> dict[str, Any]:
    required = {
        "campaign_id",
        "title",
        "basis_refs",
        "objective",
        "claim_ceiling",
        "target_objects",
        "unresolved_relations",
        "pressure_points",
        "dependency_edges",
        "proposal_allowance",
        "completion_criteria",
        "stop_conditions",
        "explicit_non_authorizations",
    }
    if set(spec) != required:
        raise DevelopmentCampaignError("campaign spec fields are not exact")
    if not isinstance(spec["campaign_id"], str) or not spec["campaign_id"]:
        raise DevelopmentCampaignError("campaign_id must be non-empty")
    if not isinstance(spec["title"], str) or not spec["title"]:
        raise DevelopmentCampaignError("title must be non-empty")
    if not isinstance(spec["objective"], str) or not spec["objective"]:
        raise DevelopmentCampaignError("objective must be non-empty")
    if not isinstance(spec["claim_ceiling"], str) or not spec["claim_ceiling"]:
        raise DevelopmentCampaignError("claim_ceiling must be non-empty")

    basis_refs = _unique_nonempty_strings(spec["basis_refs"], "basis_refs")
    target_objects = _unique_nonempty_strings(spec["target_objects"], "target_objects")
    completion = _unique_nonempty_strings(spec["completion_criteria"], "completion_criteria")
    stops = _unique_nonempty_strings(spec["stop_conditions"], "stop_conditions")
    nonauth = _unique_nonempty_strings(
        spec["explicit_non_authorizations"], "explicit_non_authorizations"
    )

    relations = spec["unresolved_relations"]
    if not isinstance(relations, list) or not relations:
        raise DevelopmentCampaignError("unresolved_relations must be non-empty")
    relation_ids: list[str] = []
    normalized_relations: list[dict[str, str]] = []
    for relation in relations:
        if not isinstance(relation, dict) or set(relation) != {"relation_id", "statement"}:
            raise DevelopmentCampaignError("invalid unresolved relation shape")
        rid = relation["relation_id"]
        statement = relation["statement"]
        if not isinstance(rid, str) or not rid:
            raise DevelopmentCampaignError("relation_id must be non-empty")
        if not isinstance(statement, str) or not statement:
            raise DevelopmentCampaignError("relation statement must be non-empty")
        relation_ids.append(rid)
        normalized_relations.append({"relation_id": rid, "statement": statement})
    if len(relation_ids) != len(set(relation_ids)):
        raise DevelopmentCampaignError("relation_id values must be unique")

    pressure_points = spec["pressure_points"]
    if not isinstance(pressure_points, list):
        raise DevelopmentCampaignError("pressure_points must be a list")
    if not all(isinstance(v, str) and v for v in pressure_points):
        raise DevelopmentCampaignError("pressure_points must contain strings")

    edges = spec["dependency_edges"]
    if not isinstance(edges, list):
        raise DevelopmentCampaignError("dependency_edges must be a list")
    normalized_edges: list[dict[str, str]] = []
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"from", "to"}:
            raise DevelopmentCampaignError("invalid dependency edge")
        if not all(isinstance(edge[k], str) and edge[k] for k in ("from", "to")):
            raise DevelopmentCampaignError("dependency edges require non-empty strings")
        normalized_edges.append({"from": edge["from"], "to": edge["to"]})

    allowance = spec["proposal_allowance"]
    required_allowance = {
        "max_candidates",
        "max_model_calls",
        "allowed_resource_classes",
    }
    if not isinstance(allowance, dict) or set(allowance) != required_allowance:
        raise DevelopmentCampaignError("proposal_allowance fields are not exact")
    max_candidates = allowance["max_candidates"]
    max_model_calls = allowance["max_model_calls"]
    if not isinstance(max_candidates, int) or not 1 <= max_candidates <= 10:
        raise DevelopmentCampaignError("max_candidates must be 1..10")
    if not isinstance(max_model_calls, int) or not 0 <= max_model_calls <= 3:
        raise DevelopmentCampaignError("max_model_calls must be 0..3")
    resource_classes = _unique_nonempty_strings(
        allowance["allowed_resource_classes"], "allowed_resource_classes"
    )
    if not set(resource_classes).issubset(RESOURCE_CLASSES):
        raise DevelopmentCampaignError("unknown resource class")

    return {
        "schema": CAMPAIGN_SCHEMA,
        "campaign_id": spec["campaign_id"],
        "title": spec["title"],
        "basis_refs": basis_refs,
        "objective": spec["objective"],
        "claim_ceiling": spec["claim_ceiling"],
        "target_objects": target_objects,
        "unresolved_relations": normalized_relations,
        "pressure_points": list(pressure_points),
        "dependency_edges": normalized_edges,
        "proposal_allowance": {
            "max_candidates": max_candidates,
            "max_model_calls": max_model_calls,
            "allowed_resource_classes": resource_classes,
            "external_effects": "NONE",
            "authority_effect": "NONE",
        },
        "completion_criteria": completion,
        "stop_conditions": stops,
        "explicit_non_authorizations": nonauth,
        "status": "CANDIDATE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "adoption_effect": "NONE",
    }


def validate_campaign(campaign: dict[str, Any]) -> None:
    expected = build_campaign(
        {
            "campaign_id": campaign.get("campaign_id"),
            "title": campaign.get("title"),
            "basis_refs": campaign.get("basis_refs"),
            "objective": campaign.get("objective"),
            "claim_ceiling": campaign.get("claim_ceiling"),
            "target_objects": campaign.get("target_objects"),
            "unresolved_relations": campaign.get("unresolved_relations"),
            "pressure_points": campaign.get("pressure_points"),
            "dependency_edges": campaign.get("dependency_edges"),
            "proposal_allowance": {
                "max_candidates": campaign.get("proposal_allowance", {}).get("max_candidates"),
                "max_model_calls": campaign.get("proposal_allowance", {}).get("max_model_calls"),
                "allowed_resource_classes": campaign.get("proposal_allowance", {}).get(
                    "allowed_resource_classes"
                ),
            },
            "completion_criteria": campaign.get("completion_criteria"),
            "stop_conditions": campaign.get("stop_conditions"),
            "explicit_non_authorizations": campaign.get("explicit_non_authorizations"),
        }
    )
    if campaign != expected:
        raise DevelopmentCampaignError("campaign bytes do not match build_campaign v0")


def validate_request(request: dict[str, Any], campaign: dict[str, Any]) -> None:
    required = {
        "schema",
        "request_id",
        "campaign_id",
        "campaign_sha256",
        "seat_id",
        "object_under_pressure",
        "unresolved_relation_id",
        "unresolved_relation",
        "smallest_proposed_intervention",
        "expected_observable",
        "allowed_effect_surface",
        "forbidden_effects",
        "required_authority",
        "resource_cost",
        "expected_information_gain",
        "stop_conditions",
        "packet_status",
        "authorization_effect",
        "execution_effect",
    }
    if set(request) != required:
        raise DevelopmentCampaignError("envelope request fields are not exact")
    if request["schema"] != REQUEST_SCHEMA:
        raise DevelopmentCampaignError("unexpected request schema")
    if request["campaign_id"] != campaign["campaign_id"]:
        raise DevelopmentCampaignError("request campaign_id mismatch")
    if request["campaign_sha256"] != object_sha256(campaign):
        raise DevelopmentCampaignError("request campaign identity mismatch")
    for field in (
        "request_id",
        "seat_id",
        "object_under_pressure",
        "unresolved_relation_id",
        "unresolved_relation",
        "smallest_proposed_intervention",
        "expected_observable",
        "required_authority",
        "expected_information_gain",
    ):
        if not isinstance(request[field], str) or not request[field]:
            raise DevelopmentCampaignError(f"{field} must be non-empty")

    relation_map = {
        item["relation_id"]: item["statement"] for item in campaign["unresolved_relations"]
    }
    rid = request["unresolved_relation_id"]
    if rid not in relation_map or request["unresolved_relation"] != relation_map[rid]:
        raise DevelopmentCampaignError("request relation is not in campaign")
    if request["object_under_pressure"] not in campaign["target_objects"]:
        raise DevelopmentCampaignError("object_under_pressure is not in campaign")

    allowed_effect_surface = request["allowed_effect_surface"]
    if not isinstance(allowed_effect_surface, list) or not all(
        isinstance(v, str) and v for v in allowed_effect_surface
    ):
        raise DevelopmentCampaignError("allowed_effect_surface must be a string list")

    forbidden = request["forbidden_effects"]
    if not isinstance(forbidden, list) or not forbidden or not all(
        isinstance(v, str) and v for v in forbidden
    ):
        raise DevelopmentCampaignError("forbidden_effects must be non-empty strings")

    stops = request["stop_conditions"]
    if not isinstance(stops, list) or not stops or not all(
        isinstance(v, str) and v for v in stops
    ):
        raise DevelopmentCampaignError("stop_conditions must be non-empty strings")

    cost = request["resource_cost"]
    if not isinstance(cost, dict) or set(cost) != {"resource_class", "model_calls", "notes"}:
        raise DevelopmentCampaignError("invalid resource_cost")
    if cost["resource_class"] not in campaign["proposal_allowance"]["allowed_resource_classes"]:
        raise DevelopmentCampaignError("resource class exceeds campaign allowance")
    if (
        not isinstance(cost["model_calls"], int)
        or cost["model_calls"] < 0
        or cost["model_calls"] > campaign["proposal_allowance"]["max_model_calls"]
    ):
        raise DevelopmentCampaignError("model call cost exceeds campaign allowance")
    if not isinstance(cost["notes"], str):
        raise DevelopmentCampaignError("resource notes must be text")

    if request["packet_status"] != "CANDIDATE_REQUEST":
        raise DevelopmentCampaignError("request is not candidate-only")
    if request["authorization_effect"] != "NONE":
        raise DevelopmentCampaignError("request may not grant authorization")
    if request["execution_effect"] != "NONE":
        raise DevelopmentCampaignError("request may not grant execution")


def validate_standing_update(update: dict[str, Any], campaign: dict[str, Any]) -> None:
    required = {
        "schema",
        "campaign_id",
        "relation_id",
        "standing",
        "adjudication_ref",
        "basis_ref",
    }
    if set(update) != required or update["schema"] != STANDING_SCHEMA:
        raise DevelopmentCampaignError("invalid standing update shape")
    if update["campaign_id"] != campaign["campaign_id"]:
        raise DevelopmentCampaignError("standing update campaign mismatch")
    relation_ids = {item["relation_id"] for item in campaign["unresolved_relations"]}
    if update["relation_id"] not in relation_ids:
        raise DevelopmentCampaignError("standing update relation not in campaign")
    if update["standing"] not in STANDING_VALUES:
        raise DevelopmentCampaignError("invalid standing")
    if not isinstance(update["adjudication_ref"], str) or not update["adjudication_ref"]:
        raise DevelopmentCampaignError("standing update needs adjudication_ref")
    if not isinstance(update["basis_ref"], str) or not update["basis_ref"]:
        raise DevelopmentCampaignError("standing update needs basis_ref")


class CampaignStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS campaigns(
                    campaign_id TEXT PRIMARY KEY,
                    campaign_sha256 TEXT NOT NULL,
                    campaign_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS relation_standing(
                    campaign_id TEXT NOT NULL,
                    relation_id TEXT NOT NULL,
                    standing TEXT NOT NULL,
                    adjudication_ref TEXT,
                    basis_ref TEXT,
                    PRIMARY KEY(campaign_id, relation_id)
                );

                CREATE TABLE IF NOT EXISTS envelope_requests(
                    request_id TEXT PRIMARY KEY,
                    request_sha256 TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    seat_id TEXT NOT NULL,
                    relation_id TEXT NOT NULL,
                    request_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS execution_receipts(
                    receipt_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    execution_status TEXT NOT NULL
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

    def post_campaign(self, campaign: dict[str, Any]) -> dict[str, Any]:
        validate_campaign(campaign)
        digest = object_sha256(campaign)
        rendered = _canonical_bytes(campaign).decode("utf-8")
        conn = self._connect()
        try:
            existing = conn.execute(
                "SELECT * FROM campaigns WHERE campaign_id=?",
                (campaign["campaign_id"],),
            ).fetchone()
            if existing is not None:
                if existing["campaign_sha256"] != digest:
                    raise DevelopmentCampaignError(
                        "campaign_id already names different campaign bytes"
                    )
                return {
                    "campaign_id": campaign["campaign_id"],
                    "campaign_sha256": digest,
                    "idempotent_replay": True,
                    "authority_effect": "NONE",
                    "execution_effect": "NONE",
                }

            conn.execute(
                """
                INSERT INTO campaigns(campaign_id, campaign_sha256, campaign_json)
                VALUES(?,?,?)
                """,
                (campaign["campaign_id"], digest, rendered),
            )
            for relation in campaign["unresolved_relations"]:
                conn.execute(
                    """
                    INSERT INTO relation_standing(
                        campaign_id, relation_id, standing, adjudication_ref, basis_ref
                    ) VALUES(?,?, 'OPEN', NULL, NULL)
                    """,
                    (campaign["campaign_id"], relation["relation_id"]),
                )
            conn.commit()
            return {
                "campaign_id": campaign["campaign_id"],
                "campaign_sha256": digest,
                "idempotent_replay": False,
                "authority_effect": "NONE",
                "execution_effect": "NONE",
            }
        finally:
            conn.close()

    def get_campaign(self, campaign_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT campaign_json FROM campaigns WHERE campaign_id=?",
                (campaign_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise DevelopmentCampaignError(f"unknown campaign {campaign_id!r}")
        return json.loads(row["campaign_json"])

    def lodge_request(self, request: dict[str, Any]) -> dict[str, Any]:
        campaign = self.get_campaign(request.get("campaign_id", ""))
        validate_request(request, campaign)
        digest = object_sha256(request)
        rendered = _canonical_bytes(request).decode("utf-8")

        conn = self._connect()
        try:
            existing = conn.execute(
                "SELECT * FROM envelope_requests WHERE request_id=?",
                (request["request_id"],),
            ).fetchone()
            if existing is not None:
                if existing["request_sha256"] != digest:
                    raise DevelopmentCampaignError(
                        "request_id already names different request bytes"
                    )
                return {
                    "request_id": request["request_id"],
                    "idempotent_replay": True,
                    "authorization_effect": "NONE",
                    "execution_effect": "NONE",
                }

            count = conn.execute(
                """
                SELECT COUNT(*) FROM envelope_requests
                WHERE campaign_id=? AND seat_id=?
                """,
                (request["campaign_id"], request["seat_id"]),
            ).fetchone()[0]
            if count >= campaign["proposal_allowance"]["max_candidates"]:
                raise DevelopmentCampaignError(
                    "seat candidate count exceeds campaign draft allowance"
                )

            conn.execute(
                """
                INSERT INTO envelope_requests(
                    request_id, request_sha256, campaign_id, seat_id, relation_id,
                    request_json
                ) VALUES(?,?,?,?,?,?)
                """,
                (
                    request["request_id"],
                    digest,
                    request["campaign_id"],
                    request["seat_id"],
                    request["unresolved_relation_id"],
                    rendered,
                ),
            )
            conn.commit()
            return {
                "request_id": request["request_id"],
                "idempotent_replay": False,
                "authorization_effect": "NONE",
                "execution_effect": "NONE",
            }
        finally:
            conn.close()

    def draft_requests(
        self,
        campaign_id: str,
        seat_id: str,
        *,
        max_candidates: int | None = None,
    ) -> list[dict[str, Any]]:
        campaign = self.get_campaign(campaign_id)
        snapshot = self.snapshot(campaign_id, current_basis_refs=campaign["basis_refs"])
        open_relations = snapshot["open_relations"]

        conn = self._connect()
        try:
            existing_rows = conn.execute(
                """
                SELECT request_json FROM envelope_requests
                WHERE campaign_id=? AND seat_id=?
                ORDER BY request_id
                """,
                (campaign_id, seat_id),
            ).fetchall()
        finally:
            conn.close()
        if existing_rows:
            return [json.loads(row["request_json"]) for row in existing_rows]

        allowance = campaign["proposal_allowance"]["max_candidates"]
        if max_candidates is None:
            limit = allowance
        else:
            if not isinstance(max_candidates, int) or max_candidates < 1:
                raise DevelopmentCampaignError("max_candidates must be positive")
            limit = min(max_candidates, allowance)

        if "DETERMINISTIC" not in campaign["proposal_allowance"]["allowed_resource_classes"]:
            raise DevelopmentCampaignError("deterministic draft allowance unavailable")

        relation_map = {
            item["relation_id"]: item["statement"] for item in campaign["unresolved_relations"]
        }
        targets = campaign["target_objects"]
        pressure_points = campaign["pressure_points"] or [
            "Apply the smallest intervention that independently varies the relation."
        ]
        campaign_sha = object_sha256(campaign)
        requests: list[dict[str, Any]] = []

        for index, relation_id in enumerate(open_relations[:limit]):
            statement = relation_map[relation_id]
            target = targets[index % len(targets)]
            pressure = pressure_points[index % len(pressure_points)]
            request = {
                "schema": REQUEST_SCHEMA,
                "request_id": f"{campaign_id}-{seat_id}-E{index + 1:02d}",
                "campaign_id": campaign_id,
                "campaign_sha256": campaign_sha,
                "seat_id": seat_id,
                "object_under_pressure": target,
                "unresolved_relation_id": relation_id,
                "unresolved_relation": statement,
                "smallest_proposed_intervention": pressure,
                "expected_observable": (
                    f"Whether pressure on {relation_id} changes an observable consequence."
                ),
                "allowed_effect_surface": [],
                "forbidden_effects": list(campaign["explicit_non_authorizations"]),
                "required_authority": "EXECUTIVE_AUTHORIZATION_REQUIRED",
                "resource_cost": {
                    "resource_class": "DETERMINISTIC",
                    "model_calls": 0,
                    "notes": "Deterministic envelope skeleton only.",
                },
                "expected_information_gain": (
                    f"Discriminate the unresolved relation: {statement}"
                ),
                "stop_conditions": list(campaign["stop_conditions"]),
                "packet_status": "CANDIDATE_REQUEST",
                "authorization_effect": "NONE",
                "execution_effect": "NONE",
            }
            self.lodge_request(request)
            requests.append(request)
        return requests

    def record_execution_receipt(
        self,
        *,
        receipt_id: str,
        request_id: str,
        execution_status: str,
    ) -> None:
        if not receipt_id or not request_id or not execution_status:
            raise DevelopmentCampaignError("receipt fields must be non-empty")
        conn = self._connect()
        try:
            request = conn.execute(
                "SELECT request_id FROM envelope_requests WHERE request_id=?",
                (request_id,),
            ).fetchone()
            if request is None:
                raise DevelopmentCampaignError("receipt request does not exist")
            conn.execute(
                """
                INSERT INTO execution_receipts(receipt_id, request_id, execution_status)
                VALUES(?,?,?)
                """,
                (receipt_id, request_id, execution_status),
            )
            conn.commit()
        finally:
            conn.close()

    def record_standing_update(self, update: dict[str, Any]) -> None:
        campaign = self.get_campaign(update.get("campaign_id", ""))
        validate_standing_update(update, campaign)
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE relation_standing
                SET standing=?, adjudication_ref=?, basis_ref=?
                WHERE campaign_id=? AND relation_id=?
                """,
                (
                    update["standing"],
                    update["adjudication_ref"],
                    update["basis_ref"],
                    update["campaign_id"],
                    update["relation_id"],
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def snapshot(
        self,
        campaign_id: str,
        *,
        current_basis_refs: list[str],
    ) -> dict[str, Any]:
        campaign = self.get_campaign(campaign_id)
        conn = self._connect()
        try:
            standing_rows = conn.execute(
                """
                SELECT relation_id, standing, adjudication_ref, basis_ref
                FROM relation_standing
                WHERE campaign_id=?
                ORDER BY relation_id
                """,
                (campaign_id,),
            ).fetchall()
            request_rows = conn.execute(
                """
                SELECT request_id, seat_id, relation_id
                FROM envelope_requests
                WHERE campaign_id=?
                ORDER BY request_id
                """,
                (campaign_id,),
            ).fetchall()
            receipt_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM execution_receipts r
                JOIN envelope_requests e ON e.request_id = r.request_id
                WHERE e.campaign_id=?
                """,
                (campaign_id,),
            ).fetchone()[0]
        finally:
            conn.close()

        standings = {
            row["relation_id"]: {
                "standing": row["standing"],
                "adjudication_ref": row["adjudication_ref"],
                "basis_ref": row["basis_ref"],
            }
            for row in standing_rows
        }
        open_relations = sorted(
            rid for rid, value in standings.items() if value["standing"] == "OPEN"
        )
        frontier_status = "RESOLVED" if not open_relations else "OPEN"
        basis_status = (
            "CURRENT"
            if current_basis_refs == campaign["basis_refs"]
            else "STALE"
        )
        return {
            "campaign_id": campaign_id,
            "campaign_sha256": object_sha256(campaign),
            "campaign_status": campaign["status"],
            "frontier_status": frontier_status,
            "basis_status": basis_status,
            "open_relations": open_relations,
            "standing": standings,
            "candidate_requests": [
                {
                    "request_id": row["request_id"],
                    "seat_id": row["seat_id"],
                    "relation_id": row["relation_id"],
                }
                for row in request_rows
            ],
            "execution_receipt_count": receipt_count,
            "authority_effect": "NONE",
            "execution_effect": "NONE",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--spec", required=True)

    post = sub.add_parser("post")
    post.add_argument("--db", required=True)
    post.add_argument("--campaign", required=True)

    draft = sub.add_parser("draft")
    draft.add_argument("--db", required=True)
    draft.add_argument("--campaign-id", required=True)
    draft.add_argument("--seat-id", required=True)
    draft.add_argument("--max-candidates", type=int)

    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--db", required=True)
    snapshot.add_argument("--campaign-id", required=True)
    snapshot.add_argument("--current-basis-ref", action="append", required=True)

    args = parser.parse_args(argv)

    if args.command == "build":
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        campaign = build_campaign(spec)
        print(json.dumps(campaign, indent=2, sort_keys=True))
        return 0

    store = CampaignStore(args.db)

    if args.command == "post":
        campaign = json.loads(Path(args.campaign).read_text(encoding="utf-8"))
        result = store.post_campaign(campaign)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "draft":
        result = store.draft_requests(
            args.campaign_id,
            args.seat_id,
            max_candidates=args.max_candidates,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "snapshot":
        result = store.snapshot(
            args.campaign_id,
            current_basis_refs=args.current_basis_ref,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    raise DevelopmentCampaignError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
