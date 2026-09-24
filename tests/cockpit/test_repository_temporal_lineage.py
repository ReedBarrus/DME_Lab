from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

import src.cockpit.repository_temporal_lineage as temporal_lineage
from src.cockpit.repository_temporal_lineage import (
    WOUND_PATH,
    build_repository_temporal_lineage,
    generate_repository_temporal_lineage,
)


REPOSITORY = "Example/TemporalAtlas"


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repo, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return completed.stdout.strip()


def write(repo: Path, path: str, content: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


class RepositoryTemporalLineageTest(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        git(root, "init")
        git(root, "config", "user.email", "git-author@example.invalid")
        git(root, "config", "user.name", "Git Author Fixture")

        write(root, WOUND_PATH, "one\n")
        write(root, "continuity/cursors/labboib.json", json.dumps({
            "consumer": "labboib", "cursor_state": "POSITIONED",
            "last_seen_event_id": "CE-1", "bootstrap_mode": "FROM_HEAD",
        }))
        git(root, "add", ".")
        git(root, "commit", "-m", "initial frame")

        write(root, WOUND_PATH, "two\n")
        git(root, "add", ".")
        git(root, "commit", "-m", "content transition")

        write(root, "continuity/seats/labboib.json", json.dumps({
            "schema_version": "temporal_seat_manifest_v0",
            "seat_id": "LABBOIB", "consumer_id": "labboib",
            "cursor_ref": "continuity/cursors/labboib.json",
            "trigger": {"state": "UNBOUND"},
            "occupant": {"binding": "UNBOUND"},
            "authority_effect": "NONE_BY_MANIFEST",
            "execution_effect": "NONE_BY_MANIFEST",
        }))
        write(root, "continuity/cursors/labboib.json", json.dumps({
            "consumer": "labboib", "cursor_state": "POSITIONED",
            "last_seen_event_id": "CE-2", "bootstrap_mode": "FROM_HEAD",
        }))
        git(root, "mv", WOUND_PATH, "src/cockpit/observer/renamed_app.mjs")
        git(root, "add", ".")
        git(root, "commit", "-m", "exact rename and explicit seat source")

    def test_frames_and_adjacent_diff_are_deterministic(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            first = build_repository_temporal_lineage(repo, source_ref="HEAD", repository_identity=REPOSITORY)
            second = build_repository_temporal_lineage(repo, source_ref="HEAD", repository_identity=REPOSITORY)
            self.assertEqual(first, second)
            self.assertEqual(first["counts"]["frames"], 3)
            self.assertEqual(first["counts"]["transitions"], 2)
            self.assertEqual(first["frames"][0]["first_parent_commit_sha"], None)
            self.assertEqual(first["transitions"][0]["from_frame_id"], first["frames"][0]["frame_id"])
            self.assertEqual(first["transitions"][0]["to_frame_id"], first["frames"][1]["frame_id"])

    def test_content_change_preserves_path_lineage_but_not_version_identity(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            model = build_repository_temporal_lineage(repo, source_ref="HEAD", repository_identity=REPOSITORY)
            event = next(
                event for event in model["transitions"][0]["events"]
                if event["new_path"] == WOUND_PATH
            )
            self.assertIn("PERSISTED", event["classifications"])
            self.assertIn("CONTENT_CHANGED", event["classifications"])
            self.assertEqual(event["lineage_id_before"], event["lineage_id_after"])
            self.assertNotEqual(event["old_object_sha"], event["new_object_sha"])
            self.assertEqual(event["actor_lineage"], "UNRESOLVED")
            self.assertEqual(event["semantic_lineage"], "UNRESOLVED")

    def test_only_exact_git_rename_carries_identity(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            model = build_repository_temporal_lineage(repo, source_ref="HEAD", repository_identity=REPOSITORY)
            event = next(
                event for event in model["transitions"][1]["events"]
                if event["status"] == "R100"
            )
            self.assertEqual(event["identity_basis"], "EXACT_BLOB_RENAME_R100")
            self.assertIn("PATH_CHANGED", event["classifications"])
            self.assertEqual(event["lineage_id_before"], event["lineage_id_after"])

    def test_seat_and_cursor_sources_are_admitted_without_git_actor_collapse(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            model = build_repository_temporal_lineage(repo, source_ref="HEAD", repository_identity=REPOSITORY)
            kinds = {item["source_kind"] for item in model["actor_source_versions"]}
            self.assertEqual(kinds, {"SEAT_SOURCE", "CURSOR_SOURCE"})
            seat = next(item for item in model["actor_source_versions"] if item["source_kind"] == "SEAT_SOURCE")
            self.assertEqual(seat["payload"]["seat_id"], "LABBOIB")
            self.assertEqual(model["frames"][-1]["git_author"]["standing"], "GIT_METADATA_ONLY")
            self.assertEqual(model["transitions"][-1]["seat_actor"], "UNRESOLVED")
            cursor_event = next(
                event for event in model["transitions"][-1]["events"]
                if event.get("new_path") == "continuity/cursors/labboib.json"
            )
            self.assertEqual(cursor_event["actor_lineage"], "EXPLICIT_CURSOR_TRANSITION")
            self.assertEqual(
                cursor_event["declared_operational_relations"][0]["relation"],
                "CURSOR_ADVANCED_TO",
            )

    def test_wound_replay_retains_challenge_handles_and_unresolved_lineage(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            model = build_repository_temporal_lineage(repo, source_ref="HEAD", repository_identity=REPOSITORY)
            wound = model["wound_replay"]
            self.assertEqual(wound["family"], "PATH_IDENTITY != CONTENT_IDENTITY")
            self.assertGreaterEqual(len(wound["steps"]), 2)
            for step in wound["steps"]:
                self.assertEqual(step["actor_lineage"], "UNRESOLVED")
                self.assertEqual(step["semantic_lineage"], "UNRESOLVED")
                self.assertTrue(all(item["source_handles"] for item in step["distinctions"]))

    def test_raw_diff_falls_back_when_diff_tree_fails_without_detail(self) -> None:
        raw = (
            b":100644 100644 "
            b"1111111111111111111111111111111111111111 "
            b"2222222222222222222222222222222222222222 M\x00"
            b"example.txt\x00"
        )
        with patch.object(
            temporal_lineage,
            "_git",
            side_effect=[
                temporal_lineage.RepositoryTemporalLineageError(
                    "git diff-tree failed rc=1: no stderr/stdout emitted"
                ),
                raw,
            ],
        ) as git_call:
            rows = temporal_lineage._raw_diff(
                Path("."),
                "a" * 40,
                "b" * 40,
            )
        self.assertEqual(rows[0]["status"], "M")
        self.assertEqual(rows[0]["old_path"], "example.txt")
        self.assertEqual(rows[0]["new_path"], "example.txt")
        self.assertEqual(git_call.call_count, 2)
        self.assertEqual(git_call.call_args_list[1].args[1], "diff")

    def test_temporal_git_subprocess_uses_no_window_flag_on_windows(self) -> None:
        completed = Mock(returncode=0, stdout=b"abc\n", stderr=b"")
        with (
            patch("src.cockpit.repository_temporal_lineage.__import__") as importer,
            patch.object(
                temporal_lineage.subprocess,
                "CREATE_NO_WINDOW",
                0x08000000,
                create=True,
            ),
            patch(
                "src.cockpit.repository_temporal_lineage.subprocess.run",
                return_value=completed,
            ) as run,
        ):
            fake_os = Mock()
            fake_os.name = "nt"
            importer.return_value = fake_os
            temporal_lineage._git(Path("."), "rev-parse", "HEAD")
        self.assertEqual(run.call_args.kwargs["creationflags"], 0x08000000)

    def test_generation_is_atomic_and_read_only(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            self.make_repo(repo)
            output = Path(temporary) / "generated" / "temporal.json"
            before = git(repo, "status", "--short")
            model = generate_repository_temporal_lineage(
                repo=repo, source_ref="HEAD", repository_identity=REPOSITORY, output=output,
            )
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), model)
            self.assertEqual(git(repo, "status", "--short"), before)
            self.assertFalse(output.with_name("temporal.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
