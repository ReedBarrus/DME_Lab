# REPOSITORY ADDRESS FABRIC V0 — IDENTITY-FIRST PROJECTION FRAME

OBJECT_TYPE:
IMPLEMENTATION / PRESSURE FRAME

STATUS:
NEXT COCKPIT SUBSTRATE TARGET

PRIMARY PURPOSE:

Make the repository itself navigable as a shared address space
without requiring a custom semantic adapter for every file.

PRIMARY LAW:

UNKNOWN SEMANTICS
!=
INVISIBLE OBJECT

EVERY DISCOVERABLE REPOSITORY OBJECT
SHOULD BE ADDRESSABLE BEFORE IT IS SEMANTICALLY INTERPRETED.

# ==================================================
# 1. SOURCE SUBSTRATE
# ==================================================

Initial substrate:

Git repository at one explicit commit / branch coordinate.

Initial discoverable objects:

REPOSITORY
DIRECTORY
FILE
FILE VERSION / BLOB

Do NOT require campaign / test / trace / authority interpretation
before these objects become visible.

# ==================================================
# 2. MINIMUM OBJECT IDENTITY
# ==================================================

For each repository object preserve at minimum:

object_kind

repository_identity

source_commit

path

parent_path

content_identity when applicable

git_blob_identity when applicable

existence_standing

semantic_standing

Suggested semantic standing for an uninterpreted file:

UNINTERPRETED

This means:

OBJECT EXISTS
SEMANTIC ROLE NOT YET DERIVED

not:

UNKNOWN OBJECT

# ==================================================
# 3. ADDRESSING
# ==================================================

V0 addresses must be deterministic and reversible to source coordinates.

Do not require a final URI scheme yet.

A canonical address object may be represented structurally as:

{
  substrate: "repo",
  repository: "ReedBarrus/DME_Lab",
  commit: "<exact commit>",
  path: "<exact path>",
  object_kind: "file"
}

For file-version identity, include:

git_blob_sha
and/or
content_sha256

FREEZE:

PATH IDENTITY
!=
CONTENT IDENTITY

FILE OBJECT
!=
FILE VERSION

SAME PATH AT DIFFERENT COMMITS
MAY BE DIFFERENT VERSION OBJECTS

SAME CONTENT AT DIFFERENT PATHS
DOES NOT AUTOMATICALLY COLLAPSE OBJECT IDENTITY

# ==================================================
# 4. BASE RELATIONS
# ==================================================

The raw repository projection may assert only mechanically derivable relations:

repository CONTAINS directory

directory CONTAINS directory

directory CONTAINS file

file HAS_VERSION file_version

file_version MATERIALIZED_AT commit

file_version HAS_CONTENT_IDENTITY hash

Optional Git-native relations may be added only where directly derived:

commit PARENT_OF commit

commit MODIFIES path

Do NOT infer semantic relations from filename / directory proximity.

# ==================================================
# 5. FIBER-LIKE VISUALIZATION
# ==================================================

Initial visual interpretation MAY render:

repository
→ directory fibers
→ file fibers
→ version / blob points

But this is initially a projection metaphor.

Do NOT claim formal fiber-bundle structure yet.

Pressure later:

WHAT IS CONSERVED
WHEN MOVING:

repository → directory
directory → file
file → version
version → semantic projection

Potential conserved coordinates:

repository identity
path ancestry
content identity
provenance
currentness basis

The geometry becomes earned only where these conservation relations survive pressure.

# ==================================================
# 6. LOCAL TYPED BASIS OVERLAYS
# ==================================================

Typed semantics are overlays over addressed objects.

Examples:

TEST BASIS
may project a file as:
test apparatus

TRACE BASIS
may project a file as:
execution witness / recorded specimen

CAMPAIGN BASIS
may project a file as:
campaign artifact

AUTHORITY BASIS
may project a file / local object as:
policy / executor / capability support

SCIENTIFIC BASIS
may project:
control
intervention
observation
claim
unresolved
discriminator

Multiple typed projections may coexist over one addressed object.

FREEZE:

OBJECT IDENTITY
!=
TYPED ROLE

ONE OBJECT
MAY SUPPORT MULTIPLE LOCAL ROLES

