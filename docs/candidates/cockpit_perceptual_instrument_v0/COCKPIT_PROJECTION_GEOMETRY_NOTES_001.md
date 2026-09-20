# COCKPIT_PROJECTION_GEOMETRY_NOTES_001

## Purpose

This note exists to project a small set of earned perceptual invariants onto
future Cockpit work without prematurely freezing one visual style.

The Cockpit should not be treated as:

```text
one dashboard
one graph
one archive
one text surface
```

It should be treated as an instrument for moving among multiple projections of
one addressable ecology.

The rendering may evolve.

The semantic cuts below should not silently collapse.

---

## Core invariant set

```text
ADDRESS
must survive representation change

CONSEQUENCE
!=
TOPOLOGY

OBSERVATION
!=
EVALUATION
!=
AUTHORITY

GEOMETRY
must not invent relations

SCREEN POSITION
!=
SEMANTIC PRIORITY
```

These are the minimum perceptual scars future Cockpit attempts should preserve.

If future rendering cannot preserve one of these cuts, that is pressure on the
design rather than permission to blur the relation.

---

## One ecology, many projections

The Atlas is not one picture of DME.

```text
THE ATLAS
=
A FAMILY OF PROJECTIONS
OVER ONE ADDRESSABLE ECOLOGY
```

Different projections answer different questions.

### Consequence

```text
what is happening?
what is moving?
what is live?
what can I engage?
where are effects flowing?
what may happen next?
```

Possible native material:

```text
campaigns
requests
attention
seats
occupants
assignments
bells
wake opportunities
runtime processes
receipts
incidents
authority / capability boundaries
consequence transitions
```

### Topology

```text
what does this mean?
what supports it?
what is it related to?
where did it come from?
what remains unresolved?
```

Possible native material:

```text
dependencies
distinctions
claims
lineage
basis
provenance
standing
evidence
pressure history
missing discriminators
residue
constraints
scars
```

Neither projection is the master truth.

```text
SAME ECOLOGY
!=
SAME REPRESENTATION
```

---

## Address persistence

The most important navigation requirement is:

```text
SWITCH REPRESENTATION
WITHOUT LOSING ADDRESS
```

If the user selects:

```text
campaign
relation
seat
assignment
receipt
incident
request
occupant
process
or another addressable object
```

then switching projection should preserve that object coordinate whenever the
destination representation can express it.

If the destination projection cannot express it:

```text
ADDRESS LOSS
MUST BE EXPLICIT
```

Never silently substitute a nearby object.

```text
REPRESENTATION SWITCH
!=
OBJECT RESELECTION
```

---

## Orthogonal lenses

CONSEQUENCE and TOPOLOGY may be the two primary geometries.

A second dimension may be supplied by relation lenses:

```text
OBSERVATION
EVALUATION
AUTHORITY
```

These should remain distinct even if one visual mode eventually overlays them.

### Observation

```text
what was seen?
what was retained?
what evidence entered the model?
what event actually occurred?
```

### Evaluation

```text
what did the evidence warrant?
what standing was earned?
what interpretation survived pressure?
what remains unresolved?
```

### Authority

```text
what consequence is permitted?
what capability is available?
who may act?
what effect boundary is open or closed?
```

The important cut:

```text
OBSERVED
!=
EVALUATED

EVALUATED
!=
AUTHORIZED

AUTHORIZED
!=
EXECUTED
```

Future rendering may realize these as:

```text
overlays
depth planes
radial channels
field layers
camera modes
color / texture families
edge classes
animated envelopes
or something not yet designed
```

Do not freeze the rendering before use earns it.

---

## Time is a first-class rendering dimension

A static Atlas risks becoming another archive.

The ecology is temporal.

The rendering should eventually make changes through time legible without
inventing causality.

Potential temporal material includes:

```text
selection begins / ends
assignment created / satisfied / released
bell emitted
wake opportunity appears
seat becomes occupied
unit starts
receipt appears
basis moves
warrant becomes stale
revalidation restores applicability
campaign becomes live / blocked
incident occurs
standing changes
handoff occurs
```

Animation can make these transformations perceptible as configuration change
rather than forcing the user to compare text snapshots.

Key scar:

```text
ANIMATION
!=
CAUSAL PROOF
```

Motion should only render transitions already grounded by durable events or
derived relations.

Do not animate speculative causal flow simply because it looks explanatory.

```text
VISIBLE TRANSITION
must have
TRACEABLE TRANSITION BASIS
```

---

## Rendering through time

A useful mental model:

```text
OBSERVATION
↓
EVALUATION
↓
AUTHORITY
↓
CONSEQUENCE
↓
NEW OBSERVATION
```

This is not a claim that every event follows one universal linear pipeline.

It is a perceptual loop for exploring how retained evidence, judgment,
permission, and consequence relate through time.

CONSEQUENCE view may emphasize temporal change:

```text
what just changed?
what is currently active?
what path is energized?
what is blocked?
what object is waiting?
```

TOPOLOGY may emphasize structural persistence:

```text
what remained invariant?
what dependency still exists?
what provenance supports this?
what historical relation changed standing?
```

