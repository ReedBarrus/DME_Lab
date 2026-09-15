# Basis Report v0

**Status:** IMPLEMENTED / BOUNDED MECHANICAL OPERATOR
**Implementation basis:** `c2502f6a7a7c81e7169ed86f14328e52121bc9c3`
**Scientific standing:** NONE
**Semantic authority:** NONE
**Integration / repair authority:** NONE

## Purpose

`basis_report_v0` compresses the recurring changed-world observation procedure
into one deterministic report. It compares one local `HEAD` with one declared
remote-tracking branch and preserves worktree state separately from history
relation.

The operator accepts:

```text
repository_root
remote
branch
fetch: true | false
```

When `fetch` is true, it performs one declared fetch into
`refs/remotes/<remote>/<branch>`. When false, it performs no remote contact.

## Result contract

The returned `basis_report_v0` object contains:

```text
schema
request { repository_root, remote, branch, fetch }
local_head
remote_head
current_branch
worktree_state {
  status
  tracked_changes
  untracked_changes
  entries
}
relation
fetch_attempted
fetch_result { status, returncode, stdout, stderr, failure }
observation_failures[]
mechanical_basis_only: true
integration_performed: false
```

Relation values are:

```text
SYNCHRONIZED
LOCAL_BEHIND
LOCAL_AHEAD
DIVERGED
REMOTE_REF_ABSENT
CHECK_FAILED
```

Fetch status remains separately recoverable as `NOT_REQUESTED`, `SUCCEEDED`,
or `FAILED`. A failed requested fetch forces `CHECK_FAILED`; it does not permit
a stale remote-tracking ref to masquerade as a current remote observation.

## Preserved boundaries

```text
clean worktree != synchronized branch
local HEAD != remote-tracking HEAD
fetched != integrated
tracked change != untracked change
observation failure != remote-ref absence
mechanical basis != semantic standing
```

The operator never pulls, merges, rebases, checks out, switches, resets,
stashes, cleans, commits, pushes, selects authority, or infers scientific
standing. Fetch may update only the explicitly named remote-tracking ref.

## Deterministic evidence

Focused `basis_report_v0` tests passed 10/10. They cover synchronized, behind,
ahead, diverged, dirty, absent-ref, and failed-fetch states; fetch suppression;
exactly one requested fetch; separate tracked/untracked evidence; and unchanged
worktree bytes, local `HEAD`, and current branch.

The full Python suite passed 741/741. Cockpit observer tests passed 39/39.
Python compilation, JavaScript syntax checking, decision-index completeness and
link checks, and `git diff --check` also passed.

## Bounded standing

The repeated mechanical observation is compressed. No automatic fast-forward,
repair, continuation admission, model invocation, agent selection, routing,
scheduling, validation framework, or result-packaging authority is introduced.

The continuation cleanup that motivated this operator does not establish
continuation efficiency or reconstruction displacement as a mechanism.
