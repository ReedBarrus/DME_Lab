# Cross-Domain Predictive Transformation Selection Pressure v0

## Scope and Starting Boundary

This hardware-free pass asks whether Candidates A, C, or E from the first
repository-acoustic comparison already constrain a falsifiable source-domain
prediction strongly enough to select a next transformation. It uses prediction
first and transformation second. It emits and captures no audio, adds no
source, changes no physical arrangement, and creates no production machinery.

Refreshed local `main` and `origin/main` were identical at
`d092aa0cda0ada600b8a4cf4be899497d020172c`
(`Comparison between Repo and Audio`), with divergence `0/0` and a clean
worktree.

The earned starting result was `tomographic_structure_not_yet_earned` with
`freeze_comparison_and_seek_new_transformation`. Candidate A, C, and E were
partial correspondences; D2 was supported only because both domains traversed
the same generic DME pipeline.

## Prediction Admissibility Applied

A candidate prediction must be predeclarable, follow from existing evidence,
be capable of failure, materially wound its correspondence on failure, add
information beyond pipeline compatibility, be observable in one bounded pass,
and allow domain residue. The pipeline-subtraction question is decisive:

> Would the prediction still be interesting if observation-envelope,
> admission, ledger, reconstruction, and projection machinery were removed?

Predictions that reduce to continued ingestion, distinct occurrence IDs,
generic repetition, or unspecified possible survival are rejected.

## Candidate A — Configuration/Condition Descriptor Versus Occurrence

Candidate shared relation `R_A`:

```text
equality at a configuration/condition-descriptor scale
does not imply equality of observation occurrence
```

Repository evidence: two real filesystem captures had the same snapshot and
envelope identities at different observation intervals. Acoustic evidence:
equal requested C0/S1/S2 condition labels had distinct trial IDs, buffer
hashes, and measurements across repeated trials and acquisition blocks.

Known mismatch: repository equality is observed structural equality within an
explicit snapshot scope. Acoustic equality is only equality of requested
command condition; physical room, routing, emission, and transduction state are
not established equal.

### Attempted recognizable signature

```text
DOMAIN A — repository
before: relations {same observed snapshot, distinct occurrence}
TA: recapture without a selected source change
after:
  preserved {snapshot equality, if the source is in fact unchanged}
  changed {observation interval and ledger coordinates}
  unresolved residue {unobserved interval path}

DOMAIN B — acoustic
before: relations {same requested condition, distinct trials}
TB: repeat or reinitialize acquisition under the same requested condition
predicted after:
  preserved {requested condition label}
  changed {trial identity and likely sampled values}
  allowed residue {unknown physical state and mechanism}
```

The only entailed acoustic prediction is another distinct occurrence under the
same label. That is expressly non-discriminating: it is supplied by acquisition
and record construction even if no source-domain correspondence exists. The
acoustic pairwise verdict pattern belongs to Candidate C and does not follow
from `R_A`.

Attempted prediction: “a repeated equal descriptor produces a distinct
occurrence.” Rejection: pipeline/generic-observation induced, predicts no novel
source-domain property, and its failure would indicate an identity bug rather
than wound a repository-acoustic relation.

Candidate A yields no admissible prediction.

## Candidate C — Concrete Realization Versus Relational Signature

Candidate shared relation `R_C`:

```text
a selected relation may remain recognizable while concrete realization changes
```

Repository evidence includes locally preserved but different relations across
endpoint recurrence, coordinator replacement, replay/reconstruction, and other
repository transformations. Acoustic evidence is more specific: S2 medians
shifted while the complete S1/C0/S2 discrimination pattern recurred after one
fresh process/backend initialization.

Known mismatch: the repository side has no one relation matching acoustic
pairwise discrimination and no one transformation matching acoustic
reinitialization. Reducing both to “some relation survived some change” created
the partial correspondence post hoc.

### Attempted recognizable signature

