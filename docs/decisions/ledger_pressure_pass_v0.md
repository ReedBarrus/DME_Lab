# Ledger Pressure Pass v0

## Status

Pressure pass before runtime implementation.

No code, schema, Windows capture adapter, semantic interpretation, consequence model, agent layer, or feedback layer is introduced here.

## Hidden Assumptions

### Deterministic Order

- Assumes one total commit order is required for useful replay.
- Assumes commit order is the replay order, even when source sequence or event time disagree.
- Assumes source sequence, event time, arrival time, and commit index are distinguishable in admitted envelopes.
- Assumes single-writer append is enough for the first runtime.

### Stable Identity

- Assumes `record_id` and envelope identity are separate identity domains.
- Assumes one replayed record maps to exactly one committed ledger record.
- Assumes duplicate source observations can be preserved without merging by identity.
- Assumes record identity does not imply observed-subject identity.

### Envelope Preservation

- Assumes complete-envelope storage is acceptable for first replay tests.
- Assumes preserving bytes or canonical content is more important than normalizing shape.
- Assumes envelope preservation does not require interpreting payload fields.
- Assumes the ledger can reject or mark malformed envelopes before silently repairing them.

### Integrity

- Assumes per-record integrity is sufficient for the first runtime.
- Assumes history-level integrity can remain deferred.
- Assumes a content hash over a stable representation is testable.
- Assumes integrity verification detects mutation but does not establish truth.

### Missingness Preservation

- Assumes missingness can be represented structurally without semantic explanation.
- Assumes `missing`, `unavailable`, `malformed`, and `unknown` may need to remain distinguishable later.
- Assumes missing fields should not be replaced with defaults during commit or replay.
- Assumes explicit gaps can be committed as evidence of absence from the source envelope, not absence from reality.

### Append-Only Amendment

- Assumes correction can be represented as a later record pointing at an earlier record.
- Assumes replay can avoid ambiguity when both original and amendment are present.
- Assumes amendment relation names are provisional and should not drive runtime semantics yet.
- Assumes lookup cost is tolerable in the first local implementation.

## Strongest Counterexamples

- Two source events arrive in commit order `B, A` while source sequence says `A, B`; deterministic replay is stable but may not match event order.
- Two records preserve the same envelope identity due to capture retry; stable ledger identity survives, but envelope identity is no longer unique.
- A JSON encoder changes field order or numeric/string representation; content hash changes without source evidence changing.
- An amendment `corrects` an earlier record, but replay cannot tell whether to expose both records or a resolved view.
- A missing payload field is stored as `null`; replay cannot distinguish absent, unavailable, malformed, and explicitly null.

## Falsification Tests

### Deterministic Order

```text
guarantee -> deterministic order
mechanism -> append synthetic envelopes with conflicting event_time, source_sequence, and commit_index
resource cost -> replay cost, ordering contention
failure mode -> replay silently sorts by event_time or source_sequence
observed pressure -> commit order must stay distinct from event order
```

### Stable Identity

```text
guarantee -> stable identity
mechanism -> append two records with the same envelope identity and different record_id values
resource cost -> lookup cost, ambiguity
failure mode -> replay merges records or treats envelope identity as ledger identity
observed pressure -> identity domains must remain explicit
```

### Envelope Preservation

```text
guarantee -> envelope preservation
mechanism -> append an envelope with unusual field order, explicit null, missing field, and opaque payload
resource cost -> storage, verification cost
failure mode -> commit normalizes, fills, drops, or reorders information needed for replay comparison
observed pressure -> decide whether preservation means raw bytes, canonical JSON, or parsed structure
```

### Integrity

```text
guarantee -> integrity
mechanism -> mutate one persisted ledger line after commit and run verification
resource cost -> verification cost
failure mode -> mutation is not detected or hash input is unstable
observed pressure -> define stable hash boundary before schema work
```

### Missingness Preservation

