# Repository Transition Pressure v0

## Status

Second bounded live repository observation completed.

This pass used the naturally occurring transition from the first live baseline to the post-cleanup repository state. It did not manufacture `tests/fixtures/repo_observation_probe.txt`.

## Observations

Baseline:

- S0: `repo-snapshot-v0:660b63323c908e534c2d7b55ee8c222c30d1d3f646ac131babccd779fa3aadfd`
- G0: `git-state-v0:2026-09-06T06:07:20.620023Z`
- G0 HEAD: `5f1181accff683eb5149b345c9a14daf4f98990c`

Current:

- S1: `repo-snapshot-v0:be452e352e465ed7ec1184fdf7ebc5340be49bf0de0188f76e53f3d783ec12fd`
- G1: `git-state-v0:2026-09-06T06:32:38.356400Z`
- G1 HEAD: `0a981a3339991208ce370bbceecc0c6dc9b05613`

Evidence artifacts:

- `traces/repo_snapshot_v0_post_cleanup.json`
- `traces/git_state_v0_post_cleanup.json`
- `traces/repo_transition_pressure_v0.json`

## Filesystem Transition

`S0 -> S1` exposed endpoint structure only.

- added paths: 0
- removed paths: 0
- content-changed paths: 5
- entry count delta: 0
- total byte delta: 288
- capture error delta: 0

Changed paths:

- `PROJECT_STATE.md`
- `docs/contracts/README.md`
- `docs/contracts/ingest.md`
- `docs/contracts/provenance.md`
- `docs/decisions/repo_provenance_pressure_v0.md`

## Git Transition

`G0 -> G1` exposed Git state and retrospective ancestry.

- branch changed: no, `main -> main`
- HEAD changed: yes
- baseline status entries: 13
- current status entries: 0
- status added: 0
- status removed: 13
- capture errors: 0 -> 0

Retrospective commits traversed:

- `c4cba9ac923c63ff3f2e3e1f0bb5cce5dfd7b28c` `Project Provenance Source`
- `0a981a3339991208ce370bbceecc0c6dc9b05613` `Cleanup pass`

Git reconstructed commit history and changed paths after the fact. It did not provide contemporaneous filesystem events for the interval.

## Correspondence

Path correspondence summary:

- rows: 54
- filesystem added: 0
- filesystem removed: 0
- filesystem content changed: 5
- Git commit-touched paths: 16
- Git status removed: 13
- Git status added: 0
- exact correspondences: 49
- regional correspondences: 2
- Git-visible filesystem-out-of-scope paths: 3
- unresolved correspondences: 0
- same filesystem bytes later committed: 8

Regional Git-to-filesystem correspondences:

- `src/capture/` -> `src/capture/__init__.py`, `src/capture/git_state.py`, `src/capture/repo_snapshot.py`
- `tests/capture/` -> `tests/capture/__init__.py`, `tests/capture/test_repo_snapshot.py`

Git-visible but genuinely filesystem-out-of-scope paths:

- `traces/git_state_v0_baseline.json`
- `traces/repo_provenance_pressure_v0.json`
- `traces/repo_snapshot_v0_baseline.json`

Unchanged filesystem bytes that nevertheless participated in Git history:

- `docs/contracts/capture.md`
- `docs/distinctions/registry.jsonl`
- `src/capture/__init__.py`
- `src/capture/git_state.py`
- `src/capture/repo_snapshot.py`
- `src/runtime/repo_provenance_pressure.py`
- `tests/capture/__init__.py`
- `tests/capture/test_repo_snapshot.py`

This shows Git state transformation without corresponding filesystem content transformation over the observed interval.

## Correspondence Amendment

The initial correspondence interpretation counted 5 Git-visible paths as filesystem-out-of-scope.

That over-counted genuine scope mismatch because path membership alone could not distinguish:

```text
excluded observational region
from
coarser Git directory representation
```

The amended classifier decomposes that ambiguity:

- 3 genuine filesystem-out-of-scope paths remain under excluded `traces/`
- 2 regional correspondences map Git directory-level entries to observed filesystem leaves
- 0 unresolved Git correspondences remain for this transition

`src/capture/` and `tests/capture/` are not evidence that Git observed regions invisible to the filesystem observer. They are evidence that Git porcelain represented regions at directory granularity while the filesystem observer represented file descendants.

This does not claim directory-level observation is equivalent to leaf-level observation.

## Identity Pressure

Repeated unchanged temporary filesystem observations produced:

- same `snapshot_id`: yes
- different observation interval: yes
- same candidate `envelope_identity`: yes

Current filesystem envelope identity therefore collapses same structural state observations into the same envelope identity. This is exposed pressure, not yet an amendment.

Metadata-only temporary pressure produced:

- `snapshot_id` changed: yes
- `changed_paths` count: 0

Snapshot identity and content-change comparison do not use the same equivalence relation.

## Ingest And Ledger

Current candidate envelopes:

- filesystem envelope JSON-domain valid: yes
- Git envelope JSON-domain valid: yes

Temporary multi-source ledger result:

- append order: filesystem, then Git
- append order claim: experimental handling order, not source chronology
- replayed sources: `repository_filesystem_snapshot`, `repository_git_state`
- replayed payload observers: `repo_snapshot`, `git_state`
- schema shadow-valid records: 2
- commit indices: 1, 2
- integrity verification: yes

The ledger preserved heterogeneous raw observations without collapsing source-specific provenance in this bounded handshake.

## Timing Surface

Timing and order claims surfaced:

- filesystem observation interval: observer-produced
- file `mtime_ns`: source-provided metadata
- Git `observed_at`: observer-produced
- Git commit timestamps: retrospectively reconstructed
- candidate `arrival_time`: handling-produced provisional mapping from capture completion or Git observation time
- ledger `commit_index`: ledger-produced

These are not one clock.

## Root Identity

Both v0 observers invoked with `.` preserved:

```text
root_identity.name = ""
```

This exposes:

```text
invocation path representation != stable specimen identity
```

Do not change v0 identity semantics inside this comparison. A later observer-version amendment is warranted.

## Earned Distinctions

- `filesystem_scope != git_scope`
- `structural_state_identity != observation_occurrence_identity`
- `snapshot_identity != content_change_classification`
- `retrospective_git_history != contemporaneous_filesystem_history`
- `working_tree_state != committed_state`
- `raw_observation != derived_comparison`
- `invocation_path != stable_source_identity`
- `directory_level_observation != leaf_level_observation`

`capture_finished_at != ingest_arrival_time` remains unresolved pressure, not a registry entry from this pass.

## Contract Changes

Capture remains implemented only within the bounded repository specimen.

Provenance remains projected with bounded live evidence.

Ingest remains projected with candidate live handshakes.

Ledger remains pressure-tested within the current declared scope.

Schema remains descriptive and shadow-only.

## Next Frontier

The closest failure horizon is ingest admission:

```text
Which observed structures may become admitted envelopes, and which must remain capture errors, unavailable fields, or rejected candidates?
```

The controlled probe-file experiment remains useful, but it should now test a complementary regime: a deliberately created filesystem content transition observed before Git commit, after Git status, and after commit, without using excluded `traces/`.
