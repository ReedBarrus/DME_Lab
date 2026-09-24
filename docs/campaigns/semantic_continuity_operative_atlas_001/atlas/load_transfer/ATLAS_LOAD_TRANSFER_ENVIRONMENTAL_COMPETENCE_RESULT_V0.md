# Atlas Load-Transfer / Environmentally-Supplied-Competence Result V0

OBJECT_TYPE:
BOUNDED_PRESSURE_RESULT

OBJECT_ID:
ATLAS_LOAD_TRANSFER_ENVIRONMENTAL_COMPETENCE_RESULT_V0

PRESSURE:
ATLAS_LOAD_TRANSFER_ENVIRONMENTAL_COMPETENCE_V0

SUBJECT:
DISTINCTION_PATH_IDENTITY_NE_CONTENT_IDENTITY_001

REPOSITORY_HEAD:
47225a76a315ee8234757b23ce0b886341379534

RESULT:
PARTIAL_SURVIVAL

AUTHORITY_EFFECT:
NONE

REPOSITORY_EXECUTION_EFFECT:
NONE

EXTERNAL_EFFECT:
LOCAL_MODEL_INFERENCE_ONLY

## 1. Frozen evidence basis

The pressure used only:

- `QWEN_ATLAS_CELL001_INDEPENDENT_PRESSURE_V0`;
- the canonical Cell 001 registry record;
- the current derived reconstruction packet;
- the exact source handles carried by those artifacts.

No original design conversation, repository-wide inference, corrective
follow-up, or operator explanation was admitted into either baseline seat.

Coordinates:

```text
REGISTRY_SHA256:
0d5e33efbcae1694557bf899ef716b75840ca38e31fc13fe0140018b53462600

DERIVED_PROJECTION_SHA256:
d737b151b8566dc645d2f5a42b5d8eebe2891c168d5cc7a87b288bc15d321177

BASELINE_INPUT_ENVELOPE_SHA256:
25162f602f0f702c364faa8771f784f1ca676890a41f6e1762c71a86b495eed0

ABLATION_INPUT_ENVELOPE_SHA256:
91fc8603c5de18d71c7e1fa75a2428a03ce346915b7ac38833dd15098e8ecb67

ADVERSARIAL_INPUT_ENVELOPE_SHA256:
ecf2775b39dc96385c962f77e4210cdc31ad13f7df6b901e7f35e29acecf94b1
```

The first malformed HTTP body was rejected before model invocation. It created
no semantic specimen and is not counted as a seat run.

## 2. Independent baseline seats

### Seat A — Qwen

```text
MODEL:
qwen/qwen3-coder-30b

INVOCATION_ID:
chatcmpl-axnq96bum5fj0rqczj4fq

PROMPT_TOKENS:
3315

COMPLETION_TOKENS:
925

FINISH_REASON:
stop

OPERATOR_CLARIFICATIONS:
0
```

Observed output retained:

- exact distinction;
- exact subject path and repository;
- both full commit identities;
- bounded standing;
- claim ceiling;
- all three unresolved boundaries;
- non-authority and non-execution posture;
- one explicitly `CANDIDATE` dependence proposal.

Observed loss:

- blob identities were abbreviated rather than retained exactly;
- `HISTORICAL_SPECIMEN` was not returned as a separate currentness relation;
- `NO_LOCAL_RECEIPT != NO_FAILURE` was not positively reconstructed.

### Seat B — Phi-4

```text
MODEL:
microsoft/phi-4

INVOCATION_ID:
chatcmpl-3agrtsas08vwa3p9o9d24q

PROMPT_TOKENS:
2772

COMPLETION_TOKENS:
866

FINISH_REASON:
stop

OPERATOR_CLARIFICATIONS:
0
```

Observed output retained:

- exact distinction;
- exact subject path and repository;
- both full commit pairs;
- all three full blob identities;
- bounded standing;
- claim ceiling;
- all three unresolved boundaries;
- non-authority and non-execution posture;
- one explicitly `CANDIDATE` dependence proposal.

