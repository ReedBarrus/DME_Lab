# Pressure / Resolution Map v0

This is a derived navigational surface over authoritative repository evidence.
It does not establish empirical claims, distinctions, requirements, or
implementation authority. Every resolution must point to evidence that
warrants it. If this map conflicts with committed decisions, traces, tests, or
current repository state, the underlying evidence wins.

The map may expose open and newly reachable pressures, but does not authorize
execution. DME_Lab normally maintains at most one explicitly active
experimental pressure at a time unless a separate need independently justifies
parallel work.

Resolution is basis-relative: `resolution != universal solution`. A pressure
may later be reopened or refined without making its earlier bounded result
wrong. Exact empirical statuses remain in each node; the standing labels below
are navigational shorthand, not a comprehensive state machine.

## Current Navigation

Active pressure: none

Newly reachable / open:

- PR-006 — scoped interval or change observation
- PR-018 — prospective cross-domain prediction

Shelved:

- PR-010 — history-association carrier selection; three realizations remain
  equivalent under current pressure

## How to read a node

- **Pressure** names the unresolved question or wound.
- **Standing** uses the map's small navigational vocabulary.
- **Missing discriminator** states what evidence could not or cannot separate.
- **Resolution so far** preserves the exact bounded result where useful.
- **Residue** records what remains unresolved or unlicensed.
- **Blocked by** and **Unlocks** contain only demonstrated dependencies.
- **Evidence** links to authoritative committed artifacts. This map is never
  evidence for itself.

An em dash means that no relation is established. An `OPEN` node is reachable,
not authorized or active.

## A. Repository historical observation

### PR-001 — Captured endpoints versus complete transformation history

- **Pressure:** Can equivalent captured repository endpoints establish that no
  transformation occurred between observations?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** source-relative evidence from inside an unobserved
  interval.
- **Resolution so far:** `snapshot != complete_transformation_history`. A real
  alpha -> beta -> alpha excursion and true stasis produced equivalent captured
  endpoints at distinct occurrences; an alpha -> beta control left at beta was
  detected.
- **Residue:** the authoritative endpoint history cannot distinguish stasis
  from the hidden round trip and contains no general recurrence model.
- **Blocked by:** —
- **Unlocks:** PR-006, PR-017
- **Evidence:** [decision](docs/decisions/absent_interval_round_trip_pressure_v0.md),
  [trace](traces/absent_interval_round_trip_pressure_v0.json)

### PR-002 — Coordinator lifetime versus historical continuity

- **Pressure:** Does replacing the foreground coordinator break recovery or
  define a new historical session?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** durable session or invocation identity beyond
  ledger history.
- **Resolution so far:** a fresh coordinator reconstructed prior durable
  records and continued capture; `coordinator_lifetime != historical_continuity`.
- **Residue:** process replacement does not prove source freshness, persistent
  participant identity, or complete observation of the interval.
- **Blocked by:** —
- **Unlocks:** PR-003
- **Evidence:** [decision](docs/decisions/foreground_persistent_coordinator_pressure_v0.md),
  [trace](traces/foreground_persistent_coordinator_pressure_v0.json)

### PR-003 — Caller outcome versus durable partial-round state

- **Pressure:** Can authoritative history determine whether a four-record
  capture request returned successfully after zero through four records became
  durable?
- **Standing:** `PARTIAL_RESOLUTION`
- **Missing discriminator:** a durable request, round, completion, or caller
  acknowledgement coordinate.
- **Resolution so far:** every committed prefix remained valid and legible, but
  F4 failure and successful completion could expose the same normalized durable
  composition; `caller_invocation_outcome != durable_history_state`.
- **Residue:** retry after unknown acknowledgement requires a concrete caller
  policy; no atomic-round guarantee was earned.
- **Blocked by:** —
- **Unlocks:** —
- **Evidence:** [decision](docs/decisions/partial_round_completion_pressure_v0.md),
  [trace](traces/partial_round_completion_pressure_v0.json)

### PR-004 — Reconstructed history versus current external configuration

- **Pressure:** Does `current_result()` report current external repository
  state when the source changed without recapture?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** new source observation or an externally supplied
  present and freshness criterion.
- **Resolution so far:** append-free results remained historically correct but
  externally stale after dirty and committed source changes, including after
  coordinator replacement; `current_derived_history != current_external_configuration`.
- **Residue:** evidence age and latest-state selection remain consumer-relative;
  a fresh process is not a fresh observation.
- **Blocked by:** —
- **Unlocks:** PR-006
- **Evidence:** [decision](docs/decisions/stale_current_result_pressure_v0.md),
  [trace](traces/stale_current_result_pressure_v0.json)

### PR-005 — One capture request versus one coherent repository world

