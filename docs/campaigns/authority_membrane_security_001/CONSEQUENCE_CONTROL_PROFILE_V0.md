# CONSEQUENCE CONTROL PROFILE V0

OBJECT_TYPE:
CONSEQUENCE_CONTROL_PROFILE

STATUS:
PROVISIONAL / VECTOR-VALUED / NON-SCALAR

PRIMARY LAW:

AUTHORIZED CONSEQUENCE
MUST REMAIN WITHIN
AN OBSERVABLE / CORRECTABLE CONSEQUENCE SURFACE

ALONG A SPECIFIC BASIS
THAT HAS BEEN PRESSURE-TESTED
AT THE AUTHORIZED LOAD / CAPABILITY RANGE.

CORRECTIVE AUTHORITY IS NOT GENERIC.

It is qualified only where:
- the corrective owner controls a real chokepoint;
- the relevant consequence is observable within the declared scope;
- the corrective action has been tested at the relevant load/range;
- the claim ceiling remains bounded to that basis.

## Views

AUTHORITY / SECURITY VIEW:
- principal
- capability
- current authority
- use budget
- corrective owner
- allowed corrective operations
- policy/executor coordinates

EPISTEMIC VIEW:
- what is observed
- what is witnessed
- what is inferred
- what is unresolved
- currentness
- challenge handles

CONSEQUENCE VIEW:
- what may propagate
- reachable surface
- observation surface
- correction surface
- propagation latency
- escape / replication surface
- unresolved consequence range

## Corrective families

PREVENTIVE:
- DENY
- REQUIRE_REVALIDATION
- REFUSE_ESCALATION

AUTHORITY_REDUCING:
- FREEZE
- REVOKE
- EXPIRE
- REDUCE_REMAINING_USES

CONTAINMENT:
- STOP_MANAGED_INSTANCE
- INVALIDATE_MANAGED_CREDENTIAL
- CLOSE_MANAGED_ROUTE

RECOVERY:
- MARK_RECOVERY_REQUIRED
- QUARANTINE_STATE
- RECONCILE_FROM_WITNESSES
- ESCALATE_TO_OPERATOR

## Corrective integrity

CORRECTIVE AUTHORITY
MAY REDUCE AUTHORITY
WITHIN ITS WARRANT.

CORRECTIVE AUTHORITY
MAY NOT
SELF-EXPAND ITS WARRANT.

PRINCIPAL MAY:
- consume admitted authority;
- refuse a request;
- request restoration or expansion.

PRINCIPAL MAY NOT:
- expand its own authority;
- veto lawful corrective action inside the qualified corrective relation.

OPERATOR / SUPERVISOR AUTHORITY:
also remains bounded by explicit policy and consequence envelopes.

NO ACTOR GETS AMBIENT CONSEQUENCE AUTHORITY.

## Vector dimensions

REACHABILITY
OBSERVABILITY
CORRECTIVE_COVERAGE
CORRECTIVE_LATENCY
CORRECTIVE_AUTHORITY_INTEGRITY
ATOMICITY
CONCURRENCY
RECOVERY
PERSISTENCE
REVOCABILITY
CONTAINMENT
REPLICATION_POTENTIAL
ESCAPE_SURFACE
LEGIBILITY
WITNESSABILITY
CURRENTNESS

Do not collapse these into one security score.

Example:

ATOMICITY:
QUALIFIED_SINGLE_PROCESS

CONCURRENCY:
UNTESTED

CRASH_RECOVERY:
UNTESTED

REVOCABILITY:
DESIGNED / NOT YET PRESSURED

REPLICATION_CONTAINMENT:
NOT_ESTABLISHED

## Security objective

WHEN SOMETHING DEVIATES,
THE MAXIMUM UNCORRECTED CONSEQUENCE
SHOULD BE
SMALL,
LEGIBLE,
BOUNDED,
RECOVERABLE,
AND INSIDE A TESTED CORRECTIVE RANGE.

UNCONTROLLED / UNCORRECTABLE RANGE
MUST REMAIN VISIBLE.
