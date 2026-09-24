# ATLAS RELATIONAL-DISTINCTION SYNTHESIZER TECHNICAL FRAME V0

OBJECT_TYPE:
TECHNICAL_DESIGN_FRAME

OBJECT_ID:
ATLAS_RELATIONAL_DISTINCTION_SYNTHESIZER_V0

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

STATUS:
PROVISIONAL / PRE-IMPLEMENTATION

PURPOSE:

Define the smallest technical engine that can synthesize source-bound
typed distinctions and dependence relations over mechanically grounded
Atlas objects without inventing authority or semantic truth.

# ==================================================
# 1. DESIGN TARGET
# ==================================================

INPUT:

mechanical Atlas objects
+
source evidence
+
local scientific frame

OUTPUT:

candidate typed relations
+
candidate distinction cells
+
explicit support
+
standing
+
dependencies
+
unresolveds

NOT:

free-form semantic graph
automatic ontology
automatic authority
automatic truth.

# ==================================================
# 2. CORE OBJECTS
# ==================================================

DISTINCTION_CELL

RELATION_CELL

DEPENDENCE_CELL

WITNESS_CELL

PRESSURE_RESULT

Each is addressable and source-bound.

# ==================================================
# 3. DISTINCTION CELL
# ==================================================

Candidate fields:

distinction_id
subject_addresses[]
relation_type
object_addresses[]
value
scope
source_handles[]
constructed_by
constructed_at
observed_at
evaluated_at
standing
currentness
claim_ceiling
dependencies[]
unresolved[]
supersedes[]
conflicts_with[]

The engine must permit n-ary relations later,
but V0 may implement unary / binary cells first.

# ==================================================
# 4. RELATION CELL
# ==================================================

Candidate fields:

relation_id
relation_type
source_addresses[]
target_addresses[]
scope
support_handles[]
standing
currentness
constructed_by
claim_ceiling

relation_family:

MECHANICAL
SYMBOLIC
RELATIONAL
AUTHORITY
WITNESS
DEPENDENCE

Relation family is descriptive, not authority-granting.

# ==================================================
# 5. DEPENDENCE CELL
# ==================================================

Candidate fields:

dependence_id
subject_address
support_address
dependence_type
scope
support_handles[]
standing
currentness

load:
  functional
  semantic
  authority
  provenance
  temporal
  coordination

witness_class

corrective_path_ids[]

unresolved[]

No scalar importance score.

# ==================================================
# 6. WITNESS CELL
# ==================================================

Candidate fields:

witness_id
witness_type
observed_object_or_event
observer_address
source_handle
observed_at
standing
scope

witness_type candidates:

LOCAL
EXTERNAL
REDUNDANT
UPSTREAM
DOWNSTREAM_RECONSTRUCTION
POST_HOC

Witness presence does not automatically establish causal interpretation.

# ==================================================
# 7. ADMISSION PIPELINE
# ==================================================

SOURCE
→
RESOLVE ADDRESSES
→
EXTRACT CANDIDATE
→
TYPE RELATION
→
BIND SUPPORT
→
CHECK SCOPE
→
CHECK CURRENTNESS
→
CHECK CLAIM CEILING
→
CHECK DEPENDENCIES
→
CLASSIFY UNRESOLVED
→
REGISTER CANDIDATE
→
PRESSURE
→
ADMIT / DEGRADE / REJECT / SUPERSEDE

The extractor may be generative.

Admission must be challengeable.

# ==================================================
# 8. DETERMINISTIC VS GENERATIVE RESPONSIBILITY
# ==================================================

DETERMINISTIC:

- object address resolution;
- Git frame / blob / path recovery;
- exact source handles;
- schema validation;
- currentness checks where mechanically available;
- standing transitions with explicit rule;
- dependency existence checks;
- source hash / identity checks.

GENERATIVE:

- candidate symbolic relation;
- candidate abstraction;
- candidate idea attribution;
- candidate dependency hypothesis;
- candidate unresolved question.

