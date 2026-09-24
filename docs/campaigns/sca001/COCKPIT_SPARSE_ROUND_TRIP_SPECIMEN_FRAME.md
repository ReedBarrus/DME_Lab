# COCKPIT SPARSE ROUND-TRIP — SPECIMEN FRAME

OBJECT_TYPE:
COCKPIT_SPECIMEN_IMPLEMENTATION_FRAME

STATUS:
SECOND SPECIMEN / AFTER CELL 002

PURPOSE:

Prove that Cockpit can visualize an experimentally important
unknown interval without inventing an event or trajectory.

USE EXISTING:

src/projection/draci_local_frame_v0.py

and the exact sparse-observation evidence / source refs already
required by that projector.

# ==================================================
# REQUIRED VISUAL
# ==================================================

FRAME 0

observation occurrence:
A

configuration:
alpha

        |
        |
        | UNKNOWN REGION
        |
        | event:
        | NOT_DERIVED
        |
        | event hypothesis:
        | UNRESOLVED
        |
        | intermediate trajectory:
        | UNRESOLVED
        |
        v

FRAME 1

observation occurrence:
B

configuration:
alpha-equivalent

# ==================================================
# REQUIRED RELATIONAL DISPLAY
# ==================================================

Render simultaneously:

CONFIGURATION(A)
EQUIVALENT_TO
CONFIGURATION(B)

and:

OCCURRENCE(A)
!=
OCCURRENCE(B)

Do not visually collapse equivalent configuration into
identical occurrence.

# ==================================================
# UNKNOWN REGION LAW
# ==================================================

The interval between admitted endpoint observations must be
rendered as UNKNOWN_REGION.

Cockpit must not draw:
- an inferred event;
- an inferred intermediate state;
- a continuous trajectory;
- a causal path;

unless a separate admitted source supplies it.

UNKNOWN
MUST REMAIN VISIBLE AS UNKNOWN.

# ==================================================
# EDGE INSPECTOR
# ==================================================

For FRAME 0 -> UNKNOWN REGION -> FRAME 1 show:

endpoint source refs
endpoint content identities
configuration relation
occurrence relation
observation depth
currentness standing
event hypothesis standing
consequence closure standing
unresolved coordinates

# ==================================================
# ACCEPTANCE CRITERION
# ==================================================

A human should be able to see immediately that:

1. the two endpoint observations are distinct occurrences;
2. their configurations are equivalent under the admitted basis;
3. the interval between them is unobserved;
4. no event is derived for the interval;
5. trajectory and consequence closure remain unresolved;
6. the projection itself is DERIVED_VIEW_ONLY;
7. every claim resolves to retained source / basis references.

This specimen exists specifically to pressure Cockpit against
inventing continuity where the science does not admit it.