TYPED PROJECTION
MUST RETAIN SOURCE ADDRESS

# ==================================================
# 7. INVARIANCE ROLE
# ==================================================

Do NOT make "invariance" the first global projection.

Instead:

invariance is a scientific / relational question applied to transformations
between addressed states.

Example:

FILE VERSION A
→ transformation
→ FILE VERSION B

Scientific projection asks:

WHAT REMAINED INVARIANT?
WHAT CHANGED?
WHICH REFERENCES SURVIVED?
WHICH SEMANTIC PROJECTIONS REMAIN VALID?
WHICH CLAIMS BECAME STALE?

Thus:

ADDRESS FABRIC
FIRST

INVARIANCE / CONSERVATION
AS EVALUATIVE PROJECTION
SECOND

# ==================================================
# 8. CONSEQUENCE-SPACE BRIDGE
# ==================================================

Repository objects become consequence-relevant only through explicit relations.

Example:

repo file
→ loaded as executable
→ process / invocation
→ runtime consequence

or:

repo test
→ executed by harness
→ witness trace
→ scientific standing

Cockpit should be able to traverse:

REPO OBJECT
→ OPERATIVE USE
→ RUNTIME TRANSFORMATION
→ CONSEQUENCE
→ WITNESS
→ SCIENTIFIC STANDING

without treating repository presence itself as runtime consequence.

# ==================================================
# 9. SHARED OPERATOR / SEAT ADDRESS
# ==================================================

One exact address must be usable by:

operator
seat
cursor context
Town Square message
scientific projection
authority request

without implying shared authority.

FREEZE:

SAME ADDRESS
!=
SAME VIEW

SAME ADDRESS
!=
SAME AUTHORITY

SAME ADDRESS
!=
SAME EVALUATION

TARGET:

REED selects object X
→ SOLA can receive X
→ LABBOIB can receive X
→ CODEX can receive X

all referencing the same source object identity.

# ==================================================
# 10. FIRST IMPLEMENTATION
# ==================================================

Build a read-only repository substrate projection that:

1. walks the repository tree at one exact commit;
2. emits repository / directory / file / version objects;
3. assigns deterministic source-bound addresses;
4. preserves parent containment relations;
5. records content / blob identity where available;
6. marks semantic standing UNINTERPRETED by default;
7. renders all objects in Cockpit without special semantic adapters;
8. lets the operator select one file and inspect its exact source coordinates.

DO NOT yet:

infer semantic role from filename
construct universal relation graph
render full 3D geometry
add write controls
add authority
add seat invocation
normalize all existing Cockpit models

# ==================================================
# 11. FIRST PRESSURES
# ==================================================

PRESSURE A — UNKNOWN != INVISIBLE

Add an arbitrary file with no known semantic adapter.

Expected:

file is visible
addressable
selectable

semantic_standing = UNINTERPRETED

PRESSURE B — PATH != CONTENT

Two files with identical bytes at different paths.

Expected:

distinct file objects
possibly same content identity

PRESSURE C — PATH ACROSS VERSION

Same path modified across commits.

Expected:

stable path relation if represented
distinct version objects / content identities

PRESSURE D — ADDRESS SHARING WITHOUT AUTHORITY

Operator and seat refer to same exact file address.

Expected:

same source referent

no authority transfer

no execution

# ==================================================
# 12. SUCCESS CRITERION
# ==================================================

Cockpit can answer for any repository file:

WHAT IS THIS OBJECT?

WHERE IS IT?

WHICH EXACT VERSION AM I LOOKING AT?

WHAT CONTAINS IT?

WHAT CONTENT IDENTITY DOES IT HAVE?

WHICH TYPED PROJECTIONS CURRENTLY APPLY?

WHICH SEMANTICS ARE STILL UNKNOWN?

and can hand the exact same address to another seat
without reconstructing the referent from prose.

# ==================================================
# CLAIM CEILING
# ==================================================

This frame does NOT establish:

formal fiber bundles
canonical global geometry
semantic correctness
runtime consequence linkage
authority linkage
dependency graph correctness
causal relation between files
scientific meaning of all repository objects

It establishes only the target for a source-bound shared address fabric.
