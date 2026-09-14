# Intra-Capture Timing Skew Pressure v0

## Scope

This bounded Phase-C pass changed the external repository after filesystem
capture returned but before Git observation began inside one explicitly invoked
`capture_round()`. It characterized the existing sequential acquisition regime
without adding locks, transactions, repository freezing, atomic snapshots,
barriers, shared timestamps, grouping IDs, threads, watchers, polling, temporal
fusion, or a current-world object.

Starting state was clean `main` at
`249cde3783a528018269c7b7f08a7a9dfe245c9b`
(`Pre-goblin capstone Super Tetaroni`). The prior foreground/partial-round
targeted baseline passed 50/50 and the full baseline passed 326/326. Canonical
live history and the production observers/coordinator were not modified.

## Deterministic Intervention

The experiment replaced only the coordinator module's process-local
`make_repo_snapshot` reference. The wrapper:

1. called the real filesystem observer to completion;
2. handed control to an external-driver callback;
3. returned the already completed alpha snapshot;
4. allowed unchanged production control to call the real Git observer.

The callback rewrote the fixture for S1 and rewrote, added, and committed it for
S2. The production coordinator did not know the intended trajectory and did not
perform the mutation. No sleep, race, thread, or arbitrary timing was used.

## Specimens and Chart 15

| Specimen | Filesystem evidence | Later Git evidence | Driver mutation between acquisitions | Structural health | Immediate same invocation | Durable same invocation | Shared world configuration |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0 | alpha | clean alpha | no | valid | yes | unresolved | true by control; unresolved from DME evidence |
| S1 | alpha | dirty later state over alpha HEAD | yes | valid | yes | unresolved | false by control; unresolved from DME evidence |
| S2 | alpha | clean committed beta | yes | valid | yes | unresolved | false by control; unresolved from DME evidence |
| C1 | beta | clean committed beta | no | valid | yes | unresolved | true by control; unresolved from DME evidence |

C0 used an independent clean-alpha fixture. S1 used another independent
clean-alpha fixture. S2 used a third fixture, then C1 performed a fresh ordinary
capture after that same world had settled at committed beta.

The stable comparison surface earned Chart 15. Its coordinates are specimen,
source-relative configuration, externally controlled mutation, structural
health, process-local grouping, durable grouping, and world-configuration
justification. It is not a generalized temporal model, synchronization regime,
or world-state abstraction.

## Ground Truth and DME Knowledge

The deterministic driver knew the mutation point, alpha and beta content, and
the commit action. It therefore established that the C0 and C1 pairs came from
stable configurations and that the S1 and S2 pairs did not describe one shared
configuration.

None of those driver facts was written to the ledger. No mutation event or
transition record was manufactured. DME evidence established two individually
valid source observations, their source-relative payloads and provenance, and
their ledger coordinates. It did not establish that a mutation occurred
between them or that they shared one world configuration. Those questions
remain unresolved from DME evidence even for the controls; control knowledge is
not historical knowledge.

## Temporal Evidence

The filesystem observer already records:

```text
observation_started_at
observation_finished_at
```

The Git observer records:

```text
observed_at
```

All three fields survive admission and fresh replay in the observation payload
and provenance. In every executed specimen, the filesystem finish timestamp
preceded the Git marker, so that recorded timestamp relation remained
recoverable. It did not establish simultaneity.

The current evidence also does not establish non-overlap between two complete
source acquisition intervals: Git exposes one marker rather than a start/finish
interval, and no clock identity or precision contract is recorded. Most
importantly, timestamp order alone cannot establish that both sources refer to
one identical repository configuration.

## Source Validity and Structural Health

C0, S1, S2, and C1 had no filesystem or Git capture errors. Every observation
was admitted under the existing comparator. Every resulting history passed
record integrity, start-at-one continuity, canonical replay, reconstruction,
projection, and Chart 11 companion reproduction.

S1 and S2 therefore demonstrate the critical bounded possibility:

```text
valid filesystem evidence
+ valid Git evidence
+ healthy composed invocation
!= justified single-world snapshot
```

The observations are not corrupt or invalid. The least misleading description
is source-relative observations acquired at different times. For S1 and S2,
experiment control additionally establishes temporal heterogeneity.

## What “Together” Means

Immediately after `capture_round()` returns, the non-authoritative return value
contains both raw captures and summaries of the four records appended by that
call. At that process-local surface, “together” means:

```text
products returned by one explicitly requested composition
```

It does not mean simultaneous acquisition or one global snapshot.

After the coordinator is destroyed, a fresh `current_result()` reconstructs
the observations and admissions but returns no captured-observation group. The
ledger contains no round, request, invocation, or group identity. Adjacent
commit indices and the convenient observation/observation/admission/admission
shape do not license durable invocation grouping. Thus “same invocation” is
unresolved from authoritative history alone.

Source payloads and timing fields were not lost on recovery. The process-local
association between the two captures and one caller invocation was lost. This
is a representational boundary, not corruption.

## Projection and Companion

The existing any-admitted projection preserved each admitted filesystem and
Git observation as a separate subject. It did not fuse payloads, assert
simultaneity, or claim a current coherent repository state. The Chart 11
companion continued to return one empty-state row per projected subject because
each subject had only its normal admitted decision.

No projection redesign or temporal fusion was warranted. Source separation was
enough to keep the heterogeneous evidence legible.

## Distinction

Execution independently forced and registered D-0044:

```text
same_capture_invocation != same_world_configuration
```

S1 and S2 each returned normally from one invocation while experiment control
established that the filesystem and Git evidence came from different repository
configurations. The distinction does not claim that DME history can infer the
mutation, and it creates no generalized round or world-state ontology.

## Production Boundary and Prior Findings

`ForegroundRepositoryObservationCoordinator` remains promoted with a narrower
explicit guarantee: one foreground call sequentially acquires, admits, and
returns two source-relative observations. It provides no atomic or global
snapshot guarantee. Existing production surfaces made no stronger temporal or
coherence claim, so no production mismatch or unjustified certainty was found.

D-0042 remains supported: fresh coordinators recovered every durable record.
D-0043 remains supported: this pressure did not add caller acknowledgement or
operation-completion evidence. Partial-round findings, Chart 11 companion
semantics, source separation, and append-only history remain preserved.

## Strongest Results

The strongest invariant is that individually valid source-relative observations
remain durable, separate, reconstructible, and projectable despite
intra-capture world change.

The strongest failure is that a successful, structurally healthy capture can
return a pair that, by experiment control, never described one shared repository
configuration.

The strongest unresolved horizon is that authoritative history lacks durable
invocation grouping and cannot decide whether independently timed source
observations share a world configuration.

## Next Smallest Pressure

Pressure stale `current_result()` semantics without adding a latest-state or
temporal-fusion abstraction. Retry policy after unknown acknowledgement remains
a separate unresolved caller-policy horizon from the previous pass.

## Canonical History

`traces/live_ingest_ledger_v0.jsonl` remained unchanged at SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.

## Verification

Final targeted tests passed 76/76. The full suite passed 352/352.