Observed loss:

- `HISTORICAL_SPECIMEN` was not returned as a separate currentness relation;
- `NO_LOCAL_RECEIPT != NO_FAILURE` was interpreted incorrectly as absence of a
  failure claim rather than a prohibition on inferring no failure.

## 3. Strict seat metrics

| Metric | Qwen | Phi-4 |
|---|---|---|
| `RECONSTRUCTION_SUCCESS` | `PARTIAL` | `PARTIAL` |
| `OPERATOR_INTERVENTIONS` | `0` | `0` |
| `DISTINCTION_RETENTION` | `YES` | `YES` |
| `PROVENANCE_RETENTION` | `NO` — abbreviated blobs | `YES` |
| `CLAIM_CEILING_RETENTION` | `YES` | `YES` |
| `CURRENTNESS_RETENTION` | `NO` | `NO` |
| `UNRESOLVED_RETENTION` | `YES` | `YES` |
| `AUTHORITY_NON_MINTING` | `PASS` | `PASS` |
| `CANDIDATE_DEPENDENCE_DISCIPLINE` | `PASS` | `PASS` |
| `CROSS_SEAT_VARIANCE` | `MEDIUM` | `MEDIUM` |

`PROVENANCE_RETENTION` is strict: recognition of a source relation with
truncated identities does not equal exact-source retention.

## 4. Context-removal results

| Cell | Observed result | Disposition |
|---|---|---|
| A01 full packet / no conversation | Both seats recovered the bounded core in one turn and zero clarifications | `PARTIAL_SURVIVAL` because currentness did not travel and Qwen compressed blobs |
| A02 remove provenance | Qwen returned reconstruction `NO` and fabricated no support, but retained `ADMITTED_BOUNDED` instead of degrading standing | `FAIL_STANDING_DEGRADATION` |
| A03 remove claim ceiling | Qwen returned `PARTIAL` without scope expansion, but retained `ADMITTED_BOUNDED` | `FAIL_ADMISSIBILITY_DEGRADATION` |
| A04 remove currentness | The reconstruction packet contains `current_standing` but no separate `currentness` field | `PACKET_SCHEMA_FRACTURE` |
| A05 remove unresolveds | Core relation survived as `PARTIAL`; unresolved output became empty | `PARTIAL_UNCERTAINTY_LOSS` |

The A04 discovery is not repaired here. The canonical registry retains
`HISTORICAL_SPECIMEN`, but the reconstruction packet does not independently
carry that relation.

## 5. Load-transfer verification

| Cell | Result |
|---|---|
| B01 human explanation absent | `PASS` — zero clarifications for both seats |
| B02 model variance | `MEDIUM` — shared core posture, differing exact provenance retention |
| B03 packet compression | Removing source handles caused complete reconstruction failure; claim-ceiling and unresolved removal caused partial drift; currentness is already absent as a separate packet field |
| B04 projection-only failure | `PASS` — visual label plus selected subject was not treated as admitted evidence |
| B05 registry-only reconstruction | `PASS_CORE / PARTIAL_STANDING` — core relation survived without visualization; standing remained the canonical `CANDIDATE_FOR_BOUNDED_ADMISSION` rather than derived admission |

Visualization was not load-bearing for core reconstruction.

The source-bound registry and exact handles were load-bearing.

## 6. Environmental burden

```text
C01_RECONSTRUCTION_LATENCY:
one invocation turn per baseline seat;
zero clarification turns;
wall-clock latency not independently instrumented

C02_COORDINATION_LOAD:
zero operator interventions inside either semantic specimen

C03_SEMANTIC_LOAD:
the relation and claim boundary were environmentally supplied;
no prose reconstruction request was needed

C04_PROVENANCE_LOAD:
directly supplied;
retained exactly by Phi-4 and compressed by Qwen

C05_TEMPORAL_LOAD:
not conserved;
canonical currentness exists but did not survive the reconstruction outputs

C06_AUTHORITY_LOAD:
both seats preserved non-authority and non-execution standing
```

