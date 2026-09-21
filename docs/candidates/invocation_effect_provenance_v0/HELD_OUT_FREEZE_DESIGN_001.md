# INVOCATION_EFFECT_PROVENANCE_001 — Held-Out Freeze Design v0

## Freeze order

```text
1 public warrant / candidate contract
2 input membrane
3 result vocabularies + precedence
4 scorer correspondence predicate
5 raw fixture identities
6 held-out evaluation key
7 candidate apparatus identity
8 held-out administration
```

## Closed result vocabulary

```text
EFFECT_EXISTS:
true | false

INVOCATION_EFFECT_ATTRIBUTION:
ESTABLISHED | UNATTRIBUTED | INVALID

CLAIM_EXERCISE:
VALID | INVALID | UNESTABLISHED

AUTHORIZATION_AT_EFFECT_START:
VALID | ABSENT | CONSUMED | INVALID

EFFECT_RESULT:
SUCCESS | FAILURE | NOT_STARTED

PRESSURE:
INVOCATION_EFFECT_PROVENANCE_SURVIVES
INVOCATION_EFFECT_PROVENANCE_FRACTURES
ADMINISTRATION_INVALID
```

## Candidate-input membrane

Candidate input contains only:

```text
invocation_binding:
  seat_id
  occupant_id
  invocation_id
  claim_id
  work_unit_id
  authority_ref

effect_observation:
  effect_id
  effect_kind
  mutation_event_id
  pre_coordinate
  post_coordinate
  object_refs
  entry_witness
```

Forbidden candidate inputs:

```text
actual_actor_ground_truth
tested_invocation
expected_attribution
expected_claim_exercise
expected_authority
evaluation_key
pre-adjudicated correspondence
```

## Held-out cells

```text
A  matched I1 / ACTIVE C1 / U1 / authority VALID
B  actual I2; tested relation I1; same synthetic target surface
C  durable effect with no candidate provenance path for I1
D  I1 receipt claims wrong pre-basis
E1 matched I1 with authority ABSENT
E2 matched I1 with authority CONSUMED
F  actual I2 produces task-correct output; tested relation I1
G  actual I1 attributed, but C1 covers wrong work unit
H  I1 provenance claims wrong durable post-coordinate
```

## Held-out isolation

The candidate function never reads fixture or evaluation-key paths.

The held-out runner owns fixture loading and gives the candidate only the
candidate-input object constructed for the actual synthetic actor.

The scorer independently receives harness ground truth and the frozen key.

Qualification uses dummy Q-* specimens only. A-H/E1/E2 are not evaluated
during apparatus qualification.