```text
guarantee -> missingness preservation
mechanism -> append envelopes separately containing absent field, explicit null, malformed value, and unavailable value marker
resource cost -> storage, ambiguity
failure mode -> replay collapses distinct missing states into one value
observed pressure -> missingness representation needs a small structural convention
```

### Append-Only Amendment

```text
guarantee -> append-only amendment
mechanism -> append original record, append later amendment pointing to it, then replay in canonical order
resource cost -> amendment lookup cost, replay cost
failure mode -> replay erases original, ignores amendment, or exposes an unresolved contradiction as resolved
observed pressure -> define raw replay before any resolved replay view
```

## Smallest Runtime Hypothesis

- Synthetic envelope generator.
- Append operation assigning `record_id` and `commit_index`.
- Local append-only persistence, likely JSONL.
- Replay operation returning records in canonical commit order.
- Integrity writer and verifier over the chosen record boundary.
- Tiny test harness with synthetic fixtures.

The runtime should execute capture, commit, replay, verification, and reconstruction against current contracts only when those pieces exist. For the first ledger tests, capture and reconstruction can stay synthetic or stubbed at the boundary.

## Storage Hypothesis Pressure

Complete-envelope JSONL makes these easy:

- inspect committed history by eye
- append records locally
- replay in file order
- build synthetic fixtures
- corrupt one line for integrity tests
- compare raw replay output to committed input

It introduces these assumptions:

- one line can hold a complete envelope without practical storage pressure
- JSON encoding is stable enough for hashing or can be canonicalized
- local file append behavior is sufficient for first ordering tests
- complete envelope duplication is acceptable
- replay can load or stream records without memory pressure

Reconsider JSONL when observed pressure shows:

- storage grows mainly from repeated payload or provenance duplication
- replay requires random access rather than sequential scan
- amendment lookup becomes expensive enough to obscure test results
- integrity verification depends on fragile serialization details
- append contention prevents deterministic commit assignment

Evidence for references or content addressing would be:

- repeated payloads or envelopes dominate storage in measured fixtures
- integrity needs to verify shared content independently from ledger records
- replay can reconstruct the same committed history while resolving referenced immutable content deterministically
- missing referenced content remains visible as missing rather than silently becoming absent data

## First Topology Pressure

The first meaningful pressure is a synthetic replay where commit order disagrees with source sequence or event time:

```text
commit_index: 1, source_sequence: 2, event_time: T2
commit_index: 2, source_sequence: 1, event_time: T1
```

That result would force the project to keep distinguishing:

```text
commit order != event order
```

It does not yet require causal ordering. Causal or dependency order should remain deferred unless a source exposes an explicit dependency relation that replay must preserve without interpretation.

## Recommendation

Amend the ledger contract before implementation, but only narrowly.

The amendment should clarify:

- `record_id`, envelope identity, source sequence, event time, arrival time, and commit index are distinct claims when present.
- v0 replay exposes raw canonical commit order.
- resolved amendment views are deferred.
- integrity covers a defined record boundary and does not imply truth.
- missingness needs a small structural convention before tests.

Do not replace complete-envelope JSONL yet. Use synthetic tests to discover whether it breaks under actual storage, replay, verification, or ambiguity pressure.

## Provisional Choices

- JSONL storage.
- Complete-envelope records.
- Per-record hash.
- Single local append writer.
- Synthetic envelopes before live OS capture.
- Amendment relation names.

## Explicit Deferrals

- Windows capture adapter.
- Semantic interpretation.
- Intent inference.
- Consequence modeling.
- Feedback systems.
- Agents.
- Adaptive behavior.
- Navigation.
- Admissibility.
- Causal or dependency modeling.
- Databases, services, concurrency systems, or content addressing until pressure demands them.

## Recommended Next Step

Patch `docs/contracts/ledger.md` with the narrow clarifications above, then implement the smallest JSONL append/replay/integrity test harness using synthetic envelopes.

