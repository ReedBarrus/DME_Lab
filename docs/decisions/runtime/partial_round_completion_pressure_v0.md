# Partial-Round and Ambiguous Completion Pressure v0

## Scope

This bounded Phase-C pass injected deterministic exceptions at every commitment
boundary of the promoted foreground repository coordinator:

```text
filesystem observation
Git observation
filesystem admission
Git admission
successful caller return
```

It characterized existing history and derivations without adding transactions,
atomic groups, round IDs, request IDs, rollback, repair, truncation, retries,
deduplication, locking, fsync policy, or torn-write pressure.

Starting state was clean `main` at
`b7757c91dbacf25d75217d30bed304b8081f033c` (`Phase-C`). Foreground
coordinator tests passed 23/23 and the full baseline passed 299/299.

## Fixture and Fault Injection

Each independent specimen used the same deterministic clean-alpha repository
configuration. File content, file mtime, Git commit, branch, status, and capture
error state were fixed. World mutation did not confound fault position.

Every ledger first received one successful four-record capture. Those records
formed a declared prior complete-history prefix. A second capture then used
experiment-local method replacement to raise `InjectedCaptureFailure` after
zero through four durable appends. F4 raised after all four records and current
result derivation, immediately before successful return. Control C ran without
injection.

No production function was modified. No real process kill or torn JSON write
was tested.

After each invocation, the coordinator was closed and destroyed. A fresh
coordinator received only the root and ledger paths; the recovery evaluator
also received the declared prior-prefix witness. It did not receive the fault
position or failed process state. `current_result()` appended nothing.

## Chart 14

| Specimen | New durable records | Total records | Caller outcome | Integrity | Continuity | Observations | Admissions | Projection | Completion from history |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | --- |
| F0 | 0 | 4 | exception | valid | valid | 2 | 2 | 2 | unresolved |
| F1 | 1 | 5 | exception | valid | valid | 3 | 2 | 2 | unresolved |
| F2 | 2 | 6 | exception | valid | valid | 4 | 2 | 2 | unresolved |
| F3 | 3 | 7 | exception | valid | valid | 4 | 3 | 3 | unresolved |
| F4 | 4 | 8 | exception | valid | valid | 4 | 4 | 4 | unresolved |
| C | 4 | 8 | success | valid | valid | 4 | 4 | 4 | unresolved |

The stable fault-boundary surface earned Chart 14. Its coordinates are durable
record shape, caller outcome, integrity, continuity, reconstruction, projection,
and completion inference. It is not a transaction or generalized operation
model.

## Partial Composition

F1 through F3 were integrity-valid, continuity-valid, replayable, and
reconstructible. None was classified as corruption.

- F1 preserved a new filesystem observation with no admission.
- F2 preserved new filesystem and Git observations with no new admissions.
- F3 preserved both observations and one admitted filesystem relationship;
  the Git observation had no admission.

Reconstruction exposed exactly those committed facts. Projection continued to
apply its existing any-admitted rule: it omitted observations without admitted
relations and included the admitted F3 filesystem subject. No orphan admission
was created.

The histories were semantically legible at record and relationship level. The
experiment did not assume that a foreground round is itself a durable
historical unit.

## Completion Inference

Every recovered history lacked round, request, completion, and caller
acknowledgement fields. Therefore authoritative history alone established
neither completion nor incompletion for any requested invocation, including F0.

The test driver knew where it injected each exception. That knowledge was not
used as DME knowledge.

Integrity, continuity, and structural reconstruction remained independent of
operation completion. A caller exception did not establish that nothing was
persisted, and four expected-looking records did not establish that the caller
received success.

## F4 Versus Successful Control

F4 and C had different caller outcomes:

```text
F4: exception after four durable records
C:  successful return after four durable records
```

Because they were independent real captures, their ledger bytes differed in
observation timestamps and resulting digests. That difference does not encode
acknowledgement. Their normalized durable composition surfaces were equal:
record types, relative references, admission decisions, reconstruction shape,
projection size, and companion size all matched.

Neither authoritative history contained a coordinate from which caller outcome
could be inferred.

## Retry After Unknown Acknowledgement

R4 reproduced F4, destroyed the failed coordinator, reopened from disk, and
retried against the unchanged world. The retry appended another valid
four-record group at indices 9-12 and returned successfully.

The first and second groups represented equivalent observer-relative source
configurations but distinct observation occurrences. No request, attempt,
round, or retry marker existed. Authoritative history therefore could not
distinguish retry after unknown success from intentional repeated observation.

No request identity or retry policy was added merely to resolve that ambiguity.

## Companion and Source Separation

The Chart 11 companion continued to contain one empty-state row per projected
subject. Subjects without admissions were not projection members and therefore
did not acquire companion rows. Partial composition did not require admission
multiplicity or direct admission IDs in the companion.

Filesystem and Git source values and provenance remained distinct in every
partial history. Absence of one later record was not interpreted as source
collapse.

## Historical Prefix and D-0042

Every specimen preserved its four-record prior complete-history prefix under
existing ordered-digest semantics. Fresh coordinators recovered exactly the
records that became durable.

D-0042 remains supported without amendment:

```text
coordinator_lifetime != historical_continuity
```

Its current record-level wording remains accurate under mid-operation
termination. Historical continuity does not establish operation completion,
but that refinement does not contradict or require rewriting D-0042.

## Production Boundary

`ForegroundRepositoryObservationCoordinator` remains promoted. The current
bounded guarantee is foreground composition through four independently
committed records. It does not guarantee atomic rounds or durable caller
acknowledgement.

No existing production API or documentation claimed stronger semantics, so no
production mismatch was found and no production code was changed.

## Distinction

Execution independently forced D-0043:

```text
caller_invocation_outcome != durable_history_state
```

F4 and C demonstrated different caller outcomes over the same durable
composition surface, while neither history encoded acknowledgement. This
distinction is scoped to the tested foreground coordinator and does not create
a general transaction, request, or retry ontology.

## Epistemic Audit

The experiment made none of the prohibited inferences:

- integrity, continuity, or reconstruction success was not treated as capture
  completion;
- four records were not treated as caller success;
- caller exception was not treated as absence of persistence;
- repeated configuration was not treated as proof of retry;
- injected fault knowledge was not transferred into recovered history.

Charts 4-13, D-0040, D-0041, D-0042, projection semantics, Chart 11 companion
semantics, source separation, and prefix semantics remain preserved.

## Strongest Results

The strongest invariant is that fresh recovery preserves exactly the records
and relations that became durable.

The strongest failure is that authoritative history cannot establish whether a
fully durable invocation was acknowledged to its caller.

The strongest unresolved horizon is policy for retry after unknown
acknowledgement.

## Next Smallest Pressure

Use a concrete caller requirement to determine whether retry policy or request
identity is actually needed to distinguish retry from intentional repeated
observation. Do not add either preemptively.

## Canonical History

`traces/live_ingest_ledger_v0.jsonl` remained unchanged at SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.

## Verification

Final targeted tests passed 50/50. The full suite passed 326/326.
