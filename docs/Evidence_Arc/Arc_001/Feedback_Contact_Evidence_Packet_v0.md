# Feedback Contact Evidence Packet v0

**Status:** Evidence checkpoint  
**Scope:** Post-proposal feedback/contact campaign and immediately adjacent relation-application findings  
**Purpose:** Freeze observed distinctions and claims before further matrix construction or architecture work.

---

## 1. Experimental Scope

This packet records evidence from the most recent symbolic pressures involving:

- relation application under opaque vs lexically loaded symbols,
- command-surface carry,
- feedback relation/contact/availability/event/admissibility,
- ecological resolution,
- downstream selection,
- fresh-run vs continuous-run replication.

It does **not** promote a final architecture.

It records only what the observed specimens currently support.

---

# 2. Relation-Application Findings

## 2.1 Lexically loaded membership specimen

Declared system:

```text
T_BOOL allowed values: TRUE, FALSE
PRECONDITION_RESULT bound to T_BOOL
PRECONDITION_RESULT = SATISFIED
SATISFIED IS_NOT_MEMBER_OF T_BOOL
```

Observed output:

```text
VALUE_MEMBER_OF_BOUND_TYPE: TRUE
FIELD_ADMISSIBLE: TRUE
```

Expected by declared topology:

```text
FALSE
FALSE
```

### Local consequence

The model failed the declared membership relation despite minimal compositional burden.

Candidate distinction:

```text
declared symbolic relation
!=
pretrained lexical-semantic relation
```

Local interpretation:

```text
lexically meaningful tokens can perturb explicit local topology
```

Standing:

**Supported by one direct contrast pair, not yet broadly replicated.**

---

## 2.2 Opaque membership control

Opaque system:

```text
T0 members: V0, V1
F0 bound to T0
F0 = V2
V2 IS_NOT_MEMBER_OF T0
```

Observed:

```text
VALUE_MEMBER_OF_BOUND_TYPE: FALSE
FIELD_ADMISSIBLE: FALSE
```

Result:

**PASS**

This supports the possibility that the earlier failure was driven by lexical-semantic interference rather than generic inability to apply the relation.

---

## 2.3 Alias-bearing opaque control

Opaque governing IDs were retained while aliases were added:

```text
T0 -> BOOL
V0 -> TRUE
V1 -> FALSE
V2 -> SATISFIED
```

The model still concluded that `F0: V2` was invalid because `V2` was not a member of `T0`.

Candidate distinction:

```text
lexical alias
!=
governing symbolic coordinate
```

Local interpretation:

Human-readable aliases did not override governing opaque IDs in this specimen.

Standing:

**Single-specimen support.**

---

# 3. Opaque Relation-Application Ladder

## R1 — Membership application

Observed:

```text
F0_VALUE: V2
F0_BOUND_TYPE: T0
F0_MEMBER_OF_BOUND_TYPE: FALSE
```

Result:

**PASS**

---

## R2 — Field admissibility

Observed:

```text
F0_VALUE: V2
F0_BOUND_TYPE: T0
F0_MEMBER_OF_BOUND_TYPE: FALSE
F0_ADMISSIBLE: FALSE
```

Result:

**PASS**

---

## R3 — Two-field independent application

System:

```text
T0 members: V0, V1
T1 members: V2, V3

F0 bound to T0
F1 bound to T1

F0 = V2
F1 = V2
```

Observed:

```text
F0_MEMBER_OF_BOUND_TYPE: FALSE
F0_ADMISSIBLE: FALSE
F1_MEMBER_OF_BOUND_TYPE: TRUE
F1_ADMISSIBLE: TRUE
```

Result:

**PASS**

Local support:

```text
membership application survives
field admissibility derivation survives
two-field isolation survives
```

---

## R4 — Expanded role surface without explicit carry

Requested:

```text
F0_ADMISSIBLE:
F0_DECISION_ROLE:
F1_ADMISSIBLE:
F1_DECISION_ROLE:
DECISIVE_FIELDS_ADMISSIBLE:
```

Observed:

```text
F0_ADMISSIBLE:
F0_DECISION_ROLE: DECISIVE
F1_ADMISSIBLE:
F1_DECISION_ROLE: NON_DECISIVE
DECISIVE_FIELDS_ADMISSIBLE:
```

The previously resolved admissibility values were omitted while newly introduced role fields were retained.

Important caution:

This is a failure of the **chat command/output surface**. It does not establish that hidden model reasoning state itself was lost.

Candidate distinction:

```text
prior inferred result
!=
explicitly represented active state
```

and more cautiously:

```text
reasoning continuity
!=
prompt-state continuity
```

Standing:

**Observed projection failure; no claim about hidden internal state.**

---

## R4B — Explicitly carried prior resolutions

Prior evaluations were supplied directly:

```text
F0_ADMISSIBLE: FALSE
F1_ADMISSIBLE: TRUE
```

Observed:

```text
F0_ADMISSIBLE: FALSE
F0_DECISION_ROLE: DECISIVE
F1_ADMISSIBLE: TRUE
F1_DECISION_ROLE: NON_DECISIVE
DECISIVE_FIELDS_ADMISSIBLE: FALSE
```

