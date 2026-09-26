# ATLAS TEMPORAL LINEAGE / ACTOR PROJECTION / WOUND REPLAY V0

OBJECT_TYPE:
COCKPIT_ATLAS_TRANSFORM_PACKAGE

OBJECT_ID:
ATLAS_TEMPORAL_LINEAGE_ACTOR_WOUND_REPLAY_V0

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

TARGET:
EXISTING_ATLAS_PRIMARY_SURFACE

MODE:
THREE-STEP IMPLEMENTATION
+
HISTORICAL PRESSURE CALIBRATION

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

CONTROL_EFFECT:
NONE

# ==================================================
# PURPOSE
# ==================================================

Move the Atlas from a mostly static spatial projection into a
source-bound temporal / operational instrument without fabricating
semantic causation or seat lineage that the repository does not record.

This package implements three next primitives:

1. TEMPORAL LINEAGE
2. TRANSITION EMISSION
3. ACTOR / SEAT / CURSOR PROJECTION

Then uses those primitives to replay one historical wound as an
instrument-quality pressure.

PRIMARY TARGET:

STATIC ADDRESSED WORLD
+
REAL SOURCE HISTORY
+
EXPLICIT ACTOR EVIDENCE
→
PRESSUREABLE DYNAMICAL ATLAS

NOT:

STATIC WORLD
+
ANIMATION
→
CLAIMED CAUSAL MODEL

# ==================================================
# 0. CRITICAL LINEAGE DISTINCTIONS
# ==================================================

The repository likely contains strong MECHANICAL lineage and incomplete
SEMANTIC / ACTOR lineage.

Freeze these non-collapses:

COMMIT AUTHOR
!=
SEAT ACTOR

COMMITTER
!=
SEMANTIC CAUSE

FILE DIFF
!=
INTENDED TRANSFORMATION

TEMPORAL SUCCESSION
!=
CAUSATION

CO-OCCURRENCE IN ONE COMMIT
!=
DEPENDENCY

FILE CREATED BY COMMIT
!=
OBJECT CONCEIVED BY COMMIT AUTHOR

CURRENT FILE CONTENT
!=
ORIGINAL SEMANTIC INTENT

CURSOR RECORD
!=
PROOF OF EVERY TRANSFORMATION PERFORMED BY THAT SEAT

MISSING ACTOR LINEAGE
!=
NO ACTOR EXISTED

UNKNOWN
MUST REMAIN
UNKNOWN.

Do not infer seat authorship from filenames, folder names, timing,
commit author, conversational memory, or visual proximity.

# ==================================================
# 1. LINEAGE EVIDENCE CLASSES
# ==================================================

Use explicit evidence classes so the Atlas can represent what is known
without flattening all history into one "provenance" edge.

MECHANICAL_HISTORY:

- commit identity
- parent commit identity
- tree identity
- path at commit
- blob / content identity
- added / modified / deleted status
- rename detection only if mechanically justified
- author / committer metadata as Git metadata only
- timestamp metadata

DECLARED_OPERATIONAL_LINEAGE:

- seat / cursor record explicitly naming an object, task, or transition
- execution / mutation receipt
- campaign artifact explicitly binding actor to transformation
- continuity event explicitly binding seat / cursor to operation
- explicit handoff record

SEMANTIC_LINEAGE:

- explicit source artifact stating why a transformation occurred
- pressure object / decision / warrant tied to the resulting mutation
- explicit source-to-result relation
- exact reconstruction handle

UNRESOLVED_LINEAGE:

- mechanical transition exists
- semantic or actor attribution is absent / conflicting / insufficient

Lineage may be strong mechanically and unresolved semantically.

# ==================================================
# 2. STEP ONE — TEMPORAL LINEAGE OPERATOR V0
# ==================================================

OBJECT_ID:
TEMPORAL_LINEAGE_OPERATOR_V0

Build a source-bound timeline over real Git history.

Primary interaction:

EARLY COMMIT
←
FRAME SLIDER
→
HEAD

Each frame is one exact repository snapshot.

FRAME_ID should bind at minimum:

repository identity
commit SHA
tree identity where available
source ref context

The Atlas must reconstruct the addressed repository world at the
selected commit.

Required frame-to-frame classifications:

PERSISTED

APPEARED

DISAPPEARED

CONTENT_CHANGED

PATH_CHANGED
only when the underlying identity relation is mechanically supportable

IDENTITY_UNRESOLVED
when rename / move identity cannot be lawfully established

