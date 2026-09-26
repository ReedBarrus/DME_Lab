# G19 Pressure 001 Ready To Run

PRESSURE_ID:
RELATIONAL_CHANGE_STEWARDSHIP_V0_PRESSURE_001

PLAIN_ENGLISH_TARGET:

A local transformation is not allowed to close a relation merely because the
edited endpoint changed successfully.

The system must also check declared counterpart/edge obligations and any required
flow witness.

PROTOCOL:
docs/methods/RELATIONAL_CHANGE_STEWARDSHIP_PROTOCOL_V0.md

PROTOCOL_BLOB:
bbef9bc0a6812bc714146fe762abe045cbe37684

STEWARD:
src/control/relational_change_steward_v0.py

STEWARD_BLOB:
8dddd57779d2432dd87c92ce95056dee2be398b5

HORIZON_SELECTION_BLOB:
e06c0600f7ed2662318e40d4b0a50916a0807666

CONTRACT_BLOB:
b193ffdb37da4e263752a878b13aeb294f502b13

OBSERVER_BLOB:
a7cd8f39375a39393adf484515fa866bd1e9e26a

RUN:

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item docs/evidence/for_planner/relational_change_stewardship_v0_observation.json -ErrorAction SilentlyContinue

python tools/observe_relational_change_stewardship_v0.py
```

EXPECTED:

C1_COHERENT -> COHERENT
C2_MISSING_FLOW -> HOLD
C3_COUNTERPART_DRIFT -> HOLD
C4_UNRESOLVED -> UNRESOLVED
all_cases_match True

OUTPUT:

docs/evidence/for_planner/relational_change_stewardship_v0_observation.json

TARGET_RELATION:

LOCAL_TRANSFORMATION_SUCCESS != RELATIONAL_CLOSURE

DO NOT INFER:

relation discovery
automatic propagation semantics
planning activation
mutation authority
work admission
execution
global relational coherence

STOP:
after producing the observation.