```text
DOMAIN A — repository
before: relations {source-relative observations, exact record identities,
                   selected historical/reconstruction relations}
TA: one repository-local transformation
after:
  preserved {only the relation tested by that specific repository pressure}
  changed {transformation-specific source or process realization}
  unresolved residue {freshness, interval path, grouping, or source success}

DOMAIN B — acoustic
before: relations {S1~C0, S2 separated from C0 and S1}
TB: not yet selected
predicted after:
  preserved {? pairwise verdict pattern}
  changed {? magnitude or spread}
  allowed residue {physical mechanism, routing, gain, spatial field}
```

The question marks cannot be filled from current evidence for a qualitatively
new `TB`. A third process restart would merely repeat the already used
transformation and test additional acoustic recurrence, not cross-domain
structure. Spatial displacement, orientation, distance, a new command, or a
new measurement basis could each change any portion of the acoustic pattern;
the existing fixed-arrangement evidence supplies no directional expectation.

Attempted prediction: “the three-way acoustic verdict survives another or a
different transformation while magnitude may change.” Rejection: under
another restart it is generic repetition; under a different transformation it
does not follow from earned evidence. Either form lacks predictive novelty at a
matched cross-domain scale.

Candidate C yields no admissible prediction.

## Candidate E — Structural Admission Versus Source/Physical Truth

Candidate shared relation `R_E`:

```text
structural admission does not certify a stronger source-world claim
```

Repository evidence is an executed counterexample: three failed Git commands
produced errors and null state fields, yet the well-formed observation was
admitted by COMPARATOR_V0. Acoustic evidence shows admitted measurements while
speaker realization remains unobserved, but supplies no independent truth
about actuation success or failure.

Known mismatch: Git acquisition failure is independently established. Acoustic
speaker realization is missing, not known false.

### Attempted recognizable signature

```text
DOMAIN A — repository
before: relations {known degraded acquisition, structurally valid envelope}
TA: healthy Git directory -> non-Git directory
after:
  preserved {minimum structural admissibility}
  changed {source-success fields and capture errors}
  unresolved residue {consumer trust policy}

DOMAIN B — acoustic
before: relations {structurally valid measurement, unknown actuation truth}
TB: would require independently known actuation-success change
predicted after:
  preserved {structural admissibility}
  changed {? independently observed physical success}
  allowed residue {microphone response and physical path}
```

The predicted admission result is already guaranteed by comparator semantics
for a structurally unchanged envelope. Remove the common pipeline and the
prediction disappears. Conversely, current evidence cannot predict microphone
behavior under independently established speaker success or failure.

Attempted prediction: “a structurally valid acoustic observation remains
admitted even if an independent witness reports actuation failure.” Rejection:
pipeline-induced, and the necessary independent acoustic witness does not
exist. Success would retest COMPARATOR_V0, not establish source-domain
correspondence.

Candidate E yields no admissible prediction.

## Prediction Attempts Summary

| Candidate | Proposed prediction | Could fail? | Failure wounds correspondence? | Novel beyond pipeline/repetition? | Result |
| --- | --- | --- | --- | --- | --- |
| A | repeated equal descriptor yields a distinct occurrence | only via identity/recording failure | no; it wounds occurrence handling | no | rejected |
| C | acoustic pairwise pattern survives another restart | yes | weakly wounds acoustic repeatability, not the cross-domain mapping | no; same transformation and repetition | rejected |
| C | acoustic pairwise pattern survives a spatial, command, or measurement change | yes | could wound the proposed invariant | no evidence determines the expected preserved/changed pattern | rejected |
| E | structurally valid evidence remains admitted despite independently known source failure | yes at implementation level | wounds comparator behavior, not source-domain relation | no; comparator guarantees it | rejected |
| E | microphone response changes in a specified way with independently known actuation failure | yes | potentially | no independent actuation coordinate or directional evidence exists | insufficient basis |

No surviving prediction says what previously unused source-domain property must
remain or change.

## Candidate Transformation Comparison

These qualitative fields are selection aids only; no aggregate score is
computed.

