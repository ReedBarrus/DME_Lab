# Project State

Primary fast-entry working memory for DME_Lab.

## Status

Repository scaffold initialized.

Ledger pressure pass completed in `docs/decisions/ledger_pressure_pass_v0.md`.

Synthetic ledger append/replay/integrity harness implemented and tested.

Development distinction registry initialized as provisional, non-authoritative research memory.

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

## Next Smallest Question

Does the coherent bounded field justify extracting an explicitly invoked
foreground persistent coordinator without introducing a daemon, scheduler, or
new identity semantics?

## Contract Surface Status

- projected: signal, provenance, general ingest envelope, generalized reconstruction, generalized exposed projection
- implemented within bounded v0 scope: ingest admission classification
- implemented within bounded v0 scope: admission relationship reconstruction
- implemented within bounded v0 scope: admitted projection
- implemented within bounded v0 scope: read-only non-admitted decision-state companion
- pressure-tested within synthetic v0 scope, with canonical bounded live evidence: append ledger, raw replay
- implemented within bounded repository specimen: capture adapter
- deferred: general OS and Windows capture

## Current Pressure

- keep `record_id`, envelope identity, source sequence, event time, arrival time, and `commit_index` distinct
- test raw replay in canonical commit order before resolved amendment views
- keep the integrity hash boundary explicit: canonical JSON of record content without the `integrity` field
- preserve missingness structurally without explaining it semantically
- JSONL and complete-envelope storage remain provisional after small synthetic tests
- use `docs/distinctions/registry.jsonl` as appendable distinction memory, not as authority over runtime evidence
- keep schema work local to boundaries with executable evidence; ledger record remains the current strongest candidate
- current synthetic runtime records conform to `schemas/ledger_record_v0.schema.json`
- schema validation remains shadow-only and does not regulate ledger append
- runtime can currently produce some records the schema rejects, including non-object envelopes and non-finite JSON values
- ingest/provenance admission is now the likely next pressure frontier
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
- the next pressure should ask whether an explicitly invoked foreground persistent coordinator is justified without adding always-on architecture
- hash chains, manifests, partial-write recovery, and repair remain deferred
- no index exists or is yet justified by lookup pressure
