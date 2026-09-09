# Acoustic Prediction Bridge Dwell v0

## Scope and repository gate

This analysis-only pass asks for the smallest legitimate bridge from PR-016's
physical/acoustic residue toward PR-018 prospective cross-domain prediction.
It does not execute an experiment, preregister a final experiment, or promote
tomography or prediction.

After `git fetch origin main`, local `HEAD` and `origin/main` were identical at
`7d39fc1cf41cae76c4a2a364244f534501bc8067`. The only pre-existing worktree
change was formatting-only cleanup of `WORKFLOW.md`; this pass preserves it.

The adjudication is option B: PR-018 is not ready. One physical-deepening
pressure is worth preserving as an open question before any renewed PR-018
selection, but it is not itself an informative cross-domain prediction.

## 1. PR-016 licensed surface

### Directly observed source coordinates

- A fresh separate-process WASAPI shared-mode loopback watcher independently
  reacquired the exact Realtek endpoint for every primary trial.
- The endpoint identity, mix format, packet content, hashes, spectral
  magnitudes, level-normalized shapes, and capture metadata were observed.
- Across all 15 primary trials, maximum endpoint shape distance was
  approximately `7.78e-15` dB and endpoint mean-level range was `0.516145` dB.
  Both frozen source-stability criteria passed.

This coordinate is post-mix endpoint PCM. It is not commanded playback,
speaker position, driver receipt, DAC output, transducer motion, or airborne
sound.

### Operator-supplied intervention provenance

- A, B, and return-to-A definitions were marked before primary evidence.
- The operator reported A1 -> B -> A2 microphone movement, approximately one
  microphone length laterally, with height and orientation held or restored.
- The operator reported unchanged speaker position, system gain, routing, and
  hardware settings.

The microphone positions, displacement, orientation, and return placement were
not machine measured.

### Downstream measurements

- Each trial independently sampled XIBERIA microphone PCM through the existing
  microphone observer.
- The retained reduction was a ten-bin, source-normalized microphone spectral
  signature containing absolute response and level-normalized shape.
- The frozen absolute-response centroid distances were `22.603324` dB for
  A1-to-B, `3.824222` dB for A1-to-A2, and `24.203247` dB for A2-to-B.

### Derived recurrence

Under the frozen metric and threshold, B discriminated from A1. A2 was closer
to A1 than B, A1-to-A2 was less than half the A1-to-B separation, and all five
A2 trials were individually closer to A1. The licensed status is
`positional_acoustic_transformation_recurrent`.

### Unresolved physical interpretation

PR-016 does not identify why the microphone realization changed. It does not
separate changed relative geometry from microphone handling, exact pose,
orientation error, cable movement, local obstruction, ambient variation, or
other consequences of the operator intervention. It does not establish pure
airborne causality, a physical transfer function, complete room state, or a
general law.

## 2. Unresolved acoustic residue

The following alternatives remain compatible with PR-016:

1. **Relative-geometry response:** changing microphone position relative to a
   fixed source changed the sampled realization, and restoring the relation
   produced recurrence.
2. **Observer-side handling or pose nuisance:** movement, cable state, angle,
   support contact, or imperfect pose restoration supplied part or all of the
   separation and return.
3. **Intervention-locus dependence:** moving the microphone may not generalize
   to moving the physical source while holding the microphone fixed.
4. **Level-dominant versus shape-bearing response:** both absolute response and
   post-hoc normalized shape changed, but only absolute response carried the
   frozen primary judgment.
5. **Coordinate return versus state return:** operator-reported return to the
   marked coordinate coincided with response recurrence; exact physical state
   recurrence was not observed.
6. **Boundary-specific response:** microphone orientation, source geometry, or
   a changed path boundary could each produce a different relation even when
   the post-mix endpoint remains stable.

PR-017 contributes one retrospective cross-domain pattern: an external
A -> B -> A transformation with a discriminable intermediate and a later
equivalent or recurrent A realization. It does not select which of these
physical alternatives is true and contains no direction, magnitude, spectral,
or mechanism-specific acoustic expectation.

## 3. Candidate transformations

Five candidates were assessed. Each could use the existing post-mix and
microphone observers. Instrumentation failure would be declared separately if
either observer failed, the endpoint stability gate failed, or a required
capture was incomplete.

### C1. Speaker lateral displacement and return with microphone fixed

- **Transformation:** operator-marked speaker A1 -> B -> A2 lateral movement;
  microphone position, height, and orientation fixed.
- **Observed source coordinate:** post-mix endpoint PCM remains independently
  observed; physical speaker position remains operator provenance.
- **Downstream target:** the existing source-normalized microphone spectral
  signature at unseen B and A2 trials.
- **PR-017 contribution:** it identifies source-side change versus observer-side
  change as a material scale mismatch and motivates placing the reversible
  intervention on the acoustic source side.
