# LLM_EXTERNAL_IO_OBSERVATION_MODULE_v0

```text
OBJECT_TYPE:
CANDIDATE_PROJECT_MODULE

OBJECT_ID:
LLM_EXTERNAL_IO_OBSERVATION_MODULE_v0

SHORT_NAME:
LLM_IO_OBSERVER_v0

STATUS:
PROVISIONAL
REVIEW_REQUIRED
PRESSURE_REQUIRED
NON-CANONICAL

TARGET_SYSTEMS:
CHATGPT_STYLE_LLM_TURNS
CODEX_RUNS
LM_STUDIO_LOCAL_MODELS

PRIMARY_MODE:
EXTERNAL_INPUT_OUTPUT_OBSERVATION

HIDDEN_ACTIVATION_ACCESS:
NOT_REQUIRED

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCHEMA_FREEZE:
NO

IMPLEMENTATION:
NONE
```

## 0. Purpose

Define a bounded observation module that can be aimed at an LLM invocation and
capture enough externally observable information to reconstruct a useful local
Atlas transition without requiring access to hidden transformer activations.

The intended scientific primitive is:

```text
FRAME_A
→
LLM INVOCATION / TOOL-INTERACTION EVENT
→
FRAME_B
```

The module exists to support later pressure on:

```text
semantic coherence
cursor quality
seat behavior
projection drift
context-path dependence
tool-mediated inference
snapshot sparsity
cross-model comparison
developmental provenance
```

It is NOT a claim that external I/O fully explains model internals.

## 1. Core distinction

Freeze:

```text
EXTERNALLY OBSERVED TRAJECTORY
!=
HIDDEN INTERNAL TRAJECTORY
```

and:

```text
INPUT / OUTPUT EQUIVALENCE
!=
INTERNAL PROCESS EQUIVALENCE
```

The project begins by asking whether external observation is sufficient for the
specific relational questions under pressure.

Internal instrumentation may be added later for local/open models when a
higher-resolution question actually requires it.

## 2. Primary observation object

Candidate invocation observation:

```text
LLM_INVOCATION_OBSERVATION_v0

RUN_ID

SYSTEM_ADAPTER
MODEL_ID / MODEL_LABEL
MODEL_CONFIGURATION where exposed

SEAT_ID? where explicitly defined
CURSOR_ID? where explicitly defined

FRAME_A_REF
RAW_INPUT_REF

TOOL_TRACE[]

START_TIME? where reliably measured
END_TIME? where reliably measured
ELAPSED_TIME? where reliably measured

INPUT_TOKENS? where exposed
OUTPUT_TOKENS? where exposed
TOTAL_TOKENS? where exposed

STOP_REASON? where exposed

RAW_OUTPUT_REF
FRAME_B_REF

MEASURED_FIELDS
DERIVED_FIELDS
INTERPRETED_FIELDS
UNRESOLVED_FIELDS

SOURCE_REFS
```

Question marks indicate optional availability, not required fields.

Missing telemetry MUST remain unavailable / unresolved.

Do not estimate or fabricate unavailable runtime metadata.

## 3. A / B frame contract

### FRAME_A

FRAME_A should represent the bounded externally available input-side relation,
not an invented complete model state.

Candidate observations may include:

```text
user / task input
visible conversation context
retrieved context actually supplied
files / evidence supplied
tool results already available
explicit system / developer constraints where adapter access lawfully exposes them
current seat / role / warrant where explicitly represented
current object / basis / unresolved coordinates
```

### FRAME_B

FRAME_B should represent the externally observable post-invocation relation.

Candidate observations may include:

```text
emitted response
tool requests
external mutations / artifacts where separately evidenced
new distinctions
preserved distinctions
dropped distinctions
changed relations
basis shifts
projection shifts
standing claims
new unresolved coordinates
next-action posture
```

Freeze:

```text
RAW TEXT
!=
ATLAS FRAME

ATLAS FRAME
=
DERIVED LOCAL PROJECTION
OVER SOURCE-BACKED EXTERNAL OBSERVATION
```

Raw text should remain available by reference for provenance where practical.

## 4. Tool-mediated trajectory

Where tools are used, the module MAY represent a denser externally observed
trajectory:

```text
FRAME_A
↓
MODEL STEP
↓
TOOL REQUEST
↓
TOOL RESULT
↓
MODEL STEP
↓
...
↓
FRAME_B
```

Each externally visible tool boundary may become an optional sub-observation.

Freeze:

```text
TOOL REQUEST
!=
TOOL EFFECT

TOOL RESULT
!=
MODEL INTERPRETATION OF TOOL RESULT

MODEL INVOCATION ENDED
!=
DOWNSTREAM EFFECT ENDED
```

