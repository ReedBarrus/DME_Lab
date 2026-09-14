# Cross-Domain Tomographic Re-Adjudication v0

## Scope and repository gate

This hardware-free pass re-adjudicates the repository-acoustic comparison from
committed evidence only. It emitted and captured no audio, moved no hardware,
changed no gain or routing, created no observer, and did not mutate canonical
history.

After `git fetch origin main`, local `main` and `origin/main` were identical at
`01808db0c5f5151df57bb3b6e1e7ae98b4a603ab` (`A-B-A Positional Modulation on
acoustic investigation`). Divergence was `0/0` and the starting worktree was
clean. The unmodified baseline suite passed 494/494.

The relevant chronology is material:

1. `absent_interval_round_trip_pressure_v0` entered at
   `d129a6da2a617ccbc6e6a4bf871bd49768688e3e`;
2. the first repository-acoustic comparison entered at
   `d092aa0cda0ada600b8a4cf4be899497d020172c`;
3. predictive selection entered at
   `2618453d233a5867757c22ff732459f701834372`;
4. the independent WASAPI witness entered at
   `a7ea13d45b60f7109dd0abe35bf23fc695ed30c5`;
5. positional A1 -> B -> A2 evidence entered at the starting commit.

The repository round-trip relation is therefore prior evidence. The proposed
cross-domain mapping and expected acoustic consequence were not preregistered.

## Before and now

Before, the acoustic side lacked an independently observed source-relative
coordinate whose equality or change was established before DME ingest. The
earlier comparison could not distinguish command construction from render-path
observation, and therefore returned `tomographic_structure_not_yet_earned`.

Now, current evidence supplies all four parts of that specific gate:

| Requirement | Current evidence | Standing |
| --- | --- | --- |
| independently observed source-relative coordinate | a separate-process WASAPI watcher reacquired the exact Realtek post-mix endpoint and retained endpoint PCM-derived evidence | satisfied at the declared post-mix endpoint boundary |
| observable equality/change | all 15 primary endpoint observations had maximum shape distance `7.78360568894479e-15` dB and mean-level range `0.516145272125712` dB | recurrent equality under the frozen source-stability rule |
| transformation outside DME ingest | the operator reported A -> B microphone displacement and B -> A2 return; labels were marked before evidence and joined only after capture | satisfied under operator-reported, not instrumented, geometry |
| downstream relational consequence | B separated from A1 by `22.60332427957769` dB against a `9.458591613680312` dB threshold; A2 was `3.8242218132972137` dB from A1 and all five A2 trials were closer to A1 than B | recurrent position-conditioned microphone realization |

This removes the named acoustic source-coordinate insufficiency. It does not
establish driver receipt, DAC output, speaker actuation, pure airborne
causality, measured geometry, a physical transfer function, or tomography by
itself.

## Candidate reassessment

Eight candidate families were pressure-tested. `R` is new; the other seven
retain their earlier labels so lineage remains legible.

| Candidate | New evidence effect | Current classification | After shared-pipeline subtraction |
| --- | --- | --- | --- |
| A. configuration versus observation occurrence | acoustic source equality is now observed rather than inferred from a requested condition, strengthening the equality side | partial, basis-relative | generic occurrence non-collapse remains useful but is not a matched transformation |
| B. process lifetime versus historical continuity | none: WASAPI process independence and new acoustic observations still differ from recovery of old durable records | refuted | no candidate |
| C. concrete realization versus relational signature | materially strengthened by changed B realization and A2 recurrence under stable endpoint evidence | partial, basis-relative | subsumed by the more specific return candidate R |
| D1. source coordinate versus reduced/downstream evidence | moves from insufficient to partial because endpoint and microphone observations now bound a source-relative reduction relation | partial, different reduction classes | finite observation alone remains too general |
| D2. shared capture/envelope/history/analysis pipeline | unchanged and exact at its software boundary | representation-induced, supported locally | subtracted completely; it is not source tomography |
| E. structural admission versus source or physical truth | post-mix success is better witnessed, but no acoustic failure counterpart was exercised and admission is not the positional transformation | partial prohibition only | no matched transformation |
| F. source/change noun substitution | no evidentiary change | linguistic only | rejected |
| R. return transformation | newly available stable endpoint plus external A -> B -> A2 intervention, changed B microphone realization, and A2 recurrence | partial and basis-relative | one nontrivial source-domain candidate survives |

The new evidence does not revive B, convert D2 into source structure, or make E
predictive. It sharpens A, C, and D1, while R is the only candidate that remains
nontrivial after common instrumentation is removed.

## Return-transformation candidate R

### Repository relation

The earlier absent-interval pressure executed three external-driver paths in
independent temporary Git repositories:

```text
C0: alpha -> alpha
S1: alpha -> beta -> alpha
S2: alpha -> beta
```

In S1 the driver observed beta content and dirty Git, then restored alpha
content, exact `mtime_ns`, clean HEAD, branch, status, and capture-error state
before the second DME capture. A1-like and A2-like repository endpoint
configurations were exactly equivalent while their observation occurrences
were distinct. The beta excursion was real control evidence but deliberately
absent from DME history. S2 established that beta was observer-discriminable
when left at the endpoint.

### Acoustic relation

The positional pressure retained five paired observations at each of A1, B,
and A2. Each trial independently captured post-mix endpoint PCM through a fresh
separate watcher and microphone PCM through the existing observer. The endpoint
relation passed its frozen recurrence gate. B was discriminable from A1, and
the independently acquired A2 block recurred toward A1 rather than B.

### Required dimensions

| Dimension | Repository coordinate | Acoustic coordinate |
| --- | --- | --- |
| source coordinate | filesystem content/hash/size/mtime plus Git HEAD, branch, status, and capture errors in a temporary repository | Realtek post-mix endpoint spectrum plus XIBERIA microphone spectral response under operator-marked position |
| observation occurrence | two real filesystem/Git capture pairs with distinct timestamps, records, indices, and digests | 15 paired endpoint/microphone trials with distinct process/PCM/occurrence identities |
| transformation | external driver alpha -> beta -> alpha, with no mutation during capture | operator-reported A1 -> B displacement and B -> A2 return while requested render configuration remained fixed |
| relational signature | exact endpoint-configuration equality across distinct occurrences; S2 endpoint change detectability | stable endpoint shape; A1/B separation; A2 closer to A1 than B under the frozen metric |
| preserved | alpha filesystem/Git endpoint configuration after return | post-mix endpoint relation and recurrence toward the A1 microphone realization |
| changed | control-observed interval configuration and observation occurrence | microphone position, B microphone realization, and every sampled occurrence |
| unresolved | the hidden interval path from DME history; general recurrence semantics | exact geometry, synchronization, physical mechanism, room field, driver/DAC/speaker behavior |
| source independence | repository mutations existed before and outside capture, envelope, and ledger code | endpoint witness and human physical intervention existed outside ingest; microphone is a distinct observation path |
| observer independence | real filesystem and Git observers; beta is independently control-observed but not DME-observed in S1 | separate-process WASAPI endpoint watcher and microphone observer; position remains operator-reported |
| shared-pipeline contamination | record/envelope/ledger/reconstruction structure is common machinery and removed from the comparison | same |
| representation dependence | exact equality depends on declared snapshot/Git fields and hash/mtime boundaries | distances depend on frozen spectral bins, source normalization, response metric, and thresholds |
| retrospective/prospective | repository relation predates acoustic evidence | mapping to the already-observed acoustic relation was selected retrospectively |
| prediction standing | no prior artifact mapped this repository round trip to a positional acoustic result | no prospective acoustic consequence was declared |

Proposed correspondence:

```text
external A -> B -> A transformation
+
independently discriminable B
+
equivalent or recurrent A endpoint realization at a later occurrence
```

This structure is independently constituted in both domains and survives
shared-pipeline subtraction. It is not exact. It is a partial, basis-relative
correspondence because its operational scales disagree in important ways:

- repository B was control-observed but intentionally not captured by DME,
  whereas acoustic B was directly observed by paired witnesses;
- repository transformation changed the observed source configuration, whereas
  acoustic transformation changed microphone position under a stable observed
  render coordinate;
- repository return is exact symbolic/content/mtime equality under declared
  fields, whereas acoustic return is noisy metric recurrence;
- repository interval history is absent from authoritative observation history,
  whereas all three acoustic blocks survive in the experiment trace.

The match therefore supports a serious candidate, not an exact commuting map
or a generalized cross-domain law.

## Shared-pipeline subtraction

Both domains use capture -> envelope -> comparator -> ledger/trace ->
reconstruction -> analysis. Removing that inherited structure eliminates D2
and any inference based only on shared record identities, hashes, admission, or
projection navigation.

The remaining residue is source-domain evidence: an external bounded return
intervention, a discriminable intermediate condition, and a later endpoint
that is equivalent or recurrent toward the initial realization. This residue
does not depend on the common DME envelope or ledger representation. Candidate
R therefore survives subtraction, subject to the scale mismatches above.

Representation identity remains different from relational identity. SHA-256
values, endpoint IDs, and occurrence IDs establish identity only under their
declared byte or observation boundaries; they do not supply the correspondence.

## Non-corresponding residue