- **Separate acoustic contribution:** ordinary acoustics makes changed relative
  geometry relevant, and PR-016 supplies a proven measurement lane, source
  gate, and bounded return criterion.
- **Freezable expectation:** if the endpoint gate passes, B separates from A1
  and A2 recurs toward A1 under a predeclared version of the PR-016 metric.
- **Prediction failure:** complete stable-source evidence with no B separation,
  or with B separation but no A2 return.
- **Nuisance boundary:** operator-only speaker geometry, speaker orientation,
  support coupling, cable movement, microphone drift, and room activity.
- **Cost and requirements:** medium operator action; no new hardware and no new
  software observer.
- **Meaning of success:** within-domain prospective recurrence and limited
  evidence against a microphone-handling-only account; not informative
  cross-domain prediction and not a physical mechanism.

### C2. Microphone orientation change and return at fixed location

- **Transformation:** rotate the microphone from marked orientation A to B and
  restore A2 without translating its marked location.
- **Observed source coordinate:** independently observed stable endpoint PCM;
  orientation is operator provenance.
- **Downstream target:** unseen microphone response signature.
- **PR-017 contribution:** only the abstract return pattern.
- **Separate acoustic contribution:** directional microphone response and
  PR-016's observer-side recurrence make change-and-return plausible.
- **Freezable expectation:** B separation and A2 recurrence under a frozen
  metric, with no predeclared spectral direction.
- **Prediction failure:** stable complete witnesses with failed B separation or
  failed return.
- **Nuisance boundary:** translation during rotation, cable/support movement,
  angle error, and unknown microphone directivity.
- **Cost and requirements:** low operator action; no new hardware or observer.
- **Meaning of success:** within-domain orientation-conditioned recurrence and
  limited physical deepening, not cross-domain predictive novelty.

### C3. Reversible path obstruction with source and microphone fixed

- **Transformation:** insert a predeclared passive obstruction at B and remove
  it for A2 while leaving source and microphone positions fixed.
- **Observed source coordinate:** independently observed stable endpoint PCM;
  obstruction placement is operator provenance.
- **Downstream target:** unseen microphone response signature.
- **PR-017 contribution:** only the abstract external excursion and return.
- **Separate acoustic contribution:** ordinary acoustic knowledge already
  predicts that an obstruction may change level or spectral shape and that its
  removal may restore them.
- **Freezable expectation:** B separation and A2 recurrence under a frozen
  metric; no evidence licenses a directional spectral prediction.
- **Prediction failure:** stable complete witnesses with no B separation or no
  return after removal.
- **Nuisance boundary:** obstruction material and placement, reflections,
  environmental disturbance, and absent machine observation of the boundary.
- **Cost and requirements:** low-to-medium operator action using a declared
  passive object; no new measurement hardware or observer.
- **Meaning of success:** within-domain boundary-conditioned recurrence and
  limited path-sensitivity evidence, not informative cross-domain prediction.

### C4. Repeat the original microphone displacement and return

- **Transformation:** repeat the PR-016 A1 -> B -> A2 protocol.
- **Observed source coordinate:** the validated endpoint witness.
- **Downstream target:** another microphone response block.
- **PR-017 contribution:** none beyond naming the already-observed return.
- **Separate acoustic contribution:** PR-016 directly supplies the expectation.
- **Freezable expectation:** recurrence of the existing discrimination and
  return verdict.
- **Prediction failure:** a complete stable-source trial that does not recur.
- **Nuisance boundary:** the full existing operator-pose and room residue.
- **Cost and requirements:** low operator action; no new hardware or observer.
- **Meaning of success:** additional within-domain recurrence only.

### C5. Radial microphone distance change and return

- **Transformation:** move the microphone a predeclared distance toward or away
  from the speaker and return it to A2, holding orientation and height fixed.
- **Observed source coordinate:** independently observed stable endpoint PCM;
  distance is operator provenance.
- **Downstream target:** unseen microphone response signature.
- **PR-017 contribution:** only the abstract return topology.
- **Separate acoustic contribution:** ordinary level-versus-distance knowledge
  and PR-016 already motivate separation and return.
- **Freezable expectation:** B separates and A2 returns; neither repository
  evidence nor PR-016 licenses a quantitative level law or spectral direction.
- **Prediction failure:** stable complete witnesses with no B separation or no
  A2 return.
- **Nuisance boundary:** unmeasured distance, lateral/angle drift, near-field
  behavior, reflections, and handling.
- **Cost and requirements:** low operator action; no new hardware or observer.
- **Meaning of success:** within-domain distance-conditioned recurrence and
  limited physical deepening, not cross-domain predictive novelty.

## 4. Contribution separation