| Candidate transformation | Candidate tested | Specific prediction available now | Strengthening outcome | Wound outcome | New residue | Expected discrimination | New basis | Human intervention | Physical uncertainty | Post-hoc risk | Selection |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| microphone spatial displacement | C, possibly A | none beyond “maybe pattern survives/changes” | unavailable without a predeclared signature | any result can be redescribed | geometry, room modes, placement error | low | high | medium | high | high | rejected |
| microphone orientation change | C | none directional | unavailable | unavailable | polar response and placement repeatability | low | high | medium | high | high | rejected |
| speaker/microphone distance change | C | none directional or thresholded | unavailable | unavailable | gain law, reflections, geometry | low | high | medium | high | high | rejected |
| fresh acquisition-process restart | C | same acoustic verdict pattern recurs | another acoustic recurrence | failure weakens acoustic stability but not a matched repository relation | driver/ambient/process state | low | low | low | medium | medium | rejected as generic repetition |
| new acoustic command condition | C | no predicted placement relative to C0/S1/S2 | unavailable | unavailable | new routing/actuation semantics | low | high | low | high | high | rejected |
| richer retained acoustic measurement | C, D1 | no evidence selects a feature or preserved relation | unavailable | unavailable | privacy, morphology, feature-selection dependence | medium | high | low | medium | high | rejected |
| repository-native transformation | A, C, E | repository result only; no paired acoustic consequence | repository-local relation survives | repository-local failure | source-specific commit/filesystem semantics | low | medium | low | none | high | rejected |
| another observation basis | A, C, E | no matched-scale relational signature yet | unavailable | unavailable | new source semantics and reduction boundary | medium | high | unknown | unknown | high | rejected |
| no transformation currently justified | all | prediction gates remain unsatisfied | preserves explicit missingness | future evidence may overturn | none introduced | low | low | low | low | low | selected |

Microphone movement is not selected: existing evidence does not constrain a
specific property that should survive or change under displacement.

## Pipeline Subtraction and Predictive Novelty

- Candidate A's distinct-occurrence expectation is implemented by capture and
  identity construction. It is not a source-domain prediction.
- Candidate C's further-recurrence expectation uses the same acoustic evidence
  and transformation from which recurrence was defined. It predicts more of
  the constructing pattern, not a qualitatively new consequence.
- Candidate E's admission expectation is entailed by COMPARATOR_V0's minimum
  structural checks. Without the pipeline there is no admission claim.
- “The pipeline continues working” and “new evidence can still be ingested”
  are excluded entirely.

After subtraction, no candidate predicts information not already used to build
the correspondence.

## Required Result

```text
no_cross_domain_prediction_yet_earned
```

The comparison remains frozen. The smallest missing evidence is one
independently observed source-domain coordinate on the acoustic side whose
equality or change can be established before DME ingest—not merely a requested
condition label, occurrence ID, admitted envelope, or unknown speaker
realization—and a repository coordinate demonstrably matched at the same
relational scale. Until such a matched coordinate exists, no evidence-derived
prediction can specify which relation must survive and which property must
change under a new transformation.

This statement identifies missing evidence, not a source design or permission
to add a witness. No next experiment is specified or authorized.

## Distinction and Production Status

No distinction is added or amended. The failure to earn a prediction is fully
expressed by the existing partial-correspondence findings, source/occurrence
boundary, raw/derived boundary, and structural-admission/source-success
boundary. “Prediction” and “transformation selection” do not require registry
concepts.

No audio, physical actuation, source, trace, pressure runtime, test, chart,
Atlas, tomography, topology, coherence, or production machinery is added.

## Verification and Artifacts

Tests:

- baseline full suite before authoring: 469/469 passed;
- relevant repository-horizontal and all earned acoustic tests before
  authoring: 280/280 passed;
- final relevant composition: 280/280 passed;
- final full suite: 469/469 passed;
- runner: `python -m unittest`; every command was hardware-free.

Artifacts changed:

- this decision record;
- `PROJECT_STATE.md`.

No original trace, test, runtime, registry entry, or prior decision record was
changed. Canonical live history was not used or mutated. Its SHA-256 remained
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after the pass. No `.wav`, `.pcm`, or `.raw` file was created.

Final HEAD remains `d092aa0cda0ada600b8a4cf4be899497d020172c`
(`Comparison between Repo and Audio`). The worktree contains only the two
scoped documentation changes above.
