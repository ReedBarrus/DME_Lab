# Local Automation Ecology v0

**Object type:** `CANDIDATE_DESIGN_SPECIFICATION`  
**Object ID:** `LOCAL_AUTOMATION_ECOLOGY_v0`  
**Status:** `PROJECTED_UNIMPLEMENTED`  
**Design owner:** `codex`  
**Prepared:** `2026-09-21`  
**Scientific standing:** `NONE`  
**Architecture authority:** `NONE`  
**Implementation authority:** `NONE`  
**Execution authority:** `NONE`  
**Repository mutation authorized by this document:** `NONE`  
**Live ecology effect:** `NONE`  
**Laboratory standing effect:** `NONE`

## 1. Purpose

This document specifies a desired local automation ecology for DME_Lab. It is
an official design proposal in the limited sense that it is explicit,
versioned, inspectable, and falsifiable. It is not an adopted architecture, an
implementation plan, an execution warrant, or evidence that the described
system exists.

The target is a local operating environment in which humans, model
realizations, deterministic tools, repository history, and bounded execution
cells can collaborate without silently collapsing:

```text
capability into authority
proposal into adoption
observation into truth
continuity into identity
completion into scientific standing
```

The ecology should make useful work easier to initiate, inspect, interrupt,
resume, challenge, reproduce, and retire. The Laboratory remains the place
where claims earn standing through pressure and adjudication.

## 2. Basis and limits

This candidate was drafted against the following inspected basis:

- authoritative remote `main` resolved on `2026-09-21` as
  `f36261e17790b853a91c81bc2f7d0e63e8ee8436`;
- the local drafting worktree was at
  `8dd7ea176a90a56dfd9afd72078d806cf8794bb7`;
- PR `#76` ecology material was inspected only as candidate science at exact
  head `7be98e829f82670730cb23076330ecb10a900d99`;
- `docs/projection/Persistent_Ecology.md`;
- `docs/projection/Investigator_Continuation_v0.md`;
- `docs/projection/local_automation/Local_Model_Workshop.md`;
- `docs/methods/local_automation/Repo_Scout_v0.md`;
- `WORKFLOW.md`;
- `continuity/README.md`.

These references have different owners and authority. Their inclusion here
does not promote projected or candidate material. If this candidate is ever
reviewed for adoption, every basis coordinate must be revalidated against the
then-current repository.

## 3. Design thesis

The dream setup is not one immortal agent and not one omniscient world model.
It is a small, typed ecology with a thin deterministic kernel and replaceable
participants at the edges.

```text
                         HUMAN EXECUTIVE
                     authorize / adjudicate
                              |
                              v
  +-------------------- LABORATORY --------------------+
  | questions -> pressure -> evidence -> standing     |
  | repository authority, decisions, claim ceilings   |
  +--------------------------+-------------------------+
                             | ecology-Lab membrane
                 candidate packets | evidence returns
                             v
  +--------------- LOCAL AUTOMATION ECOLOGY -----------+
  |                                                    |
  |  observe -> reconstruct -> challenge -> plan       |
  |                     |                              |
  |             admit exact warrant                    |
  |                     v                              |
  |           execute one bounded cell                 |
  |                     |                              |
  |            verify -> return receipts               |
  |                                                    |
  +----------------------------------------------------+
```

The membrane is the central architectural feature. It allows the ecology to
be fast, local, and highly instrumented while preventing its internal
coordination state from becoming Laboratory truth by accident.

## 4. Non-collapse invariants

Every implementation claiming conformance must preserve these distinctions:

```text
recommendation != adoption != commitment != execution authority
capability != qualification != authorization != current admission
event != semantic truth != scientific standing
role != seat != occupant != invocation != work claim
participant identity != model identity != process identity != session
cursor position != working state != liveness != authority
branch access != repository mutation authority
test pass != acceptance != integration != generalization
historical authority reference != current authority
missing observation != observed absence
current world != observation basis
```

No convenience layer may erase these distinctions. A user interface may
summarize them, but the underlying objects and provenance must remain
independently inspectable.

## 5. System boundary

### 5.1 Inside the ecology

The local ecology may eventually contain:

