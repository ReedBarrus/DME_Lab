# COCKPIT AUTHORITY / SECURITY / CONSEQUENCE VIEW V0

OBJECT_TYPE:
COCKPIT_OPERATIVE_MEMORY_PROJECTION_SPEC

STATUS:
PROVISIONAL / IMPLEMENTATION TARGET

PRIMARY ROLE:

COCKPIT
=
OPERATIVE MEMORY PROJECTION
+
AUTHORITY / SECURITY LEGIBILITY
+
PROPOSAL / APPROVAL CEREMONY SURFACE

NOT:
TRUST ROOT

## Three synchronized projections

### 1. AUTHORITY / SECURITY

For every principal/task/capability show:

- capability_id
- approval_id
- principal_id
- task / project association
- operation / scope
- use_limit
- remaining_uses
- lifecycle state
- corrective_owner
- allowed corrective operations
- executor hash
- policy hash
- expiry
- current authority status

Controls MAY request:

- grant N uses
- deny
- freeze
- revoke
- reduce remaining uses
- request expansion
- request fresh review

Cockpit does not mint authoritative state.
The trusted local membrane must create / mutate current authority state.

### 2. EPISTEMIC

Show separately:

- request
- admission decision
- approval
- execution witness
- receipts
- result
- scientific interpretation
- unresolveds
- challenge handles
- historical standing
- current standing

Do not collapse:

MODEL CLAIM
!=
EXECUTION WITNESS

RECORDED
!=
CURRENT

### 3. CONSEQUENCE / CORRECTION

Show:

- consequence class
- reachable surface
- observed surface
- corrective surface
- corrective owner
- corrective actions qualified
- corrective latency standing
- containment standing
- replication / escape standing
- unresolved consequence radius

## Primary human interactions

WHY DO WE BELIEVE THIS?
→ backward provenance

WHAT DID THIS CAUSE?
→ forward consequence lineage

WHAT MAY HAPPEN NOW?
→ current authority / admissibility

WHAT CAN STOP OR REDUCE IT?
→ corrective relation

WHAT CAN WE NOT YET CONTROL?
→ explicit unresolved consequence range

## Capability card example

CAP-014
principal: SOLA-7
task: CELL002

MODEL INVOCATION
granted: 8
consumed: 3
remaining: 5
status: ACTIVE

corrective owner:
LOCAL_AUTHORITY_MEMBRANE

qualified corrections:
DENY
FREEZE
REVOKE

atomicity:
QUALIFIED_SINGLE_PROCESS

concurrency:
UNTESTED

crash recovery:
UNTESTED

[VIEW RECEIPTS]
[VIEW LINEAGE]
[REQUEST +N]
[FREEZE]
[REVOKE]

## Critical UI law

ARMED
!=
GUARANTEED EXECUTION

The membrane may reject an otherwise-budgeted request when current policy,
identity, standing, or corrective conditions fail.

## Current implementation order

1. Cell 002 establishes authority-envelope and consumption records.
2. Cockpit projects those records read-only first.
3. Cockpit may later submit typed grant/freeze/revoke requests.
4. Trusted local membrane remains the authority source.

READ-ONLY LEGIBILITY
PRECEDES
COCKPIT-SOURCED MUTATION.
