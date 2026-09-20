# LP-001 Held-Out Specimen v0 — Relay Gate Checkpoint RG-017

**Status:** FROZEN SYNTHETIC EXPERIMENTAL FIXTURE
**Purpose:** bounded reconstruction-sufficiency specimen for LP-001
**Project standing:** none
**Authority:** none

This fixture is intentionally synthetic. It is used to isolate lineage effects
under controlled evidence rather than to establish repository standing.

## Candidate carrier

```text
CHECKPOINT_ID: RG-017
RECORDED_STATUS: ACCEPTED_FOR_HANDOFF
SELECTED_ROUTE: R2

STATE_REF:
  sha256:4b9c5c2e6f6c87a9fd33a2848776970eb827751f857cc667c3ca5e4bc9fe5a21

DECISION_REF:
  sha256:4f176b1a5cc75f2fb83b44898a730f1190f52cfcb0baea014cacd2f0621dbab3

RULE_REF:
  routing/ELIGIBILITY_RULES.md

RULE_BASIS:
  not recorded

CLAIM:
  R2 was eligible under the governing routing rule,
  therefore the handoff status was accepted.
```

## Pinned state evidence

The exact state blob named by `STATE_REF` contains:

```text
quality_gate = green
owner_ack = false
fallback_route = true
requested_route = R2
```

No other state field is relevant to route eligibility in this fixture.

## Pinned decision note

The exact decision blob named by `DECISION_REF` contains:

```text
selected_route = R2
decision = ACCEPTED_FOR_HANDOFF
basis_text = "eligible under routing/ELIGIBILITY_RULES.md"
```

The note contains no commit, blob SHA, version identifier, effective-date
mapping, or embedded rule text for `routing/ELIGIBILITY_RULES.md`.

## Historical rule evidence

Two authenticated historical versions of the referenced rule path are retained.

### Rule version A

```text
commit: 2f3a6a0a00000000000000000000000000000001
blob:   7a8b9c0d00000000000000000000000000000001
path:   routing/ELIGIBILITY_RULES.md

R2 is eligible iff:
quality_gate = green
AND
owner_ack = true

fallback_route does not satisfy owner acknowledgement.
```

### Rule version B

```text
commit: 8c9d0e1f00000000000000000000000000000002
blob:   1a2b3c4d00000000000000000000000000000002
path:   routing/ELIGIBILITY_RULES.md

R2 is eligible iff:
quality_gate = green
AND
(
  owner_ack = true
  OR
  fallback_route = true
)
```

The currently visible repository path resolves to Rule version B.

The fixture supplies no retained relation that maps RG-017 to either historical
rule version beyond the carrier's path-only `RULE_REF`.

## Scope boundary

The experiment asks only whether the candidate carrier is sufficient for a
fresh observer to reconstruct whether the historical
`ACCEPTED_FOR_HANDOFF` status was warranted under the rule basis that actually
governed RG-017.

It does not ask whether R2 would be eligible under today's visible rule, which
rule is preferable, or whether any real repository action should occur.

No external evidence, repository browsing, conversation history, or unstated
policy may be used.