GENERATIVE OUTPUT
MUST ENTER
AS CANDIDATE,
NOT FACT.

# ==================================================
# 9. SYNTHESIS MODES
# ==================================================

MODE A:
MECHANICAL_DERIVATION

Example:
same path + different blob
→ candidate:
PATH_IDENTITY != CONTENT_IDENTITY

MODE B:
SOURCE_SPAN_EXTRACTION

conversation / document spans
→ candidate symbolic distinction

MODE C:
RELATION_RECONSTRUCTION

multiple admitted artifacts
→ candidate dependence / support chain

MODE D:
WOUND_REPLAY

historical pressure materials
→ candidate surviving distinction

# ==================================================
# 10. FIRST THREE IMPLEMENTATION CELLS
# ==================================================

CELL_A:
PATH_IDENTITY != CONTENT_IDENTITY

Inputs:
exact Git frames
same path
distinct blob identities

Expected:
mechanically supported distinction

CELL_B:
REFERENCE_REACHABILITY != REFERENCE_ADMISSION

Inputs:
exact packet
reference handle
admission state

Expected:
symbolic / evidential distinction

CELL_C:
HISTORICAL_AUTHORITY != CURRENT_AUTHORITY

Inputs:
approval
consumption
current standing

Expected:
typed authority distinction
with AUTHORITY_EFFECT = NONE.

# ==================================================
# 11. DEPENDENCE SYNTHESIS
# ==================================================

A dependence candidate must answer:

SUBJECT:
what continuity-bearing object?

SUPPORT:
what object / relation supplies continuity?

TYPE:
what class of continuity is supplied?

EVIDENCE:
what source supports the dependence?

FAILURE QUESTION:
what changes if support degrades or disappears?

If the engine cannot answer these,
the relation remains generic / unresolved.

# ==================================================
# 12. STAKE PRESSURE MODEL
# ==================================================

Represent provisional pressure tuple:

(A, C, B)

A:
subject

C:
continuity source

B:
candidate disruptor / perturbation

Require:

A DEPENDS_ON C

Then evaluate candidate:

STAKE_A(B | C)

Do not compute one scalar in V0.

Return a six-dimensional potential-loss posture:

functional
semantic
authority
provenance
temporal
coordination

plus:

rupture_likelihood:
UNRESOLVED unless independently supported

realized_loss:
NONE / PARTIAL / TERMINAL / UNRESOLVED

# ==================================================
# 13. WITNESSABILITY
# ==================================================

For each dependence pressure:

can A witness loss locally?

if not:

what external object can witness it?

can the external witness survive the same rupture?

can a post-hoc reconstruction recover enough evidence?

Candidate output:

SELF_WITNESSABLE
EXTERNALLY_WITNESSABLE
POST_HOC_RECONSTRUCTABLE
TERMINAL_UNWITNESSED
UNRESOLVED

# ==================================================
# 14. CORRECTIVE INDEPENDENCE
# ==================================================

For target T and corrector C:

collect dependence sets:

D(T)
D(C)

Pressure intersection:

D(T) ∩ D(C)

A shared support is not automatically dangerous.

But if rupture of shared support S disables both:

TARGET_RECOVERY_FOR_S
=
UNCOVERED

unless another independent corrective route exists.

# ==================================================
# 15. GRAPH / GEOMETRY OUTPUT
# ==================================================

The synthesizer should emit typed relations to Atlas projection.

Projection rules:

MECHANICAL NODE:
existing Atlas object

DISTINCTION NODE:
small typed symbolic object

DEPENDENCE EDGE:
explicit typed relation

WITNESS EDGE:
evidence relation

UNRESOLVED FRONTIER:
relation terminates / remains incomplete

Do not make visual distance itself a semantic relation.

# ==================================================
# 16. RECONSTRUCTION CONTRACT
# ==================================================

Fresh reconstruction input:

- distinction / dependence address;
- local frame;
- source handles;
- current standing.

Fresh seat must recover:

