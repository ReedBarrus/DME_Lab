# WORKCYCLE_STABILIZATION_001 — ATLAS TEMPORAL-HORIZON CLOSURE 001

OBJECT_TYPE:
READY_TO_SEND_HORIZON_PRESSURE_PACKET

PRESSURE_ID:
ATLAS_TEMPORAL_HORIZON_CLOSURE_001

ROLE:
INDEPENDENT_RELATIONAL_HORIZON_EVALUATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
NO_EXECUTION
+
NO_CAMPAIGN_REPLAN
+
NO_AUTHORITY_GRANT

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# TARGET

Pressure whether Atlas can derive one bounded, challengeable relational-horizon
candidate from three distinct temporal coordinates:

```
HISTORY
+
CURRENT OPERATIVE WORKCYCLE
+
DECLARED UPCOMING WORK
→
RELATIONAL HORIZON CANDIDATE
```

without collapsing history into causation, projection into standing, or horizon
into execution authority.

# REQUIRED EVIDENCE

Use only:

1. `generated/repository_temporal_lineage.json`
2. `generated/repository_address_fabric.json`
3. `docs/campaigns/workcycle_stabilization_001/WORKCYCLE_STABILIZATION_CAMPAIGN_001.md`
4. `docs/campaigns/workcycle_stabilization_001/decomposition/WORKCYCLE_STABILIZATION_001_D001.json`
5. `docs/campaigns/workcycle_stabilization_001/decomposition/WORKCYCLE_STABILIZATION_001_COMPRESSION_W1.json`
6. `docs/campaigns/workcycle_stabilization_001/state/WORKCYCLE_STABILIZATION_001_COMPRESSION_W1_OBSERVED_CONSEQUENCE.json`
7. `docs/campaigns/workcycle_stabilization_001/state/WORKCYCLE_STABILIZATION_001_COMPRESSION_W1_CONSEQUENCE_EVALUATION.json`
8. `docs/campaigns/workcycle_stabilization_001/state/WAKE_BUDGET_V0.json`
9. `docs/campaigns/workcycle_stabilization_001/state/REPAIR_ROUTING_PRESSURE_SPEC_001.json`
10. `src/cockpit/development_horizon_projection.py`
11. `src/cockpit/workcycle_projection.py`

Do not use chat history as evidence.

# THREE TEMPORAL COORDINATES

The evaluator must distinguish:

## HISTORY

Exact prior transitions / frames / source handles that establish what changed.

```
TEMPORAL SUCCESSION
!=
SEMANTIC CAUSATION
```

## CURRENT

Current operative projection:
- campaign/workcycle posture;
- latest completed work;
- current unresolved debt;
- wake-budget posture;
- local-control posture if present;
- active/occupied seat state if present.

```
CURRENT PROJECTION
!=
SCIENTIFIC STANDING
```

## UPCOMING

Only already-declared next pressures/work relations may be used.

```
DECLARED UPCOMING WORK
!=
AUTOMATIC EXECUTION
```

# HORIZON CANDIDATE

Return at most one primary candidate:

```
H =
(
  subject_scope,
  support_predicate,
  current_supported_region,
  boundary_condition,
  pressure_direction,
  evidence_handles,
  applicable_distinctions,
  load_dimensions,
  conservation_surfaces_at_risk,
  unresolved_boundary,
  claim_ceiling
)
```

The candidate may be one of the existing families:

- H_observe
- H_correct
- H_reconstruct
- H_authority
- H_operate

or a more precise bounded subtype if required.

Do not invent a generic scalar horizon score.

# SEVEN-SURFACE PRESSURE

For the chosen horizon candidate, explicitly state the current consequence
potential across all seven provisional surfaces:

1. IDENTITY / ADDRESS
2. MECHANICAL
3. SYMBOLIC / SEMANTIC
4. RELATIONAL / TOPOLOGICAL
5. CONSEQUENCE / ENVIRONMENTAL
6. PROVENANCE
7. INVARIANCE / META-CONSERVATION

Allowed posture per surface:

```
SUPPORTED
AT_RISK
UNRESOLVED
NOT_APPLICABLE
```

Every non-NOT_APPLICABLE posture must cite exact repository evidence handles.

# SIX LOAD DIMENSIONS

Review separately:

- functional
- semantic
- authority
- provenance
- temporal
- coordination

Do not scalarize.

For each load dimension identify:
- load-bearing relation/object;
- why it matters at the candidate horizon;
- whether load is increasing, decreasing, redistributed, or unresolved.

# DISTINCTION BASIS

Identify the minimum distinctions required to make the horizon operable.

Examples may include, only if evidence supports them:

```
HISTORY != CURRENTNESS

TEMPORAL SUCCESSION != CAUSATION

LATEST COMPLETED != ACTIVE

PARTIAL ELIGIBILITY != REAL ELIGIBILITY

REPO REQUESTED CONTROL != OPERATIVE LOCAL CONTROL

REGISTERED SEAT != LIVE OCCUPANT != EXECUTION AUTHORITY

WAKE REQUEST != WORK ADMISSION != MODEL INVOCATION

WORK COMPLETION != CAMPAIGN ADVANCE
```

# NEXT-WORK CANDIDATE

After the horizon is derived, propose at most ONE bounded next-work candidate.

It must specify:

```
campaign/horizon handle
addressed region
applicable distinctions
bounded operator
expected consequence
seven-surface conservation envelope
six-load review debt
authority requirement
wake-budget requirement
evidence debt
stop condition
repair destination
```

The candidate is not admitted merely because it is proposed.

# FAILURE CONDITIONS

Return HOLD if:

- temporal evidence is missing/stale;
- current projection cannot be reconstructed;
- upcoming work is not declared;
- horizon support depends on hidden chat context;
- a surface/load posture cannot be challengeably supported;
- next-work relevance requires speculative causation.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

HISTORY_POSTURE:
CURRENTNESS_POSTURE:
UPCOMING_WORK_POSTURE:

PRIMARY_HORIZON_FAMILY:
HORIZON_SUBJECT:
SUPPORT_PREDICATE:
BOUNDARY_CONDITION:
PRESSURE_DIRECTION:

SEVEN_SURFACES:
IDENTITY_ADDRESS:
MECHANICAL:
SYMBOLIC_SEMANTIC:
RELATIONAL_TOPOLOGICAL:
CONSEQUENCE_ENVIRONMENTAL:
PROVENANCE:
INVARIANCE_META:

SIX_LOAD_DIMENSIONS:
FUNCTIONAL:
SEMANTIC:
AUTHORITY:
PROVENANCE_LOAD:
TEMPORAL:
COORDINATION:

DISTINCTIONS_APPLIED:

NEXT_WORK_CANDIDATE:
EXPECTED_CONSEQUENCE:
AUTHORITY_REQUIREMENT:
WAKE_BUDGET_REQUIREMENT:
STOP_CONDITION:
REPAIR_DESTINATION:

DISPOSITION:
HORIZON_MATCHED
| HORIZON_PARTIAL
| HORIZON_FRACTURED
| HORIZON_UNRESOLVED

UNRESOLVED:
AUTHORITY_EFFECT:
EXECUTION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:
STOPPED:
```
