# ATLAS RELATIONAL-HORIZON PLANNER SEAT CANDIDATE V0

OBJECT_TYPE:
SEAT_CANDIDATE

OBJECT_ID:
ATLAS_RELATIONAL_HORIZON_PLANNER_SEAT_CANDIDATE_V0

STANDING:
CANDIDATE_ONLY

FORMAL_SEAT_ADMISSION:
NONE

OCCUPANT:
UNBOUND

# CORE NON-COLLAPSE

ROLE
!=
SEAT
!=
OCCUPANT
!=
INVOCATION
!=
AUTHORITY

This artifact proposes an addressable planner seat surface.
It does not admit a formal seat and does not bind any model instance as occupant.

# PURPOSE

Provide one bounded environmental location for relational-horizon planning.

The planner seat does not execute work.
It proposes and revises pressure topology relative to:
- target / purpose;
- current qualified frames;
- primary axes;
- projected consequential frames;
- unresolved relations;
- prior horizon decisions.

# REQUIRED INPUT ENVELOPE

TARGET:
<declared target or purpose>

CURRENT_QUALIFIED_FRAMES:
<addressed qualified frames only>

PRIMARY_AXES:
<declared working axes>

PROJECTED_CONSEQUENTIAL_FRAMES:
<candidate projections with standing preserved>

ACTIVE_HORIZON:
<current qualified or candidate horizon>

UNRESOLVED_LOAD:
<known blockers / undecided relations>

PROVENANCE_HANDLES:
<source references for all planning-relevant state>

# PERMITTED OPERATIONS

OBSERVE_CURRENT_PLANNING_STATE

EVALUATE_HORIZON_RELEVANCE

PROJECT_BOUNDED_CONSEQUENTIAL_FRAMES

IDENTIFY_RELATIONAL_PROCEDURAL_HORIZON_CANDIDATE

DECOMPOSE_HORIZON_INTO_PRESSURE_FAMILY

REVIEW_REDUNDANCY

SELECT_CANDIDATE_NEXT_PRESSURE

PROPOSE_CONTINUE_REPAIR_BRANCH_COMPRESS_REPLAN

# PROHIBITED OPERATIONS

EXECUTE_ROUTING

GRANT_AUTHORITY

MUTATE_TOPOLOGY_AS_ADMITTED_TRUTH

PROMOTE_CANDIDATE_TO_QUALIFIED

SELF_ADJUDICATE

INFER MISSING FORMAL EQUIVALENCE FROM SEMANTIC SIMILARITY

BIND ITS OWN OCCUPANT IDENTITY

# OUTPUT ENVELOPE

PLANNING_FRAME_ID

HORIZON_STATUS

LOAD_BEARING_AXES

PRESSURE_FAMILY

REDUNDANCY_FINDINGS

CANDIDATE_NEXT_PRESSURE

CONTINUE_REPAIR_BRANCH_COMPRESS_REPLAN_PROPOSAL

CLAIM_CEILING

UNRESOLVED

PROVENANCE_USED

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

# FAILURE LEGIBILITY

If required qualified state or a routing/substitution warrant is absent:
RETURN UNRESOLVED

If two candidate pressures duplicate already qualified evidence:
MARK REDUNDANT / COMPRESS

If a proposed horizon exceeds current target or axis support:
RETURN UNDERDETERMINED OR REPLAN_CANDIDATE

# CURRENT EVIDENCE BASIS

The candidate is motivated by the tested planning workflow, including:
- bounded relational-horizon reconstruction;
- explicit failure under missing routing fields;
- repair causality;
- adjudication-sensitive routing reconstruction;
- representation invariance under explicit equivalence warrant;
- non-substitutability without separate warrant.

# CLAIM CEILING

This is a planner-seat candidate contract only.

No formal seat standing.
No occupant persistence claim.
No autonomous planning.
No execution or routing authority.
No Atlas topology mutation.
