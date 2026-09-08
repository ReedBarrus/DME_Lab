# Foreground Repository Horizontal Pressure Capstone v0

## Scope and Boundary

This capstone composes the earned foreground repository-observation pressures
without introducing another specimen merely to seek a new wound. It asks for
the smallest coherent account of what the current bounded regime can and
cannot legitimately know across:

```text
source observation
-> ingest and admission
-> append-only ledger and replay
-> reconstruction
-> admitted projection and read-only companion
-> consumer inference
```

Starting state was clean `main` at
`a214751d1afd95daa985d7a886086a756a401005`
(`Final-for-now Goblin Wound`). The degraded-Git pressure was already committed,
so the required lineage boundary was present. Baseline composed targeted tests
passed 239/239 and the full suite passed 442/442.

This pass did not modify production code, canonical history, old decision
records, the distinction registry, or `docs/projection/Persistent_Ecology.md`.
It added no service, watcher, scheduler, global-state object, source-health
policy, temporal ontology, atlas runtime, consequence engine, or metabolics.

## Evidence Basis

The capstone treats executable traces and tests for Charts 11 through 18,
their decision records, the current contracts, and the distinction registry as
its evidence. The pressure axes are:

- projection disagreement exposure;
- repeated observation and persistence;
- coordinator replacement and historical continuity;
- partial commitment and ambiguous caller completion;
- sequential cross-source timing skew;
- historical derivation versus external freshness;
- equivalent endpoints around an unobserved interval;
- degraded source acquisition versus structural admission;
- reconstruction versus projection exposure;
- source-relative configuration versus observation occurrence.

The simultaneous targeted run included admission reconstruction, vertical
composition, admission-disagreement exposure, and every Chart 12 through Chart
18 foreground pressure module. Its success establishes regression compatibility
among the local findings; it does not turn them into a global state model.

## Claim and Evidence Map

| Claim under pressure | Standing | Evidence basis | Strongest licensed inference | Strongest forbidden inference | Horizon |
| --- | --- | --- | --- | --- | --- |
| Durable records survive coordinator replacement | supported within the bounded single-writer coordinator | Chart 13 / D-0042 | a fresh coordinator recovers every durably committed record and rebuilds the derived surfaces from the ledger | the original process, session, or invocation remained alive or completed | durability/concurrency remains separate |
| A successful-looking durable composition proves caller acknowledgement | refuted | Chart 14 / D-0043 | the expected record and relationship shape became durable | the caller received a successful return | concrete caller/request policy |
| Adjacent records establish one invocation group | not represented; the implication is unsupported | Charts 14-15 / D-0043 and D-0044 | record types, references, commit order, and source provenance are recoverable | observation/observation/admission/admission adjacency is a durable round or request identity | concrete grouping consumer |
| Filesystem and Git captures returned by one call share one world configuration | refuted | Chart 15 / D-0044 | one immediate return contains products of one sequential composition | simultaneous acquisition or one coherent repository snapshot | temporal composition only if demanded |
| `current_result()` reports the current external repository | refuted | Chart 16 / D-0045 | it is the current append-free derivation of authoritative recorded history | the external source still equals its recorded endpoint | concrete freshness/navigation demand |
| Equivalent observed endpoints imply nothing happened between them | refuted as an implication; interval path unresolved | Chart 17 / D-0012 | two source-relative endpoints are equivalent at distinct observations | the unobserved interval was static | denser or qualitatively different observation basis |
| Equivalent source configuration means the same observation occurrence | refuted | Charts 12 and 17 / D-0016 | a configuration may recur while ledger coordinates preserve distinct observations | repeated structural identity collapses occurrence identity | no current horizon; existing coordinates suffice |
| An admitted Git observation means Git acquisition succeeded | refuted | Chart 18 / D-0046 | the recorded observation was structurally valid under the named comparator | HEAD, branch, or status was successfully acquired or trusted | concrete source-quality consumer |
| `COMPARATOR_V0` certifies minimum structural admissibility | supported and narrowly scoped | ingest implementation and Chart 18 | required record, observation-envelope, and signal shape passed `ingest_candidate_envelope_minimum_v0` | semantic truth, source success, freshness, completeness, or trust | a different comparator only for a real requirement |
| Projection membership establishes admission resolution | refuted | Charts 10-11 / D-0041 | at least one recorded admission decision is `admitted` under the current any-admitted rule | no opposed, unresolved, or duplicate admission evidence exists | reconstruction navigation; companion already exposes unique non-admitted states |
| Git `capture_errors` remain recoverable | supported through authoritative replay and reconstruction; direct exposure is surface-dependent | Chart 18 / D-0046 | nested observation provenance and signal payload recover the complete error list after coordinator replacement | projection, companion, or `current_result()` directly communicates acquisition quality | concrete projection consumer |
| The foreground regime produces a coherent global repository snapshot | not established; contradicted as a general inference by timing-skew evidence | Chart 15 / D-0044 | it preserves separate source-relative observations and their recorded times | the pair denotes one atomic, simultaneous, or globally coherent world state | separate temporal/concurrency regime |

