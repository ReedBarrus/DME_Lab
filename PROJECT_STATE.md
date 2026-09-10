# Project State

Primary fast-entry working memory for DME_Lab.

## Status

Repository scaffold initialized.

Ledger pressure pass completed in `docs/decisions/ledger_pressure_pass_v0.md`.

Synthetic ledger append/replay/integrity harness implemented and tested.

Constraint Registry initialized as provisional, non-authoritative research memory; its historical `D-*` identifiers are preserved.

v0 contract surface mapped in `docs/contracts/README.md`.

Ledger record schema hypothesis added as descriptive, shadow-only JSON Schema.

Bounded repository filesystem observer and separate Git observer implemented.

First live repository baseline captured in `traces/repo_snapshot_v0_baseline.json` and `traces/git_state_v0_baseline.json`.

Second live repository observations captured in `traces/repo_snapshot_v0_post_cleanup.json` and `traces/git_state_v0_post_cleanup.json`.

Repository transition pressure completed in `docs/decisions/repo_transition_pressure_v0.md`.

Bounded v0 ingest admission pressure completed in `docs/decisions/ingest_admission_pressure_v0.md`.

Bounded v0 reconstruction pressure completed in `docs/decisions/reconstruction_pressure_v0.md`.

First bounded live vertical-chain probe completed in `docs/decisions/live_vertical_probe_v0.md`.

Canonical bounded live ingest ledger extraction completed in `docs/decisions/live_ingest_ledger_extraction_v0.md`.

Canonical bounded live ingest ledger continuation completed in `docs/decisions/live_ingest_continuation_v0.md`.

Ledger continuity pressure completed in `docs/decisions/ledger_continuity_pressure_v0.md`.

History extent witness pressure completed in `docs/decisions/history_extent_witness_pressure_v0.md`.

Historical relation pressure completed in `docs/decisions/historical_relation_pressure_v0.md`.

Witness content ablation pressure completed in `docs/decisions/witness_content_ablation_pressure_v0.md`.

Provenance recovery pressure completed in `docs/decisions/provenance_recovery_pressure_v0.md`.

Declarative commitment semantics pressure completed in `docs/decisions/declarative_commitment_semantics_pressure_v0.md`.

Vocabulary identity pressure completed in `docs/decisions/vocabulary_identity_pressure_v0.md`.

Operation identity pressure completed in `docs/decisions/operation_identity_pressure_v0.md`.

Candidate set expansion pressure completed in `docs/decisions/candidate_set_expansion_pressure_v0.md`.

Admissible history discriminator pressure completed in `docs/decisions/admissible_history_discriminator_pressure_v0.md`.

History constraint ablation pressure completed in `docs/decisions/history_constraint_ablation_pressure_v0.md`.

Tie-order invariance pressure completed in `docs/decisions/tie_order_invariance_pressure_v0.md`.

First bounded vertical composition pressure completed in `docs/decisions/vertical_composition_pressure_v0.md`.

Admission disagreement exposure pressure completed in `docs/decisions/admission_disagreement_exposure_pressure_v0.md`.

Persistent observational field pressure completed in `docs/decisions/persistent_observational_field_pressure_v0.md`.

Foreground persistent coordinator pressure completed in `docs/decisions/foreground_persistent_coordinator_pressure_v0.md`.

Partial-round and ambiguous-completion pressure completed in `docs/decisions/partial_round_completion_pressure_v0.md`.

Foreground repository horizontal pressure capstone completed in `docs/decisions/foreground_repository_horizontal_capstone_v0.md`.

Bounded acoustic basis-entry pressure completed in `docs/decisions/acoustic_basis_entry_pressure_v0.md`.

Bounded acoustic replication pressure completed in `docs/decisions/acoustic_replication_pressure_v0.md`.

Bounded acoustic relational-recurrence pressure completed in `docs/decisions/acoustic_relational_recurrence_pressure_v0.md`.

First repository-acoustic tomographic comparison pressure completed in `docs/decisions/repository_acoustic_tomographic_comparison_pressure_v0.md`.

Cross-domain predictive-transformation selection pressure completed in `docs/decisions/cross_domain_predictive_transformation_selection_pressure_v0.md`.

Acoustic source-coordinate witness selection pressure completed in `docs/decisions/acoustic_source_coordinate_witness_selection_pressure_v0.md`.

WASAPI loopback witness validation completed in `docs/decisions/wasapi_loopback_witness_validation_v0.md`.

Acoustic positional transformation pressure completed in `docs/decisions/acoustic_positional_transformation_pressure_v0.md`.

Astra consumer-pressure adjudication and independent reproduction completed in `docs/decisions/astra_consumer_pressure_adjudication_v0.md`.

Public history-association adjudication completed in `docs/decisions/public_history_association_adjudication_v0.md`.

History-association selection adjudication completed in `docs/decisions/history_association_selection_adjudication_v0.md`.

Constraint Registry lineage audit completed in `docs/decisions/constraint_registry_lineage_audit_v0.md`.

Acoustic prediction bridge dwell completed in `docs/decisions/acoustic_prediction_bridge_dwell_v0.md`.

