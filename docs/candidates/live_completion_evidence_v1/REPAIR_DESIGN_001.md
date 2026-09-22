# LIVE_COMPLETION_EVIDENCE_001 — Repair Design 001

```text
OBJECT_TYPE:
BOUNDED_REPAIR_DESIGN

OBJECT_ID:
LIVE_COMPLETION_EVIDENCE_001-REPAIR-V1

BASIS_REVIEW:
LIVE_COMPLETION_EVIDENCE_001-INDEPENDENT_REVIEW-001

TARGETED_FRACTURES:
Q1-Q6

LIVE_LANE_MUTATION:
NONE

LIFECYCLE_EXECUTION:
NONE

MERGE:
NONE
```

The repair preserves the v0 qualification as historical evidence and materializes a
separate v1 bridge.

## Q1
Completion criterion semantics are now mechanically compared against exact fields of
the pre-work claim. Post-work commit IDs and final head are evidence, not criterion
terms.

## Q2
The blocker producer no longer accepts caller-supplied boolean evaluations. It derives
every closed-scope blocker class from raw live basis and the P07 candidate/runtime
producer result.

## Q3
Candidate declaration and runtime producer qualification are separate APIs. Candidate
metadata can support qualification pressure only; runtime production requires a
receipt-backed qualified-producer registry.

## Q4
The next phase must materialize reproducible P07/P08 basis objects that transitively pin
every consumed raw input, implementation identity, and qualification witness.

## Q5
The next phase must invoke the exact authoritative lifecycle controller blob through an
explicit adapter. A hand-built COMPLETE_EVALUABLE conjunction is not sufficient.

## Q6
The bounded-unit identity is canonical:
sha256(canonical pre-work claim identity basis).
Consistent renaming across new fixtures therefore fails P05.

This first repair phase qualifies only Q1/Q2/Q3/Q6 candidate mechanics and prepares
Q4/Q5. It does not claim the full bridge repaired until receipt-backed producer
qualification, reproducible basis objects, and exact controller composition survive.
