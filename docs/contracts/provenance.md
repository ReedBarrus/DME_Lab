# Provenance Contract

## Status

Projected.

Provenance records how a signal entered the system. It surrounds the signal without redefining it.

## Role

Keep origin and handling context visible around primitive signal content.

## Input

Capture or synthetic metadata surrounding a signal.

## Output

Provenance metadata inside an ingest envelope.

## Initial Metadata

- envelope identity
- source
- sequence
- integrity
- capture version

## Must Preserve

- source information when present
- envelope identity when present
- source sequence when present
- integrity metadata when present
- capture version when present
- missingness when provenance information is unavailable

## Boundary

Provenance is not authority, interpretation, or proof of reality. It records origin and handling context.

## Must Not Claim

- truth
- semantic interpretation
- causality
- completeness
- authority over runtime evidence

## Open Pressure

The integrity mechanism and sequence guarantees need runtime evidence before being treated as stable.

Synthetic ledger tests exercise provenance-shaped fields, but do not validate a real provenance capture boundary.

## Evidence

Bounded repository provenance construction has been exercised in shadow mode:

- `src/runtime/repo_provenance_pressure.py`
- `traces/repo_provenance_pressure_v0.json`
- `docs/decisions/repo_provenance_pressure_v0.md`
- `src/runtime/repo_transition_pressure.py`
- `traces/repo_transition_pressure_v0.json`
- `docs/decisions/repo_transition_pressure_v0.md`
- `traces/live_ingest_ledger_v0.jsonl`
- `traces/live_vertical_probe_v0.json`
- `docs/decisions/live_vertical_probe_v0.md`
- `docs/decisions/live_ingest_ledger_extraction_v0.md`

This is bounded live repository evidence, not general provenance runtime validation. It does not establish final provenance schema or enforced admission rules.