- read-only observers and exact-basis repository tools;
- role specifications and durable, unoccupied seats;
- short-lived occupants and invocations;
- bounded work claims;
- frozen execution packets;
- sandbox worktrees and disposable processes;
- append-only observations, receipts, and lifecycle events;
- deterministic validators, scorers, and collision guards;
- consumer-relative continuity cursors;
- local dashboards that expose state without granting authority.

### 5.2 Outside the ecology

The following remain external unless separately and explicitly warranted:

- adoption of a scientific claim;
- change to authoritative project standing;
- selection of a new Laboratory pressure;
- permission to mutate `main` or a live lane;
- merge, release, deployment, publication, or external communication;
- spending, credentials, account changes, or irreversible external effects;
- creation or delegation of authority.

### 5.3 The Laboratory owns

The Laboratory owns the authoritative question-and-evidence loop:

```text
question
-> bounded pressure
-> controlled execution
-> durable evidence
-> independent interpretation
-> adjudication
-> standing or unresolved residue
```

Repository state speaks for implementation facts. Tests and traces speak for
the bounded executions they actually cover. Decisions and adjudications speak
for standing. None substitutes for the others.

### 5.4 The ecology owns

The ecology owns only its operational bookkeeping and candidate production:

```text
who or what observed
what exact basis was observed
what was proposed
what warrant was admitted
what bounded operation was attempted
what mechanically happened
what remains unresolved
```

An ecology record may be durable without being authoritative Laboratory
standing.

## 6. Four operating planes

### 6.1 Epistemic plane

Forms questions, reconstructs relevant history, exposes disagreements, and
states claim ceilings. It produces candidate interpretations, not truth.

### 6.2 Coordination plane

Represents dependencies, routes bounded packets, detects collisions, and
tracks lifecycle state. It does not decide scientific meaning or invent
authority.

### 6.3 Execution plane

Runs a caller-frozen operation inside an admitted consequence envelope. It
cannot widen scope, retry itself, accept its own output, or promote its own
result.

### 6.4 Assurance plane

Performs mechanical validation and fresh review against declared criteria. It
returns a receipt and unresolved discrepancies. It cannot repair the subject
under review in the same invocation.

## 7. Role catalog

Roles describe bounded duties. They are not identities, processes, seats, or
permissions. One realization may fill different roles in separate invocations,
but never by silently carrying state or authority between them.

### 7.1 `SCIENTIST`

**Purpose:** Frame questions, distinctions, pressure designs, interpretations,
and claim ceilings.

**May produce:** question packets, hypothesis sets, pressure candidates,
interpretation candidates, unresolved-relation lists.

**May not:** authorize execution, manipulate evidence, adjudicate its own
claim, or promote a result.

### 7.2 `ADVERSARY`

**Purpose:** Search for counterexamples, hidden collapses, leakage paths,
confounds, and cheaper falsifiers.

**May produce:** challenge packets, contradiction reports, adversarial fixture
proposals, rejection recommendations.

**May not:** alter the subject being challenged, execute the repair, or turn
criticism into standing.

### 7.3 `PLANNER`

**Purpose:** Translate an accepted objective into bounded candidate sequences,
dependencies, stop conditions, and cost envelopes.

**May produce:** plan candidates and execution-warrant drafts.

**May not:** adopt its plan, allocate authority, start an invocation, or claim
that projected capability exists.

### 7.4 `COORDINATOR`

**Purpose:** Route attention and packets among seats, lanes, claims, and
consumers while preserving ownership and collision constraints.

**May produce:** routing proposals, collision reports, readiness views, stale
basis warnings.

**May not:** render semantic verdicts, choose pressure, acknowledge semantic
application for another consumer, or treat availability as permission.

### 7.5 `WORKSHOP`

**Purpose:** Realize one admitted bounded operation in a frozen cell.

**May produce:** artifacts, operation traces, raw outputs, and execution
receipts.

**May not:** self-authorize, broaden its envelope, retry without a new warrant,
merge, deploy, or accept its own work.

### 7.6 `QC`

**Purpose:** Review an artifact or receipt from a fresh basis against explicit
criteria.