- subject;
- relation;
- support;
- scope;
- standing;
- claim ceiling;
- dependencies;
- witnessability;
- unresolveds.

Success:
operational equivalence,
not identical prose.

# ==================================================
# 17. STORAGE V0
# ==================================================

Prefer appendable source-controlled artifacts first.

Possible V0:

generated / derived registry for projection
+
source-controlled canonical candidate / admitted relation records
+
tests

Do not introduce a heavy graph database until pressure requires it.

# ==================================================
# 18. FIRST TEST MODULES
# ==================================================

test_distinction_schema

test_source_binding

test_relation_typing

test_currentness

test_claim_ceiling

test_dependence_binding

test_load_vector

test_witnessability

test_corrective_independence

test_reconstruction

test_authority_non_minting

# ==================================================
# 19. SECURITY / AUTHORITY RULE
# ==================================================

The synthesizer may represent authority relations.

It may not mint authority.

REGISTERED:
AUTHORIZES(A, X)

does not itself mean:

EXECUTION PERMITTED.

Authority consumption / admission remains in the deterministic authority
membrane.

# ==================================================
# 20. CLAIM CEILING
# ==================================================

This design frame specifies a pressureable technical direction.

It does NOT establish:

- minimal schema;
- safe generative extraction;
- complete dependence inference;
- correct stake measurement;
- complete witness architecture;
- graph database need;
- autonomous relation admission;
- authority correctness.

Those must be earned experimentally.


# ==================================================
# 21. LABBOI IMPLEMENTATION-WARRANT INTEGRATION
# ==================================================

SOURCE:
ATLAS_TYPED_DISTINCTION_ENGINE_V0_IMPLEMENTATION_WARRANT

INTEGRATION_MODE:
APPEND / PRESERVE / DO NOT FLATTEN

RATIONALE:

The Labboi warrant independently converged on the same V0 primitive while
adding several useful operational non-collapses and stop conditions.

This section incorporates only the additional constraints that sharpen
the existing synthesizer frame.

The prior technical sections remain authoritative as historical design
trajectory; this section refines rather than replaces them.

# ==================================================
# 22. ADDITIONAL CORE NON-COLLAPSES
# ==================================================

SERIALIZABLE
!=
SCIENTIFICALLY_RECONSTRUCTABLE

REGISTERED
!=
ADMITTED

VISIBLE_EDGE
!=
SOURCE_SUPPORTED_RELATION

OBJECT_IDENTITY
!=
RELATION_IDENTITY

MULTIPLE_RELATION_FAMILIES
MAY_COEXIST
BETWEEN_THE_SAME_OBJECTS

APPEND_OR_REGISTER
!=
PROMOTE_STANDING

SCHEMA_VALID
!=
SCIENTIFICALLY_ADMISSIBLE

PATH_RESOLVES
!=
CONTENT_IDENTITY_RESOLVES

DEPENDENCY_OMITTED
!=
DEPENDENCY_ABSENT

PROJECTION
!=
SOURCE_OF_TRUTH

DRAWN_PROXIMITY
MUST_NOT
CREATE_RELATION_STANDING

These are now explicit synthesizer constraints.

# ==================================================
# 23. MINIMUM DISTINCTION CELL — IMPLEMENTATION PRESSURE
# ==================================================

The current implementation already carries a richer record than the
minimum candidate cell.

For future schema reduction pressure, the irreducible candidate core is:

distinction_id
subject_address
relation_type
object_address | value
source_handles
constructed_by
standing
currentness
claim_ceiling
dependencies
unresolveds

Optional fields should remain pressure-earned rather than assumed:

source_episode
evaluated_by
admitted_by
supersedes

The current implementation is NOT required to delete already useful
fields merely to match this minimum.

MINIMAL_SCHEMA
!=
REQUIRED_SCHEMA_REWRITE

# ==================================================
# 24. ADDRESS RESOLUTION DISCIPLINE
# ==================================================

Address resolution must preserve distinct questions:

DOES THE SUBJECT ADDRESS RESOLVE?

DOES THE OBJECT / VALUE TARGET RESOLVE?

