# DEVELOPMENT_HORIZON_PROJECTION_001 — Qualification 001

## Tested basis

```text
candidate branch:
development-horizon-projection-v0

tested head:
b13faa420e4b9b7b71895ca12b624d8d71a76e99

stack base:
wake-source-v0
2ee939453651da741769ea07210fcdeaec9da971

workflow:
DEVELOPMENT_HORIZON_PROJECTION_001

run:
35508392994

job:
106071937057

conclusion:
SUCCESS
```

The same tested head also re-ran:

```text
DEVELOPMENT_CAMPAIGN_001
run 35508392969
SUCCESS

LIVE_RUNTIME_PROJECTION_001
run 35508392959
SUCCESS

BOUNDED_REENTRY_001
run 35508392964
SUCCESS
```

## Exact tested artifacts

```text
candidate design:
110e5cb924a44274b5b12edb0fd5cc8d7e953f40

horizon reducer:
9f5efb36a526c9311e059cdfefca32a3f8b5d785

live runtime integration:
c0fd7b0287b9910aa960e141d8734e2f7041ef92

Cockpit horizon renderer:
c6411089c7919c77e76429407efab43ca03ed9f5

Cockpit horizon styling:
a99b3bf292b6fe1ec5cad79c3503014b72a1a291

pressure suite:
45bd9cd03329af505a7c9bfc7458d4396ac64cac

COCKPIT_OPERATING_SPACE_001 candidate:
eed0ce5ec256d26be572882fe7305607820e3a29

RUNTIME_SANITY_GATE_001 candidate:
622e83c905b6d90c5f11541b40e3a1109f5bbb34

WAKE_POLICY_001 candidate:
c098df38278bfd562981dcb25558d69d27a26ff8

focused workflow:
b18376f3ddaa00af7f4c3eea27d904eb0d10c486
```

## Observed pressure

```text
H1 READY:
PASS

OPEN campaign
no declared external blocker
no work/evidence activity

→ READY_FOR_PRESSURE


H2 ACTIVE:
PASS

OPEN campaign
request + current selection + current assignment

→ ACTIVE

priority_effect = NONE


H3 EVIDENCE ACCUMULATING:
PASS

OPEN campaign
preparation receipt + bounded-reentry receipt

→ EVIDENCE_ACCUMULATING


H4 EARNED:
PASS

all declared relations EARNED

→ EARNED


H5 FRACTURED:
PASS

no OPEN relations
at least one FRACTURED

→ FRACTURED


H6 BLOCKED:
PASS

visible campaigns:
RUNTIME_SANITY_GATE_001
WAKE_POLICY_001

declared edge:
RUNTIME_SANITY_GATE_001
→ WAKE_POLICY_001

sanity gate:
not EARNED

wake policy:
BLOCKED

exact blocker exposed:
RUNTIME_SANITY_GATE_001


H7 UNLOCK:
PASS

same declared graph

RUNTIME_SANITY_GATE_001:
EARNED

WAKE_POLICY_001:
loses blocker
→ READY_FOR_PRESSURE

priority_effect:
NONE


H8 UNKNOWN EDGE:
PASS

edge endpoints not both visible campaign IDs

→ retained as campaign-local dependency
→ no fabricated cross-campaign blocker


H9 PROJECTION ONLY:
PASS

input runtime state before / after projection:
identical

authority_effect = NONE
execution_effect = NONE
standing_effect = NONE


H10 COEXISTING HORIZONS:
PASS

one READY_FOR_PRESSURE
one ACTIVE

both retained simultaneously

priority_effect = NONE
```

## Existing durable objects only

No roadmap database was introduced.

The projection consumes:

```text
development_campaign_v0 packets
current relation standing
existing dependency_edges
envelope requests
current selection
preparation receipts
assignment history / satisfaction
manual bells
wake opportunities
bounded-reentry receipts
```

and derives orientation.

```text
PROJECT FUTURE
!=
SECOND TASK DATABASE
```

## Cross-campaign dependency convention

The tested convention is deliberately narrow.

When both endpoints of an existing campaign `dependency_edges` entry exactly
name campaigns visible to the projection:

```text
FROM_CAMPAIGN
→ TO_CAMPAIGN
```