**May produce:** mechanical scores, discrepancy lists, qualification
recommendations, and review receipts.

**May not:** repair the reviewed artifact in the same role episode, conceal
missingness, or convert a recommendation into acceptance.

### 7.7 `RECONSTRUCTOR`

**Purpose:** Recover exact lineage, bases, prior claims, limits, and unresolved
residue for a fresh operator.

**May produce:** reconstruction packets and admission checklists.

**May not:** inherit predecessor identity, invent absent evidence, carry old
authority forward, or treat a continuation packet as current truth.

### 7.8 Human `EXECUTIVE`

The Executive is outside the automation role pool. The Executive may select
pressure, grant a bounded warrant, adopt or reject a recommendation, adjudicate
standing, and authorize integration. Automation may prepare the decision
surface, but cannot simulate this authority by consensus or repetition.

## 8. Durable objects

All ecology objects use a common envelope. A conforming serializer should make
unknown fields fail closed at authority-sensitive boundaries.

```json
{
  "schema": "local_automation_ecology_v0",
  "object_type": "...",
  "object_id": "...",
  "version": 1,
  "status": "CANDIDATE",
  "created_at": "RFC-3339 timestamp",
  "producer_ref": "exact participant or apparatus reference",
  "basis_refs": ["exact immutable references"],
  "content_digest": "sha256:...",
  "authority_effect": "NONE",
  "execution_effect": "NONE",
  "standing_effect": "NONE"
}
```

The shared envelope is not a universal ontology. Each object type retains its
own schema, owner, validation rules, and claim ceiling.

### 8.1 `ROLE_SPEC`

Defines duties, permitted outputs, forbidden effects, required inputs, and
separation-of-duty constraints. It grants no permission.

### 8.2 `SEAT_MANIFEST`

A durable coordinate at which an admitted role may be occupied. It preserves:

```text
seat identity
role reference
lane or domain scope
lifecycle state
current occupant binding, if any
current work-claim reference, if any
current invocation reference, if any
currentness basis
history reference
```

An unoccupied seat explicitly carries null occupant, work-claim, and invocation
references. Null is not inferred from missing fields.

### 8.3 `OCCUPANT_BINDING`

Binds one currently admitted realization to one seat for a bounded interval.
It contains a fresh binding ID, admission evidence, start condition, expiry or
release condition, and no inherited authority payload.

### 8.4 `INVOCATION_MANIFEST`

Describes one process/model/tool episode: exact runtime, frozen input digest,
operation budget, tool surface, environment basis, output schema, and terminal
status. An invocation is not an occupant and may not outlive its admitted
occupant binding.

### 8.5 `WORK_CLAIM`

Reserves one bounded unit of work against an exact basis. It contains an owner,
scope, exclusions, collision key, preconditions, expiry, and terminal
disposition. A work claim is neither a scientific claim nor execution
authority.

### 8.6 `OBSERVATION_BASIS`

Names the exact world slice actually observed: repository/commit, source
digests, time bounds, event range, runtime facts, and declared missingness.
Every interpretation points to its observation basis rather than pretending to
describe an unqualified present.

### 8.7 `CONTINUITY_CURSOR`

Records one consumer's acknowledged position in one append-only stream. It
means only that the consumer successfully applied events through that
position. It does not establish liveness, seat occupancy, shared understanding,
or authority.

### 8.8 `AUTHORITY_WITNESS`

References a separately owned authorization and binds it to exact subject,
actor class, operations, targets, limits, basis, expiry, and stop conditions.
The witness makes authority inspectable; it does not create authority merely
by being serialized.

### 8.9 `EXECUTION_PACKET`

The immutable input to a Workshop cell:

```text
objective
exact basis
authorized operations
forbidden operations
input artifacts
tool and network surface
budgets
expected outputs
success criteria
stop conditions
authority witness reference
```

### 8.10 `EVIDENCE_RECEIPT`

Mechanically records what an invocation actually attempted and observed. It
must separate request, operation trace, raw output, validation result,
repository/runtime before-and-after fingerprints, and missing evidence.

### 8.11 `REVIEW_RECEIPT`

