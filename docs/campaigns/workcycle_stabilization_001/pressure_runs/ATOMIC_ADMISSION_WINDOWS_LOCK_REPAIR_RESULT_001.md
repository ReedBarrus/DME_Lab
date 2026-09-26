# ATOMIC ADMISSION WINDOWS LOCK REPAIR RESULT 001

PRESSURE_ID:
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_001

FROZEN_IMPLEMENTATION_SOURCE:
11da60ee7b6de02dcea39537301c6c317cd44d9b

WITNESS_SOURCE_MATCHED:
YES

WITNESS_ONLY_TRANSPORT:
YES

SERIAL_FIRST:
ADMITTED

SERIAL_SECOND:
BLOCKED

UNSATISFIED_AUTHORITY_CASE:
BLOCKED

RACE_ADMITTED_COUNT:
1

RACE_BLOCKED_COUNT:
1

TRANSIENT_PERMISSION_ERROR:
BOUNDED_CONTENTION

PERSISTENT_PERMISSION_ERROR:
FAILS_CLOSED

MODEL_INVOCATION_EFFECT:
NONE

EXECUTION_PERFORMED:
false

AUTHORITY_EFFECT:
NONE

CLAIM_CEILING_PRESERVED:
YES

DISPOSITION:
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_MATCHED

UNRESOLVED:
[]

CLAIM_CEILING:
At the exact repaired source, same-process two-caller local-filesystem atomic admission again yields exactly one admitted caller and one blocked caller under the bounded fixture. Windows PermissionError during O_EXCL sentinel acquisition is treated as bounded contention, while persistent inability to acquire remains fail-closed. This does not establish cross-process contention safety, stale-lock recovery, crash safety, power-loss durability, verified-authority composition, model invocation, work execution, or self-moving-workcycle standing.

SCIENTIFIC_STANDING_EFFECT:
NONE

STOPPED:
YES