## 7. Failure-as-unexternalized-load pressure

One independent Qwen adversarial invocation evaluated all six mutations:

```text
INVOCATION_ID:
chatcmpl-6izudtd3dxcnejdnhlpym

MODEL:
qwen/qwen3-coder-30b

PROMPT_TOKENS:
1213

COMPLETION_TOKENS:
310

FINISH_REASON:
stop
```

| Cell | Seat decision | Resulting standing |
|---|---|---|
| D01 wrong subject | `REJECT` | `NOT_ADMITTED` |
| D02 scope expansion | `REJECT` | `NOT_ADMITTED` |
| D03 missing source support | `REJECT` | `UNRESOLVED` |
| D04 historical/current collapse | `REJECT` | `NOT_ADMITTED` |
| D05 authority minting | `REJECT` | `NOT_ADMITTED` |
| D06 unresolved erasure | `REJECT` | `UNRESOLVED` |

D01 included an unsupported statement that the replacement path was
non-existent. Rejection was correct, but wrong-subject rejection must depend on
address mismatch, not assumed non-existence.

## 8. Minimum dependence pressure

Both seats proposed a relation equivalent to:

```text
SUBJECT:
bounded reconstructability of Cell 001

SUPPORT:
exact Git source handles / retained temporal lineage

DEPENDENCE_TYPE:
PROVENANCE / TEMPORAL RECONSTRUCTION DEPENDENCE

CLASSIFICATION:
CANDIDATE
```

This remains `CANDIDATE`, not `SUPPORTED`, because the Cell 001 canonical
record has `dependencies: []` and no separately admitted dependence relation.

Removing source handles caused reconstruction failure, which is a matched
falsification pressure for the proposal. It does not by itself promote the
relation to admitted topology.

The six-dimensional E03 load decomposition was not returned by either baseline
seat and is not inferred here.

## 9. Witnessability and load redistribution

```text
F01_SELF_WITNESSABLE_FAILURE:
NOT_ESTABLISHED

F02_EXTERNAL_WITNESS_REQUIRED:
NOT_ESTABLISHED

F03_NO_LOCAL_RECEIPT:
FAILED_BY_BOTH_BASELINE_RECONSTRUCTIONS

F04_CORRECTOR_CO_FAILURE:
NOT_ESTABLISHED

G01_BEFORE_AFTER_SUPPORT_TOPOLOGY:
NOT_EXECUTED_NO_ADMITTED_FIXTURE

G02_REDUNDANCY_COLLAPSE:
NOT_EXECUTED_NO_ADMITTED_FIXTURE

G03_LOAD_DISPERSION:
NOT_EXECUTED_NO_ADMITTED_FIXTURE
```

No witness or load-topology fixture was invented merely to complete the table.

## 10. Finding

The pressure supports a bounded positive finding:

```text
SOME CORE RECONSTRUCTION LOAD
MOVED INTO
SOURCE-BOUND ENVIRONMENTAL STRUCTURE
```

Evidence:

- two distinct local model seats reconstructed the same bounded distinction;
- neither required Reed explanation or corrective interaction;
- both conserved subject, scope, standing, claim ceiling, unresolveds, and
  non-authority posture;
- projection-only evidence failed while registry/source evidence survived.

The pressure does not support complete environmentally supplied competence.

Remaining environmental load is localized to:

- exact provenance conservation across seats;
- explicit currentness transport in the reconstruction packet;
- standing degradation rules under ablation;
- witnessability discipline;
- six-dimensional load decomposition;
- admitted dependence and redistribution topology.

## Claim ceiling

This result establishes only that the current Cell 001 registry and source
handles can carry enough environmental structure for two tested local models
to recover the bounded core posture without operator explanation.

It does not establish general model competence, model capability increase,
complete load transfer, complete semantic reconstruction, safe autonomous
execution, general dependence inference, witness architecture, load topology,
or portability beyond the two tested model coordinates.

