# Ledger Schema Pressure v0

## Status

Shadow schema comparison completed.

No schema enforcement, live capture, ingest admission engine, provenance runtime, reconstruction, projection engine, database, service, graph system, semantic interpretation, or ledger-wide schema framework was introduced.

## Schema Hypothesis

The smallest justified machine-readable schema is JSON Schema for one tested v0 ledger record:

```text
schemas/ledger_record_v0.schema.json
```

The schema is descriptive and shadow-only. It is a comparison surface, not an admission gate.

## What The Schema Constrains

- record is an object
- required fields: `record_id`, `commit_index`, `envelope`, `integrity`
- no additional record-level fields
- `record_id` is a non-empty string
- `commit_index` is an integer with minimum `1`
- `envelope` is a JSON object
- `integrity.algorithm` is currently `sha256`
- `integrity.boundary` matches the current tested hash boundary text
- `integrity.digest` is a 64-character lowercase hexadecimal string
- no additional integrity fields

## What The Schema Leaves Open

- signal fields inside `envelope`
- provenance fields inside `envelope`
- ingest admission rules
- envelope identity uniqueness
- source sequence semantics
- event time encoding
- arrival time encoding
- amendment relation vocabulary
- cross-record ledger invariants
- truth, causality, intent, consequence, or semantic meaning

## Runtime Conformance

The current synthetic runtime records conformed to the schema.

- records tested: 11
- conforming: 11
- nonconforming: 0
- evidence: `traces/ledger_schema_pressure_v0.json`

This strengthens the claim that current `JsonlLedger.append()` output inhabits the schema region for the existing synthetic fixtures.

It does not prove that all runtime-possible records are schema-valid.

## Schema / Runtime Mismatches

### Runtime-Possible But Schema-Rejected

- `array_envelope`: runtime can append, hash, replay, and verify a non-object envelope; schema rejects it because `envelope` must be an object.
- `nan_envelope_value`: runtime can append, hash, replay, and verify a Python `NaN` value; schema rejects it because non-finite numbers are outside valid JSON.

Current stronger evidence: runtime behavior exists, but contract text says the ledger receives an admitted ingest envelope. The schema appears correct to keep `envelope` object-shaped while preserving this mismatch as ingest/admission pressure.

### Schema-Allowed But Runtime-Problematic

- `schema_valid_bad_digest`: schema accepts the record shape, but integrity verification fails.

This is not a serialization or replay failure. It is evidence that structural validity and integrity validity are separate checks.

## JSON-Domain Pressure

Accepted inside an object envelope:

- strings
- integers
- finite floats
- booleans
- null
- arrays
- nested objects
- empty strings
- empty arrays
- empty objects

Rejected by shadow validation:

- `NaN`
- `Infinity`
- negative `Infinity`
- non-string object keys

Python `json.dumps()` can emit non-standard `NaN` and infinity by default. That is runtime pressure, not a reason to expand the schema beyond valid JSON.

## Missingness Pressure

The existing missingness fixtures are schema-valid:

- `absent`
- `explicit_null`
- `unavailable`
- `malformed`

The schema sees these only as structure preserved inside the opaque `envelope` object. Their distinction currently depends on envelope convention and tests, not on ledger-record schema semantics.

Likely pressure points upstream:

- which malformed structures should be preserved versus rejected
- which missingness states originate from source, capture, or ingest
- what provenance is required before ledger admission

## Structural Validity vs Integrity Validity

A mutated record can remain schema-valid while failing integrity verification.

Therefore:

```text
schema_validity != integrity_validity
```

Schema validation asks whether a record inhabits the described structural region. Integrity verification asks whether committed content still matches the recorded hash boundary.

## Outside Per-Record Schema Scope

The following ledger guarantees are not represented by the record schema:

- unique `record_id`
- monotonic `commit_index`
- append-only history
- deterministic replay order
- amendment relationship behavior
- history integrity

This may justify a future ledger-level validator, but this pass does not implement one.

## Assumptions Strengthened

- Current synthetic runtime records conform to the minimal record schema.
- Keeping `envelope` object-shaped is enough to avoid upstream semantic over-specification.
- JSON Schema is adequate for the tested per-record boundary.
- Shadow validation can expose pressure without regulating append.

## Assumptions Weakened

- Runtime-produced does not imply schema-valid.
- Schema-valid does not imply integrity-valid.
- Per-record schema cannot carry ledger-wide guarantees.
- Python JSON behavior is wider than strict JSON structure.

## Contract Amendment Recommendation

No ledger contract amendment is required yet.

The mismatch evidence points toward ingest/provenance admission pressure, not a need to rewrite the ledger contract immediately.

## Runtime Amendment Recommendation

Do not amend `JsonlLedger.append()` yet.

The current mismatch is useful evidence that append accepts a wider Python value space than the schema describes. Enforcement should wait until admission rules are tested.

## Enforcement Recommendation

The schema is not ready for enforcement.

Keep validation shadow-only until the project has pressure on:

- ingest admission behavior
- provenance requirements before admission
- malformed source preservation versus rejection
- JSON-domain limits at the runtime boundary

## Next Pressure Frontier

The next pressure frontier appears to be ingest/provenance admission:

```text
What may enter the ledger as an admitted envelope, and which malformed or non-JSON structures should remain preserved evidence versus rejected input?
```

Live capture remains deferred, but source-shape uncertainty is now visible as pressure.