Source-side positional return pressure completed in `docs/decisions/acoustic_source_side_positional_return_pressure_v0.md`.

Independent source-side positional return replication completed in `docs/decisions/acoustic_source_side_positional_return_replication_v1.md`.

## Objective

Build toward deterministic reconstruction of OS-derived event history while preserving provenance.

## Current Primitive Signal

- identity
- time
- type
- payload

## Current Provenance Boundary

Minimum surrounding metadata only:

- envelope identity
- source
- sequence
- integrity
- capture version

## Active Pipeline

```text
OS Source
-> Capture Adapter
-> Raw Observation
-> Ingest Envelope
-> Append Ledger
-> Replay
-> Reconstructed Topology
-> Exposed Projection
```

signal
-> provenance envelope
-> append-only ledger
-> deterministic replay
-> reconstructed topology

next:
navigation
-> comparison
-> projection
-> feedback

## Explicit Deferrals

- Windows capture adapter
- semantic interpretation
- intent inference
- consequence modeling
- feedback systems
- agents
- adaptive behavior
- large formal ontology

## Missing Evidence

- no general OS raw observations captured
- no generalized live ingest admission rules
- no generalized live ingest envelope ledger
- JSONL append ledger pressure-tested mainly against synthetic envelopes, with bounded temporary live candidate-envelope handshakes
- raw replay validated only in canonical commit order
- no generalized projection exposed from evidence

## Current Navigation and Development Standing

`PRESSURE_RESOLUTION_MAP.md` is the current derived navigation surface over
committed evidence. It does not establish the standing it displays.

- Active experimental pressure: none.
- PR-006 remains `OPEN`, blocked by a concrete consumer need and a separately
  justified bounded observation basis.
- PR-018 remains `OPEN`; its exact status remains
  `cross_domain_prediction_not_earned` pending an antecedent mapping and
  independently authorized unseen target evidence.
- No next experimental pressure has been selected.

PR-019 preserves two independently retained specimens:

- R0 — `BASIS_INSUFFICIENT`: the first source-side positional run completed all
  paired observations, but its endpoint source gate failed and B did not pass
  the frozen discrimination threshold.
- R1 — `BOUNDED_RESOLUTION`: the independently selected replication passed the
  endpoint source gate, B discrimination, and all A2 recurrence criteria under
  the unchanged protocol.

The strongest licensed acoustic interpretation is recurrent source-side
positional return under an operator-reported fixed microphone configuration.
Pure airborne causality, exact geometry, transfer-function semantics,
tomography, and prospective cross-domain prediction remain unearned. The
replication forced no new constraint or chart.

The DME Cockpit is authorized as read-only, repository-derived,
observer-facing projection work. This implementation-development decision is
not an active experimental pressure and does not create a Pressure / Resolution
Map node. The Controller remains a `PARKED`, non-authoritative projection and
is not an implementation warrant.

The bounded Cockpit Projection Adapter v0 now deterministically projects the
allowlisted committed repository surfaces into the contracted read-only model.
The Cockpit website is not yet implemented and the Controller remains parked.
This is implementation development, not an active scientific Pressure /
Resolution Map node.

Stage 3 Cockpit adapter pressure preserved nine named source wounds while
exposing one silent-history-loss contract violation and one duplicate-pressure-
ID contract ambiguity. Stage 4A tightened the projection contract so duplicate
current IDs preserve every occurrence, remain uniquely unresolved, and make
relations to that ID visibly ambiguous.

Stage 4B implemented only the bounded remediation licensed by those findings.
Strongly structured R-entry material outside the exact supported Resolution
history section now remains visible as unsupported residue without becoming
valid history. Duplicate current pressure nodes now retain occurrence-local
line provenance and emit `duplicate_pressure_id`; an explicit relation to the
duplicated ID survives with ambiguous unique-target resolution. The Stage 3
decision and trace remain unchanged historical evidence, and the projection
contract was not changed in Stage 4B.

Stage 4C independently re-pressured the original and nearby P8/P11 wounds,
healthy history and identity controls, duplicate relation targets, a combined
wound, and a three-way duplicate. All 12 named specimens survived without
silent loss, winner selection, or healthy-source regression; the exact current
repository projection also remained complete and diagnostic-free.

The next permitted Cockpit step is a deliberately plain, read-only observer UI
specimen over the normalized model, where usability and visual projection can
be pressured. This is not production readiness, general adapter reliability,
authority, or Controller integration. The Controller remains `PARKED`; this is
Cockpit implementation development, not an active scientific Pressure /
Resolution Map node.

## Contract Surface Status

- projected: signal, provenance, general ingest envelope, generalized reconstruction, generalized exposed projection
- implemented within bounded v0 scope: ingest admission classification
- implemented within bounded v0 scope: admission relationship reconstruction
- implemented within bounded v0 scope: admitted projection
- implemented within bounded v0 scope: read-only non-admitted decision-state companion
- implemented within bounded repository scope: explicitly invoked foreground filesystem/Git observation coordinator
- pressure-tested within synthetic v0 scope, with canonical bounded live evidence: append ledger, raw replay
- implemented within bounded repository specimen: capture adapter
- deferred: general OS and Windows capture

