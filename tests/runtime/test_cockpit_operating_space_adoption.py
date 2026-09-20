from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from tools.campaign_adoption_v0 import (
    CURRENT_ADOPTED,
    LIVE,
    CampaignAdoptionStore,
)
from tools.campaign_applicability_projection_v0 import (
    CURRENT_BY_REVALIDATION,
    CampaignApplicabilityProjector,
)
from tools.campaign_basis_revalidation_v0 import (
    ARTIFACT_EVIDENCE_SCHEMA,
    EFFECT_TRACE_SCHEMA,
    CURRENTLY_APPLICABLE,
    CampaignBasisRevalidationStore,
    build_revalidation,
)
from tools.development_campaign_v0 import CampaignStore, object_sha256


ROOT = Path(__file__).resolve().parents[2]

ADMISSION_GIT_BASIS = "d644f22efdd164dafc1104b20a77e3e157ba5f32"
EXPECTED_CAMPAIGN_SHA256 = (
    "92b67855b553c727928bf45be5ea6206c177d5c4e93416987795f94d3d11406b"
)
EXPECTED_ADOPTION_SHA256 = (
    "1dc27e46301ff7edbabdb0d39805c18d0631305e491133caf1060ffbb9bd8c72"
)


class CockpitOperatingSpaceAdoptionDogfood(unittest.TestCase):
    def test_reed_adoption_is_admitted_against_exact_current_warrant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign_store = CampaignStore(root / "campaign.sqlite3")
            revalidation_store = CampaignBasisRevalidationStore(
                root / "revalidation.sqlite3"
            )
            adoption_store = CampaignAdoptionStore(root / "adoption.sqlite3")

            campaign_path = (
                ROOT
                / "docs"
                / "campaigns"
                / "candidates"
                / "COCKPIT_OPERATING_SPACE_001.json"
            )
            campaign_bytes = campaign_path.read_text(encoding="utf-8")
            campaign = json.loads(campaign_bytes)
            self.assertEqual(object_sha256(campaign), EXPECTED_CAMPAIGN_SHA256)
            campaign_store.post_campaign(campaign)

            qualification_ref = next(
                ref
                for ref in campaign["basis_refs"]
                if ref.startswith("qualification:")
            )
            prefix, _blob = qualification_ref.rsplit("@", 1)
            qualification_path = prefix.removeprefix("qualification:")
            qualification_content = (ROOT / qualification_path).read_text(
                encoding="utf-8"
            )

            admission_basis = [
                "git:" + ADMISSION_GIT_BASIS,
                qualification_ref,
            ]

            raw_evidence: list[dict] = [
                {
                    "schema": ARTIFACT_EVIDENCE_SCHEMA,
                    "artifact_ref": qualification_path,
                    "content": qualification_content,
                }
            ]
            for value in campaign["explicit_non_authorizations"]:
                raw_evidence.append(
                    {
                        "schema": EFFECT_TRACE_SCHEMA,
                        "effect": value[3:],
                        "event_refs": [],
                    }
                )

            revalidation = build_revalidation(
                {
                    "schema": "campaign_basis_revalidation_request_v0",
                    "revalidation_id": "COS-REVALIDATION-ADOPTION-001",
                    "campaign_bytes": (
                        json.dumps(
                            campaign,
                            sort_keys=True,
                            separators=(",", ":"),
                            ensure_ascii=False,
                        )
                        + "\n"
                    ),
                    "candidate_current_basis_refs": admission_basis,
                    "raw_evidence": raw_evidence,
                    "adjudication_ref": (
                        "dogfood:COCKPIT_OPERATING_SPACE_001:ADOPTION_001"
                    ),
                }
            )
            retained_revalidation = json.loads(
                (
                    ROOT
                    / "docs"
                    / "dogfood"
                    / "cockpit_operating_space_001"
                    / "REVALIDATION_001.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(revalidation, retained_revalidation)
            self.assertEqual(
                revalidation["disposition"],
                CURRENTLY_APPLICABLE,
            )
            revalidation_store.append(revalidation, campaign=campaign)

            projector = CampaignApplicabilityProjector(
                campaign_store,
                revalidation_store,
            )
            applicability = projector.project(
                campaign["campaign_id"],
                current_basis_refs=admission_basis,
            )
            self.assertEqual(
                applicability["effective_applicability"],
                CURRENT_BY_REVALIDATION,
            )
            self.assertEqual(
                applicability["historical_basis_status"],
                "STALE",
            )

            adoption_path = (
                ROOT
                / "docs"
                / "dogfood"
                / "cockpit_operating_space_001"
                / "ADOPTION_001.json"
            )
            adoption = json.loads(adoption_path.read_text(encoding="utf-8"))
            self.assertEqual(object_sha256(adoption), EXPECTED_ADOPTION_SHA256)

            receipt = adoption_store.append(
                adoption,
                campaign=campaign,
                applicability_projector=projector,
                current_basis_refs=admission_basis,
            )
            self.assertFalse(receipt["idempotent_replay"])

            current_adoption = adoption_store.current_adoption(campaign)
            self.assertEqual(
                current_adoption["current_adoption_state"],
                CURRENT_ADOPTED,
            )
            live = adoption_store.live_projection(
                campaign,
                current_basis_refs=admission_basis,
                applicability_projector=projector,
            )
            self.assertEqual(live["live_developmental_contract"], LIVE)
            self.assertEqual(
                live["effective_applicability"],
                CURRENT_BY_REVALIDATION,
            )

            # The adoption declaration persists after repository movement, but
            # LIVE must be re-earned against the exact current head. The final
            # workflow supplies the PR head SHA explicitly so we do not confuse
            # a pull-request merge ref with the candidate branch identity.
            current_git_basis = os.environ.get(
                "DME_CURRENT_GIT_BASIS",
                ADMISSION_GIT_BASIS,
            )
            self.assertRegex(current_git_basis, r"^[0-9a-f]{40}$")
            adoption_history_before = list(
                adoption_store.history(campaign["campaign_id"])
            )

            current_basis = [
                "git:" + current_git_basis,
                qualification_ref,
            ]
            if current_git_basis != ADMISSION_GIT_BASIS:
                current_revalidation = build_revalidation(
                    {
                        "schema": "campaign_basis_revalidation_request_v0",
                        "revalidation_id": (
                            "COS-REVALIDATION-CURRENT-"
                            + current_git_basis[:12]
                        ),
                        "campaign_bytes": (
                            json.dumps(
                                campaign,
                                sort_keys=True,
                                separators=(",", ":"),
                                ensure_ascii=False,
                            )
                            + "\n"
                        ),
                        "candidate_current_basis_refs": current_basis,
                        "raw_evidence": raw_evidence,
                        "adjudication_ref": (
                            "dogfood:COCKPIT_OPERATING_SPACE_001:"
                            "CURRENT_LIVE_PROJECTION"
                        ),
                    }
                )
                self.assertEqual(
                    current_revalidation["disposition"],
                    CURRENTLY_APPLICABLE,
                )
                revalidation_store.append(
                    current_revalidation,
                    campaign=campaign,
                )

            current_live = adoption_store.live_projection(
                campaign,
                current_basis_refs=current_basis,
                applicability_projector=projector,
            )
            self.assertEqual(
                current_live["current_adoption_state"],
                CURRENT_ADOPTED,
            )
            self.assertEqual(
                current_live["live_developmental_contract"],
                LIVE,
            )
            self.assertEqual(
                current_live["effective_applicability"],
                CURRENT_BY_REVALIDATION,
            )
            self.assertEqual(
                adoption_store.history(campaign["campaign_id"]),
                adoption_history_before,
            )

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
                self.assertEqual(adoption[field], "NONE")
                self.assertEqual(live[field], "NONE")

            print(
                "DOGFOOD_REVALIDATION_JSON="
                + json.dumps(
                    revalidation,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
            )
            print(
                "DOGFOOD_ADOPTION_SHA256="
                + object_sha256(adoption)
            )
            print(
                "DOGFOOD_LIVE_STATE="
                + live["live_developmental_contract"]
            )
            print("DOGFOOD_CURRENT_GIT_BASIS=" + current_git_basis)
            print(
                "DOGFOOD_CURRENT_LIVE_STATE="
                + current_live["live_developmental_contract"]
            )
            print(
                "DOGFOOD_ADOPTION_HISTORY_COUNT="
                + str(len(adoption_history_before))
            )


if __name__ == "__main__":
    unittest.main()