Result:

**PASS**

This localizes the earlier failure away from the role rule itself.

Candidate decomposition:

```text
relation evaluated
!=
resolution represented on current command surface
!=
relation composed
```

---

## R5 — Integrated selection with explicit current state

Observed:

```text
F0_ADMISSIBLE: FALSE
F1_ADMISSIBLE: TRUE
DECISIVE_FIELDS_ADMISSIBLE: FALSE
SELECTED_NOW: HOLD
```

Result:

**PASS**

Local consequence:

Given explicitly represented current state, the model correctly carried:

```text
inadmissible decisive field
→ decisive aggregate FALSE
→ HOLD
```

---

# 4. Feedback Contact Ladder

The feedback campaign pressured one boundary at a time.

Core chain:

```text
OPEN
→ CONTACT
→ AVAILABLE
→ EVENT
→ ADMISSIBLE
→ RESOLVED
→ SELECTED
```

The aim was to test whether each state could remain distinct from the next.

---

## CONTACT-001 — Open relation without contact

Observed:

```text
OPEN_FEEDBACK_RELATION: TRUE
CONTACT_ESTABLISHED: FALSE
SOURCE_AVAILABLE: FALSE
FEEDBACK_EVENT_PRESENT: FALSE
ECOLOGICAL_RESOLUTION_AVAILABLE: FALSE
P0_AFTER_EVALUATION: UNRESOLVED
SELECTED_NOW: FALSE
```

The contact geometry held, but `SELECTED_NOW` was flattened into boolean `FALSE` rather than the declared selection-state identity `HOLD`.

Earned distinction:

```text
selection predicate
!=
selected state/object identity
```

This prompted explicit typing of the selection field in later rounds.

---

## CONTACT-002 — Contact without source availability

Observed twice, including a fresh run:

```text
OPEN_FEEDBACK_RELATION: TRUE
CONTACT_ESTABLISHED: TRUE
SOURCE_AVAILABLE: FALSE
FEEDBACK_EVENT_PRESENT: FALSE
ECOLOGICAL_RESOLUTION_AVAILABLE: FALSE
P0_AFTER_EVALUATION: UNRESOLVED
SELECTED_NOW: HOLD
```

Result:

**PASS, replicated**

Local support:

```text
OPEN_FEEDBACK_RELATION
!=
CONTACT_ESTABLISHED
```

and:

```text
CONTACT_ESTABLISHED
!=
SOURCE_AVAILABLE
```

Contact alone did not resolve the target coordinate or trigger action.

---

## CONTACT-003 — Source available without event

Continuous and fresh runs both returned:

```text
OPEN_FEEDBACK_RELATION: TRUE
CONTACT_ESTABLISHED: TRUE
SOURCE_AVAILABLE: TRUE
FEEDBACK_EVENT_PRESENT: FALSE
ECOLOGICAL_RESOLUTION_AVAILABLE: FALSE
P0_AFTER_EVALUATION: UNRESOLVED
SELECTED_NOW: HOLD
```

Result:

**PASS, replicated across continuity conditions**

Local support:

```text
SOURCE_AVAILABLE
!=
FEEDBACK_EVENT_PRESENT
```

No phantom event was inferred from source reachability.

---

## CONTACT-004 — Event present but inadmissible

Continuous and fresh runs both returned:

```text
OPEN_FEEDBACK_RELATION: TRUE
CONTACT_ESTABLISHED: TRUE
SOURCE_AVAILABLE: TRUE
FEEDBACK_EVENT_PRESENT: TRUE
FEEDBACK_EVENT_ADMISSIBLE: FALSE
ECOLOGICAL_RESOLUTION_AVAILABLE: FALSE
P0_AFTER_EVALUATION: UNRESOLVED
SELECTED_NOW: HOLD
```

Result:

**PASS, replicated across continuity conditions**

Local support:

```text
FEEDBACK_EVENT_PRESENT
!=
FEEDBACK_EVENT_ADMISSIBLE
```

and:

```text
inadmissible event
does not modify target state
```

This strongly reinforces the earlier distinction:

```text
event presence
!=
event admissibility
```

---

## CONTACT-005 — Admissible event resolves local state

Fresh:

```text
OPEN_FEEDBACK_RELATION: TRUE
CONTACT_ESTABLISHED: TRUE
SOURCE_AVAILABLE: TRUE
FEEDBACK_EVENT_PRESENT: TRUE
FEEDBACK_EVENT_ADMISSIBLE: TRUE
ECOLOGICAL_RESOLUTION_AVAILABLE: TRUE
P0_AFTER_EVALUATION: TRUE
SELECTED_NOW: O0
```

Continuous:

```text
OPEN_FEEDBACK_RELATION: TRUE
CONTACT_ESTABLISHED: TRUE
SOURCE_AVAILABLE: TRUE
FEEDBACK_EVENT_PRESENT: TRUE
FEEDBACK_EVENT_ADMISSIBLE: TRUE
ECOLOGICAL_RESOLUTION_AVAILABLE: TRUE
P0_AFTER_EVALUATION: TRUE
SELECTED_NOW: O0
```

