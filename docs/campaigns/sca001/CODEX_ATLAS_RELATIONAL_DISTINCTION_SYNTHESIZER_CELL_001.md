# CODEX — ATLAS RELATIONAL-DISTINCTION SYNTHESIZER CELL 001

OBJECT_TYPE:
CODEX_IMPLEMENTATION_WARRANT

OBJECT_ID:
ATLAS_RELATIONAL_DISTINCTION_SYNTHESIZER_CELL_001

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

TARGET:
EXISTING_ATLAS_PRIMARY_SURFACE
+
TYPED_DISTINCTION_REGISTRY_V0

MODE:
MINIMUM EXECUTABLE PRESSURE
+
SOURCE-BOUND SYMBOLIC / RELATIONAL REGISTRATION

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
REPO_LOCAL_ONLY

CONTROL_EFFECT:
NONE


# ==================================================
# PURPOSE
# ==================================================

Implement the first executable metabolic cell for the Atlas:

Teach the Atlas to register one challenged symbolic distinction
as a typed relation over mechanically grounded objects,
then replay the scientific actor cycle
until that relation survives reconstruction.

The first target distinction is:

PATH_IDENTITY
!=
CONTENT_IDENTITY

This cell should be small enough to falsify quickly.


# ==================================================
# SOURCE BASIS
# ==================================================

Use the current branch:

draci-v0-candidate-basis

Read and preserve the current contracts in:

docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_TYPED_DISTINCTION_LATTICE_METABOLIC_CELL_V0.md

docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_RELATIONAL_DISTINCTION_SYNTHESIZER_TECHNICAL_FRAME_V0.md

docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_DEPENDENCE_WITNESS_TOPOLOGY_DEVELOPMENT_PLAN_V0.md

Do not broaden beyond Cell 001 unless required to make the target pressure executable.


# ==================================================
# PRIMARY LAW
# ==================================================

SAME ADDRESSED OBJECTS
MAY PARTICIPATE
MECHANICALLY,
SYMBOLICALLY,
AND
RELATIONALLY

WITHOUT
BECOMING DIFFERENT OBJECTS.


DISTINCTION
!=
MECHANICAL EDGE

RELATION
!=
DEPENDENCE

DEPENDENCE
!=
AUTHORITY

REGISTERED AUTHORITY RELATION
!=
ACTIVE AUTHORITY

STATE EXISTS
!=
STATE IS ADMITTED


# ==================================================
# SCIENTIFIC CYCLE
# ==================================================

Use the local operator cycle:

OBSERVE
→
EVALUATE
→
REGISTER
→
WITNESS
→
RECONSTRUCT
→
SETTLE

For this cell:

OBSERVE:
exact Git history already supporting
PATH_IDENTITY != CONTENT_IDENTITY

EVALUATE:
construct the candidate typed distinction

REGISTER:
write the source-bound distinction into the registry

WITNESS:
preserve exact support handles and standing

RECONSTRUCT:
fresh reconstruction from Atlas / registry only

SETTLE:
retain the distinction with explicit claim ceiling and unresolveds


# ==================================================
# CELL 001 TARGET
# ==================================================

DISTINCTION:

PATH_IDENTITY
!=
CONTENT_IDENTITY

Use the already reconstructed historical specimen around:

src/cockpit/observer/repository_fabric_app.mjs

and the exact frame / blob identities produced by the temporal lineage implementation.

Do NOT restate the distinction from prose alone.

The mechanical support must resolve from exact repository history.


# ==================================================
# MINIMUM REGISTRY OBJECT
# ==================================================

Implement the smallest pressureable distinction record.

Candidate fields:

distinction_id

subject_addresses

relation_type

object_addresses
or
value

scope

source_handles

constructed_by

constructed_at

observed_at

evaluated_at

standing

currentness

claim_ceiling

dependencies

unresolved

If any field proves unnecessary, document the pressure that justifies removing it.

If any field proves insufficient, add only the minimum missing field and explain why.


# ==================================================
# CELL 001 ADMISSION RULE
# ==================================================

The distinction may be admitted only if:

1. the subject address resolves;

2. the source frames resolve;

3. same-path continuity is mechanically established;

4. at least two distinct content / blob identities are established;

5. the relation type is explicit;

6. exact source handles are retained;

7. claim ceiling is present;

8. current standing is explicit.

Failure of required support must result in:

UNRESOLVED
or
NOT_ADMITTED

not:

synthetic completion.


# ==================================================
# MECHANICAL / SYMBOLIC / RELATIONAL SPLIT
# ==================================================

MECHANICAL:

same repository path persists across admitted adjacent frames

and

blob / content identity changes.

SYMBOLIC:

PATH_IDENTITY
!=
CONTENT_IDENTITY

RELATIONAL:

the distinction applies to the exact addressed path / file-version objects
supported by the admitted mechanical specimen.

Do not let the symbolic distinction replace the mechanical evidence.

Do not let visual geometry stand in for the relation.


# ==================================================
# DEPENDENCE SEAM
# ==================================================

Do NOT implement general dependence inference yet.