Records the review basis, criteria, findings, disagreements, scorer output, and
recommendation. It has no adoption effect.

### 8.12 `DISPOSITION_RECEIPT`

Closes or releases a work claim, invocation, occupant binding, or seat
transition with explicit reason and terminal evidence. Lifecycle completion is
not scientific completion.

### 8.13 `RECONSTRUCTION_PACKET`

Carries exact mechanical coordinates, predecessor claims labeled as prior
projections, unresolved residue, and a list of coordinates requiring current
admission. It intentionally excludes hidden reasoning, subjective identity,
and transferable authority.

## 9. Seat and invocation lifecycle

The desired lifecycle is explicit and fail-closed:

```text
AVAILABLE_UNOCCUPIED
    -> ADMISSION_PENDING
    -> OCCUPIED_IDLE
    -> CLAIMED
    -> INVOCATION_ACTIVE
    -> INVOCATION_TERMINAL
    -> DISPOSITION_PENDING
    -> AVAILABLE_UNOCCUPIED | HELD | CLOSED
```

This state vocabulary is projected. Existing live lane vocabularies remain
authoritative for their own objects until an adapter and migration pressure
earn a replacement.

Rules:

1. A seat is not occupied until a fresh occupant binding passes admission.
2. Occupancy does not create a work claim.
3. A work claim does not start an invocation.
4. An invocation may enter `ACTIVE` only with an admitted execution packet.
5. Terminal invocation output does not close the work claim automatically.
6. Disposition must reconcile artifacts, receipts, cursor effects, and
   remaining residue.
7. Releasing a seat clears current occupant, invocation, and work-claim
   references while preserving immutable history.
8. A fresh occupant reconstructs from durable history and performs current
   admission; no predecessor authority or subjective identity transfers.

## 10. Core protocols

### 10.1 Protocol P0 — Observe and reconstruct

1. Resolve authoritative repository state independently.
2. Read the consumer's cursor without mutating it.
3. Read the unread event delta in order.
4. Resolve only task-consequential references.
5. Separate observations, prior interpretations, current admissions, and
   missing relations.
6. Acknowledge only after semantic application succeeds and only when the task
   authorizes cursor mutation.

Output: `OBSERVATION_BASIS` plus optional `RECONSTRUCTION_PACKET`.

### 10.2 Protocol P1 — Form a bounded question

The Scientist emits one falsifiable question, named claim ceiling, frozen
conditions, measures, forbidden inferences, and termination criteria.

Output: candidate pressure packet. No execution.

### 10.3 Protocol P2 — Adversarial pressure review

The Adversary checks for confounds, authority laundering, mutable controls,
duplicate collapse, unmeasured cost, missing negative cases, and conclusions
that exceed the fixture.

Output: challenge receipt. The original author does not silently repair the
record of the challenge.

### 10.4 Protocol P3 — Plan and warrant draft

The Planner converts an accepted question into the smallest test sequence. It
declares exact targets, roles, bases, operations, budgets, evidence, abort
conditions, and which decisions remain human.

Output: unsigned execution-warrant draft.

### 10.5 Protocol P4 — Human authorization

The Executive accepts, narrows, rejects, or replaces the draft. Authorization
must bind to an exact warrant digest and current basis. Any material change
requires new authorization.

Output: externally owned authority source plus an `AUTHORITY_WITNESS`.

### 10.6 Protocol P5 — Admission

Deterministic checks verify exact basis, object identity, current authority,
seat availability, claim collision, scope, budgets, tool surface, and
preconditions. Missing, stale, duplicate, ambiguous, or contradictory inputs
fail closed.

Output: admission receipt. Admission validates applicability; it does not
create authority.

### 10.7 Protocol P6 — Frozen-cell execution

The Workshop runs exactly one admitted packet. The default is one attempt, no
retry, no scope expansion, no hidden network, and no self-selected follow-up.
Before/after fingerprints and raw outputs are retained outside the model-visible
surface where possible.

Output: artifacts plus `EVIDENCE_RECEIPT`.

### 10.8 Protocol P7 — Fresh QC

QC receives the frozen criteria, subject artifacts, and evidence receipt. It
checks completeness, schema, provenance, invariants, tests, and claim ceiling
without editing the subject.

