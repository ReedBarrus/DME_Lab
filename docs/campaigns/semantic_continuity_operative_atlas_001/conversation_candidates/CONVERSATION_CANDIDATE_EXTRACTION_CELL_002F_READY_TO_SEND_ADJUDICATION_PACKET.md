# CONVERSATION CANDIDATE EXTRACTION CELL 002F — READY-TO-SEND ADJUDICATION PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002F_ADJUDICATION_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
PRIOR CROSS-EVALUATION THREAD / EVALUATOR INSTANCE

USE:
REMOTE EVIDENCE ONLY

# REQUIRED EVIDENCE

Read exactly:

1.
docs/campaigns/semantic_continuity_operative_atlas_001/
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002F_READY_TO_SEND_ROLE_REVERSED_CONTAINMENT_RUN_A_PACKET.md

2.
docs/campaigns/semantic_continuity_operative_atlas_001/
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002F_RUN_A_FROZEN_OUTPUT_001.md

3.
docs/campaigns/semantic_continuity_operative_atlas_001/
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002E_ADJUDICATION_RESULT_001.md

# PRIMARY QUESTION

Does Cell 002F show that contained-extent recovery is invariant to which source entity carries the containing interval?

# REQUIRED CHECKS

1. EXPOSURE NEUTRALITY

Did the packet avoid supplying:
- a containment label;
- a role-reversal label as semantic guidance inside the admitted source;
- a precomputed intersection;
- an expected relation;
- a consequence cue?

Return:
CLEAN
PARTIAL
LEAKED
UNRESOLVED

2. RELATION DERIVATION

Did the extractor require both intervals:
later incarnation [YEAR_16, YEAR_22]
and
shrine-bound form [YEAR_10, YEAR_30]
to derive the candidate relation and extent?

Return:
RELATIONALLY_DERIVED
DIRECTLY_EXPRESSED
PARTIAL
UNRESOLVED

3. EXTENT BOUNDING

Is the derived extent exactly:
[YEAR_16, YEAR_22]?

Return:
EXACT
OVERBROAD
UNDERBOUNDED
UNRESOLVED

4. ROLE INVARIANCE

Compared with Cell 002E, does the same generic relation-recovery contract recover the same jointly warranted contained extent when the containing interval is assigned to the opposite source entity?

Return:
SUPPORTED
PARTIAL
UNSUPPORTED
UNRESOLVED

5. CLAIM CEILING

Did the output avoid:
- encounter/interaction;
- formal identity/non-identity;
- continuity claims;
- dependency standing;
- admission;
- topology;
- authority;
- execution;
- control?

Return:
CONSERVED
DEGRADED
VIOLATED
UNRESOLVED

6. PROVENANCE DISCIPLINE

Did exact authorship and idea attribution remain unresolved?

Return:
CONSERVED
DEGRADED
VIOLATED
UNRESOLVED

7. CELL 002F DISPOSITION

Choose exactly one:

ROLE_REVERSED_CONTAINMENT_INVARIANCE_ESTABLISHED

ROLE_REVERSED_CONTAINMENT_INVARIANCE_ESTABLISHED_WITH_BOUNDED_WOUNDS

SOURCE_SENSITIVE_EXTRACTION_ONLY

UNRESOLVED

# REQUIRED OUTPUT

Return exactly:

EXPOSURE_NEUTRALITY:

RELATION_DERIVATION:

EXTENT_BOUNDING:

ROLE_INVARIANCE:

CLAIM_CEILING:

PROVENANCE_DISCIPLINE:

CELL_002F_DISPOSITION:

NEW_WOUNDS:
<list or NONE>

MAXIMUM_WARRANTED_CLAIM:
<one bounded claim>

NEXT_LAWFUL_PRESSURE:
<one bounded next pressure only>

# CLAIM CEILING

Maximum allowable success claim:

For these tested fictional specimens, under the same neutral relation-recovery contract, fresh extractors recovered the exact contained jointly warranted extent [YEAR_16, YEAR_22] both when the later incarnation supplied the outer interval and when the shrine-bound symbolic form supplied the outer interval, while preserving claim and provenance boundaries.

Do not claim generic interval algebra, generic semantic understanding, scientific admission, autonomous semantic metabolism, or self-organizing memory.

# STOP

Stop after adjudication.
Do not mutate anything.
Do not design implementation.
