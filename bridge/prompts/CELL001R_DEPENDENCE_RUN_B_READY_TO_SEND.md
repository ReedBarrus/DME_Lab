# LOCAL FRAME DEPENDENCE CELL 001R — BRIDGE RECONSTRUCTION

ROLE:
BOUNDED RECONSTRUCTION MODEL

EXPERIMENT_SOURCE_REF:
d5a47606ce0ed8a08ea444638e5ae4b90c59ea91

DECLARED_LOAD:
SEMANTIC_RECONSTRUCTION

TARGET:
Reconstruct the bounded operative meaning of the supplied WORKCYCLE_STABILIZATION_001 subject.

DO NOT:
- use information outside this prompt;
- infer missing evidence from filenames or general familiarity;
- repair absent coordinates;
- create scientific standing;
- create authority;
- execute or mutate anything.

RECONSTRUCT EXACTLY THESE COORDINATES:

1. CAMPAIGN_IDENTITY
2. CAMPAIGN_TARGET
3. RELATIONAL_HORIZON_ROLE
4. CAMPAIGN_TO_DECOMPOSITION_TO_WORK_RELATION
5. BASIS_GOVERNED_PRESSURE_JUSTIFICATION
6. DISTINCTION_VS_TASK
7. EXPECTED_VS_OBSERVED_CONSEQUENCE
8. WORK_COMPLETION_VS_CAMPAIGN_ADVANCE
9. QUALIFICATION_VS_AUTHORITY
10. APPLICATION_CONSEQUENCE_BASIS_RECONCILIATION
11. HOLD_NO_JUSTIFIED_WORK_ROLE
12. BUDGET_AND_STOP_BOUNDARIES
13. SOURCE_HANDLES_AND_CLAIM_CEILING

FOR EACH COORDINATE RETURN:

<COORDINATE>:
POSTURE: SUPPORTED | PARTIAL | ABSENT | UNRESOLVED
BASIS: one concise statement grounded only in supplied evidence

FINAL FIELDS:

BOUNDED_OPERATIVE_POSTURE:
PRESERVED | DEGRADED | LOST | UNRESOLVED

UNRESOLVED:
[...]

AUTHORITY_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

STOPPED:
YES


EVIDENCE_APERTURE:
CELL001R_B_WITHHELD_ONE

