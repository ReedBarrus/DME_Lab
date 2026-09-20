from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from tools.campaign_applicability_projection_v0 import (
    CURRENT_BY_HISTORICAL_BASIS,
    CURRENT_BY_REVALIDATION,
    NOT_CURRENT,
    REVALIDATION_STALE,
    REVALIDATION_UNAVAILABLE,
    CampaignApplicabilityProjector,
)
from tools.campaign_basis_revalidation_v0 import (
    ARTIFACT_EVIDENCE_SCHEMA,
    EFFECT_TRACE_SCHEMA,
    INSUFFICIENT_BASIS,
    NOT_APPLICABLE,
    CampaignBasisRevalidationStore,
    build_revalidation,
)
from tools.development_campaign_v0 import CampaignStore, object_sha256
from tools.envelope_selection_v0 import (
    SELECT,
    SelectionStore,
    build_selection_event,
)
from tools.preparation_assignment_v0 import AssignmentStore
from tools.preparation_v0 import PreparationStore
from tools.bounded_reentry_v0 import ReentryStore
from tools.wake_source_v0 import WakeSourceStore


ROOT = Path(__file__).resolve().parents[2]


class CampaignApplicabilityProjectionPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)

        self.campaign_db = root / "campaign.sqlite3"
        self.revalidation_db = root / "revalidation.sqlite3"
        self.selection_db = root / "selection.sqlite3"
        self.prep_db = root / "prep.sqlite3"
        self.assignment_db = root / "assignment.sqlite3"
        self.reentry_db = root / "reentry.sqlite3"
        self.wake_db = root / "wake.sqlite3"
        self.controller_db = root / "controller.sqlite3"

        self.campaign_store = CampaignStore(self.campaign_db)
        self.revalidation_store = CampaignBasisRevalidationStore(
            self.revalidation_db
        )
        self.projector = CampaignApplicabilityProjector(
            self.campaign_store,
            self.revalidation_store,
        )

        self.campaign = json.loads(
            (
                ROOT
                / "docs"
                / "campaigns"
                / "candidates"
                / "COCKPIT_OPERATING_SPACE_001.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            self.campaign["campaign_id"],
            "COCKPIT_OPERATING_SPACE_001",
        )
        self.campaign_store.post_campaign(self.campaign)

        self.historical_basis = list(self.campaign["basis_refs"])
        qualification_refs = [
            ref
            for ref in self.historical_basis
            if ref.startswith("qualification:")
        ]
        self.assertEqual(len(qualification_refs), 1)
        qualification = qualification_refs[0]
        prefix, _blob = qualification.rsplit("@", 1)
        self.qualification_path = prefix.removeprefix("qualification:")
        self.qualification_content = (
            ROOT / self.qualification_path
        ).read_text(encoding="utf-8")

        self.b2 = [
            "git:" + "1" * 40,
            qualification,
        ]
        self.b3 = [
            "git:" + "2" * 40,
            qualification,
        ]

        relation = next(
            row
            for row in self.campaign["unresolved_relations"]
            if row["relation_id"] == "COS-R2"
        )
        self.request = {
            "schema": "execution_envelope_request_v0",
            "request_id": "COS-DOGFOOD-E1",
            "campaign_id": self.campaign["campaign_id"],
            "campaign_sha256": object_sha256(self.campaign),
            "seat_id": "MAYA",
            "object_under_pressure": "COCKPIT_ASSIGNMENT_CONTROL",
            "unresolved_relation_id": relation["relation_id"],
            "unresolved_relation": relation["statement"],
            "smallest_proposed_intervention": (
                "Inspect one human-readable assignment representation."
            ),
            "expected_observable": (
                "Whether display remains distinct from queue semantics."
            ),
            "allowed_effect_surface": [],
            "forbidden_effects": list(
                self.campaign["explicit_non_authorizations"]
            ),
            "required_authority": "EXECUTIVE_AUTHORIZATION_REQUIRED",
            "resource_cost": {
                "resource_class": "DETERMINISTIC",
                "model_calls": 0,
                "notes": "Applicability projection fixture only.",
            },
            "expected_information_gain": (
                "Pressure COS-R2 without changing its meaning."
            ),
            "stop_conditions": list(self.campaign["stop_conditions"]),
            "packet_status": "CANDIDATE_REQUEST",
            "authorization_effect": "NONE",
            "execution_effect": "NONE",
        }
        self.campaign_store.lodge_request(self.request)

        self.selection_store = SelectionStore(
            self.campaign_store,
            self.selection_db,
            applicability_projector=self.projector,
        )
        selection = build_selection_event(
            campaign=self.campaign,
            request=self.request,
            selection_id="SEL-COS-R2",
            basis_refs=self.historical_basis,
            kind=SELECT,
            reason="fixture selection only",
        )
        self.selection_store.append(selection)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def raw_evidence(
        self,
        *,
        omit_qualification: bool = False,
        fractured_effect: str | None = None,
    ) -> list[dict]:
        rows: list[dict] = []
        if not omit_qualification:
            rows.append(
                {
                    "schema": ARTIFACT_EVIDENCE_SCHEMA,
                    "artifact_ref": self.qualification_path,
                    "content": self.qualification_content,
                }
            )
        for value in self.campaign["explicit_non_authorizations"]:
            effect = value[3:]
            rows.append(
                {
                    "schema": EFFECT_TRACE_SCHEMA,
                    "effect": effect,
                    "event_refs": (
                        ["EV-FRACTURE"]
                        if effect == fractured_effect
                        else []
                    ),
                }
            )
        return rows

    def revalidate(
        self,
        basis: list[str],
        *,
        revalidation_id: str,
        campaign: dict | None = None,
        omit_qualification: bool = False,
        fractured_effect: str | None = None,
    ) -> dict:
        campaign = campaign or self.campaign
        result = build_revalidation(
            {
                "schema": "campaign_basis_revalidation_request_v0",
                "revalidation_id": revalidation_id,
                "campaign_bytes": campaign,
                "candidate_current_basis_refs": basis,
                "raw_evidence": self.raw_evidence(
                    omit_qualification=omit_qualification,
                    fractured_effect=fractured_effect,
                ),
                "adjudication_ref": "test:campaign-applicability-projection",
            }
        )
        self.revalidation_store.append(result, campaign=campaign)
        return result

    def selection_projection(self, basis: list[str]) -> dict:
        return self.selection_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=basis,
        )

    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_p1_historical_basis_current_without_revalidation(self) -> None:
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.historical_basis,
        )
        self.assertEqual(projection["historical_basis_status"], "CURRENT")
        self.assertEqual(projection["revalidation_status"], "NONE")
        self.assertEqual(
            projection["effective_applicability"],
            CURRENT_BY_HISTORICAL_BASIS,
        )

    def test_p2_stale_historical_basis_exact_valid_revalidation(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-P2")
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(projection["historical_basis_status"], "STALE")
        self.assertEqual(
            projection["revalidation_status"],
            "CURRENTLY_APPLICABLE",
        )
        self.assertEqual(
            projection["effective_applicability"],
            CURRENT_BY_REVALIDATION,
        )
        historical = self.campaign_store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(historical["basis_status"], "STALE")

    def test_p3_b2_warrant_does_not_unblock_b3(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-P3")
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b3,
        )
        self.assertEqual(
            projection["revalidation_status"],
            REVALIDATION_STALE,
        )
        self.assertEqual(
            projection["effective_applicability"],
            NOT_CURRENT,
        )

    def test_p4_wrong_campaign_identity_does_not_transfer(self) -> None:
        altered = copy.deepcopy(self.campaign)
        altered["title"] = "Same label, different exact campaign bytes"
        self.revalidate(
            self.b2,
            revalidation_id="R-P4-WRONG",
            campaign=altered,
        )
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(
            projection["effective_applicability"],
            NOT_CURRENT,
        )
        self.assertTrue(
            any(
                item.startswith("INVALID_REVALIDATION_IDENTITY:")
                for item in projection["diagnostics"]
            )
        )

    def test_p5_insufficient_basis_remains_not_current(self) -> None:
        result = self.revalidate(
            self.b2,
            revalidation_id="R-P5",
            omit_qualification=True,
        )
        self.assertEqual(result["disposition"], INSUFFICIENT_BASIS)
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(
            projection["revalidation_status"],
            INSUFFICIENT_BASIS,
        )
        self.assertEqual(
            projection["effective_applicability"],
            NOT_CURRENT,
        )

    def test_p6_not_applicable_remains_not_current(self) -> None:
        effect = self.campaign["explicit_non_authorizations"][0][3:]
        result = self.revalidate(
            self.b2,
            revalidation_id="R-P6",
            fractured_effect=effect,
        )
        self.assertEqual(result["disposition"], NOT_APPLICABLE)
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(
            projection["revalidation_status"],
            NOT_APPLICABLE,
        )
        self.assertEqual(
            projection["effective_applicability"],
            NOT_CURRENT,
        )

    def test_p7_selection_projection_consumes_exact_warrant(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-P7")
        projection = self.selection_projection(self.b2)
        selected = projection["current_selection_set"][0]
        self.assertEqual(
            selected["request_applicability"],
            CURRENT_BY_REVALIDATION,
        )
        self.assertEqual(
            selected["preparation"],
            "ELIGIBLE_FOR_PACKET_PREPARATION",
        )
        self.assertEqual(
            len(self.selection_store.history(self.campaign["campaign_id"])),
            1,
        )

    def test_p8_selection_projection_rejects_stale_warrant(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-P8")
        projection = self.selection_projection(self.b3)
        selected = projection["current_selection_set"][0]
        self.assertEqual(selected["request_applicability"], "STALE")
        self.assertEqual(
            selected["preparation"],
            "BLOCKED_PENDING_REVALIDATION",
        )

    def test_p9_projection_preserves_historical_snapshot_and_campaign(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-P9")
        campaign_before = json.dumps(
            self.campaign_store.get_campaign(self.campaign["campaign_id"]),
            sort_keys=True,
        )
        snapshot_before = self.campaign_store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        campaign_after = json.dumps(
            self.campaign_store.get_campaign(self.campaign["campaign_id"]),
            sort_keys=True,
        )
        snapshot_after = self.campaign_store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(campaign_before, campaign_after)
        self.assertEqual(snapshot_before, snapshot_after)
        self.assertEqual(snapshot_after["basis_status"], "STALE")

    def test_p10_valid_warrant_has_no_neighboring_effects(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-P10")
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        for field in (
            "authority_effect",
            "adoption_effect",
            "selection_effect",
            "assignment_effect",
            "priority_effect",
            "standing_effect",
            "scheduler_effect",
            "wake_effect",
            "execution_effect",
        ):
            self.assertEqual(projection[field], "NONE")
        self.assertEqual(
            projection["live_developmental_contract"],
            "NOT_ESTABLISHED",
        )

    def test_p11_exact_durable_warrant_identity_exposed(self) -> None:
        result = self.revalidate(self.b2, revalidation_id="R-P11")
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(projection["revalidation_id"], "R-P11")
        self.assertEqual(
            projection["revalidation_sha256"],
            object_sha256(result),
        )
        history = self.revalidation_store.history(
            self.campaign["campaign_id"]
        )
        self.assertIn("_seq", history[0])
        self.assertNotEqual(
            object_sha256(history[0]),
            projection["revalidation_sha256"],
        )

    def test_p12_multiple_matching_warrants_create_no_priority(self) -> None:
        first = self.revalidate(self.b2, revalidation_id="R-P12-B")
        second = self.revalidate(self.b2, revalidation_id="R-P12-A")
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(
            projection["effective_applicability"],
            CURRENT_BY_REVALIDATION,
        )
        self.assertEqual(len(projection["matching_warrants"]), 2)
        self.assertEqual(
            [row["revalidation_id"] for row in projection["matching_warrants"]],
            ["R-P12-A", "R-P12-B"],
        )
        self.assertEqual(projection["priority_effect"], "NONE")
        self.assertEqual(
            projection["warrant_selection_rule"],
            "LEXICOGRAPHIC_DURABLE_IDENTITY_NON_SEMANTIC",
        )
        self.assertEqual(
            {
                row["revalidation_sha256"]
                for row in projection["matching_warrants"]
            },
            {object_sha256(first), object_sha256(second)},
        )

    def test_x1_caller_cannot_supply_effective_verdict(self) -> None:
        with self.assertRaises(TypeError):
            self.projector.project(
                self.campaign["campaign_id"],
                current_basis_refs=self.b2,
                effective_applicability=CURRENT_BY_REVALIDATION,
            )

    def test_x2_mutated_stored_bytes_do_not_validate(self) -> None:
        result = self.revalidate(self.b2, revalidation_id="R-X2")
        changed = copy.deepcopy(result)
        changed["adjudication_ref"] = "tampered:after-storage"
        conn = sqlite3.connect(self.revalidation_db)
        try:
            conn.execute(
                """
                UPDATE campaign_basis_revalidations
                SET result_json=?
                WHERE revalidation_id=?
                """,
                (
                    json.dumps(changed, sort_keys=True, separators=(",", ":")) + "\n",
                    "R-X2",
                ),
            )
            conn.commit()
        finally:
            conn.close()

        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(
            projection["effective_applicability"],
            NOT_CURRENT,
        )
        self.assertTrue(
            any(
                "INVALID_REVALIDATION_IDENTITY:R-X2" in item
                for item in projection["diagnostics"]
            )
        )

    def test_x3_visually_similar_wrong_basis_does_not_match(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X3")
        similar = list(self.b2)
        similar[0] = "git:" + ("1" * 39) + "0"
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=similar,
        )
        self.assertEqual(
            projection["effective_applicability"],
            NOT_CURRENT,
        )

    def test_x4_historical_current_ignores_stale_old_warrants(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X4")
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.historical_basis,
        )
        self.assertEqual(
            projection["effective_applicability"],
            CURRENT_BY_HISTORICAL_BASIS,
        )
        self.assertEqual(projection["revalidation_status"], "NONE")

    def test_x5_missing_revalidation_source_fails_legibly(self) -> None:
        projector = CampaignApplicabilityProjector(
            self.campaign_store,
            None,
        )
        projection = projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(
            projection["revalidation_status"],
            REVALIDATION_UNAVAILABLE,
        )
        self.assertEqual(
            projection["effective_applicability"],
            NOT_CURRENT,
        )
        self.assertIn(
            "REVALIDATION_SOURCE_UNAVAILABLE",
            projection["diagnostics"],
        )

    def test_x6_projection_writes_no_neighboring_store(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X6")

        prep_store = PreparationStore(
            self.campaign_store,
            self.selection_store,
            self.prep_db,
        )
        assignment_store = AssignmentStore(
            self.campaign_store,
            self.selection_store,
            prep_store,
            self.assignment_db,
        )
        reentry_store = ReentryStore(self.reentry_db)
        WakeSourceStore(
            assignment_store=assignment_store,
            reentry_store=reentry_store,
            db_path=self.wake_db,
        )
        conn = sqlite3.connect(self.controller_db)
        try:
            conn.execute("CREATE TABLE marker(value TEXT)")
            conn.execute("INSERT INTO marker(value) VALUES('unchanged')")
            conn.commit()
        finally:
            conn.close()

        watched = [
            self.campaign_db,
            self.revalidation_db,
            self.selection_db,
            self.prep_db,
            self.assignment_db,
            self.reentry_db,
            self.wake_db,
            self.controller_db,
        ]
        before = {path.name: self.digest(path) for path in watched}
        self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.selection_projection(self.b2)
        after = {path.name: self.digest(path) for path in watched}
        self.assertEqual(before, after)

    def test_x7_standing_blocks_independently_of_applicability(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X7")
        for standing, expected in (
            ("FRACTURED", "BLOCKED_OBSOLETE"),
            ("EARNED", "BLOCKED_RESOLVED"),
        ):
            with self.subTest(standing=standing):
                self.campaign_store.record_standing_update(
                    {
                        "schema": "campaign_standing_update_v0",
                        "campaign_id": self.campaign["campaign_id"],
                        "relation_id": "COS-R2",
                        "standing": standing,
                        "adjudication_ref": f"test:{standing}",
                        "basis_ref": self.b2[0],
                    }
                )
                selected = self.selection_projection(self.b2)[
                    "current_selection_set"
                ][0]
                self.assertEqual(
                    selected["request_applicability"],
                    CURRENT_BY_REVALIDATION,
                )
                self.assertEqual(selected["preparation"], expected)

    def test_x8_applicability_does_not_create_live_intent(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X8")
        projection = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(
            projection["effective_applicability"],
            CURRENT_BY_REVALIDATION,
        )
        self.assertEqual(
            projection["live_developmental_contract"],
            "NOT_ESTABLISHED",
        )
        self.assertEqual(projection["adoption_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
