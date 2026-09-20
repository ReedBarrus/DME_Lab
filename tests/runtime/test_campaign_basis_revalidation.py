from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from tools.bounded_reentry_v0 import ReentryStore
from tools.campaign_basis_revalidation_v0 import (
    ARTIFACT_EVIDENCE_SCHEMA,
    CURRENTLY_APPLICABLE,
    EFFECT_TRACE_SCHEMA,
    INSUFFICIENT_BASIS,
    NOT_APPLICABLE,
    REQUEST_SCHEMA,
    CampaignBasisRevalidationError,
    CampaignBasisRevalidationStore,
    _git_blob_sha1,
    build_revalidation,
    derive_continuity_requirements,
)
from tools.development_campaign_v0 import CampaignStore, object_sha256
from tools.envelope_selection_v0 import SelectionStore
from tools.preparation_assignment_v0 import AssignmentStore
from tools.preparation_v0 import PreparationStore
from tools.wake_source_v0 import WakeSourceStore


ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN_PATH = (
    ROOT
    / "docs"
    / "campaigns"
    / "candidates"
    / "COCKPIT_OPERATING_SPACE_001.json"
)
QUAL_PATH = "docs/candidates/wake_source_v0/QUALIFICATION_001.md"
QUAL_FILE = ROOT / QUAL_PATH


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CampaignBasisRevalidationPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.campaign_bytes = CAMPAIGN_PATH.read_text(encoding="utf-8")
        self.campaign = json.loads(self.campaign_bytes)
        self.qual_content = QUAL_FILE.read_text(encoding="utf-8")
        self.qual_blob = _git_blob_sha1(self.qual_content)
        self.assertEqual(
            self.qual_blob,
            "ee721faebb5f2a3e6780d20b7a558043e164a5b3",
        )
        self.head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip()
        self.assertRegex(self.head, r"^[0-9a-f]{40}$")
        self.current_basis = [
            f"git:{self.head}",
            f"qualification:{QUAL_PATH}@{self.qual_blob}",
        ]
        self.store = CampaignBasisRevalidationStore(
            self.root / "revalidation.sqlite3"
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def evidence(
        self,
        *,
        qualification_content: str | None = None,
        violated_effect: str | None = None,
        metadata: bool = False,
    ) -> list[dict]:
        content = (
            self.qual_content
            if qualification_content is None
            else qualification_content
        )
        rows: list[dict] = [
            {
                "schema": ARTIFACT_EVIDENCE_SCHEMA,
                "artifact_ref": QUAL_PATH,
                "content": content,
            }
        ]
        for value in self.campaign["explicit_non_authorizations"]:
            effect = value.removeprefix("NO_")
            rows.append(
                {
                    "schema": EFFECT_TRACE_SCHEMA,
                    "effect": effect,
                    "event_refs": (
                        [f"raw-event:{effect}:1"]
                        if violated_effect == effect
                        else []
                    ),
                }
            )
        if metadata:
            for idx, row in enumerate(rows, 1):
                row["_seq"] = idx
        return rows

    def request(
        self,
        revalidation_id: str,
        *,
        campaign_bytes: str | None = None,
        basis: list[str] | None = None,
        evidence: list[dict] | None = None,
    ) -> dict:
        return {
            "schema": REQUEST_SCHEMA,
            "revalidation_id": revalidation_id,
            "campaign_bytes": (
                self.campaign_bytes
                if campaign_bytes is None
                else campaign_bytes
            ),
            "candidate_current_basis_refs": (
                list(self.current_basis) if basis is None else list(basis)
            ),
            "raw_evidence": self.evidence() if evidence is None else evidence,
            "adjudication_ref": f"test:{revalidation_id}",
        }

    def test_r1_exact_same_basis_is_current_and_replay_idempotent(self) -> None:
        result = build_revalidation(
            self.request(
                "R1",
                basis=list(self.campaign["basis_refs"]),
            )
        )
        self.assertEqual(result["disposition"], CURRENTLY_APPLICABLE)
        before = self.campaign_bytes
        first = self.store.append(result, campaign=self.campaign)
        second = self.store.append(result, campaign=self.campaign)
        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(CAMPAIGN_PATH.read_text(encoding="utf-8"), before)

    def test_r2_moved_basis_requires_all_grounded_requirements(self) -> None:
        result = build_revalidation(self.request("R2"))
        self.assertNotEqual(
            result["candidate_current_basis_refs"],
            self.campaign["basis_refs"],
        )
        self.assertEqual(result["disposition"], CURRENTLY_APPLICABLE)
        self.assertTrue(
            all(
                row["observed_result"] == "ESTABLISHED"
                for row in result["derived_continuity_requirements"]
            )
        )

        missing_qualification = [
            row
            for row in self.evidence()
            if row["schema"] != ARTIFACT_EVIDENCE_SCHEMA
        ]
        blocked = build_revalidation(
            self.request(
                "R2-NO-QUAL",
                evidence=missing_qualification,
            )
        )
        self.assertEqual(blocked["disposition"], INSUFFICIENT_BASIS)

    def test_r3_changed_required_surface_without_qualification_is_insufficient(self) -> None:
        changed = self.qual_content + "\nUNQUALIFIED REPLACEMENT\n"
        changed_blob = _git_blob_sha1(changed)
        basis = [
            f"git:{self.head}",
            f"qualification:{QUAL_PATH}@{changed_blob}",
        ]
        result = build_revalidation(
            self.request(
                "R3",
                basis=basis,
                evidence=self.evidence(qualification_content=changed),
            )
        )
        self.assertEqual(result["disposition"], INSUFFICIENT_BASIS)
        qual = next(
            row
            for row in result["derived_continuity_requirements"]
            if row["requirement_id"].startswith("QUALIFICATION::")
        )
        self.assertEqual(qual["observed_result"], "UNRESOLVED")

    def test_r4_grounded_non_authorization_fracture_is_not_applicable(self) -> None:
        result = build_revalidation(
            self.request(
                "R4",
                evidence=self.evidence(
                    violated_effect="DIRECT_CONTROLLER_MUTATION"
                ),
            )
        )
        self.assertEqual(result["disposition"], NOT_APPLICABLE)
        fractured = [
            row
            for row in result["derived_continuity_requirements"]
            if row["observed_result"] == "FRACTURED"
        ]
        self.assertEqual(
            [row["requirement_id"] for row in fractured],
            ["NONAUTH::DIRECT_CONTROLLER_MUTATION"],
        )
        self.assertEqual(result["standing_effect"], "NONE")

    def test_r5_unrelated_content_addressed_world_change_remains_current(self) -> None:
        unrelated = hashlib.sha256(b"unrelated-world-change").hexdigest()
        basis = list(self.current_basis) + [
            f"sha256:unrelated-world:{unrelated}"
        ]
        result = build_revalidation(self.request("R5", basis=basis))
        self.assertEqual(result["disposition"], CURRENTLY_APPLICABLE)
        expected_ids = [
            row["requirement_id"]
            for row in derive_continuity_requirements(self.campaign)
        ]
        actual_ids = [
            row["requirement_id"]
            for row in result["derived_continuity_requirements"]
        ]
        self.assertEqual(actual_ids, expected_ids)

    def test_r6_changed_campaign_bytes_do_not_inherit_prior_revalidation(self) -> None:
        result = build_revalidation(self.request("R6-ORIGINAL"))
        self.store.append(result, campaign=self.campaign)

        changed = copy.deepcopy(self.campaign)
        changed["title"] = "Cockpit Operating Space Horizon — changed identity"
        changed_bytes = json.dumps(changed, indent=2) + "\n"
        changed_obj = json.loads(changed_bytes)
        self.assertEqual(changed_obj["campaign_id"], self.campaign["campaign_id"])
        self.assertNotEqual(
            object_sha256(changed_obj),
            object_sha256(self.campaign),
        )

        projection = self.store.current_applicability(
            changed_obj,
            current_basis_refs=self.current_basis,
        )
        self.assertEqual(projection["applicability"], "NOT_ESTABLISHED")

    def test_r7_success_has_no_adoption_or_other_downstream_effect(self) -> None:
        result = build_revalidation(self.request("R7"))
        self.assertEqual(result["disposition"], CURRENTLY_APPLICABLE)
        for field in (
            "authority_effect",
            "adoption_effect",
            "selection_effect",
            "standing_effect",
            "execution_effect",
            "priority_effect",
            "scheduler_effect",
        ):
            self.assertEqual(result[field], "NONE")

    def test_r8_failure_preserves_history_and_prior_result(self) -> None:
        success = build_revalidation(self.request("R8-SUCCESS"))
        self.store.append(success, campaign=self.campaign)

        failed = build_revalidation(
            self.request(
                "R8-FAIL",
                evidence=self.evidence(
                    violated_effect="AUTOMATIC_PRIORITY"
                ),
            )
        )
        self.assertEqual(failed["disposition"], NOT_APPLICABLE)
        self.store.append(failed, campaign=self.campaign)

        history = self.store.history(self.campaign["campaign_id"])
        self.assertEqual(len(history), 2)
        first = self.store.durable_object(history[0])
        self.assertEqual(first, success)
        self.assertEqual(
            CAMPAIGN_PATH.read_text(encoding="utf-8"),
            self.campaign_bytes,
        )

    def test_r9_success_at_b2_does_not_transfer_to_b3(self) -> None:
        success = build_revalidation(self.request("R9-B2"))
        self.store.append(success, campaign=self.campaign)

        b2 = self.store.current_applicability(
            self.campaign,
            current_basis_refs=self.current_basis,
        )
        self.assertEqual(b2["applicability"], CURRENTLY_APPLICABLE)

        b3_git = "0" * 40 if self.head != "0" * 40 else "1" * 40
        b3 = [
            f"git:{b3_git}",
            f"qualification:{QUAL_PATH}@{self.qual_blob}",
        ]
        moved = self.store.current_applicability(
            self.campaign,
            current_basis_refs=b3,
        )
        self.assertEqual(moved["applicability"], "NOT_ESTABLISHED")

    def test_r10_answer_key_inputs_are_rejected(self) -> None:
        top_level = self.request("R10-TOP")
        top_level["campaign_currently_applicable"] = True
        with self.assertRaises(CampaignBasisRevalidationError):
            build_revalidation(top_level)

        evidence = self.evidence()
        evidence[0]["requirement_passed"] = True
        with self.assertRaises(CampaignBasisRevalidationError):
            build_revalidation(self.request("R10-EVIDENCE", evidence=evidence))

    def test_a1_requirement_derivation_is_deterministic(self) -> None:
        first = derive_continuity_requirements(self.campaign)
        second = derive_continuity_requirements(copy.deepcopy(self.campaign))
        self.assertEqual(first, second)

    def test_a2_omitted_grounded_requirement_is_failure_legible(self) -> None:
        result = build_revalidation(self.request("A2"))
        result["derived_continuity_requirements"] = result[
            "derived_continuity_requirements"
        ][1:]
        with self.assertRaises(CampaignBasisRevalidationError):
            self.store.append(result, campaign=self.campaign)

    def test_a3_evidence_order_is_not_semantic(self) -> None:
        evidence = self.evidence()
        first = build_revalidation(
            self.request("A3", evidence=evidence)
        )
        second = build_revalidation(
            self.request("A3", evidence=list(reversed(evidence)))
        )
        self.assertEqual(first, second)

    def test_a4_storage_metadata_is_excluded_from_durable_identity(self) -> None:
        clean = build_revalidation(
            self.request("A4", evidence=self.evidence())
        )
        annotated = build_revalidation(
            self.request("A4", evidence=self.evidence(metadata=True))
        )
        self.assertEqual(clean, annotated)
        self.store.append(clean, campaign=self.campaign)
        history_row = self.store.history(self.campaign["campaign_id"])[0]
        self.assertIn("_seq", history_row)
        self.assertEqual(self.store.durable_object(history_row), clean)

    def test_a5_revalidation_id_collision_with_changed_bytes_is_rejected(self) -> None:
        success = build_revalidation(self.request("A5"))
        self.store.append(success, campaign=self.campaign)
        changed = build_revalidation(
            self.request(
                "A5",
                evidence=self.evidence(
                    violated_effect="AUTOMATIC_ASSIGNMENT"
                ),
            )
        )
        with self.assertRaises(CampaignBasisRevalidationError):
            self.store.append(changed, campaign=self.campaign)

    def test_a6_current_basis_must_be_explicit_and_content_addressed(self) -> None:
        bad = ["git:HEAD", f"qualification:{QUAL_PATH}@{self.qual_blob}"]
        with self.assertRaises(CampaignBasisRevalidationError):
            build_revalidation(self.request("A6-BAD", basis=bad))

        good = build_revalidation(self.request("A6-GOOD"))
        self.assertEqual(
            good["candidate_current_basis_sha256"],
            object_sha256(self.current_basis),
        )

    def test_a7_a10_revalidation_store_is_isolated_from_operational_stores(self) -> None:
        campaign_db = self.root / "campaign.sqlite3"
        selection_db = self.root / "selection.sqlite3"
        prep_db = self.root / "preparation.sqlite3"
        assignment_db = self.root / "assignment.sqlite3"
        reentry_db = self.root / "reentry.sqlite3"
        wake_db = self.root / "wake.sqlite3"
        controller_db = self.root / "controller.sqlite3"

        campaign_store = CampaignStore(campaign_db)
        campaign_store.post_campaign(self.campaign)
        selection_store = SelectionStore(campaign_store, selection_db)
        prep_store = PreparationStore(campaign_store, selection_store, prep_db)
        assignment_store = AssignmentStore(
            campaign_store,
            selection_store,
            prep_store,
            assignment_db,
        )
        reentry_store = ReentryStore(reentry_db)
        WakeSourceStore(
            assignment_store=assignment_store,
            reentry_store=reentry_store,
            db_path=wake_db,
        )
        conn = sqlite3.connect(controller_db)
        try:
            conn.execute("CREATE TABLE sentinel(value TEXT)")
            conn.execute("INSERT INTO sentinel VALUES('UNCHANGED')")
            conn.commit()
        finally:
            conn.close()

        operational = [
            campaign_db,
            selection_db,
            prep_db,
            assignment_db,
            reentry_db,
            wake_db,
            controller_db,
        ]
        before = {path.name: file_sha(path) for path in operational}

        result = build_revalidation(self.request("A7-A10"))
        self.store.append(result, campaign=self.campaign)

        after = {path.name: file_sha(path) for path in operational}
        self.assertEqual(after, before)

        conn = sqlite3.connect(campaign_db)
        try:
            standing_count = conn.execute(
                "SELECT COUNT(*) FROM relation_standing"
            ).fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(
            standing_count,
            len(self.campaign["unresolved_relations"]),
        )


if __name__ == "__main__":
    unittest.main()