| Candidate | What PR-017 uniquely supplies | What PR-016 or ordinary acoustics supplies | Prospective standing |
| --- | --- | --- | --- |
| C1 speaker displacement | identifies the repository-source/acoustic-observer locus mismatch and selects source-side intervention as the sharper comparison | geometry sensitivity, the measurement lane, and the entire B-separation/A2-return expectation | useful physical-deepening pressure only |
| C2 orientation | abstract A -> B -> A form | pose sensitivity and return expectation | within-domain only |
| C3 obstruction | abstract external excursion and return | boundary sensitivity and return expectation | within-domain only |
| C4 exact repeat | nothing not already used to form PR-017 | the full expected result | repetition only |
| C5 radial distance | abstract A -> B -> A form | level/geometry sensitivity and return expectation | within-domain only |

## 5. Shared-explanation subtraction and rejection

| Candidate | Subtraction result | PR-018 judgment |
| --- | --- | --- |
| C1 | after subtracting PR-016 and ordinary geometry expectations, only better alignment of the intervention locus remains; no repository-specific downstream outcome remains | rejected as a direct PR-018 target; retained as an intermediate pressure |
| C2 | the expected change and return follow from microphone pose sensitivity and PR-016's return pattern | rejected |
| C3 | generic acoustics supplies the expected effect and removal recurrence; PR-017 adds no direction or threshold | rejected |
| C4 | the expected result is exactly the evidence already used to construct PR-017 | rejected |
| C5 | ordinary distance response and PR-016 supply the expected relation; the cross-domain mapping adds no discriminating outcome | rejected |

All five candidates are rejected as direct PR-018 bridges. No metric, mapping,
position, or definition of return may move after acquisition to rescue one.
Commanded or operator-reported configuration would schedule the intervention,
not guarantee success. A source-gate or acquisition failure would remain an
instrumentation result rather than prediction failure.

## 6. Strongest surviving candidate and information gain

C1 is the sole survivor for a narrower purpose. Moving the speaker while
holding the microphone fixed has the best information gain because it directly
pressures two live alternatives: relative-geometry response versus
microphone-handling nuisance, and source-side versus observer-side
intervention. It also retains the validated source gate and downstream metric.

The other candidates either repeat PR-016, continue moving the observer, or
introduce a new unobserved boundary without reducing the source/observer scale
mismatch. None supplies an informative cross-domain prediction.

## 7. Whether PR-018 is ready

No. PR-018 still lacks a repository-derived expectation that changes the
predicted acoustic outcome after PR-016 and ordinary acoustic knowledge are
subtracted. The antecedent repository relation says only that a discriminable
intermediate may be followed by return to an equivalent endpoint. It does not
specify acoustic direction, magnitude, feature, asymmetry, persistence, or
which physical intervention should preserve or change the target signature.

## 8. Smallest missing discriminator

The smallest missing discriminator is an antecedently selected relation whose
repository contribution chooses between at least two otherwise viable acoustic
outcomes. That contribution must be more specific than "B changes and A
returns," must remain fixed before unseen acoustic acquisition, and must still
matter after the within-domain PR-016 recurrence and ordinary acoustic
expectations are removed.

C1 can reduce the intervention-locus mismatch, but its result cannot supply
that discriminator retroactively.

## 9. Third-option adjudication and recommended next pressure

The third option is not PR-006. PR-006 concerns scoped repository/OS interval
or change observation and currently has no demonstrated acoustic mapping,
physical intervention coordinate, or predictive contribution. Merging it into
this branch would create apparent structure rather than evidence.

A genuinely different intermediate pressure is exposed:

> Under a recurrent independently observed post-mix endpoint relation and a
> fixed microphone, does controlled speaker displacement produce a
> discriminable microphone realization that recurs when the speaker returns to
> its original position?

This is preserved as open PR-019. It is the smallest comparison-directed
physical-deepening pressure if further physical work is selected. It is not
active or authorized, does not unlock PR-018 by itself, and no execution
warrant is written here.

## 10. Explicit non-claims

This dwell does not claim or establish:

- a prospective cross-domain prediction;
- tomography, a cross-domain law, or same-scale domain identity;
- speaker position, microphone pose, or room geometry as machine-observed;
- driver receipt, DAC behavior, transducer motion, or pure airborne causality;
- a physical transfer function or quantitative acoustic law;
- that C1 will discriminate or recur;
- that success at C1 would make PR-018 ready;
- activation or authorization of PR-019;
- a new observer, production change, formal operator, chart, ontology, or
  constraint.

## Artifact standing

- candidates assessed: 5;
- direct PR-018 candidates rejected: 5;
- strongest intermediate candidate: C1, speaker displacement and return with
  microphone fixed;
- PR-016 standing: preserved;
- PR-017 standing: preserved;
- PR-018 standing: preserved as `OPEN` and not ready;
- third option: yes, PR-019 as an open physical-deepening question;
- new constraint: none;
- experiment executed: no;
- hardware touched: no.
