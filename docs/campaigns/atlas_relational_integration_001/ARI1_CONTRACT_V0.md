# Atlas Relational / Topology Slice Contract V0

PRESSURE_ID:
ATLAS_RELATIONAL_TOPOLOGY_SLICE_V0_PRESSURE_001

FROZEN BASIS:

PLANNER_RESULT_BLOB:
67359516883662ad5ef02c5db71e279cc148bad4

H1_ADJUDICATION_BLOB:
d0fa23ee2301024e9a6b96dede95ec62b253156f

H2_ADJUDICATION_BLOB:
fc789514c9276f3857add4fe90402553d70b441d

ATLAS_GEOMETRY_BLOB:
b2b8ccdd3854c15f586c1af609847a1baf655977

ATLAS_MODEL_BLOB:
e13e50e410f8bd72cf26ce8d9cfce1a6f90cdd44

ATLAS_APP_BLOB:
81ac50e6858ad7fac44cc2e59ea964d0c71705ad

SLICE_MODEL_BLOB:
785a108cb454c67d9fc0887e87fbcd1e9a9a4393

SLICE_SPECIMEN_BLOB:
56b17fbddade245af29175e34e9301ea176252da

REQUIRED CASES:

S0_CONTROL
=
BOUNDED_SLICE_READY

A1_FLATTEN_LOCAL_INTO_TOPOLOGY
=
HOLD_LOCAL_RELATION_LOST

A2_REMOVE_SURROUNDING_TOPOLOGY
=
HOLD_SURROUNDING_TOPOLOGY_LOST

A3_REMOVE_REPRESENTED_QUALIFIED_GAP
=
HOLD_TOPOLOGY_GAP_LOST

A4_CLOSE_UNRESOLVED_EXTERIOR
=
HOLD_UNRESOLVED_EXTERIOR_LOST

A5_DECLARE_PROJECTION_OPERATIVE_WORLD
=
HOLD_PROJECTION_WORLD_COLLAPSE

CONTROL MUST PRESERVE:

local relation
surrounding topology
represented topology
qualified specimen topology
explicit represented-versus-qualified gap
OPEN unresolved exterior
exact basis handles
Atlas projection semantics
neutral authority / execution / control effects

REQUIRED EFFECTS:

relation_discovery_effect = NONE
renderer_integration_effect = NONE
work_admission_effect = NONE
planning_activation_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE

DO NOT INFER:

operative-world completeness
universal topology law
automatic relation discovery
trajectory/history load
renderer correctness
planning authority
work admission
execution
scientific standing

STOP:
after one control plus five ablation observations.
