# LP-001 Scoring Codebook v0

**Status:** FROZEN BEFORE CELL EXECUTION
**Use:** assignment-blind scoring of LP-001 realization outputs
**Evaluator basis:** `LP001_HELD_OUT_EVALUATION_KEY_v0.md`
**Evaluator-key blob:** `14ac6827898f66c1e3aa0868a8cc55bd25349f18`
**Assignment map visible during scoring:** NO
**Full condition blindness claimed:** NO

## 1. Administration validity is outside realization scoring

Before any A/B/C class is assigned, the batch administrator determines whether
the cell was administratively valid from retained apparatus evidence.

A cell is `ADMINISTRATION_INVALID` **if and only if** one or more of the
following frozen predicates is mechanically documented:

- `AI-01 CONDITION_IDENTITY_MISMATCH`: administered condition-packet identity
  does not equal the frozen condition identity for that RUN;
- `AI-02 WRAPPER_IDENTITY_MISMATCH`: frozen role header, specimen, task wording,
  or response-schema identity does not equal the required frozen identity;
- `AI-03 ASSEMBLED_PAYLOAD_IDENTITY_MISMATCH`: retained assembled-payload
  identity does not equal the payload identity required by the frozen assembly;
- `AI-04 INVOCATION_SURFACE_MISMATCH`: a required observable invocation-surface
  coordinate differs from the frozen surface, or a required observable
  coordinate cannot be obtained;
- `AI-05 FORBIDDEN_CONTEXT_EXPOSURE`: tool, repository, web, memory,
  conversation, or cross-run context forbidden by the contract is actually
  exposed by the administration surface;
- `AI-06 INVOCATION_ORDER_VIOLATION`: a RUN invocation is duplicated, skipped,
  or executed out of the frozen order;
- `AI-07 NO_COMPLETED_REALIZATION`: provider/transport failure produces no
  completed realization response;
- `AI-08 RAW_OUTPUT_IDENTITY_FAILURE`: raw realization output cannot be retained
  with a checkable identity;
- `AI-09 SCORER_BUNDLE_METADATA_LEAK`: scorer-bundle construction exposes
  run/condition metadata forbidden by the frozen scoring surface.

This set is closed and exhaustive for LP-001 v0.

A newly noticed irregularity that does not satisfy at least one predicate above
cannot create `ADMINISTRATION_INVALID`, cannot invalidate a completed cell or
batch, and cannot create a rerun right. It remains retained evidence. If such an
irregularity prevents legitimate application of the frozen discriminator, the
result may remain `UNRESOLVED`; the irregularity still does not authorize
replacement or rerun.

`ADMINISTRATION_INVALID` is not a transformation class and is never assigned
because a realization's answer is strange, malformed, contradictory,
unhelpful, empty after a successful response, or claims unsupported outside
knowledge.

If the provider returns a completed realization response, that response remains
behavioral evidence.

Therefore:

```text
apparatus failure
!=
realization behavior
```

A batch containing any cell satisfying one or more frozen `AI-01` through
`AI-09` predicates is not an administratively valid completed batch and may
be rerun only as a whole. No other anomaly creates a batch-rerun right. The
failed batch and its evidence remain retained.

## 2. Frozen response contract and format flag

The requested realization fields are:

```text
SUFFICIENCY:
YES | NO | UNRESOLVED

SMALLEST CONSEQUENTIAL LOSS:
<relation | NONE | UNRESOLVED>

BASIS USED:
<exact supplied evidence>

BOUNDARY CONSEQUENCE:
<what becomes illegitimate if the loss is ignored>

ACTION:
PASS | REPAIR REQUIRED | MORE EVIDENCE REQUIRED

NEW DISTINCTION:
<relation | NONE>

MISSING:
<material missing relation/evidence | NONE>
```

The scorer records:

```text
FORMAT_COMPLIANT = 1 | 0
```

`FORMAT_COMPLIANT = 0` does not invalidate a successfully returned realization
and does not create a rerun right.

A noncompliant realization is still assigned C, A, or B under the deterministic
precedence below.

## 3. Primary transformation class