- **Pressure:** Do sequential filesystem and Git observations in one requested
  composition describe the same world configuration?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** a shared source clock, atomic capture boundary, or
  durable relation establishing simultaneity/coherence.
- **Resolution so far:** controlled mutations between the real observers
  produced valid, reconstructible compositions from different source-relative
  states; `same_capture_invocation != same_world_configuration`.
- **Residue:** recorded source times do not establish simultaneity, atomicity,
  or a globally coherent present.
- **Blocked by:** —
- **Unlocks:** PR-006
- **Evidence:** [decision](docs/decisions/intra_capture_timing_skew_pressure_v0.md),
  [trace](traces/intra_capture_timing_skew_pressure_v0.json)

### PR-006 — Scoped interval or change observation

- **Pressure:** Would a narrowly selected source-relative change coordinate
  discriminate hidden intervals, externally stale history, or sequential
  source skew under a concrete consumer basis?
- **Standing:** `OPEN`
- **Missing discriminator:** a selected event/change source, scope, clock,
  attribution rule, and consumer question with a woundable failure boundary.
- **Resolution so far:** PR-001, PR-004, and PR-005 partially converge on absent
  source-relative change evidence. That convergence supports this question,
  not a general OS observer.
- **Residue:** change notification would not by itself establish caller
  acknowledgement, cross-source simultaneity, physical realization, semantic
  consequence, or complete transformation history.
- **Blocked by:** concrete consumer need and a separately justified bounded
  observation basis
- **Unlocks:** —
- **Evidence:** [absent interval](docs/decisions/absent_interval_round_trip_pressure_v0.md),
  [stale reconstruction](docs/decisions/stale_current_result_pressure_v0.md),
  [timing skew](docs/decisions/intra_capture_timing_skew_pressure_v0.md)

## B. Source success, admission, and consumer visibility

### PR-007 — Structural admissibility versus source capture success

- **Pressure:** Does admission under the minimum comparator certify that Git
  acquisition succeeded?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** source-specific success semantics at the structural
  comparator boundary.
- **Resolution so far:** a non-Git directory produced three command failures
  and null Git fields in a structurally valid, admitted observation;
  `structural_admissibility != source_capture_success`.
- **Residue:** admission supplies no truth, trust, retry, freshness, or source
  ranking policy.
- **Blocked by:** —
- **Unlocks:** PR-008
- **Evidence:** [decision](docs/decisions/degraded_git_admission_pressure_v0.md),
  [trace](traces/degraded_git_admission_pressure_v0.json)

### PR-008 — Recoverable source-quality evidence versus consumer-visible result

- **Pressure:** Can `current_result()` answer Git acquisition-success questions
  when histories differ but the complete result bodies collide?
- **Standing:** `PARTIAL_RESOLUTION`
- **Missing discriminator:** nested historical observation evidence and its
  associated authoritative ledger.
- **Resolution so far:** opposite healthy/degraded Git histories produced
  identical complete `current_result()` bodies; reconstruction recovered all
  distinguishing fields and errors. The exact standing is
  `astra_pressure_reproduced`; the knowledgeable consumer made no overclaim.
- **Residue:** representation safety and unfamiliar-consumer reliability were
  not established; direct source-quality exposure is not automatically needed.
- **Blocked by:** —
- **Unlocks:** PR-009
- **Evidence:** [decision](docs/decisions/astra_consumer_pressure_adjudication_v0.md),
  [trace](traces/consumer_git_acquisition_pressure_v0.json)

### PR-009 — Detached result versus publicly resolvable history association

- **Pressure:** Can the public repository surface bind a detached
  `current_result()` to the authoritative history containing its referenced
  records?
- **Standing:** `BASIS_INSUFFICIENT`
- **Missing discriminator:** a public binding from the result to its reachable
  originating history.
- **Resolution so far:** record IDs were legitimate only inside an already
  selected ledger; the public canonical ledger was not bound to the specimen.
  Exact standing: `public_history_association_not_resolvable`.
- **Residue:** the evidence is recoverable after the association is supplied,
  but the detached result cannot discover or authenticate that association.
- **Blocked by:** —
- **Unlocks:** PR-010
- **Evidence:** [decision](docs/decisions/public_history_association_adjudication_v0.md)

### PR-010 — History-association carrier selection

- **Pressure:** Which minimum public carrier should bind a detached result to
  its complete original committed prefix?
- **Standing:** `EQUIVALENT_UNDER_CURRENT_PRESSURE`
- **Missing discriminator:** a real transport, diagnostics, incremental
  verification, cross-host, concurrency, or export requirement that separates
  the finalists.
- **Resolution so far:** reachable location plus complete original-prefix
  discrimination was sufficient. A complete digest set, ordered-prefix
  aggregate, and canonical digest-set aggregate were functionally equivalent.
  Exact standing: `history_association_selection_reproduced`.
