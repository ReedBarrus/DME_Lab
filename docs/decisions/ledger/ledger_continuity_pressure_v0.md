# Ledger Continuity Pressure v0

## Pressure

The canonical live ingest ledger proved continuation, but record verification
still checked each record independently.

This pressure asked whether individually valid records can compose an invalid
ledger history.

## Boundary

`JsonlLedger.verify()` remains per-record parse and digest verification.

Ledger-wide continuity is separate:

`verify_continuity(records, require_start_at_one=False)`

The canonical live ingest wrapper requires start at 1:

`verify_canonical_live_ingest_continuity()`

## Invariants

The continuity verifier checks only:

- unique `commit_index`
- continuous internal `commit_index` sequence
- unique `record_id`

The canonical live ingest wrapper additionally requires the sequence to start
at `1`.

It does not validate source chronology, event chronology, truth, physical JSONL
line order, admission relationships, reconstruction, or projection.

## Specimens

Temporary copies of `traces/live_ingest_ledger_v0.jsonl` were used.

- control exact copy: record verification passed; continuity passed
- whole-record deletion of `rec-000007`: record verification passed; continuity failed with missing commit index `7`
- duplicate commit index: record verification passed; continuity failed with duplicate commit index `2` and missing commit index `4`
- duplicate record ID: record verification passed; continuity failed with duplicate record ID `rec-000002`
- reversed physical JSONL lines: record verification passed; continuity passed after canonical replay

The canonical 14-record live ingest ledger passed continuity.

## Evidence

- `src/ledger/continuity.py`
- `tests/replay/test_ledger_continuity.py`
- `traces/ledger_continuity_pressure_v0.json`

## Deferred

No hash chain, manifest, database, index, signature, locking, concurrency support,
amendment record, repair logic, or partial-write recovery was added.
