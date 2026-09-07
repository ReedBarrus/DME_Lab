# Ledger Contract — v0 Projection

## Status

Provisional contract.

Current status: pressure-tested within the synthetic v0 ledger scope, with bounded live vertical-chain evidence.

This document defines the minimum guarantees required of the first DME_Lab append-only ledger before a formal schema or runtime implementation is admitted.

The ledger is not yet a semantic, causal, or consequence model.

---

## Core Question

What minimum guarantees must an append-only ledger provide so that admitted event envelopes can be replayed deterministically, verified for integrity, and traced back to their source observations without introducing semantic interpretation?

---

## Role

The ledger converts admitted event envelopes into a conserved history.

It is responsible for:

* stable commit identity
* deterministic commit order
* preservation of admitted envelope content
* integrity verification
* explicit preservation of missingness
* explicit amendment rather than silent mutation
* replay access to committed history

The ledger is not responsible for deciding what an event means.

---

## Input Boundary

The ledger receives an admitted ingest envelope.

The current primitive signal is:

* identity
* time
* type
* payload

The surrounding provenance boundary may include:

* envelope identity
* source
* sequence
* integrity
* capture version

The ledger should preserve these distinctions without adding inferred semantics.

---

## Minimum Ledger Commit

A first ledger record should conceptually preserve:

```text
LedgerRecord
    record_id
    commit_index
    envelope
    integrity
```

This is an object sketch, not a formal schema.

The initial implementation should prefer storing the complete admitted envelope rather than depending on an external envelope store.

This favors replay clarity over storage efficiency.

---

## Distinct Identity and Ordering Claims

The following claims must remain distinguishable when present:

* `record_id`
* envelope identity
* source sequence
* event time
* arrival time
* `commit_index`

The ledger must not treat any one of these as a silent substitute for another.

---

## Core Guarantees

### 1. Deterministic Order

Every committed record receives one canonical append position.

```text
commit_index
```

Given the same ledger, replay must expose records in the same canonical sequence.

Commit order must not be silently rewritten to match inferred event chronology.

Observed time, source sequence, arrival order, and ledger commit order must remain distinguishable where available.

---

### 2. Stable Identity

Every committed ledger record has a stable ledger identity.

```text
record_id
```

A replayed record must be traceable to exactly one committed ledger record.

Ledger identity does not imply semantic identity of the observed subject.

---

### 3. Envelope Preservation

The ledger preserves the admitted envelope as committed.

The ledger must not silently:

* reinterpret it
* normalize it again
* repair missing fields
* reorder its internal meaning
* infer intent
* infer causality

If transformation of an envelope is ever required, that transformation must be explicit and separately traceable.

---

### 4. Integrity

The system must be able to test whether committed content remains the same content later used for replay.

The minimum integrity mechanism may be a content hash.

The hash boundary must be explicit before implementation. Integrity verifies preservation of committed content; it does not establish truth of the observed event.

Hash chaining between records is deferred until runtime evidence demonstrates a need for tamper-evident ledger chaining.

Integrity of a record and integrity of the full history are different claims.

---

### 5. Missingness Preservation

Missing, unavailable, incomplete, malformed, or uncertain source information must remain visible as such.

```text
missing != inferred
```

The ledger must not fill absent data with guessed or derived values.

If ingest admits an explicit gap, the ledger commits the gap.

Before implementation, tests should distinguish at least:

* absent
* explicit null
* unavailable
* malformed

These are structural states, not semantic explanations.

---

### 6. Append-Only Amendment

Committed history is not silently rewritten.

If a prior record later requires correction, invalidation, annotation, or replacement, the original record remains preserved and a later explicit amendment points to it.

Possible future amendment relations may include:

```text
annotates
supersedes
invalidates
corrects
```

These names are provisional.

Raw replay exposes committed records in canonical commit order. Any resolved amendment view is deferred.

---

## Explicit Non-Claims

The v0 ledger does not claim:

* meaning
* intent
* importance
* semantic confidence
* consequence
* value
* admissibility
* task membership
* episode membership
* inferred causal relation
* persistent identity continuity
* truth

A relation may be preserved when it is explicitly exposed by the source, but the ledger does not elevate source structure into interpreted causality.

---

## Replay Contract

Replay reads committed history according to canonical ledger order.

```text
ledger
-> ordered records
-> admitted envelopes
-> reconstruction
```

Replay must not require semantic interpretation.

Replay should reproduce the same ordered committed input sequence from the same valid ledger state.

Raw replay is currently treated as part of the ledger boundary. It does not provide a resolved amendment view.

Physical JSONL line order and canonical replay order must not be silently treated as equivalent.

---

## Acceptance Tests

### Order

Given the same ledger state, repeated replay produces the same canonical record sequence.

### Identity

Every replayed record resolves to exactly one committed `record_id`.

### Integrity

Mutation or corruption of committed content can be detected.

### Provenance

Every replayed record retains the admitted envelope necessary to trace it toward its captured source observation.

### Missingness

Missing source information survives commit and replay as missing.

### Amendment

Corrections do not erase prior committed records.

---

## Evidence

Synthetic v0 evidence:

* `src/ledger/jsonl.py`
* `tests/replay/test_ledger_harness.py`
* `traces/ledger_runtime_pressure_v0.json`
* `docs/decisions/ledger_runtime_pressure_v0.md`

Bounded live vertical-chain evidence:

* `traces/live_ingest_ledger_v0.jsonl`
* `traces/live_vertical_probe_v0.json`
* `tests/runtime/test_live_vertical_probe.py`
* `docs/decisions/live_ingest_ledger_extraction_v0.md`

This evidence does not validate live OS capture, distributed append, history-level integrity, or schema permanence.

---

## Schema-Ready Gate

This contract becomes ready for formal schema work when:

* the minimum record boundary is stable
* commit ordering semantics are unambiguous
* integrity requirements are sufficient for the first runtime
* amendment behavior is minimally defined
* replay requirements can be tested deterministically
* no field requires semantic inference to populate

Until then, field names and storage format remain provisional.

---

## Current Implementation Hypothesis

The smallest useful implementation may be an append-only JSONL ledger.

Each line contains one complete ledger record.

This is only an implementation hypothesis.

The contract does not require JSONL if another representation better satisfies the same guarantees.

---

## Next Pressure

After this contract stabilizes:

1. define the reconstruction contract
2. derive the minimum machine schema required for ledger records
3. implement a tiny append/replay harness against synthetic envelopes
4. test deterministic replay before connecting live OS capture
