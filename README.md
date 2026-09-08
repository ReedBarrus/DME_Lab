# DME_Lab

## What DME_Lab is

DME_Lab is a deliberately small, evidence-driven laboratory for learning what
can be preserved, replayed, reconstructed, and exposed from bounded
observations without silently turning those observations into stronger claims.
Its present objective remains deterministic reconstruction of OS-derived event
history with provenance intact.

The lab has lineage in [DME_Theory](docs/lineage/DME_Theory.md), but that
lineage is not authoritative here. Repository state, executable behavior,
traces, reconstruction results, and explicit decision records govern current
claims.

## Development discipline

DME_Lab advances through small pressure passes:

```text
question / pressure
-> projection
-> contract
-> implementation
-> trace
-> reconstruction
-> comparison
-> distinction
-> feedback
-> amendment
```

Every pass must keep projected, implemented, observed, and reconstructed claims
separate. The working rules are:

- prefer executable pressure to speculative architecture;
- preserve provenance and source-specific boundaries;
- keep absent or unresolved information visibly absent or unresolved;
- treat schemas, contracts, projections, and lineage as claims rather than
  proof;
- add a conserved distinction only when it prevents demonstrated collapse or
  relearning;
- keep every current structure amendable under better evidence.

The authority order and operating protocol are recorded in
[AGENT_CONTEXT.md](AGENT_CONTEXT.md) and [WORKFLOW.md](WORKFLOW.md).

## Current bounded working regime

The working vertical path is:

```text
capture
-> ingest
-> ledger
-> replay
-> reconstruction
-> projection
```

Today this path is executable only in bounded regimes. Repository capture is a
foreground, explicitly invoked specimen rather than general OS capture.
Admission uses a named minimum structural comparator. The JSONL ledger and raw
replay have pressure-tested guarantees within their declared v0 scope.
Reconstruction recovers observation/admission relationships, and projection
selects a deliberately smaller navigable surface. Acoustic specimens have also
passed through the generic ingest-to-projection path, but they remain
pressure-only experiments rather than a generalized acoustic observer.

See the [contract surface map](docs/contracts/README.md) for the maturity and
evidence attached to each boundary.

## What is actually implemented

### Repository snapshot / Git observers

- A bounded filesystem snapshot observer records scoped file structure,
  content hashes, timestamps, exclusions, and capture errors.
- A separate Git observer records HEAD, branch, porcelain status, and command
  failures.
- The two observations remain source-relative and non-coextensive. One call
  does not make them simultaneous or establish a coherent global repository
  state.

These observers are repository specimens, not a generalized Windows or OS
capture layer.

### Foreground coordinator

`ForegroundRepositoryObservationCoordinator` explicitly captures the
filesystem and Git sources, creates observation and admission records, appends
them through the bounded ledger, and returns derived reconstruction/projection
surfaces. A newly opened coordinator can recover committed history without
recapturing or appending.

It is not a watcher, background service, scheduler, autonomous loop, atomic
multi-source transaction, or proof that the caller received an acknowledgement.
Its `current_result()` is current with respect to the supplied recorded history,
not necessarily the external repository now.

### Admission + reconstruction

- The v0 admission mechanism records comparator identity and version,
  comparison result, decision, basis, and the subject record ID.
- Rejected and unresolved decisions remain replayable rather than being
  discarded.
- Deterministic reconstruction recovers observations and all recorded admission
  relationships with paths back to authoritative ledger records.
- Integrity and continuity checks are separate: per-record digest validity does
  not establish ledger-wide continuity, truth, freshness, or source success.

### Bounded projections

The admitted projection exposes subjects with at least one admitted decision
and retains identifiers for evidence navigation. A read-only companion can
expose unique non-admitted decision states for projected subjects. Neither
surface is authoritative history, a complete reconstruction, conflict
resolution, source-quality certification, or a general projection engine.

### Acoustic experimental lineage

The acoustic branch is an executed pressure lineage over a declared Windows
audio setup, not a promoted production subsystem:

- an initial low-amplitude basis-entry pass established only bounded local
  microphone measurements;
- a predeclared replication pass found the S2 condition locally discriminable
  from C0 and S1 while preserving the contaminated first block as excluded
  evidence;
- a fresh-process recurrence pass reproduced that relational verdict while
  numerical magnitudes changed;
