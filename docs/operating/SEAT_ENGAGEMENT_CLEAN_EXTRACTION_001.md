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

Its changed-file set includes both reusable SEAT_ENGAGEMENT_HANDSHAKE_001
candidate artifacts and live Lane-B coordination state, plus duplicated
TWO_LANE_COORDINATION_001 files inherited from its old base.

Freeze:

```text
OPERATING BRANCH
!=
INTEGRATION BRANCH
```

## Frozen source

```text
lane-b-recovery-continuity-v0
41316921b211c1daf75c9b71b8147e0eb67d372d
```

The historical source must remain unchanged during extraction.

## Candidate allowlist

A future clean extraction may copy only:

```text
.github/workflows/seat-engagement-handshake-001.yml

docs/candidates/seat_engagement_handshake_v0/**

schemas/seat_engagement_decision_v0.schema.json
schemas/seat_engagement_envelope_v0.schema.json
schemas/seat_engagement_pre_mutation_disposition_v0.schema.json
schemas/seat_engagement_work_unit_binding_v0.schema.json

tests/runtime/test_seat_engagement_handshake_v0.py
tools/seat_engagement_handshake_v0.py
```

Any additional path requires explicit review before inclusion.

## Explicit denylist

Do not extract from PR #69:

```text
coordination/**

docs/candidates/two_lane_coordination_v0/**
schemas/two_lane_*
tests/runtime/test_two_lane_coordination_v0.py
tools/two_lane_coordination_v0.py
.github/workflows/two-lane-coordination-001.yml
```

The two-lane substrate is already admitted to main independently.

## Extraction basis

The future clean integration branch begins from then-current admitted main, not
from the Lane-B operating branch.

The copied bytes must be checked against the exact frozen source coordinate.

```text
COPY FROM SOURCE
!=
REWRITE HISTORY

BYTE IDENTITY
!=
NEW SCIENTIFIC QUALIFICATION
```

## Required clean-basis verification

After extraction, independently run:

```text
python -m unittest tests.runtime.test_seat_engagement_handshake_v0 -v
python -m unittest tests.runtime.test_two_lane_coordination_v0 -v
```

and regenerate the seat-handshake qualification evidence from its raw fixtures
and evaluation key.

If source-byte identity or deterministic evidence correspondence fails:

```text
STOP
```

## Provenance preservation

The clean branch may record:

```text
candidate bytes extracted from
lane-b-recovery-continuity-v0@41316921b211c1daf75c9b71b8147e0eb67d372d
```

It may not claim:

```text
WORKSHOP invocation-001 authored all extracted effects
```

Freeze:

```text
SOURCE COORDINATE
!=
INVOCATION AUTHORSHIP
```

## PR #69 disposition

PR #69 remains the historical operating specimen until a separate decision
changes its state.

Clean extraction does not require rewriting, squashing, or deleting it.

```text
CLEAN INTEGRATION
!=
ERASE OPERATING HISTORY
```

## Terminal target

A successful later extraction produces:

```text
fresh branch from current main
only allowlisted seat-handshake candidate files
green clean-basis handshake tests
green two-lane regressions
reproducible qualification evidence
historical Lane-B specimen untouched
merge still separately authorized
```
