from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.campaign_adoption_v0 import (
    ADOPTED,
    ADOPTION_RELEASED,
    BLOCKED_NOT_CURRENT,
    CURRENT_ADOPTED,
    CURRENT_NOT_ADOPTED,
    LIVE,
    NOT_LIVE,
    CampaignAdoptionError,
    CampaignAdoptionStore,
    build_event,
)
from tools.campaign_applicability_projection_v0 import (
    CampaignApplicabilityProjector,
)
from tools.campaign_basis_revalidation_v0 import (
    ARTIFACT_EVIDENCE_SCHEMA,
    EFFECT_TRACE_SCHEMA,
    CampaignBasisRevalidationStore,
    build_revalidation,
)
from tools.development_campaign_v0 import CampaignStore, object_sha256


ROOT = Path(__file__).resolve().parents[2]


class CampaignAdoptionPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)

        self.campaign_db = root / "campaign.sqlite3"
        self.revalidation_db = root / "revalidation.sqlite3"
        self.adoption_db = root / "adoption.sqlite3"

        self.campaign_store = CampaignStore(self.campaign_db)
        self.revalidation_store = CampaignBasisRevalidationStore(
            self.revalidation_db
        )
        self.projector = CampaignApplicabilityProjector(
            self.campaign_store,
            self.revalidation_store,
        )
        self.adoption_store = CampaignAdoptionStore(self.adoption_db)

        self.campaign = json.loads(
            (
                ROOT
                / "docs"
                / "campaigns"
                / "candidates"
                / "COCKPIT_OPERATING_SPACE_001.json"
            ).read_text(encoding="utf-8")
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

        self.b2 = ["git:" + "1" * 40, qualification]
        self.b3 = ["git:" + "2" * 40, qualification]

    def tearDown(self) -> None:
        self.tmp.cleanup()

    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def raw_evidence(self) -> list[dict]:
        rows: list[dict] = [
            {
                "schema": ARTIFACT_EVIDENCE_SCHEMA,
                "artifact_ref": self.qualification_path,
                "content": self.qualification_content,
            }
        ]
        for value in self.campaign["explicit_non_authorizations"]:
            rows.append(
                {
                    "schema": EFFECT_TRACE_SCHEMA,
                    "effect": value[3:],
                    "event_refs": [],
                }
            )
        return rows

    def revalidate(
        self,
        basis: list[str],
        *,
        revalidation_id: str,
        campaign: dict | None = None,
    ) -> dict:
        campaign = campaign or self.campaign
        result = build_revalidation(
            {
                "schema": "campaign_basis_revalidation_request_v0",
                "revalidation_id": revalidation_id,
                "campaign_bytes": (
                    json.dumps(
                        campaign,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    + "\n"
                ),
                "candidate_current_basis_refs": basis,
                "raw_evidence": self.raw_evidence(),
                "adjudication_ref": "test:campaign-adoption",
            }
        )
        self.revalidation_store.append(result, campaign=campaign)
        return result

    def event(
        self,
        *,
        adoption_id: str = "A1",
        campaign: dict | None = None,
        kind: str = ADOPTED,
        gesture_ref: str = "human:REED:test-explicit-gesture",
        reason: str = "explicit test adoption",
        target_id: str | None = None,
        target_sha: str | None = None,
    ) -> dict:
        campaign = campaign or self.campaign
        return build_event(
            campaign=campaign,
            adoption_id=adoption_id,
            actor_id="REED",
            adoption_kind=kind,
            gesture_ref=gesture_ref,
            reason=reason,
            target_adoption_id=target_id,
            target_adoption_sha256=target_sha,
        )

    def adopt(
        self,
        basis: list[str],
        *,
        adoption_id: str = "A1",
        campaign: dict | None = None,
    ) -> tuple[dict, dict]:
        campaign = campaign or self.campaign
        event = self.event(adoption_id=adoption_id, campaign=campaign)
        receipt = self.adoption_store.append(
            event,
            campaign=campaign,
            applicability_projector=self.projector,
            current_basis_refs=basis,
        )
        return event, receipt

    def release(self, adopted: dict, *, release_id: str = "REL-1") -> dict:
        target_sha = object_sha256(adopted)
        event = self.event(
            adoption_id=release_id,
            kind=ADOPTION_RELEASED,
            reason="explicit release",
            target_id=adopted["adoption_id"],
            target_sha=target_sha,
        )
        self.adoption_store.append(event, campaign=self.campaign)
        return event

    def test_a1_applicable_explicit_adoption_becomes_live(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A1")
        self.adopt(self.b2)
        current = self.adoption_store.current_adoption(self.campaign)
        live = self.adoption_store.live_projection(
            self.campaign,
            current_basis_refs=self.b2,
            applicability_projector=self.projector,
        )
        self.assertEqual(current["current_adoption_state"], CURRENT_ADOPTED)
        self.assertEqual(live["live_developmental_contract"], LIVE)

    def test_a2_applicable_without_adoption_is_not_live(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A2")
        current = self.adoption_store.current_adoption(self.campaign)
        live = self.adoption_store.live_projection(
            self.campaign,
            current_basis_refs=self.b2,
            applicability_projector=self.projector,
        )
        self.assertEqual(current["current_adoption_state"], CURRENT_NOT_ADOPTED)
        self.assertEqual(live["live_developmental_contract"], NOT_LIVE)

    def test_a3_adoption_rejected_when_not_current(self) -> None:
        with self.assertRaisesRegex(CampaignAdoptionError, "not currently applicable"):
            self.adopt(self.b2)
        self.assertEqual(self.adoption_store.history(self.campaign["campaign_id"]), [])

    def test_a4_wrong_campaign_identity_rejected(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A4")
        altered = copy.deepcopy(self.campaign)
        altered["title"] = "Different campaign bytes"
        event = self.event()
        with self.assertRaisesRegex(CampaignAdoptionError, "campaign identity mismatch"):
            self.adoption_store.append(
                event,
                campaign=altered,
                applicability_projector=self.projector,
                current_basis_refs=self.b2,
            )

    def test_a5_missing_gesture_rejected(self) -> None:
        with self.assertRaisesRegex(CampaignAdoptionError, "gesture_ref"):
            self.event(gesture_ref="")

    def test_a6_exact_replay_idempotent(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A6")
        event, first = self.adopt(self.b2)
        second = self.adoption_store.append(
            event,
            campaign=self.campaign,
            applicability_projector=self.projector,
            current_basis_refs=self.b2,
        )
        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])

    def test_a7_same_id_changed_bytes_rejected(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A7")
        self.adopt(self.b2)
        changed = self.event(adoption_id="A1", reason="different durable bytes")
        with self.assertRaisesRegex(CampaignAdoptionError, "different durable bytes"):
            self.adoption_store.append(
                changed,
                campaign=self.campaign,
                applicability_projector=self.projector,
                current_basis_refs=self.b2,
            )

    def test_a8_adoption_declares_no_neighboring_effects(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A8")
        event, _ = self.adopt(self.b2)
        for field in (
            "selection_effect",
            "assignment_effect",
            "priority_effect",
            "standing_effect",
            "authority_effect",
            "scheduler_effect",
            "wake_effect",
            "execution_effect",
        ):
            self.assertEqual(event[field], "NONE")

    def test_a9_exact_release_ends_adoption(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A9")
        adopted, _ = self.adopt(self.b2)
        self.release(adopted)
        current = self.adoption_store.current_adoption(self.campaign)
        live = self.adoption_store.live_projection(
            self.campaign,
            current_basis_refs=self.b2,
            applicability_projector=self.projector,
        )
        self.assertEqual(current["current_adoption_state"], CURRENT_NOT_ADOPTED)
        self.assertEqual(live["live_developmental_contract"], NOT_LIVE)
        self.assertEqual(len(self.adoption_store.history(self.campaign["campaign_id"])), 2)

    def test_a10_world_move_blocks_live_but_not_adoption(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A10")
        self.adopt(self.b2)
        current = self.adoption_store.current_adoption(self.campaign)
        live = self.adoption_store.live_projection(
            self.campaign,
            current_basis_refs=self.b3,
            applicability_projector=self.projector,
        )
        self.assertEqual(current["current_adoption_state"], CURRENT_ADOPTED)
        self.assertEqual(live["live_developmental_contract"], BLOCKED_NOT_CURRENT)

    def test_a11_revalidation_restores_live_without_new_adoption(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-A11-B2")
        self.adopt(self.b2)
        before = len(self.adoption_store.history(self.campaign["campaign_id"]))
        blocked = self.adoption_store.live_projection(
            self.campaign,
            current_basis_refs=self.b3,
            applicability_projector=self.projector,
        )
        self.assertEqual(blocked["live_developmental_contract"], BLOCKED_NOT_CURRENT)

        self.revalidate(self.b3, revalidation_id="R-A11-B3")
        restored = self.adoption_store.live_projection(
            self.campaign,
            current_basis_refs=self.b3,
            applicability_projector=self.projector,
        )
        after = len(self.adoption_store.history(self.campaign["campaign_id"]))
        self.assertEqual(restored["live_developmental_contract"], LIVE)
        self.assertEqual(before, after)

    def test_a12_two_campaigns_can_be_adopted_without_priority(self) -> None:
        second = copy.deepcopy(self.campaign)
        second["campaign_id"] = "COCKPIT_OPERATING_SPACE_002"
        second["title"] = "Second independent live campaign"
        self.campaign_store.post_campaign(second)

        first_event, _ = self.adopt(self.historical_basis, adoption_id="A-C1")
        second_event = self.event(adoption_id="A-C2", campaign=second)
        self.adoption_store.append(
            second_event,
            campaign=second,
            applicability_projector=self.projector,
            current_basis_refs=second["basis_refs"],
        )

        first = self.adoption_store.current_adoption(self.campaign)
        other = self.adoption_store.current_adoption(second)
        self.assertEqual(first["current_adoption_state"], CURRENT_ADOPTED)
        self.assertEqual(other["current_adoption_state"], CURRENT_ADOPTED)
        self.assertEqual(first["priority_effect"], "NONE")
        self.assertEqual(other["priority_effect"], "NONE")
        self.assertEqual(first_event["priority_effect"], "NONE")

    def test_x1_release_wrong_sha_rejected(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X1")
        adopted, _ = self.adopt(self.b2)
        bad = self.event(
            adoption_id="REL-X1",
            kind=ADOPTION_RELEASED,
            target_id=adopted["adoption_id"],
            target_sha="0" * 64,
        )
        with self.assertRaisesRegex(CampaignAdoptionError, "identity mismatch"):
            self.adoption_store.append(bad, campaign=self.campaign)

    def test_x2_release_without_exact_target_rejected(self) -> None:
        with self.assertRaises(CampaignAdoptionError):
            self.event(
                adoption_id="REL-X2",
                kind=ADOPTION_RELEASED,
                target_id=None,
                target_sha=None,
            )

    def test_x3_second_release_of_same_adoption_rejected(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X3")
        adopted, _ = self.adopt(self.b2)
        self.release(adopted, release_id="REL-X3-1")
        with self.assertRaisesRegex(CampaignAdoptionError, "already released"):
            self.release(adopted, release_id="REL-X3-2")

    def test_x4_storage_metadata_not_in_durable_identity(self) -> None:
        event = self.event(adoption_id="A-X4")
        row = dict(event)
        row["_seq"] = 9
        row["_inserted_at"] = "metadata"
        durable = self.adoption_store.durable_object(row)
        self.assertEqual(object_sha256(durable), object_sha256(event))

    def test_x5_neighbor_state_smuggling_rejected(self) -> None:
        event = self.event(adoption_id="A-X5")
        event["priority"] = 1
        with self.assertRaisesRegex(CampaignAdoptionError, "smuggle"):
            self.adoption_store.append(event, campaign=self.campaign)

    def test_x6_applicability_verdict_smuggling_rejected(self) -> None:
        event = self.event(adoption_id="A-X6")
        event["effective_applicability"] = "CURRENT_BY_REVALIDATION"
        with self.assertRaisesRegex(CampaignAdoptionError, "smuggle"):
            self.adoption_store.append(event, campaign=self.campaign)

    def test_x7_activity_without_adoption_is_not_adoption(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X7")
        state = self.adoption_store.current_adoption(self.campaign)
        self.assertEqual(state["current_adoption_state"], CURRENT_NOT_ADOPTED)

    def test_x8_active_adoption_order_is_nonsemantic(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X8")
        self.adopt(self.b2, adoption_id="Z-LAST")
        self.adopt(self.b2, adoption_id="A-FIRST")
        state = self.adoption_store.current_adoption(self.campaign)
        self.assertEqual(
            [row["adoption_id"] for row in state["active_adoptions"]],
            ["A-FIRST", "Z-LAST"],
        )
        self.assertEqual(state["priority_effect"], "NONE")

    def test_x9_missing_applicability_source_fails_closed(self) -> None:
        event = self.event(adoption_id="A-X9")
        with self.assertRaisesRegex(CampaignAdoptionError, "requires current applicability"):
            self.adoption_store.append(event, campaign=self.campaign)

    def test_x10_release_does_not_change_applicability(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X10")
        adopted, _ = self.adopt(self.b2)
        before = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.release(adopted, release_id="REL-X10")
        after = self.projector.project(
            self.campaign["campaign_id"],
            current_basis_refs=self.b2,
        )
        self.assertEqual(before, after)

    def test_x11_adoption_write_leaves_campaign_and_revalidation_stores_unchanged(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X11")
        campaign_before = self.digest(self.campaign_db)
        revalidation_before = self.digest(self.revalidation_db)
        self.adopt(self.b2)
        self.assertEqual(campaign_before, self.digest(self.campaign_db))
        self.assertEqual(revalidation_before, self.digest(self.revalidation_db))

    def test_x12_applicability_restoration_emits_no_adoption_event(self) -> None:
        self.revalidate(self.b2, revalidation_id="R-X12-B2")
        self.adopt(self.b2)
        history_before = self.adoption_store.history(self.campaign["campaign_id"])
        self.revalidate(self.b3, revalidation_id="R-X12-B3")
        live = self.adoption_store.live_projection(
            self.campaign,
            current_basis_refs=self.b3,
            applicability_projector=self.projector,
        )
        history_after = self.adoption_store.history(self.campaign["campaign_id"])
        self.assertEqual(live["live_developmental_contract"], LIVE)
        self.assertEqual(history_before, history_after)


if __name__ == "__main__":
    unittest.main()