=== EVIDENCE 1: WORKFLOW UNIT ===
{
  "object_type": "WORKFLOW_UNIT_V1",
  "identity": {
    "work_item_id": "WORKCYCLE_STABILIZATION_001_RELATIONAL_COMPRESSION_W2",
    "campaign_id": "WORKCYCLE_STABILIZATION_001",
    "parent_work_item_id": "WORKCYCLE_STABILIZATION_001_COMPRESSION_W1",
    "operative_frame_ref": "783ef1058779b9e6715cd9a852e409d6a89e3f9b",
    "created_from_event": "PRESSURE_JUSTIFICATION_001"
  },
  "basis": {
    "basis_id": "WORKCYCLE_HOT_CONTEXT_REDUCTION_BASIS_001",
    "basis_type": "LOAD_BEARING_UNCERTAINTY",
    "statement": "The active workcycle is represented by overlapping hot prose that increases seat reconstruction and coordination burden.",
    "evidence_refs": [
      "docs/campaigns/workcycle_stabilization_001/SYMBOLIC_CONSEQUENCE_DECOMPOSITION_V0.md",
      "docs/campaigns/workcycle_stabilization_001/WORKCYCLE_STABILIZATION_CAMPAIGN_001.md",
      "docs/campaigns/workcycle_stabilization_001/PRESSURE_JUSTIFICATION_001_READY_TO_SEND.md"
    ],
    "desired_consequence": {
      "statement": "A smaller hot operative representation preserves the current campaign/workcycle/basis relations while exact originals remain cold and challengeable."
    },
    "current_obstruction": {
      "statement": "Seats must currently re-ingest multiple overlapping prose artifacts to reconstruct the same operative workflow semantics."
    },
    "relevance_test": {
      "question": "Would successful compression reduce live reconstruction burden while preserving bounded consequence and challengeability?",
      "failure_if_unanswered": true
    },
    "basis_status": "SUPPORTED"
  },
  "pressure_selection": {
    "pressure_id": "WORKCYCLE_RELATIONAL_COMPRESSION_PRESSURE_001",
    "target_distinction": {
      "lhs": "COLD_EXACT_EVIDENCE",
      "rhs": "HOT_OPERATIVE_STATE"
    },
    "selection_basis": "The distinction is load-bearing because current workflow continuity depends on recovering campaign, decomposition, justification, application, consequence, and stopping semantics without repeatedly loading redundant prose.",
    "expected_information_gain": {
      "statement": "Whether a substantially smaller representation can preserve the operative workflow relations required by a fresh seat."
    },
    "application_dependency": "If fresh reconstruction and conservation review match, the compressed artifact may become the preferred hot workcycle context while exact originals remain cold-retained.",
    "stop_if_resolved_by_existing_evidence": true,
    "priority_basis": "BLOCKS_RECONSTRUCTION",
    "load_bearing_effects": [
      "RECONSTRUCTION",
      "OBSERVABILITY",
      "BASIS"
    ]
  },
  "pressure_contract": {
    "allowed_operations": [
      "OBSERVE",
      "RECONSTRUCT",
      "COMPARE",
      "FALSIFY",
      "ADJUDICATE"
    ],
    "prohibited_operations": [
      "SELF_PROMOTE",
      "CREATE_AUTHORITY",
      "EXPAND_SCOPE_WITHOUT_BASIS",
      "SPAWN_UNBOUNDED_PRESSURES",
      "DELETE_SOURCE"
    ],
    "success_condition": {
      "statement": "Candidate bytes are smaller than the combined source bytes and a fresh independent seat reconstructs the bounded operative posture without load-bearing loss."
    },
    "failure_condition": {
      "statement": "Any required campaign identity, workcycle relation, authority boundary, stopping law, application/consequence relation, provenance handle, or reconstruction capability is lost."
    },
    "unresolved_condition": {
      "statement": "Fresh reconstruction cannot determine whether a potentially load-bearing relation survived."
    },
    "pressure_budget": {
      "max_rounds": 1,
      "max_branch_count": 1,
      "max_unresolved_children": 0
    }
  },
  "result": {
    "source_result_ref": null,
    "distinctions": [],
    "apparatus_failures": [],
    "semantic_failures": []
  },
  "qualification": {
    "adjudication_ref": null,
    "scientific_standing": "NONE",
    "authority_effect": "NONE",
    "qualification_basis": "",
    "unresolved_load_bearing_questions": [
      "fresh independent reconstruction required"
    ]
  },
  "application": {
    "required": true,
    "target_surface": "WORKFLOW",
    "proposed_change": {
      "statement": "Use the compressed candidate as the preferred hot workcycle reconstruction surface while retaining all exact source artifacts as cold evidence."
    },
    "executable_change_ref": null,
    "application_status": "NOT_YET_ELIGIBLE",
    "withholding_basis": "Requires independent reconstruction and conservation match."
  },
  "consequence_observation": {
    "required_if_applied": true,
    "expected_effect": "Future seats reconstruct the same bounded workcycle from materially less hot context while exact challenge handles remain available.",
    "observed_effect": null,
    "effect_class": "NOT_YET_OBSERVABLE",
    "evidence_refs": [],
    "regression_detected": false
  },
  "basis_reconciliation": {
    "original_basis_id": "WORKCYCLE_HOT_CONTEXT_REDUCTION_BASIS_001",
    "disposition": null,
    "remaining_gap": "Compression has not yet been executed or independently reconstructed.",
    "next_pressure_allowed": false,
    "next_pressure_basis": null,
    "termination_reason": null
  },
  "sanity_check": {
    "if_this_work_succeeds": {
      "what_changes_in_the_operating_world": "A fresh seat can recover the current workcycle with less active context, making the workflow cheaper to coordinate and reducing pressure to keep redundant documentation hot."
    },
    "if_nothing_would_change": {
      "posture": "DO_NOT_RUN"
    }
  }
}

=== EVIDENCE 2: CAMPAIGN ===
# WORKCYCLE STABILIZATION CAMPAIGN 001

OBJECT_TYPE:
DEVELOPMENT_CAMPAIGN_CANDIDATE

CAMPAIGN_ID:
WORKCYCLE_STABILIZATION_001

STANDING:
CANDIDATE_ONLY

EXECUTIVE_AUTOMATION:
PINNED / DEFERRED

AUTHORITY_EFFECT:
NONE

SCIENTIFIC_PROMOTION_EFFECT:
NONE

# 1. OBJECTIVE

