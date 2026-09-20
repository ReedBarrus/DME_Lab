#!/usr/bin/env python3
"""Bounded branch-registry hygiene tool for DME_Lab.

Default: audit only.
Destructive remote deletion requires --apply and successful GitHub safety checks.

This tool manages Git refs only. It does not infer scientific standing,
execution authority, process activeness, or evidentiary importance.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Iterable


DEFAULT_REGISTRY = Path("docs/operations/BRANCH_REGISTRY_v0.json")
DEFAULT_REMOTE = "origin"


class BranchRegistryError(RuntimeError):
    pass


@dataclass(frozen=True)
class BranchInfo:
    name: str
    sha: str
    commit_time: int


@dataclass(frozen=True)
class Classification:
    name: str
    state: str
    reason: str
    reachable_from: tuple[str, ...] = ()


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        list(args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise BranchRegistryError(
            f"command failed ({proc.returncode}): {' '.join(args)}\n"
            f"{proc.stderr.strip()}"
        )
    return proc


def load_registry(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "branch_registry_v0":
        raise BranchRegistryError("unsupported or missing branch_registry_v0 schema")
    refs = data.get("durable_registered_refs")
    if not isinstance(refs, list) or not refs:
        raise BranchRegistryError("durable_registered_refs must be a non-empty list")
    names = [x.get("name") for x in refs]
    if len(names) != len(set(names)) or any(not isinstance(x, str) or not x for x in names):
        raise BranchRegistryError("durable branch names must be unique non-empty strings")
    return data


def git_remote_branches(remote: str) -> dict[str, BranchInfo]:
    fmt = "%(refname:short)\t%(objectname)\t%(committerdate:unix)"
    proc = run("git", "for-each-ref", f"--format={fmt}", f"refs/remotes/{remote}")
    result: dict[str, BranchInfo] = {}
    prefix = remote + "/"
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        ref, sha, ts = line.split("\t", 2)
        if ref == f"{remote}/HEAD" or not ref.startswith(prefix):
            continue
        name = ref[len(prefix):]
        result[name] = BranchInfo(name=name, sha=sha, commit_time=int(ts))
    return result


def is_ancestor(remote: str, candidate: str, durable: str) -> bool:
    proc = run(
        "git",
        "merge-base",
        "--is-ancestor",
        f"{remote}/{candidate}",
        f"{remote}/{durable}",
        check=False,
    )
    if proc.returncode == 0:
        return True
    if proc.returncode == 1:
        return False
    raise BranchRegistryError(
        f"ancestry check failed for {candidate} -> {durable}: {proc.stderr.strip()}"
    )


def github_safety(repo: str) -> tuple[set[str], set[str]]:
    if shutil.which("gh") is None:
        raise BranchRegistryError(
            "GitHub CLI 'gh' is required for destructive mode safety checks"
        )

    prs = run(
        "gh", "pr", "list",
        "--repo", repo,
        "--state", "open",
        "--limit", "100",
        "--json", "headRefName",
    )
    open_heads = {
        row["headRefName"]
        for row in json.loads(prs.stdout)
        if row.get("headRefName")
    }

    branches = run(
        "gh", "api", "--paginate",
        f"repos/{repo}/branches?per_page=100",
    )
    protected = {
        row["name"]
        for row in json.loads(branches.stdout)
        if row.get("protected") is True
    }
    return open_heads, protected


def classify(
    branches: dict[str, BranchInfo],
    durable_names: set[str],
    reachability: dict[str, tuple[str, ...]],
    *,
    open_pr_heads: set[str],
    protected: set[str],
    mode: str,
    cache_max_refs: int,
    cache_ttl_hours: int,
    now: int,
) -> list[Classification]:
    eligible_cache: list[BranchInfo] = []
    out: list[Classification] = []

    for name, info in branches.items():
        if name in durable_names:
            out.append(Classification(name, "RETAIN_DURABLE", "registered durable ref"))
            continue
        if name in protected:
            out.append(Classification(name, "RETAIN_PROTECTED", "remote branch is protected"))
            continue
        if name in open_pr_heads:
            out.append(Classification(name, "RETAIN_TRANSIENT", "open pull-request head"))
            continue

        reachable = reachability.get(name, ())
        if not reachable:
            out.append(
                Classification(
                    name,
                    "RETAIN_ORPHAN_UNIQUE",
                    "tip is not reachable from any durable registered ref",
                )
            )
            continue

        if mode == "steady":
            eligible_cache.append(info)
        else:
            out.append(
                Classification(
                    name,
                    "DELETE_ELIGIBLE",
                    "reachable from durable ref; bootstrap cache disabled",
                    reachable,
                )
            )

    if mode == "steady":
        ttl_seconds = cache_ttl_hours * 3600
        newest = sorted(eligible_cache, key=lambda b: b.commit_time, reverse=True)
        count_cache = {b.name for b in newest[:cache_max_refs]}
        for info in newest:
            age_ok = (now - info.commit_time) <= ttl_seconds
            if info.name in count_cache and age_ok:
                out.append(
                    Classification(
                        info.name,
                        "RETAIN_CACHE",
                        "bounded trailing cache",
                        reachability[info.name],
                    )
                )
            else:
                out.append(
                    Classification(
                        info.name,
                        "DELETE_ELIGIBLE",
                        "reachable from durable ref and outside bounded cache",
                        reachability[info.name],
                    )
                )

    return sorted(out, key=lambda x: (x.state, x.name))


def build_reachability(
    branches: dict[str, BranchInfo],
    durable_names: set[str],
    remote: str,
) -> dict[str, tuple[str, ...]]:
    result: dict[str, tuple[str, ...]] = {}
    for name in branches:
        if name in durable_names:
            continue
        carriers = tuple(
            durable
            for durable in sorted(durable_names)
            if durable in branches and is_ancestor(remote, name, durable)
        )
        result[name] = carriers
    return result


def print_plan(items: Iterable[Classification]) -> None:
    counts: dict[str, int] = {}
    for item in items:
        counts[item.state] = counts.get(item.state, 0) + 1
        carriers = ",".join(item.reachable_from) if item.reachable_from else "-"
        print(f"{item.state:22} {item.name:64} via={carriers}")
    print()
    for state in sorted(counts):
        print(f"{state}: {counts[state]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--repo", default="ReedBarrus/DME_Lab")
    parser.add_argument("--mode", choices=("bootstrap", "steady"), default="bootstrap")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--no-fetch", action="store_true")
    args = parser.parse_args(argv)

    registry = load_registry(args.registry)
    durable_names = {
        row["name"] for row in registry["durable_registered_refs"]
    }

    if not args.no_fetch:
        run("git", "fetch", "--prune", args.remote)

    branches = git_remote_branches(args.remote)
    missing = sorted(durable_names - set(branches))
    if missing:
        raise BranchRegistryError(
            "registered durable refs missing from remote: " + ", ".join(missing)
        )

    if args.apply:
        open_pr_heads, protected = github_safety(args.repo)
    else:
        # Dry run is non-destructive. It may classify an unknown open PR head as
        # deletion-eligible, so the output is only a candidate plan.
        try:
            open_pr_heads, protected = github_safety(args.repo)
        except BranchRegistryError:
            open_pr_heads, protected = set(), set()
            print(
                "WARNING: GitHub PR/protection safety data unavailable; "
                "dry-run deletion labels are provisional.",
                file=sys.stderr,
            )

    reachability = build_reachability(branches, durable_names, args.remote)

    cache = registry["trailing_cache"]
    items = classify(
        branches,
        durable_names,
        reachability,
        open_pr_heads=open_pr_heads,
        protected=protected,
        mode=args.mode,
        cache_max_refs=int(cache["max_refs"]),
        cache_ttl_hours=int(cache["ttl_hours"]),
        now=int(time.time()),
    )

    print_plan(items)

    orphaned = [x for x in items if x.state == "RETAIN_ORPHAN_UNIQUE"]
    deletions = [x.name for x in items if x.state == "DELETE_ELIGIBLE"]

    if args.apply:
        if orphaned:
            raise BranchRegistryError(
                "destructive mode blocked: ORPHAN_UNIQUE refs exist: "
                + ", ".join(x.name for x in orphaned)
            )
        for name in deletions:
            run("git", "push", args.remote, "--delete", name)
            print(f"DELETED {name}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BranchRegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
