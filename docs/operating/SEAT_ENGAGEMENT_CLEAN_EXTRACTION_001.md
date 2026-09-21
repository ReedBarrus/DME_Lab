# SEAT_ENGAGEMENT_CLEAN_EXTRACTION_001

## Object

```text
OBJECT_TYPE:
INTEGRATION_PLAN

OBJECT_ID:
SEAT_ENGAGEMENT_CLEAN_EXTRACTION_001

STATUS:
MATERIALIZED FOR REVIEW

EXECUTION:
NOT AUTHORIZED
```

## Problem

PR #69 is an operating-branch specimen.

Its changed-file set includes:

```text
reusable SEAT_ENGAGEMENT_HANDSHAKE_001 candidate artifacts
+ live Lane-B coordination state
+ duplicated TWO_LANE_COORDINATION_001 files inherited from its old base
```

and the candidate contract itself still contains source-operating material:

```text
Human warrant identity
Operating assignment
LANE_B operating branch
WORKSHOP invocation relation
```

Therefore:

```text
OPERATING BRANCH != INTEGRATION BRANCH
SOURCE PROVENANCE != CURRENT OPERATING ASSIGNMENT
SOURCE QUALIFICATION EVIDENCE != CLEAN-BASIS QUALIFICATION RECEIPT
```

## Frozen source

```text
lane-b-recovery-continuity-v0
41316921b211c1daf75c9b71b8147e0eb67d372d
```

The historical source remains unchanged during extraction.

## Extraction classes

### A — exact reusable implementation/material

These may be copied byte-for-byte if still appropriate at execution time:

```text
.github/workflows/seat-engagement-handshake-001.yml
schemas/seat_engagement_decision_v0.schema.json
schemas/seat_engagement_envelope_v0.schema.json
schemas/seat_engagement_pre_mutation_disposition_v0.schema.json
schemas/seat_engagement_work_unit_binding_v0.schema.json
tests/runtime/test_seat_engagement_handshake_v0.py
tools/seat_engagement_handshake_v0.py
docs/candidates/seat_engagement_handshake_v0/fixtures/RAW_FIXTURES_v0.json
docs/candidates/seat_engagement_handshake_v0/fixtures/EVALUATION_KEY_v0.json
```

Byte identity must be checked against the frozen source coordinate.

### B — de-operationalized scientific contract material

The following source material must not be presented as current operating
authority merely because it existed on the Lane-B branch:

```text
SEAT_ENGAGEMENT_HANDSHAKE_001.md
PRESSURE_DESIGN_001.md
QUALIFICATION_EVIDENCE_001.json
```

The clean branch must preserve the source coordinate and historical origin but
must separate source-operating provenance from current scientific semantics.

Minimum repair:

```text
source Lane-B / warrant / invocation coordinates
→ retained as historical provenance only

no source operating assignment
→ treated as current binding or authority

old qualification evidence
→ treated as source evidence, not current clean-basis qualification
```

Any semantic edit beyond this de-operationalization requires explicit review.

## Explicit denylist

Do not import:

```text
coordination/**
docs/candidates/two_lane_coordination_v0/**
schemas/two_lane_*
tests/runtime/test_two_lane_coordination_v0.py
tools/two_lane_coordination_v0.py
.github/workflows/two-lane-coordination-001.yml
```

The two-lane substrate is already admitted to main independently.

## Clean branch basis

The future clean integration branch begins from then-current admitted main.

Freeze:

```text
COPY FROM SOURCE != REWRITE HISTORY
DE-OPERATIONALIZE SOURCE CONTEXT != RETROACTIVE REINTERPRETATION
BYTE IDENTITY != NEW SCIENTIFIC QUALIFICATION
```

## Fresh qualification requirement

The clean branch must produce a fresh qualification receipt from the clean
candidate basis.

It may reuse frozen raw fixtures / evaluation key only if fresh review confirms
they remain valid inputs after de-operationalization.

Required deterministic checks:

```text
python -m unittest tests.runtime.test_seat_engagement_handshake_v0 -v
python -m unittest tests.runtime.test_two_lane_coordination_v0 -v
```

and:

```text
regenerate seat-handshake qualification evidence
from clean candidate inputs
```

The new receipt must be addressable as clean-basis evidence rather than merely
relabeling the old Lane-B receipt.

If de-operationalization changes the scientific question or scorer contract:

```text
STOP FOR AMENDMENT
```

## Provenance preservation

The clean branch may say:

```text
derived from source candidate
lane-b-recovery-continuity-v0@41316921b211c1daf75c9b71b8147e0eb67d372d
```

It may not say:

```text
WORKSHOP invocation-001 authored all extracted effects
source warrant remains current authority
source Lane-B assignment remains active
```

Freeze:

```text
SOURCE COORDINATE != INVOCATION AUTHORSHIP
HISTORICAL WARRANT != CURRENT GRANT
HISTORICAL ASSIGNMENT != CURRENT BINDING
```

## PR #69 disposition

PR #69 remains the historical operating specimen until a separate decision
changes its state.

Clean extraction does not require rewriting, squashing, or deleting it.

```text
CLEAN INTEGRATION != ERASE OPERATING HISTORY
```

## Terminal target

A successful later extraction produces:

```text
fresh branch from current main
only integration-safe seat-handshake artifacts
historical operating provenance explicitly demoted to source provenance
fresh clean-basis qualification receipt
green handshake tests
green two-lane regressions
historical Lane-B specimen untouched
merge still separately authorized
```
