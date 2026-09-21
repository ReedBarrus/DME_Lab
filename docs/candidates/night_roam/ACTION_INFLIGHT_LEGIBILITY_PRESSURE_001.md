# ACTION_INFLIGHT_LEGIBILITY_PRESSURE_001

## Status

```text
NIGHT ROAM PRESSURE DESIGN
IMPLEMENTATION REPAIR: NONE
SCIENTIFIC PROMOTION: NONE
AUTHORITY EFFECT: NONE
EXECUTION EFFECT: NONE
```

## Exact observed basis

Source commit inspected:

```text
d7ae8134cf7b41610b6fc3da57ecd93c9bb53986
```

Current `src/cockpit/action_surface.py` admits these routing event types:

```text
PROCESS_REGISTERED
TRANSITION_REQUESTED
TRANSITION_STARTED
TRANSITION_SUCCEEDED
TRANSITION_FAILED
ROLE_JUDGMENT_REQUIRED
HUMAN_DECISION_REQUIRED
HUMAN_DECISION_RECORDED
BLOCKED
PACKET_ACCEPTED_FOR_TRANSPORT
```

Its `_apply` reconstruction changes routing state for registration, success,
failure, role judgment, human decision, and blocker events. It does not change
routing state for:

```text
TRANSITION_REQUESTED
TRANSITION_STARTED
PACKET_ACCEPTED_FOR_TRANSPORT
```

Those events are nevertheless consumed and become `last_event_type`.

The action projector then derives `declared_next_action` from the reconstructed
phase/status. Therefore the current implementation can consume evidence that a
transition was requested or started while still rendering the phase's declared
transition with an eligibility such as `MECHANICAL_ROUTING_AVAILABLE` or
`MECHANICAL_CAPABILITY_REQUIRED`.

This is an implementation observation only. It does **not** establish that the
rendered posture is wrong, because the current committed basis inspected here
does not settle the intended semantics of requested/started/transport-accepted
states.

## Proposed distinction

```text
NEXT DECLARED TRANSITION
!=
TRANSITION CURRENTLY AVAILABLE TO REQUEST
!=
TRANSITION ALREADY IN FLIGHT
```

A second related cut is:

```text
EVENT CONSUMED BY PROJECTION
!=
EVENT SEMANTICALLY ACCOUNTED FOR BY ROUTING RECONSTRUCTION
```

## Why current evidence does not settle it

The Action Surface contract establishes:

```text
ACTION VISIBLE
!=
ACTION SELECTED
!=
ACTION AUTHORIZED
!=
ACTION EXECUTED
```

and requires declared routing position to be reconstructed from the committed
event vocabulary. The inspected implementation, however, does not assign a
routing-state effect to every admitted event type. From this alone we cannot
infer whether `TRANSITION_REQUESTED`, `TRANSITION_STARTED`, or
`PACKET_ACCEPTED_FOR_TRANSPORT` are intentionally observational-only events,
or whether one or more must suppress/reclassify next-action eligibility while
in flight.

Changing implementation before resolving that relation would risk inventing
Conductor semantics from Cockpit convenience.

## Smallest discriminating pressure

Use one synthetic registered process with a single declared mechanical
transition `T1` from phase `P0` to `P1`. Hold the process specification and
source commit constant. Vary only the committed routing event suffix.

### Cells

```text
A — REGISTERED ONLY
PROCESS_REGISTERED

B — REQUESTED
PROCESS_REGISTERED
TRANSITION_REQUESTED(T1)

C — STARTED
PROCESS_REGISTERED
TRANSITION_REQUESTED(T1)
TRANSITION_STARTED(T1)

D — SUCCEEDED CONTROL
PROCESS_REGISTERED
TRANSITION_REQUESTED(T1)
TRANSITION_STARTED(T1)
TRANSITION_SUCCEEDED(T1, P0 -> P1)
```

Optional separate transport cell only if the governing Conductor contract
establishes that `PACKET_ACCEPTED_FOR_TRANSPORT` belongs to the same transition
lifecycle. Do not assume that relation merely because the event is admitted by
the Action Surface parser.

## Observables

For each cell record only:

```text
phase
routing_status
last_event_type
declared_next_action.transition_id
declared_next_action.eligibility
event_count_consumed
projection boundary flags
```

Also verify that no cell creates authority, selects an action, advances a
cursor, or performs execution.

## Outcome interpretation / claim ceiling

If B/C intentionally retain the same availability posture as A under an exact
Conductor contract, earn only:

```text
REQUEST/START EVIDENCE
DOES NOT ALTER ACTION-SURFACE ELIGIBILITY
IN TESTED TRANSITION CLASS
```

If B/C require a distinct in-flight posture, earn only:

```text
DECLARED NEXT TRANSITION
!=
CURRENTLY REQUESTABLE TRANSITION
IN TESTED TRANSITION CLASS
```

If requested and started differ from one another, preserve that finer relation;
do not collapse both into a generic `IN_FLIGHT` state without evidence.

If governing semantics remain ambiguous, earn no runtime change. Retain the
pressure as blocked on exact lifecycle semantics.

## Dangerous neighboring inference

Do **not** infer any of the following from this pressure:

```text
TRANSITION_STARTED == EXTERNAL CONSEQUENCE OCCURRED
TRANSITION_REQUESTED == AUTHORIZED
PACKET_ACCEPTED_FOR_TRANSPORT == TRANSITION_STARTED
IN_FLIGHT == LIVE PROCESS
COCKPIT ROUTING POSTURE == EXECUTION STATE
```

The Cockpit remains a read-only projection. This pressure must not turn routing
reconstruction into consequence reconstruction.

## Disposition

```text
FUTURE CAMPAIGN VALUE: HIGH
IMPLEMENTATION CHANGE NOW: HELD
REASON: exact lifecycle semantics are not yet mechanically established
```

The smallest next step is to locate/freeze the authoritative Conductor event
lifecycle semantics for `TRANSITION_REQUESTED` and `TRANSITION_STARTED`, then
run the four-cell pressure before changing Action Surface behavior.
