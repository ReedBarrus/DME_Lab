# DRACI_EVENT_v0

```text
OBJECT_TYPE:
CANDIDATE_ATLAS_EVENT

OBJECT_ID:
DRACI_EVENT_v0

STATUS:
PROVISIONAL
LOCAL
FRAME_RELATIVE
SET_VALUED_FOOTPRINT

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCHEMA_FREEZE:
NO
```

## 0. Purpose

Represent a consequential transition between local Atlas snapshots without
forcing an event into one cell or confusing action origin with total consequence.

## 1. Event identity

```text
EVENT_ID:
...

SOURCE_FRAME:
...

TARGET_FRAME:
...

TEMPORAL_ANCHOR:
...

BASIS:
...
```

Freeze:

```text
EVENT_ID
!=
EVENT CONTENT
!=
EVENT CONSEQUENCE CLOSURE
```

## 2. Trigger / transformation

```text
TRIGGER:
...

TRANSFORMATION:
...
```

Distinguish:

```text
TRIGGER
!=
REQUEST
!=
SELECTED OPERATION
!=
EXECUTION
!=
CONSEQUENCE
```

unless a specific mechanism establishes equivalence.

## 3. Event footprint

```text
EVENT_FOOTPRINT
⊆
{
cells,
temporal membranes,
cross-relational edges,
higher-order couplings
}
```

Therefore:

```text
ONE EVENT
MAY OCCUPY MANY CELLS

ONE CELL
MAY RECEIVE MANY EVENTS
```

Freeze:

```text
ORIGINATING ACTION LOCATION
!=
EVENT FOOTPRINT
!=
FULL CONSEQUENCE FOOTPRINT
```

## 4. Event occurrence vs consequence closure

An event may occur before all of its consequences are closed or observed.

Where a mechanism earns the standing, represent separately:

```text
EVENT STATUS:
PROPOSED | OCCURRED | UNRESOLVED | ...

CONSEQUENCE STATUS:
OPEN | PARTIALLY_OBSERVED | CLOSED | UNRESOLVED | ...
```

Freeze:

```text
EVENT OCCURRED
!=
EVENT CONSEQUENCE CLOSED

INVOCATION ENDED
!=
EFFECT ENDED
```

Do not install statuses a mechanism has not earned.

## 5. Differential

Record only consequentially relevant changes:

```text
CHANGED CONFIGURATIONS:
...

CHANGED RELATIONS:
...

CHANGED STANDINGS:
...

CHANGED CURRENTNESS:
...

CHANGED AUTHORITY:
...

CHANGED REALIZATION SUPPORT:
...

OTHER:
...
```

No-change dimensions may remain implicit unless their conservation is itself
evidentially important.

## 6. Consequence / observation depth

```text
EXPECTED CONSEQUENCE:
...

REALIZED CONSEQUENCE:
...

OBSERVED CONSEQUENCE:
...

EVIDENCE:
...

QUALIFIED INTERPRETATION:
...
```

Preserve:

```text
EXPECTED
!=
REALIZED
!=
OBSERVED
!=
EVIDENCED
!=
QUALIFIED
```

## 7. Lineage

```text
PREDECESSOR REFERENCES:
...

SUCCESSOR REFERENCES:
...

DEPENDENCY REFERENCES:
...

CORRESPONDENCE BASIS:
...
```

```text
LINEAGE
=
qualified relational provenance
and dependency correspondence
across the event
```

Freeze:

```text
LINEAGE
!=
TRAJECTORY
```

## 8. Sparse observation / transition gaps

A source and target frame do not prove that the intervening event sequence was
fully observed.

Represent explicitly where needed:

```text
TRANSITION_GAP
=
a bounded interval whose exact event path is not established
```

Freeze:

```text
OBSERVATION SPARSITY
!=
EVENT ABSENCE

UNOBSERVED INTERVAL
!=
UNKNOWN EVERYTHING
```

Known invariants, lineage bounds, or consequence constraints may survive across
a transition gap without fabricating an event.

An inferred transition must remain:

```text
EVENT_HYPOTHESIS
```

until evidence earns stronger standing.

## 9. Recovery

```text
VIABILITY EFFECT:
...

CORRECTIVE PATH:
...

RECOVERY COVERAGE:
...

UNCOVERED REGION CREATED / REMOVED:
...
```

An event may improve, degrade, or leave unchanged future recoverability.

## 10. Trajectory compilation

```text
FRAME₀
→ EVENT₁
→ FRAME₁
→ EVENT₂
→ FRAME₂
→ ...
```

produces:

```text
RECORDED LOCAL TRAJECTORY
```

Preserve:

```text
RECORDED TRAJECTORY
!=
PROJECTED TRAJECTORY
!=
SIMULATED TRAJECTORY
```

## 11. Snapshot threshold

An event MAY trigger a fresh snapshot when a locally declared consequential
threshold is crossed.

Candidate threshold families include:

```text
identity
currentness
authority
admission
execution
lifecycle
observation
qualification
recovery
realization / hosting support
```

No universal threshold set is installed.

## 12. Scientific pressure

Pressure should determine:

```text
which events require snapshots
how much information a snapshot must retain
how sparse observation may become before reconstruction degrades
how sparse observation may become before recovery standing degrades
which local frames compose reliably
when simulation diverges from recorded trajectory
```

The Lab determines these experimentally.

The Atlas records the surviving relations.

## 13. Disposition

```text
CANDIDATE MINIMUM ATLAS EVENT OBJECT

PRESSURE BEFORE SCHEMA FREEZE
```
