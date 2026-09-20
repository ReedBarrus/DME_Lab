# Branch Registry / Retention Policy v0

## Purpose

Reduce Git ref sprawl without deleting unique scientific or operational evidence.

The governing distinction is:

```text
DURABLE_REGISTERED_REF
!=
TRAILING_CACHE_REF
```

with two supporting non-collapses:

```text
COMMIT HISTORY
!=
BRANCH NAME

EVIDENCE RETENTION
!=
REF SPRAWL
```

A branch name is retained only when it serves a current durable navigation purpose. Historical commits may remain reachable through another retained ref without preserving every intermediate branch label.

## Durable set

The exact durable set is defined by `BRANCH_REGISTRY_v0.json`.

Target:

```text
DURABLE REGISTERED REFS:
13
```

Classes:

```text
PRIMARY
ACTIVE_FRONTIER
OPEN_PR_DURABLE
EVIDENCE_ANCHOR
```

Registration does not establish scientific standing, merge authority, execution authority, or process activeness.

## Transient work refs

A branch may exist temporarily without becoming a durable registered ref when it is:

```text
an open PR head
or
an explicitly active maintenance branch
```

Such a ref is retained only for the lifetime of that work.

After merge/closure, if its tip is reachable from a durable registered ref:

```text
TRANSIENT WORK REF
→ deletion eligible
```

The present `branch-registry-v0` branch is itself transient and should disappear after this policy lands.

## Trailing cache

After the bootstrap cleanup reaches the 13-ref durable set, steady-state hygiene may retain a bounded trailing cache:

```text
MAX CACHE REFS:
5

TTL:
72 hours
```

A cache ref must satisfy all of:

```text
not durable registered
not protected
not an open PR head
tip reachable from at least one durable registered ref
```

The cache exists only for short-term human convenience.

```text
CACHE PRESENCE
!=
DURABLE REGISTRATION
```

If the cache exceeds its hard cap, delete the oldest eligible cache refs first.

## Unique-commit safety gate

Any unregistered branch whose tip is not reachable from a durable registered ref is:

```text
ORPHAN_UNIQUE
```

and must not be deleted.

Disposition:

```text
ORPHAN_UNIQUE
→ STOP
→ REGISTER OR CONSERVE ITS UNIQUE COMMITS
→ RECHECK
```

No age, naming pattern, conversational claim, or apparent obsolescence overrides this gate.

## Bootstrap cleanup

Observed before creating this maintenance branch:

```text
LIVE BRANCHES:
59

DURABLE TARGET:
13

NON-DURABLE BRANCH NAMES
WHOSE COMMITS ARE ALREADY REACHABLE
FROM THE 13 DURABLE REFS:
46
```

The first cleanup intentionally disables the trailing cache so the repository reaches the clean baseline.

The following 46 refs are bootstrap deletion candidates after this registry is admitted and after a final open-PR/protection/reachability check:

```text
addressing-001-apparatus
addressing-001-held-out-realization-001
atlas-five-node-local-v0
atlas-route-selection-execution-evidence-harness-v0
atlas-route-selection-pressure-v0
atlas-route-selection-realization-v1
atlas-route-selection-recovery-contract-v0
atlas-route-selection-recovery-realization-v0
atlas-route-selection-scientific-adjudication-v0
authorization-to-active-001-candidate
carrier-swap-probation-cs001
checkpoint-authorization-to-active-001
cockpit-desktop-launcher-v0
cockpit-test-fixture-parent-repair
cockpit-windows-child-process-containment
command-authority-flattening-observation-v0
commander-experimental-preflight-v0
concordance-cockpit-edge-source-standing-candidate-v0
concordance-cockpit-edge-source-standing-held-out-contract-v1
concordance-cockpit-v0-edge-entitlement-candidate
concordance-cockpit-v0-edge-entitlement-pressure
concordance-cockpit-v0-primitives
conductor-role-handoff-001-candidate
conductor-role-handoff-001-commander-evidence
counterfeit-warrant-001-execution-envelope
counterfeit-warrant-001-realization
crash-salvage-2026-09-06
dme-warranted-delta-001-contract-candidate-v2
dme-warranted-delta-001-contract-candidate-v5
evidence-authority-boundary-incident-2026-09-18
execution-stop-latch-001
handling-001-bounded-apparatus
handling-001-held-out-contract-v0
handling-001-held-out-realization-v0
handling-001-recovery-reissue-v1
integrate-continuity-v0
lab-conductor-v0
lab-ops-registry-v0
live-four-root-migration-v0
lp001-close-administration-invalidity-v0
lp001-freeze-scorer-apparatus-v0
lp001-repair-round-2
lp001-separate-bundle-invalidity-v0
method-capability-withdrawal-pressure-v0
pulse-ack-001-proposed-ack
workshop-authority-gate-001-apparatus
```

The newly observed:

```text
concordance-cockpit-edge-source-standing-held-out-contract-v1
```

points at the prior fractured held-out head and is already an ancestor of the corrected retained `...held-out-contract-v0` frontier. It therefore illustrates:

```text
RECENT BRANCH
!=
UNIQUE EVIDENCE
```

## Mechanical deletion predicate

A branch may be deleted only when:

```text
NOT DURABLE_REGISTERED
AND
NOT PROTECTED
AND
NOT OPEN_PR_HEAD
AND
TIP_REACHABLE_FROM_DURABLE_REF
AND
OUTSIDE_ACTIVE_TRAILING_CACHE
```

Otherwise:

```text
DO NOT DELETE
```

## Intended automation

`tools/branch_registry.py` is the bounded operator tool for this policy.

Default behavior is dry-run audit.

Destructive application requires an explicit flag and refuses to proceed when the open-PR check cannot be performed.

The tool must never infer scientific standing or choose which unique evidence deserves conservation.
