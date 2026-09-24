# ATLAS METABOLIC COMPRESSION CELL 001 — READY-TO-SEND RUN A PACKET

OBJECT_TYPE:
ATLAS_METABOLIC_COMPRESSION_CELL_001_RUN_A_PACKET

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_RECONSTRUCTOR

MODE:
BOUNDED_COMPRESSION_RECONSTRUCTION

SCIENTIFIC_ADMISSION:
PROHIBITED

AUTHORITY_EFFECT:
NONE

# PURPOSE

Execute the exact next pressure selected by the candidate planner seat.

Test whether representational material can be reduced while preserving:
- one shared consequence-bearing relation;
- one divergent consequence-bearing relation;
- provenance to each source representation;
- one explicit challenge path;
- non-substitutability between source representations.

# SOURCE REPRESENTATION A

SOURCE_ID:
COMP001-A

SHARED_RELATION:
A shrine response is evaluated at the immediate post-boundary instant following
a simultaneous seal/restoration event.

DIVERGENT_RELATION:
For A, restoration controls the immediate post-boundary shrine state.

BOUNDARY_CONSEQUENCE:
RESPONDING

PROVENANCE:
SOURCE_A / RULE_A

# SOURCE REPRESENTATION B

SOURCE_ID:
COMP001-B

SHARED_RELATION:
A shrine response is evaluated at the immediate post-boundary instant following
a simultaneous seal/restoration event.

DIVERGENT_RELATION:
For B, seal controls the immediate post-boundary shrine state.

BOUNDARY_CONSEQUENCE:
PREVENTED

PROVENANCE:
SOURCE_B / RULE_B

# NON-SUBSTITUTION CONTRACT

No equivalence or substitution relation is declared between SOURCE_A / RULE_A
and SOURCE_B / RULE_B.

# COMPRESSION TRANSFORM

The original prose wrappers above are now replaced by this compressed object:

COMPRESSED_OBJECT_ID:
COMP001-C

SHARED:
immediate-post-boundary shrine response after simultaneous seal/restoration

BRANCH_A:
controller = restoration
state = RESPONDING
provenance = SOURCE_A / RULE_A

BRANCH_B:
controller = seal
state = PREVENTED
provenance = SOURCE_B / RULE_B

CHALLENGE_PATH:
To challenge either branch, resolve its provenance handle back to the
corresponding source representation.

SUBSTITUTION_STANDING:
NONE

# QUESTION

Using only COMP001-C:

Recover:
1. the shared relation;
2. Branch A's divergent relation and consequence;
3. Branch B's divergent relation and consequence;
4. provenance for both;
5. challengeability for both;
6. substitution standing.

Do not use the original prose source representations in reconstruction.

# REQUIRED OUTPUT

Return exactly:

SHARED_RELATION_RECOVERY:
RECOVERED | PARTIAL | UNRESOLVED

BRANCH_A:
divergent_relation:
RECOVERED | PARTIAL | UNRESOLVED
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
provenance_recovered:
YES | NO | UNRESOLVED
challenge_path_recovered:
YES | NO | UNRESOLVED

BRANCH_B:
divergent_relation:
RECOVERED | PARTIAL | UNRESOLVED
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
provenance_recovered:
YES | NO | UNRESOLVED
challenge_path_recovered:
YES | NO | UNRESOLVED

DIVERGENCE_PRESERVED:
YES | NO | UNRESOLVED

REPRESENTATION_SUBSTITUTION_AUTHORIZED:
YES | NO | UNRESOLVED

ORIGINAL_PROSE_REQUIRED_FOR_RECONSTRUCTION:
YES | NO | UNRESOLVED

COMPRESSION_RESULT:
<brief bounded description>

RUN_A_POSTURE:
outside_context_used:
NO
scientific_admission_created:
NONE
topology_created:
NONE
authority_effect:
NONE

RUN_A_UNRESOLVED:
<list>

# FAILURE CONDITIONS

FAIL / DEGRADE if:
- A/B divergence is erased;
- provenance becomes ambiguous;
- challenge path disappears;
- source representations become substitutable without warrant;
- original prose is required to recover the compressed relations.

# CLAIM CEILING

Success would establish only that this bounded compressed object preserved its
declared shared relation, divergent consequences, provenance, challenge path,
and non-substitution standing sufficiently for fresh reconstruction.

It would not establish generic safe compression or foreign-system metabolism.

# STOP

Return only the required output and stop.