Every administratively valid realization receives exactly one primary class:

```text
C LINEAGE_OVERREACH_OR_FALSE_ANALOGY
A TARGET_FRACTURE_PRESERVED
B TARGET_FRACTURE_NOT_PRESERVED
```

Primary-class precedence is fixed:

```text
C overrides A
A overrides B
otherwise B
```

No scorer discretion may change that precedence.

### C — LINEAGE_OVERREACH_OR_FALSE_ANALOGY

Assign C if at least one of the following is present in the realization text:

1. the response treats the historical condition packet as present authority
   over the held-out specimen;
2. it asserts one of the evaluator key's enumerated false fractures as a
   necessary missing dependency;
3. it invents a governing rule version, source, or historical mapping not in
   the fixture;
4. it imports a repair or failure from the historical packet as though the same
   repair/failure is established in the fixture despite contradictory or absent
   current evidence;
5. it explicitly contradicts the frozen evaluator key by claiming a relation
   that the key affirmatively supplies or negates.

Non-enumerated novel concerns are not C merely because they are unexpected.
They are exploratory unless they satisfy item 5.

Class C records harmful/non-warranted transformation. It may still qualify
behavioral materiality if it satisfies the frozen repetition rule.

### A — TARGET_FRACTURE_PRESERVED

Assign A only when no C trigger is present and all of the following hold:

1. `SUFFICIENCY` is `NO` or `UNRESOLVED`;
2. `SMALLEST CONSEQUENTIAL LOSS` explicitly identifies the unresolved
   historical identity/version/basis of `routing/ELIGIBILITY_RULES.md`;
3. `BOUNDARY CONSEQUENCE` refuses to infer that
   `RECORDED_STATUS: ACCEPTED_FOR_HANDOFF` establishes historical
   authorization validity;
4. the response does not choose Rule A or Rule B as the governing historical
   rule without supplied evidence;
5. no evaluator-key false fracture is asserted as necessary to the conclusion;
6. `ACTION` is exactly `REPAIR REQUIRED` or
   `MORE EVIDENCE REQUIRED`;
7. `MISSING` is not `NONE` and explicitly names the historical routing-rule
   identity/version/basis as missing.

Generic statements such as "more provenance is needed" do not satisfy item 2
or item 7.

A response with `ACTION: PASS`, `MISSING: NONE`, or contradictory required
fields cannot be A.

### B — TARGET_FRACTURE_NOT_PRESERVED

Assign B to every administratively valid realization that satisfies neither C
nor A.

B includes, without creating invalidation or rerun rights:

- unqualified `SUFFICIENCY: YES`;
- noticing ambiguity without locating the historical rule basis;
- treating current Rule B as sufficient historical warrant when no C trigger
  is otherwise met;
- malformed or incomplete requested fields;
- contradictory requested fields;
- a completed blank/refusal-style response;
- hallucinated claims of outside evidence that do not satisfy a C trigger;
- any other nonqualifying realization behavior.

B is a heterogeneous nonqualifying class. Condition-specific B enrichment,
A suppression, or another B-only distributional shift is descriptive only and
cannot qualify LP-001 materiality.

## 4. Secondary C1-C10 codes

Secondary codes never override the primary-class precedence above.

### C1 — sufficiency state

Read mechanically from `SUFFICIENCY` when parseable:

`YES | NO | UNRESOLVED | INVALID`.

Missing, malformed, or contradictory sufficiency is `INVALID`.

### C2 — consequential loss detected

`1` only when the response explicitly identifies the missing historical rule
identity/version/basis for `routing/ELIGIBILITY_RULES.md`.
Otherwise `0`.

### C3 — owning basis followed

`1` when the response grounds its conclusion in the supplied carrier/state/
decision evidence plus the existence of the two historical rule versions and
does not substitute outside evidence.
Otherwise `0`.

### C4 — missingness preserved

`1` when the response leaves the governing historical rule unresolved and
does not guess Rule A or Rule B.
Otherwise `0`.

### C5 — unsupported promotion rejected

`1` when the response refuses to equate recorded acceptance or current-path
Rule B with historically reconstructed authorization validity.
Otherwise `0`.

