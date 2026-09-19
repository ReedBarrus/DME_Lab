# COUNTERFEIT_WARRANT_001 — EXECUTION ENVELOPE v0

**Host:** `CONDUCTOR_ROLE_HANDOFF_001`  
**Pressure:** `COUNTERFEIT_WARRANT_001`  
**Campaign phase:** `PROCESS CONSEQUENCE`  
**Envelope status:** READY_FOR_REED_EXECUTION_AUTHORIZATION  
**A/B realization consumed:** NO  
**Scientific standing effect:** NONE  
**Merge authority:** NONE  

## 1. CURRENT REPOSITORY / APPARATUS BASIS

Current repository main observed before this envelope was retained:

```text
ReedBarrus/DME_Lab
main:
f7d5bb6705085f45725a040153e0c66616789ed4
```

The apparatus is already admitted into current repository lineage via merged PR #19.

The exact experimental implementation basis remains the one-commit apparatus realization:

```text
72ad130c35dc2be7b02cf7239d33d11de3af280e
parent:
f332bfe8aebfda16b588689dd1fd4455f7da2935
```

Current `main` contains byte-identical apparatus files for the implementation surfaces listed below. The matched-pair realization, if separately authorized, is bound to `72ad130c35dc2be7b02cf7239d33d11de3af280e`, not to branch identity, PR identity, or "latest main."

## 2. EXACT IMPLEMENTATION IDENTITIES

```text
evaluator.py
Git blob:
2ad67ba03ba5a12d39dd1a9b038b9b7788e15e15

static_comparator.py
Git blob:
615fcc0b7c21b3cbab20fbbd82739b2f28720711

process_fixture.json
Git blob:
29c5d8232d01915123f99e64cafa10b7da4a9906
SHA-256:
9c20e3b9e3ccb9a3ad877a210438a3aff78f0a65ca39244ee8b7c9d4af7ad09e

role_output_packet.json
Git blob:
3946d2ff2345246e602f2d6e13f4cc826d381a4f
canonical whole-packet SHA-256:
04b24d8beb04803f6a6b208f4f953efaa005bd2bb94556499870e15e68fd2beb

routing_warrant_A.json
Git blob:
b9ab264ac8b0e9709e94af94c357c75198972a9b
SHA-256:
5032ff9a45b98e83d0143e76cdf9484e764be3585ea985d217ab5e3262a35a50

routing_warrant_B.json
Git blob:
de431de642b6535a077ad28fa5a033880ba46398
SHA-256:
7a1c8c6c99b9dec74261b83ca06d514907adfca6e2453745c3564d707709a792
```

Published frozen relations retained by the apparatus:

```text
semantic payload SHA-256:
9e5e367615e9df465dbf945272d011c1d2ec0646ff4baa9bfbc27202c438a203

binding tuple SHA-256:
685925fa653bc2cf82d8b2e70aa9d61650075fab64fdb5c10f25c0c2449316a2

routed packet SHA-256:
fe837a4a9885404846bf353d3edb3f573976fba56d7e9e929d4dc183fede8e1e
```

## 3. HELD-OUT STATUS BEFORE REALIZATION

Retained apparatus receipt from PR #19 states:

```text
NO A/B EXPERIMENTAL REALIZATION OCCURRED

A.routing_warrant.valid = UNOBSERVED
B.routing_warrant.valid = UNOBSERVED

A.edge.admissible = UNOBSERVED
B.edge.admissible = UNOBSERVED

A movement = UNOBSERVED
B movement = UNOBSERVED

A/B differential result = UNOBSERVED
```

Current repository inspection exposes apparatus surfaces and apparatus tests only; no retained `COUNTERFEIT_WARRANT_001` realization-result artifact is present in the admitted specimen directory.

This envelope does not independently prove that no off-repository realization ever occurred. Before future execution, Workshop must re-check for any new contamination evidence and stop if the held-out state is no longer supportable.

## 4. EXACT INITIAL EVENT HISTORY

Each condition begins in a fresh isolated root.

Initial retained event history is exactly one registration event:

```jsonl
{"event_type":"PROCESS_REGISTERED","initial_phase":"OUTPUT_READY","process_id":"CONDUCTOR-ROLE-HANDOFF-001-FIXTURE"}
```

