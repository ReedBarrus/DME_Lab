# LABBOIB_CONTROLLER_BINDING_001 — Qualification 001

## Tested basis

```text
candidate head:
6f8a11574cb4fbc4427acd87cf4791c5d2f567da

stack base:
goblin-pool-v0
88bc5a3daa6e36306da939738e453ac7a29679fb

canonical merged LABBOIB basis:
main
e6b56d12352f9594b25d1db3036afc3d1d0d7ef6
```

External workflow receipts:

```text
GOBLIN_POOL_001
run:
35501174115
conclusion:
SUCCESS

LABBOIB_CONTROLLER_BINDING_001
run:
35501174221
job:
106053085290
conclusion:
SUCCESS
```

## Observed execution

### LABBOIB temporal-seat regression

```text
7 / 7 PASS
```

This re-establishes the temporal-seat candidate behavior under the descendant
controller-binding checkout.

### GOBLIN_POOL_001 regression

```text
11 / 11 PASS
```

The original overlap, stale-basis, duplicate, deterministic, semantic,
authority-stop, crash, operator-layer, and atomic-transition pressures remained
green after the controller was extended with:

```text
external-seat binding hooks
repository-basis applicability tracking
```

Therefore, in tested scope:

```text
ANCESTOR QUALIFICATION
WAS NOT MERELY INHERITED;
THE DESCENDANT CONTROLLER
RE-EXECUTED THE PRESSURE.
```

### LABBOIB controller-binding pressure

```text
6 / 6 PASS
```

The six executable tests covered seven named pressure cells because B3/B4 share
one declared-test specimen.

Observed:

```text
B1 exact LABBOIB basis binding:
PASS

B2 real READ_REPO_STATE non-mutation +
   controller-only successor:
PASS

B3 caller argv cannot replace declared test argv:
PASS

B4 mechanical PASS adds no scientific standing:
PASS

B5 WRITE_PACKET ineligible / unexecuted:
PASS

B6 H1 → H2 during declared test:
   operator execution survives
   current_basis_applicability = false
   successor rejects invocation:
PASS

B7 same exact initial basis binds idempotently
   before runtime evolution:
PASS
```

### Real CLI specimen

The workflow executed the actual script entrypoint as separate processes:

```text
bind
→ wake
→ read
→ test
```

Observed:

```text
LABBOIB_CONTROLLER_BINDING_001_CLI_PASS
```

The CLI asserted:

```text
seat:
LABBOIB

cursor:
CE-000033

continuity head:
CE-000033

READ_REPO_STATE:
authorized
executed
current_basis_applicability = true
mutation_effect = NONE_BY_READ_REPO_STATE

RUN_DECLARED_TEST:
authorized
executed
mechanical_result = PASS
scientific_standing_effect = NONE
current_basis_applicability = true

WRITE_PACKET:
eligible = false
authorized = false
```

## Stale-environment result

The B6 pressure used a copied Git workspace.

The declared test started against repository head H1.

While that exact test process remained active, the pressure harness committed a
new repository head H2.

The operator still returned a mechanically successful result.

Observed:

```text
operator status:
EXECUTED

mechanical_result:
PASS

repo_head_at_start:
H1

repo_head_at_return:
H2

basis_stable_during_operator:
false

current_basis_applicability:
false
```

Attempting to admit that invocation into the next LABBOIB controller successor
was rejected.

The seat retained:

```text
state_version:
0

cursor:
CE-000033

occupancy:
OCCUPIED
```

until the lease was explicitly recovered.

This mechanically supports, within the tested fixture:

```text
OPERATOR EXECUTED
!=
RESULT CURRENTLY APPLICABLE

RESULT EXISTS
!=
CURRENT-BASIS APPLICABILITY
```

## Git seat / controller runtime separation

B2 committed a real controller runtime successor after
`READ_REPO_STATE`.

Observed:

```text
controller state_version:
0 → 1
```

while the checkout's exact:

```text
continuity/cursors/labboib.json
continuity/current_state/labboib_working_state_v0.json
```

bytes remained unchanged.

This supports only the tested separation:

```text
CONTROLLER SUCCESSOR
!=
GIT LABBOIB SEAT ARTIFACT MUTATION
```

## Declared-test boundary

The pressure caller supplied a fake `argv` field alongside the valid test ID.

The controller ignored that caller argv and resolved the registered
`LABBOIB_TEMPORAL_SEAT_FOCUSED` command from its declared-test registry.

Observed result explicitly carried:

```text
mechanical_result:
PASS

scientific_standing_effect:
NONE
```

Thus the tested fixture preserved:

```text
DECLARED TEST
!=
ARBITRARY SHELL COMMAND

PROCESS EXITED
!=
SCIENTIFIC STANDING PROMOTED
```

## Rake retained — module importability vs direct CLI execution

The first binding workflow run observed:

```text
all semantic pressure tests:
PASS

direct CLI entrypoint:
FAIL
```

Cause:

```text
python tools/labboib_controller_binding.py

→ sys.path[0] = tools/
→ import tools.goblin_pool failed
```

Repair:

```text
direct script resolves repository root
→ inserts root into sys.path
→ imports tools.goblin_pool
```

The repaired script was re-pinned in the binding object and the complete
workflow then passed.

Scar:

```text
MODULE IMPORTABLE IN TEST HARNESS
!=
CLI EXECUTABLE FROM REPO ROOT
```

## Bounded result

The observed candidate supports:

```text
THE MERGED LABBOIB TEMPORAL SEAT
CAN BE BOUND AS A DISTINCT
SQLITE CONTROLLER-MEDIATED RUNTIME RECORD

AND CAN USE THE TESTED REAL LOCAL:

READ_REPO_STATE
RUN_DECLARED_TEST

UNDER THE TESTED:

EXACT SEAT BASIS
EXPLICIT OPERATOR AUTHORITY
DECLARED-TEST RESOLUTION
REPOSITORY-BASIS APPLICABILITY
TRANSACTIONAL SUCCESSOR
AND NON-MUTATING GIT-SEAT BOUNDARIES.
```

## Claim ceiling

This qualification does not establish:

```text
scheduler correctness
model occupation
Codex / VS Code adapter safety
LM Studio binding
arbitrary shell safety
repository-write safety
automatic Git seat persistence
30-seat scalability
distributed-controller safety
production reliability
general autonomous agency
```

It does not authorize merge or capability expansion.
