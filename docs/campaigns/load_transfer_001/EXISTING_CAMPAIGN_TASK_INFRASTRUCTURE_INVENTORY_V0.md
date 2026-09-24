# EXISTING CAMPAIGN / TASK INFRASTRUCTURE INVENTORY V0

OBJECT_TYPE:
ARCHITECTURE_INVENTORY

OBJECT_ID:
LOAD_TRANSFER_001_EXISTING_CAMPAIGN_TASK_INFRASTRUCTURE_INVENTORY_V0

STANDING:
CANDIDATE_ONLY

PURPOSE:

Account for existing campaign, task, process, handoff, planning, cockpit,
and operational-control machinery before extending LOAD_TRANSFER_001 into a
campaign-decomposition work lifecycle.

This inventory does not authorize mutation of any existing surface.

# 1. TARGET RELATION

The missing relation is not "task management" in general.

It is:

```
REGISTERED CAMPAIGN / DECLARED HORIZON
↓
BOUNDED DECOMPOSITION BASIS
↓
DETERMINISTIC SEAT WORK ITEMS
↓
OBSERVED CONSEQUENCE
↓
CAMPAIGN-RELATIVE EVALUATION
↓
CONTINUE | REPAIR DECOMPOSITION | HOLD | REPLAN
```

The primary scientific question is whether higher-order executive symbolism can
be conserved through decomposition into discrete work objects and recovered
again from observable consequences.

Freeze:

```
CAMPAIGN TARGET
!=
WORK ITEM

WORK ITEM COMPLETION
!=
CAMPAIGN PROGRESS

PLANNED CONSEQUENCE
!=
OBSERVED CONSEQUENCE

DECOMPOSITION FAILURE
!=
CAMPAIGN FAILURE
```

# 2. EXISTING SURFACE CLASSIFICATION

## A. DME_Development_Campaign_v0.md

CLASSIFICATION:
REUSE

CURRENT LEVERAGE:
- declared campaign objective;
- coupled frontiers;
- immediate campaign sequence;
- attack/failure modes;
- campaign success metrics;
- campaign-level navigation and priority law.

WHY REUSE:
This is already a high-order campaign / horizon object. It demonstrates that
campaign semantics are not missing.

DO NOT:
- convert the prose document directly into an execution queue;
- infer task completion from campaign prose;
- make it the universal campaign schema.

USE AS:
one campaign-semantic specimen and source of campaign-level conservation laws.

---

## B. Cockpit development_horizon_projection.py

CLASSIFICATION:
REUSE / ADAPT AT THE PROJECTION EDGE

CURRENT LEVERAGE:
It already reconstructs durable campaign objects containing:
- campaign_id;
- objective;
- claim_ceiling;
- unresolved_relations;
- dependency_edges;
- relation standing;
- envelope requests;
- execution receipts;
- current selections;
- preparation receipts;
- assignment state;
- wake/reentry state.

It derives campaign horizon states:

```
READY_FOR_PRESSURE
ACTIVE
EVIDENCE_ACCUMULATING
BLOCKED
EARNED
FRACTURED
```

It explicitly reports:

```
priority_effect = NONE
authority_effect = NONE
execution_effect = NONE
standing_effect = NONE
```

WHY REUSE:
This is already a campaign-observation / horizon projection surface.

ADAPT LATER:
Project decomposition/work-cycle state into Cockpit once the work lifecycle
has pressure evidence.

DO NOT:
make this read-only projection the writer/source of campaign truth.

---

## C. live_runtime_projection.py campaign / assignment / selection surfaces

CLASSIFICATION:
REFERENCE + FUTURE ADAPTER TARGET

CURRENT LEVERAGE:
The runtime projection already expects distinct stores for:
- campaigns / relation_standing / envelope_requests / execution_receipts;
- selection events;
- preparation receipts/artifacts;
- assignment events/satisfactions;
- semantic resources/runs;
- reentry opportunities/events/receipts;
- manual wake bells.

WHY IMPORTANT:
The repository already contains the shape of a richer operational ecology.
LOAD_TRANSFER_001 should not duplicate these concepts accidentally.

CURRENT LIMIT:
The inventory has not established a single admitted writer/API for all of these
runtime stores from current repository evidence.

DECISION:
Do not bind the first decomposition lifecycle directly to these stores yet.
Use immutable handles/adapters after the campaign/work seam is pressure-stable.

---

## D. DEVELOPMENT_PRESSURE_MAP.md

CLASSIFICATION:
REFERENCE_ONLY / DO_NOT_MUTATE INTO QUEUE

CURRENT LEVERAGE:
Development reachability, role boundaries, gating, and packet-worthiness.