- repository/acoustic comparison found only partial source correspondences and
  one shared software-pipeline correspondence inherited by construction;
- prediction-first selection earned no novel cross-domain prediction.

Commanded playback, constructed buffers, microphone samples, physical speaker
realization, airborne causality, and a complete room field remain distinct.
Raw PCM was intentionally ephemeral; hashes and bounded measurements survived,
so later questions cannot recover discarded waveform content.

## What has been earned

### Historical continuity != present-world freshness

Committed history can survive coordinator replacement and be deterministically
rederived. That proves continuity of recorded evidence, not that the external
source still matches its last captured endpoint. Equivalent endpoints also do
not prove that nothing happened during an unobserved interval.

### Admission != source success

The minimum comparator establishes structural admissibility only. A Git
observation with failed source commands can be well formed, admitted,
replayed, reconstructed, and projected while its HEAD, branch, and status
remain unavailable and its capture errors remain preserved in history.

### Projection != full reconstruction

Projection is a selected view. It can preserve subject and admission
coordinates while omitting source payload, capture-error, timing, measurement,
and opposed-decision detail that remains available through reconstruction and
authoritative replay. Projection membership therefore does not establish
uncontested admission, source success, or complete evidence exposure.

### Missingness / unresolved evidence is preserved

Unavailable source sequence and event time, capture failures, unresolved or
opposed admission decisions, unobserved interval paths, discarded waveform
content, and unsupported physical claims are not filled with inference.
Missingness can have different causes; the lab does not collapse them into one
generic unknown or treat them as corruption by default.

## Current frontier

### Repository surface horizontally frozen

The foreground repository-observation surface is locally saturated and frozen
for dwell. Its bounded findings compose without a known contradiction. Reopen
it only for a concrete consumer demand, an independent contradiction, a
qualitatively new observation basis, or a separately scoped
durability/concurrency regime.

### Acoustic render-path witness candidate

The smallest legitimate candidate for a new acoustic source coordinate is a
separate-process WASAPI shared-mode loopback observer on the selected Realtek
render endpoint. It could provide independently observed, post-system-mix PCM
with endpoint and device-clock coordinates downstream of command submission.

This is a frozen witness proposal with result `candidate_requires_new_basis`.
The host exposes the required APIs, but DME_Lab contains no such observer and
no render-path witness has been executed. Even a successful witness would not
by itself prove electrical output, speaker actuation, airborne sound, or causal
attribution of microphone measurements.

### Consumer/navigation pressure entering experimentally

A bounded consumer-pressure handoff is testing whether the recovered
`current_result()` surface is sufficient for a historical Git-acquisition
question. Its reported specimens make opposite source-acquisition outcomes
indistinguishable at that selected surface while existing reconstruction retains
the distinguishing source fields and errors. This pressures evidence navigation,
not automatic surface expansion: it is experimental activity, not a merged
consumer runtime, navigation system, production-contract change, or new
distinction.

## Explicitly NOT implemented

DME_Lab does not currently implement:

- a generalized consequence engine, consequence space, or feedback economy;
- an agent architecture, autonomous observer, planner, or adaptive behavior;
- a world model or globally coherent present-state representation;
- an atlas runtime, chart graph, translation engine, or generalized topology;
- a generalized Windows observer or general OS capture adapter.

Also deferred are continuous polling/watchers, generalized source-health or
trust policy, conflict adjudication, durable invocation grouping, atomic
multi-record rounds, concurrent-writer semantics, torn-write recovery, hash
chains, repair authority, and a generalized index.

## Where to go next

- [PROJECT_STATE.md](PROJECT_STATE.md) — primary fast-entry working memory and
  present pressure boundary.
- [WORKFLOW.md](WORKFLOW.md) — development cycle and missingness rule.
- [AGENT_CONTEXT.md](AGENT_CONTEXT.md) — authority order, startup protocol, and
  current intention.
- [Decision records](docs/decisions/) — scoped claims, evidence, failures,
  deferrals, and frontier judgments.
- [Contract surface](docs/contracts/README.md) — maturity of capture, ingest,
  ledger, replay, reconstruction, and projection boundaries.
- [Traces](traces/README.md) — runtime evidence and its authority limits.

Start with `PROJECT_STATE.md`, then follow only the contract, trace, or decision
record relevant to the question at hand.
