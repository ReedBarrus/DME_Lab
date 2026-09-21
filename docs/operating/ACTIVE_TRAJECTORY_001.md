# ACTIVE_TRAJECTORY_001 — Durable Bounded Development Toward Continuity Control

## STATUS

```text
OPERATING TRAJECTORY:
PROVISIONAL / TRACKED

AUTHORITY EFFECT:
NONE

EXECUTION EFFECT:
NONE

LANE ACTIVATION EFFECT:
NONE

MERGE EFFECT:
NONE
```

This map records current standing and intended evidence gates. It does not
activate a campaign, bind an occupant, grant authority, merge a branch, or
authorize execution.

## Current observed coordinates

Observed while this trajectory record was materialized:

```text
main:
8a5321c098b7f3a944e180612cd2e670b20f282e

TWO_LANE_COORDINATION_001 qualified head:
ee178c23124cac68bd8b5a3bc75ce16a486845b9

LANE_A:
lane-a-cockpit-coordination-v0
de667390d81c1219abfee063d2a3b1fe13d1ba71
READY_UNCLAIMED

LANE_B:
lane-b-recovery-continuity-v0
f55a89de6478691587ab67298fa1b3ad546f27ce
ACTIVE
WORKSHOP bound to SEAT_ENGAGEMENT_HANDSHAKE_001

INVOCATION_RECOVERY_001 apparatus branch:
invocation-recovery-apparatus-v0
990ec59204eb1ecac1c2527a7f00dc387b238ed5

AUTHORITY_POLICY_001 candidate branch:
authority-policy-contract-v0
2a06510cfc58ec7cac635ddd67795771ae855016
```

Coordinates are historical observations, not permanent truths. Future work must
revalidate current heads before consequence.

## What counts as a qualified lane?

A lane is not qualified merely because a Git branch exists.

### Q0 — lane coordinate exists

```text
branch
+
lane manifest
+
intended horizon
```

This establishes an address only.

### Q1 — coordination substrate qualified

Required:

```text
bounded work-claim grammar
peer coordination cursor
pre-mutation guard
semantic/provenance collision pressure
claim-change revalidation
branch-activity != claim-change
NO_COORDINATION_BLOCK != AUTHORITY
```

Current standing:

```text
SUPPORTED IN TESTED TWO-LANE / ONE-PEER SCOPE
```

by TWO_LANE_COORDINATION_001.

### Q2 — operating lane lifecycle qualified

A lane must survive an end-to-end bounded lifecycle:

```text
READY_UNCLAIMED
→ explicit occupant/invocation binding
→ ACTIVE work claim
→ peer consumption
→ pre-mutation guard
→ separately authorized bounded mutation
→ receipt
→ claim disposition
→ occupant release
→ lane returns to a mechanically legible terminal/available state
```

The lifecycle must preserve:

```text
WORK COMPLETE != CLAIM SILENTLY DISAPPEARS
RELEASE != SUCCESS
FAILURE != ERASURE
LANE AVAILABLE != AUTHORITY AVAILABLE
```

Current standing:

```text
NOT YET QUALIFIED END-TO-END

LANE_B is the first live bounded specimen now exercising this sequence
through SEAT_ENGAGEMENT_HANDSHAKE_001.
```

### Q3 — multi-peer coordination qualified

Opening a third lane changes topology.

Two lanes imply one peer.

Three lanes imply each active lane may have two relevant peers.

Before a third mutating lane is opened, pressure must establish:

```text
EXPECTED PEER SET IS COMPLETE
!=
CALLER HAPPENED TO SUPPLY SOME PEERS
```

and:

```text
ONE CLEAR PEER + ONE COLLIDING PEER
→ HOLD

ONE CURRENT PEER + ONE UNACKNOWLEDGED CHANGED CLAIM
→ REVALIDATION_REQUIRED

UNRELATED PEER BRANCH ACTIVITY
+ unchanged claims
→ no acknowledgement ping-pong

OMITTED EXPECTED PEER
→ fail closed

DUPLICATE PEER IDENTITY
→ fail closed
```

