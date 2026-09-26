# Atlas Relational / Topology Slice V0 Pressure 001 — Ready To Run

PRESSURE_ID:
ATLAS_RELATIONAL_TOPOLOGY_SLICE_V0_PRESSURE_001

LEVERAGE_SOUGHT:

Test whether the planner-selected H1/H2 relational basis can be carried in one
read-only Atlas-shaped slice without flattening the local relation into the
surrounding topology, erasing the represented-versus-qualified gap, hiding the
unresolved exterior, or promoting Atlas into the operative world.

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

SLICE_MODEL:
src/cockpit/observer/atlas_relational_topology_slice.mjs

SLICE_MODEL_BLOB:
785a108cb454c67d9fc0887e87fbcd1e9a9a4393

SLICE_SPECIMEN:
docs/campaigns/atlas_relational_integration_001/specimens/
ATLAS_RELATIONAL_TOPOLOGY_SLICE_V0.json

SLICE_SPECIMEN_BLOB:
56b17fbddade245af29175e34e9301ea176252da

HORIZON_BLOB:
2e4196d297c8837dd30ad39d6b71522bfdef947e

CONTRACT_BLOB:
4a28d09c9c5d7b52031afcdbe485913facb2a4e7

OBSERVER:
tools/observe_atlas_relational_topology_slice_v0.mjs

OBSERVER_BLOB:
c9379feb1b110643184fd97c169e8714c87f47fb

CASES:

S0_CONTROL
expected:
BOUNDED_SLICE_READY

A1_FLATTEN_LOCAL_INTO_TOPOLOGY
expected:
HOLD_LOCAL_RELATION_LOST

A2_REMOVE_SURROUNDING_TOPOLOGY
expected:
HOLD_SURROUNDING_TOPOLOGY_LOST

A3_REMOVE_REPRESENTED_QUALIFIED_GAP
expected:
HOLD_TOPOLOGY_GAP_LOST

A4_CLOSE_UNRESOLVED_EXTERIOR
expected:
HOLD_UNRESOLVED_EXTERIOR_LOST

A5_DECLARE_PROJECTION_OPERATIVE_WORLD
expected:
HOLD_PROJECTION_WORLD_COLLAPSE

CONTROL MUST PRESERVE:

- local relation;
- surrounding topology;
- represented topology;
- qualified specimen topology;
- explicit represented-versus-qualified gap;
- OPEN unresolved exterior;
- relation-driven Atlas semantics;
- derived-projection posture;
- neutral authority / execution / control effects.

RUN:

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item docs/evidence/for_planner/atlas_relational_topology_slice_v0_observation.json -ErrorAction SilentlyContinue

node tools/observe_atlas_relational_topology_slice_v0.mjs
```

EXPECTED STDOUT:

```text
[OK] wrote docs/evidence/for_planner/atlas_relational_topology_slice_v0_observation.json
[OK] S0_CONTROL -> BOUNDED_SLICE_READY
[OK] A1_FLATTEN_LOCAL_INTO_TOPOLOGY -> HOLD_LOCAL_RELATION_LOST
[OK] A2_REMOVE_SURROUNDING_TOPOLOGY -> HOLD_SURROUNDING_TOPOLOGY_LOST
[OK] A3_REMOVE_REPRESENTED_QUALIFIED_GAP -> HOLD_TOPOLOGY_GAP_LOST
[OK] A4_CLOSE_UNRESOLVED_EXTERIOR -> HOLD_UNRESOLVED_EXTERIOR_LOST
[OK] A5_DECLARE_PROJECTION_OPERATIVE_WORLD -> HOLD_PROJECTION_WORLD_COLLAPSE
[OK] all_expectations_match true
```

OUTPUT:

docs/evidence/for_planner/atlas_relational_topology_slice_v0_observation.json

TARGET CANDIDATE RELATIONS:

ATLAS_RELATIONAL_SLICE_CAN_PRESERVE_DECLARED_RELATIONAL_COORDINATES

LOCAL_RELATION_COORDINATE
!=
UNDIFFERENTIATED_RELATION_BAG

REPRESENTED_QUALIFIED_GAP
MUST_REMAIN_EXPLICIT_FOR_THIS_SLICE

UNRESOLVED_EXTERIOR
MUST_REMAIN_VISIBLE_FOR_THIS_SLICE

ATLAS_PROJECTION_IDENTITY
!=
OPERATIVE_WORLD_IDENTITY

PRESERVE:

ATLAS PROJECTION != OPERATIVE WORLD

QUALIFIED SPECIMEN TOPOLOGY != UNIVERSAL TOPOLOGY

RELATIONAL SLICE != RELATION DISCOVERY

LOCAL RELATION != FULL TOPOLOGY

REPRESENTED TOPOLOGY != QUALIFIED SPECIMEN TOPOLOGY

UNRESOLVED EXTERIOR != KNOWN ABSENCE OF RELATIONS

FIELD-SLICE READINESS != PLANNING AUTHORITY

FIELD-SLICE READINESS != WORK ADMISSION

FIELD-SLICE READINESS != EXECUTION

DO NOT:

modify the Atlas renderer

infer new relations

activate planning ecology

admit work

grant authority

execute transformations

create scientific standing

NEXT IF MATCHED:

Freeze + independent adjudication.

Then review whether the qualified slice should:
- enter the existing Atlas renderer as an optional overlay;
- feed H3 trajectory pressure;
- or remain a machine-facing carrier while another planner pressure chooses.

Do not assume renderer integration is next merely because this data-model
pressure passes.

STOP:
after producing and pushing the one observation.
