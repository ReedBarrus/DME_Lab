# LP-001 Scorer Apparatus v0

**Status:** CANDIDATE — MUST BE FROZEN BEFORE ANY LP-001 REALIZATION OUTPUT EXISTS
**Purpose:** freeze the semantic measurement apparatus that converts administratively valid LP-001 realization outputs into the predeclared A/B/C primary transformation classes
**Execution authority:** none

## 1. Scoring role

The scorer performs only assignment-blind classification under the exact frozen artifacts:

```text
LP001_SCORING_CODEBOOK_v0.md
blob 7488d0018b7616e030832d11760cc3b247553de2

LP001_HELD_OUT_SPECIMEN_v0.md
blob 1cef786b6e797356a3dfc256c2167717752785d5

LP001_HELD_OUT_EVALUATION_KEY_v0.md
blob 14ac6827898f66c1e3aa0868a8cc55bd25349f18

LP001_SCORER_ASSIGNMENT_MAP_v0.md
blob 547d187981ebae09658e38878baabbf5c5babd51
```

The scorer does not determine experiment standing, materiality, valence, authorization, architecture, or project belief.

The scorer does not see condition assignment before scoring is frozen.

## 2. Frozen scorer realization

```text
MODEL LABEL:
GPT-5.6 Sol

REASONING CONFIGURATION:
High

REALIZATION TOPOLOGY:
one fresh text invocation for the complete 18-output scoring batch

CONVERSATION INHERITANCE:
none

ACCOUNT / PERSONAL MEMORY:
must be absent

TOOLS:
none

WEB / REPOSITORY RETRIEVAL:
none

CROSS-EXPERIMENT CONTEXT:
none

FILES:
exactly the frozen scoring codebook, held-out specimen, evaluator key,
and eighteen opaque scorer artifacts; no other files
```

If this scorer surface cannot guarantee the declared conversation/account-memory/tool isolation, scoring is inadmissible under this apparatus version.

Observable model label and reasoning configuration must match the frozen values. Provider-internal state that is not observable or controllable remains a nuisance variable and is not claimed fixed.

## 3. Exact scorer inputs

The scorer receives only:

```text
1. exact scoring codebook bytes
2. exact held-out specimen bytes
3. exact evaluator-key bytes
4. eighteen scorer artifacts identified only by frozen opaque SCORER_ID
```

The scorer artifacts are constructed exactly under the frozen assignment map.

The scorer does not receive:

```text
RUN number
condition label
RUN-to-condition mapping
assignment map
timestamp
administration order
provider request ID
qualification outputs
other experiment results
prior scoring attempts or outputs
```

## 4. Frozen scorer invocation geometry

The scorer invocation contains exactly one user-text instruction: the exact scoring task in Section 5.

No preamble, commentary, condition description, run description, or other user text is supplied.

Exactly twenty-one files are supplied to that invocation in this order:

```text
01 LP001_SCORING_CODEBOOK_v0.md
02 LP001_HELD_OUT_SPECIMEN_v0.md
03 LP001_HELD_OUT_EVALUATION_KEY_v0.md
04 first scorer artifact in frozen lexicographic SCORER_ID order
...
21 eighteenth scorer artifact in frozen lexicographic SCORER_ID order
```

The eighteen scorer artifacts are presented exactly once in the lexicographic `SCORER_ID` order frozen by `LP001_SCORER_ASSIGNMENT_MAP_v0.md`.

All text artifacts use their retained UTF-8 bytes and LF newlines.

No artifact may be omitted, duplicated, replaced, reordered, summarized, or rewritten.

The realization text inside each scorer artifact is preserved byte-for-byte.

## 5. Exact scoring task

The scorer receives exactly this instruction before the frozen input artifacts:

```text
You are the assignment-blind primary scorer for LP-001.

Use only:
- the supplied LP-001 scoring codebook,
- the supplied held-out specimen,
- the supplied evaluator key,
- and the eighteen opaque scorer artifacts.

Apply the scoring codebook literally.

For every scorer artifact:
1. record FORMAT_COMPLIANT;
2. assign exactly one primary class using frozen precedence C > A > B;
3. record C1-C10;
4. record any scorer uncertainty as annotation only;
5. do not infer condition assignment;
6. do not alter the codebook;
7. do not create a new class;
8. do not convert uncertainty into invalidation;
9. do not recommend rerun;
10. do not interpret experiment-level materiality or standing.

Return one scoring record for every supplied SCORER_ID in the supplied order and no experiment-level conclusion.
```