## 5. Measurement layers

Every captured field MUST be classified as one of:

```text
MEASURED
DERIVED
INTERPRETED
UNRESOLVED
```

### MEASURED

Directly supplied by the runtime / adapter / external clock / tool system.

Examples:

```text
raw input
raw output
model label
tool call sequence
tool result payload refs
wall-clock timestamps
elapsed time
token counts
stop reason
```

only when actually exposed.

### DERIVED

Computed from source-backed observations.

Examples:

```text
FRAME_A
FRAME_B
changed relations
preserved distinctions
introduced distinctions
dropped distinctions
projection change
lineage links
trajectory segment
```

### INTERPRETED

Claims requiring qualification beyond mechanical extraction.

Examples:

```text
semantic coherence
cursor quality
seat stability
context interference
observational momentum
recovery confidence
```

### UNRESOLVED

Anything not established by the available evidence.

Freeze:

```text
MEASURED
!=
DERIVED
!=
INTERPRETED
!=
UNRESOLVED
```

## 6. Time / length / distance discipline

Record independently where available:

```text
WALL_TIME
INPUT_TOKEN_COUNT
OUTPUT_TOKEN_COUNT
TOTAL_TOKEN_COUNT
OBSERVED_EVENT_COUNT
TOOL_CALL_COUNT
RAW_OUTPUT_LENGTH
```

Do NOT treat any one of these as semantic trajectory length.

Freeze:

```text
WALL TIME
!=
TOKEN PATH LENGTH
!=
OBSERVED EVENT COUNT
!=
SEMANTIC DISTANCE
```

A semantic-distance or trajectory-length metric must be earned separately.

## 7. Adapter model

The module should use provider/runtime adapters rather than pretending every
system exposes the same telemetry.

Candidate adapters:

```text
CHATGPT_ADAPTER
CODEX_ADAPTER
LM_STUDIO_ADAPTER
```

Each adapter MUST declare:

```text
what it can observe
what it cannot observe
what it can timestamp
what token accounting it receives
what tool boundaries it can observe
what raw context is available
what model/config identity is available
what data is unavailable
```

Freeze:

```text
COMMON OBSERVATION CONTRACT
!=
IDENTICAL PROVIDER TELEMETRY
```

## 8. ChatGPT-style target

Initial ChatGPT-style use case:

```text
one visible conversation pass
=
FRAME_A
→ model / tool events
→ FRAME_B
```

Potential source surfaces:

```text
current user message
visible supplied conversation basis
tool calls made during the turn
tool results returned
final emitted response
runtime metadata actually exposed
```

Do NOT claim access to hidden activations or private internal reasoning.

The adapter should preserve a provenance link to the raw conversational objects
that support each derived frame.

## 9. Codex target

Codex observations may additionally expose useful software-development events:

```text
repository / branch / head basis
files inspected
commands / tests executed
tool calls
files changed
diff / commit result
test result
returned strategy / implementation object
```

The module must distinguish:

```text
MODEL OUTPUT CLAIM
!=
REPOSITORY EFFECT
```

Repository effects require independent tool / Git evidence.

## 10. LM Studio / local-model target

LM Studio or other local-model adapters may provide richer direct telemetry,
depending on the serving interface.

Initial target remains external:

```text
request payload
response payload
model/config identity
sampling configuration
token accounting where available
timing where available
tool / structured-output events where available
```

Future optional instrumentation MAY add:

```text
logits
token probabilities
layer checkpoints
attention summaries
activation traces
feature / circuit observations
```

but these are explicitly outside the minimum module.

Freeze:

```text
INTERNAL OBSERVABILITY
=
OPTIONAL RESOLUTION INCREASE

NOT:
BASE REQUIREMENT
```

## 11. Atlas relation

The module should emit or support a derived DRACI local-frame projection rather
than create an independent semantic ontology.

Candidate composition:

```text
RAW INVOCATION OBSERVATION
+
PROJECTION QUESTION
+
BASIS
↓
DRACI LOCAL FRAME_A
+
DRACI EVENT / TRANSITION VIEW
+
DRACI LOCAL FRAME_B
```

The projection question matters.

Different valid questions may yield different S/O/F role assignments over the
same source observation.

Freeze:

```text
PROJECTION CHANGE
!=
SOURCE EVENT CHANGE
```

## 12. Developmental-history use

A conversation / coding / research process may compile as:

```text
FRAME_0
→ EVENT_1
→ FRAME_1
→ EVENT_2
→ FRAME_2
→ ...
```

with raw source references retained.

This may support:

```text
developmental history
semantic lineage
decision provenance
cursor reconstruction
seat handoff
cross-model comparison
pressure replay
global-view rendering
```