RELATION_ADDED

RELATION_REMOVED

The same object should retain stable identity across frames only where
the identity rule is actually supported.

Do not force continuity across ambiguous rename / rewrite boundaries.

# ==================================================
# 3. TEMPORAL CAMERA / SELECTION LAW
# ==================================================

Scrubbing history must preserve operator orientation where possible.

When selected object survives into adjacent frame:

preserve selection
preserve focus
preserve camera neighborhood where practical

When selected object does not exist:

show:

OBJECT_NOT_PRESENT_IN_FRAME

not:

silent deselection
synthetic persistence

When identity across frames is unresolved:

show:

IDENTITY_UNRESOLVED

not:

automatic rename continuity.

# ==================================================
# 4. STEP TWO — TRANSITION EMISSION V0
# ==================================================

OBJECT_ID:
ATLAS_TRANSITION_EMISSION_V0

A transition between adjacent frames becomes an explicit visual event.

Canonical structure:

FRAME N
→
SOURCE-SUPPORTED TRANSITION
→
FRAME N+1

A transition event must be generated from the mechanical diff /
admitted evidence between exact frames.

Candidate visual primitive:

SOURCE OBJECT / REGION
→ bounded pulse / wave / light emission
→ affected object / region
→ decay

This is a perceptual cue.

It must not imply unsupported causation.

Freeze:

EMISSION
=
VISUALIZATION OF AN ESTABLISHED TRANSITION

EMISSION
!=
PROOF OF SEMANTIC CAUSE

# ==================================================
# 5. EMISSION SCALE REGIMES
# ==================================================

QUIESCENT / LOCAL SCALE:

show individual transition emissions

Examples:

file appears
file content changes
relation is added
episode classification changes

MID SCALE:

aggregate nearby transitions into regional activity bundles

GLOBAL SCALE:

project only large-scale density / direction / persistent growth

Target:

avoid turning high activity into visual noise.

The same underlying transition ledger should support all three scales.

FILTERING
!=
DELETION OF HISTORY

AGGREGATION
!=
NEW EVIDENCE

# ==================================================
# 6. TRANSITION CHALLENGE HANDLE
# ==================================================

Every visible transition must be challengeable.

Selecting an emission should expose:

FROM_FRAME
TO_FRAME

SOURCE_OBJECT(S)

DESTINATION_OBJECT(S)

MECHANICAL_DIFF

CONTENT / BLOB IDENTITIES

RELATIONS ADDED / REMOVED

ACTOR LINEAGE:
EXPLICIT | UNRESOLVED

SEMANTIC LINEAGE:
EXPLICIT | UNRESOLVED

SOURCE HANDLES

If semantic causation is unknown, say so.

# ==================================================
# 7. STEP THREE — ACTOR / SEAT / CURSOR PROJECTION V0
# ==================================================

OBJECT_ID:
ATLAS_ACTOR_PROJECTION_V0

Seats and cursors become first-class visible Atlas objects only from
existing source-bound seat / cursor / continuity artifacts.

Freeze:

SEAT
!=
CURSOR

CURSOR
!=
ATTENTION

ATTENTION
!=
AUTHORITY

AUTHORITY
!=
EXECUTION

SEAT
=
PERSISTENT OPERATIONAL LOCUS

CURSOR
=
RECONSTRUCTION / CONTINUITY COORDINATE

A seat may be large and visually obvious.

A cursor may be separately visible and associated with its seat through
an explicit relation.

Do not represent inferred live attention unless a source records it.

# ==================================================
# 8. ACTOR VISUAL REQUIREMENT
# ==================================================

Seats and cursors should be perceptually distinguishable from passive
repository objects across the whole-world view.

Minimum:

SEAT:
large explicit glyph / sprite / volume

CURSOR:
smaller but distinct marker

Do not spend this phase on elaborate skins.

Need only enough distinction that the operator can answer quickly:

WHERE IS LABBOIB?

WHERE IS ITS CURSOR?

WHAT EXPLICIT OBJECTS / EVENTS IS IT RELATED TO?

# ==================================================
# 9. ACTOR LINEAGE RELATIONS
# ==================================================

Only emit actor relations from explicit evidence.

Allowed candidate relations when source-supported:

SEAT_HAS_CURSOR

SEAT_REGISTERED_OBJECT

SEAT_EVALUATED_EPISODE

SEAT_RECEIVED_HANDOFF

SEAT_EMITTED_DISTINCTION

SEAT_EXECUTED_MUTATION