the source campaign must currently be `EARNED` for the target to be unblocked.

Edges whose endpoints do not both name visible campaigns remain local
dependency information.

No general dependency ontology is claimed.

## Horizon vocabulary

The tested reducer derives:

```text
READY_FOR_PRESSURE
ACTIVE
EVIDENCE_ACCUMULATING
BLOCKED
EARNED
FRACTURED
```

These values are never written back into campaign packets.

```text
HORIZON PROJECTION
!=
CAMPAIGN MUTATION
```

## No roadmap priority

The tested projection retains:

```text
priority_effect = NONE
```

Multiple unblocked horizons can coexist.

```text
UNBLOCKED
!=
PRIORITIZED

SCREEN POSITION
!=
PRIORITY

DEPENDENCY
!=
RECOMMENDATION
```

## Cockpit composition

The live runtime sidecar now accepts optional read-only:

```text
assignment DB
wake-source DB
```

in addition to its previous durable sources.

The normalized runtime state now includes:

```text
assignment history
assignment satisfactions
manual bells
bell emissions
development_horizons
```

God Gobbo renders a DEVELOPMENT HORIZONS section showing:

```text
campaign / horizon ID
objective
derived current state
open / earned / fractured counts
exact blockers
declared unlocks
work / evidence counts
```

No horizon-control UI was added.

```text
CAN READ HORIZON
!=
CAN ALTER HORIZON
```

## Current horizon candidate packets

Three ordinary `development_campaign_v0` candidate packets were retained:

```text
COCKPIT_OPERATING_SPACE_001

RUNTIME_SANITY_GATE_001

WAKE_POLICY_001
```

They remain:

```text
status = CANDIDATE
adoption_effect = NONE
authority_effect = NONE
execution_effect = NONE
```

They are not automatically posted, adopted, selected, assigned, or executed.

`WAKE_POLICY_001` declares:

```text
RUNTIME_SANITY_GATE_001
→ WAKE_POLICY_001
```

so the horizon projection can expose the intended gate if both campaigns are
present in a live campaign store.

## Composition regression

The focused workflow passed:

```text
DEVELOPMENT_HORIZON_PROJECTION_001:
PASS

LIVE_RUNTIME_PROJECTION_001:
PASS

existing Cockpit observer:
PASS

WAKE_SOURCE_001:
PASS

PREPARATION_ASSIGNMENT_001:
PASS

BOUNDED_REENTRY_001:
PASS

DEVELOPMENT_CAMPAIGN_001:
PASS
```

Separately triggered campaign, live-runtime, and bounded-reentry workflows also
passed on the same tested head.

## Bounded result

The executed fixture supports only that:

```text
THE TESTED COCKPIT PROJECTION
CAN DERIVE CURRENT DEVELOPMENTAL
HORIZON ORIENTATION

FROM EXISTING DURABLE CAMPAIGN
AND RUNTIME EVIDENCE,

INCLUDING EXACT DECLARED
CROSS-CAMPAIGN BLOCKERS,

WITHOUT CREATING:
a roadmap database
priority
authorization
execution
standing
or horizon-mutation authority.
```

## Nonclaims

This qualification does not establish:

```text
automatic campaign adoption
automatic prioritization
best-next-horizon selection
horizon mutation through Cockpit
scheduler policy
wake policy
runtime sanity-gate satisfaction
general dependency semantics
```

## Standing boundary

```text
DEVELOPMENT_HORIZON_PROJECTION_001:
10 / 10 PASS

DURABLE ROADMAP DATABASE:
NONE

CURRENT HORIZON PROJECTION:
YES

EXACT BLOCKER / UNLOCK VIEW:
YES

COCKPIT HORIZON VIEW:
YES

HORIZON WRITE AUTHORITY:
NONE

PRIORITY:
NONE

COCKPIT_OPERATING_SPACE_001:
CANDIDATE ONLY

RUNTIME_SANITY_GATE_001:
CANDIDATE ONLY

WAKE_POLICY_001:
CANDIDATE ONLY / GATED BY DECLARED SANITY EDGE

SCHEDULER:
UNTOUCHED

MERGE:
NO
```
