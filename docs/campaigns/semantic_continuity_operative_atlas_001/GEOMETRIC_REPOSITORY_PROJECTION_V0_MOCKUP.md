# GEOMETRIC REPOSITORY PROJECTION V0 — IMPLEMENTATION MOCKUP

OBJECT_TYPE:
COCKPIT_PROJECTION_IMPLEMENTATION_MOCKUP

STATUS:
READY_FOR_CODEX

SOURCE BASIS:
existing REPOSITORY_ADDRESS_FABRIC_V0

PURPOSE:

Stop representing the repository as a list/tree browser.

Build the first actual geometric projection of the Lab:

ALL ADDRESSABLE REPOSITORY OBJECTS
+
MECHANICAL RELATIONS
→
ONE CONTINUOUS NAVIGABLE 2D FIELD

PRIMARY LAW:

GEOMETRY MUST COMPRESS RELATIONAL DIFFERENCE.

UNKNOWN SEMANTICS
!=
INVISIBLE OBJECT

ZOOM
!=
NEW DATA MODEL

BASIS CHANGE
!=
NEW OBJECT IDENTITY

FILTER
!=
OBJECT DELETION

# ==================================================
# 1. WHAT THIS IS
# ==================================================

This is NOT:

- a file explorer;
- a directory page;
- a scrollable object list;
- a card matrix;
- a dashboard of typed fields;
- a collection of special-case viewers.

This IS:

- one continuous 2D projection surface;
- every repository object placed in the same navigable field;
- object identity stable under camera movement and basis change;
- geometry derived from source-bound relations;
- local inspection attached to selected objects without replacing the field.

The address fabric remains the source substrate.

The projection is a view over it.

# ==================================================
# 2. PRIMARY COORDINATE BASIS
# ==================================================

V0 uses only mechanically grounded coordinates.

PRIMARY STRUCTURAL COORDINATES:

A. PATH / CONTAINMENT
   repository
   → directory
   → file
   → file_version

B. DEPENDENCY / REFERENCE
   mechanically derived import/reference edges where available

C. VERSION / CONTENT
   commit
   blob identity
   content identity

V0 must NOT infer semantic role from filenames.

The first rendered basis should be:

STRUCTURAL_BASIS_V0

with strong weight on containment
and secondary weight on dependency/reference relations.

# ==================================================
# 3. GEOMETRIC MODEL
# ==================================================

Use a simple, pressureable relation-driven embedding.

Preferred V0:

HIERARCHICAL FORCE / RADIAL HYBRID

Interpretation:

- repository root = global anchor;
- directories = containment wells / cluster anchors;
- files = stable points within directory regions;
- file versions = smaller attached points or local satellites;
- dependency/reference edges = cross-region attraction links;
- containment prevents unrelated objects from collapsing into one cluster.

The exact algorithm is not sacred.

The invariant is:

POSITION MUST BE A CONSEQUENCE OF RELATIONS,
NOT ALPHABETICAL ORDER OR SCROLL ORDER.

A deterministic seed / stable layout basis is required so the same source state
does not randomly reshuffle on every load.

# ==================================================
# 4. BASIS WEIGHT MODEL
# ==================================================

V0 supports one explicit mutable basis weighting object.

Example:

basis = {
  containment: 1.0,
  dependency: 0.35,
  version: 0.10
}

Changing weights must deform the same object field.

NO object recreation.
NO identity remapping.
NO new data model.

Later modes may add:

runtime_interaction
authority_relation
scientific_relation
semantic_relation
temporal_relation

but V0 need only prove one mutable structural basis.

# ==================================================
# 5. CAMERA / NAVIGATION
# ==================================================

Required:

- continuous pan;
- continuous zoom;
- zoom-to-selected;
- reset-to-whole-repository;
- click object to select;
- preserve selected object identity while camera changes;
- preserve selected object identity while basis weights change.

Optional if cheap:

- drag-to-rotate if using pseudo-3D presentation;
- minimap;
- search-to-focus by exact path/address.

Search is an accelerator only.

Search MUST NOT become the primary navigation model.

# ==================================================
# 6. VISUAL ENCODING
# ==================================================

Keep V0 minimal.

Repository:
global anchor / outer field

Directory:
cluster boundary / region well

File:
primary node

File version:
secondary / satellite node

Dependency/reference:
visible edge

Containment:
encoded spatially and optionally by weak boundary/edge

Selected object:
visually emphasized without moving identity

Unknown semantic standing:
visible normally
not dimmed into irrelevance

Do NOT add decorative pseudo-physics unrelated to source relations.

# ==================================================
# 7. MOCKUP — WHOLE REPOSITORY
# ==================================================

Conceptual only:

                      docs/
                 .  .  .  .  .
              .                 .
            .      campaign      .
           .                     .
          .                       .

                   src/
          . . . . . . . . . . . . .
       .                               .
      . cockpit/        runtime/        .
      .   o--o--o          o--o         .
      .    \  |            \ |         .
      .     o  o             o          .
       .                               .
          . . . . . . . . . . . . .

                     tests/
                .  .  .  .  .

Cross-region dependency edges may bridge clusters.

The operator should perceive:
clusters
bridges
isolates
dense regions
cross-directory dependencies

without reading 1200 labels.

# ==================================================
# 8. MOCKUP — ZOOMED REGION
# ==================================================