EXPLICIT EXISTING LAW:
The map must not become:
- a task queue;
- a scheduler;
- automatic activation;
- execution authority.

DECISION:
Preserve that boundary.

The future work lifecycle may reference a development-pressure node as a
campaign/horizon source, but must not reinterpret map reachability as queued
work or authorization.

---

## E. Lab Conductor v0
Surfaces:
- tools/lab_conductor.py
- lab/processes/
- lab/events/events.jsonl
- lab/packets/
- lab/state/LAB_STATE_v0.json
- src/cockpit/action_surface.py

CLASSIFICATION:
REUSE FOR DECLARED PROCESS / EVENT SEMANTICS;
DO NOT MERGE WITH WORK QUEUE YET

CURRENT LEVERAGE:
- explicitly declared process graphs;
- append-only events;
- replayable operational state;
- MECHANICAL transitions;
- ROLE_JUDGMENT stop;
- HUMAN_DECISION stop;
- BLOCKED posture;
- packet validation;
- read-only Action Surface projection.

EXISTING NON-COLLAPSES INCLUDE:

```
process state != scientific standing
mechanical routing != semantic judgment
packet validity != claim validity
replay != re-execution
logged intent != completed consequence
human authority != human state transport
```

WHY REUSE:
These are directly relevant lifecycle laws.

WHY NOT MERGE NOW:
The Conductor is a process-routing prototype, while LOAD_TRANSFER_001 is testing
campaign-derived work identity and handoff reconstruction. Prematurely making
work items conductor transitions would make it difficult to tell which layer
actually carries the conservation relation.

FUTURE ADAPTER:
A stable work-item state transition may emit/consume conductor-compatible
process events after the work lifecycle earns that relation.

---

## F. Lab Ops Registry v0

CLASSIFICATION:
REUSE AS OPERATOR VISIBILITY PRECEDENT;
ADAPT LATER FOR WORK-CYCLE OBSERVABILITY

CURRENT LEVERAGE:
One operator-facing projection answering:

```
WHAT EXISTS?
WHERE IS IT?
WHY IS IT STOPPED?
WHO OWNS THE NEXT MOVE?
DOES REED NEED TO DO ANYTHING?
```

IMPORTANT EXISTING RULE:

```
If it is not represented here,
Reed is not responsible for remembering it
as active operational state.
```

DECISION:
This is highly aligned with LOAD_TRANSFER_001.

Do not make the registry campaign/work authority.
Later extend or adapt its projection model so active campaign/work posture,
blockers, next eligible role, and human-attention requirements are visible from
the work lifecycle.

---

## G. CAMPAIGN-LEG-1A bounded task / handoff evidence

Surfaces:
- continuity/handoffs/campaign_leg_1a_task.json
- traces/campaign_leg_1a_handoff.json
- traces/campaign_leg_1a_task_result.json

CLASSIFICATION:
REUSE AS HISTORICAL SPECIMEN / PRECEDENT

OBSERVED RELATIONS:
- bounded requested_task;
- declared required basis refs;
- request standing;
- explicit nonclaims;
- exact expected result shape;
- task understood without human restatement;
- result artifacts retained;
- authority_changed = false;
- standing_changed = false;
- human reconstruction required = false.

WHY IMPORTANT:
This is already evidence that a campaign-labelled bounded task can cross a
seat/tool boundary without human semantic restatement.

LIMIT:
It does not establish a reusable decomposition lifecycle, dependency graph,
repair cycle, campaign progress semantics, or general routing.

---

## H. Twinning Protocol v0

CLASSIFICATION:
REFERENCE / REUSE FOR ENVELOPE BOUNDARIES

CURRENT LEVERAGE:
Preserves separation between:
- interpretation;
- human authorization;
- bounded execution;
- returned evidence.

Relevant reciprocal surfaces include EXECUTION_PACKET_v0 and EVIDENCE_RETURN_v0.

DECISION:
Do not replace these with SEAT_WORK_ITEM_V0.

Instead:
a campaign-derived work item may later be rendered into an execution packet,
and the returned evidence may later satisfy/close a work item's evidence debt.

Freeze:

```
WORK ITEM
!=
EXECUTION PACKET

HANDOFF RECEIPT
!=
EVIDENCE RETURN
```

Adapters may connect them after pressure.

---

## I. Atlas development cycle / relational-horizon process

Surfaces:
- ATLAS_DEVELOPMENT_CYCLE_AND_RELATIONAL_HORIZON_PROCESS_V0.md
- ATLAS_MINIMAL_SCIENCE_WORKSHOP_HANDOFF_LOOP_V0.md
- planner / relational-horizon artifacts

CLASSIFICATION:
REFERENCE AS SCIENTIFIC DECOMPOSITION LAW