```text
ENVIRONMENTALLY SUPPLIED COMPETENCE
!=
MODEL CAPABILITY INCREASE

LOAD TRANSFER
!=
LOAD ELIMINATION

RECONSTRUCTION SUCCESS
!=
IDENTICAL PROSE

NO NEW AUTHORITY
NO REPOSITORY EXECUTION
NO CONTROL EFFECT
```

STOP:
YES

The two-seat reconstruction and failure attribution stop condition is met.
No repair, Cell 002 work, dependence admission, witness fixture, or load-
redistribution implementation is authorized by this result.

## Appendix — retained model response bodies

These response bodies are retained as produced. Evaluator interpretation
remains separate from model output.

### Qwen baseline

```text
1. RECONSTRUCTED DISTINCTION — SUPPORTED
The distinction is that the path identity and content identity of the file
src/cockpit/observer/repository_fabric_app.mjs are not equal across two
adjacent Git transitions, as evidenced by differing blob SHAs while the path
remains constant.

2. EXACT MECHANICAL SUPPORT — SUPPORTED
First transition: 32b22057af4e38b33d5fe69c2658466281f33e0b to
dd9da1053a9c4d698c417d7c5e6c4a55f613087d, with blob SHA change from
36f7d491... to 55ce3ccb....
Second transition: e3675ca361fdb19ea5b66c5e5071430cf9cacf5d to
2f3dd79d5d25c79f5ec69cae8767fef2f45e96bc, with blob SHA change from
55ce3ccb... to a1368628....

3. EXACT SUBJECT / SCOPE — SUPPORTED
Subject: src/cockpit/observer/repository_fabric_app.mjs.
Scope: exact adjacent Git transitions within ReedBarrus/DME_Lab, bounded to
the two specified commits and their respective tree and blob SHAs.

4. CURRENT STANDING — SUPPORTED
ADMITTED_BOUNDED.

5. CLAIM CEILING — SUPPORTED
Establishes only that the exact registered repository path persisted across
the admitted adjacent Git frames while its exact blob identities differed. It
does not establish path continuity outside this specimen, semantic causation,
actor attribution, dependence, authority, or executable standing.

6. EXPLICIT UNRESOLVED BOUNDARIES — SUPPORTED
ACTOR_LINEAGE; SEMANTIC_CAUSE; GENERALIZATION_BEYOND_EXACT_SPECIMEN.

7. FALSIFICATION ATTEMPT — CANDIDATE
Weakest support assumption: path identity and content identity are distinct in
the two transitions. Identical blob SHAs, path change, deletion, or move would
invalidate admission.

8. ONE MINIMUM DEPENDENCE PROPOSAL — CANDIDATE
The distinction relies on the integrity of Git history for its two source
handles. Without valid Git commit and blob SHAs there would be no evidence of
differing content at the same path.

9. NON-COLLAPSE CONFIRMATION — SUPPORTED
Mechanical Evidence != Symbolic Distinction.
Symbolic Distinction != Authority.
Registered Relation != Executable Relation.
State Exists != State Is Admitted.
No Local Receipt != No Failure: the distinction is not about failure, but
about the absence of equality between path and content identity.
```

### Phi-4 baseline

