# Live Ingest Ledger Extraction v0

## Pressure

`traces/live_vertical_probe_v0.json` embedded both experiment report data and
the twelve authoritative observation/admission records.

The next pressure was whether authoritative live history could move to a
canonical ledger surface while the trace became summary plus references.

## Chosen Ledger Surface

`traces/live_ingest_ledger_v0.jsonl`

This path is already outside the bounded repository filesystem observer scope,
because `traces/` is excluded. No observer exclusion policy changed.

The directory name remains historical. The semantic role of this file is the
canonical bounded live ingest ledger, not an experiment report.

## Extraction

Source embedded artifact:

`6c999affebde4d5ae741e44eb37a77cee2c9d60c:traces/live_vertical_probe_v0.json`

Extracted field:

`authoritative_history.records`

The extracted records preserved record IDs, commit indices, envelopes, integrity
data, and replay order.

The compact trace now records ledger reference, record summaries, extraction
provenance, integrity result, rebuild equality, transition visibility, and
provenance navigation examples.

## Result

Runtime reconstruction now reads canonical ledger replay before deriving
reconstruction and projection.

The trace is no longer authoritative record storage.

The canonical ledger preserves only observation and admission records. It does
not persist reconstruction or projection.

## Evidence

- `traces/live_ingest_ledger_v0.jsonl`
- `traces/live_vertical_probe_v0.json`
- `src/ledger/live_ingest.py`
- `src/runtime/live_vertical_probe.py`
- `tests/runtime/test_live_vertical_probe.py`

## Deferred

No database, index, projection persistence, generalized amendment policy,
semantic authority mechanism, topology, coordinate system, or watcher was added.