## Conserved Pressure Evidence

- keep `record_id`, envelope identity, source sequence, event time, arrival time, and `commit_index` distinct
- test raw replay in canonical commit order before resolved amendment views
- keep the integrity hash boundary explicit: canonical JSON of record content without the `integrity` field
- preserve missingness structurally without explaining it semantically
- JSONL and complete-envelope storage remain provisional after small synthetic tests
- use `docs/constraints/registry.jsonl` as appendable constraint memory, not as authority over runtime evidence
- keep schema work local to boundaries with executable evidence; ledger record remains the current strongest candidate
- current synthetic runtime records conform to `schemas/ledger_record_v0.schema.json`
- schema validation remains shadow-only and does not regulate ledger append
- runtime can currently produce some records the schema rejects, including non-object envelopes and non-finite JSON values
- ingest/provenance admission was a prior pressure frontier
- repository snapshot baseline produced a JSON-domain valid candidate envelope
- temporary ledger handshake for the live candidate passed schema shadow validation, replay, and integrity verification
- filesystem observation and Git observation are separate live evidence regimes
- snapshots expose endpoint structure, not complete transformation history
- second live transition produced 5 filesystem content changes, 0 filesystem adds, 0 filesystem removes, and 2 retrospective Git commits
- multi-source temporary ledger preserved filesystem and Git candidate envelopes without collapsing source-specific provenance
- repeated same-state observations currently reuse filesystem snapshot identity and candidate envelope identity
- metadata-only changes can alter snapshot identity without producing content-changed paths
- filesystem scope and Git scope are overlapping but non-coextensive
- root identity remains ambiguous when v0 observers are invoked with `.`
- bounded admission records now preserve `record_type`, `subject_record_id`, comparator identity/version, comparison result, decision, and decision basis
- rejected and unresolved observations remain replayable in the temporary admission pressure ledger
- admitted projection is derived from replayed observation and admission records, not duplicated into a second physical store
- one preserved observation can have multiple admission records under different comparator versions
- bounded reconstruction now recovers admission relationships from authoritative replayed ledger records
- reconstructed admission relationships preserve record-id paths back to observation provenance
- rebuilding reconstruction and admitted projection from the same replayed records is structurally stable in v0 pressure
- first live vertical probe preserved filesystem and Git observations through admission, replay, reconstruction, admitted projection, and provenance navigation
- capture sequence and ledger commit order are distinct; ledger commit_index records handling order, not source chronology
- canonical bounded live ingest history now lives in `traces/live_ingest_ledger_v0.jsonl`
- the live probe trace now summarizes and references authoritative history rather than owning complete records
- canonical bounded live ingest history continued from 12 to 14 records across reopen/process discontinuity
- the original 12-record prefix remained structurally unchanged after continuation
- per-record integrity verified before and after continuation, but ledger-wide history integrity remains unimplemented
- ledger-wide continuity verification now checks duplicate commit indices, missing internal commit indices, and duplicate record IDs separately from per-record integrity
- canonical live ingest continuity additionally requires start at commit index 1
- a derived experiment trace can witness prior H14 extent without becoming authoritative history
- temporary tail loss of `rec-000014` remains internally valid while failing witnessed extent correspondence
- witness disagreement is preserved as mismatch evidence, not corruption proof or repair authority
- exact extent equality collapses tail loss, extension, and replacement into generic mismatch
- lower-bound extent separates shrinkage from non-shrinkage but does not distinguish extension from replacement
- prefix preservation distinguishes loss, control, extension, and replacement within the bounded append-only pressure
- terminal record digest alone does not commit to interior prefix history in the current non-chained ledger
- ordered record IDs and commit indices do not establish historical content identity
- ordered record digests are the smallest sufficient tested prefix witness projection within the bounded pressure
- historical identity can change without changing current reconstruction/projection shape
- the same fixed H14 ordered-digest carrier produced recovered, mismatched, and unresolved outcomes under different interpretation regimes
- the smallest sufficient tested interpretation includes SHA-256 identity, commitment boundary, exact canonicalization, commit-index ordering, prefix comparison, and candidate recomputation semantics
- commitment semantics plus ordering remained unresolved when the historical prefix relation was withheld
- changed integrity algorithm and boundary labels did not govern current verifier execution
- shared chart referents pressure proto-transition-map investigation without establishing transition maps
- full explicit declarative semantics reproduced the Chart 3 R6 historical outcomes
- the smallest sufficient tested declaration explicitly preserves algorithm, boundary fields, exact canonicalization, ordering field and direction, and prefix relation
- candidate recomputation mode was redundant because recomputation is implied by the bounded evaluator operation
- opaque `current_record` and `current` labels remained unresolved without ambient implementation meaning
- complete but wrong boundary or canonicalization descriptions produced mismatch rather than unresolved
- declaration vocabulary and token interpretation remain ambient in the bounded evaluator
- Chart 5 held S9 structure and the H14 carrier fixed while varying vocabulary interpretation
- eight explicit semantic bindings reproduced the R6/S9 historical outcomes without vocabulary identity metadata
- tokens-only and focused missing mappings remained unresolved without inheriting ambient meaning
- wrong complete relation and field bindings remained executable but changed historical outcomes
- renamed tokens and vocabulary identity preserved outcomes when descriptor mappings remained equivalent
- Chart 5 refines Chart 4 necessity into semantic role, token spelling, and recoverable binding without invalidating Chart 4
- the resulting axis split supports chart-fold pressure, but no folding or transition machinery exists
- operation-descriptor execution and provenance remain ambient in the local evaluator
- Chart 6 held the H14 carrier, S9 declaration, V2a mapping, and historical specimens fixed while changing prefix realizations
- a separately implemented iterative prefix path preserved the R6/S9/V2a historical outcomes
- the same descriptor realized as equality changed the legitimate H16 extension outcome
- H14 control alone could not distinguish prefix from equality; H16 extension did
- one H14-to-H16-extension behavioral case selected prefix among the two tested realizations
- implementation identity was unnecessary when bounded discriminating behavior was conserved
- Chart 6 refines Chart 5 operation binding into descriptor, implementation, and bounded behavior without invalidating Chart 5
- the second axis split earns chart-fold pressure without adding folding machinery
- proto-scheduler grounding strengthened, but preconditions, effects, and admissibility remain absent
- candidate set expansion held the H14 carrier, S9 declaration, V2a vocabulary, B0/B1 cases, and five historical specimens fixed
- ordered subsequence independently accepted H14 control and legitimate H16 extension
- unchanged B1 selected one realization from the original two candidates but matched two of three after expansion
- multiple B1 matches remained unresolved without implementation-name, ordering, or prior-success tie-breaking
- prefix and ordered subsequence produced the same complete outcome pattern over all five existing historical specimens
- Chart 7 exposes a bounded observational-resolution limit without claiming universal behavioral equivalence
- Chart 6 E6 sufficiency is refined as relative to its original candidate set; Chart 6 and D-0037 remain supported
- future operation recognition must preserve ambiguity when multiple executable moves fit available evidence
- admissible-history pressure held the H14 carrier, digest boundary, replay ordering, continuity rules, and canonical history fixed
- duplicate-index and fractional-index insertions preserved all H14 digests and separated prefix from ordered subsequence but failed continuity
- shifting indices 2..14 passed integrity and continuity after rehashing but preserved only one H14 digest
- normal append passed integrity and continuity while preserving H14 as both prefix and ordered subsequence
- no tested admissible construction preserved H14 as an ordered subsequence without also preserving it as a prefix
- under current bounded assumptions and absent a constructed digest collision, dense committed indices 1..14 force additional admissible records after H14
- Chart 8 strengthens Chart 7 from specimen coincidence to a bounded contract-induced observational limit without invalidating Chart 7
- behavioral identity now explicitly depends on an observational basis that includes the admissible history domain; no basis runtime was added
- future navigation must preserve ambiguity when distinguishing pressure lies outside the admissible state domain
- Chart 9 changed one current history rule per regime while keeping H14 source lineage and relation implementations fixed
- relaxing integer-only coordinates, start-at-one, replay ordering, or commit-index participation in the digest boundary independently opened a discriminator
- relaxing gap freedom or record-ID uniqueness alone maintained the prefix/subsequence collapse
- duplicate-index relaxation made equal-index order depend on physical input and remained unresolved without canonical tie semantics
- only the commit-index-boundary variant rederived its H14 carrier; source H14 lineage remained fixed
- commit_index role coupling is supported across commitment identity, ordering, and continuity/admissibility, but not every related constraint contributed
- Chart 9 strengthens Chart 8 by showing that single changes to the admissible basis alter local operation distinguishability
- multiple alternative discrimination regimes were found, but no cost, attention, preference, regime-switching, or scheduler mechanism was added
- tie-order invariance pressure reused the exact Chart 9 C2 construction without changing its evidence
- the two-record commit-index tie has exactly two bounded linearizations under known unequal-index constraints
- both linearizations produced prefix false and ordered-subsequence true
- canonical replay ordering and whole-state C2 admissibility remain unresolved without tie semantics
- both specific relations are resolved by invariance over every bounded compatible linearization
- exact coordinate resolution was unnecessary for these bounded relation consequences; no tie-break was added
- vertical composition used one temporary Git fixture and the real filesystem and Git observers across capture, ingest, append, integrity, continuity, replay, reconstruction, projection, and historical relation
- clean Phase A and legitimate Phase B passed integrity and continuity, reconstructed deterministically, projected reproducibly, and Phase B preserved the Phase-A ordered-digest prefix
- the Phase-B filesystem observation retained both an admitted v0 decision and a rejected event-time-required decision in replay and reconstruction
- current admitted projection kept that subject while exposing only the admitted decision record; projection membership therefore did not establish uncontested admission
- an integrity-valid and continuity-valid prior-provenance mutation remained structurally reconstructable with an unchanged projection while the Phase-A historical relation reported MISMATCHED
- Phase-A-to-Phase-B operation recognition remained UNRESOLVED between prefix and ordered subsequence even though the fixed prefix relation returned RECOVERED
- Chart 10 records five bounded composition scenarios across stable epistemic coordinates without becoming a generalized state model
- D-0041 conserves projection membership as distinct from admission resolution
- no tested contract made an unjustified certainty claim; composition exposed the unsupported inference from projection membership to uncontested admission
- admission disagreement exposure pressure used six deterministic temporary-ledger subjects spanning admitted-only, admitted plus rejected, admitted plus unresolved, mixed, duplicate admitted, and rejected-only exclusion
- all five subjects with at least one admitted decision retained exactly the current any-admitted projection membership; the rejected-only control remained excluded
- C0 projection-only exposed no disagreement and C1 generic disagreement collapsed rejected, unresolved, and mixed evidence
- C2 unique non-admitted decision states was the smallest sufficient tested companion because projection membership already supplies admitted while subject_record_id preserves navigation to full reconstruction evidence
- C3 counts, C4 grouped admission IDs, and C5 full evidence preserved additional multiplicity or identity detail not required by the declared question
- the selected pure derive_non_admitted_decision_states companion was promoted beside admitted projection without changing projection membership, choosing comparator authority, resolving conflict, or writing authoritative state
- Chart 11 records the candidate representation by disagreement-exposure criterion surface
- D-0041 was sufficient for the result; no distinction was added or amended
- multiplicity and direct admission-record identity remain outside the companion until concrete consumer pressure requires them
- one temporary persistent field preserved six filesystem/Git observation rounds through 24 append-only records, including a disk reopen after record 20
- repeated filesystem configurations reused structural, envelope, and signal identity while distinct capture timestamps and ledger coordinates preserved occurrence
- equivalent Git configurations retained fresh timestamp-derived observation, envelope, and signal identities; the comparison surface remained experiment-local
- O4 to O5 preserved filesystem structural identity while Git HEAD/status changed, conserving overlapping sources without collapsing them
- every round passed integrity, continuity, replay, reconstruction, projection, companion, source-separation, and O1 ordered-digest prefix checks
- disk history alone reconstructed 10 observations and projections after O5 before O6 continued the ledger to 24 records
- temporal depth did not require admission multiplicity or direct admission-record IDs in the Chart 11 companion
- Chart 12 records the bounded six-round field across stable coordinates without becoming a generalized state model
- D-0011, D-0016, D-0030, and D-0041 were sufficient; no distinction was added or amended
- an externally controlled Phase-C trajectory drove five foreground captures through clean alpha, repeated alpha, dirty beta, committed beta, and dirty gamma after coordinator absence
- the foreground coordinator retained only root, ledger path, and process-local close state; it cached no history-derived state or round counter
- a fresh coordinator recovered 16 records, 8 observations, 8 admission relations, 8 projection subjects, and 8 companion rows from disk before continuing to 20 records
- world mutation during coordinator absence appended no history and was represented afterward only as a changed observed endpoint with unavailable intermediate transformation history
- the small repository-specific ForegroundRepositoryObservationCoordinator boundary was promoted as foreground, explicitly invoked, single-writer, and non-autonomous
- Chart 13 records caller-selected captures across external world action, coordinator lifetime, source-relative configuration, ledger range, reconstruction, and prefix
- D-0042 records coordinator_lifetime != historical_continuity without asserting persistent participant identity
- F0 through F4 deterministically failed after zero through four new durable records over independent equal-world four-record prefixes
- every partial history remained integrity-valid, continuity-valid, replayable, reconstructible, and legible at the committed record/relation level
- F1 retained one unadmitted filesystem observation; F2 retained filesystem and Git observations without new admissions; F3 additionally retained one filesystem admission
- authoritative history contained no round, request, completion, or caller-acknowledgement coordinate, so invocation completion remained UNRESOLVED for F0 through F4 and successful control
- F4 and successful control had different caller outcomes but equal normalized durable composition surfaces; independent occurrence timestamps and digests differed without encoding acknowledgement
- a retry after F4 appended another valid same-configuration observation pair and admissions, but history could not distinguish retry from intentional repetition
- D-0042 remained supported without amendment because fresh coordinators recovered every durably committed record under mid-operation termination
- the promoted foreground coordinator remains scoped to four independently committed records and provides no atomic-round or durable-acknowledgement guarantee
- Chart 14 records fault boundary against durable shape, caller outcome, integrity, continuity, reconstruction, projection, and completion inference
- D-0043 records caller_invocation_outcome != durable_history_state
- retry policy after unknown acknowledgement remains unresolved until a concrete caller requires it
- C0, S1, S2, and C1 isolated sequential filesystem/Git acquisition across stable alpha, dirty skew, committed skew, and settled beta
- deterministic experiment-local interception mutated the fixture only after the real filesystem observer returned and before the real Git observer ran; production capture code remained unchanged
- S1 returned filesystem-alpha plus later dirty Git, while S2 returned filesystem-alpha plus later clean committed-beta; both compositions remained integrity-valid, continuity-valid, reconstructible, and projectable
- filesystem start/finish and Git observed-at fields survived fresh recovery and preserved their recorded timestamp relation, but Git supplied no complete interval and the evidence established neither simultaneity nor a shared world configuration
- the immediate non-authoritative return grouped both captures as products of one requested composition; fresh authoritative history retained no round, request, invocation, or group identity
- projection preserved both admitted observations as separate historical subjects and made no current coherent repository-state claim
- Chart 15 records source-relative configuration, external mutation, structural health, process-local grouping, durable grouping, and world-configuration justification across the four specimens
- D-0044 records same_capture_invocation != same_world_configuration
- C0, S1, S2, R1, and F1 isolated read-only current_result semantics across stable alpha, dirty beta, committed beta, process replacement, and explicit recapture
- every current_result call preserved ledger SHA, record count, commit indices, ordered digests, reconstruction, projection, and companion while acquiring no source evidence
- S1 and S2 reproduced clean-alpha history exactly while external control observed dirty or committed beta; the results were historically correct, structurally healthy, and externally stale
- R1 showed that a fresh coordinator reconstructs the same stale historical surface, so process freshness does not supply source freshness
- only F1 capture_round advanced history from 4 to 8 records and from 2 to 4 projected subjects; its following current_result was again append-free
- observation timestamps were absent from the current_result surface but recoverable through authoritative reconstruction; evidence age requires an external now and clock assumptions and cannot establish unchanged sources
- the production docstring already scopes current_result to derived state without append or capture, so no external-freshness overclaim, rename, or production defect was introduced
- Chart 16 records last captured configuration, external configuration at read, byte conservation, derivation, coordinator lifetime, and source-freshness inference
- D-0045 records current_derived_history != current_external_configuration
- D-0042 through D-0044 remain supported without amendment
- C0, S1, and S2 compared true alpha stasis, an unobserved alpha-to-beta-to-alpha excursion, and a visible alpha-to-beta endpoint change
- S1 restored alpha content and original mtime plus clean Git HEAD, branch, status, and capture-error state before its second real capture
- C0 and S1 produced equivalent filesystem snapshot identities and Git configuration surfaces at distinct observation occurrences despite different control-known interval paths
- record IDs, commit indices, capture timestamps, and digests distinguished occurrences but did not establish stasis, transformation, or recurrence
- S2 changed filesystem snapshot identity and Git status, confirming that both observers detect an ordinary endpoint difference while leaving intermediate path unresolved
- every specimen preserved eight valid contiguous records, four reconstructed observations, four projected subjects, four Chart 11 companion rows, and separate source provenance
- fresh coordinators recovered the complete endpoint histories append-free from root plus ledger path without driver-path knowledge
- the hidden excursion was never observed, so its absence is an endpoint-observability boundary rather than corruption or loss of captured evidence
- Chart 17 records control-known path, source endpoint relations, occurrence, reconstruction, projection, and intervening-transformation inference
- D-0012 snapshot != complete_transformation_history was sufficient; no distinction was added or amended
- D-0016 and D-0042 through D-0045 remain supported
- C0 and S1 compared a healthy clean Git repository with an ordinary filesystem directory lacking .git through the real promoted foreground path
- S1 returned a normal Git observation with three capture_errors and null head_sha, branch, and status_porcelain while filesystem capture remained healthy
- the degraded Git ingest envelope preserved errors in provenance and raw signal payload and passed COMPARATOR_V0 minimum structural validation
- both healthy and degraded Git observations were admitted with basis comparison valid under comparator and entered the any-admitted projection
- COMPARATOR_V0 checks minimum record, observation-envelope, and signal shape but does not inspect Git success fields or capture_errors
- degraded errors remained recoverable in ledger/replay and reconstruction nested observation provenance and signal payload, including after fresh coordinator recovery
- capture_errors were not copied into outer coordinator provenance and were not directly exposed by projection, Chart 11 companion, or current_result
- the projection boundary retained subject navigation to authoritative reconstruction and did not erase degraded-source evidence from history
- both specimens remained integrity-valid, continuity-valid, reconstructible, projectable, companion-reproducible, and source-separated
- Chart 18 records acquisition quality, error carriage, structural schema, comparator decision, reconstruction recovery, projection exposure, and companion exposure
- D-0046 records structural_admissibility != source_capture_success
- D-0012, D-0016, and D-0042 through D-0045 remain supported
- the foreground capstone left source-quality companion data, trust policy, retry, confidence, and source ranking blocked on a concrete consumer
- horizontal capstone composition found no conflict among Charts 11-18 and invalidated no prior finding
- D-0012, D-0016, D-0023, D-0025 through D-0027, and D-0041 through D-0046 remain independently necessary on their scoped evidence
- the current pressure map licenses source-relative historical recovery and navigation, not caller acknowledgement, durable invocation grouping, shared-world capture, external freshness, complete interval history, source success, or admission resolution
- remaining foreground questions require a concrete consumer, an independent contradiction, a qualitatively new observation basis, or a separate durability/concurrency regime
- no Chart 19, D-0047, production change, atlas machinery, or next implementation was earned; the foreground semantic surface is locally saturated and frozen for dwell
- one open-loop WinMM acoustic pass captured C0 no-playback, S1 left-lane, and S2 right-lane trials through a Realtek room-stereo command and XIBERIA headset microphone, as operator-identified device roles
- the 180 ms chirp used 0.02 full scale (about -33.98 dBFS); no gain increase, feedback, jack movement, or further emission occurred, and the operator reported hearing no playback
- S1 microphone-window RMS remained near C0 while S2 measured about 2.029 PCM RMS above C0 on both captured channels; one trial per command and no threshold license only the numerical local-response comparison
- physical speaker realization, emitted waveform, command-response causality, complete room field, and channel health remain unobserved or unresolved
- raw PCM was ephemeral and discarded after SHA-256 plus deterministic measurement derivation; ingest, ledger, and reconstruction preserve the selected metadata basis, while projection retains only navigation coordinates
- three acoustic observation envelopes passed COMPARATOR_V0 and survived a six-record temporary ledger, replay, reconstruction, projection, and companion without repository-specific payload assumptions or semantic inflation
- the acoustic result forces no production change, chart, or registry distinction; D-0046 and D-0020 are only bounded post-hoc correspondences, not preselected templates or universal tomography
- no next domain is selected; replicated conservative range-finding with an explicit discrimination criterion remains a possible question rather than an authorized next implementation
- acoustic replication predeclared `delta_rms = response_window_rms - that_trial_pre_roll_rms`, an interleaved seed-20260903 order, and a two-part non-overlap plus median/MAD rule before acquisition
- an initial 15-capture block was retained but excluded from primary adjudication after the operator reported likely overlapping video audio; a separately authorized 15-capture replacement used the same frozen order, low level, devices, and rule
- in the replacement block S1 and C0 overlapped and were not locally discriminable, while S2 was locally discriminable from both C0 and S1 on both captured microphone channels; no MAD was zero
- the result licenses replicated local sampled-microphone measurement differences under the declared command basis, not speaker realization, airborne causality, channel health, routing mechanism, synchronized timing, or complete room-field state
- 15 replacement occurrences remained distinct through 15 observations, 15 admissions, a 30-record temporary ledger, replay, reconstruction, projection, and companion; projection preserved navigation but did not directly expose command or measurement fields
- raw PCM remained ephemeral in both blocks; hashes and deterministic measurements survived in raw and reconstructed nested observations, while waveform morphology was irrecoverably discarded
- replication forced no new distinction or chart; D-0016 and D-0020 are stronger bounded post-hoc correspondences, and the registry remains unchanged through D-0046
- no next experiment is authorized; the smallest residue is unexplained S2 magnitude variation within and across runs under otherwise fixed requested configuration
- a fresh-process acoustic recurrence block froze seed 20260910, a new 15-trial interleaved order, the unchanged delta/range/MAD rule, and the complete prior verdict pattern before device enumeration
- the new block independently reproduced S1-vs-C0 non-discrimination and S2 separation from both C0 and S1 on both microphone channels, satisfying `relationally_recurrent_under_declared_basis`
- S2 medians shifted by -0.066660 and -0.060891 PCM RMS while all three pairwise verdicts survived; numerical realization changed without changing the declared relational structure
- the fresh boundary establishes a new Python process, WinMM backend instance, and per-trial handle lifecycle only; it does not establish reset or identity of room, hardware, driver, routing, or Windows audio state
- all 15 recurrence observations remained distinct through admission, a temporary 30-record ledger, replay, reconstruction, projection, and companion; no occurrence/configuration collapse or new identity ambiguity appeared
- no acoustic recurrence distinction or chart was added; D-0016, D-0020, and D-0042 are bounded post-hoc correspondences only, and the registry remains unchanged through D-0046
- no consumer decision or next experiment is authorized by recurrence; physical mechanism and magnitude variation remain intentionally unexplained
- the first repository-acoustic comparison separated source-domain, shared-pipeline, and interpretation correspondences rather than promoting common pipeline shape into source tomography
- configuration/condition descriptor versus occurrence and realization versus relational signature are partial correspondences only; their source scales and transformations do not fully match
- coordinator replacement with durable recovery versus fresh acoustic acquisition with a recurring verdict is a refuted correspondence because old-record continuity is not new-observation recurrence
- observation-envelope traversal through admission, ledger, replay, reconstruction, and projection is a supported local pipeline correspondence inherited by construction, not a source-domain map
- D-0046 is only a partial acoustic correspondence because degraded Git has independent acquisition-failure evidence while acoustic speaker realization lacks independent ground truth
- the comparison preserves explicit repository and acoustic residue and returns `tomographic_structure_not_yet_earned`
- no new distinction, chart, comparison runtime, source, audio actuation, or production machinery was added; the registry remains unchanged through D-0046
- horizontal judgment is `freeze_comparison_and_seek_new_transformation`; no transformation or next experiment is presently justified or authorized
- prediction-first pressure rejected Candidate A's distinct-occurrence expectation as generic identity handling rather than novel source-domain prediction
- Candidate C supplied no declared preservation/change pattern for a qualitatively new acoustic transformation; another process restart would add recurrence evidence but not cross-domain predictive novelty
- Candidate E's admission expectation is entailed by COMPARATOR_V0 and disappears under pipeline subtraction, while no independent acoustic actuation-success coordinate exists
- spatial displacement, orientation, distance, new command, richer measurement, repository-native transformation, and another observation basis were compared but none had an evidence-derived falsifiable signature
- the selected result is `no_cross_domain_prediction_yet_earned`; microphone movement and all other next transformations remain unjustified
- no distinction, trace, script, test, chart, audio action, source, or production machinery was added; comparison is frozen pending matched pre-ingest source-domain evidence
- separate-process WASAPI shared-mode loopback validation selected the exact active `Speakers (Realtek High Definition Audio)` endpoint and observed its 48 kHz, stereo, 32-bit-float post-mix format
- an idle no-render gate yielded no packets; an all-zero render activation yielded actual `IAudioCaptureClient` packets before any tonal trial, so packet availability was established without using emitter success as the witness
- the frozen primary used five C0, five 900 Hz S1, and five 1500 Hz S2 trials at 0.002 full scale; all trials were retained and no device, gain, or hardware setting was changed
- all ten commanded trials contained content-bearing endpoint PCM; S1 and S2 passed every predeclared spectral-dominance criterion, while all five C0 intervals retained explicit packet absence and imitated neither command relation
- nineteen unique external watcher processes covered gate, preflight, and primary captures; every primary process reacquired the same endpoint ID and mix format with zero acquisition failures
- watcher processes received only endpoint ID, duration, and artifact paths; condition and emitter metadata were joined after acquisition, preserving command construction != render-path observation != physical realization
- the bounded result is `post_mix_loopback_witness_validated`; it establishes a post-mix render-endpoint coordinate, not driver receipt, DAC output, speaker actuation, airborne sound, microphone causality, or tomography
- raw PCM remained ephemeral after per-capture hashing and measurement; the canonical ledger remained byte-identical and no distinction, chart, production source, adapter, or generalized observer was added
- positional pressure froze A and B before primary evidence, then retained five paired endpoint/microphone observations at A1, five after an operator-reported lateral displacement by approximately the microphone's own length, and five after operator-confirmed return to A2
- three exploratory A-position preflights at 0.005, 0.010, and 0.020 full scale were retained separately; only the existing 0.020 ceiling produced a sufficient supported-band microphone response, and no higher level was attempted
- all 15 primary Realtek loopback captures used unique external watcher processes and recurrent endpoint shape; all 15 XIBERIA buffers had distinct hashes and zero capture errors
- endpoint shape varied by at most approximately `7.78e-15` dB and endpoint mean level by 0.516145 dB, satisfying the frozen source-stability gate before positional attribution
- A1-to-B response-centroid distance was 22.603324 dB against a frozen 9.458592 dB threshold; A1-to-A2 was 3.824222 dB, A2-to-B was 24.203247 dB, and all five A2 trials were individually closer to A1
- the bounded result is `positional_acoustic_transformation_recurrent`; it licenses a recurrent position-conditioned sampled-microphone realization under the declared operator intervention, not a measured geometry, physical transfer function, pure airborne mechanism, general acoustic law, or tomography
- no new distinction, chart, production promotion, canonical-history mutation, or next physical transformation was earned
- hardware-free cross-domain re-adjudication confirmed that separate-process WASAPI endpoint evidence plus positional A1-to-B-to-A2 recurrence removes the specific acoustic source-coordinate blocker in the earlier repository-acoustic comparison
- the pre-existing absent-interval pressure supplies a prior repository alpha-to-beta-to-alpha relation with exact endpoint equivalence at distinct occurrences, while the acoustic pressure supplies a stable observed endpoint, discriminable B microphone realization, and metric return toward A1
- after subtracting common capture, envelope, ledger/trace, reconstruction, and analysis machinery, one nontrivial return-transformation candidate survives as a partial, basis-relative retrospective correspondence
- the match remains inexact: repository B was control-observed but absent from DME capture, acoustic B was directly paired-observed; repository return is exact declared-field equality, acoustic return is noisy spectral recurrence; source/observer scale, clocks, geometry, and persistence differ
- a post-hoc withholding check classified both remaining A1 trials, both remaining B trials, and all five A2 trials toward the expected first-three-trial centroid, supporting robustness without creating prospective evidence
- no prior artifact predicted the positional consequence; prior prediction selection explicitly declined microphone displacement for lack of a directional preserved/changed signature
- current statuses are `tomographic_structure_candidate_prediction_not_earned` and `cross_domain_prediction_not_earned`
- the comparative geometry changed qualitatively but boundedly: the anticipated coordinate was supplied, a new independent observer relation and return-transformation family were introduced, and one serious retrospective candidate replaced the earlier no-matched-candidate standing
- no new distinction, chart, trace, test, source, observer, production change, runtime ontology, canonical-history mutation, or next experiment was earned
- hash chains, manifests, partial-write recovery, and repair remain deferred
- no index exists or is yet justified by lookup pressure