Output: `REVIEW_RECEIPT` with pass, fail, or unresolved recommendation.

### 10.9 Protocol P8 — Laboratory adjudication

The evidence return crosses the membrane. The Laboratory independently decides
whether to reject, re-pressure, qualify narrowly, integrate, or update
standing. No ecology object performs this transition on its own.

### 10.10 Protocol P9 — Disposition and turnover

The current occupant stops, the invocation becomes terminal, the work claim is
disposed, current references are cleared, and durable history remains. A fresh
occupant may later enter only through a new binding and current admission.

A successful turnover demonstrates:

```text
old occupant ends
+ durable lane history remains
+ fresh occupant/invocation enters
+ old occupant authority does not transfer
+ new operator reconstructs enough state to continue lawfully
```

## 11. Tooling surface

Tools are intentionally narrower than roles. A tool performs mechanics; a role
owns a bounded interpretive duty.

### 11.1 Existing or evidenced primitives to reuse

#### Repo Scout

Exact-commit, caller-planned, read-only repository inspection with mechanically
attached source identities. It remains one-shot apparatus, not a scheduler,
router, planner, retry engine, or authority source.

#### Continuity ledger and cursor reader

Append-only activity transport with consumer-relative acknowledgement. It is
not global memory, semantic truth, seat state, or presence proof.

#### Workshop frozen cell

The desired execution primitive is the smallest admitted one-shot cell with a
frozen packet, explicit tool surface, captured fingerprints, and external
review. Mock fidelity does not establish a real provider or generalized
Workshop.

#### Lane and claim collision guards

Deterministic checks should reuse qualified exact-basis, stale-currentness,
claim-collision, revalidation, and lifecycle mechanics where their contracts
actually match the target object.

### 11.2 Projected supporting tools

#### Basis resolver

Resolves branches, commits, blobs, schemas, event ranges, and runtime
coordinates into immutable references. Read-only.

#### Packet compiler

Builds canonical candidate packets from declared fields, validates schemas,
computes digests, and refuses omitted mandatory limits. It cannot authorize
the packet.

#### Authority gate

Validates that a separately owned authority source matches subject, basis,
scope, actor class, time, and operation. It returns admit/reject; it never
manufactures permission.

#### Claim registry and collision detector

Indexes active bounded work claims by exact collision keys. It reports
conflicts and staleness without choosing a winner.

#### Cell runner

Creates a disposable local process/worktree, exposes only admitted inputs and
tools, captures output and fingerprints, enforces budgets, and terminates at
the packet boundary.

#### Receipt verifier

Checks canonical serialization, digests, source resolution, operation
allowlists, budget compliance, and before/after state. It reports mechanics,
not scientific meaning.

#### Lifecycle controller

Applies one authorized state transition with compare-and-swap currentness and
an append-only receipt. It has no power to choose the transition.

#### Reconstruction builder

Collects exact mechanical basis, prior projected standing, unresolved residue,
and mandatory revalidation coordinates for a replacement operator.

#### Read-only cockpit

Displays seats, occupants, invocations, work claims, bases, unread deltas,
receipts, conflicts, and missing relations. Every displayed conclusion links
to its owner and basis. Buttons that cause consequence require a separately
admitted warrant.

### 11.3 Deliberately absent from v0

- universal scheduler;
- background daemon;
- autonomous objective selector;
- generalized model router;
- automatic retries or self-healing;
- consensus-as-authority mechanism;
- shared writable global world state;
- automatic merge, deployment, or external messaging;
- personality or model identity as durable operator identity;
- hidden promotion from telemetry to standing.

If repeated bounded pressures later show that one of these pays rent, it should
enter through its own candidate contract and qualification path.

## 12. Ecology–Laboratory membrane

Only typed transfers cross the membrane.

### 12.1 Laboratory to ecology

Permitted inputs:

- accepted question or explicitly labeled candidate question;
- exact repository and evidence basis;
- frozen constraints and measures;
- approved execution warrant and authority reference;
- declared evaluation and stop criteria.

### 12.2 Ecology to Laboratory

Permitted outputs:

