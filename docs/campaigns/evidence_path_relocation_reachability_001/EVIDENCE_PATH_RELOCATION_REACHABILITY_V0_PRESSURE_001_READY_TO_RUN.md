# G16 Pressure 001 Ready To Run

PRESSURE_ID:
EVIDENCE_PATH_RELOCATION_REACHABILITY_V0_PRESSURE_001

LEDGER_BLOB:
5f665ec27f07c46c83ca8427aa5a8697d2276253

HORIZON_SELECTION_BLOB:
7f71e9fbb65b3362733bdc4b6e401f4b33bcdc5a

CONTRACT_BLOB:
158b77a086fef0026cf6dff312ca79b7a66ea156

OBSERVER_BLOB:
812b0a4ab1334445a29c2026a2a28f7227bc7856

PRE_MOVE_SOURCE:
cf2d62f175bfae784d3755dc83ab7ea1d4e33b2f

RELOCATION_COMMIT:
2ea35acb8d4fb61f55f4725a5af72510746460b5

RELOCATION_INVENTORY_BLOB:
b5401152ef89b209e535c49ca4e989e32095ced3

TARGET_RELATION:
CONTENT_IDENTITY_PRESERVATION != WITNESS_PATH_REACHABILITY

RUN:

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item docs/evidence/for_planner/evidence_path_relocation_reachability_v0_observation.json -ErrorAction SilentlyContinue

python tools/observe_evidence_path_relocation_reachability_v0.py
```

EXPECTED:

cases = 6
control = True
old paths absent = True
new paths exact = True
content preserved = True
route break = True

OUTPUT:

docs/evidence/for_planner/evidence_path_relocation_reachability_v0_observation.json

REQUIRED_NONCOLLAPSES:

BLOB_IDENTITY_PRESERVED != PATH_HANDLE_PRESERVED
PATH_RELOCATION != EVIDENCE_LOSS
PATH_RELOCATION != SCIENTIFIC_STANDING_CHANGE
REFERENCE_BREAKAGE != CLAIM_FALSIFICATION
RECOVERABLE_BY_INVENTORY != ORIGINAL_PATH_STILL_VALID

CLAIM_CEILING:

One bounded repository-path relocation pressure over six invariant-ledger witness
references only. No automatic reference rewriting, generic relocation resolver,
archive policy, cold-storage admission, source deletion, planning, authority,
execution, or scientific standing.

STOP:
after producing the observation