Only expose an explicit seam for later typed dependence.

For Cell 001, it is enough to make the distinction reconstructable.

If a dependence is registered, it must be source-supported and typed.

No generic:

CONNECTED_TO

should silently become:

DEPENDS_ON.


# ==================================================
# ATLAS PROJECTION
# ==================================================

Project the admitted distinction onto the existing Atlas.

Minimum interaction:

SELECT:
repository_fabric_app.mjs

→
SEE:
PATH_IDENTITY != CONTENT_IDENTITY

→
SEE:
exact source frames / blobs

→
SEE:
standing

→
SEE:
claim ceiling

→
SEE:
unresolveds

The projection may be visually simple.

Do not spend this cell on complex lattice geometry.


# ==================================================
# RECONSTRUCTION PRESSURE
# ==================================================

Create a fresh reconstruction packet that excludes the original conversation.

Supply only:

- distinction address;
- subject address;
- source handles;
- current standing;
- claim ceiling;
- dependencies;
- unresolveds.

Ask reconstruction to return:

1. exact distinction;

2. what mechanically supports it;

3. where it applies;

4. what it does NOT establish;

5. current standing;

6. unresolveds.

Success criterion:

OPERATIONAL POSTURE CONSERVED

not:

IDENTICAL WORDING.


# ==================================================
# REQUIRED NEGATIVE PRESSURES
# ==================================================

P01
Same distinction text
+
wrong subject address
→
NOT_ADMITTED / UNRESOLVED

P02
Same subject
+
same blob identity only
→
insufficient to establish PATH_IDENTITY != CONTENT_IDENTITY

P03
Missing source handle
→
standing degrades

P04
Missing claim ceiling
→
admission fails or degrades

P05
Historical frame presented as current state
→
must not silently become CURRENT

P06
Mechanical path continuity exists
but content comparison absent
→
distinction unresolved

P07
Visual relation exists
without registry/source support
→
must not count as admitted relation

P08
Fresh reconstruction expands scope beyond admitted specimen
→
FAIL

P09
Registry entry survives
but provenance is broken
→
FAIL

P10
Relation record accidentally produces authority effect
→
FAIL


# ==================================================
# RECONSTRUCTION INVARIANTS
# ==================================================

The following must survive:

subject identity

relation type

source handles

standing

claim ceiling

unresolved boundary

mechanical applicability

The following MAY vary:

prose

render order

visual placement

seat-specific explanation


# ==================================================
# STORAGE
# ==================================================

Prefer a source-controlled V0 registry.

Do NOT introduce a heavy graph database.

Acceptable shape:

canonical distinction records
+
derived projection artifact
+
tests

Keep generated projection data clearly separate from source-of-truth records.


# ==================================================
# UI / INSPECTOR
# ==================================================

In the Atlas inspector, add a compact section:

DISTINCTIONS

For the selected object, show:

relation type

standing

currentness

source handles

claim ceiling

dependencies

unresolveds

challenge / reconstruction handle

No automatic execution controls.


# ==================================================
# TEST MODULES
# ==================================================

At minimum add focused tests for:

distinction schema

source binding

mechanical support

relation typing

currentness

claim ceiling

provenance preservation

reconstruction

scope expansion failure

authority non-minting

Atlas projection

Run existing Cockpit suites and report all pre-existing failures separately.


# ==================================================
# REQUIRED RETURN
# ==================================================

Return:

1. exact files added / modified;

2. distinction record schema;

3. exact Cell 001 registry record;

4. exact source frames / blobs admitted;

5. exact admission logic;

6. exact negative-pressure outcomes;

7. reconstruction packet;

8. reconstruction result;

9. Atlas projection behavior;

10. tests and counts;

11. screenshot if available;

12. explicit unresolveds;

13. explicit confirmation:

MECHANICAL EVIDENCE
!=
SYMBOLIC DISTINCTION

SYMBOLIC DISTINCTION
!=
AUTHORITY

REGISTERED RELATION
!=
EXECUTABLE RELATION

STATE EXISTS
!=
STATE IS ADMITTED

NO NEW AUTHORITY
NO EXTERNAL EXECUTION
NO SYNTHETIC PROVENANCE


# ==================================================
# OUT OF SCOPE
# ==================================================

DO NOT YET IMPLEMENT:

broad symbolic extractor

conversation ingestion

automatic distinction admission

general dependence inference

stake scoring

witness-class automation

continuity horizon calculation

recognition enforcement

eligibility enforcement

authority mutation

live seat execution

network / process / filesystem consequence control

global ontology

adaptive semantic geometry


# ==================================================
# STOP CONDITION
# ==================================================

STOP WHEN:

PATH_IDENTITY != CONTENT_IDENTITY

IS:

SOURCE-BOUND
→
REGISTERED
→
PROJECTED
→
CHALLENGED
→
RECONSTRUCTED

OVER
REAL MECHANICAL OBJECTS

WITHOUT LOSING:

IDENTITY
PROVENANCE
CLAIM CEILING
CURRENTNESS
UNRESOLVED BOUNDARY.

Do not proceed to Cell 002 until this cell is human-pressured.