- candidate artifacts;
- raw operation evidence;
- mechanical receipts;
- review recommendations;
- contradictions and missing relations;
- lifecycle/disposition evidence.

### 12.3 Forbidden implicit transfers

The following never cross merely because they exist inside the ecology:

- authority inferred from branch or tool access;
- standing inferred from a green check;
- admission inferred from a prior occupant;
- objective inferred from an old work claim;
- truth inferred from event repetition;
- completion inferred from a terminal process;
- identity inferred from the same model family or consumer name.

## 13. Storage and topology

The desired physical design is local-first and repository-addressable:

```text
authoritative Git repository
    authoritative contracts, decisions, fixtures, admitted evidence

candidate branches or isolated worktrees
    proposed code, schemas, tests, and reports

append-only local ecology store
    events, invocations, receipts, dispositions, cursor histories

content-addressed artifact store
    large/raw inputs and outputs referenced by digest

disposable cell directories
    invocation-scoped files destroyed only after durable receipt verification
```

The thin kernel should understand object identity, canonical serialization,
digests, exact basis, admission, lifecycle transitions, and append-only
receipts. Domain semantics remain in adapters and Laboratory-owned contracts.

The first implementation should remain single-node and single-writer where
possible. Distribution, locking, and multi-writer reconciliation are later
pressures, not v0 assumptions.

## 14. Safety and failure semantics

The ecology fails closed on:

- unresolved or stale basis;
- missing or ambiguous authority witness;
- mismatched warrant digest;
- unknown schema or extra authority-sensitive field;
- duplicate object identity or collision key;
- occupied seat or conflicting active claim;
- invocation/occupant mismatch;
- operation outside the allowlist;
- path, network, time, token, cost, or output-budget excess;
- before/after mutation not authorized by the packet;
- incomplete raw evidence;
- failed semantic application of a continuity event;
- claimed success without the required receipt;
- any attempt by a producer to accept or promote its own output.

Failure records the observable attempt and reason. Failure does not authorize a
retry. Recovery is a new, separately admitted operation.

## 15. Maturity ladder

The design should be earned in layers. A higher tier may not be claimed from a
lower-tier demonstration.

### Tier 0 — Read-only orientation

Exact-basis inspection, reconstruction, candidate packets, and dashboards.
No execution effect. This is closest to currently evidenced primitives.

### Tier 1 — Sandbox candidate production

One occupant produces artifacts in an isolated worktree under an explicit
packet. No live-lane or authoritative mutation. Fresh QC remains separate.

### Tier 2 — Bounded Workshop consequence

One frozen cell performs one explicitly authorized mutation, returns complete
evidence, and is externally adjudicated. No retry or scheduler.

### Tier 3 — Multi-seat local ecology

Several independently admitted seats coordinate concurrent claims, stale
currentness, handoffs, and turnover without collision or authority transfer.

### Tier 4 — Persistent bounded operation

Time-separated invocations can reconstruct, continue, stop, and recover under
explicit commitments and budgets. Scheduling is introduced only if repeated
manual pressures establish its value and safe contract.

### Tier 5 — External consequence adapters

Narrow adapters may affect systems outside the repository under domain-specific
authority, rollback, and audit contracts. No general external action authority
is implied.

No tier is currently adopted by this document. Each requires its own evidence
and adjudication.

## 16. Ideal operating cycle

An ideal bounded cycle looks like this:

1. A human or Scientist records a falsifiable question.
2. A Reconstructor resolves the current basis and relevant history.
3. An Adversary identifies the cheapest confounds and forbidden inferences.
4. A Planner drafts the smallest pressure and warrant.
5. The Executive authorizes, narrows, or rejects it.
6. The Coordinator verifies seat/claim availability and routes the exact
   packet.
7. Admission checks currentness, authority, budgets, and collisions.
8. Workshop executes once inside the frozen cell.
9. Mechanical tools attach raw evidence and before/after fingerprints.
10. Fresh QC reviews without repairing the subject.
11. The Laboratory adjudicates what, if anything, was earned.
12. Lifecycle disposition releases the seat while retaining history.
13. Any fresh occupant reconstructs and re-admits rather than inheriting the
    prior occupant's authority or interpretation.