CURSOR_REFERENCES_STATE

CURSOR_ADVANCED_TO

SEAT_WITNESSED_EVENT

Do NOT emit:

SEAT_BUILT_FILE

SEAT_CAUSED_COMMIT

SEAT_INTENDED_CHANGE

unless an admitted source explicitly supports it.

For historical repository content with no actor lineage:

ACTOR:
UNRESOLVED

That is a valid result.

# ==================================================
# 10. GIT AUTHORSHIP PROJECTION
# ==================================================

Git author / committer metadata may be rendered as a separate
MECHANICAL AUTHORSHIP layer.

It must be labeled distinctly from seat lineage.

Example:

GIT_AUTHOR:
<metadata>

SEAT_ACTOR:
UNRESOLVED

SEMANTIC_CAUSE:
UNRESOLVED

This separation is mandatory.

# ==================================================
# 11. FIRST HISTORICAL WOUND REPLAY
# ==================================================

After Steps 1–3 are usable, select one existing historical wound that
has enough surviving artifacts to pressure the instrument.

Preferred candidate families:

REFERENCE_REACHABILITY
!=
REFERENCE_ADMISSION

HISTORICAL_AUTHORITY
!=
CURRENT_AUTHORITY

CURRENT_TRUTH
!=
DECISION_TIME_BASIS

DECLARATION
!=
ENFORCEMENT
!=
VERIFICATION

PATH_IDENTITY
!=
CONTENT_IDENTITY

SEAT
!=
OCCUPANT
!=
INVOCATION

Use whichever candidate has the clearest exact source / commit /
pressure history.

Do not manufacture a full semantic lineage if the historical record
does not contain one.

# ==================================================
# 12. WOUND REPLAY PROCEDURE
# ==================================================

1. locate earliest recoverable frame relevant to the wound;

2. scrub forward through exact Git frames;

3. identify mechanically visible transformations;

4. render transition emissions;

5. enable actor layer;

6. mark actor lineage explicit where supported;

7. leave actor lineage unresolved where unsupported;

8. project the wound's scientific distinctions over the same world;

9. inspect when the distinction first becomes source-supported;

10. inspect later repairs / pressures;

11. ask whether a fresh seat can reconstruct the wound from the Atlas
    without receiving the original conversation;

12. record translation loss.

# ==================================================
# 13. FIRST SEMANTIC THROUGHPUT MEASURES
# ==================================================

For the wound replay, record at minimum:

IDENTITY_RETENTION

Which required object identities survive frame translation?

DISTINCTION_RETENTION

Which operational non-collapses survive?

PROVENANCE_RETENTION

Can claims still be traversed to exact support?

ACTOR_LINEAGE_RETENTION

Can responsibility / participation be established where claimed?

UNRESOLVED_HONESTY

Does the instrument preserve unknown regions rather than smoothing them?

RECONSTRUCTION_COST

How much external context is needed for a fresh seat to recover the
scientific posture?

CROSS_SEAT_VARIANCE

Do independent seats reconstruct materially different operational
relations from the same addressed world?

# ==================================================
# 14. IMPORTANT EXPECTED FINDING
# ==================================================

It is acceptable, and likely, that early history will show:

MECHANICAL LINEAGE:
HIGH

SEMANTIC LINEAGE:
PARTIAL

ACTOR / SEAT LINEAGE:
LOW OR UNRESOLVED

This is not a failure of the Atlas.

It is a measurement of the historical instrumentation deficit.

Future seat operations can then improve lineage prospectively by
emitting explicit receipts / registrations / cursor transitions.

# ==================================================
# 15. PROSPECTIVE LINEAGE LAW
# ==================================================

Once actor projection exists, future work should begin preserving:

WHO / WHICH SEAT

OPERATED ON WHAT OBJECT

UNDER WHICH FRAME

USING WHICH SOURCE BASIS

WITH WHAT AUTHORITY

WHAT TRANSFORMATION WAS INTENDED

WHAT TRANSFORMATION WAS REALIZED

WHAT WITNESS CONFIRMED IT

WHAT REMAINED UNRESOLVED

This should be learned from pressure, not imposed as a giant generic
schema before the first replay.

# ==================================================
# 16. REQUIRED AUTOMATED PRESSURES
# ==================================================

T01
Same commit always reconstructs same source frame.

T02
Adjacent-frame diff is deterministic.

T03
Source-order shuffle does not alter frame identity.

T04
Object persistence is not inferred across unsupported identity changes.

