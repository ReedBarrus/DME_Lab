from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Sequence


DEFAULT_OUTPUT = Path("generated/repository_address_fabric.json")
OBJECT_TYPE = "REPOSITORY_ADDRESS_FABRIC_V0"
EXISTENCE_STANDING = "EXISTS_AT_SOURCE_COMMIT"
SEMANTIC_STANDING = "UNINTERPRETED"


class RepositoryAddressFabricError(RuntimeError):
    pass


def _git(repo: Path, *args: str, check: bool = True) -> bytes:
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={repo}", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryAddressFabricError(
            f"git {' '.join(args)} failed: {detail or 'unknown git failure'}"
        )
    return completed.stdout


def infer_repository_identity(repo: str | Path) -> str:
    root = Path(repo).resolve()
    remote = _git(root, "remote", "get-url", "origin").decode("utf-8").strip()
    patterns = (
        r"^https?://github\.com/(?P<identity>[^/]+/[^/]+?)(?:\.git)?$",
        r"^git@github\.com:(?P<identity>[^/]+/[^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/(?P<identity>[^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.match(pattern, remote)
        if match:
            return match.group("identity")
    raise RepositoryAddressFabricError(
        "repository identity is not derivable from the origin remote; "
        "supply --repository-identity explicitly"
    )


def canonical_address(address: dict[str, Any]) -> str:
    return json.dumps(address, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _identity(prefix: str, address: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_address(address).encode("utf-8")).hexdigest()
    return f"{prefix}:sha256:{digest}"


def _address(
    repository: str,
    commit: str,
    path: str,
    object_kind: str,
    *,
    git_blob_sha: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "substrate": "repo",
        "repository": repository,
        "commit": commit,
        "path": path,
        "object_kind": object_kind,
    }
    if git_blob_sha is not None:
        value["git_blob_sha"] = git_blob_sha
    return value


def _path_identity(repository: str, path: str, object_kind: str) -> dict[str, str]:
    return {
        "substrate": "repo_path",
        "repository": repository,
        "path": path,
        "object_kind": object_kind,
    }


def _parent_path(path: str) -> str:
    parent = str(PurePosixPath(path).parent)
    return "" if parent == "." else parent


def _branch_coordinate(repo: Path, source_ref: str) -> str | None:
    if source_ref != "HEAD":
        if source_ref.startswith("refs/heads/"):
            return source_ref.removeprefix("refs/heads/")
        return None
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={repo}", "symbolic-ref", "--quiet", "--short", "HEAD"],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.decode("utf-8").strip() or None


def _git_object_contents(repo: Path, identities: list[str]) -> dict[str, bytes]:
    unique = list(dict.fromkeys(identities))
    if not unique:
        return {}
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={repo}", "cat-file", "--batch"],
        cwd=repo,
        input=("\n".join(unique) + "\n").encode("ascii"),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryAddressFabricError(
            f"git cat-file --batch failed: {detail or 'unknown git failure'}"
        )

    contents: dict[str, bytes] = {}
    offset = 0
    for requested in unique:
        header_end = completed.stdout.find(b"\n", offset)
        if header_end < 0:
            raise RepositoryAddressFabricError("truncated git cat-file batch header")
        header = completed.stdout[offset:header_end].decode("ascii").split(" ")
        if len(header) != 3 or header[1] == "missing":
            raise RepositoryAddressFabricError(
                f"git object {requested} was unavailable during projection"
            )
        returned_identity, _git_type, raw_size = header
        size = int(raw_size)
        start = header_end + 1
        end = start + size
        if end >= len(completed.stdout) or completed.stdout[end : end + 1] != b"\n":
            raise RepositoryAddressFabricError("truncated git cat-file batch content")
        contents[returned_identity] = completed.stdout[start:end]
        offset = end + 1
    return contents


def _relation(
    source_id: str,
    relation: str,
    *,
    target_id: str | None = None,
    target_address: dict[str, Any] | None = None,
) -> dict[str, Any]:
    material = {
        "source_id": source_id,
        "relation": relation,
        "target_id": target_id,
        "target_address": target_address,
    }
    return {
        "relation_id": _identity("relation", material),
        **material,
        "derivation": "GIT_MECHANICAL",
    }


def build_repository_address_fabric(
    repo: str | Path,
    *,
    source_ref: str,
    repository_identity: str | None = None,
) -> dict[str, Any]:
    root = Path(repo).resolve()
    repository = repository_identity or infer_repository_identity(root)
    commit = _git(root, "rev-parse", f"{source_ref}^{{commit}}").decode("ascii").strip()
    branch = _branch_coordinate(root, source_ref)
    tree_rows = _git(root, "ls-tree", "-r", "-t", "-z", "--full-tree", commit)

    repository_address = _address(repository, commit, "", "repository")
    repository_id = _identity("repository", repository_address)
    repository_object = {
        "object_id": repository_id,
        "object_kind": "repository",
        "repository_identity": repository,
        "source_commit": commit,
        "source_ref": source_ref,
        "source_branch": branch,
        "path": "",
        "parent_path": None,
        "path_identity": _path_identity(repository, "", "repository"),
        "content_identity": None,
        "git_blob_identity": None,
        "git_tree_identity": None,
        "existence_standing": EXISTENCE_STANDING,
        "semantic_standing": SEMANTIC_STANDING,
        "typed_projections": [],
        "address": repository_address,
    }

    objects: list[dict[str, Any]] = [repository_object]
    relations: list[dict[str, Any]] = []
    container_by_path: dict[str, str] = {"": repository_id}
    file_by_path: dict[str, str] = {}
    entries: list[tuple[str, str, str, str]] = []

    for raw_row in tree_rows.split(b"\0"):
        if not raw_row:
            continue
        metadata, raw_path = raw_row.split(b"\t", 1)
        mode, git_type, git_identity = metadata.decode("ascii").split(" ")
        try:
            path = raw_path.decode("utf-8")
        except UnicodeDecodeError as error:
            raise RepositoryAddressFabricError(
                "V0 requires repository paths to be valid UTF-8"
            ) from error
        entries.append((path, mode, git_type, git_identity))

    entries.sort(key=lambda row: (row[0].count("/"), row[0], row[2] != "tree"))
    object_contents = _git_object_contents(
        root,
        [git_identity for _path, _mode, git_type, git_identity in entries if git_type != "tree"],
    )

    for path, mode, git_type, git_identity in entries:
        parent_path = _parent_path(path)
        if git_type == "tree":
            address = _address(repository, commit, path, "directory")
            object_id = _identity("directory", address)
            item = {
                "object_id": object_id,
                "object_kind": "directory",
                "repository_identity": repository,
                "source_commit": commit,
                "source_ref": source_ref,
                "source_branch": branch,
                "path": path,
                "parent_path": parent_path,
                "path_identity": _path_identity(repository, path, "directory"),
                "content_identity": None,
                "git_blob_identity": None,
                "git_tree_identity": git_identity,
                "git_mode": mode,
                "git_object_type": git_type,
                "existence_standing": EXISTENCE_STANDING,
                "semantic_standing": SEMANTIC_STANDING,
                "typed_projections": [],
                "address": address,
            }
            objects.append(item)
            container_by_path[path] = object_id
            relations.append(
                _relation(container_by_path[parent_path], "CONTAINS", target_id=object_id)
            )
            continue

        address = _address(repository, commit, path, "file")
        file_id = _identity("file", address)
        file_object = {
            "object_id": file_id,
            "object_kind": "file",
            "repository_identity": repository,
            "source_commit": commit,
            "source_ref": source_ref,
            "source_branch": branch,
            "path": path,
            "parent_path": parent_path,
            "path_identity": _path_identity(repository, path, "file"),
            "content_identity": None,
            "git_blob_identity": None,
            "git_tree_identity": None,
            "git_mode": mode,
            "git_object_type": git_type,
            "existence_standing": EXISTENCE_STANDING,
            "semantic_standing": SEMANTIC_STANDING,
            "typed_projections": [],
            "address": address,
        }
        objects.append(file_object)
        file_by_path[path] = file_id
        relations.append(
            _relation(container_by_path[parent_path], "CONTAINS", target_id=file_id)
        )

        content_bytes = object_contents[git_identity]
        content_sha256 = hashlib.sha256(content_bytes).hexdigest()
        version_address = _address(
            repository,
            commit,
            path,
            "file_version",
            git_blob_sha=git_identity if git_type == "blob" else None,
        )
        version_id = _identity("file-version", version_address)
        version_object = {
            "object_id": version_id,
            "object_kind": "file_version",
            "repository_identity": repository,
            "source_commit": commit,
            "source_ref": source_ref,
            "source_branch": branch,
            "path": path,
            "parent_path": parent_path,
            "path_identity": _path_identity(repository, path, "file"),
            "content_identity": f"sha256:{content_sha256}",
            "git_blob_identity": git_identity if git_type == "blob" else None,
            "git_tree_identity": None,
            "git_mode": mode,
            "git_object_type": git_type,
            "existence_standing": EXISTENCE_STANDING,
            "semantic_standing": SEMANTIC_STANDING,
            "typed_projections": [],
            "address": version_address,
        }
        objects.append(version_object)
        relations.extend(
            [
                _relation(file_id, "HAS_VERSION", target_id=version_id),
                _relation(
                    version_id,
                    "MATERIALIZED_AT",
                    target_address={
                        "substrate": "git",
                        "repository": repository,
                        "commit": commit,
                        "object_kind": "commit",
                    },
                ),
                _relation(
                    version_id,
                    "HAS_CONTENT_IDENTITY",
                    target_address={
                        "substrate": "hash",
                        "algorithm": "sha256",
                        "digest": content_sha256,
                        "object_kind": "content_identity",
                    },
                ),
            ]
        )

    kind_order = {"repository": 0, "directory": 1, "file": 2, "file_version": 3}
    objects.sort(
        key=lambda item: (
            item["path"],
            kind_order[item["object_kind"]],
            item["object_id"],
        )
    )
    relations.sort(key=lambda item: item["relation_id"])

    counts = {
        kind: sum(1 for item in objects if item["object_kind"] == kind)
        for kind in kind_order
    }
    return {
        "object_type": OBJECT_TYPE,
        "projection_standing": "DERIVED_READ_ONLY",
        "repository_identity": repository,
        "requested_ref": source_ref,
        "source_branch": branch,
        "source_commit": commit,
        "semantic_default": SEMANTIC_STANDING,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "objects": objects,
        "relations": relations,
        "counts": counts,
        "claim_ceiling": (
            "Git mechanically establishes object existence, containment, path, version, "
            "blob, and content coordinates at the exact source commit. Semantic role, "
            "runtime consequence, authority, causality, and dependency remain unestablished."
        ),
    }


def generate_repository_address_fabric(
    *,
    repo: str | Path,
    source_ref: str,
    output: str | Path,
    repository_identity: str | None = None,
) -> dict[str, Any]:
    output_path = Path(output)
    temporary_path = output_path.with_name(output_path.name + ".tmp")
    output_path.unlink(missing_ok=True)
    temporary_path.unlink(missing_ok=True)
    model = build_repository_address_fabric(
        repo,
        source_ref=source_ref,
        repository_identity=repository_identity,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        temporary_path.write_text(
            json.dumps(model, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(output_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        raise
    return model


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the commit-bound read-only repository address fabric V0."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--repository-identity", default=None)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    model = generate_repository_address_fabric(
        repo=args.repo,
        source_ref=args.source_ref,
        repository_identity=args.repository_identity,
        output=args.output,
    )
    print(
        json.dumps(
            {
                "output": str(Path(args.output)),
                "repository_identity": model["repository_identity"],
                "source_commit": model["source_commit"],
                "source_branch": model["source_branch"],
                "counts": model["counts"],
                "authority_effect": model["authority_effect"],
                "execution_effect": model["execution_effect"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