Result:

**PASS, replicated across continuity conditions**

This completes the positive end-to-end path:

```text
open relation
→ contact
→ available source
→ event present
→ event admissible
→ target resolved
→ operator selected
```

---

# 5. Evidentiary Distinction Set

The current feedback/contact campaign supports the following local non-collapse relations:

```text
OPEN_FEEDBACK_RELATION
!=
CONTACT_ESTABLISHED
```

```text
CONTACT_ESTABLISHED
!=
SOURCE_AVAILABLE
```

```text
SOURCE_AVAILABLE
!=
FEEDBACK_EVENT_PRESENT
```

```text
FEEDBACK_EVENT_PRESENT
!=
FEEDBACK_EVENT_ADMISSIBLE
```

```text
FEEDBACK_EVENT_ADMISSIBLE
!=
TARGET_RESOLVED
```

```text
TARGET_RESOLVED
!=
SELECTED_OBJECT_IDENTITY
```

Together:

```text
OPEN
!=
CONTACT
!=
AVAILABLE
!=
EVENT
!=
ADMISSIBLE
!=
RESOLVED
!=
SELECTED
```

Additional adjacent distinctions:

```text
declared symbolic relation
!=
pretrained lexical-semantic relation
```

```text
lexical alias
!=
governing symbolic coordinate
```

```text
prior inferred result
!=
explicitly represented active state
```

```text
relation evaluated
!=
resolution represented on current command surface
!=
relation composed
```

```text
selection occurred
!=
selected object identity
```

---

# 6. Claim Standing

## Replicated local evidence

The following survived both continuous and fresh runs:

```text
CONTACT_ESTABLISHED != SOURCE_AVAILABLE
SOURCE_AVAILABLE != FEEDBACK_EVENT_PRESENT
FEEDBACK_EVENT_PRESENT != FEEDBACK_EVENT_ADMISSIBLE
inadmissible event does not resolve P0
admissible event can resolve P0
resolved P0 can alter selection from HOLD to O0
```

The full positive contact-to-selection sequence also replicated.

---

## Supported but not yet broadly replicated

```text
declared symbolic relation != pretrained lexical-semantic relation
lexical alias != governing symbolic coordinate
explicit current-state representation improves downstream composition
```

---

## Candidate / unresolved

The following should not yet be promoted beyond candidate standing:

```text
lexical semantics are the general cause of CARRIER-003
materialized prompt-state continuity is required in all multi-step tasks
fresh vs continuous context is generally behaviorally invariant
contact chain alone is sufficient for ecological navigation
```

---

# 7. Consequence of the Campaign

The campaign sharpens the earlier ecological claim.

Previously:

```text
local closure
!=
ecological closure
```

Now there is an experimentally decomposed path showing how ecological reopening can occur:

```text
local unresolved state
→ open feedback relation
→ actual contact
→ source availability
→ emitted event
→ admissibility
→ local resolution
→ changed selection
```

The important consequence is that **potential feedback topology and realized feedback passage are not the same thing**.

An ecology can therefore be falsely modeled in either direction:

```text
FALSE CLOSURE:
a viable feedback path exists but is not represented or consulted
```

```text
FALSE OPENNESS:
a represented feedback path is treated as presently usable despite absent contact,
availability, event, or admissibility
```

The contact ladder gives these failures a concrete intermediate structure.

---

# 8. Immediate Next Pressure Candidates

Do not widen architecture yet.

Highest-value next pressures:

### A. Conflicting sources

Two available sources each emit admissible events with conflicting values for the same coordinate.

Pressure:

```text
source identity
+ evidence conflict
+ resolution policy
+ selection consequence
```

Question:

```text
what additional distinction is required before either event may govern?
```

---

### B. Governing vs non-governing event defects

Repeat event admission while perturbing one field at a time:

```text
SOURCE
TARGET_COORDINATE
OBSERVED_VALUE
EVIDENCE_STATUS
AUTHORITY metadata
ancillary metadata
```

Question:

```text
which coordinates actually determine admissibility?
```

---

### C. Distinction interaction matrix

Build a matrix over currently earned distinctions and classify pairwise relations:

```text
independent
prerequisite
mutually constraining
same axis
false split
admissibility-governing
consequence-only
event-budget-sensitive
emergence-sensitive
```

Goal:

```text
discover admissibility geometry
rather than merely catalog distinctions
```

---

# 9. Freeze

Current evidence supports the following compact freeze:

```text
A feedback relation is not equivalent to contact.

Contact is not equivalent to present source availability.

Availability is not equivalent to event passage.

Event passage is not equivalent to admissibility.

Admissibility is not equivalent to resolution.

Resolution is not equivalent to selected object identity.

When an admissible external event resolves a previously unresolved coordinate,
the local action surface can change.

The path from ecological possibility to local consequence is therefore
multi-stage and pressure-sensitive.

Each stage must earn its own standing.
```

This packet should be treated as a checkpoint for subsequent matrix construction, not as final runtime architecture.
