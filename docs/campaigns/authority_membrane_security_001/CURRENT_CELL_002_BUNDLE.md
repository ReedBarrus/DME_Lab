# Authority Membrane Security — Cell 002 Current Bundle

CURRENT_CELL:
AUTHORITY_MEMBRANE_SECURITY_CELL_002

TARGET:
AUTHORITY CONSUMPTION / REPLAY

UPSTREAM REQUIREMENT:
CELL_001_INSTALLED_EXECUTOR = BOUNDEDLY_QUALIFIED

STATUS:
READY FOR PARALLEL DESIGN / IMPLEMENTATION REVIEW

## Send map

LANE A:
LANE_A_CELL_002_REVIEW_PACKET.md

LANE B:
LANE_B_CELL_002_PRESSURE_PACKET.md

CODEX:
CODEX_CELL_002_IMPLEMENTATION_PACKET.md

## Cross-cutting design references

CONSEQUENCE_CONTROL_PROFILE_V0.md
COCKPIT_AUTHORITY_SECURITY_VIEW_V0.md

These references constrain interpretation and projection.
They do not broaden Cell 002's claim.

## Cell 002 current target

ONE PROCESS
ONE CAPABILITY
ONE PRINCIPAL
ONE CHOKEPOINT
ONE ALLOWED USE
ONE ATTEMPTED REPLAY
ONE DURABLE AUTHORITY HISTORY

## Minimum candidate lifecycle

ISSUED
→ ACTIVE
→ CONSUMING
→ CONSUMED

bounded exits:

ACTIVE → FROZEN
ACTIVE → REVOKED
ACTIVE → EXPIRED

CONSUMING → RECOVERY_REQUIRED
when consequence / consumption state cannot be safely reconciled.

## Primary replay pressure

fresh capability:
remaining_uses = 1

first lawful use:
→ reserve / consume
→ one invocation
→ remaining_uses = 0
→ historical receipt persists

second use of exact same authority:
→ no second invocation
→ deny / exhausted
→ historical validity remains visible
→ current authority = NONE

## Cockpit dependency

Cockpit should become a projection of Cell-002 authority state as soon as
the authority-envelope / receipt representation stabilizes enough to inspect.

Do not make Cockpit the authority source.

READ-ONLY FIRST.

## Stop conditions

Do not claim:
- concurrency safety
- crash recovery safety
- multi-process atomicity
- replication containment
- general authority security

until separately pressured.