Establish a boring, observable, repairable campaign→decomposition→seat-work
lifecycle in which DME_Lab can perform bounded useful work on itself without
Reed carrying currentness, routing, handoff narration, or low-level corrective
churn.

The first permanent workload is:

```
REPOSITORY / MEMORY COMPRESSION
+
HISTORY CONSERVATION
```

because this workload simultaneously:

- reduces contextual burden;
- pressures conservation directly;
- exposes meaningless artifact production quickly;
- exercises lineage, provenance, relation, and invariance reconstruction;
- creates operational rent even before executive automation exists.

# 2. PRIMARY LAW

```
SELF-MOVING BOUNDED WORK
!=
GENERAL AUTONOMY
```

and:

```
WORK COMPLETION
!=
CAMPAIGN PROGRESS
```

Progress requires observed consequence evaluated against the campaign/horizon
envelope.

# 3. ATLAS BASIS

Current provisional Atlas conservation surfaces:

1. IDENTITY / ADDRESS
2. MECHANICAL
3. SYMBOLIC / SEMANTIC
4. RELATIONAL / TOPOLOGICAL
5. CONSEQUENCE / ENVIRONMENTAL
6. PROVENANCE
7. INVARIANCE / META-CONSERVATION

Current provisional load dimensions:

```
L(x) = {
  functional,
  semantic,
  authority,
  provenance,
  temporal,
  coordination
}
```

Do not scalarize the load vector in this campaign.

The campaign treats these as pressure coordinates, not canonical universal
ontology.

# 4. CORE WORKCYCLE

```
EXISTING CAMPAIGN / RELATIONAL HORIZON
↓
DECOMPOSITION IDENTITY
↓
DETERMINISTIC WORK ITEM
↓
SEAT EXECUTION
↓
OBSERVED CONSEQUENCE
↓
CAMPAIGN-RELATIVE EVALUATION
↓
CONTINUE
| REPAIR DECOMPOSITION
| HOLD
| REPLAN
```

# 5. SCIENTIFIC DECOMPOSITION LOOP

Use the existing Atlas scientific cycle:

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

but apply it at two distinct levels.

## Executive / campaign level

For now this remains human/planner-led.

It determines:

- target;
- relevant relational horizon;
- campaign-level conservation envelope;
- allowed work-item classes;
- campaign stop/hold/replan boundaries.

## Work-item level

Seats may:

- reconstruct assigned state;
- execute one bounded transformation;
- observe local consequence;
- emit evidence/receipts;
- surface a typed repair need.

Seats may not:

- invent a new campaign target;
- widen authority;
- silently replan the campaign;
- self-promote scientific standing;
- continue indefinitely.

# 6. FIRST PERMANENT WORKLOAD — COMPRESSION / HISTORY CONSERVATION

Candidate metabolic loop:

```
OBSERVE BLOAT
↓
IDENTIFY LOAD-BEARING RELATIONS
↓
BOUND A COMPRESSION REGION
↓
PROJECT A SMALLER REPRESENTATION
↓
TRANSFORM / REDUCE
↓
RECONSTRUCT FROM REDUCED FORM
↓
COMPARE AGAINST ORIGINAL BASIS
↓
CHECK SEVEN CONSERVATION SURFACES
↓
CHECK SIX LOAD DIMENSIONS
↓
DETECT LOSS / LOAD REDISTRIBUTION
↓
ACCEPT CANDIDATE
| REPAIR COMPRESSION
| HOLD
↓
COLD-RETAIN ORIGINAL BASIS
```

Early compression is non-destructive.

```
COMPRESSED CANDIDATE
!=
DELETION AUTHORITY
```

# 7. FIRST CAMPAIGN PRESSURE FAMILY

## CELL 001 — LOAD_TRANSFER mechanical closure

Target:
LOAD_TRANSFER_001 deterministic tests pass.

## CELL 002 — real two-seat handoff

Target:
Seat A→Seat B handoff succeeds without Reed narrating the transition.

## CELL 003 — campaign decomposition identity

Target:
one work item proves that it is a bounded decomposition of one exact addressed
campaign/horizon.

## CELL 004 — expected vs observed consequence

Target:
work completion carries a separately witnessed expected consequence and observed
consequence.

## CELL 005 — conservation envelope

Target:
a work result can be tested over the seven provisional conservation surfaces and
six load dimensions without scalarizing them.

## CELL 006 — typed repair routing

