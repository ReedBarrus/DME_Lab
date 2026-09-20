# COCKPIT_CONTROL_ADAPTER_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

READ SIDE:
LIVE_RUNTIME_PROJECTION_001 remains separate

WRITE SIDE:
typed Cockpit control adapter

VERBS:
FOCUS
ASSIGN
RELEASE
RING

AUTHORIZE:
ABSENT

STOP:
ABSENT

GENERALIZED REVIEW:
ABSENT

DIRECT CONTROLLER MUTATION:
NONE
```

## Sole question

```text
CAN AN EXPLICIT HUMAN COCKPIT ACTION

MATERIALIZE ONE EXACT
ALREADY-QUALIFIED DURABLE OBJECT

WITHOUT THE COCKPIT
ACQUIRING DIRECT CONTROLLER MUTATION,
PRIORITY,
WORK SELECTION,
OR AUTHORITY?
```

## Membrane

```text
READ SIDE
LIVE_RUNTIME_PROJECTION_001
        │
        │ observation only
        │
────────┼────────────────────────
        │
        │ explicit human gesture
        ▼
COCKPIT_CONTROL_ADAPTER_001
        │
        ├─ FOCUS
        ├─ ASSIGN
        ├─ RELEASE
        └─ RING
        │
        ▼
existing qualified stores
```

The adapter has no controller database input.

RING may retain an already-qualified `manual_bell_v0` and its exact
assignment-bound `wake_opportunity_v0`, but it does not invoke
`BoundedReentryRunner` and does not occupy a seat.

## Interaction contract

Every control gesture follows:

```text
INTENT
↓
PREVIEW EXACT OBJECT BYTES
↓
PREVIEW SHA-256
↓
EXPLICIT REED CONFIRMATION
↓
REBUILD AGAINST CURRENT STATE
↓
REQUIRE SAME PREVIEW IDENTITY
↓
APPEND THROUGH EXISTING QUALIFIED STORE
↓
RETURN MECHANICAL RESULT
```

Therefore:

```text
PREVIEW
!=
APPEND

BUTTON
!=
MAGIC ACTION

PREVIEW WAS VALID
!=
PREVIEW IS STILL CURRENT
```

If the current basis or underlying selected/assignment state changes between
preview and confirmation, the commit is rejected and a fresh preview is
required.

## Four verbs

### FOCUS

```text
human names exact:
campaign
request

adapter previews:
envelope_selection_v0

commit:
SelectionStore.append()
```

No request is selected automatically.

### ASSIGN

```text
human names exact:
campaign
request
seat
preparation_kind

adapter derives:
the one exact current selection for that request

adapter previews:
preparation_assignment_v0

commit:
AssignmentStore.append()
```

The adapter does not choose a seat or preparation kind.

### RELEASE

```text
human names exact:
campaign
assignment

adapter resolves:
the exact current allocation

adapter previews:
preparation_assignment_v0
assignment_kind = ASSIGNMENT_RELEASED

commit:
AssignmentStore.append()
```

Release remains distinct from satisfaction.

### RING

```text
human names exact:
campaign
assignment

precondition:
exact assignment projection
= OUTSTANDING
wake_eligible = true

adapter previews:
manual_bell_v0
+
exact wake_opportunity_v0

commit:
WakeSourceStore.emit()

then:
STOP
```

The adapter does not invoke bounded reentry.

```text
COCKPIT RING
!=
WAKE SOURCE RAN MAYA
```

## Exact gesture identity

The browser supplies a gesture identity used only to derive object labels.

```text
FOCUS:
CCA-S-<gesture>

ASSIGN:
CCA-A-<gesture>

RELEASE:
CCA-R-<gesture>

RING:
CCA-B-<gesture>
CCA-W-<gesture>
```

Gesture identity does not choose work, priority, authority, or seat.

## Control UI

The observer page now has two separate roots:

```text
#runtime-root
#control-root
```

and two separate modules:

```text
runtime_live.mjs
control_live.mjs
```

The read-side runtime module contains no control endpoint.

The control panel is enabled only when an explicit `?control=<base-url>`
adapter endpoint is supplied.

The control panel displays the exact preview JSON and preview SHA before the
confirmation button may append it.

## Dogfood specimen

The pressure suite uses the real
`COCKPIT_OPERATING_SPACE_001` candidate campaign semantics, re-based only to
the isolated test Git world so applicability can be mechanically current.

The specimen pressures real Cockpit relations rather than generic `OBJ_A`
semantics:

```text
COS-R1
COCKPIT_INTERACTION != DIRECT_CONTROLLER_MUTATION

COS-R2
HUMAN_READABLE_ASSIGNMENT_DISPLAY != QUEUE_SEMANTICS
```

The first full specimen is:

```text
COCKPIT_OPERATING_SPACE_001
↓
COS-E1
↓
FOCUS
↓
ASSIGN MAYA / RESOLVE_REFS
↓
RING
↓
exact wake opportunity retained
↓
CONTROL ADAPTER STOPS
↓
external BOUNDED_REENTRY runner answers opportunity
↓
one preparation receipt
↓
MAYA AVAILABLE
```

Assignment satisfaction remains a separate existing relation.

## Pressure cells

```text
C1  FOCUS preview → exact selection commit
C2  ASSIGN preview → exact assignment commit
C3  RELEASE → exact allocation release only
C4  RING → exact bell + opportunity; no wake
C5  explicit REED confirmation + exact preview SHA required
C6  world move after preview → commit rejected
C7  two eligible assignments → only named assignment rings
C8  two MAYA assignments → no queue / second bell inferred
C9  unqualified verbs / extra intent semantics rejected
C10 all four verbs leave controller store untouched
C11 ring then external reentry proves adapter did not run MAYA
C12 selection change after preview forces re-preview
```

## Hard boundaries

```text
LIVE PROJECTION
!=
CONTROL PATH

COCKPIT CONTROL
!=
DIRECT CONTROLLER MUTATION

HUMAN INTENT
!=
DURABLE OBJECT

PREVIEW
!=
APPEND

FOCUS
!=
PRIORITY

ASSIGN
!=
WORK SELECTION BY COCKPIT

RING
!=
WAKE ACCEPTANCE

WAKE OPPORTUNITY
!=
SEAT OCCUPANCY

CONTROL RESULT
!=
SCIENTIFIC STANDING
```

## Claim ceiling

A passing candidate may support only that the tested separate Cockpit control
adapter can preview and, after explicit confirmation, append the four named
already-qualified object relations against current durable state while
preserving exact identity and leaving the controller store untouched.

It does not establish:

```text
authentication security
external kill
capability admission
runtime sandboxing
scheduler correctness
automatic wake policy
automatic assignment
automatic work selection
general review routing
authority granting
standing promotion
production deployment safety
```

Those remain outside this membrane.