The user should be able to move between temporal and structural understanding
without losing the selected coordinate.

---

## Geometry must remain epistemically humble

Spatial representation is powerful enough to lie accidentally.

Therefore:

```text
PROXIMITY
!=
RELATION

SIZE
!=
IMPORTANCE

CENTER
!=
PRIORITY

UP
!=
SUPERIOR

BRIGHTER
!=
MORE TRUE

MOTION
!=
CAUSALITY

CLUSTER MEMBERSHIP
!=
IDENTITY

SCREEN ORDER
!=
QUEUE ORDER
```

Any geometric property with semantic meaning should have a declared basis.

If layout is purely compositional:

```text
LAYOUT IS NON-SEMANTIC
```

should remain recoverable from the interface.

---

## Addressed interaction

Spatial navigation becomes useful when interaction also preserves address.

Potential operations:

```text
POINT
SELECT
MULTISELECT
ZOOM
COMPARE
CHAT
FOCUS
ASSIGN
RELEASE
RING
REVIEW
HANDOFF
INSPECT
```

The available operation should depend on the current objects and qualified
relations:

```text
SELECTED OBJECTS
+
CURRENT RELATIONS
+
CURRENT AUTHORITY
=
AVAILABLE AFFORDANCES
```

But:

```text
UI AFFORDANCE
!=
AUTHORITY GRANT
```

The UI may preview a possible consequence.

The existing causal membrane still decides whether the action is admissible.

---

## Addressed chat

Chat remains a useful cognitive operator.

It should not require abandoning the Atlas coordinate.

```text
SELECT OBJECT(S)
↓
CHAT
↓
CONVERSATION RECEIVES
EXACT ADDRESS CONTEXT
```

The addressing packet should be visible and inspectable.

Example:

```text
seat:
MAYA

campaign:
COCKPIT_OPERATING_SPACE_001

relation:
COS-R2

assignment:
A17

basis:
B
```

Scar:

```text
ADDRESS SUPPLIED
!=
CLAIM ESTABLISHED
```

The chat model receives coordinate context.

It does not receive permission to treat every nearby projection as truth.

---

## Scale

The Atlas should eventually support meaningful scale changes such as:

```text
WORLD
CAMPAIGN
SEAT / PROCESS
OBJECT
```

Scale determines what can be rendered usefully.

It must not silently change epistemic standing.

```text
ZOOM
!=
PROMOTION

VISIBLE AT WORLD SCALE
!=
MORE IMPORTANT

HIDDEN AT CURRENT SCALE
!=
ABSENT
```

A future rendering may expose additional scales if actual operation requires
them.

---

## Learn geometry from use

The current objective is not to decide the final visualization.

The objective is:

```text
FREEZE:
SEMANTIC DIFFERENCES

LEAVE OPEN:
SPATIAL REALIZATION
```

Future Cockpit dogfood should reveal whether the relation lenses work best as:

```text
toggles
overlays
depth
color
motion
radial channels
small multiples
camera modes
linked panes
or new tools
```

If the existing labels / tools become insufficient:

```text
OBSERVED OPERATING FRICTION
↓
NEW DISTINCTION OR TOOL
↓
SMALLEST RENDERING REPAIR
↓
DOGFOOD AGAIN
```

Do not create visual concepts merely because they are imaginable.

---

## Animation pressure questions

Future implementation attempts should pressure at least:

```text
1. Can a durable transition animate without implying extra causality?

2. Can basis drift visibly change current applicability without rewriting the
   historical object?

3. Can one unreleased adoption remain visually persistent while LIVE toggles as
   applicability becomes stale / restored?

4. Can assignment → bell → wake → receipt be followed through time while keeping
   assignment, opportunity, occupancy, work, and receipt identities separate?

5. Can two parallel seats move independently without suggesting one global
   synchronized cognition?

6. Can an incident interrupt a path without erasing the history before it?

7. Can a user scrub or inspect prior configuration without confusing historical
   projection with current state?

8. Can the same selected address survive temporal navigation and projection
   switching?
```

---

## Failure conditions

Future Cockpit attempts should be treated as perceptually fractured if:

```text
- the operating surface becomes mostly text / cards again;
- animated flow invents causal relations;
- switching representation loses address silently;
- historical and current states become visually indistinguishable;
- observation, evaluation, and authority collapse into one status color;
- screen position becomes accidental priority;
- seat / occupant / model / role collapse visually;
- the user must return to generic chat to recover basic operational orientation;
- the rendering hides basis / provenance when challenged;
- the Atlas becomes pretty but less useful for action and reconstruction.
```

---

## Current design law

```text
TOPOLOGY TELLS YOU
WHAT THE WORLD MEANS.

CONSEQUENCE TELLS YOU
WHAT THE WORLD IS DOING.

TIME SHOWS YOU
HOW CONFIGURATION CHANGES.

OBSERVATION / EVALUATION / AUTHORITY
TELL YOU
WHAT KIND OF RELATION YOU ARE LOOKING AT.

ADDRESS LETS YOU
MOVE BETWEEN ALL OF THEM
WITHOUT LOSING THE THING.
```

This is a projection guide for future attempts.

It is not a final rendering specification.