DO THE SOURCE HANDLES RESOLVE?

DO DECLARED DEPENDENCIES RESOLVE?

Candidate resolution states:

RESOLVED
UNRESOLVED
MISSING

Do not silently repair:

stale paths
renamed objects
missing objects
missing source handles

For path-based objects:

PATH RESOLUTION
DOES NOT ESTABLISH
CONTENT IDENTITY.

This constraint is directly required by Cell D001.

# ==================================================
# 25. STANDING EVALUATION DISCIPLINE
# ==================================================

The standing evaluator does not decide truth.

It determines whether the cell carries sufficient bounded reconstruction
support for its declared standing.

Useful candidate standing vocabulary remains intentionally small:

CANDIDATE
SOURCE_BOUND
PRESSURED
BOUNDED
SUPERSEDED

The currently implemented standing vocabulary does not need to be
renamed merely to match this candidate list.

Standing pressure should verify:

subject correspondence
source support
claim ceiling
dependency status
currentness
forbidden authority promotion

No broad standing ontology is authorized.

# ==================================================
# 26. DEPENDENCY OMISSION LAW
# ==================================================

Fresh reconstruction must distinguish:

NO_DEPENDENCIES_DECLARED

from:

KNOWN_DEPENDENCY_UNRESOLVED

from:

DECLARED_DEPENDENCY_MISSING

Therefore:

DEPENDENCY OMITTED
!=
DEPENDENCY ABSENT

Do not infer global transitive closure.

Do not fill missing dependence from semantic similarity.

# ==================================================
# 27. RECONSTRUCTION RESULT STATES
# ==================================================

A reconstruction pressure may return only a bounded disposition such as:

SAME_BOUNDED_POSTURE

DIFFERENT_BOUNDED_POSTURE

UNRESOLVED

ADMINISTRATION_INVALID

Success remains:

OPERATIONAL POSTURE CONSERVED

not:

IDENTICAL PROSE.

# ==================================================
# 28. VISUAL PROJECTION DISCIPLINE
# ==================================================

The Atlas may render:

A --[RELATION_TYPE]--> B

only when a source-bound registered relation supports that edge.

Rendering may expose:

subject node
typed relation
object / value target
standing
source indicator
dependency indicator
unresolved indicator

But:

VISUAL PROXIMITY
!=
RELATIONAL STANDING

VISUAL EDGE
!=
SOURCE SUPPORT

PROJECTION
!=
SOURCE OF TRUTH

# ==================================================
# 29. IMPLEMENTATION STOP MEMBRANE
# ==================================================

STOP / ESCALATE IF THE WORK ATTEMPTS TO INTRODUCE:

1. a generic ontology;

2. autonomous extractor implementation before extractor pressure;

3. authority activation from symbolic registration;

4. visual geometry as evidence;

5. standing inferred from schema validity;

6. generic dependency closure / graph inference;

7. automatic promotion;

8. semantic similarity replacing exact subject relation;

9. broad ingestion merely to validate the primitive;

10. reconstruction skipped because the registry appears correct.

The first job remains:

prove that a bounded distinction can:

ENTER
→
REMAIN SOURCE_BOUND
→
BE CHALLENGED
→
BE PROJECTED
→
SURVIVE TRANSFORMATION
→
BE RECONSTRUCTED

without becoming more authoritative than the evidence earns.

# ==================================================
# 30. LABBOI CONVERGENCE RECEIPT
# ==================================================

The Labboi warrant independently reinforced:

- minimal distinction-cell structure;
- source-bound admission;
- explicit currentness;
- dependency status;
- projection/source separation;
- reconstruction as the success criterion;
- authority non-minting;
- stop conditions against premature ontology / extractor expansion.

This convergence is informative but is not itself scientific admission.

INDEPENDENT DESIGN CONVERGENCE
!=
EMPIRICAL VALIDATION

The next pressure remains empirical:
fresh-seat reconstruction,
cross-seat conservation,
dependency admission,
and wound replay.