No prior finding was invalidated. Later pressures narrowed tempting readings of
earlier success: structural success did not become completion, admission did
not become source success, persistence did not become session identity,
projection did not become resolution, and deterministic derivation did not
become external freshness.

## Composition Audit

The registry distinctions compose without contradiction:

| Boundary | Registry basis | Composition result | Status after later pressure |
| --- | --- | --- | --- |
| observation != admission | D-0023 and D-0025 (`persisted_observation != admission_classification`; `observation_identity != admission_classification`) | observations persist before and independently of one or more admission decisions | independently necessary; partial and degraded histories rely on it |
| admission != projection | D-0027 and D-0041 | reconstruction retains all admission relations while projection applies the any-admitted selection rule | independently necessary; Chart 11 exposes disagreement without resolving it |
| replay != reconstruction | D-0026 (`authoritative_history != reconstructed_representation`) | replay remains authoritative record history; reconstruction is a deterministic derived relation surface | independently necessary; recovery navigation depends on the boundary |
| reconstruction != projection | D-0027 | reconstruction preserves observations and all admissions; projection exposes selected members and identifiers | independently necessary; degraded-source detail crosses only the reconstruction surface |
| snapshot != complete transformation history | D-0012 | endpoint evidence cannot supply an unobserved interval path | independently necessary; Chart 17 strengthens rather than subsumes it |
| structural state identity != observation occurrence identity | D-0016 | repeated configurations retain distinct durable observation coordinates | independently necessary; not reducible to interval ignorance |
| projection membership != admission resolution | D-0041 | membership plus the companion can expose states without choosing authority | independently necessary; not subsumed by D-0046 source quality |
| coordinator lifetime != historical continuity | D-0042 | disk history survives process-local coordinator death | independently necessary; D-0043 narrows what continuity cannot prove |
| caller invocation outcome != durable history state | D-0043 | complete-looking records do not encode acknowledgement | independently necessary; distinct from grouping and atomicity |
| same capture invocation != same world configuration | D-0044 | sequential source captures can be individually healthy yet temporally heterogeneous | independently necessary; distinct from external freshness after capture |
| current derived history != current external configuration | D-0045 | append-free derivation can remain historically correct and externally stale | independently necessary; distinct from an unobserved path between two captures |
| structural admissibility != source capture success | D-0046 | failed acquisition evidence can be well formed, admitted, and projectable | independently necessary; distinct from admission disagreement |

None of D-0012, D-0016, or D-0041 through D-0046 is redundant. Attractive
phrases such as `same endpoint != no intervening transformation` are useful
readings of the existing D-0012/D-0016 composition, not independently forced
registry entries. Likewise, `admitted Git != successful Git` is the executed
Git instance of D-0046, not a second distinction.

## Consumer Inference Surface

