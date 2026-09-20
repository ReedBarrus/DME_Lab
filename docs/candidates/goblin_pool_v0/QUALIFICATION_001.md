# GOBLIN_POOL_001 — Qualification 001

## Tested basis

```text
candidate head:
47d4044d652d793d7c9c5e536fe96315c7c46155

stack base:
labboib-temporal-seat-v0
35d1f13396afde04e4fbad8d3c3de60136926736

workflow:
GOBLIN_POOL_001

workflow run:
35500575299

job:
106051505299

trigger:
pull_request

conclusion:
SUCCESS
```

## Observed execution

GitHub Actions externally observed:

```text
Compile controller:
PASS

Run GOBLIN_POOL_001 pressure cells:
PASS

Exercise fixture CLI:
PASS
```

Exact focused test result:

```text
11 / 11 PASS
```

Observed pressure cells:

```text
P1 simultaneous different-seat wake:
PASS

P2 same-seat overlap:
PASS

P3 stale state submission:
PASS

P4 duplicate output:
PASS

P5 deterministic-only wake:
PASS

P6 semantic escalation without seat mutation:
PASS

P7 authority stop:
PASS

P8 crash before commit + lease recovery:
PASS

P9 retry after commit / idempotent successor:
PASS
```

Additional executed regressions:

```text
REGISTERED / AVAILABLE / ELIGIBLE / AUTHORIZED noncollapse:
PASS

cursor + working state + output + lease release in one transition:
PASS
```

## Observed bounded consequences

### Different-seat occupancy

Two separate seats may hold distinct active wakes without cross-contaminating
their retained working states.

### Same-seat single successor

Two overlapping wake attempts against one seat produced exactly:

```text
1 STARTED
1 OCCUPANCY_CONFLICT
```

No second legitimate occupant was created.

### Stale-basis rejection

An old wake produced against seat version 0 was rejected after a later wake
committed seat version 1.

```text
VALIDLY PRODUCED OUTPUT
!=
VALID AGAINST CURRENT SEAT BASIS
```

was mechanically material in the tested fixture.

### Duplicate-output conservation

Reusing an output identity after its first committed transition was rejected.

Observed retained counts remained:

```text
outputs:
1

transitions:
1
```

### Deterministic agentic behavior without transformer

`GOB_B` executed the exact declared `SMOKE_TRUE` test through
`RUN_DECLARED_TEST`, received an operator receipt, and committed a seat
successor while:

```text
semantic_requests:
0
```

This supports only the bounded tested distinction:

```text
AGENTIC BEHAVIOR
!=
TRANSFORMER INVOCATION
```

### Semantic proposal isolation

A semantic request and proposal were retained while:

```text
seat state_version:
UNCHANGED

seat cursor:
UNCHANGED

seat working state:
UNCHANGED
```

Therefore the tested semantic proposal did not directly mutate the seat.

### Authority stop

For `GOB_C / WRITE_PACKET` the tested posture was:

```text
REGISTERED:
true

AVAILABLE:
true

ELIGIBLE:
true

AUTHORIZED:
false
```

Observed result:

```text
AUTHORITY_REQUIRED
action request retained
packet file absent
```

### Crash before commit

A synthetic crash after successor SQL statements but before SQLite commit
rolled back:

```text
output
transition
cursor change
working-state change
version change
receipt
```

The durable lease remained visibly occupied and was separately recovered.

### Retry after commit

Replaying the same wake / transition / output identities after a successful
commit returned:

```text
ALREADY_COMMITTED
idempotent_replay = true
```

with exactly one output and one transition retained.

## CLI fixture

The exact candidate CLI initialized:

```text
GOB_A
GOB_B
GOB_C
```

and independently reported:

```text
GOB_B / RUN_DECLARED_TEST

registered:
true

available:
true

eligible:
true

authorized:
true
```

A `GOB_A` wake then started from:

```text
basis_version:
0

basis_cursor_event_id:
EV-000001
```

The CLI check emitted:

```text
GOBLIN_POOL_001_CLI_PASS
```

## Bounded result

The observed candidate supports:

```text
ONE SQLITE CONTROLLER
CAN MEDIATE THREE
DURABLE TEMPORAL SEATS

UNDER THE EXECUTED
OVERLAP,
STALE-BASIS,
DUPLICATE,
DETERMINISTIC,
SEMANTIC-ESCALATION,
AUTHORITY-STOP,
AND CRASH PRESSURES

WITHOUT OBSERVED
SEAT-IDENTITY OR
SINGLE-SUCCESSOR COLLAPSE.
```

## Claim ceiling

This qualification does not establish:

```text
30-seat scalability
distributed-controller safety
network partition tolerance
general autonomous agency
safe arbitrary operators
general scheduler correctness
general economic autonomy
VS Code / CLI tunnel safety
model-router correctness
production reliability
main integration
```

It does not authorize merge or capability expansion.
