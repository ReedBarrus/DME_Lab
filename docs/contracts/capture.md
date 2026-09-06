# Capture Adapter Contract

## Status

Implemented within the bounded repository specimen.

General OS and Windows event capture remain deferred.

## Role

A capture adapter would convert external OS or source behavior into raw observations.

## Input

External source behavior.

## Output

Raw observation structure for ingest.

## Must Preserve

- observed identity when available
- observed time when available
- observed type when available
- observed payload when available
- visible missingness when source information is unavailable

## Must Not Claim

- complete OS history
- intent
- causality
- consequence
- truth beyond captured observation structure

## Known Pressure

- no live Windows capture exists
- real source event shape is unknown
- capture timing, source sequence, and arrival time may diverge
- repository snapshots observe endpoint structure, not complete transformation history

## Evidence

Bounded repository observer evidence exists:

- `src/capture/repo_snapshot.py`
- `src/capture/git_state.py`
- `tests/capture/test_repo_snapshot.py`
- `traces/repo_snapshot_v0_baseline.json`
- `traces/git_state_v0_baseline.json`

This evidence does not validate general OS or Windows event capture.
