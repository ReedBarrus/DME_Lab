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
| Capture Adapter | deferred | Convert external OS/source behavior into raw observations. | none | real OS observation shape; capture identity and timing |
| Signal | projected | Represent primitive observed event content. | `docs/contracts/signal.md`; `docs/projection/v0_observability.md` | field encodings under real observation pressure |
| Provenance | projected | Surround a signal with origin and handling metadata. | `docs/contracts/provenance.md`; synthetic fields exercised inside ledger tests only | real source sequence, arrival time, and integrity behavior |
| Ingest Envelope | projected | Admit raw observation structure into the ledger boundary while preserving provenance and missingness. | `docs/contracts/ingest.md`; ledger input boundary; synthetic envelopes only | admission behavior; malformed and unavailable source structure |
| Append Ledger | pressure-tested | Commit admitted envelopes as stable append-only records. | `src/ledger/jsonl.py`; `tests/replay/test_ledger_harness.py`; `traces/ledger_runtime_pressure_v0.json`; `docs/decisions/ledger_runtime_pressure_v0.md` | scale, serialization stability, single-writer assumption, amendment lookup |
| Raw Replay | pressure-tested | Return committed ledger records in canonical `commit_index` order. | `src/ledger/jsonl.py::JsonlLedger.replay`; ordering and amendment tests | canonical order vs physical file order; replay cost; no resolved amendment view |
| Reconstruction | projected | Derive a deterministic topology from replayed ledger input. | `docs/contracts/reconstruction.md` | smallest topology target; same input -> same output |
| Exposed Projection | projected | Expose selected reconstructed structure without becoming proof or raw evidence. | `docs/contracts/projection.md`; `docs/projection/v0_observability.md` | reducibility to reconstructed evidence |

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

Registry entries may point toward supporting evidence, but the registry alone does not upgrade a boundary status.