Repository evidence remains discrete, symbolic, content-addressed, based on
logical mutations and exact declared-field comparison, durably historical,
and ordered by ledger-relative occurrences. Its hidden excursion demonstrates
endpoint-observability limits rather than a persistent transformation record.

Acoustic evidence remains a temporally sampled physical regime with
unsynchronized endpoint/microphone clocks, operator-reported geometry,
continuous-ish propagation, noise, local spectral reduction, and only bounded
post-mix and microphone witnesses. Its return is similarity under a metric,
not exact state identity.

None of this residue is transferred or deleted to make the candidate fit.

## Retrospective robustness and prediction

A temporary read-only withholding analysis used only the first three A1 trials
and first three B trials to form mean absolute-response centroids, then applied
RMS vector distance to the remaining existing observations. Both held-out A1
trials classified toward A1, both held-out B trials toward B, and all five A2
trials toward A1. The training-centroid distance was `22.833357070532234` dB.

This supports robustness of the already-existing acoustic relation. It is not
a prospective test: the mapping and withholding scheme were selected after all
target evidence existed.

No prior artifact predicted the positional result. In fact,
`cross_domain_predictive_transformation_selection_pressure_v0` explicitly
recorded that spatial displacement had no selected preserved/changed signature
or directional expectation and declined to select microphone movement. The
older repository round trip therefore supplies prior structure, but not a
preregistered cross-domain mapping or prediction that B would separate and A2
would recur.

Prediction status:

```text
cross_domain_prediction_not_earned
```

## Did the comparative picture materially change?

Yes, qualitatively but boundedly.

The WASAPI result supplied the specifically anticipated missing acoustic
source coordinate and a new independent observer relation. The positional
pressure then introduced a qualitatively new acoustic transformation family:
an external physical displacement with a changed downstream realization and a
return recurrence under a recurrent observed endpoint. In combination with
the already-earned repository round trip, this materially revises the
comparison geometry from “no matched source-side candidate” to “one
retrospective partial return-transformation candidate.”

It does not earn exact tomography, same-scale identity, or prospective
prediction. The earlier judgment was correct under its earlier evidence.

## Adjudication

Eight candidates were reconsidered. One nontrivial source-domain candidate, R,
survived shared-pipeline subtraction. It remains partial and basis-relative,
and it was selected retrospectively.

Primary status:

```text
tomographic_structure_candidate_prediction_not_earned
```

Separate prediction status:

```text
cross_domain_prediction_not_earned
```

No distinction, chart, trace, test, source, observer, production code, or
runtime ontology was added. No production promotion was earned. The canonical
14-record ledger remained byte-identical at 65,970 bytes with SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.

## Evidence and verification

Core inspected artifact hashes at the starting commit:

| Artifact | SHA-256 |
| --- | --- |
| prior comparison decision | `3a0c2c4e72fd5eec8f7eedb5531660447ce91e617aac4d1fad57784d6744df2f` |
| predictive-selection decision | `a444b434875fcc9bf5e78fd681da81846eb465dc4822bd266965106f44a7ea84` |
| source-coordinate selection decision | `18a912215adab14e114ebc81feac6990695e27baacea9f85d7e45b09f85e9472` |
| WASAPI witness decision | `9d63f85d8ff968a9704fa40f93cdcee2970fdbdec6dd1df219b399071dc86cd1` |
| WASAPI witness trace | `573e0bb377eb398c1aa55561c194fccdd4ffa5298b7ddeb682b8d62e6a8a4bcc` |
| positional decision | `e52ab83b0031d3d536a2061fabe4551312fd86a564b2f604675e3a30f9b6465c` |
| positional trace | `1c5eb7c5b6b4176ff499518371cfa36a69f251177451d816368944719745fdef` |
| absent-interval decision | `26db5d30c0843eb22064d7fb2ae34a93ecc4f177c9b695c6c393b27f4eed4a08` |
| absent-interval trace | `f14d63464373afe31edd4e936740e128e784a32a08c632b3d6259146a54b3d1a` |
| distinction registry through D-0046 | `f58473ff3bef6ca8d16ab4181f9aaf91988f9ca53a2dc25442d580d7c0651688` |

Verification after the documentation integration:

- focused absent-interval, WASAPI-witness, and positional-pressure suite:
  55/55 passed;
- full repository suite: 494/494 passed;
- `git diff --check`: passed;
- final committed HEAD and `origin/main` remained
  `01808db0c5f5151df57bb3b6e1e7ae98b4a603ab`, divergence `0/0`;
- worktree changes were limited to this decision and `PROJECT_STATE.md`;
- no commit or push was made.

## Stop boundary

The unresolved question is whether a future, genuinely preregistered mapping
can predict a new matched transformation without changing its invariant or
scale after observation. This pass does not select or execute that experiment.
