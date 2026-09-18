# Authority Routing Reconciliation Dry Run v0

## Status

**NON-AUTHORITATIVE DRY RUN**

This pass does not modify `AGENT_CONTEXT.md`,
`DEVELOPMENT_PRESSURE_MAP.md`, scientific standing, objective wording,
pressure activation, or execution authority.

Basis:

`a4465a6615c0d591101a5f4482397280dd913f7b`
— `Record constitutional claim inventory audit`.

## Pressure

Can the two authority-routing wounds identified by the constitutional claim
inventory be repaired by minimal wording changes alone, while preserving:

```text
evidence != adjudication
adjudication != projection
interpretation != authorization
authorization != execution
```

and without changing scientific standing?

The two wounds are:

1. `AGENT_CONTEXT.md` mixes startup/navigation order with evidential
   precedence.
2. `DEVELOPMENT_PRESSURE_MAP.md` groups evidence, adjudicated standing, and
   derived projections under the phrase "authoritative scientific standing."

## Candidate repair A — AGENT_CONTEXT.md

Replace the ambiguous combined heading with two distinct responsibilities.

### Startup / navigation order

```text
1. PROJECT_STATE.md
2. README.md and WORKFLOW.md
3. relevant active contract / projection
4. relevant decisions, traces, tests, constraints, and source
5. current conversation when needed
6. DME_Theory lineage only when useful
```

This is a reading/navigation order only.

### Evidential precedence

```text
Direct retained evidence and executable behavior
↓
Adjudicated bounded standing
↓
Scoped contracts / conserved constraints
↓
Derived current-state and navigation projections
↓
Conversation / orientation
↓
Lineage
```

Qualifier:

```text
evidential precedence
!=
automatic interpretation or adjudication
```

Direct evidence may contradict a derived projection, but raw evidence does not
silently become adjudicated standing.

## Candidate repair B — DEVELOPMENT_PRESSURE_MAP.md

Replace the ambiguous sentence:

> Authoritative scientific standing remains in committed evidence, decisions,
> traces, tests, PROJECT_STATE.md, and PRESSURE_RESOLUTION_MAP.md.

with:

> Scientific standing is grounded in committed evidence and adjudicated
> decision records.

> `PROJECT_STATE.md` and `PRESSURE_RESOLUTION_MAP.md` are derived
> current-state and navigation projections over that standing. They do not
> establish it.

No other map semantics change.

## Candidate routing surface

The two repairs jointly imply the following current routing:

```text
DIRECT EVIDENCE
      ↓
ADJUDICATED STANDING
      ↓
CURRENT-STATE / NAVIGATION PROJECTION
```

and independently:

```text
INTERPRETATION
      ↓
AUTHORIZATION
      ↓
EXECUTION
```

These are routing distinctions, not universal scientific ontology.

## Adversarial reconstruction cases

The expected consequence is intentionally not encoded as a new rule in either
candidate repair. The cases ask whether the repaired routing is sufficient to
derive it.

### Case A — Projection contradicted by evidence

Given:

```text
PROJECT_STATE says X.

Direct retained evidence under the relevant basis establishes not-X.
```

Questions:

- What is evidentially warranted?
- What is current adjudicated standing?
- May PROJECT_STATE continue to govern X against that evidence?
- What must occur before current standing and projection are updated?

### Commander reconstruction

```text
Direct evidence defeats X as an evidentially warranted projection claim.

The contradiction does not by itself create a new adjudicated standing.

The current projection cannot legitimately override the contradictory direct
evidence.

New standing requires adjudication.

After adjudication, the current-state projection may be updated to reflect the
new standing.
```

Recovered boundary:

```text
evidence
!=
adjudicated standing
!=
current-state projection
```

### Case B — Interpretation without authorization

Given:

```text
Council evaluates the evidence and recommends operation Y.

Both twins agree.

No Executive authorization exists.
```

Questions:

- What standing does the recommendation have?
- May Workshop execute Y?
- Does Twin agreement change execution authority?