Any global view remains derived from qualified local observations.

## 13. Candidate cursor / seat pressures

The module should eventually support controlled comparison of:

```text
same FRAME_A
+
different model

same FRAME_A
+
different cursor

same FRAME_A
+
different seat

same semantic content
+
different context ordering / prior trajectory

same cursor
+
different projection question
```

Observe differences in FRAME_B without assuming the cause in advance.

Candidate hypotheses to pressure:

```text
CONTENT EQUIVALENCE
MAY NOT IMPLY
TRAJECTORY EQUIVALENCE

SEMANTIC COHERENCE
MAY DEPEND ON
MORE THAN RAW CONTEXT CONTENT

CURSOR QUALITY
MAY BE TESTABLE AS
RECONSTRUCTABLE RELATIONAL CONTINUITY
```

These are hypotheses, not installed laws.

## 14. Privacy / security / capture ceiling

The module MUST NOT treat maximum capture as the objective.

Capture only what is needed for the declared scientific question.

Potentially sensitive or high-volume source material should be referenced,
redacted, hashed, summarized, or omitted according to the local experiment's
requirements.

Freeze:

```text
OBSERVABILITY
!=
UNBOUNDED COLLECTION
```

and:

```text
MORE TELEMETRY
!=
BETTER SCIENCE
```

## 15. Primary attack surfaces

Reviewers should attack at least:

1. whether FRAME_A can be derived reproducibly from available external context;
2. whether FRAME_B extraction smuggles interpretation into measurement;
3. whether tool traces are sufficiently ordered and source-backed;
4. whether provider differences make the common contract dishonest;
5. whether token/time statistics are actually available and comparable;
6. whether raw-text provenance can survive compression;
7. whether two projections over one source event remain identity-safe;
8. whether context-path dependence can be tested without fabricating hidden state;
9. whether observation density creates storage burden or false precision;
10. whether Atlas-derived labels accidentally become authoritative over source behavior.

## 16. Initial pressure program

### Pressure A — same conversation turn, two projections

Use one external invocation observation.

Derive:

```text
task-centered projection
seat/cursor-centered projection
```

Pressure source-identity conservation.

### Pressure B — same semantic task, different context trajectory

Hold the final requested task as constant as practical.

Vary preceding context path.

Observe whether FRAME_B differs in conserved / dropped / introduced relations.

Do not infer internal mechanism from one trial.

### Pressure C — tool-mediated vs no-tool path

Use a task that can be completed with and without an external tool where
scientifically appropriate.

Compare:

```text
observed event density
semantic outcome
basis quality
unresolved coordinates
```

### Pressure D — cross-runtime

Run the same bounded task on:

```text
ChatGPT
Codex
LM Studio local model
```

Compare only fields supported by all three adapters.

Retain provider-specific fields separately.

## 17. Implementation candidates

Do not assume persistence yet.

Compare:

```text
A.
EPHEMERAL DERIVED OBSERVER

B.
APPEND-ONLY INVOCATION OBSERVATION LOG

C.
FULL TRAJECTORY STORE
```

Prefer the minimum representation justified by pressure.

A durable store is warranted only if replay, lineage, comparison, or
developmental-history use demonstrates a real need.

## 18. Success criterion

The module is useful if it can repeatedly produce a source-backed A/B transition
that:

```text
preserves raw provenance
separates measured from derived from interpreted
supports multiple valid projections
retains uncertainty honestly
allows cross-run comparison
improves reconstruction of model / cursor / seat behavior
without requiring hidden-state access
```

## 19. Failure criterion

The module requires repair if it:

```text
pretends unavailable telemetry exists
treats raw output as qualified semantics
confuses model claim with external effect
forces all providers into false telemetry symmetry
manufactures internal trajectory from endpoints
treats time or token count as semantic distance
creates authoritative Atlas state from observational convenience
stores huge volumes without a pressure-backed reason
```

## 20. Disposition

```text
DISPOSITION:
PROMISING CANDIDATE PROJECT MODULE

NEXT:
BOUNDED ADVERSARIAL REVIEW

THEN:
SPECIMEN PRESSURE

NOT YET:
IMPLEMENTATION
PERSISTENCE
SCHEMA FREEZE
INTERNAL-ACTIVATION INSTRUMENTATION
```

Primary review question:

```text
CAN THIS MODULE OBSERVE
AN LLM INVOCATION AS A LOCAL ATLAS TRANSITION
WITHOUT INVENTING INTERNAL STATE
OR LOSING THE EXTERNAL CAUSAL / SEMANTIC RELATIONS
WE ACTUALLY CARE ABOUT?
```
