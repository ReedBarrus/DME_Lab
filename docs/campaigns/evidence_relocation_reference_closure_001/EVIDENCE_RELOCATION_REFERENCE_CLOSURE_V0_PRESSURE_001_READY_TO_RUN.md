# G17 Pressure 001 Ready To Run

PRESSURE_ID:
EVIDENCE_RELOCATION_REFERENCE_CLOSURE_V0_PRESSURE_001

LEDGER_BLOB:
1b28599b0e69844617f76cee47dabf5577c6baed

PREDECESSOR:
G16 / EVIDENCE_PATH_RELOCATION_REACHABILITY_V0_MATCHED

EARNED_INVARIANT:
EMI-015 / CONTENT_IDENTITY_PRESERVATION != WITNESS_PATH_REACHABILITY

REPAIR_RECEIPT:
docs/campaigns/evidence_path_relocation_reachability_001/repairs/EVIDENCE_PATH_ROUTE_REPAIR_001.md

REPAIR_RECEIPT_BLOB:
654949d1b726085d08eac2792b6a062ce21abfaa

HORIZON_SELECTION_BLOB:
937fdabc662c4bf2fe3246bf3c7b5895131361eb

CONTRACT_BLOB:
d02d691269c8904891301a6acfc3c9245d04d7e9

OBSERVER_BLOB:
08f7593e5c4dddfabf70ea61183b3cc54d018b1f

SOURCE_INVENTORY:
docs/evidence/for_planner/ROOT_EVIDENCE_INVENTORY.md

MOVED_ARTIFACT_COUNT:
37

TARGET:
MECHANICALLY INVENTORY TRACKED-TREE REFERENCES TO THE 37 RELOCATED ROOT ARTIFACTS

RUN:

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item docs/evidence/for_planner/evidence_relocation_reference_closure_v0_observation.json -ErrorAction SilentlyContinue

python tools/observe_evidence_relocation_reference_closure_v0.py
```

REQUIRED:

inventory rows = 37
relocated paths present = True
relocated blobs exact = True
dependency classification performed False

INFO ONLY:

qualified route occurrences = <observed count>
bare/root-style occurrences = <observed count>

IMPORTANT:

BARE_OR_ROOT_STYLE_MENTION
!=
BROKEN_DEPENDENCY

Do not repair or classify references during this run.

OUTPUT:

docs/evidence/for_planner/evidence_relocation_reference_closure_v0_observation.json

REQUIRED_NONCOLLAPSES:

TEXT_OCCURRENCE != LIVE_DEPENDENCY
KNOWN_ROUTE_REPAIR != ALL_REFERENCE_CLOSURE
RELOCATED_ROUTE_PRESENT != ALL_DEPENDENCIES_REPAIRED
HISTORICAL_MENTION != CURRENT_ROUTE
REFERENCE_DISCOVERY != REFERENCE_REWRITE_AUTHORITY

CLAIM_CEILING:

One tracked-tree occurrence inventory over the 37 exact relocated artifacts.
No live-dependency standing, automatic repair, archive policy, cold-storage
admission, deletion permission, planning, authority, execution, or scientific
standing is created.

STOP:
after producing the observation
