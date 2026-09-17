# Bounded Read Consumer Experiment v0

**Status:** READY TO EXECUTE  
**Authority:** READ-ONLY EXPERIMENT ONLY  
**Starting basis:** Home Capture schema v7, bounded bridge stabilization complete, no heartbeat or external transport authorized.

## Purpose

Pressure the newly stabilized Home bridge as a semantic membrane rather than merely a JSON serializer.

The experiment asks:

> Can an independent read-only consumer reconstruct exactly the bounded state exposed by the bridge, preserve identity/standing/provenance/freshness, and refuse to infer facts that were not projected?

This experiment is intentionally narrower than model-memory testing. It establishes whether the bridge can carry a bounded semantic contract before Qwen or another model is asked to navigate from it.

---

## Authoritative live specimen

Recurring commitment:

`home:commitment:b1fd812d-7510-4712-83c5-355767e7f346`

Verified lineage:

```text
stable commitment_id
    ↓
INITIAL specification 5140c7af-… : THU / SAT
    ↓ prior_specification
RECORDING_CORRECTION 520752fb-… : WED / FRI
```

The live specimen must remain unchanged during this experiment.

Live state currently contains no scheduled events. Do not create one merely to satisfy the experiment.

---

## Bridge contract already established

Bridge projections expose at least the stabilized envelope fields appropriate to their surface:

```text
authority = DERIVED_FROM_HOME
generated_at
relevant_source_revision
source_instance_id
source surface/schema identity
semantic_freshness = CURRENT_AT_GENERATION_FOR_RELEVANT_SOURCE_REVISION
```

Event projections, when events exist, can expose typed references and derived applicability standing:

```text
commitment_id
specification_id
context_refs
raw_instruction
CURRENT
SPECIFICATION_SUPERSEDED
COMMITMENT_CLOSED
REFERENCE_UNRESOLVED
current commitment status/specification
applicability-adjudication requirement
due_grants_execution_authority = false
```

---

## Core law under pressure

```text
DERIVED PROJECTION != AUTHORITATIVE SOURCE
READABLE STATE != EXECUTION AUTHORITY
AVAILABLE REFERENCE != WARRANTED INFERENCE
```

The consumer must reconstruct only what the projection warrants.

---

## Experiment A — Live non-mutating read

Use the actual live v7 Home instance.

### Allowed

- Read current bridge projection(s).
- Read current Home source-instance/revision coordinates once for comparison.
- Read the authoritative recurring commitment/specification state for comparison.
- Produce an experiment report.

### Forbidden

- No database mutation.
- No scheduled event creation.
- No acknowledgement/cancellation.
- No heartbeat.
- No polling loop.
- No external transport.
- No agent invocation.
- No execution capability.
- No source rewriting to make the projection pass.

### Consumer questions

The consumer should answer, from the bridge only where the bridge actually exposes the required fields:

```text
1. What source instance produced this projection?
2. At what relevant source revision was it generated?
3. What authority does the projection claim?
4. What semantic freshness claim does it make?
5. Is any execution authority granted by being readable/due?
6. Which facts about the live recurring amendment lineage are actually projected?
7. Which lineage facts are NOT projected and therefore remain UNKNOWN to the consumer?
```

The last two questions are deliberately important.

If the bridge does not contain enough information to reconstruct `INITIAL -> RECORDING_CORRECTION`, the consumer must say so. It must not infer the lineage merely because the test harness knows it exists in Home.

### Live freshness check

At one bounded read moment:

```text
bridge.source_instance_id == Home.source_instance_id
bridge.relevant_source_revision == Home.current_relevant_source_revision
```

If equal, the legitimate statement is only:

> projection corresponds to the current relevant source revision at the moment checked.

Do not generalize this into detached future freshness.

---

## Experiment B — Isolated event-standing fixture

Because the live database contains zero scheduled events, event applicability should be pressured in an isolated temporary fixture/database rather than by mutating live state.

### Fixture sequence

1. Create a recurring commitment with specification `INITIAL`.
2. Create a scheduled event through the ordinary event route so it mechanically attaches:
   - `commitment_id`
   - then-current `specification_id`
   - immutable `raw_instruction`
