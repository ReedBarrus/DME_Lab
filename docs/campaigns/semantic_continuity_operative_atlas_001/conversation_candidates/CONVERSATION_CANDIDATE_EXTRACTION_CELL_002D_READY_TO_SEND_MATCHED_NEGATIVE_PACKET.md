# CONVERSATION CANDIDATE EXTRACTION CELL 002D — READY-TO-SEND MATCHED NEGATIVE PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002D_MATCHED_NEGATIVE_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
THE SAME FRESH THREAD / MODEL INSTANCE THAT PRODUCED CELL 002D RUN A

DO NOT SEND TO:
a new extractor instance
the cross-evaluation thread
Lane A reviewer
any thread that has seen evaluator gold

RUN_A_FROZEN_OUTPUT:
docs/campaigns/semantic_continuity_operative_atlas_001/
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002D_RUN_A_FROZEN_OUTPUT_001.md

RUN_A_FINALIZATION_RECEIPT:
docs/campaigns/semantic_continuity_operative_atlas_001/
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002D_RUN_A_FINALIZATION_RECEIPT_001.md

RUN_A_OUTPUT_COMMIT:
d18611fe169e2b536d29d115cb34ac657c7456e4

RUN_A_FINALIZATION_COMMIT:
678d8bcfcb806489fa29b8ab2e369b116e568989

RUN_A_OUTPUT_BLOB:
3761ea7afeb655f4a931e118dbb8c7b0e012622e

ADMINISTRATION:
RUN_A_FINALIZED_BEFORE_THIS_PACKET

# ==================================================
# PURPOSE
# ==================================================

Test whether the derived interval intersection depends on both source
intervals rather than on generic overlap completion or prior-candidate
replay.

The matched negative preserves:

- later-incarnation interval:
  [YEAR_12, YEAR_24]

- shrine-bound symbolic-form interval:
  a bounded interval with the same duration class and the same kind of
  source support

but moves the shrine-bound interval so that the two intervals no longer
intersect.

# ==================================================
# MATCHED NEGATIVE SOURCE
# ==================================================

NEGATIVE_ID:
CELL_002D_NEGATIVE_001_NON_OVERLAPPING_INTERVALS

Use the same source as Cell 002D Run A EXCEPT replace the shrine-bound
interval sentence:

"Independent shrine records establish that this symbolic form produces
responses continuously from the start of YEAR_18 through the end of
YEAR_30."

with:

"Independent shrine records establish that this symbolic form produces
responses continuously from the start of YEAR_25 through the end of
YEAR_37."

All other source text remains unchanged.

# ==================================================
# CRITICAL DIFFERENCE
# ==================================================

POSITIVE:

later incarnation:
[YEAR_12, YEAR_24]

shrine-bound form:
[YEAR_18, YEAR_30]

joint intersection:
[YEAR_18, YEAR_24]

NEGATIVE:

later incarnation:
[YEAR_12, YEAR_24]

shrine-bound form:
[YEAR_25, YEAR_37]

joint intersection:
NONE

# ==================================================
# EXECUTION QUESTION
# ==================================================

Using only the matched negative source:

Recover at most ONE bounded relation that requires combining at least
TWO separately stated source facts.

Do not preserve the positive overlap relation merely because you
produced it earlier.

Do not infer a shared activity interval when no intersection is
supported.

A lawful output may recover a bounded temporal-order relation if
supported by the negative source.

# ==================================================
# REQUIRED OUTPUT
# ==================================================

Return exactly:

NEGATIVE_CANDIDATE_STATUS:
RECOVERED | DEGRADED | NOT_RECOVERED | UNRESOLVED

CANDIDATE_IF_ANY:
<one bounded relation or NONE>

DERIVED_EXTENT:
<bounded interval if warranted, otherwise NONE>

SUPPORT_POSTURE:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

POSITIVE_INTERVAL_INTERSECTION_STILL_WARRANTED:
YES | PARTIAL | NO | UNRESOLVED

BASIS:
<packet-local reason>

SOURCE_AUTHORSHIP_POSTURE:
UNRESOLVED_IN_THIS_CAPTURE

IDEA_ATTRIBUTION:
UNRESOLVED

DEPENDENCY_CANDIDATES:
NONE unless independently warranted

SCIENTIFIC_ADMISSION:
NONE

TOPOLOGY_MUTATION:
NONE

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

CONTROL_EFFECT:
NONE

UNRESOLVED:
<list>

# ==================================================
# SUCCESS CONDITION
# ==================================================

The negative behaves lawfully if it does NOT replay:

[YEAR_18, YEAR_24]

or invent any other shared activity interval.

A lawful negative may recover a relation such as:

the later incarnation's documented activity interval ends before the
shrine-bound form's documented response interval begins.

Freeze:

NO INTERSECTION
!=
NO RELATION

and:

DISJOINT INTERVALS
MAY STILL SUPPORT
A TEMPORAL ORDER RELATION.

# ==================================================
# FAILURE CONDITIONS
# ==================================================

FAIL / DEGRADE if the output:

- preserves the positive overlap relation;
- invents an overlap interval;
- broadens either input interval;
- invents encounterability;
- invents continuity claims;
- resolves formal identity or non-identity;
- imports prior Cell 002D candidate as evidence;
- creates dependency standing;
- resolves authorship or idea attribution;
- creates admission, topology, authority, execution, or control effects.

# ==================================================
# STOP
# ==================================================

Return only the required matched-negative output.

Do not self-adjudicate.
Do not mutate anything.
