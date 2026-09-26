# Atlas Load-Transfer E03 Decomposed-Load Result V0

OBJECT_TYPE:
BOUNDED_PRESSURE_RESULT

OBJECT_ID:
ATLAS_LOAD_TRANSFER_E03_DECOMPOSED_LOAD_RESULT_V0

BASIS:
ATLAS_LOAD_TRANSFER_ENVIRONMENTAL_COMPETENCE_RESULT_V0

PRESSURE_CELL:
E03_LOAD_QUESTION

REPOSITORY_HEAD:
47225a76a315ee8234757b23ce0b886341379534

RESULT:
PARTIAL_SURVIVAL

DEPENDENCE_STANDING:
CANDIDATE

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
LOCAL_MODEL_INFERENCE_ONLY

CONTROL_EFFECT:
NONE

## Frozen candidate

```text
SUBJECT:
bounded reconstructability of
DISTINCTION_PATH_IDENTITY_NE_CONTENT_IDENTITY_001

PROPOSED SUPPORT:
exact Git source handles retained in the canonical registry

PROPOSED TYPE:
PROVENANCE / TEMPORAL RECONSTRUCTION DEPENDENCE

CANONICAL DEPENDENCIES:
[]

MATCHED PRESSURE OBSERVATION:
removing exact source handles caused reconstruction failure
```

The matched observation does not promote the candidate into admitted
topology. The underlying repository state is not claimed to disappear when
its reconstruction support disappears.

## Seat A — format failure

```text
MODEL:
qwen/qwen3-coder-30b

INVOCATION_ID:
chatcmpl-odbuebadt2gu37zag2pw5

PROMPT_SHA256:
5a61cc0be8124198789dcc7b9cbedbc21cf7e8160b7b9b38b5cff2e0e3a7db2e

PROMPT_TOKENS:
147

COMPLETION_TOKENS:
43

FINISH_REASON:
stop
```

The seat returned six positional statuses without the required dimension
labels or bounded reasons:

```text
DIMENSION: LOST
DIMENSION: DEGRADED
DIMENSION: UNAFFECTED
DIMENSION: UNRESOLVED
DIMENSION: LOST
DIMENSION: UNAFFECTED
```

Disposition:

```text
E03_DECOMPOSITION:
FAILED_FORMAT

INTERPRETATION:
NONE
```

The positions are not silently mapped onto the requested dimensions.

## Seat B — bounded decomposition

```text
MODEL:
microsoft/phi-4

INVOCATION_ID:
chatcmpl-dv199v25a6wkifdlytw3nl

PROMPT_SHA256:
f83091fed748731e83a5575d5ca2e320c424c3a64c98dda0950b7fd3ab3fe559

PROMPT_TOKENS:
284

COMPLETION_TOKENS:
114

FINISH_REASON:
stop
```

Retained response:

```text
FUNCTIONAL: LOST - Exact source handles are necessary for reconstruction.

SEMANTIC: DEGRADED - The meaning may be partially inferred but lacks
precision without exact handles.

AUTHORITY: UNAFFECTED - Authority remains as it does not depend on specific
source handles.

PROVENANCE: LOST - Source handles provide critical provenance information
that is lost.

TEMPORAL: DEGRADED - Temporal context may be inferred but lacks accuracy
without exact handles.

COORDINATION: UNRESOLVED - Coordination impact cannot be determined from the
given data.
```

## Evaluator disposition

The alternate seat supplied all six required dimensions without a scalar
score and did not mint authority or admit the candidate.

The decomposition is retained as a pressure observation, not as an admitted
dependency relation:

| Load dimension | Seat-B observation | Evaluator ceiling |
|---|---|---|
| Functional | `LOST` | Loss is bounded to reconstructability; underlying repository function was not tested |
| Semantic | `DEGRADED` | Plausible candidate classification; semantic retention without exact handles was not independently pressured here |
| Authority | `UNAFFECTED` | Consistent with the frozen non-authority boundary |
| Provenance | `LOST` | Directly aligned with removal of exact source handles |
| Temporal | `DEGRADED` | Plausible candidate classification; exact currentness transport remains independently fractured |
| Coordination | `UNRESOLVED` | Preserves missing evidence rather than inventing a coordination consequence |

## Finding

```text
E03_SIX_DIMENSION_OUTPUT:
OBSERVED_ON_ONE_ALTERNATE_SEAT

CROSS_SEAT_CONSERVATION:
NO

DEPENDENCE_ADMISSION:
NONE

TOPOLOGY_MUTATION:
NONE
```

The environment carried enough structure for one alternate seat to produce
a bounded six-dimensional candidate decomposition. It did not carry enough
structure to make the response format invariant across the two tested seats,
or to establish the semantic and temporal classifications independently.

## Claim ceiling

This result establishes only that one tested alternate local-model seat could
decompose the proposed loss of exact Git reconstruction support into the six
requested load dimensions while preserving non-authority and unresolved
coordination.

It does not establish the proposed dependence, dependency topology,
cross-model invariance, loss of underlying repository state, semantic cause,
actor lineage, execution standing, or authority.

```text
CANDIDATE DECOMPOSITION
!=
ADMITTED DEPENDENCE

RECONSTRUCTION SUPPORT LOSS
!=
UNDERLYING STATE LOSS

NO NEW AUTHORITY
NO REPOSITORY EXECUTION
NO CONTROL EFFECT
```

STOP:
YES

The E03 continuation pressure is evidenced. No registry dependency, schema,
witness path, Cell 002 surface, or load topology is modified.
