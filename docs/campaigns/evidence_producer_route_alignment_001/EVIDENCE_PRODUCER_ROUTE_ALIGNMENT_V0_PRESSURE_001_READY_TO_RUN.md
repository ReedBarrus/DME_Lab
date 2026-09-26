# G18 Pressure 001 Ready To Run

PRESSURE_ID:
EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_PRESSURE_001

LEDGER_BLOB:
1b28599b0e69844617f76cee47dabf5577c6baed

G17_WITNESS_BLOB:
9cf234fffd1d5b63bfc0af2238e496a2402fe308

HORIZON_SELECTION_BLOB:
8de47c6ba85c2fb28eedea587f715ca8aaf7d7c2

CONTRACT_BLOB:
20b078a14d2afec0b09af01f22b3ec2176c67c8f

PRESSURE_WRAPPER_BLOB:
d0029b0096bf4c895d1d82051888b73df5f718ca

TEST_PRODUCER:
tools/observe_horizon_gap_selector_v0.py

TEST_PRODUCER_BLOB:
54891e276f28a3f4fe4d61775d14b706cf56bd1e

RELOCATED_HISTORICAL_PATH:
docs/evidence/for_planner/horizon_gap_selector_v0_observation.json

RELOCATED_HISTORICAL_BLOB:
be23eba7c50f1b51a0e3b1412d9f5adc07dee1ff

OLD_ROOT_OUTPUT_PATH:
horizon_gap_selector_v0_observation.json

TARGET_RELATION:
STORED_EVIDENCE_RELOCATION != PRODUCER_OUTPUT_ROUTE_MIGRATION

RUN:

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item docs/evidence/for_planner/evidence_producer_route_alignment_v0_observation.json -ErrorAction SilentlyContinue
Remove-Item horizon_gap_selector_v0_observation.json -ErrorAction SilentlyContinue

python tools/pressure_evidence_producer_route_alignment_v0.py
```

EXPECTED:

producer exit code = 0
old root output created = True
relocated historical blob preserved = True
pressure cleanup complete = True
target relation = YES

OPTIONAL_INFO:

generated root blob != historical blob = <observed>

The wrapper removes the temporary generated root output after capture.
Do not commit any regenerated root observation.

OUTPUT:

docs/evidence/for_planner/evidence_producer_route_alignment_v0_observation.json

REQUIRED_NONCOLLAPSES:

STORED_ARTIFACT_RELOCATION != PRODUCER_ROUTE_MIGRATION
OLD_PATH_REOCCUPATION != HISTORICAL_EVIDENCE_OVERWRITE
NEW_OUTPUT != HISTORICAL_ARTIFACT
PRODUCER_ROUTE_MISALIGNMENT != GENERIC_RELOCATION_POLICY
PRESSURE_CLEANUP != EVIDENCE_DELETION

CLAIM_CEILING:

One bounded execution of tools/observe_horizon_gap_selector_v0.py only.
No producer/consumer repair authority, generic intake router, archive policy,
cold-storage admission, deletion permission, automatic rewriting, planning,
authority, execution, or scientific standing.

STOP:
after producing the pressure observation and cleaning the temporary root output.