3. Generate/read the bridge projection.
4. Verify consumer reconstructs event standing as `CURRENT`.
5. Append a `RECORDING_CORRECTION` specification to the same commitment identity.
6. Do not rewrite the event.
7. Generate/read the bridge again.
8. Verify the consumer reconstructs:
   - original event `specification_id` retained,
   - current commitment specification changed,
   - applicability standing = `SPECIFICATION_SUPERSEDED`,
   - raw instruction unchanged,
   - explicit adjudication still required,
   - no execution authority granted.
9. Close the commitment in the isolated fixture.
10. Verify standing becomes `COMMITMENT_CLOSED` without rewriting/cancelling/executing the event.

Optional fourth state:

- break/remove the referenced object in the isolated fixture through a controlled test-only condition and verify `REFERENCE_UNRESOLVED` rather than fabricated reconstruction.

---

## Consumer implementation constraint

The consumer should be boring.

It may be a small experiment/test module that:

```text
reads projection
validates envelope
extracts projected facts
records UNKNOWN for absent facts
compares bounded reconstructed facts with authoritative fixture state
emits machine-readable result
```

Do not build a general agent, ontology, graph engine, or retrieval service.

---

## Required output record

Candidate:

```json
{
  "experiment": "bounded_read_consumer_v0",
  "source_instance_match": true,
  "source_revision_match_at_read": true,
  "projection_authority": "DERIVED_FROM_HOME",
  "execution_authority_inferred": false,
  "reconstructed": {},
  "unknown_not_projected": [],
  "incorrect_inferences": [],
  "fixture_event_standing_sequence": [
    "CURRENT",
    "SPECIFICATION_SUPERSEDED",
    "COMMITMENT_CLOSED"
  ],
  "semantic_pass": true,
  "notes": []
}
```

Use actual field names supported by the runtime. Do not change production schema merely to match this example.

---

## Pass conditions

The experiment passes only if:

1. projection source-instance/revision coordinates are reconstructable;
2. `DERIVED_FROM_HOME` remains distinct from authoritative Home state;
3. consumer does not infer execution authority;
4. projected identity/standing/provenance survive read consumption;
5. absent/non-projected facts remain explicitly unknown rather than guessed;
6. isolated event standing changes through `CURRENT -> SPECIFICATION_SUPERSEDED -> COMMITMENT_CLOSED` without event rewriting;
7. source and consumer agree on all facts that the projection claims to expose;
8. no live mutation is introduced.

---

## Fail conditions

Fail if any of the following occurs:

```text
bridge treated as source authority
absent lineage guessed by consumer
due/readability interpreted as execution authority
stale revision silently called current
event rewritten after specification amendment
event automatically cancelled/acknowledged/executed due to standing change
consumer requires hidden access to source state to appear correct
live database mutated for test convenience
```

---

## Result categories

### PASS — BOUNDED SEMANTIC READ SURVIVES

The bridge carries its declared bounded semantics to an independent consumer without hidden source dependence or invented state.

### PARTIAL — SERIALIZATION WORKS, SEMANTIC CONTRACT INCOMPLETE

Fields survive mechanically, but the consumer cannot reconstruct some claimed semantics or cannot distinguish unknown from false/current.

### FAIL — PROJECTION CREATES FALSE NAVIGATIONAL STANDING

The consumer is led to infer state, authority, freshness, or applicability that the source does not warrant.

---

## Codex warrant

Treat schema-v7 Home and the verified real recurring amendment specimen as the authoritative starting basis.

Implement the smallest read-only consumer experiment described here.

Use the live instance only for non-mutating source/projection comparison. Because the live database has zero scheduled events, exercise event applicability in an isolated temporary fixture/database rather than creating synthetic live state.

The consumer must reconstruct only what the bridge actually exposes and explicitly preserve UNKNOWN for facts that are not projected. In particular, do not let test knowledge of the real `INITIAL -> RECORDING_CORRECTION` lineage leak into the consumer unless that lineage is actually available on the consumed surface.

Do not add heartbeat behavior, polling, external transport, routing, execution, model invocation, generalized retrieval, or new authority.

Return:

1. files changed,
2. exact consumer input surface,
3. facts successfully reconstructed,
4. facts correctly left UNKNOWN,
5. isolated event-standing sequence observed,
6. tests/run commands and results,
7. any hidden dependency the consumer required,
8. verdict: `PASS_BOUNDED_SEMANTIC_READ`, `PARTIAL_CONTRACT`, or `FAIL_FALSE_STANDING`.

Do not commit or push unless separately instructed.