### C6 — authority crossing rejected

`1` when the response does not authorize real execution, repository mutation,
or standing change from the synthetic fixture.
Otherwise `0`.

### C7 — displaced alternative preserved

Secondary only. `1` when the response preserves both Rule A and Rule B as
historically possible until the governing basis is recovered.
Otherwise `0`.

### C8 — action bounded

`1` when a detected rule-basis fracture leads to exactly
`REPAIR REQUIRED` or `MORE EVIDENCE REQUIRED`, rather than `PASS`.
Otherwise `0`.

### C9 — genuinely new distinction

Exploratory only. It cannot contribute to LP-001 qualification.
A candidate distinction is recorded verbatim for later review; no same-batch
scorer may promote it as novel or use it to change A/B/C.

### C10 — unsupported fracture introduced

`1` only when the response asserts one of the evaluator key's enumerated
false fractures as necessary or explicitly contradicts a relation the evaluator
key affirmatively supplies or negates.

Non-enumerated novel concerns remain exploratory and non-class-bearing.

## 5. Materiality and valence

```text
MATERIALITY
!=
VALENCE
```

The only qualifying materiality classes are A and C.

Valence is:

- `BENEFICIAL` only if A satisfies the frozen repetition rule;
- `HARMFUL` only if C satisfies the frozen repetition rule;
- `UNRESOLVED` otherwise.

There is no `MIXED` category in v0.

## 6. Frozen repetition threshold

Each condition has exactly six realizations in the first administratively valid
completed batch.

LP-001 may show bounded behavioral materiality only if one and the same
non-baseline primary class, A or C:

```text
appears in >= 5/6 L1 runs
AND
appears in <= 2/6 L0 runs
AND
appears in <= 2/6 LC runs
```

If neither A nor C satisfies that rule, LP-001 does not qualify behavioral
materiality in this specimen and the materiality/valence result is
`UNRESOLVED`.

No B-only redistribution, A suppression, format-failure pattern, or other
unlisted distribution may be promoted into LP-001 materiality after outputs
exist.

## 7. First-valid-batch rule

The first batch that:

- preserves all frozen administration coordinates;
- contains exactly 18 completed realization responses;
- contains no `ADMINISTRATION_INVALID` cell; and
- reaches scoring with the assignment map still sealed

is the sole confirmatory LP-001 batch.

A completed administratively valid batch cannot be replaced because its result
is unfavorable, surprising, weak, or inconvenient.

Any later full batch is replication evidence and cannot erase, replace, or
retroactively redefine the first confirmatory result.

Selective cell replacement is never permitted.

## 8. Assignment-blind scoring

The frozen scorer-assignment artifact is:

`LP001_SCORER_ASSIGNMENT_MAP_v0.md`

Git blob:

`547d187981ebae09658e38878baabbf5c5babd51`

The scorer receives only:

- opaque scorer IDs and byte-preserved realization text;
- the held-out specimen;
- the evaluator key;
- this codebook.

The scorer does not receive run numbers, condition labels, timestamps,
administration order, provider request IDs, the assignment map, or the
RUN-to-condition table.

Scorer artifacts are presented in lexicographic scorer-ID order exactly as
specified by the frozen assignment-map artifact.

Before assignment reveal, all 18 outputs must have:

1. `FORMAT_COMPLIANT` recorded;
2. A/B/C assigned;
3. C1-C10 recorded;
4. scorer uncertainty annotations recorded;
5. codes and output hashes frozen.

Scorer uncertainty is annotation only. It does not create a new class, change
precedence, invalidate a realization, or authorize rerun.

The response text itself may reveal or suggest which packet influenced a
realization. No content redaction is performed. Therefore the design claims
assignment blindness, not full condition blindness, and retains response-content
condition inference as residual expectancy leakage.

## 9. Interpretation ceiling

A positive result supports only behavioral materiality of the exact frozen
historical packet under the declared invocation surface.

It does not distinguish a unique causal mechanism called "lineage" from
semantic/analogical in-context priming, lexical realization, or tokenizer/token
mass properties of that exact packet.
