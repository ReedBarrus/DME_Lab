# G22 Invariance Catalogue Carrier Reconstruction Load — Ready To Run

PRESSURE_ID:
INVARIANCE_CATALOGUE_CARRIER_RECONSTRUCTION_LOAD_V0_PRESSURE_001

LEVERAGE_SOUGHT:

Identify which coordinates in the G21 candidate operational entry actually carry
the declared reconstruction/use target, so later compression can remove
non-load-bearing packaging without damaging bounded reuse.

BASIS:

G21 adjudication:
docs/campaigns/invariance_catalogue_001/pressure_runs/
OPERATIONAL_INVARIANCE_CATALOGUE_V0_ADJUDICATION_RESULT_001.md

G21_ADJUDICATION_BLOB:
204988eac6d1161a06e1e26250565dc303c62c77

CONTROL_CARRIER:
docs/campaigns/invariance_catalogue_001/specimens/
G20_OPERATIONAL_CATALOGUE_ENTRY_V0.json

CONTROL_CARRIER_BLOB:
8e67e8aca3ff71d1512e008196f905fffd82bbd2

RECONSTRUCTOR:
src/control/invariance_catalogue_carrier_reconstructor_v0.py

RECONSTRUCTOR_BLOB:
7d19a07ca1c8bc8d53ff175955f1128fb6e2a4de

HORIZON_BLOB:
82fd28c98eea50892fca0388f95d1213759a3be2

CONTRACT_BLOB:
b6440a52ff4746fb9cb6199e517b9537a9f59216

OBSERVER:
tools/observe_invariance_catalogue_carrier_reconstruction_v0.py

OBSERVER_BLOB:
e91d7e8dab7249bc82a907bd3224845f533a0736

BOUNDED_RECONSTRUCTION_TARGET:

Recover exactly, without rich-evidence reads:

- G20 matched relation pair;
- bounded standing;
- live-applicability currentness;
- repository tested binding and HOLD posture;
- callable tested binding and COHERENT posture;
- refusal of UNTESTED_SURFACE_SENTINEL;
- exact basis handles;
- exact known nonclaims;
- live_application_authorized = false.

ABLATIONS:

```text
A1 remove object_type
A2 remove catalogue_entry_id
A3 remove qualified_scope
A4 remove tested_surfaces
A5 remove reconstruction_use
A6 remove catalogue_authority_effect
A7 remove stopped

B1 remove relations
B2 remove standing
B3 remove surface_bindings
B4 remove live_applicability_currentness
B5 remove basis_handles
B6 remove known_nonclaims

C1 remove qualified_scope + tested_surfaces
```

CANDIDATE_EXPECTATION:

```text
A1-A7 -> RECONSTRUCTION_EQUIVALENT

B1-B6 -> RECONSTRUCTION_LOSS

C1 -> RECONSTRUCTION_LOSS
      specifically losing justified refusal of the untested sentinel
```

The expectation is pressure bait, not standing.

RUN:

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item docs/evidence/for_planner/invariance_catalogue_carrier_reconstruction_v0_observation.json -ErrorAction SilentlyContinue

python tools/observe_invariance_catalogue_carrier_reconstruction_v0.py
```

EXPECTED STDOUT SHAPE:

```text
[OK] control RECONSTRUCTION_EQUIVALENT
[OK] A1_REMOVE_OBJECT_TYPE -> ...
...
[OK] C1_REMOVE_SCOPE_AND_TESTED_SURFACES -> ...
[OK] paired scope/tested-surfaces loss coordinates [...]
[OK] all_expectations_match True
```

OUTPUT:

docs/evidence/for_planner/
invariance_catalogue_carrier_reconstruction_v0_observation.json

TARGET_CANDIDATE_RELATIONS:

```text
SINGLE COORDINATE REDUNDANCY
!=
ABSENCE OF DISTRIBUTED RECONSTRUCTION LOAD
```

and:

```text
OPERATIONAL CARRIER LOAD
IS TASK-RELATIVE
```

PRESERVE:

```text
FIELD UNUSED FOR G22 TARGET != FIELD GLOBALLY USELESS
FIELD LOAD-BEARING FOR G22 TARGET != UNIVERSALLY REQUIRED FIELD
SINGLE-FIELD ABLATION PASS != GROUP ABLATION PASS
RECONSTRUCTION SUFFICIENCY != SAFE DELETION
RECONSTRUCTION SUFFICIENCY != FINAL CATALOGUE SCHEMA
COMPRESSION CANDIDATE != PERFORMANCE IMPROVEMENT
```

DO NOT INFER:

global field uselessness
global field necessity
final catalogue schema
safe deletion
quantitative compression benefit
live applicability
automatic relation discovery
planning activation
authority
execution
global invariance
scientific standing

NEXT IF MATCHED:

Use the observed reconstruction-load profile to construct a candidate reduced
carrier, then G23 compares its actual carrying/retrieval cost against the richer
G21 carrier under the same bounded task.

STOP:
after producing the one G22 observation.