| Surface | Strongest legitimate inference | Tempting illegitimate inference |
| --- | --- | --- |
| `capture_round()` | one explicit foreground call sequentially captured two source-relative observations, appended four independently committed records, and returned current derivations | atomic round, durable grouping, caller acknowledgement, simultaneity, or a coherent global snapshot |
| `current_result()` | current deterministic, append-free derivation of the ledger presently supplied to the coordinator | current external repository state or freshness |
| admitted projection | each row has at least one admitted decision and retains identifiers for evidence navigation | uncontested admission, source success, complete payload exposure, or latest-state status |
| Chart 11 companion | for each projected subject, the unique recorded non-admitted decision states are exposed without adjudication | multiplicity, comparator priority, conflict resolution, or source-quality state |
| reconstruction | observations and all admission relationships are deterministically derived with paths to authoritative records and nested source evidence | authoritative history, external truth, complete event history, operation completion, or present-world state |

## Authoritative Ignorance Surface

The unavailable claims have different causes and must not be collapsed into one
generic unknown:

| Unavailable claim | Why unavailable | What remains known |
| --- | --- | --- |
| whether a fully durable invocation was acknowledged | not durably represented | exact committed records and relationships; driver-only caller outcome in the experiment |
| whether adjacent records came from one invocation after recovery | not durably represented | record identities, references, sources, and commit ordering |
| whether sequential filesystem and Git captures shared one world state | basis insufficient and no complete common temporal coordinate | separate payloads and their source-relative observation times |
| whether the external repository still equals recorded evidence | not observed by `current_result()`; freshness policy absent | current derivation of the last recorded evidence |
| what occurred in an unobserved interval | not observed | endpoint configurations and distinct observation occurrences |
| whether structurally admitted Git acquisition succeeded | outside `COMPARATOR_V0` semantics | comparator identity, structural decision, null fields, and recoverable errors |
| whether projected admission is uncontested | not exposed by projection alone | subject navigation; unique opposed states in the companion; full evidence in reconstruction |
| whether source quality must appear directly in projection | consumer requirement absent | full source-quality evidence remains recoverable through reconstruction |
| whether a round is atomic under torn writes or concurrency | outside the tested durability basis | behavior under deterministic exceptions between complete record appends |

`capture_errors` illustrate the surface boundary precisely. They are directly
visible in the raw Git observation, ingest-envelope provenance, and ingest
signal payload. The ledger retains both nested locations. Reconstruction
retains the nested envelope provenance and payload, although its outer
provenance does not copy the errors. The admitted projection, Chart 11
companion, and fresh `current_result()` do not directly expose them. Navigation
from their subject identifiers to authoritative reconstruction recovers them;
the information ceases to be directly visible at projection, not to exist in
history.

## Compression Observations

### Temporal-coherence family

D-0012, D-0016, and D-0042 through D-0045 form a useful pressure family around
occurrence, continuity, completion, cross-source timing, freshness, and absent
intervals. The family supports a compression hypothesis: temporal coherence is
relative to the evidence basis and requested inference. It does not yet support
one temporal-coherence object. Each distinction is still independently needed
because its missing claim fails for a different reason: absent observation,
absent durable representation, sequential acquisition, or lack of a new source
read.

### Epistemic-qualification family

Integrity, continuity, schema shape, named-comparator admission,
reconstruction, projection membership, companion exposure, and source success
are locally valid qualification regimes. Existing evidence supports preserving
explicit translations among them while forbidding certainty from silently
moving upward. It does not support a generalized trust, confidence, or
epistemic-coherence model.

## Chart Overlap and Iterative Gluing

The earned charts overlap through concrete identifiers and recoverable
relations rather than one global coordinate system:

```text
raw source evidence
-> ingest envelope copied into an observation record
-> authoritative record ID and subject relation
-> reconstruction observation and all admissions
-> projection subject/admission IDs
-> optional companion states
-> navigation back to reconstruction
```

Filesystem and Git charts overlap at a caller-selected composition and ledger
history, but their scopes, payloads, and times remain non-coextensive. The
degraded-Git chain demonstrates a partial translation: failed acquisition
becomes well-formed failure evidence, then structurally admitted evidence, then
a projected historical subject. There is no earned translation from projection
membership to successful current Git knowledge.

Existing evidence therefore supports iterative gluing only as a dwell
hypothesis: a later chart may compose with an already related surface where an
explicit identifier, conserved payload, or tested relation supplies the
translation. The result need not and currently does not become a complete
global state. This is a useful projection for future work, but no Atlas,
ChartGraph, translation engine, or topology is earned.

