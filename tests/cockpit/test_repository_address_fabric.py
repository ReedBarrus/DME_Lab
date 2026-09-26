from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from src.cockpit.repository_address_fabric import (
    build_repository_address_fabric,
    canonical_address,
    generate_repository_address_fabric,
)


REPOSITORY = "Example/AddressFabric"


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


class RepositoryAddressFabricTest(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        git(root, "init")
        git(root, "config", "user.email", "fabric@example.invalid")
        git(root, "config", "user.name", "Fabric Fixture")

    def object_for(self, model: dict, kind: str, path: str) -> dict:
        return next(
            item
            for item in model["objects"]
            if item["object_kind"] == kind and item["path"] == path
        )

    def test_pressure_a_unknown_file_is_visible_addressable_and_uninterpreted(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            write(repo / "opaque" / "mystery.zqx", b"no adapter\n")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "add opaque specimen")

            model = build_repository_address_fabric(
                repo,
                source_ref="HEAD",
                repository_identity=REPOSITORY,
            )
            file_object = self.object_for(model, "file", "opaque/mystery.zqx")
            version = self.object_for(model, "file_version", "opaque/mystery.zqx")

            self.assertEqual(file_object["existence_standing"], "EXISTS_AT_SOURCE_COMMIT")
            self.assertEqual(file_object["semantic_standing"], "UNINTERPRETED")
            self.assertEqual(file_object["typed_projections"], [])
            self.assertEqual(version["semantic_standing"], "UNINTERPRETED")
            self.assertEqual(file_object["address"]["path"], "opaque/mystery.zqx")

    def test_pressure_b_path_identity_does_not_collapse_identical_content(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            write(repo / "a" / "same.bin", b"identical")
            write(repo / "b" / "same.bin", b"identical")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "same bytes different paths")
            model = build_repository_address_fabric(
                repo,
                source_ref="HEAD",
                repository_identity=REPOSITORY,
            )

            left_file = self.object_for(model, "file", "a/same.bin")
            right_file = self.object_for(model, "file", "b/same.bin")
            left_version = self.object_for(model, "file_version", "a/same.bin")
            right_version = self.object_for(model, "file_version", "b/same.bin")

            self.assertNotEqual(left_file["object_id"], right_file["object_id"])
            self.assertNotEqual(left_version["object_id"], right_version["object_id"])
            self.assertEqual(left_version["content_identity"], right_version["content_identity"])
            self.assertEqual(left_version["git_blob_identity"], right_version["git_blob_identity"])

    def test_pressure_c_same_path_across_commits_has_stable_path_and_distinct_versions(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            target = repo / "changing.txt"
            write(target, b"version one\n")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "version one")
            first_commit = git(repo, "rev-parse", "HEAD")
            first = build_repository_address_fabric(
                repo,
                source_ref=first_commit,
                repository_identity=REPOSITORY,
            )

            write(target, b"version two\n")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "version two")
            second = build_repository_address_fabric(
                repo,
                source_ref="HEAD",
                repository_identity=REPOSITORY,
            )
            first_file = self.object_for(first, "file", "changing.txt")
            second_file = self.object_for(second, "file", "changing.txt")
            first_version = self.object_for(first, "file_version", "changing.txt")
            second_version = self.object_for(second, "file_version", "changing.txt")

            self.assertEqual(first_file["path_identity"], second_file["path_identity"])
            self.assertNotEqual(first_file["address"], second_file["address"])
            self.assertNotEqual(first_version["object_id"], second_version["object_id"])
            self.assertNotEqual(first_version["content_identity"], second_version["content_identity"])

    def test_pressure_d_same_address_can_be_shared_without_authority_or_execution(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            write(repo / "shared.txt", b"shared address\n")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "shared address")
            model = build_repository_address_fabric(
                repo,
                source_ref="HEAD",
                repository_identity=REPOSITORY,
            )
            address = self.object_for(model, "file", "shared.txt")["address"]
            operator_reference = json.loads(canonical_address(address))
            seat_reference = json.loads(canonical_address(address))

            self.assertEqual(operator_reference, seat_reference)
            self.assertNotIn("authority", address)
            self.assertNotIn("execution", address)
            self.assertEqual(model["authority_effect"], "NONE")
            self.assertEqual(model["execution_effect"], "NONE")

    def test_projection_reads_exact_commit_not_uncommitted_worktree(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.make_repo(repo)
            write(repo / "committed.txt", b"retained\n")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "committed basis")
            write(repo / "uncommitted.txt", b"must stay outside projection\n")

            model = build_repository_address_fabric(
                repo,
                source_ref="HEAD",
                repository_identity=REPOSITORY,
            )
            paths = {item["path"] for item in model["objects"]}
            self.assertIn("committed.txt", paths)
            self.assertNotIn("uncommitted.txt", paths)

    def test_generation_writes_one_atomic_derived_projection(self) -> None:
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            self.make_repo(repo)
            write(repo / "one.txt", b"one\n")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "one")
            output = Path(temporary) / "generated" / "fabric.json"

            model = generate_repository_address_fabric(
                repo=repo,
                source_ref="HEAD",
                repository_identity=REPOSITORY,
                output=output,
            )
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), model)
            self.assertFalse(output.with_name("fabric.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
