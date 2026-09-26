# CELL 002 THREE-WAY ADJUDICATION 001

OBJECT_TYPE:
FORMAL_RELATIONAL_ADJUDICATION

CELL:
AUTHORITY_MEMBRANE_SECURITY_CELL_002

INPUTS:
- Lane A conservation / claim-ceiling review
- Lane B replay pressure design
- Codex candidate apparatus result

## Convergence

Lane A requires:
- current authority consumed before consequence can admit a second use;
- 1 current use → at most 1 admitted invocation;
- history remains without restoring authority;
- denial alone is not proof of no invocation.

Lane B independently requires:
- exact same consumed envelope reused;
- no new approval/capability/request/policy/executor;
- authority unavailable before model invocation;
- second invocation delta = 0;
- historical approval remains visible.

Codex reports:
- pre-invocation CONSUMING reservation;
- durable local current-state write;
- one control invocation;
- post-use current authority NONE / CONSUMED;
- exact same capability replay;
- replay denial before invocation;
- second invocation count = 0;
- historical receipt retained.

## Adjudication

TARGET PRESSURE GEOMETRY:
INSTANTIATED IN CANDIDATE HARNESS

ONE MATERIAL INTERVENTION:
SATISFIED

CONSUMPTION ORDERING:
MATCHES LANE A / LANE B REQUIREMENT

SECOND INVOCATION:
NOT OBSERVED IN CANDIDATE HARNESS

HISTORY / CURRENTNESS SEPARATION:
REPRESENTED

## Standing

CELL_002_CANDIDATE_APPARATUS:
BOUNDEDLY_QUALIFIED_CANDIDATE

CELL_002_REFERENCE_REPO:
NOT YET CANONICALIZED

CELL_002_INSTALLED_TRUST_ROOT:
NOT YET PROMOTED

CELL_002_INSTALLED_EXECUTOR:
NOT YET PRESSURE-QUALIFIED

## Exact candidate claim

Under the tested candidate single-process apparatus,
one exact use_limit=1 authority envelope admitted one
mocked model-invocation-boundary crossing, became unavailable
for subsequent ordinary admission before that consequence path
could be reused, transitioned to consumed standing, and an exact
sequential reuse attempt was denied before a second invocation crossing.

## Claim ceiling

DO NOT infer:
- crash-safe exactly-once execution
- concurrent atomic consumption
- multi-process safety
- distributed replay resistance
- local tamper resistance
- revocation / freeze / expiry correctness
- alternate-route containment
- copied-trust-root replay resistance
- real provider behavior
- generic authority security

## Next gate

1. canonicalize the exact Cell-002 candidate artifacts;
2. inspect exact pushed bytes;
3. promote the reviewed consumption primitive into the local trust root;
4. bind it to the installed executor without broadening capability;
5. run matched installed-path control + exact replay pressure;
6. record installed authority-state and receipt coordinates;
7. only then consider Cell 002 installed-path qualification.

FREEZE:

CANDIDATE CONSUMPTION SURVIVAL
!=
OPERATIVE AUTHORITY CONSUMPTION


---

## Post-push exact-byte inspection correction

The canonical pushed bytes were inspected after the initial three-way adjudication.

A material omission was found:

The V0 authority envelope implemented in
src/runtime/local_authority_consumption_v0.py
does NOT contain principal_id / authorized-consumer identity.

Implemented envelope fields are:

object_type
capability_id
approval_id
request_sha256
input_sha256
model
endpoint_identity
executor_sha256
policy_sha256
use_limit
remaining_uses
status
issued_at
expires_at

Lane A requires the minimum operative authority relation to bind:

capability
× principal
× scope
× current policy
× current executor
× remaining consumable use.

Therefore the exact pushed candidate does NOT yet instantiate
the full Lane-A minimum envelope relation.

REVISED STANDING:

CELL_002_CONSUMPTION_ORDERING:
SUPPORTED IN CANDIDATE HARNESS

CELL_002_EXACT_REPLAY_DENIAL:
SUPPORTED IN CANDIDATE HARNESS

CELL_002_PRINCIPAL_BINDING:
MISSING

CELL_002_CANDIDATE_APPARATUS:
APPARATUS_PARTIAL / REPAIR_REQUIRED

CELL_002_INSTALLED_TRUST_ROOT:
DO NOT PROMOTE YET

Required repair:

- add principal_id to the authority envelope;
- validate principal_id as authority-material;
- persist it in issuance / reservation / receipt / denial history where relevant;
- require attempted consumption principal identity to correspond to issued authority;
- add matched control and wrong-principal pressure;
- preserve the existing exact replay pressure unchanged;
- do not broaden capability class;
- do not begin Cell 003.

FREEZE:

COUNT-BOUNDED AUTHORITY
!=
PRINCIPAL-BOUND AUTHORITY
