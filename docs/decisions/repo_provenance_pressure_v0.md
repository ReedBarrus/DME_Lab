# Repository Provenance Pressure v0

## Status

First bounded live repository observation completed.

This pass observed DME_Lab as a repository specimen. It did not implement general OS capture, filesystem watching, semantic diffing, reconstruction, projection, databases, graph systems, agents, or continuous telemetry.

## Filesystem Observation Boundary

The filesystem observer records a deterministic structural snapshot of the repository working tree.

Snapshot shape:

```text
snapshot_id
observer
observer_version
observation_started_at
observation_finished_at
root_identity
scope
entries
capture_errors
duration_seconds
```

Each file entry records:

```text
path
kind
size_bytes
mtime_ns
sha256
```

Paths are repository-relative. File contents are not stored.

## Git Observation Boundary

Git state is observed separately.

Git observation shape:

```text
observation_id
observer
observer_version
observed_at
root_identity
head_sha
branch
status_porcelain
capture_errors
```

Git is not used to correct the filesystem snapshot. It is a second observation regime.

## Scope And Exclusions

The filesystem snapshot observes working tree files under `.` while excluding:

- `.git/`
- `__pycache__/`
- `traces/`
- `*.pyc`

These exclusions prevent instrument noise and generated traces from dominating the first live specimen. A path outside scope is not the same claim as a path absent from the repository.

## Temporal Model

A snapshot is an observation interval:

```text
observation_started_at
observation_finished_at
```

File `mtime_ns` is preserved as file metadata. It is not interpreted as event time.

`snapshot_id` is content-derived from structural entries, scope, root identity, and capture errors. Two observations can therefore share structural identity while still having different observation intervals.

## Candidate Provenance Fields

The live evidence required only:

- observer
- observer version
- root identity
- explicit scope
- observation started at
- observation finished at
- capture errors

Filesystem and Git provenance remain distinct.

## Candidate Ingest Envelope

The candidate filesystem envelope carried:

```text
envelope_identity
source
source_sequence
event_time
arrival_time
capture_version
provenance
signal
missingness
```

The signal payload was the raw filesystem snapshot. `signal.time` and `source_sequence` were marked unavailable rather than inferred.

## Admission Handshake

The live handshake executed:

```text
live filesystem observation
-> candidate provenance envelope
-> JSON-domain check
-> temporary ledger append
-> ledger record schema shadow validation
-> raw replay
-> integrity verification
```

Schema validation remained shadow-only. It did not regulate append.

## Ledger And Schema Result

Baseline evidence:

- filesystem entries: 49
- filesystem capture errors: 0
- filesystem total bytes: 117851
- Git branch: `main`
- Git status entries: 13
- candidate envelope JSON-domain valid: yes
- temporary ledger append attempted: yes
- ledger record schema shadow-valid: yes
- replayed records: 1
- integrity verification: yes
- temporary ledger bytes written: 10391

Evidence artifact:

```text
traces/repo_provenance_pressure_v0.json
```

Baseline observations:

```text
traces/repo_snapshot_v0_baseline.json
traces/git_state_v0_baseline.json
```

## Live Pressure Beyond Synthetic Fixtures

- The live repository snapshot is structurally richer than prior synthetic envelopes.
- Complete-envelope storage remains workable for this baseline, but the envelope already reached 10193 bytes for one record.
- Filesystem observation and Git observation expose different surfaces and must remain separate.
- The snapshot captures endpoint structure, not complete transformation history.
- Observation interval, file `mtime_ns`, Git `observed_at`, and ledger `commit_index` remain different timing/order claims.

## Unknowable Between Snapshots

The observer can compare endpoint structures:

```text
S0 -> ? -> S1
```

It cannot reconstruct intermediate transformations that occurred between observations.

## Contract Amendment Recommendation

Do not amend the ledger, schema, reconstruction, or projection contracts from this run.

The provenance and ingest contracts do not need immediate amendment, but this run makes their next pressure clearer: admission rules for real observed structures.

## Runtime Amendment Recommendation

Do not amend `JsonlLedger.append()` yet.

The live candidate envelope is JSON-domain valid, schema shadow-valid after ledger wrapping, replayable, and integrity-verifiable.

## Second Snapshot Justification

A second live snapshot is now justified.

The first baseline cannot test observed repository change because no controlled live perturbation was introduced. The comparison code is tested with temporary directories, but live comparison needs an approved specimen change.

## Recommended Controlled Perturbation

For snapshot #2, do not use `traces/` because it is excluded.

Prefer adding or editing a small file under a clearly scoped non-trace path, such as:

```text
tests/fixtures/repo_observation_probe.txt
```

Then capture a second filesystem snapshot and Git observation and compare them to the baseline.

## Next Pressure Frontier

The next pressure frontier is live ingest/provenance admission:

```text
Which live observed structures may enter the ledger as admitted envelopes, and which malformed or unstable observations must remain capture errors or missingness?
```
