# Live Vertical Probe v0

## Pressure

Can a real bounded repository change move through capture, observation persistence,
admission, replay, reconstruction, admitted projection, and provenance navigation
without adding index, topology, policy, or semantic interpretation?

## Controlled Specimen

`tests/fixtures/repo_observation_probe.txt`

The file was absent at T0, created with deterministic text at T1, and committed
at T2 in commit `8343e83a1db8bc9a0557d2e563662f43c1225aca`.

## Ordering

For each observation point, filesystem state was captured in memory, then Git
state was captured in memory.

The trace was written only after T0, T1, and T2 filesystem/Git captures completed.

Ledger append order records handling order, not source chronology.

## Result

The bounded trace records:

- 3 filesystem observations
- 3 Git observations
- 6 observation records
- 6 admission records
- 6 admitted decisions
- 6 reconstructed observation/admission relationships
- 6 admitted projection subjects

Replay of the authoritative records rebuilt the same reconstruction and projection
structurally.

## Extraction Amendment

The original trace at
`6c999affebde4d5ae741e44eb37a77cee2c9d60c:traces/live_vertical_probe_v0.json`
embedded the complete authoritative ledger history.

That history was extracted to `traces/live_ingest_ledger_v0.jsonl`.

The current trace is compacted to experiment summary, canonical ledger reference,
record summaries, integrity/rebuild evidence, transition visibility, and
provenance navigation examples.

## Evidence

- `traces/live_vertical_probe_v0.json`
- `traces/live_ingest_ledger_v0.jsonl`
- `tests/runtime/test_live_vertical_probe.py`

## Deferred

No index, topology, graph database, generalized policy, conflict resolution,
watcher, Windows capture adapter, or generalized reconstruction/projection engine
was added.