The precedence between stale/unacknowledged peer state and collision evaluation
must be frozen before realization.

Current standing:

```text
NOT YET QUALIFIED
```

## Seat standing

LABBOIB Temporal Seat v0 has focused qualification evidence.

Qualified in tested scope:

```text
durable seat manifest
independent continuity cursor
working-state coordinate
inbox/outbox probe surfaces
read-only wake reconstruction
exact source-ref resolution
cursor / working-state disagreement blocks wake
new continuity is visible without implicit acknowledgement
wake creates no authority
output creates no authority
```

Current claim ceiling:

```text
RECONSTRUCTABLE TEMPORAL SEAT:
SUPPORTED IN FOCUSED CANDIDATE SCOPE
```

Not qualified by that result:

```text
real occupant binding
seat engagement handshake
scheduler binding
continuous execution
chat-bus semantics
authority inheritance
general occupant replacement
live consequence
```

SEAT_ENGAGEMENT_HANDSHAKE_001 is the current pressure intended to close the
engagement / binding / one-unit transition grammar.

## Cursor standing

Cursor mechanics have bounded retained evidence for:

```text
independent cursor-bearing consumers
consumer-local unread delta
monotonic acknowledgement
one consumer does not acknowledge for another
registry membership != minimum consumer-local cursor capability
acknowledgement != new semantic knowledge
```

But:

```text
CURSOR POSITION
!=
WORKING SEMANTIC STATE

CURSOR SAYS CONSUMED
!=
FRESH OCCUPANT CAN RECONSTRUCT CONSEQUENCE OF CONSUMPTION
```

Therefore cursor continuity is partially evidenced, not generally qualified as
semantic continuity.

The open pressure is fresh-occupant reconstruction from:

```text
cursor
+
working-state basis
+
required retained refs
+
semantic debt
```

without replaying arbitrary old conversation history.

## Invocation recovery standing

INVOCATION_RECOVERY_001 deterministic apparatus:

```text
QUALIFIED

28 / 28 deterministic apparatus tests:
PASS

held-out successor-model A-F realization:
UNTOUCHED

held-out successor invocations:
0
```

Therefore:

```text
RECOVERY APPARATUS QUALIFIED
!=
RECOVERY SCIENTIFIC CLAIM ESTABLISHED
```

A separate human authorization remains required for the one held-out A-F batch.

## Authority policy standing

AUTHORITY_POLICY_001 currently has:

```text
candidate contract:
MATERIALIZED

pressure design:
MATERIALIZED

policy adoption:
NO

policy implementation:
NONE

policy qualification:
NONE
```

This must be pressure-qualified before a continuity controller is permitted to
treat policy as an automatic grant source.

## Candidate third lane

The intended third lane is primarily a SCIENCE / QUALIFICATION lane.

Provisional horizon:

```text
LANE_C — SCIENCE

fresh adversarial review
pressure design
held-out administration
mechanical scoring
claim-ceiling review
qualification receipts
cross-lane falsification
```

Its default posture should initially be:

```text
SYSTEM_READ:
available under governing policy

SYSTEM_WRITE:
only for its own bounded science artifacts when separately granted

INTEGRATION:
NONE

AUTHORITY OVER OTHER LANES:
NONE
```

Therefore:

```text
SCIENCE LANE
!=
SYSTEM GOVERNOR
```

Most qualification activity belongs naturally here, but implementation teams
must still run their deterministic tests and preserve receipts. Science owns
independent pressure/adjudication, not every test command.

## Gate before opening Lane C

Recommended minimum gate:

```text
1. SEAT_ENGAGEMENT_HANDSHAKE_001
   reaches terminal qualification or explicit fracture

2. LANE_B
   demonstrates clean bounded release / claim disposition after its unit

3. MULTI_PEER_COORDINATION_001
   synthetically qualifies complete-peer-set behavior for >= 3 lanes

4. exact Lane C horizon + mutation default are frozen
```

