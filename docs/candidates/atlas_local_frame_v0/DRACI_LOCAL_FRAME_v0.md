# DRACI_LOCAL_FRAME_v0

```text
OBJECT_TYPE:
CANDIDATE_ATLAS_LOCAL_FRAME

OBJECT_ID:
DRACI_LOCAL_FRAME_v0

STATUS:
PROVISIONAL
LOCAL_ONLY
EVENT_ANCHORED
PROJECTION_RELATIVE
NON-CANONICAL

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCHEMA_FREEZE:
NO

ONTOLOGY_FREEZE:
NO
```

## 0. Purpose

Define the smallest stable local coordinate face through which DRACI may
snapshot, reconstruct, compare, pressure, and later simulate a bounded
relational situation.

The frame is a local chart.

It is not the world.

## 1. Projection anchor

Every local frame MUST declare:

```text
SUBJECT_ROLE:
S = ...

OBJECT_ROLE:
O = ...

FIELD_ROLE:
F = ...

SCOPE:
...

TEMPORAL_ANCHOR:
...

BASIS:
...
```

Freeze:

```text
S / O / F ROLE ASSIGNMENT
!=
OBJECT IDENTITY
```

One underlying object may occupy different projection roles under different
questions.

One specimen may therefore support multiple valid local frames.

## 2. Configuration triad

```text
S:
subject / acting configuration

O:
object / referent / other configuration

F:
relevant conditioning / supporting field configuration
```

`F` is projection-relative.

It MAY represent:

```text
runtime
repository
filesystem
peer ecology
institution
social environment
physical substrate
network
or another locally relevant support structure
```

Freeze:

```text
F
!=
UNIVERSAL ENVIRONMENT OBJECT
```

## 3. Primary relational face

The three configuration roles generate three primary pairwise projections:

```text
R_SO:
S ↔ O

R_SF:
S ↔ F

R_OF:
O ↔ F
```

These form the visible relational axis of the local frame.

Important:

```text
R_SO
+
R_SF
+
R_OF

!=
COMPLETE RELATIONAL FACTORIZATION
```

Higher-order joint coupling may span:

```text
multiple relations
multiple cells
multiple objects
multiple basis terms
```

Pairwise projections do not establish joint compositional standing.

Where required, higher-order coupling may be represented by:

```text
hyperedge
brace
shared dependency
joint correspondence
or another explicit non-cell-local relation
```

## 4. Temporal face

The visible temporal coordinates are:

```text
PRE
OPERATIVE
POST
```

They MAY render conversationally as:

```text
BEFORE
NOW
AFTER
```

but only relative to the declared:

```text
TEMPORAL_ANCHOR
```

Examples:

```text
before / during / after execution
before / during / after adjudication
before / during / after observation
before / during / after mutation
before / during / after historical event E
```

Therefore:

```text
A HISTORICAL EVENT
MAY HAVE ITS OWN OPERATIVE "NOW"

WITHOUT BEING
CURRENT NOW
```

## 5. Post mode

POST MUST NOT imply realized execution.

Where relevant, expose:

```text
PROJECTED
EXPECTED
ADJUDICATED
REALIZED
OBSERVED
RETAINED
```

Freeze:

```text
ADJUDICATED POSTCONDITION
!=
REALIZED POST-EXECUTION STATE
```

## 6. Local 3×3 face

```text
                    PRE            OPERATIVE           POST

S ↔ O            R_SO(pre)        R_SO(op)          R_SO(post)

S ↔ F            R_SF(pre)        R_SF(op)          R_SF(post)

O ↔ F            R_OF(pre)        R_OF(op)          R_OF(post)
```

Each cell is:

```text
A RELATIONAL-TEMPORAL
COORDINATE NEIGHBORHOOD
```

not:

```text
A COMPLETE STATE
A SINGLE VALUE
A COMPLETE CAUSAL OBJECT
```

## 7. Cell depth

Where evidence permits, each cell may expose:

```text
REALIZED RELATION
↓
OBSERVED RELATION
↓
EVIDENCE REPRESENTATION
↓
QUALIFIED STANDING
```

Freeze:

```text
REALIZED
!=
OBSERVED
!=
EVIDENCED
!=
QUALIFIED
```

This is depth on the same local face, not another required geometric axis.

## 8. Currentness

```text
OPERATIVE COLUMN
!=
CURRENTNESS
```

OPERATIVE means the temporal slice designated by the frame anchor.

CURRENTNESS means qualified correspondence establishing that a basis,
relation, standing, or operator is applicable at that operative slice.

Currentness may decorate, gate, invalidate, or qualify any operative projection.

## 9. Higher-order coupling

A local frame MAY carry explicit couplings across cells.

```text
JOINT COUPLING
MAY SPAN
MULTIPLE ROWS / OBJECTS / CELLS

PAIRWISE PROJECTIONS
DO NOT ESTABLISH
JOINT COMPOSITIONAL STANDING
```

This allows the 3×3 to remain visually finite without pretending all causal
structure is pairwise.

## 10. Local frame snapshot

A local frame snapshot records, where known:

```text
FRAME_ID
PROJECTION_IDENTITY
FRAME_CONTENT_IDENTITY

PROJECTION_ANCHOR
TEMPORAL_ANCHOR
BASIS

S CONFIGURATION
O CONFIGURATION
F CONFIGURATION

R_SO
R_SF
R_OF

HIGHER_ORDER_COUPLINGS

CURRENTNESS
AUTHORITY PROJECTION
OPERATOR PROJECTION
OBSERVATION DEPTH
LINEAGE REFERENCES
RECOVERY / VIABILITY PROJECTION
REALIZATION / HOSTING DEPENDENCIES

UNRESOLVED COORDINATES
```

Freeze:

```text
FRAME_ID
!=
FRAME_CONTENT_IDENTITY
!=
PROJECTION_IDENTITY
```

Unknown fields remain:

```text
UNRESOLVED
```

Do not fabricate completeness.

## 11. Global compilation

```text
LOCAL FRAME
=
PRIMARY EVIDENCE-BEARING MAP UNIT
```

```text
GLOBAL VIEW
=
COMPILED PROJECTION
OVER QUALIFIED LOCAL FRAMES
AND THEIR CORRESPONDENCE
```

Freeze:

```text
GLOBAL VIEW
!=
AUTHORITATIVE CONTINUOUS WORLD STATE
```

A global rendering may emerge from:

```text
local snapshots
+
event relations
+
lineage
+
qualified correspondence
+
shared identities / dependencies
```

## 12. Recursive charting

The same chart grammar may be reused at different scales by re-declaring:

```text
S
O
F
SCOPE
TEMPORAL_ANCHOR
BASIS
```

This is recursive charting, not recursive ontology.

## 13. Disposition

```text
CANDIDATE STABLE LOCAL ATLAS FRAME

USE FOR:
snapshotting
reconstruction
visualization
pressure localization
trajectory compilation
bounded simulation

NOT:
universal ontology
global state schema
complete causal factorization
continuous world simulation
```