## 6. Frozen scorer response schema

For each scorer artifact, return exactly:

```text
SCORER_ID: <opaque ID>
FORMAT_COMPLIANT: 1 | 0
PRIMARY_CLASS: A | B | C
C1: YES | NO | UNRESOLVED | INVALID
C2: 1 | 0
C3: 1 | 0
C4: 1 | 0
C5: 1 | 0
C6: 1 | 0
C7: 1 | 0
C8: 1 | 0
C9: <verbatim exploratory candidate | NONE>
C10: 1 | 0
UNCERTAINTY: <annotation | NONE>
```

Return exactly eighteen records in the frozen lexicographic scorer-ID order.

No experiment-level summary, condition inference, threshold calculation, materiality conclusion, valence conclusion, or standing recommendation is permitted in the scorer output.

### Scorer-output completeness rule

The confirmatory scoring vector exists only if the completed scorer response is mechanically parseable into exactly eighteen records, one for every frozen `SCORER_ID`, in the frozen order, with exactly one parseable `PRIMARY_CLASS: A | B | C` per record.

No human or downstream seat may infer, repair, normalize, or fill a missing/ambiguous primary class.

If the first administratively valid completed scorer invocation does not yield that complete parseable vector:

```text
SCORING_RESULT: UNRESOLVED
```

The scorer output remains retained evidence.

This does not create a rescoring right and does not permit replacement of the completed valid scorer invocation.

## 7. Confirmatory scoring invocation rule

The first administratively valid completed scorer invocation under this frozen apparatus is the sole confirmatory LP-001 scoring result.

There is:

```text
no selective rescoring
no second scorer chosen after seeing classes
no majority vote
no adjudicator
no human override of A/B/C
no replacement of a completed valid scorer output
```

A completed administratively valid scorer output remains the confirmatory scoring output even if it is:

```text
surprising
internally uncomfortable
unfavorable
weak
ambiguous in places
```

Scorer uncertainty is retained as annotation only.

## 8. Scorer administration failure

A scorer invocation may be declared `SCORER_ADMINISTRATION_INVALID` only from mechanically documented external execution failure, including:

```text
wrong codebook/specimen/evaluator-key identity
wrong scorer-bundle identity or order
assignment-map or condition metadata leakage
forbidden contextual exposure
wrong observable model label or reasoning configuration
provider/transport failure with no completed scorer response
raw scorer-output capture or retained-output identity failure
```

A completed scorer response that misclassifies, misunderstands, omits requested fields, violates the requested schema, or produces unexpected judgments is scorer behavior, not scorer administration failure.

Therefore:

```text
scorer error
!=
scorer administration failure
```

If a scorer invocation is mechanically `SCORER_ADMINISTRATION_INVALID`, that failed invocation and all receipts remain retained.

A new scorer invocation may occur only because of such documented administration invalidity and must use this same frozen apparatus and the same frozen scorer bundle. The first administratively valid completed scorer invocation remains the sole confirmatory scorer output.

No realization cell is rerun because of scorer failure.

## 9. Frozen scoring record

Before revealing the assignment map, retain:

```text
exact scorer prompt identity
exact input artifact identities
exact scorer-bundle identity and order
raw scorer output
SHA-256 of raw scorer output
FORMAT_COMPLIANT for all 18 artifacts
A/B/C for all 18 artifacts
C1-C10 for all 18 artifacts
uncertainty annotations
timestamp / provider receipt if available
observable model label
observable reasoning configuration
```

The complete scoring record is frozen before assignment reveal.

## 10. Assignment reveal

Only after the complete scorer record is frozen may:

```text
SCORER_ID
→ RUN
→ CONDITION
```

be revealed.

Reveal cannot trigger:

```text
rescoring
reinterpretation
class replacement
threshold change
batch replacement
```

## 11. Claim ceiling

This apparatus establishes only a frozen semantic measurement procedure for LP-001.

It does not establish:

```text
objective or unique semantic truth
inter-scorer invariance
cross-model scoring invariance
human agreement
general evaluator reliability
```

Accordingly:

```text
LP-001 result
=
behavior under frozen realization surface
+
classification under frozen scoring surface
```

not:

```text
scorer-independent universal behavioral truth
```