Target:
distinguish output defect, decomposition defect, campaign defect, and apparatus
defect.

## CELL 007 — compression specimen

Target:
reduce one bounded documentation/history region while preserving reconstructable
operative posture and exact cold-source challengeability.

## CELL 008 — operator visibility

Target:
Cockpit/operator projection can show current campaign, work state, seat,
conservation debt, consequence posture, blocker, next eligible destination,
budget, and whether Reed needs to act.

# 8. SUCCESS CONDITION

The campaign begins to succeed when:

```
REED EXPLAINS CURRENT STATE:
NO

REED ROUTES ROUTINE WORK:
NO

SEATS CREATE BOUNDED CONSEQUENCE:
YES

CONSEQUENCE IS OBSERVABLE:
YES

CONSERVATION FAILURE IS LEGIBLE:
YES

REPAIR DESTINATION IS TYPED:
YES

AUTHORITY CROSSINGS STILL REQUIRE REED:
YES
```

# 9. BUDGET POSTURE

Real self-moving work requires bounded consequence capacity.

A budget plane is therefore required before automatic continuation.

Initial budget must remain vector-valued / typed rather than one universal
currency.

Candidate coordinates:

- maximum work items per wake;
- maximum seat invocations per campaign step;
- maximum repository mutation scope;
- maximum changed bytes/files;
- maximum model/token/tool expenditure where measurable;
- maximum unresolved debt tolerated before HOLD;
- maximum repair attempts;
- authority class permitted;
- wall-clock / external-cost ceiling where relevant.

Freeze:

```
BUDGET EXHAUSTION
!=
CAMPAIGN FAILURE

BUDGET
!=
AUTHORITY

AVAILABLE BUDGET
!=
PERMISSION TO SPEND IT
```

# 10. MULTI-SEAT POSTURE

Do not treat a seat as a model instance.

Future relation:

```
SEAT
=
ROLE + STATE + CONTRACT + CURRENT WORK COORDINATE

OCCUPANT
=
ONE MODEL / HUMAN / TOOL REALIZATION
THAT MAY TEMPORARILY OCCUPY THE SEAT
```

Therefore:

```
MULTIPLE LLMs WANT SAME SEAT
→ occupancy / lease arbitration required

ONE LLM MAY OCCUPY MULTIPLE SEATS
→ role/state boundaries must remain explicit
```

Current campaign does not implement concurrent occupancy.

Before concurrency, pressure:

- one current occupant per consequence-producing seat coordinate;
- explicit lease / attempt identity;
- stale occupant fencing;
- succession;
- budget reservation;
- one-shot consequence authority where applicable.

# 11. ATLAS CONTROL / VISIBILITY TARGET

The Atlas should not be imagined as "always thinking."

Candidate posture:

```
ATLAS STATE:
persistently addressable

SEAT:
quiescent unless occupied / woken

WORK:
inactive unless eligible and admitted

WAKE:
event / explicit request / later lawful scheduler

CONTROL:
operator-visible and bounded
```

Future Cockpit controls may expose:

- seat active / inactive / held;
- occupant / lease identity;
- current work item;
- campaign/horizon;
- budget consumed / remaining;
- wake request;
- stop / pause;
- blockers;
- latest receipts;
- unresolved conservation debt.

Control representation does not itself create authority.

# 12. STOP MEMBRANE

Do not build yet:

- autonomous campaign assembly;
- generic executive planner;
- unbounded free-running agents;
- broad automatic filesystem cleanup;
- destructive compression;
- silent task creation;
- unlimited repair loops;
- concurrent seat occupancy without fencing;
- scalar trust / load / budget score;
- automatic scientific promotion.

# 13. CURRENT NEXT PRESSURE

After LOAD_TRANSFER_001 mechanical tests pass:

```
RUN ONE REAL TWO-SEAT HANDOFF
```

Then use a bounded compression specimen as the first campaign-derived real work
object.

The campaign should be judged by whether it reduces human and repository load
while increasing reconstructability, not by artifact count.


=== EVIDENCE 3: PRESSURE JUSTIFICATION ===
# WORKCYCLE_STABILIZATION_001 — PRESSURE JUSTIFICATION 001

OBJECT_TYPE:
READY_TO_SEND_PRESSURE_PACKET

PRESSURE_ID:
PRESSURE_JUSTIFICATION_001

