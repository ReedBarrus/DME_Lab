# CODEX_INVOCATION_WITNESS_IMPLEMENTATION_001

```text
OBJECT_TYPE:
BOUNDED_IMPLEMENTATION_WARRANT

OBJECT_ID:
CODEX_INVOCATION_WITNESS_IMPLEMENTATION_001

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

IMPLEMENTATION_FRONT:
2

TARGET:
LLM_IO_OBSERVER_v0

ROLE:
RAW INVOCATION WITNESS

NOT:
ATLAS INTERPRETER
SEMANTIC CONTINUITY EVALUATOR
GENERIC MODEL WRAPPER

PERSISTENCE:
NONE UNLESS REQUIRED BY THE BOUNDED TEST FIXTURE

SCHEMA_FREEZE:
NO
```

## 0. Mission

Implement the smallest source-backed invocation witness capable of representing
one bounded LLM invocation as externally observable evidence.

Target future adapters:

```text
ChatGPT-style turn
Codex run
LM Studio local model
```

This warrant does NOT require all three adapters now.

First implementation should use one deterministic synthetic or repository-local
specimen and prove the witness boundary.

## 1. Required epistemic cut

Freeze:

```text
RAW INVOCATION WITNESS
!=
ATLAS PROJECTION
!=
SEMANTIC INTERPRETATION
```

The witness records available source facts.

It does not decide continuity.

## 2. Minimum candidate capture

Use only fields actually supported by the specimen:

```text
invocation_id

input_identity / raw_input_ref

model_identity? where supplied
adapter_identity

declared_basis_refs

tool_trace_refs[]

raw_output_identity / raw_output_ref

start_frame_ref?
end_frame_ref?

external_crossing_refs[]

observer_limitations

measured_fields
unresolved_fields
```

Question-marked fields are optional.

Do not fabricate unavailable metadata.

## 3. Tool trace discipline

Where tools are present preserve ordering and distinguish:

```text
TOOL_REQUEST
!=
TOOL_RESULT
!=
MODEL CLAIM ABOUT TOOL RESULT
!=
EXTERNAL EFFECT
```

Do not require tools for the first specimen if a no-tool specimen is simpler.

## 4. Metadata discipline

Keep separate:

```text
MEASURED
DERIVED
INTERPRETED
UNRESOLVED
```

For this implementation, prefer MEASURED + UNRESOLVED only.

Any derived convenience must be clearly marked and mechanically reproducible.

No semantic-coherence score.
No semantic-distance metric.

## 5. Mutation / environment ceiling

The witness implementation must be:

```text
deterministic where inputs are fixed
clock-independent unless explicit timestamps are injected
network-free in tests
Git-lookup-free during witness construction
append-free
external-effect-free
```

## 6. Suggested bounded file surface

Prefer a new isolated module such as:

```text
src/observation/llm_invocation_witness_v0.py
tests/observation/test_llm_invocation_witness_v0.py
```

Do not modify DRACI projector mechanisms unless an unavoidable fracture is
returned instead of repaired.

## 7. First tests

At minimum pressure:

1. identical explicit source input yields deterministic witness;
2. raw input identity is preserved;
3. raw output identity is preserved;
4. adapter identity is explicit;
5. unavailable model metadata remains unresolved;
6. tool request and tool result remain distinct where supplied;
7. external effect is not inferred from tool/model claim;
8. observer limitations are retained;
9. no Atlas standing is emitted;
10. witness construction performs no I/O or mutation.

## 8. Required return

```text
OBJECT_TYPE:
INVOCATION_WITNESS_IMPLEMENTATION_RESULT

WORKTREE_BASE:

FILES_CHANGED:

TEST_RESULT:

SPECIMEN:

WITNESS_SHAPE:

MEASURED_FIELDS:

UNRESOLVED_FIELDS:

DISTINCTIONS_PRESERVED:

FRACTURES_EXPOSED:

NEW_REPRESENTATION_DEBT:

MUTATION_CHECK:

ATLAS_INTERPRETATION:
NONE

PERSISTENCE:
NONE

SCHEMA_FREEZE:
NO

NEXT_PRESSURE:
real adapter specimen selection
```

## 9. Stop membrane

If the implementation requires a generic provider abstraction, persistence
platform, semantic evaluator, or Atlas ontology:

```text
STOP
RETURN FRACTURE
DO NOT REPAIR BY ARCHITECTURE
```
