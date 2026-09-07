# Contract Surface v0

This map shows the current DME_Lab transformation boundaries, their maturity, and the evidence supporting each status.

Contract text is not proof. A boundary status should say no more than the strongest evidence available for its scope.

## Status Vocabulary

- `projected`: Described enough to guide future work, but not yet executed or tested sufficiently.
- `implemented`: A concrete mechanism exists, but the boundary has not yet earned strong support under deliberate pressure.
- `pressure-tested`: Executable tests or runtime evidence exercise the stated guarantees within a declared scope.
- `deferred`: Known to exist in the larger projection, but intentionally outside current implementation pressure.

## Boundary Map

| Boundary | Status | Current Role | Evidence | Open Pressure |
| --- | --- | --- | --- | --- |
| Capture Adapter | implemented within bounded repository specimen; general OS deferred | Convert external source behavior into raw observations. | `src/capture/repo_snapshot.py`; `src/capture/git_state.py`; `tests/capture/test_repo_snapshot.py`; `traces/repo_snapshot_v0_baseline.json`; `traces/git_state_v0_baseline.json`; `traces/repo_snapshot_v0_post_cleanup.json`; `traces/git_state_v0_post_cleanup.json`; `traces/repo_transition_pressure_v0.json`; `traces/live_vertical_probe_v0.json` | real OS observation shape; stable root identity; explicit perturbation sequence |
| Signal | projected | Represent primitive observed event content. | `docs/contracts/signal.md`; `docs/projection/v0_observability.md` | field encodings under real observation pressure |
| Provenance | projected | Surround a signal with origin and handling metadata. | `docs/contracts/provenance.md`; synthetic fields in ledger tests; bounded repository provenance construction in shadow mode; `traces/repo_transition_pressure_v0.json`; `traces/live_vertical_probe_v0.json` | real source sequence, arrival time, integrity behavior, final provenance schema |
| Ingest Envelope | projected; bounded v0 admission mechanism implemented | Admit raw observation structure into the ledger boundary while preserving provenance and missingness. | `docs/contracts/ingest.md`; synthetic ledger envelopes; bounded live candidate-envelope handshakes; `src/ingest/admission.py`; `tests/ingest/test_admission.py`; `traces/ingest_admission_pressure_v0.json`; `traces/live_vertical_probe_v0.json` | general admission behavior; policy conflict resolution; malformed and unavailable source structure |
| Append Ledger | pressure-tested | Commit admitted envelopes as stable append-only records. | `src/ledger/jsonl.py`; `tests/replay/test_ledger_harness.py`; `traces/ledger_runtime_pressure_v0.json`; `docs/decisions/ledger_runtime_pressure_v0.md`; `traces/live_vertical_probe_v0.json` | scale, serialization stability, single-writer assumption, amendment lookup |
| Raw Replay | pressure-tested | Return committed ledger records in canonical `commit_index` order. | `src/ledger/jsonl.py::JsonlLedger.replay`; ordering and amendment tests; `traces/live_vertical_probe_v0.json` | canonical order vs physical file order; replay cost; no resolved amendment view |
| Reconstruction | projected; bounded v0 admission relationship reconstruction implemented | Derive deterministic recoverable structure from replayed ledger input. | `docs/contracts/reconstruction.md`; `src/reconstruction/admission.py`; `tests/reconstruction/test_admission_reconstruction.py`; `traces/reconstruction_pressure_v0.json`; `traces/live_vertical_probe_v0.json` | generalized topology; index pressure; admission conflict policy |
| Exposed Projection | projected; bounded admitted projection implemented | Expose selected reconstructed structure without becoming proof or raw evidence. | `docs/contracts/projection.md`; `docs/projection/v0_observability.md`; `src/reconstruction/admission.py`; `traces/reconstruction_pressure_v0.json`; `traces/live_vertical_probe_v0.json` | generalized projection engine; admission conflict policy |

## Preserved Non-Equivalences

- projected contract != implemented boundary
- implemented boundary != pressure-tested boundary
- pressure-tested boundary != machine schema
- documented != implemented
- implemented != validated
- synthetically exercised != validated against live observations
- trace produced != guarantee established
- projection != proof
- descriptive schema != enforced schema
- schema-valid != integrity-valid
- per-record schema != ledger-wide invariant
- runtime-produced != schema-valid
- filesystem observation != Git observation
- snapshot != complete transformation history
- observation interval != event time
- shadow schema comparison != admission decision
- filesystem scope != Git scope
- structural state identity != observation occurrence identity
- snapshot identity != content-change classification
- retrospective Git history != contemporaneous filesystem history
- working-tree state != committed state
- raw observation != derived comparison
- invocation path != stable source identity
- persisted observation != admission classification
- rejected != deleted
- observation identity != admission classification
- authoritative history != reconstructed representation
- reconstruction != projection
- capture sequence != ledger commit order

Registry entries may point toward supporting evidence, but the registry alone does not upgrade a boundary status.
