# TWO_LANE_COORDINATION_001

## STATUS

```text
CANDIDATE COORDINATION CONTRACT
NOT ACTIVE POLICY
NOT SCHEDULER
NOT AUTHORITY
NOT INTEGRATION AUTHORIZATION
```

## Sole question

Can two independently attributed work lanes observe each other's current bounded
work claims and detect stale or overlapping consequence trajectories before
mutation, without shared chat context and without a central writable lock?

## Protected distinctions

```text
GIT SERIALIZATION != WORK COORDINATION
LINEAR HISTORY != SINGLE INVOCATION LINEAGE
COMMIT AUTHOR != OCCUPANT / INVOCATION PROVENANCE

PEER AWARENESS != SHARED CHAT CONTEXT
REPRESENTATION OVERLAP != SEMANTIC COLLISION
BYTE EQUIVALENCE != PROVENANCE RECONCILIATION
NO COORDINATION BLOCK != AUTHORIZATION TO MUTATE

VISIBLE AUTHORIZATION != ADDRESSED AUTHORIZATION
ROLE LABEL != ROLE BINDING
WORK CLAIM != AUTHORITY GRANT
```

## Lane coordinate

A lane is represented by independently retained coordinates:

```text
lane_id
seat_id
occupant_id
invocation_id
branch
basis_head
target_lineage
active_work_claim
peer_coordination_cursor
```

None substitutes for another.

## Work claim v0

A claim preserves:

```text
claim_id
lane_id
seat_id
occupant_id
invocation_id
branch
basis_head
target_lineage
campaign_id
pressure_id
addressed_role
binding_ref
consequence_envelope_id
semantic_surfaces[]
artifact_scopes[]
mutation_paths[]
status
```

and exact non-effects:

```text
authority_effect = NONE
execution_effect = NONE
integration_effect = NONE
priority_effect = NONE
```

Occupant, invocation, role, and binding fields are provenance declarations only.
This contract does not authenticate them.

## Coordination cursor v0

Each lane retains, for each peer:

```text
peer lane_id
peer branch
last_seen_head
last_seen_claim_digest
```

The cursor is a vector, not a global event counter.

```text
PEER AWARENESS
DOES NOT REQUIRE
GLOBAL TOTAL ORDER
```

## Pre-mutation rule

Immediately before a lane begins a new repository mutation unit:

1. resolve each relevant peer branch to its current exact head;
2. compare with the retained peer coordinate;
3. if head or claim digest changed, return REVALIDATION_REQUIRED;
4. only after consuming the current peer claim may overlap be evaluated;
5. if a collision is present, return COORDINATION_HOLD;
6. otherwise return NO_COORDINATION_BLOCK.

```text
NO_COORDINATION_BLOCK
!=
SYSTEM_WRITE AUTHORITY
```

Authority remains a separate membrane.

## Collision axes

### Semantic collision

For two ACTIVE claims:

```text
exact semantic_surface intersection
→ SEMANTIC_COLLISION
```

v0 performs no synonym or embedding inference.

### Provenance / consequence-envelope collision

For two ACTIVE claims:

```text
same target_lineage
+
same consequence_envelope_id
+
overlapping artifact_scope
→ PROVENANCE_COLLISION
```

This relation holds even if:

```text
branches differ
bytes would be identical
Git would merge cleanly
```

It captures the natural INVOCATION_RECOVERY_001 incident where two invocations
independently exercised the same apparatus-materialization trajectory.

### Representation overlap

```text
mutation_path intersection
without semantic/provenance collision
→ REPRESENTATION_OVERLAP_ONLY
```

This is visible residue, not proof of safe merge.

## Natural Cell Zero

Observed specimen:

```text
two invocations
same apparatus target lineage
same consequence envelope
same semantic purpose
no shared active-work claim
no pre-mutation peer revalidation

Git:
serialized both write sequences

bytes:
four duplicated common components identical

damage:
contained before qualification / held-out realization
```

The target behavior is not to prevent Git from serializing.

The target is:

```text
SECOND LANE
sees current peer claim
before duplicate mutation
→ COORDINATION_HOLD
```

## Pressure cells

### A — non-overlapping work
Different semantic surfaces, artifact scopes, and consequence envelopes.
Expected: NO_COORDINATION_BLOCK.

### B — same path, different semantics
Same mutation path, distinct semantic surfaces and consequence envelopes.
Expected: REPRESENTATION_OVERLAP_ONLY, no coordination block.

### C — different files, same semantic surface
Expected: SEMANTIC_COLLISION → COORDINATION_HOLD.

### D — duplicate consequence trajectory
Different branches are allowed, but target_lineage, consequence_envelope_id,
and artifact_scope overlap.
Expected: PROVENANCE_COLLISION → COORDINATION_HOLD.

### E — stale peer coordinate
Local cursor retains peer H0; peer branch is now H1.
Expected: REVALIDATION_REQUIRED before overlap adjudication.

After the lane explicitly consumes the H1 peer claim and updates its cursor,
the guard may adjudicate the current claims. If they overlap, hold.

### F — claim changes without cursor acknowledgement
Peer head/current claim differs from the retained claim digest.
Expected: REVALIDATION_REQUIRED.

## Failure behavior

Fail closed when:

```text
peer current head unavailable
peer current claim unavailable
claim malformed
cursor malformed
peer branch identity disagrees
claim digest disagrees
coordination basis stale
collision detected
```

Do not auto-expire an ACTIVE claim.

No clock-based lease exists in v0.

## Explicit non-features

```text
NO scheduler
NO leader election
NO lease expiry
NO heartbeats
NO distributed locks
NO automatic claim stealing
NO automatic merge
NO automatic priority
NO semantic synonym inference
NO authority creation
NO role authentication
NO occupant authentication
```

## Claim ceiling

A passing pressure may establish only:

> Two bounded lanes can expose exact declared work claims, detect exact tested
> semantic/provenance collisions, and refuse to rely on stale peer coordination
> coordinates before mutation.

It does not establish general multi-agent safety, general conflict detection,
authenticated identity, authority to mutate, or safe parallel integration.

## First operating regime

After qualification, create two isolated READY_UNCLAIMED operating branches:

```text
LANE_A
Cockpit / coordination / operator interaction

LANE_B
seat continuity / invocation recovery / successor-cost work
```

Occupant binding and ACTIVE work claims occur only when a later invocation is
explicitly assigned its lane.

Authoritative integration remains serialized.
