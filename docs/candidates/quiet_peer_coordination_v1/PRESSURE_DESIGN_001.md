# QUIET_PEER_COORDINATION_REPRESENTATION_001 — Pressure Design 001

## Basis

```text
authoritative main:
788c754c95d1874e5a2dd245ee100f42d2760fad

trigger qualification:
lane-b-successor-engagement-qualification-v0
f6d033068c2df18c3261dae3e1769517a4762ae5

successor:
lane-b-successor-v1
5c2318b12317298345dbd71f0df735a7c4f376c5

Lane A:
lane-a-cockpit-coordination-v0
de667390d81c1219abfee063d2a3b1fe13d1ba71
READY_UNCLAIMED
ACTIVE claim ABSENT
```

## Protected distinctions

```text
PEER EXISTENCE
!=
CLAIM EXISTENCE

PEER STATE OBSERVATION
!=
ACTIVE CLAIM OBSERVATION

ABSENCE CLAIM
!=
ABSENCE OF INPUT

NO_ACTIVE_CLAIM
!=
SPECIAL CLAIM DIGEST

NEW REPRESENTATIONAL CAPABILITY
!=
RETROACTIVE HISTORICAL FACT
```

## v1 surfaces

```text
PEER_STATE_OBSERVATION_v1

two_lane_coordination_cursor_v1
  PEER_STATE_COORDINATE_v1
    claim_observation:
      ACTIVE_CLAIM + claim_digest
      XOR
      NO_ACTIVE_CLAIM
```

For a quiet observation, raw input must explicitly contain:

```text
claim_presence:
NO_ACTIVE_CLAIM

claim_path_observation:
  path: coordination/active_work_claim.json
  state: ABSENT_AT_OBSERVED_HEAD
```

The producer never derives quiet state from an omitted claim object.

## Producer

```text
acknowledge_peer_states(
  known relevant PEER_STATE_OBSERVATION_v1 objects
)
```

Law:

```text
KNOWN PEER
→
EXACTLY ONE CURSOR COORDINATE
```

regardless of claim presence.

## Revalidation

```text
NO_ACTIVE_CLAIM → ACTIVE_CLAIM
= PEER_CLAIM_APPEARED

ACTIVE_CLAIM digest A → ACTIVE_CLAIM digest B
= PEER_CLAIM_CHANGED

ACTIVE_CLAIM → NO_ACTIVE_CLAIM
= PEER_CLAIM_DISAPPEARED

cursor omitted + current peer observed
= PEER_NOT_ACKNOWLEDGED
```

Head advancement remains separately visible:

```text
ACTIVE same digest + head advance
= PEER_ACTIVITY_ADVANCED_CLAIM_UNCHANGED

NO_ACTIVE_CLAIM + fresh quiet observation + head advance
= PEER_ACTIVITY_ADVANCED_NO_ACTIVE_CLAIM
```

Neither head advance alone creates a collision.

## Compatibility

v0 remains unchanged.

For an ACTIVE peer claim, v1 must derive the exact same claim digest that v0
acknowledge() derives.

No v0 empty cursor is reinterpreted as proof of historical quiet state.

## Pressure

```text
A quiet peer explicit representation
B active peer representation + v0 digest compatibility
C NO_ACTIVE_CLAIM + null digest rejected
D NO_ACTIVE_CLAIM + fake sha256 digest rejected
E ACTIVE_CLAIM without digest rejected
F quiet → active revalidation
G active A → active B revalidation
H active → quiet revalidation
I quiet stable
J quiet head advance
K explicit quiet coordinate vs omitted coordinate
L active collision regression
M fenced predecessor regression
```

## Claim ceiling

A survivor establishes only explicit peer-state representation and mechanically
legible claim-presence transition revalidation.

It does not establish scheduler correctness, liveness, distributed consensus,
authority, execution, or live successor engagement.

## Non-effects

```text
LIVE LANE A MUTATION:
NONE

LIVE LANE B SUCCESSOR MUTATION:
NONE

PREDECESSOR MUTATION:
NONE

LIVE ENGAGEMENT:
NONE

AUTHORITY:
NONE

EXECUTION:
NONE

MERGE:
NONE
```