## 17. Minimum dashboards

The cockpit should expose four views without merging them:

### 17.1 Current operations

Seats, occupants, claims, invocations, budgets, and terminal conditions.

### 17.2 Evidence lineage

Questions, warrants, exact bases, artifacts, receipts, reviews, and
adjudications.

### 17.3 Continuity

Event-stream heads, consumer cursors, unread ranges, application status, and
reconstruction packets.

### 17.4 Authority

Who owns each decision, what exact action is admitted, expiry, scope, and
unresolved authority gaps.

The dashboard must make `UNKNOWN`, `MISSING`, `STALE`, `UNRESOLVED`, and
`NOT_AUTHORIZED` first-class states. It must not render them as empty or green.

## 18. Qualification pressures

The smallest useful qualification sequence is:

1. **Membrane pressure:** prove that candidate artifacts and receipts can cross
   between ecology and Laboratory without changing standing automatically.
2. **Exact-basis admission pressure:** reject stale, ambiguous, mismatched, and
   missing bases before invocation.
3. **Claim-collision pressure:** preserve two concurrent claims without
   last-writer wins or silent duplication.
4. **Fresh-occupant turnover pressure:** end an old occupant, retain lane
   history, admit a fresh occupant, and prove authority does not transfer.
5. **Interrupted-consequence recovery pressure:** distinguish observed attempt,
   unknown effect, retry admissibility, and false closure.
6. **Scheduler-necessity pressure:** compare manual triggering with the smallest
   candidate scheduler only after the preceding mechanics are stable.

Each pressure must freeze fixtures, measures, budgets, negative cases, and
claim ceilings in advance. Local success remains local.

## 19. First recommended design slice

If this specification is ever authorized for realization, the first slice
should not build the whole ecology. It should implement only:

```text
one durable unoccupied seat
+ one fresh occupant binding
+ one bounded work claim
+ one frozen read-only invocation
+ one evidence receipt
+ one explicit disposition
+ one fresh reconstruction by a replacement operator
```

The slice should use an isolated fixture, not a live lane. Its sole claim would
be that the object relations and turnover mechanics work for that fixture. It
would not earn scheduling, generalized orchestration, autonomous operation, or
Laboratory adoption.

## 20. Open design questions

The following relations remain deliberately unresolved:

- whether seat and lane should share a lifecycle vocabulary or be connected by
  an adapter;
- which object owner may request, but not authorize, occupant binding;
- whether authority witnesses belong in Git, an append-only operational store,
  or both;
- how expiration is represented without trusting wall-clock time alone;
- what atomicity boundary is required between claim, invocation, and
  disposition writes;
- when a continuity event is semantically applied enough to acknowledge;
- which raw artifacts belong in Git versus a content-addressed store;
- how independent QC is established when realizations share a model family;
- what evidence would justify a scheduler rather than repeated explicit
  invocation;
- how cost, latency, and attention are measured without becoming hidden
  optimization authority;
- what recovery contract applies after an authorized external consequence is
  observed but its final result is missing.

## 21. Acceptance conditions for this design

This document should be considered a useful candidate only if review finds
that it:

1. preserves the Laboratory's existing authority and standing boundaries;
2. keeps role, seat, occupant, invocation, work claim, and authority distinct;
3. supports fresh-occupant reconstruction without identity or authority
   inheritance;
4. makes consequence and missingness mechanically visible;
5. begins with bounded, testable slices rather than generalized orchestration;
6. can be contradicted or narrowed by explicit pressure;
7. does not claim implementation, qualification, adoption, or execution.

## 22. Terminal declaration

```text
DESIGN_SPECIFICATION: COMPLETE
IMPLEMENTATION: NONE
EXECUTION: NONE
AUTHORITY_CREATED: NONE
SCIENTIFIC_STANDING_CHANGED: NONE
LIVE_LANE_EFFECT: NONE
REPOSITORY_EFFECT: ONE LOCAL CANDIDATE DOCUMENT ONLY
NEXT_ACTION: HUMAN REVIEW OR A SEPARATELY AUTHORIZED BOUNDED PRESSURE
```
