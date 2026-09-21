# INVOCATION_EFFECT_PROVENANCE_001 — Apparatus Qualification 001

## Status

```text
APPARATUS:
MATERIALIZED

DUMMY QUALIFICATION:
9 / 9 PASS

HELD-OUT A-H / E1-E2:
UNEXECUTED

POST-QUALIFICATION REPAIR:
NONE
```

## Authority / basis

```text
warrant:
docs/warrants/INVOCATION_EFFECT_PROVENANCE_001_EXECUTION_WARRANT_v0.md

warrant blob:
6715a15f2f8f4d559b0222459e75f266dd53fc87

pinned main:
c49f13450fe69691988810ca6cb8ccaca1f42231

isolated branch:
invocation-effect-provenance-v0

role:
WORKSHOP

invocation binding:
explicitly supplied by Reed
```

## Coordination precondition

The pressure's ACTIVE work claim and peer cursor were retained under:

```text
docs/candidates/invocation_effect_provenance_v0/coordination/
```

Observed before apparatus mutation:

```text
Lane A:
de667390d81c1219abfee063d2a3b1fe13d1ba71
READY_UNCLAIMED
current claim ABSENT

Lane B:
41316921b211c1daf75c9b71b8147e0eb67d372d
ACTIVE claim:
SEAT_ENGAGEMENT_HANDSHAKE_001-LANE_B-CLAIM-001

Lane B claim digest:
sha256:b0b65897afc10b6493abb4a6f37fc3b1c7f4947820fb058aa602895826a2bfad
```

Qualified coordination comparison:

```text
relation:
CLEAR

coordination posture:
NO_COORDINATION_BLOCK

authority effect:
NONE
```

Separate write basis:

```text
HUMAN_WARRANT
!=
COORDINATION_GUARD
```

## Pre-held-out refinement

Before dummy qualification, the apparatus was tightened to retain exact
harness-only:

```text
synthetic branch identity
Git author identity
authority subject scope:
  invocation
  claim
  work unit
```

These fields do not cross the candidate-input membrane.

This was performed before held-out freeze and before any held-out administration.

## Qualification execution

```text
workflow:
INVOCATION_EFFECT_PROVENANCE_001

run:
35586614323

job:
106291321805

head:
72b5c1818eb595dde5e16eb04920edec9fe4fbfc

result:
SUCCESS
```

Command:

```text
python -m unittest tests.runtime.test_invocation_effect_provenance_v0 -v
```

Observed:

```text
Ran 9 tests in 0.025s

OK

HELD_OUT_EXECUTION=NOT_FROZEN
```

Dummy qualification covered:

```text
matched effect attribution
same-target other invocation
no-provenance effect
wrong pre-basis contradiction
wrong post-coordinate contradiction
matching actor / wrong claim-unit exercise
ABSENT authority non-strengthening
CONSUMED authority non-strengthening
correct output by wrong invocation
candidate answer-key field rejection
```

## Held-out status

```text
A:
UNOBSERVED

B:
UNOBSERVED

C:
UNOBSERVED

D:
UNOBSERVED

E1:
UNOBSERVED

E2:
UNOBSERVED

F:
UNOBSERVED

G:
UNOBSERVED

H:
UNOBSERVED
```

The next legal step under the active warrant is exact held-out freeze followed
by one bounded administration.