## Horizontal Saturation Judgment

Judgment:

```text
freeze_surface_and_dwell
```

Evidence that would justify continuing horizontal pressure was sought:

- no production claim on this surface remains known to overstate its evidence;
- no two earned distinctions conflict under composition;
- later pressure invalidated no earlier result;
- projection omits source-quality detail, but no current consumer requires it
  directly and navigation preserves recoverability;
- retry, acknowledgement, and grouping questions require a concrete caller;
- freshness selection requires an actual navigation demand;
- atomic rounds, torn writes, and concurrency belong to another durability
  regime.

Evidence for stopping is stronger:

- Charts 11 through 18 and their companion/reconstruction tests survive
  simultaneously;
- new specimens have been absorbed by existing distinctions where appropriate;
- the remaining questions require hypothetical consumers, qualitatively new
  observation, or a different durability/concurrency basis;
- further variants on this repository surface would increasingly restage known
  failures without new discriminating power.

The foreground repository-observation semantic surface is therefore locally
saturated and frozen for dwell. Reopen it only for a concrete consumer demand,
an independent contradiction, or a qualitatively new observation basis.

## Dwell / Compression Candidates

These are non-authoritative hypotheses, not registry entries or architecture:

- H1: freshness may be an inference-relative temporal relation among recorded
  evidence, a supplied present, and a consumer criterion.
- H2: epistemic coherence may arise from preserving warranted translations
  among heterogeneous local qualification regimes rather than assigning one
  global confidence value.
- H3: partial local charts may compose iteratively through earned translation
  maps without requiring a complete global state.
- H4: uncertainty may remain a navigational coordinate rather than a defect
  that every downstream surface must eliminate.
- H5: future metabolics might concern allocating finite observation or
  attention capacity toward consequence-relevant uncertainty.

The last hypothesis remains especially distant: no consequence space,
capacity-allocation regime, or economics is implemented or licensed here.

## Deferred and Consumer-Dependent Horizons

Consumer-dependent:

- retry after unknown acknowledgement: requires a concrete caller/request
  policy;
- direct projection exposure of source quality: requires a concrete projection
  consumer;
- source age or latest-state selection: requires an actual freshness/navigation
  demand;
- durable invocation grouping: requires a consumer that cannot use record-level
  history.

Separate durability/concurrency regime:

- atomic multi-record rounds;
- torn JSONL writes and recovery;
- concurrent writers, locking, and ordering;
- fsync, acknowledgement, and crash-boundary policy.

Still unearned:

- polling, watchers, and autonomous observation;
- recurrence or hysteresis operators;
- generalized consequence machinery;
- atlas or translation runtime;
- metabolics or economics.

No next implementation is selected. The next useful activity is dwell. The
smallest eventual reason to leave this domain would be a qualitatively new
observation basis that can test whether the earned distinctions recur outside
repository observation; no such observer is designed here.

## Capstone Result

No new chart was earned. The synthesis matrix organizes existing coordinates
but adds no stable coordinate with independent discriminating power.

No new distinction was earned. D-0012, D-0016, D-0023, D-0025 through D-0027,
and D-0041 through D-0046 already explain the composed surface.

The strongest invariant across the foreground regime is that captured evidence
remains separately sourced, append-only, integrity-checkable, replayable,
reconstructible, and navigable across repetition, coordinator replacement,
partial composition, temporal skew, external staleness, endpoint recurrence,
and degraded acquisition without silently increasing its epistemic strength.

The strongest remaining epistemic boundary is that source-relative historical
evidence cannot by itself establish a complete, current, atomic, or globally
coherent external world. It also cannot recover caller acknowledgement or an
unobserved interval, and structural admission plus projection membership cannot
substitute for source success or admission resolution.

## Canonical History and Verification

`traces/live_ingest_ledger_v0.jsonl` had SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before capstone authoring. It was not modified.

Baseline verification:

- composed targeted tests: 239/239 passed;
- full suite: 442/442 passed.

Final verification with the capstone files present:

- composed targeted tests: 239/239 passed;
- full suite: 442/442 passed.

Canonical-history SHA-256 remained
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.
