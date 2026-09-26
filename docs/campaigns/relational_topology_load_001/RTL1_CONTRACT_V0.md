# Relational Topology Load Contract V0

PRESSURE_ID:
RELATIONAL_TOPOLOGY_LOAD_V0_PRESSURE_001

H1_ADJUDICATION_BLOB:
d0fa23ee2301024e9a6b96dede95ec62b253156f

PROJECTION_BLOB:
c09a78d496a0df65ec9570ee05bfbd6d21f5f80a

TOPOLOGY_EVALUATOR_BLOB:
810d05ed8dfdfb72b7b6e2cc052d511ac8d8a865

FIXED_LOCAL_RELATION:

FOCAL = A -> B
FOCAL_LOAD = 2
B_INCOMING_CAPACITY = 3

T0:

FOCAL = A -> B load 2
CONTEXT = C -> D load 2

expected:
SUPPORTED

T1:

FOCAL = A -> B load 2
CONTEXT = C -> B load 2

expected:
HOLD

required T0/T1 equivalences:

- same nodes;
- same node capacities;
- exact same focal relation;
- same focal endpoint-local state;
- same edge count;
- same global edge-load multiset.

required T0/T1 difference:

- only the surrounding context relation target changes.

T2:

bijective topology-symbol renaming of T1 preserving directed incidence,
capacity, load, and focal-edge role.

expected:
HOLD

normalized topology consequence signature:
must equal T1

T3:

operative topology = T1

represented topology = T1 with CONTEXT omitted

expected operative consequence:
HOLD

expected represented prediction:
SUPPORTED

local focal relation in both:
identical

REQUIRED_CANDIDATE_RELATIONS_IF_MATCHED:

LOCAL_RELATION_STATE_EQUIVALENCE_NE_TOPOLOGICAL_CONSEQUENCE_EQUIVALENCE = YES

QUALIFIED_TOPOLOGICAL_CONSEQUENCE_INVARIANT_UNDER_BIJECTIVE_RENAMING = YES

REPRESENTED_RELATIONAL_TOPOLOGY_NE_OPERATIVE_RELATIONAL_TOPOLOGY = YES

UNREPRESENTED_COUPLING_CAN_CARRY_CONSEQUENCE_WITHIN_DECLARED_HORIZON = YES

RELATIONAL_TOPOLOGY_CARRIES_CONSEQUENTIAL_LOAD_BEYOND_ISOLATED_LOCAL_RELATION = YES

REQUIRED_EFFECTS:

relation_discovery_effect = NONE
trajectory_law_effect = NONE
planning_effect = NONE
seat_identity_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE

DO_NOT_INFER:

universal topology law
causal ontology
global coupling
physical validation
trajectory/history load
planning activation
seat identity law
authority
execution
global invariance
scientific standing

STOP:
after producing one T0-T3 observation.
