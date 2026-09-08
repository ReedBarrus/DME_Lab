# Foreground Persistent Coordinator Pressure v0

## Scope

This Phase-C pass removed ownership of the world trajectory from observation
coordination. A separate driver changed a real temporary Git repository while
the candidate coordinator only executed explicit capture requests through the
already-earned stack:

```text
filesystem and Git capture
-> existing ingest envelopes
-> observation append
-> normal admission append
-> replay
-> reconstruction
-> admitted projection
-> non-admitted companion
-> non-authoritative current result
```

Starting state was clean `main` at
`d80cc701c7e03ab377600869ce46812adb62b922`. Chart 12 tests passed 21/21 and
the full baseline passed 276/276.

The experiment did not modify `docs/projection/Persistent_Ecology.md` or append
to canonical live history.

## Candidate

The experiment first tested an experiment-local candidate with only three
process-local fields:

```text
root
ledger_path
closed flag
```

It had no round counter, last snapshot, previous Git state, record-count cache,
reconstruction cache, or projection cache. Every `capture_round()` created a
ledger handle from the path, captured the filesystem and Git, appended two
observations and two normal admissions, replayed authoritative history, and
rebuilt current derivations.

The coordinator did not write fixture files, run Git commits, decide when to
capture, schedule future work, know the next world state, or know the total
number of calls.

## Externally Controlled Trajectory

| Call | External world condition | Driver action before call | Record range | Reconstructed observations | Coordinator lifetime |
| --- | --- | --- | ---: | ---: | --- |
| C1 | clean alpha | create and commit fixture | 1-4 | 2 | first |
| C2 | repeated clean alpha | none | 5-8 | 4 | first |
| C3 | dirty beta | rewrite `state.txt` outside coordinator | 9-12 | 6 | first |
| C4 | clean committed beta | add and commit outside coordinator without rewriting | 13-16 | 8 | first |
| C5 | dirty gamma | rewrite while coordinator absent; reopen; capture | 17-20 | 10 | second |

C1/C2 preserved equivalent filesystem and Git configurations while receiving
new ledger observation records. C2/C3 changed filesystem content and Git
working status while HEAD remained fixed. C3/C4 preserved filesystem structural
identity while the external commit changed Git HEAD and cleared status.

The coordinator did not encode any expected relation among these calls.

## Durable and Process-Local State

The only durable coordinator history required was:

```text
ledger path
+
authoritative ledger contents
```

The root path remained an external source locator, not historical metadata.
No coordinator metadata, manifest, checkpoint, persisted round count, cached
projection, or cached reconstruction was created.

After C4 the first coordinator was closed and destroyed. A fresh coordinator
used the same root and ledger paths. Before capturing C5, `current_result()`
recovered from disk alone:

```text
16 records
8 observations
8 admission relations
8 projection subjects
8 companion rows
```

That read appended nothing. C5 then legitimately extended history to 20
records. Coordinator close state was process-local and was not persisted.

## Absent Interval

The external driver rewrote `state.txt` from beta to gamma while no coordinator
object existed. The ledger remained byte-identical during that mutation and
contained no record for the absent interval.

After reopen, the real observers captured a gamma filesystem endpoint and a
dirty Git endpoint. An experiment-local snapshot comparison established that
the newly captured endpoint differed from the last captured beta endpoint.

The DME claim remained strictly bounded:

```text
newly captured endpoint differs from last captured endpoint
intermediate transformation history is unavailable
```

No intermediate state, transition time, transition mechanism, or synthetic
transition record was invented. Existing D-0012 was sufficient for this
boundary: a snapshot is not complete transformation history.

## Result Surface

Each explicit capture returned a detached, non-authoritative result containing:

- summaries of the four new record identities and commit indices;
- the two existing raw source observations;
- integrity, continuity, and replay status;
- reconstruction counts;
- the admitted projection;
- the non-admitted companion.

It did not return or persist a round identity. The ledger assigned all record
coordinates. The surface is a bounded repository observation result, not a
dashboard or generalized view system.

## Integrity, Reconstruction, and Projection

Every call passed record integrity, start-at-one continuity, and reproducible
canonical replay. The C1 four-record ordered-digest witness remained a prefix
through C5 without persistent witness infrastructure.

Reconstruction and projection rebuilt structurally identically after every
call. Projection grew from 2 to 10 subjects without overwriting prior
occurrences. Filesystem and Git provenance remained separate.

All ten observations received one normal admitted decision. The Chart 11
companion returned one empty-state row per projected subject. Foreground
coordination required neither admission multiplicity nor direct admission IDs
in the companion and did not turn projection membership into admission
resolution.

## Epistemic Audit

The coordinator introduced no knowledge beyond source evidence. Process-local
memory did not strengthen certainty, repeated captures did not aggregate
confidence, restart lost no authoritative evidence, and current state did not
overwrite history.

Most importantly, the externally known beta-to-gamma mutation was kept
separate from what DME could claim. DME observed two endpoints around a missing
interval; it did not reconstruct the driver's action as observed history.

## Production Promotion

The candidate succeeded across five caller-selected captures, two independently
caused working-tree changes, an external commit, destruction/reopen, disk-only
recovery, and continuation. That execution earned the small reusable
composition boundary.

`ForegroundRepositoryObservationCoordinator` was therefore promoted in
`src/runtime/foreground_repository_observation.py` and exported from
`src/runtime`. Promotion includes only the repository-specific, foreground,
explicitly invoked, single-writer composition. The external trajectory driver,
fixture mutation, chart evaluation, and absent-interval interpretation remain
experiment-local.

No daemon, watcher, poller, timer, scheduler, background thread, async event
bus, source registry, generalized observer class, database, networking, agent,
planner, or persistent ecology runtime was added.

## Chart 13

Execution earned a bounded caller-selected-capture matrix. Its stable
coordinates are external world action, coordinator lifetime, source-relative
configuration, ledger range, reconstruction, and historical prefix.

Chart 13 is not a generalized state model or autonomous runtime. It records
only the five executed foreground calls and two coordinator lifetimes.

## Distinction

Execution independently forced and registered D-0042:

```text
coordinator_lifetime != historical_continuity
```

The first coordinator ceased to exist, yet a fresh coordinator recovered all
16 prior records and derived state from disk before continuing. The distinction
does not assert persistent participant identity or define a universal field.

Charts 4-12, D-0012, D-0016, D-0040, D-0041, any-admitted projection,
non-admitted companion, source separation, and ordered-digest prefix semantics
remain preserved within their prior scopes.

## Strongest Results

The strongest invariant is that authoritative ledger history, not coordinator
lifetime, supplies operational continuity.

The strongest bounded failure is that the coordinator cannot recover events
inside an unobserved interval. It can expose only a later captured endpoint.

The strongest unresolved horizon is partial-round failure: one requested round
performs four sequential appends, but no current test establishes atomicity or
the meaning of a ledger ending partway through that group.

## Next Smallest Frontier

Isolate partial-round append failure before adding autonomy, polling, Windows
observation, or new sources.

## Canonical History

`traces/live_ingest_ledger_v0.jsonl` remained unchanged at SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.

## Verification

Final targeted tests passed 44/44. The full suite passed 299/299.
