# Persistent Observational Field Pressure v0

## Scope

This pass exercised one finite observational field over a real temporary Git
repository and the existing stack:

```text
filesystem and Git capture
-> observation and normal admission append
-> integrity and continuity
-> canonical replay
-> reconstruction
-> admitted projection
-> non-admitted decision-state companion
```

Starting state was clean `main` at
`7e03123bb38383a9f10eb37f02e6f334e2770774`. Baseline targeted tests passed
51/51 and the full suite passed 255/255.

The field did not use or modify `docs/projection/Persistent_Ecology.md`. It did
not append to canonical live history and did not create an always-on runtime.

## Fixture and Sequence

The runner created a temporary repository with `state.txt = alpha`, a `main`
branch, and deterministic commit metadata. The real filesystem and Git
observers captured six rounds into one temporary JSONL ledger.

| Round | World condition | Mutation before capture | FS relation to prior | Git relation to prior | Record range | Reconstructed observations | O1 prefix |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| O1 | clean alpha | initial commit | initial | initial | 1-4 | 2 | recovered |
| O2 | clean alpha repeat | none | equal | equal | 5-8 | 4 | recovered |
| O3 | dirty beta | rewrite `state.txt`, do not commit | changed | changed status, same HEAD | 9-12 | 6 | recovered |
| O4 | dirty beta repeat | none | equal | equal | 13-16 | 8 | recovered |
| O5 | clean committed beta | `git add` and commit, no file rewrite | equal | changed HEAD and status | 17-20 | 10 | recovered |
| O6 | clean committed beta after reopen | none | equal | equal | 21-24 | 12 | recovered |

Each round appended the filesystem observation, Git observation, filesystem
admission, and Git admission in that handling order. All admissions used the
existing normal comparator and were admitted.

## Repeated State and Occurrence

Repeated filesystem configurations at O1/O2, O3/O4, O4/O5, and O5/O6 reused
the current structural `snapshot_id`, candidate envelope identity, and signal
identity. Their capture timestamps, ledger record IDs, commit indices, and
record digests differed.

Equivalent Git configurations at O1/O2, O3/O4, and O5/O6 were identified only
by the experiment-local surface of HEAD, branch, porcelain status, and capture
errors. Each repeated Git capture had a new timestamp-derived observation ID,
candidate envelope identity, signal identity, ledger record ID, commit index,
and record digest. No production Git configuration identity was introduced.

The ledger therefore preserved twelve observation occurrences even when a
source-relative state identity repeated. No deduplication occurred. The result
strengthens the existing scoped D-0016 evidence; it does not require a new
universal occurrence identity.

## Cross-Source Non-Collapse

O4 and O5 had equal filesystem structural identity because `state.txt` was not
rewritten and `.git` remained outside snapshot scope. Over the same transition,
Git HEAD changed and the dirty status cleared.

The two sources remained separate observation and provenance regimes. The
experiment did not infer that unchanged filesystem structure meant an
unchanged world or that changed Git state meant changed working-tree content.

## Temporal Depth and Historical Conservation

After each round:

- per-record integrity and ledger continuity passed;
- independent ledger reads produced the same canonical replay;
- reconstruction and admitted projection rebuilt structurally identically;
- source provenance remained separate;
- the O1 four-record ordered-digest witness remained a prefix.

Record count grew monotonically from 4 to 24. Reconstruction grew from 2 to 12
observations, and projection grew from 2 to 12 subjects. No earlier occurrence
was overwritten or collapsed.

The witness remained experiment-local. No hash chain, manifest, checkpoint, or
repair mechanism was added.

## Local Discontinuity

The first session function returned after O5. Its ledger, replay,
reconstruction, and projection objects went out of scope. A separate function
constructed a fresh `JsonlLedger` from the same path and, before O6, recovered
from disk:

```text
20 records
10 observations
10 admission relations
10 projection subjects
10 companion rows
```

Independent disk reconstructions, projections, and companions were equal. O6
then extended the reopened ledger to 24 records. The continuation used no
reconstruction or projection object from the first session. The declared O1
witness crossed the boundary only as non-authoritative comparison evidence.

This establishes bounded history and reconstruction continuity, not persistent
participant or session identity.

## Chart 11 Companion

Every projected occurrence had one normal admitted decision and no rejected or
unresolved decision. At every round, the read-only companion returned one row
per projection member with an empty `non_admitted_decision_states` list.

Temporal depth did not require admission multiplicity or direct admission-record
IDs in the companion. Projection subject IDs already preserved navigation to
each occurrence and its full reconstructed admission evidence. Chart 11 and
D-0041 remain unchanged.

## Epistemic Audit

Complete source observations remained in candidate signal payloads. Ledger
append added occurrence coordinates without changing source claims. Normal
admission increased certainty only to validity under the named comparator.

Projection omitted full payload and admission detail but retained navigation to
authoritative reconstruction; companion output stated only the non-admitted
states present in recorded evidence. Additional rounds did not aggregate
confidence or convert repetition into stronger truth.

The required sequence produced no mismatch or unresolved admission, so that
coordinate was not re-pressured. Existing vertical-composition evidence remains
the basis for keeping those outcomes independent from structural success.

## Chart 12

Execution earned a bounded round-by-coordinate surface. Its stable coordinates
are world condition, source-relative configuration relation, ledger occurrence,
reconstruction, projection, historical prefix, and session boundary.

Chart 12 is not a generalized state model, field schema, observer base class,
or persistent runtime. It records only the six executed rounds above.

## Result

The current bounded stack remained epistemically coherent across unchanged
repetition, an uncommitted content transition, a commit-only Git transition,
and local session discontinuity. Existing structures already preserve the
needed distinctions:

- D-0011 keeps filesystem and Git observation separate;
- D-0016 separates structural state identity from observation occurrence;
- D-0030 separates history extension from mutation;
- D-0041 separates projection membership from admission resolution.

No distinction was added or amended. No production module, contract, registry
entry, comparator policy, persistent service, daemon, scheduler, watcher,
database, or generalized identity was added.

The strongest invariant is that every captured occurrence receives distinct
ledger coordinates while observer-relative configuration identities may repeat.
The strongest local failure is that filesystem snapshot and candidate-envelope
identity alone cannot name a repeated occurrence; existing timestamps and
ledger coordinates prevent that limitation from becoming stack-level loss.

## Canonical History

`traces/live_ingest_ledger_v0.jsonl` had SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after execution. It remained untouched.

## Unresolved Horizon and Next Frontier

This bounded field did not test concurrency, partial writes, capture errors, or
admission disagreement over time. The next smallest frontier is to pressure an
explicitly invoked foreground persistent coordinator before considering any
daemon, scheduler, watcher, or service.

## Verification

Final targeted tests passed 72/72. The full suite passed 276/276.