ROLE:
INDEPENDENT_BASIS_PRESSURE_EVALUATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
NO_EXECUTION
+
NO_WORK_ADMISSION
+
NO_CAMPAIGN_REPLAN

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# TARGET

Pressure the candidate law:

```
WORK
=
JUSTIFIED TRANSFORMATION
OF A LOAD-BEARING RELATIONAL HORIZON
```

Science is an instrument inside a basis-governed consequence loop.

The evaluator must distinguish:

```
DISCOVERABLE DISTINCTION
!=
RELEVANT DISTINCTION
!=
LOAD-BEARING DISTINCTION
!=
ACTIONABLE DISTINCTION
```

and:

```
HORIZON_MATCHED
!=
PRESSURE_JUSTIFIED

PRESSURE_JUSTIFIED
!=
WORK_ADMITTED
```

# USE ONLY

1. `src/cockpit/pressure_justification.py`
2. `src/cockpit/temporal_horizon_closure.py`
3. `src/cockpit/workcycle_qualification.py`
4. `src/cockpit/workcycle_projection.py`
5. `docs/campaigns/workcycle_stabilization_001/WORKCYCLE_STABILIZATION_CAMPAIGN_001.md`
6. current deterministic output of `python tools/project_workcycle_v0.py`

# REQUIRED CASES

## A — CURRENT LOAD-BEARING CELL

A declared T7 pressure exists while T7 is not BOUNDED_PASS.

Expected:

```
pressure_posture: JUSTIFIED
proposed_pressure: T7_PRESSURE
next_work_posture: RESOLVE_LOAD_BEARING_GAP
if_nothing_changes: DO_NOT_RUN
```

## B — HORIZON UNRESOLVED

The temporal/current/upcoming basis is unresolved.

Expected:

```
pressure_posture: UNRESOLVED
next_work_posture: HOLD_NO_JUSTIFIED_WORK
```

No work proposal may become admitted.

## C — DECLARED AUTO-CONTINUATION BUT BOUNDED DEBT REMAINS

Declared next pressure is AUTO_CONTINUATION_PRESSURE, but bounded qualification
still has:

```
TEMPORAL_HORIZON:UNFROZEN
```

Expected:

```
proposed_pressure: TEMPORAL_HORIZON_ADJUDICATION
```

The basis governor must prevent premature self-motion.

## D — NO LOAD-BEARING BLOCKER

No bounded or self-moving qualification blocker remains.

Expected:

```
pressure_posture: ALREADY_RESOLVED
next_work_posture: HOLD_NO_JUSTIFIED_WORK
proposed_pressure: NONE
```

# BASIS RECORD

The basis must bind:

- campaign identity;
- active relational horizon;
- horizon disposition;
- declared next pressure;
- current unresolved load;
- bounded qualification blockers;
- self-moving qualification blockers;
- seven conservation surfaces;
- six load dimensions.

The basis ID must be deterministic over the same bounded coordinates.

# REQUIRED NON-COLLAPSES

```
DIRECTORY_TOPOLOGY
!=
RELATIONAL_TOPOLOGY

TEMPORAL_SUCCESSION
!=
CAUSATION

QUALIFICATION_DEBT
!=
EXECUTION_AUTHORITY

JUSTIFIED PRESSURE
!=
ADMITTED WORK

NO JUSTIFIED WORK
!=
SYSTEM FAILURE
```

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

CASE_A:
CASE_B:
CASE_C:
CASE_D:

BASIS_IDENTITY_DETERMINISTIC:
LOAD_BEARING_RELATION_LEGIBLE:
IF_RESOLVED_CHANGE_LEGIBLE:
DO_NOT_RUN_POSTURE_LEGIBLE:

PRESSURE_POSTURE:
JUSTIFIED
| ALREADY_RESOLVED
| NON_LOAD_BEARING
| UNRESOLVED

NEXT_WORK_POSTURE:
APPLY_QUALIFIED_RESULT
| OBSERVE_APPLICATION_CONSEQUENCE
| RESOLVE_LOAD_BEARING_GAP
| CLOSE_BASIS
| HOLD_NO_JUSTIFIED_WORK

DISPOSITION:
PRESSURE_JUSTIFICATION_MATCHED
| PRESSURE_JUSTIFICATION_PARTIAL
| PRESSURE_JUSTIFICATION_FRACTURED
| PRESSURE_JUSTIFICATION_UNRESOLVED

UNRESOLVED:
AUTHORITY_EFFECT:
EXECUTION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:
STOPPED:
```

