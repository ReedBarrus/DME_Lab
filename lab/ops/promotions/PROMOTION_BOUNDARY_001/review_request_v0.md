# PROMOTION_BOUNDARY_001 — Fresh Promotion Review Request v0

## Phase

```text
PROMOTION CANDIDATE:
MATERIALIZED

FRESH REVIEW:
REQUESTED

ADJUDICATION:
NONE

PROMOTION ENVELOPE:
NONE

PROMOTION AUTHORITY:
NONE INFERRED

PROMOTION EXECUTION:
NONE

RATIFICATION RECEIPT:
NONE
```

## Role

Fresh promotion reviewer acting only under prospective Promotion Protocol v0.

The reviewer must not treat the candidate's existing presence on `main` as
evidence that it deserves ratification.

```text
ALREADY DURABLE
!=
PROMOTABLE UNDER REVIEW
```

The candidate materializer authored both the proposed protocol and the
retroactive candidate. Under Promotion Protocol v0, that materializer is not
eligible to supply an `ADMIT` fresh review.

## Exact candidate

```text
promotion_id:
PROMOTION_BOUNDARY_001

path:
lab/ops/promotions/PROMOTION_BOUNDARY_001/candidate_v0.json

Git blob:
b328ab4c20e738d1528ee1967010c052c624b02b
```

The reviewer MUST compute and bind the SHA-256 of the exact candidate bytes in
the review artifact.

## Current durable reality to inspect

```text
main:
759eca8c3f3c2d3e37d8031207742290f1fb8b6b

PR #29 head:
9c79ad37522f58e2fa615324bdab681e21bf9501

PR #29 merge:
759eca8c3f3c2d3e37d8031207742290f1fb8b6b

Operational Constitution Article 0 blob:
f25f9ec41120bdf763082d0e340efcb1f6de98be

promotion-boundary decision blob:
c205075b6e83983c85c35e45dd604b12fe35d32b

constraint registry blob containing D-0047 / D-0048:
7be5f7b4faeca4be1be0930739f11280c1f800ce
```

## Sole question

```text
DOES PROMOTION_BOUNDARY_001,
AS EXACTLY MATERIALIZED,
SATISFY THE BURDEN
FOR RATIFICATION AS EXISTING DURABLE SUBSTRATE
UNDER PROMOTION_PROTOCOL_v0?
```

## Required review checks

Return PASS, HOLD, or FAIL for each:

```text
SUBJECT_IDENTITY
SOURCE_STATUS
TARGET_STATUS
SURVIVING_BOUNDED_BEHAVIOR
EVIDENCE_SUFFICIENCY
CLAIM_CEILING
DEPENDENCY_CONSEQUENCE
INTEGRATION_MINIMALITY
LINEAGE_RECOVERABILITY
KNOWN_DEBT
NON_PROMOTIONS
```

Then return exactly one disposition:

```text
ADMIT
HOLD
REJECT
REQUIRE_REPRESSURE
```

## Required adversarial questions

1. Does branch-retention pressure actually support the general three-layer
   development rule, or is Article 0 broader than its basis?
2. Are D-0047 and D-0048 correctly typed as design constraints?
3. Does Article 0 establish only a development constraint, or does any wording
   silently promote specific runtime/scientific claims?
4. Is the dependency consequence of durable-substrate standing explicit?
5. Is the integration rule minimal enough to prevent whole-lineage import
   without severing lineage recoverability?
6. Does retroactive ratification preserve the fact that the original path
   lacked candidate, fresh review, adjudication, envelope, and typed receipt?
7. Is any unresolved debt material enough to require HOLD or REPRESSURE?

## Output artifact

Materialize:

```text
lab/ops/promotions/PROMOTION_BOUNDARY_001/review_v0.json
```

conforming exactly to:

```text
schemas/promotion_review_v0.schema.json
```

## Stop rule

The reviewer does NOT:

```text
adjudicate
materialize a promotion envelope
authorize ratification
write a promotion receipt
merge this protocol branch
modify Article 0
promote Atlas
promote Concordance
```

A review disposition is not a promotion effect.