### Commander reconstruction

```text
The recommendation is interpretation / candidate action.

No Executive authorization exists.

Workshop may not execute Y.

Twin agreement does not create execution authority.
```

Recovered boundary:

```text
interpretation
!=
authorization
!=
execution
```

### Case C — Reachable pressure without activation

Given:

```text
PRESSURE_RESOLUTION_MAP displays pressure Z as reachable.

No pressure has been explicitly activated.
```

Questions:

- Is Z active?
- May an executor begin work on Z?
- Does map currency create authority?

### Commander reconstruction

```text
Z is reachable, not active.

An executor may not begin work merely because the map exposes Z.

Map currency does not create scientific or execution authority.
```

Recovered boundary:

```text
reachability
!=
activation
!=
authorization
```

### Case D — Historical adjudication contradicted by new evidence

Given:

```text
A historical decision records P under basis B0.

New retained evidence under basis B1 conflicts with P.
```

Questions:

- May the old decision be rewritten?
- Does the new evidence simply replace P?
- What must remain recoverable?
- What changes if a new adjudication is warranted?

### Commander reconstruction

```text
The old decision remains historical adjudicated lineage under B0.

The new evidence remains separately retained under B1.

The new evidence does not silently erase or rewrite the historical decision.

A new adjudication may establish changed current standing if warranted.

Current projections may then change while the prior adjudication and basis
remain recoverable.
```

Recovered boundaries:

```text
new evidence
!=
permission to erase old standing

old standing
!=
eternally current standing

supersession
!=
historical invalidation
```

## Internal reconstruction result

The candidate repairs are sufficient for Commander to recover all four
authority consequences without adding a new authority tier, schema, runtime
type, or document class.

The dry run therefore supports:

```text
WOUND 1:
BOUNDED REPAIR AVAILABLE

WOUND 2:
BOUNDED REPAIR AVAILABLE

SCIENTIFIC STANDING CHANGE:
NONE REQUIRED

OBJECTIVE CHANGE:
NONE REQUIRED

METHOD SEMANTICS CHANGE:
NONE REQUIRED

NEW ONTOLOGY:
NONE REQUIRED

AUTHORITY ROUTING:
INTERNALLY RECONSTRUCTIBLE

LIVE FILE MUTATION:
NOT AUTHORIZED BY THIS RECORD
```

## What is not established

This pass is not an independent fresh-observer test because the same Commander
surface that helped formulate the candidate repairs also evaluated the cases.

Therefore it does **not** establish:

```text
independent observer reconstruction
model-independent recoverability
final authority migration readiness
four-root compression success
```

The stronger test still owed is:

> Give only the candidate repaired routing language and adversarial cases to an
> independent observer that did not construct the repairs. Require it to recover
> evidence, standing, projection, interpretation, authorization, execution,
> lineage, and the next surface that should change.

## Candidate repository-level implication

If an independent observer reproduces the authority consequences above, then
the following candidate repository distinction becomes pressureable:

```text
RICH MEMORY GRAPH
!=
NARROW AUTHORITY SPINE
```

with the stronger hypothesis:

> Repository memory may grow without requiring proportional growth in the live
> governing surface, provided consequential evidence, lineage, scope,
> unresolvedness, and authority distinctions remain recoverable.

This dry run does not promote that hypothesis.

## Smallest next pressure

**Independent authority reconstruction.**

Input only:

- Candidate repair A
- Candidate repair B
- Cases A-D

Do not provide the Commander reconstructions.

Pass only if the independent observer correctly reconstructs:

- direct evidence versus standing;
- standing versus projection;
- interpretation versus authorization;
- authorization versus execution;
- reachability versus activation;
- supersession without historical erasure;
- which surface may change next after adjudication.

If that passes, the two routing wounds are boundedly repairable and live
mutation pressure becomes legitimately reachable.

If it fails, preserve the exact ambiguity and do not broaden the framework.
