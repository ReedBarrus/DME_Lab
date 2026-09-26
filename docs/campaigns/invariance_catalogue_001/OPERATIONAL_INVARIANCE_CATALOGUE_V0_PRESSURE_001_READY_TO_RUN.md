# G21 Operational Invariance Catalogue Pressure 001 — Ready To Run

PRESSURE_ID:
OPERATIONAL_INVARIANCE_CATALOGUE_V0_PRESSURE_001

LEVERAGE_SOUGHT:

Let a future agent retrieve the exact tested binding for one matched bounded
relation from a compact operational record instead of reopening the full
G18/G19/G20 evidence chain.

BASIS:

MEMORY_COMPILATION_METHOD_BLOB:
cf3179d0cb2f25459c54112cf783b2479531452c

G20_ADJUDICATION_BLOB:
2445254a4b0738c269a627bde5c746c1e51227cc

G20_PRESSURE_RESULT_BLOB:
0f1fe776a9ed7ade963b4c5373071ddb304f6ee1

G20_WITNESS_BLOB:
a63e164636a34010105d307e5891cff62e26be73

CATALOGUE_ENTRY:
docs/campaigns/invariance_catalogue_001/specimens/
G20_OPERATIONAL_CATALOGUE_ENTRY_V0.json

CATALOGUE_ENTRY_BLOB:
8e67e8aca3ff71d1512e008196f905fffd82bbd2

LOOKUP_MEMBRANE:
src/control/invariance_catalogue_v0.py

LOOKUP_MEMBRANE_BLOB:
ba74a02fbbcf3d9baa823310de09dd7082cd5aa3

HORIZON_BLOB:
ee55fed8c8c243fdb2e87d39cb2893fd1a131ab4

CONTRACT_BLOB:
245e37841e8f67f5b9a0abca38973acc7b35026f

OBSERVER_BLOB:
a89799ba7635af4569b34bca934902123f63bc7e

BOUNDED_UNKNOWN:

Can the compact entry route the two exact tested surface bindings, preserve
bounded standing/nonclaims/basis handles, refuse an untested surface, and do so
without reading the rich G20 basis contents?

RUN:

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item docs/evidence/for_planner/operational_invariance_catalogue_v0_observation.json -ErrorAction SilentlyContinue

python tools/observe_operational_invariance_catalogue_v0.py
```

EXPECTED:

```text
[OK] repository lookup CATALOGUED_TESTED_BINDING
[OK] callable lookup CATALOGUED_TESTED_BINDING
[OK] untested lookup NO_QUALIFIED_BINDING
[OK] rich basis content reads 0
[OK] all_checks_pass True
```

OUTPUT:

docs/evidence/for_planner/operational_invariance_catalogue_v0_observation.json

TARGET_RELATIONS:

```text
CATALOGUED TESTED BINDING != LIVE APPLICABILITY

CATALOGUE INDEX != SCIENTIFIC BASIS

UNTESTED SURFACE != INFERRED BINDING
```

and bounded candidate capability:

```text
COMPACT OPERATIONAL ENTRY
SUPPORTS TESTED-SURFACE ROUTING
WITHOUT RICH-BASIS REOPEN
```

PRESERVE:

standing = MATCHED_BOUNDED_RELATION_NOT_LEDGER_PROMOTED

live_applicability_currentness =
UNRESOLVED_BEYOND_FROZEN_G20_BASIS

live_application_authorized = false

catalogue_authority_effect = NONE

planning_effect = NONE

execution_effect = NONE

DO NOT INFER:

minimal carrier
final catalogue schema
safe deletion
live current applicability
automatic relation discovery
universal surface portability
planning activation
authority
execution
global invariance
scientific standing

NEXT IF MATCHED:

G22 may ablate candidate catalogue coordinates to discover which ones actually
carry reconstruction / bounded-use load.

STOP:
after producing the one G21 observation.