T05
Missing historical object becomes OBJECT_NOT_PRESENT_IN_FRAME.

T06
Transition emission always binds exact from/to frames.

T07
No visual emission exists without a source-supported transition.

T08
Aggregation does not alter underlying event identities.

A01
Seat object exists only from source-bound seat evidence.

A02
Cursor object exists only from source-bound cursor evidence.

A03
Git author never silently becomes seat actor.

A04
Missing actor provenance renders UNRESOLVED.

A05
Actor layer toggle preserves repository object identity.

W01
Historical wound replay can traverse exact frames.

W02
Every projected scientific distinction has a challenge handle.

W03
Missing semantic lineage stays unresolved.

W04
Fresh reconstruction can report what cannot be recovered.

# ==================================================
# 17. HUMAN ACCEPTANCE PRESSURE
# ==================================================

The operator should be able to:

1. open Atlas;

2. select an early commit;

3. scrub forward and visibly watch repository growth / mutation;

4. pause on one transition;

5. click its emission;

6. inspect exact diff / source handles;

7. ask "who caused this?";

8. receive:
   explicit seat lineage
   OR
   explicit Git authorship
   OR
   UNRESOLVED
   without collapse between them;

9. enable seats / cursors;

10. locate a known seat immediately if admitted;

11. replay one historical wound;

12. determine whether the Atlas improved understanding.

# ==================================================
# 18. INSTRUMENT QUALITY LEDGER
# ==================================================

Record:

MORE VISIBLE:
...

EASIER TO REASON ABOUT:
...

HARDER / NOISIER:
...

MISLEADING MOTION:
...

MISSING LINEAGE:
...

MISSING RELATION:
...

ACTION ENABLED:
...

ERROR CAUSED:
...

WHAT REQUIRED PROSE OUTSIDE THE ATLAS:
...

WHAT A FRESH SEAT COULD RECONSTRUCT:
...

# ==================================================
# 19. OUT OF SCOPE
# ==================================================

DO NOT YET IMPLEMENT:

live runtime telemetry

synthetic seat attention

seat write authority

clocked autonomous ecology

recognition enforcement

eligibility enforcement

authority-path mutation

network / filesystem / process membrane

semantic causation inferred from commit history

automatic agent credit assignment

global causal DAG

generic dependency inference

full host-computer Atlas

# ==================================================
# 20. REQUIRED RETURN
# ==================================================

Return:

1. exact files added / modified;

2. exact history source used;

3. frame identity rule;

4. object persistence rule;

5. rename / move ambiguity rule;

6. transition event model;

7. emission rendering model;

8. aggregation / scale behavior;

9. seat source artifacts admitted;

10. cursor source artifacts admitted;

11. exact actor-lineage relations available;

12. exact actor-lineage gaps;

13. exact distinction between Git authorship and seat lineage;

14. first wound selected;

15. replay result;

16. tests and counts;

17. screenshot / capture if available;

18. explicit unresolveds;

19. explicit confirmation:

TEMPORAL SUCCESSION
!=
CAUSATION

GIT AUTHOR
!=
SEAT ACTOR

EMISSION
!=
SEMANTIC CAUSE

MISSING LINEAGE
=
UNRESOLVED

NO NEW AUTHORITY
NO NEW EXECUTION
NO NEW CONTROL PATH

# ==================================================
# CLAIM CEILING
# ==================================================

This package may establish:

source-bound historical frame navigation;

deterministic mechanical transitions between repository frames;

challengeable visual transition emissions;

source-bound seat / cursor projection where evidence exists;

an empirical measure of historical lineage gaps;

a first historical-wound replay over the Atlas.

It does NOT establish:

complete semantic provenance of repository history;

correct actor attribution where explicit evidence is absent;

causal authorship from Git metadata;

live seat attention;

runtime causality;

semantic coherence across seats;

authority recognition correctness;

safe autonomous consequence.

Those remain pressure targets.

# ==================================================
# STOP CONDITION
# ==================================================

STOP WHEN:

A REAL HISTORICAL REPOSITORY TRANSITION
CAN BE:

NAVIGATED
→
SEEN
→
CHALLENGED
→
ATTRIBUTED WHERE SUPPORTED
→
LEFT UNRESOLVED WHERE NOT SUPPORTED

AND

ONE HISTORICAL WOUND
HAS BEEN REPLAYED THROUGH THE SAME ATLAS

WITHOUT INVENTING
SEMANTIC OR ACTOR LINEAGE.