Identity:

```text
SHA-256:
a6664acfa445b751fe8aa7d1954f9299df35492280e3360b4ba88e0b27190c12
```

No event log is shared between A and B.

## 5. EXACT INITIAL PROJECTION

The exact reconstructed initial process position is:

```json
{
  "processes": {
    "CONDUCTOR-ROLE-HANDOFF-001-FIXTURE": {
      "blocker": null,
      "last_event_type": "PROCESS_REGISTERED",
      "next_transition": null,
      "pending_decision": null,
      "pending_role": null,
      "phase": "OUTPUT_READY",
      "process_id": "CONDUCTOR-ROLE-HANDOFF-001-FIXTURE",
      "scientific_standing": {
        "tracked": false,
        "value": null
      },
      "status": "REGISTERED"
    }
  },
  "projection_kind": "PROCESS_ROUTING",
  "projection_warning": "Process position only. This file is not scientific standing, evidence adjudication, or universal Lab state.",
  "schema_version": "lab_state_v0"
}
```

Identity:

```text
SHA-256:
5dc662c7a465e72b9005fd72d3e8415982a8aa69ee5680e5b20bbd2a96e80f90
```

A and B must reproduce this projection byte-for-byte before either condition is evaluated.

## 6. FROZEN CAUSAL CUT

Hold constant:

```text
semantic payload
role-output packet identity
process fixture
process topology
source position
requested transition
sender role
recipient role
basis repo
basis ref
authority ceiling
packet transport validity
implementation commit
initial event history
initial projection
scientific standing
protected non-dependent surfaces
```

Vary only:

```text
routing_warrant.binding_sha256
```

Condition A:

```text
685925fa653bc2cf82d8b2e70aa9d61650075fab64fdb5c10f25c0c2449316a2
```

Condition B:

```text
085925fa653bc2cf82d8b2e70aa9d61650075fab64fdb5c10f25c0c2449316a2
```

The condition label itself must not become evaluator input.

## 7. PROPOSED AUTHORIZED OPERATIONS FOR A FUTURE REALIZATION

This section defines the exact matched-pair execution that Reed may separately authorize.

### PRE-RUN

1. Resolve implementation commit exactly `72ad130c35dc2be7b02cf7239d33d11de3af280e`.
2. Verify every implementation/fixture identity in this envelope.
3. Verify no later contamination evidence has consumed A/B.
4. Create two fresh isolated temporary roots.
5. Initialize both roots with byte-identical implementation, process fixture, role-output packet, binding tuple, dependency map, event history, and projection.
6. Install only the frozen A warrant in root A and only the frozen B warrant in root B.
7. Mechanically confirm all common surfaces are identical and the only condition-root content delta is `routing_warrant.binding_sha256`.
8. If any required common-basis identity differs, return `REJECTED`; do not realize either condition.

### RUN ORDER

```text
1. CONDITION A — VALID WARRANT
2. CONDITION B — COUNTERFEIT WARRANT
```

Order is operationally frozen here. The roots share no mutable state.

### CONDITION A

Invoke the specimen-local realization entrypoint exactly once using:
- frozen process definition
- frozen reconstructed pre-state
- frozen role-output packet
- frozen A routing warrant
- existing packet transport validator
- A-local event/state paths
- exact Conductor implementation inherited by the implementation commit

Retain all returned and mutated local receipts.

### CONDITION B

Invoke the identical specimen-local realization entrypoint exactly once with only the frozen B routing warrant substituted.

Retain all returned and mutated local receipts.

### POST-RUN

Mechanically compare A and B against the frozen protected/non-protected surfaces and assign exactly one result from:

```text
PASS
FAIL
REJECTED
```

No semantic rescue or post-hoc rule change is permitted.

## 8. EXPECTED REAL CONSEQUENCES OF EXECUTION

If the frozen implementation behaves according to its declared apparatus, the experiment may produce these local consequences:

```text
A:
derived routing_warrant.valid
derived edge.admissible
one local TRANSITION_SUCCEEDED event
local projected phase OUTPUT_READY -> HANDOFF_ROUTED
one local ACCEPTED_FOR_TRANSPORT routed packet

B:
derived routing_warrant.valid
derived edge.admissible
no movement-admitting event
local projected phase remains OUTPUT_READY
no routed next-role object

both:
raw local evaluation receipts
pre/post event histories
pre/post projections
mechanical comparison
one final PASS | FAIL | REJECTED result
```