WHOLE REPO
→ zoom toward src/cockpit/observer

Field resolves more detail:

observer/
   app.mjs ----------------------+
      |                          |
      v                          v
perceptual_instrument.mjs ---> repository_fabric_app.mjs
      |                          |
      +----> runtime_live.mjs    +----> repository_fabric_model.mjs

Labels may appear progressively with zoom.

Same objects.
Same coordinates.
More resolved presentation.

FREEZE:

ZOOM
!=
SEMANTIC PROMOTION

# ==================================================
# 9. BASIS TRANSFORMATION BEHAVIOR
# ==================================================

Add one visible basis control.

Example:

STRUCTURAL BASIS

containment  [##########] 1.00
dependency   [###       ] 0.35
version      [#         ] 0.10

If dependency weight increases:

- cross-directory dependencies pull related nodes closer;
- containment still provides continuity;
- objects visibly move;
- edges persist;
- selected identity persists;
- camera may preserve focus.

The user must be able to WATCH the transformation.

This is the first proof that:

BASIS CHANGE
→ GEOMETRIC DEFORMATION

while:

OBJECT IDENTITY
and
SOURCE ADDRESS

remain invariant.

# ==================================================
# 10. LOCAL INSPECTOR
# ==================================================

Selecting an object opens a small inspector WITHOUT replacing the field.

Inspector may show:

canonical address
path
parent
commit
blob/content identity
mechanical relations
semantic standing

Inspector is subordinate to geometry.

Do NOT let typed fields consume the primary surface.

# ==================================================
# 11. CELL 002 FUTURE OVERLAY SEAM
# ==================================================

Do NOT implement full Cell-002 runtime overlay yet.

But preserve a seam where addressed objects participating in Cell 002 can later
receive projected relations.

Future example:

authority module
→ bridge
→ model boundary

and a recorded consequence trace may animate:

CAP ACTIVE / 1
→ reservation
→ invocation
→ consumed
→ replay
→ deny

over the SAME repository nodes.

The geometric repository projection must not require Cell-002-specific object duplication.

# ==================================================
# 12. FUTURE OPERATOR MODES
# ==================================================

Do not implement these yet.

The architecture must allow future basis modes over the same object manifold:

STRUCTURAL
RUNTIME
SCIENTIFIC
AUTHORITY
SEMANTIC

Each mode exposes different relation weights/dimension sets.

Same addresses.
Same object identities.
Different local projection.

Example future scientific basis:

held_fixed
changed
witnessed
unresolved

Example future runtime basis:

loaded
called
read
wrote
spawned
invoked
emitted

# ==================================================
# 13. FIRST HUMAN PRESSURES
# ==================================================

PRESSURE 1 — WHOLE-REPO LEGIBILITY

Question:
Can the operator see the entire repository as one coherent object
without scrolling through every file?

Expected:
YES

PRESSURE 2 — REGION RECOVERY

Question:
Can the operator visually recover the src/cockpit region and move into it
without traversing an alphabetical list?

Expected:
YES

PRESSURE 3 — RELATIONAL DIFFERENCE

Question:
Do dependency-connected files appear geometrically different from merely co-located files?

Expected:
YES, where dependency relations are mechanically available.

PRESSURE 4 — BASIS DEFORMATION

Question:
Can changing a basis weight visibly deform the projection
while preserving exact object identity?

Expected:
YES

PRESSURE 5 — UNKNOWN != INVISIBLE

Question:
Does an uninterpreted file remain present in the geometric field?

Expected:
YES

# ==================================================
# 14. MACHINE PRESSURES
# ==================================================

The same selected object must expose a canonical source address usable by a seat.

Future seat-facing pressure:

OPERATOR SELECTS X
→ ADDRESS X EXTRACTED
→ SEAT RECEIVES SAME X
→ NO AUTHORITY TRANSFER
→ NO OBJECT RECONSTRUCTION FROM PROSE

Do not implement seat transport in V0.

Preserve the address seam.

# ==================================================
# 15. REQUIRED IMPLEMENTATION RETURN
# ==================================================

Return:

A. exact files added/modified;

B. exact layout algorithm selected;

C. exact mechanically derived relations used;

D. deterministic layout / seed strategy;

E. exact camera interactions;

F. basis-weight controls implemented;

G. how object identity is preserved during deformation;

H. how zoom changes presentation without changing model identity;

I. total rendered objects and relations;

J. performance at whole-repo scale;

K. tests proving:
   - all objects remain addressable;
   - unknown objects remain visible;
   - basis change preserves identity;
   - camera movement preserves identity;
   - no semantic inference is introduced;
   - no authority/execution/control path is introduced;

L. one screenshot if possible;

M. explicit confirmation:

GEOMETRY IS RELATION-DRIVEN
NOT LIST-ORDER-DRIVEN

OBJECT IDENTITY SURVIVES BASIS CHANGE

NO NEW AUTHORITY
NO NEW EXECUTION
NO NEW CONTROL PATH

# ==================================================
# 16. STOP CONDITION
# ==================================================

STOP when there is one real continuous 2D repository projection
that can render the existing address fabric at whole-repo scale
and visibly deform under at least one basis-weight change.

Do NOT proceed to:

runtime animation
scientific invariance overlay
authority overlay
semantic role inference
Town Square
seat invocation

until this projection itself is human-tested.
