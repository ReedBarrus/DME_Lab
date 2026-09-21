# HISTORICAL_P09_PRODUCER_QUALIFICATION_001

## Object

```text
OBJECT_TYPE:
UPSTREAM_STANDING_PRODUCER_QUALIFICATION

OBJECT_ID:
HISTORICAL_P09_PRODUCER_QUALIFICATION_001

RELATION_TYPE:
ACTIVE_OWNERSHIP_EFFECT_STATUS

TARGET_CONSUMER:
LANE_LIFECYCLE_DISPOSITION_001 / P09

REPAIR:
P09_SCOPE_AND_TEMPORAL_BOUNDARY_002
```

## Sole question

Given an independently pinned bounded-scope identity, the exact unit inventory
and exact ordered raw effect-event log for that scope, can a producer derive:

```text
NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP
or
UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP
```

without inferring favorable standing from an omitted unit, omitted event, or a
terminal/checkpoint event that precedes the relevant effect start?

## Repaired raw membrane

The producer does not accept `closed_scope = true` as evidence. It also does not
permit an administration to make a convenient subset self-authenticating merely
by recomputing a matching checksum.

Input is split into:

```text
UPSTREAM / HARNESS-PINNED SUBJECT IDENTITY:
scope_basis_identity

RAW SCOPE MATERIAL:
scope:
  scope_id
  unit_ids[]
  event_count
  event_log_sha256

RAW ORDERED EVENTS:
events[]:
  scope_id
  unit_id
  event_index
  event_type
```

The producer derives an observed scope identity from the supplied scope material
and requires:

```text
observed scope identity
=
scope_basis_identity
```

The pinned identity is not derived from the candidate subset being evaluated.
Under historical administration it must come from the exact retained source
basis before producer invocation.

```text
SELF-CONSISTENT SUBSET
!=
PINNED CLOSED SUBJECT

DECLARED CLOSED_SCOPE
!=
CLOSED ACCOUNTING MECHANICALLY BOUND
```

It additionally establishes:

```text
event_log_sha256 = digest(exact ordered events[])
event_count = len(events[])
every event.scope_id = scope.scope_id
every event.unit_id ∈ scope.unit_ids[]
event_index = contiguous ordered sequence
```

## Temporal derivation law

For each unit, retain the latest START, TERMINAL_RECEIPT, and
OWNERSHIP_INDEPENDENT_CHECKPOINT. A started unit ceases to require ACTIVE
ownership only when a terminal receipt or ownership-independent checkpoint
occurs strictly after its latest relevant effect start.

```text
TERMINAL EXISTS
!=
TERMINAL AFTER RELEVANT EFFECT START

CHECKPOINT EXISTS
!=
CHECKPOINT COVERS CURRENT EFFECT
```

## Frozen cells

```text
A START -> TERMINAL => favorable
B START only => unfinished
C START -> OWNERSHIP_INDEPENDENT_CHECKPOINT => favorable
D raw scope material disagrees with pinned scope identity => ADMINISTRATION_INVALID
E U1 START -> TERMINAL; U2 START => unfinished U2
F pinned subject = full {U1,U2} scope, but supplied scope/events are a fully
  self-consistent {U1}-only subset with recomputed event count and digest
  => ADMINISTRATION_INVALID
G TERMINAL -> START => unfinished
H OWNERSHIP_INDEPENDENT_CHECKPOINT -> START => unfinished
```

Cell F is the critical closure attack:

```text
SUBSET INTERNALLY CONSISTENT:
YES

SUBSET MATCHES PINNED CLOSED SUBJECT:
NO

RESULT:
ADMINISTRATION_INVALID
```

## Historical application boundary

Qualification of this producer does not itself establish the historical Lane-B
scope identity. Before historical administration, a separate reconstruction
must establish the exact retained Lane-B bounded-scope identity from the
preserved specimen. That identity is pinned as `scope_basis_identity`; P09 may
not replace it with a newly computed identity for a favorable subset.

```text
PRODUCER QUALIFIED
!=
HISTORICAL SCOPE ESTABLISHED
```

No live lane mutation. No RELEASE. No P11 standing. No P18 repair. No merge authorization.