Invocation Recovery held-out success is NOT required merely to create a
read-mostly Science lane.

It IS required before claiming durable cross-invocation continuous workers.

## Major destination — Cockpit continuity control

The desired operator surface is an explicit continuity regime control.

The target is NOT:

```text
ON
=
agents may do anything continuously
```

The target is:

```text
ON
=
the ecology may continue seeking / accepting / recovering bounded work
ONLY through currently adopted campaigns,
projected envelopes,
qualified seat engagement,
current peer coordination,
and separately valid authority.
```

and:

```text
OFF
=
do not begin new bounded work engagements

current effect-bearing unit:
must follow a separately frozen safe stop / drain law

durable history:
retained

claims:
disposed explicitly

seat state:
checkpointed

authority:
contracted as specified

recovery basis:
preserved
```

A likely later control state machine is:

```text
OFF
→ ARMING
→ ON
→ DRAINING
→ OFF

with failure-legible blocked states
```

but those states are not frozen by this map.

## Evidence ladder toward the continuity button

```text
E1  TWO_LANE_COORDINATION_001
    qualified in tested two-lane scope
    [DONE]

E2  INVOCATION_RECOVERY_001 apparatus
    deterministic qualification
    [DONE]

E3  SEAT_ENGAGEMENT_HANDSHAKE_001
    synthetic state-machine qualification
    [IN FLIGHT — LANE_B]

E4  lane lifecycle release / disposition
    [NOT YET QUALIFIED]

E5  AUTHORITY_POLICY_001
    adversarial policy qualification
    [NOT YET QUALIFIED]

E6  INVOCATION_RECOVERY_001
    one held-out A-F realization
    [NOT AUTHORIZED / UNTOUCHED]

E7  cursor + working-state fresh-occupant reconstruction
    [NOT YET QUALIFIED]

E8  MULTI_PEER_COORDINATION_001
    >=3-lane complete-peer-set pressure
    [NOT YET QUALIFIED]

E9  LANE_C science lane
    open only after E3/E4/E8 gate
    [NOT OPEN]

E10 CONTINUITY_CONTROL_001
    OFF / ARM / ON / DRAIN / BLOCK semantics
    [HORIZON ONLY]

E11 Cockpit control binding
    control preview + confirmation + durable receipt
    [HORIZON ONLY]

E12 bounded continuous-development campaign
    authorized consequence envelopes only
    [DESTINATION]
```

## General horizon after Lane C

Once Lane C is available, use it to close outstanding evidence rather than
immediately widening capability.

Priority unresolved surfaces:

```text
SEAT_ENGAGEMENT_HANDSHAKE_001
AUTHORITY_POLICY_001
INVOCATION_RECOVERY_001 held-out realization
cursor / working-state reconstruction
multi-peer coordination
cross-surface occupant / invocation provenance
open PR / branch adjudication and serialized integration
Cockpit control truthfulness
```

Then return to broader campaign horizons.

## Operating law

```text
SPACE:
LANES

TIME:
RECOVERY

LOCUS:
SEATS

POSITION:
CURSORS

PERMISSION:
AUTHORITY

MAP:
ATLAS

OPERATOR SURFACE:
COCKPIT
```

The development destination is:

```text
DURABLE TRAJECTORIES
+
REPLACEABLE OCCUPANTS
+
EXPLICIT STATE
+
PEER VISIBILITY
+
BOUNDED AUTHORITY
+
FAILURE-LEGIBLE RECEIPTS
+
RECOVERY WITHOUT ERASURE
```

not ambient autonomy.

## Conserved law

```text
FREEDOM INSIDE THE CURRENT MEMBRANE

NEGOTIATION AT THE MEMBRANE

NO SILENT EXPANSION

FAILURE != ERASURE

RECOVERY != AUTHORITY INHERITANCE

CONTINUITY != AMBIENT EXECUTION AUTHORITY
```