CURRENT LEVERAGE:

Bounded scientific execution loop:

```
OBSERVE
→ EVALUATE
→ PROJECT
→ REVIEW
→ AUDIT
→ REDUCE / COMPRESS
→ RUN
→ FREEZE
→ ADJUDICATE
→ REPAIR
→ QUALIFY
→ SELECT NEXT PRESSURE
```

Higher-order planning candidate:

```
TARGET
+
CURRENT QUALIFIED FRAME
+
PROJECTED CONSEQUENTIAL FRAME(S)
→ RELATIONAL HORIZON CANDIDATES
→ PRESSURE FAMILY
→ ORDERED BOUNDED EXECUTION LOOPS
→ REVIEW / REPLAN
```

DECISION:
This should inform the decomposition/evaluation lifecycle, but should remain
scientifically separate from the deterministic work mechanics.

Executive automation over this process remains PINNED / DEFERRED.

---

## J. Local Model Qualification Campaign v0

CLASSIFICATION:
REUSE AS DECOMPOSITION-PRESSURE SPECIMEN

CURRENT LEVERAGE:
Already contains:
- campaign objective;
- campaign controls;
- task families;
- exact specimens;
- allowed / protected surfaces;
- attempt budget;
- consequence-guided repair;
- STOP / escalation;
- evaluation dimensions;
- promotion boundary.

WHY IMPORTANT:
This is an excellent future specimen for testing whether campaign symbolism can
be decomposed into deterministic work objects without losing claim, scope,
authority, or repair boundaries.

DO NOT:
activate the campaign merely because it is structurally convenient.

---

## K. SCA001 campaign progress ledger

CLASSIFICATION:
REFERENCE / FUTURE CAMPAIGN-EVIDENCE ADAPTER

CURRENT LEVERAGE:
Append-oriented record of:
- attempted pressures;
- surviving/fractured relations;
- evidence-forced plan changes;
- next earned pressure;
- forbidden conclusions.

WHY IMPORTANT:
This is closer to "campaign evolution under consequence" than a simple task
completion log.

FUTURE USE:
Observed work consequences should eventually be evaluated into campaign-relative
progress/evidence events rather than translated directly into campaign status.

Freeze:

```
WORK COMPLETED
!=
CAMPAIGN ADVANCED
```

---

## L. LOAD_TRANSFER_001

CLASSIFICATION:
ADAPT / CURRENT MISSING-SEAM CANDIDATE

CURRENT LEVERAGE:
- CURRENT_OPERATIVE_FRAME_V0;
- predeclared SEAT_WORK_ITEM_V0 objects;
- claim fencing;
- role fencing;
- predecessor handoff requirements;
- terminal completion posture;
- HANDOFF_RECEIPT_V0;
- exact artifact byte identity;
- no authority / standing / Atlas effect;
- no automatic retry;
- no automatic next-seat invocation;
- fresh serialized reconstruction.

CURRENT REPAIR:
Handoff now distinguishes:

```
input_work_item_identity
!=
terminal_work_item_identity
```

so fresh reconstruction can verify the terminal work object while preserving the
claimed-input provenance coordinate.

# 3. RECOMMENDED ARCHITECTURE

Do NOT introduce an independent Campaign System #2.

Use a small binding layer:

```
EXISTING REGISTERED / ADDRESSED CAMPAIGN
+
CAMPAIGN REVISION / SOURCE IDENTITY
+
DECLARED HORIZON / RELATION TARGET
↓
DECOMPOSITION RECORD
↓
SEAT_WORK_ITEM_V0
↓
SEAT EXECUTION
↓
OBSERVABLE CONSEQUENCE / ARTIFACT IDENTITY
↓
WORK COMPLETION RECEIPT
↓
CAMPAIGN-RELATIVE EVALUATION
↓
CONTINUE | REPAIR_DECOMPOSITION | HOLD | REPLAN
```

The campaign identity should be a HANDLE to an existing campaign representation,
not a new universal campaign ontology.

# 4. MINIMUM WORK-ITEM EXTENSION

Before campaign decomposition pressure, SEAT_WORK_ITEM_V0 should eventually gain
the following parent/decomposition coordinates:

```
campaign_handle
campaign_revision_identity
campaign_horizon_handle
parent_work_item_id          optional
dependency_work_item_ids
decomposition_basis
expected_consequence
evidence_debt
observability_requirements
repair_destination
```

Do not add these merely as fields.

Each must be pressureable.

Required relation:

```
WORK_ITEM
IS A DECLARED DECOMPOSITION OF
CAMPAIGN/HORIZON IDENTITY
```

# 5. CONSEQUENCE EVALUATION LAYER

Completion must not be the final feedback signal.

For each work item retain separately:

```
REQUESTED TRANSFORMATION
EXPECTED CONSEQUENCE
OBSERVED CONSEQUENCE
MECHANICAL RESULT
EVIDENCE PRODUCED
UNRESOLVED LOAD
SCOPE / AUTHORITY EFFECT
CAMPAIGN-RELATIVE INTERPRETATION
```

Then:

```
MECHANICAL SUCCESS
!=
EXPECTED CONSEQUENCE OBSERVED
!=
CAMPAIGN PROGRESS
```

Candidate evaluation outputs:

```
CONSEQUENCE_MATCHED
CONSEQUENCE_PARTIAL
CONSEQUENCE_CONTRADICTED
CONSEQUENCE_UNRESOLVED
WORK_ENVELOPE_VIOLATION
```

These dispositions do not themselves promote campaign/scientific standing.

# 6. REPAIR CYCLE

The repair target must be typed.

```
WORK OUTPUT DEFECT
→ repair work/output

DECOMPOSITION DEFECT
→ repair/redecompose work item family

CAMPAIGN/HORIZON DEFECT
→ HOLD / HUMAN-PLANNER REPLAN

APPARATUS DEFECT
→ repair apparatus, preserve frozen evidence
```

Freeze:

```
BAD OUTPUT
!=
BAD DECOMPOSITION
!=
BAD CAMPAIGN
!=
BAD APPARATUS
```

This is necessary to prevent meaningless artifact production from simply
creating more tasks.

# 7. OBSERVABILITY DURING SEAT OPERATION

The eventual work-cycle observer should expose at least:

```
campaign / horizon identity
work item identity
seat / role
input identities
current lifecycle state
allowed / forbidden consequence envelope
required evidence debt
observed artifacts / receipts
current blockers / holds
authority requirement
budget posture
expected consequence
observed consequence
next eligible destination
human attention required
```

Projection remains read-only.

Observability does not become authority.

# 8. COMPRESSION / MEMORY MANAGEMENT AS PERMANENT CAMPAIGN

The proposed compression/history-conservation horizon is structurally compatible
with this lifecycle.

Why:

Compression repeatedly requires:

```
observe current information burden
→ identify load-bearing relations
→ decompose cleanup/compression work
→ transform bounded artifacts
→ reconstruct/check conserved meaning
→ detect loss
→ repair or accept
→ retain challengeable history
```

This makes compression a strong later permanent campaign because it exercises
the exact decomposition/conservation relation while reducing repository and
context bloat.

Do NOT automate destructive deletion from early compression work.

Candidate first posture:

```
classify
→ propose compression
→ reconstruct
→ compare
→ cold-retain originals
→ admit bounded replacement only after pressure
```

# 9. PROPOSED DEVELOPMENT CAMPAIGN SHAPE

A planner may formalize a campaign similar to:

```
WORKCYCLE_STABILIZATION_001
```

Target:

Establish a boring, observable, repairable campaign→decomposition→seat-work
lifecycle in which bounded work can advance without Reed carrying routing state,
while preserving campaign identity, consequence evidence, authority boundaries,
and corrective potential.

Suggested pressure sequence:

1. repair LOAD_TRANSFER_001 and pass deterministic tests;
2. run one real two-seat handoff with no Reed narration;
3. bind work items to one existing addressed campaign/horizon;
4. pressure dependency/decomposition identity;
5. add expected-vs-observed consequence witness;
6. evaluate completed work against campaign horizon without auto-promotion;
7. pressure typed repair routing;
8. project work-cycle observability into operator/cockpit surfaces;
9. repeat until routine handoffs are boring;
10. use compression/history conservation as a recurring campaign specimen.

Executive campaign assembly remains manual/planner-led during this sequence.

# 10. DO-NOT-BUILD YET

Do not build:

- autonomous campaign creation;
- generic planner engine;
- generic scheduler;
- automatic worker spawning;
- automatic scientific promotion;
- self-authorization;
- automatic trust-root promotion;
- unbounded branching;
- silent retry;
- universal campaign ontology;
- generic task database replacing existing campaign/process stores.

# 11. NEXT LAWFUL IMPLEMENTATION QUESTION

After LOAD_TRANSFER_001 tests are mechanically clean:

```
CAN ONE SEAT_WORK_ITEM_V0
PROVE ITS DECOMPOSITION LINEAGE
TO ONE EXISTING ADDRESSED CAMPAIGN/HORIZON

AND

CAN ITS OBSERVED CONSEQUENCE
BE EVALUATED AGAINST THAT HORIZON

WITHOUT
AUTO-PROMOTING CAMPAIGN PROGRESS?
```

That is the smallest seam that advances the new workcycle without automating the
executive planning layer prematurely.
