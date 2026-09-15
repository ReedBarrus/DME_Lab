from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from src.runtime import investigator_continuation as continuation
from src.runtime.investigator_continuation import (
    CHECKED_ABSENT,
    CHECK_FAILED,
    CHECK_MATCH,
    CHECK_MISMATCH,
    NOT_CHECKED,
    ContinuationBuildError,
    ContinuationContractError,
    GitObservation,
    admit_packet,
    build_packet,
    canonical_serialize,
    finalize_packet,
    packet_digest,
    verify_packet_integrity,
    write_packet_atomic,
)


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


class InvestigatorContinuationTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "--initial-branch=main")
        git(self.repo, "config", "user.email", "continuation@example.invalid")
        git(self.repo, "config", "user.name", "Continuation Test")
        (self.repo / "source.md").write_text("authoritative alpha\n", encoding="utf-8")
        (self.repo / "other.md").write_text("other\n", encoding="utf-8")
        git(self.repo, "add", "source.md", "other.md")
        git(self.repo, "commit", "-m", "initial basis")
        self.initial_head = git(self.repo, "rev-parse", "HEAD")
        self.prior = {
            "prior_objective_projection": {
                "statement": "Inspect the bounded source without treating this as current authority.",
                "source_refs": ["source-0001"],
            },
            "prior_established": [
                {
                    "statement": "The predecessor retained one projected coordinate.",
                    "standing_at_generation": "PRIOR_PROJECTION",
                    "source_refs": ["source-0001"],
                }
            ],
            "unresolved": [
                {
                    "statement": "Current applicability remains unresolved.",
                    "source_refs": ["source-0001"],
                    "missing_basis": ["current admission"],
                    "next_discriminator": "Verify the current committed source identity.",
                }
            ],
            "must_revalidate": [
                {
                    "coordinate": "source-0001",
                    "reason": "Repository state may change between investigators.",
                    "evidence_refs": ["source-0001"],
                }
            ],
            "inflight_attempts": [],
        }

    def packet(
        self,
        *,
        continuation_id: str = "continuation-0001",
        predecessor_id: str | None = None,
        generated_at: str = "2000-01-01T00:00:00Z",
        prior: dict | None = None,
    ) -> dict:
        return build_packet(
            repo_root=self.repo,
            repository="ReedBarrus/DME_Lab",
            continuation_id=continuation_id,
            predecessor_id=predecessor_id,
            generated_at=generated_at,
            source_paths=["source.md"],
            prior_projected_standing=self.prior if prior is None else prior,
        )

    def test_clean_matching_basis_blob_and_digest_admit(self) -> None:
        packet = self.packet()
        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=packet,
        )

        self.assertTrue(admission["admissible"])
        self.assertEqual(
            packet["mechanical_basis"]["basis_commit"], self.initial_head
        )
        self.assertEqual(packet["mechanical_basis"]["branch"], "main")
        self.assertEqual(
            packet["mechanical_basis"]["source_manifest"][0]["git_blob"],
            git(self.repo, "rev-parse", "HEAD:source.md"),
        )
        self.assertEqual(
            admission["checks"]["source_manifest"][0]["status"], CHECK_MATCH
        )

    def test_digest_rule_is_exact_and_tampering_is_rejected(self) -> None:
        packet = self.packet()
        without_digest = deepcopy(packet)
        without_digest["integrity"].pop("packet_digest")
        expected = hashlib.sha256(
            json.dumps(
                without_digest,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(packet["integrity"]["packet_digest"], expected)

        packet["prior_projected_standing"]["unresolved"][0]["statement"] = "tampered"
        integrity = verify_packet_integrity(packet)
        self.assertEqual(integrity["status"], CHECK_MISMATCH)
        self.assertFalse(
            admit_packet(
                repo_root=self.repo,
                expected_repository="ReedBarrus/DME_Lab",
                packet=packet,
            )["admissible"]
        )

    def test_missing_or_noncomplete_finalization_is_rejected(self) -> None:
        missing_digest = self.packet()
        missing_digest["integrity"].pop("packet_digest")
        self.assertEqual(
            verify_packet_integrity(missing_digest)["status"], CHECKED_ABSENT
        )

        missing_status = self.packet()
        missing_status["integrity"].pop("packet_status")
        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=missing_status,
        )
        self.assertEqual(
            admission["checks"]["packet_status"]["status"], CHECKED_ABSENT
        )
        self.assertFalse(admission["admissible"])

        draft = self.packet()
        draft["integrity"]["packet_status"] = "DRAFT"
        draft["integrity"].pop("packet_digest")
        draft["integrity"]["packet_digest"] = packet_digest(draft)
        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=draft,
        )
        self.assertEqual(
            admission["checks"]["packet_status"]["status"], CHECK_MISMATCH
        )
        self.assertFalse(admission["admissible"])

    def test_changed_head_is_visible_and_not_silently_reused(self) -> None:
        packet = self.packet()
        (self.repo / "other.md").write_text("changed\n", encoding="utf-8")
        git(self.repo, "add", "other.md")
        git(self.repo, "commit", "-m", "advance unrelated source")

        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=packet,
        )
        self.assertFalse(admission["admissible"])
        self.assertEqual(
            admission["checks"]["basis_commit"]["status"], CHECK_MISMATCH
        )
        self.assertFalse(admission["repair_performed"])

    def test_dirty_worktree_rejects_build_and_admission_without_cleanup(self) -> None:
        packet = self.packet()
        dirty = self.repo / "untracked.txt"
        dirty.write_text("preserve me\n", encoding="utf-8")
        before = dirty.read_bytes()

        with self.assertRaisesRegex(ContinuationBuildError, "clean worktree"):
            self.packet(continuation_id="continuation-dirty")
        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=packet,
        )
        self.assertEqual(
            admission["checks"]["worktree_clean"]["status"], CHECK_MISMATCH
        )
        self.assertFalse(admission["admissible"])
        self.assertEqual(dirty.read_bytes(), before)
        self.assertIn("?? untracked.txt", git(self.repo, "status", "--porcelain=v1"))

    def test_changed_cited_source_at_new_commit_exposes_basis_and_blob_mismatch(self) -> None:
        packet = self.packet()
        (self.repo / "source.md").write_text("authoritative beta\n", encoding="utf-8")
        git(self.repo, "add", "source.md")
        git(self.repo, "commit", "-m", "change source")

        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=packet,
        )
        self.assertEqual(
            admission["checks"]["basis_commit"]["status"], CHECK_MISMATCH
        )
        self.assertEqual(
            admission["checks"]["source_manifest"][0]["status"], CHECK_MISMATCH
        )
        self.assertFalse(admission["admissible"])

    def test_unknown_semantic_source_ref_is_rejected_by_builder_and_admission(self) -> None:
        prior = deepcopy(self.prior)
        prior["prior_objective_projection"]["source_refs"] = ["source-9999"]
        with self.assertRaisesRegex(ContinuationContractError, "unknown semantic"):
            self.packet(prior=prior)

        packet = self.packet()
        packet["prior_projected_standing"]["prior_objective_projection"][
            "source_refs"
        ] = ["source-9999"]
        packet = finalize_packet(packet)
        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=packet,
        )
        self.assertEqual(
            admission["checks"]["semantic_source_refs"]["status"], CHECK_MISMATCH
        )
        self.assertFalse(admission["admissible"])

    def test_missing_cited_source_is_checked_absent(self) -> None:
        packet = self.packet()
        git(self.repo, "rm", "source.md")
        git(self.repo, "commit", "-m", "remove source")

        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=packet,
        )
        self.assertEqual(
            admission["checks"]["source_manifest"][0]["status"], CHECKED_ABSENT
        )
        self.assertFalse(admission["admissible"])

    def test_failed_source_observation_is_check_failed_not_absent(self) -> None:
        packet = self.packet()
        real_git = continuation._git

        def fail_source(root: Path, *args: str) -> GitObservation:
            if args and args[0] == "ls-tree":
                return GitObservation(None, b"", b"", "simulated Git observation failure")
            return real_git(root, *args)

        with patch.object(continuation, "_git", side_effect=fail_source):
            admission = admit_packet(
                repo_root=self.repo,
                expected_repository="ReedBarrus/DME_Lab",
                packet=packet,
            )
        source = admission["checks"]["source_manifest"][0]
        self.assertEqual(source["status"], CHECK_FAILED)
        self.assertNotEqual(source["status"], CHECKED_ABSENT)
        self.assertFalse(admission["admissible"])

    def test_generated_at_age_alone_never_changes_admission(self) -> None:
        old = self.packet(
            continuation_id="continuation-old",
            generated_at="1900-01-01T00:00:00Z",
        )
        future = self.packet(
            continuation_id="continuation-future",
            generated_at="2999-01-01T00:00:00Z",
        )
        for packet in (old, future):
            admission = admit_packet(
                repo_root=self.repo,
                expected_repository="ReedBarrus/DME_Lab",
                packet=packet,
            )
            self.assertTrue(admission["admissible"])
            self.assertEqual(
                admission["checks"]["generated_at_age"]["status"], NOT_CHECKED
            )

    def test_construction_admission_and_external_write_do_not_mutate_source_repo(self) -> None:
        before = git(self.repo, "status", "--porcelain=v1", "--untracked-files=all")
        packet = self.packet()
        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=packet,
        )
        target = self.base / "continuation.json"
        write_packet_atomic(packet, target=target, source_worktree=self.repo)
        after = git(self.repo, "status", "--porcelain=v1", "--untracked-files=all")

        self.assertTrue(admission["admissible"])
        self.assertEqual(before, after)
        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), packet)
        self.assertEqual(target.read_text(encoding="utf-8"), canonical_serialize(packet))
        tampered = deepcopy(packet)
        tampered["prior_projected_standing"]["unresolved"][0]["statement"] = "tampered"
        with self.assertRaisesRegex(ContinuationContractError, "invalid integrity"):
            write_packet_atomic(
                tampered,
                target=self.base / "tampered.json",
                source_worktree=self.repo,
            )
        self.assertFalse((self.base / "tampered.json").exists())
        with self.assertRaisesRegex(ContinuationBuildError, "outside"):
            write_packet_atomic(
                packet,
                target=self.repo / "forbidden-packet.json",
                source_worktree=self.repo,
            )
        self.assertFalse((self.repo / "forbidden-packet.json").exists())

    def test_shared_predecessor_does_not_select_a_winner(self) -> None:
        first = self.packet(
            continuation_id="continuation-branch-a",
            predecessor_id="continuation-parent",
        )
        second = self.packet(
            continuation_id="continuation-branch-b",
            predecessor_id="continuation-parent",
        )
        self.assertEqual(first["predecessor_id"], second["predecessor_id"])
        self.assertNotEqual(first["continuation_id"], second["continuation_id"])
        for packet in (first, second):
            self.assertTrue(
                admit_packet(
                    repo_root=self.repo,
                    expected_repository="ReedBarrus/DME_Lab",
                    packet=packet,
                )["admissible"]
            )
        self.assertNotIn("winner", first)
        self.assertNotIn("winner", second)

    def test_builder_preserves_prior_projection_without_promoting_it(self) -> None:
        packet = self.packet()
        self.assertEqual(packet["prior_projected_standing"], self.prior)
        admission = admit_packet(
            repo_root=self.repo,
            expected_repository="ReedBarrus/DME_Lab",
            packet=packet,
        )
        self.assertTrue(admission["current_admission_only"])
        self.assertFalse(admission["prior_projected_standing_promoted"])
        self.assertNotIn("current_standing", packet)

    def test_checked_status_vocabulary_remains_recoverable(self) -> None:
        self.assertEqual(
            {CHECK_MATCH, CHECK_MISMATCH, CHECKED_ABSENT, CHECK_FAILED, NOT_CHECKED},
            {"MATCH", "MISMATCH", "CHECKED_ABSENT", "CHECK_FAILED", "NOT_CHECKED"},
        )

    def test_schema_artifact_matches_runtime_schema_name(self) -> None:
        schema = json.loads(
            Path("schemas/investigator_continuation_v0.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["properties"]["schema"]["const"], continuation.SCHEMA_NAME)
        self.assertEqual(
            schema["properties"]["integrity"]["properties"]["packet_status"]["const"],
            continuation.PACKET_STATUS,
        )


if __name__ == "__main__":
    unittest.main()