- **Residue:** no overall necessity ordering, authenticated producer pairing,
  unique current tail, freshness, or source truth was established.
- **Blocked by:** discriminating consumer or contractual need
- **Unlocks:** —
- **Evidence:** [decision](docs/decisions/history_association_selection_adjudication_v0.md)

## C. Acoustic source-coordinate chain

### PR-011 — Microphone discrimination under fixed requested conditions

- **Pressure:** Do repeated microphone observations discriminate the tested C0,
  S1, and S2 command conditions under a frozen low-level basis?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** —
- **Resolution so far:** the replacement primary block found S1 and C0 not
  locally discriminable while S2 separated from both on both channels under
  the predeclared rule.
- **Residue:** physical speaker realization, airborne causality, routing
  mechanism, complete room field, and general acoustics remain unlicensed.
- **Blocked by:** —
- **Unlocks:** PR-012
- **Evidence:** [decision](docs/decisions/acoustic_replication_pressure_v0.md),
  [trace](traces/acoustic_replication_pressure_v0.json)

### PR-012 — Relational recurrence across fresh acquisition process

- **Pressure:** Does the microphone discrimination pattern recur under a new
  trial order and fresh process/backend initialization?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** —
- **Resolution so far:** the complete pairwise verdict pattern recurred while
  measured S2 magnitudes shifted; exact status:
  `relationally_recurrent_under_declared_basis`.
- **Residue:** fresh process does not establish reset or identity of room,
  hardware, driver, routing, or Windows audio state.
- **Blocked by:** PR-011
- **Unlocks:** PR-013
- **Evidence:** [decision](docs/decisions/acoustic_relational_recurrence_pressure_v0.md),
  [trace](traces/acoustic_relational_recurrence_pressure_v0.json)

### PR-013 — Repository/acoustic comparison without an acoustic source witness

- **Pressure:** Did the initial repository and microphone evidence support a
  nontrivial source-domain tomographic correspondence?
- **Standing:** `BLOCKER_REMOVED`
- **Missing discriminator:** originally, an independently observed acoustic
  source-relative coordinate with equality/change established before ingest.
- **Resolution so far:** the initial result was
  `tomographic_structure_not_yet_earned`. PR-015 later supplied the missing
  post-mix coordinate; removing this blocker did not itself solve tomography.
- **Residue:** same-relational-scale transformation matching and prospective
  prediction remained separate questions.
- **Blocked by:** —
- **Unlocks:** PR-014, PR-017
- **Evidence:** [initial comparison](docs/decisions/repository_acoustic_tomographic_comparison_pressure_v0.md),
  [later witness](docs/decisions/wasapi_loopback_witness_validation_v0.md)

#### PR-013 — Resolution history

- **R0 — `BASIS_INSUFFICIENT`:** microphone results lacked an independent
  acoustic source coordinate; the original comparison stopped.
- **R1 — `BLOCKER_REMOVED`:** separate-process WASAPI evidence established a
  bounded post-mix coordinate downstream of command construction.

### PR-014 — Acoustic source-coordinate witness selection

- **Pressure:** What smallest available observer could separate command
  construction from independently observed render-path content at a scale
  comparable to a repository source snapshot?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** at selection time, execution of the proposed
  observer under quiet/control and recurrence rules.
- **Resolution so far:** separate-process WASAPI shared-mode loopback on the
  exact Realtek endpoint was selected as `candidate_requires_new_basis`.
- **Residue:** the candidate boundary was post-mix software observation, not
  driver receipt, electrical output, transducer motion, or airborne sound.
- **Blocked by:** —
- **Unlocks:** PR-015
- **Evidence:** [decision](docs/decisions/acoustic_source_coordinate_witness_selection_pressure_v0.md)

### PR-015 — Independent post-mix endpoint coordinate

- **Pressure:** Can a separate process recurrently observe and discriminate
  content-bearing PCM at the selected render endpoint?
- **Standing:** `BLOCKER_REMOVED`
- **Missing discriminator:** —
- **Resolution so far:** the exact Realtek endpoint and mix format recurred
  across fresh watcher processes; frozen C0, 900 Hz, and 1500 Hz relations were
  discriminated. Exact status: `post_mix_loopback_witness_validated`.
- **Residue:** command construction, render-path observation, and physical
  acoustic realization remain distinct; endpoint PCM proves none of the latter
  physical stages.
- **Blocked by:** PR-014
- **Unlocks:** PR-016, PR-017
- **Evidence:** [decision](docs/decisions/wasapi_loopback_witness_validation_v0.md),
  [trace](traces/wasapi_loopback_witness_validation_v0.json)

### PR-016 — Position-conditioned microphone return recurrence

- **Pressure:** Under a recurrent observed endpoint relation, does A1 -> B ->
  A2 microphone displacement produce a discriminable B realization and return
  recurrence toward A1?