```text
1. RECONSTRUCTED DISTINCTION
The path identity of src/cockpit/observer/repository_fabric_app.mjs persisted
across two adjacent Git transitions, while its content identities differed.

2. EXACT MECHANICAL SUPPORT
32b22057af4e38b33d5fe69c2658466281f33e0b ->
dd9da1053a9c4d698c417d7c5e6c4a55f613087d:
36f7d4917c32692b5810173a3bee5ad731f46a9c ->
55ce3ccb04953c1c5543f3653179322fd524370c.

e3675ca361fdb19ea5b66c5e5071430cf9cacf5d ->
2f3dd79d5d25c79f5ec69cae8767fef2f45e96bc:
55ce3ccb04953c1c5543f3653179322fd524370c ->
a13686287296e9e191799c3a999676afb15f2d23.

3. EXACT SUBJECT / SCOPE
The file at src/cockpit/observer/repository_fabric_app.mjs in
ReedBarrus/DME_Lab; exact adjacent Git transitions for this specific path.

4. CURRENT STANDING
ADMITTED_BOUNDED.

5. CLAIM CEILING
The exact registered path persisted across the admitted adjacent frames while
its exact blobs differed. No continuity outside the specimen, semantic cause,
actor attribution, dependence, authority, or executable standing is
established.

6. EXPLICIT UNRESOLVED BOUNDARIES
ACTOR_LINEAGE; SEMANTIC_CAUSE; GENERALIZATION_BEYOND_EXACT_SPECIMEN.

7. FALSIFICATION ATTEMPT
Weakest support assumption: path identity persisted. A deletion or rename in
either adjacent frame would falsify the claim.

8. ONE MINIMUM DEPENDENCE PROPOSAL — CANDIDATE
Path identity persistence is supported by the adjacent Git frame changes; loss
of that support loses evidence for path persistence in these transitions.

9. NON-COLLAPSE CONFIRMATION
Mechanical Evidence != Symbolic Distinction.
Symbolic Distinction != Authority.
Registered Relation != Executable Relation.
State Exists != State Is Admitted.
No Local Receipt != No Failure: lack of local receipt does not equate to
failure; it merely indicates no additional information was received.
```

### Qwen ablation response

```text
A02_REMOVE_PROVENANCE | NO | ADMITTED_BOUNDED | SUPPORTED NO |
FABRICATED_SUPPORT NO | CURRENTNESS_INFERRED YES | SCOPE_EXPANDED NO |
AUTHORITY_MINTED NO

A03_REMOVE_CLAIM_CEILING | PARTIAL | ADMITTED_BOUNDED | SUPPORTED YES |
FABRICATED_SUPPORT NO | CURRENTNESS_INFERRED YES | SCOPE_EXPANDED NO |
AUTHORITY_MINTED NO

A04_REMOVE_CURRENTNESS | PARTIAL | ADMITTED_BOUNDED | SUPPORTED YES |
FABRICATED_SUPPORT NO | CURRENTNESS_INFERRED NO | SCOPE_EXPANDED NO |
AUTHORITY_MINTED NO

A05_REMOVE_UNRESOLVEDS | PARTIAL | ADMITTED_BOUNDED | SUPPORTED YES |
UNRESOLVED EMPTY | FABRICATED_SUPPORT NO | CURRENTNESS_INFERRED YES |
SCOPE_EXPANDED NO | AUTHORITY_MINTED NO

B04_PROJECTION_ONLY | NO | STANDING EMPTY | SUPPORTED EMPTY |
FABRICATED_SUPPORT NO | CURRENTNESS_INFERRED NO | SCOPE_EXPANDED NO |
AUTHORITY_MINTED NO

B05_REGISTRY_ONLY | YES | CANDIDATE_FOR_BOUNDED_ADMISSION | SUPPORTED YES |
UNRESOLVED ACTOR_LINEAGE, SEMANTIC_CAUSE,
GENERALIZATION_BEYOND_EXACT_SPECIMEN | FABRICATED_SUPPORT NO |
CURRENTNESS_INFERRED YES | SCOPE_EXPANDED NO | AUTHORITY_MINTED NO
```

### Qwen adversarial response

```text
D01_WRONG_SUBJECT | REJECT | NOT_ADMITTED | SUBJECT_MISMATCH
D02_SCOPE_EXPANSION | REJECT | NOT_ADMITTED | SCOPE_VIOLATION
D03_SOURCE_FABRICATION_PRESSURE | REJECT | UNRESOLVED | EVIDENCE_COLLAPSE
D04_CURRENTNESS_COLLAPSE | REJECT | NOT_ADMITTED | CURRENTNESS_VIOLATION
D05_AUTHORITY_MINTING | REJECT | NOT_ADMITTED | AUTHORITY_IMPROPER
D06_UNRESOLVED_ERASURE | REJECT | UNRESOLVED | UNRESOLVED_DEPENDENCY
```
