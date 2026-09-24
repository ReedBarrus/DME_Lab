# RELATIONAL HORIZON PLANNING PRESSURE CELL 001 — P6 READY-TO-SEND SUBSTITUTION WARRANT PACKET

OBJECT_TYPE:
RELATIONAL_HORIZON_PLANNING_PRESSURE_CELL_001_P6_SUBSTITUTION_WARRANT_PACKET

CAMPAIGN:
RELATIONAL_HORIZON_SCIENTIFIC_PLANNING_CAMPAIGN_001

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_ROUTING_RECONSTRUCTOR

MODE:
P6_ONLY

ROUTING_EXECUTION:
PROHIBITED

AUTHORITY_EFFECT:
NONE

# DECLARED WORKFLOW RELATION

R1:
IF result_standing = ADJUDICATED_VALID
AND adjudication disposition establishes the tested pressure
AND NEXT_LAWFUL_PRESSURE is present
THEN next_destination_class =
SCIENCE_INTEGRATION_NEXT_PRESSURE_MATERIALIZATION

# SPECIMEN A

RESULT_STANDING:
ADJUDICATED_VALID

ADJUDICATION_DISPOSITION:
TESTED_PRESSURE_ESTABLISHED

NEXT_LAWFUL_PRESSURE:
PRESENT

# SPECIMEN B

RESULT_STANDING:
ADJUDICATED_VALID

ADJUDICATION_DISPOSITION:
THE_TESTED_PRESSURE_HAS_BEEN_ESTABLISHED

NEXT_LAWFUL_PRESSURE:
PRESENT

# EXPLICIT SUBSTITUTION WARRANT

For this bounded routing specimen only:

THE_TESTED_PRESSURE_HAS_BEEN_ESTABLISHED

is warranted as satisfying the R1 condition:

adjudication disposition establishes the tested pressure.

No other equivalence or substitution is authorized.

# QUESTION

Using only R1, the specimen fields, and the bounded substitution warrant:

Recover one bounded destination class for each specimen or return UNRESOLVED.

Do not execute routing.

# REQUIRED OUTPUT

Return exactly:

SPECIMEN_A:
declared_relation_used:
R1 | UNRESOLVED
next_destination_class:
SCIENCE_INTEGRATION_NEXT_PRESSURE_MATERIALIZATION | UNRESOLVED

SPECIMEN_B:
substitution_warrant_used:
YES | NO | UNRESOLVED
declared_relation_used:
R1 | UNRESOLVED
next_destination_class:
SCIENCE_INTEGRATION_NEXT_PRESSURE_MATERIALIZATION | UNRESOLVED

COMPARISON:
warrant_restores_reconstructability:
YES | NO | UNRESOLVED
extra_equivalence_inferred:
YES | NO | UNRESOLVED
operator_memory_required:
YES | NO | UNRESOLVED
execution_authority_created:
NONE
autonomous_routing_claimed:
NO
comparison_description:
<brief bounded comparison>

P6_UNRESOLVED:
<list>

# ADMINISTRATION

This is Planning Pressure Cell 001 P6 only.
Do not inspect prior planning evaluator material.
Do not self-adjudicate.
Do not execute routing.
Return only the required output and stop.