- **Standing:** `BOUNDED_RESOLUTION`
- **Missing discriminator:** —
- **Resolution so far:** the endpoint gate passed, B separated from A1, A2 was
  closer to A1 than B, and all five A2 trials returned toward A1. Exact status:
  `positional_acoustic_transformation_recurrent`.
- **Residue:** pose and geometry were operator-reported; physical mechanism,
  pure airborne causality, transfer-function semantics, and tomography were not
  earned.
- **Blocked by:** PR-015
- **Unlocks:** PR-017
- **Evidence:** [decision](docs/decisions/acoustic_positional_transformation_pressure_v0.md),
  [trace](traces/acoustic_positional_transformation_pressure_v0.json)

## D. Cross-domain structure and prediction

### PR-017 — Return-transformation correspondence across domains

- **Pressure:** After subtracting common DME machinery, does independently
  earned repository and acoustic A -> B -> A evidence support a same-scale
  cross-domain structure?
- **Standing:** `CANDIDATE_SURVIVED`
- **Missing discriminator:** exact scale matching and an antecedently declared
  cross-domain invariant.
- **Resolution so far:** one nontrivial source-domain return candidate survived
  as partial, basis-relative, and retrospective. Exact primary status:
  `tomographic_structure_candidate_prediction_not_earned`; separate prediction
  status: `cross_domain_prediction_not_earned`.
- **Residue:** repository B was control-observed but absent from DME capture;
  acoustic B was paired-observed. Repository return was exact declared-field
  equality; acoustic return was noisy spectral recurrence. Clocks, geometry,
  source/observer scale, and persistence do not transfer.
- **Blocked by:** —
- **Unlocks:** PR-018
- **Evidence:** [re-adjudication](docs/decisions/cross_domain_tomographic_readjudication_v0.md),
  [repository round trip](docs/decisions/absent_interval_round_trip_pressure_v0.md),
  [acoustic return](docs/decisions/acoustic_positional_transformation_pressure_v0.md)

#### PR-017 — Resolution history

- **R0 — `BASIS_INSUFFICIENT`:** the [initial comparison commit](https://github.com/ReedBarrus/DME_Lab/commit/d092aa0cda0ada600b8a4cf4be899497d020172c)
  lacked independent acoustic source evidence and earned no tomographic
  structure.
- **R1 — `BLOCKER_REMOVED`:** the [WASAPI witness commit](https://github.com/ReedBarrus/DME_Lab/commit/a7ea13d45b60f7109dd0abe35bf23fc695ed30c5)
  supplied the anticipated post-mix source coordinate, and the
  [positional commit](https://github.com/ReedBarrus/DME_Lab/commit/01808db0c5f5151df57bb3b6e1e7ae98b4a603ab)
  supplied a new physical return-transformation family.
- **R2 — `CANDIDATE_SURVIVED`:** the [re-adjudication commit](https://github.com/ReedBarrus/DME_Lab/commit/264883fd13ca1c72024a36d8f30645b0da899780)
  found one partial retrospective return correspondence after shared-pipeline
  subtraction.

### PR-018 — Prospective cross-domain prediction

- **Pressure:** Can a relation identified in one domain prospectively constrain
  genuinely unseen evidence in another under a predeclared mapping and failure
  boundary?
- **Standing:** `OPEN`
- **Missing discriminator:** an antecedent mapping; unseen target evidence;
  frozen preserved/changed expectations; a failure separable from
  instrumentation failure; and an informative cross-domain contribution rather
  than relabeled within-domain recurrence.
- **Resolution so far:** prior selection found no admissible prediction, and
  later A1 -> B -> A2 withholding checks were necessarily retrospective. Exact
  current status: `cross_domain_prediction_not_earned`.
- **Residue:** the surviving PR-017 candidate may guide a future question but
  does not authorize, design, or preregister an experiment here.
- **Blocked by:** a predeclared mapping and independently authorized unseen
  target evidence
- **Unlocks:** —
- **Evidence:** [prediction selection](docs/decisions/cross_domain_predictive_transformation_selection_pressure_v0.md),
  [re-adjudication](docs/decisions/cross_domain_tomographic_readjudication_v0.md)

## Operating convention

Reed selects and authorizes an active pressure and supplies operator provenance
where required. ChatGPT and Astra may inspect, dwell, challenge, and propose
map relationships. Codex and other investigators execute bounded pressure and
produce evidence. Repository evidence determines standing; this map only
reflects it.

The map is not a second `PROJECT_STATE.md`, requirements document, ontology
registry, task backlog, planner, dependency engine, causal graph, or truth
store. Its only job is to show where pressure accumulates, what reality resolved
under which basis, what residue remains, and what questions became reachable.
