# Capture Adapter Contract

## Status

Deferred.

## Role

A capture adapter would convert external OS or source behavior into raw observations.

## Input

External OS/source behavior.

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

## Evidence

No capture adapter implementation or live OS trace exists.