These are expected/allowed consequence classes, not pre-observed results.

## 9. PROTECTED NON-CONSEQUENCES

The future A/B authorization must not permit:

```text
repository main mutation
branch mutation
PR mutation
merge
generic Conductor modification
implementation modification
fixture repair
scientific-standing mutation
registry mutation
continuity-cursor mutation
SOL_A invocation
SOL_B invocation
Commander invocation
next-pressure execution
Phase-1 promotion
automatic routing beyond the one tested edge
```

Local routed-object production in A does not authorize invoking its recipient.

## 10. RESULT DOMAIN

```text
PASS
FAIL
REJECTED
```

Use only the frozen `COUNTERFEIT_WARRANT_001` scoring rules.

A valid unfavorable result remains retained evidence.

## 11. RETRY RULE

```text
No unfavorable valid rerun.
No selective replacement.
No automatic retry after a completed A or B realization.
```

A provider/tooling failure before a condition becomes experimentally consumed may be reported as apparatus failure only if the frozen scoring/administration rules support that classification. Workshop must not improvise a replacement execution route.

## 12. DEVIATION STOP RULE

Immediately stop if any of the following becomes true:

```text
implementation identity mismatch
fixture identity mismatch
common-basis mismatch
pre-state mismatch
condition label leaks into evaluator input
validity is supplied rather than derived
A or B receives an undeclared input
shared mutable A/B state appears
unexpected repository consequence occurs
apparatus requires repair to proceed
a second realization of a consumed condition would be required
```

Preserve partial receipts exactly.

## 13. CONTAMINATION RULE

The held-out claim is contaminated if, before the authorized matched-pair execution completes:

```text
A or B is realized outside the authorized run
held-out warrant validity is derived and retained by a disallowed apparatus path
held-out edge admissibility is derived and retained by a disallowed apparatus path
experimental movement is performed outside the authorized run
a consumed condition is rerun or selectively replaced
implementation changes after the basis is bound
the causal cut changes after the first condition is consumed
```

On contamination:

```text
STOP
retain contamination evidence
do not continue under the original held-out claim
```

## 14. RETAINED RECEIPTS

For each condition retain:

```text
implementation commit SHA
process fixture bytes + identity
role-output packet bytes + identity
routing warrant bytes + identity
initial event-history bytes + SHA-256
initial projection bytes + SHA-256
derived routing_warrant.valid
derived edge.admissible
pre-run event history
post-run event history
pre-run projection
post-run projection
routed next-role object or explicit absence
protected-surface comparison
raw exceptions/stdout/stderr where applicable
condition consumption status
```

For the pair retain:

```text
mechanical A/B preflight diff
mechanical A/B post-run diff
final PASS | FAIL | REJECTED
deviations
contamination status
```

## 15. NOT AUTHORIZED BY THIS ENVELOPE ARTIFACT

This file does not itself authorize A/B realization.

It does not authorize:

```text
repair
rerun
implementation modification
merge
next pressure
cursor movement
role auto-invocation
scientific-standing change
generalization
Phase-1 promotion
```

## 16. NEXT AUTHORITY OBJECT

The exact next decision is:

```text
EXPERIMENT EXECUTION AUTHORIZATION

PRESSURE_ID:
COUNTERFEIT_WARRANT_001

HOST:
CONDUCTOR_ROLE_HANDOFF_001

IMPLEMENTATION BASIS:
72ad130c35dc2be7b02cf7239d33d11de3af280e

CONDITIONS:
A then B

AUTHORIZED:
execute the frozen matched pair exactly once
retain the declared receipts
mechanically score PASS | FAIL | REJECTED

NOT AUTHORIZED:
repair
rerun
change apparatus
merge
generalize
execute P2
move cursors
invoke roles
change scientific standing
promote Phase 1
```

Until Reed explicitly authorizes that exact decision object:

```text
CONDITION_A_CONSUMED: NO
CONDITION_B_CONSUMED: NO
EXPERIMENTAL_RESULT: NONE
```

WORKSHOP STOPS.
