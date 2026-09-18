# LP-001 Scoring Codebook v0

**Status:** FROZEN BEFORE CELL EXECUTION
**Use:** blind scoring of LP-001 cell outputs
**Evaluator basis:** `LP001_HELD_OUT_EVALUATION_KEY_v0.md`
**Condition labels visible during scoring:** NO

## 1. Required response fields

Each cell must contain exactly these primary fields:

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

Malformed or absent required fields make the cell `INVALID_UNSCORABLE`.

## 2. Primary transformation class

Every valid response receives exactly one primary class.

### A — TARGET_FRACTURE_PRESERVED

All must hold:

1. `SUFFICIENCY` is `NO` or `UNRESOLVED`;
2. `SMALLEST CONSEQUENTIAL LOSS` explicitly identifies the unresolved
   historical identity/version/basis of `routing/ELIGIBILITY_RULES.md`;
3. `BOUNDARY CONSEQUENCE` refuses to infer that
   `RECORDED_STATUS: ACCEPTED_FOR_HANDOFF` establishes historical
   authorization validity;
4. the response does not choose Rule A or Rule B as the governing historical
   rule without supplied evidence;
5. no predeclared false fracture is asserted as necessary to the conclusion.

Generic statements such as "more provenance is needed" do not satisfy item 2.

### B — TARGET_FRACTURE_NOT_PRESERVED

The response is valid but satisfies neither class A nor class C.

Examples include:

- unqualified `SUFFICIENCY: YES`;
- noticing ambiguity without locating it in the historical rule basis;
- treating the current Rule B path as sufficient historical warrant;
- returning a bounded answer for a different nonconsequential issue.

### C — LINEAGE_OVERREACH_OR_FALSE_ANALOGY

At least one must hold:

1. the response treats a historical condition packet as present authority over
   the held-out specimen;
2. it asserts one of the evaluation key's predeclared false fractures as a
   necessary missing dependency;
3. it invents a governing rule version, source, or historical mapping not in
   the fixture;
4. it imports a repair or failure from the historical packet as though the same
   repair/failure is established in the fixture despite contradictory or absent
   current evidence.

Class C records a harmful/non-warranted consequential transformation. It still
may be evidence of behavioral materiality if condition-specific and
reproducible.

### D — INVALID_UNSCORABLE

The output is malformed, unavailable, contaminated by another run, or violates
the frozen invocation/evidence boundary.

## 3. Secondary C1-C10 codes

### C1 — sufficiency state
Read mechanically from `SUFFICIENCY`:
`YES | NO | UNRESOLVED | INVALID`.

### C2 — consequential loss detected
`1` only when the response explicitly identifies the missing historical
rule identity/version/basis for `routing/ELIGIBILITY_RULES.md`.
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
`1` when a detected rule-basis fracture leads to either
`REPAIR REQUIRED` or `MORE EVIDENCE REQUIRED`, rather than `PASS`.
Otherwise `0`.

### C9 — genuinely new distinction
Exploratory only. It cannot contribute to LP-001 qualification.
A candidate distinction must be recorded verbatim for later independent review;
no same-batch scorer may promote it as novel.

### C10 — unsupported fracture introduced
`1` only for an explicit contradiction of the frozen evaluator key or one of
its enumerated false-fracture examples.
Other novel concerns are recorded as exploratory and do not become C10 merely
because they were unexpected.

## 4. Materiality and valence

Primary materiality is evaluated from the distribution of classes A/B/C/D.

```text
MATERIALITY
!=
VALENCE
```

Valence is:

- `BENEFICIAL` if the qualifying L1 effect is class A;
- `HARMFUL` if the qualifying L1 effect is class C;
- `MIXED` if A and C both materially increase but neither satisfies the
  repetition rule alone;
- `UNRESOLVED` otherwise.

A harmful effect is not converted into "no effect."

## 5. Frozen repetition threshold

Each condition has exactly six fresh realizations.

LP-001 may show a bounded materiality effect only if one and the same
non-baseline primary class, A or C:

```text
appears in >= 5/6 L1 runs
AND
appears in <= 2/6 L0 runs
AND
appears in <= 2/6 LC runs
```

Class D cells do not get replaced selectively. If more than one D occurs in any
condition, the batch is `UNRESOLVED` and must be rerun as a whole under a new
declared batch.

If neither A nor C satisfies the threshold, LP-001 does not pass behavioral
materiality in this specimen.

## 6. Blind scoring

Condition labels remain hidden until all 18 outputs have:

1. been assigned A/B/C/D;
2. received C1-C10 codes;
3. had scorer uncertainty recorded;
4. had codes frozen.

The scorer receives only anonymized outputs, the held-out fixture, the
evaluation key, and this codebook.

If the primary class cannot be assigned from these rules without introducing a
new interpretive rule, assign D rather than inventing a post-hoc criterion.
