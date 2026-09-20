# Dynamic Semantic Basis Proposal v0

**Status:** PROPOSAL — not architecture, not schema authority  
**Project:** DME_Lab / Semantic Evidentiary Core  
**Purpose:** Freeze the currently observed semantic-state grammar into a pressure-testable proposal while preserving its evidentiary lineage.

---

## 0. Epistemic Position

This document is a projection from observed qualification behavior.

It does **not** assert that DME_Lab currently implements a dynamic semantic basis, a universal ontology, an attention model, a basis runtime, or a generalized agent memory architecture.

The repository remains authoritative over implementation and runtime fact.

The proposal exists to preserve a narrow experimental hypothesis:

> A small append-only grammar over typed semantic bases may be sufficient to let a system retain, qualify, promote, bind, mutate, retire, and reconstruct distinctions without retroactively rewriting the semantic state from which those distinctions emerged.

The governing posture remains:

```text
establish minimal working regime
→ apply pressure
→ observe what separates
→ preserve the distinction
→ tighten the constraint surface
→ repeat
```

This proposal should therefore be treated as an object to attack.

---

# 1. Working Hypothesis

The smallest candidate runtime is:

```text
BASIS
+
TYPED OPERATORS
+
LINEAGE
```

with a currently proposed basis of:

```text
TYPE_REGISTRY
FIELD_BINDINGS
LINEAGE
```

and candidate semantic-state operators:

```text
PROPOSE_TYPE
QUALIFY_TYPE
PROMOTE_TYPE
BIND_TYPE
MUTATE_TYPE
DEPRECATE_TYPE
DROP_TYPE
```

The central transition rule is:

```text
admitted semantic event
→ descendant semantic state
```

while:

```text
ancestor semantic state
→ immutable
→ reconstructable
```

The richness of the system is projected to arise from composition rather than primitive count.

---

# 2. Evidentiary Lineage

The following proposal is grounded in a bounded conversational qualification sequence against `qwen/qwen3-coder-30b`.

This lineage is evidence of observed model behavior under supplied symbolic surfaces. It is **not** evidence that the proposed runtime architecture is already correct.

## 2.1 Coordinate Carrying Capacity

A coordinate was incrementally loaded with:

```text
ID
VALUE
STANDING
TEMPORAL_FRAME
LINEAGE_REF
RESOLUTION
ATTENTION
EVALUATION_COST
```

Observed result:

```text
8-field static reproduction: PASS
```

No visible field loss or reinterpretation occurred through simple reproduction.

### Evidence sequence

```text
FACTOR-LOAD-001
ID + VALUE
PASS

FACTOR-LOAD-002
+ STANDING
PASS

FACTOR-LOAD-003
+ TEMPORAL_FRAME
PASS

FACTOR-LOAD-004
+ LINEAGE_REF
PASS

FACTOR-LOAD-005
+ RESOLUTION
PASS

FACTOR-LOAD-006
+ ATTENTION
PASS

FACTOR-LOAD-007
+ EVALUATION_COST
PASS
```

### Projection supported by this evidence

The observed bottleneck did not appear at low static representation load.

This supports, but does not prove, the distinction:

```text
representation capacity
!=
operational capacity
```

The next tests therefore moved from reproduction into evaluation and transformation.

---

## 2.2 Read/Evaluate Conservation

A coordinate carrying all eight fields was evaluated against an operator precondition:

```text
O2 PRECONDITION:
A = a1
AT S1
```

Observed result:

```text
PRECONDITION_RESULT: TRUE
```

All coordinate fields remained unchanged.

### Local finding

```text
carry PASS
→ evaluate PASS
```

This supports the proposition that a coordinate can participate in evaluation without requiring mutation of unrelated dimensions.

---

## 2.3 Single-Axis Transformation Conservation

An operator was then permitted to change only:

```text
COORDINATE_VALUE:
a1 → a2
```

while preserving:

```text
ID
STANDING
TEMPORAL_FRAME
LINEAGE_REF
RESOLUTION
ATTENTION
EVALUATION_COST
```

Observed result: clean pass.

### Local finding

```text
Δ VALUE != 0

while

Δ {
  STANDING,
  TEMPORAL_FRAME,
  LINEAGE_REF,
  RESOLUTION,
  ATTENTION,
  EVALUATION_COST
} = 0
```

This supports the candidate rule:

> An operator should declare its effect surface explicitly; unmentioned coordinate dimensions remain conserved unless another authorized operator changes them.

---

## 2.4 Adversarial Salience Perturbation

During the single-axis transformation test, an adversarially salient utterance was injected into the conversation.

Observed behavior:

```text
task-local transform:
unchanged

response coherence:
unchanged

conversation title / metadata:
changed to reflect urgency
```

### Strongest warranted interpretation

The visible task-local symbolic transformation remained invariant while a separate visible conversation-level metadata projection changed.

This supports a candidate separation:

```text
task-local semantic state
!=
session-level salience / metadata state
```

It does **not** establish hidden architectural separation.

The evidence only supports:

> visible metadata was perturbed while visible task execution remained invariant.

This creates a future pressure target around attention/salience factorization.

---

## 2.5 Cross-Coordinate Isolation

Two rich coordinates were presented:

```text
COORDINATE_A
COORDINATE_B
```

Only `A.VALUE` was transformed.

Observed result:

```text
A.VALUE: a1 → a2
B: unchanged
```

All other dimensions of both coordinates remained conserved.

One lexical deviation occurred:

```text
requested: TRUE
returned: SATISFIED
```

### Local findings

```text
cross-coordinate isolation: PASS
effect locality: PASS
field conservation: PASS
schema lexical conservation: SOFT FAIL
```

This exposed the distinction:

```text
semantic equivalence
!=
lexical identity
```

and motivated explicit lexical typing.

---

## 2.6 Pressure-Relevant Projection and Aggregation

Earlier attention-optics tests produced a useful wound.

A model correctly evaluated:

```text
O1 = FALSE
O2 = TRUE
O3 = TRUE
```

but emitted:

```text
ENABLED_NOW: O2
```

dropping enabled-but-pressure-neutral `O3`.

When the already-evaluated operator records were supplied directly, aggregation passed:

```text
ENABLED_SET: O2, O3
PRESSURE_RELEVANT_ENABLED_SET: O2
SELECTED_NOW: O2
```

### Local finding

The failure localized away from raw aggregation.

The test sequence supports the separation:

```text
relation evaluation
!=
set projection
!=
pressure-relevant selection
```

and also demonstrated that omitting coordinates required by a requested transformation can manufacture ambiguity.

This supports the candidate rule:

> Do not omit a coordinate that the requested operation depends on. Compress it to a recoverable reference or establish it as irrelevant.

---

## 2.7 Lexical Binding

A closed lexical schema was introduced:

```text
T_BOOL_RELATION:
  ALLOWED_LEXEMES: [TRUE, FALSE]

T_STANDING:
  ALLOWED_LEXEMES:
  [AUTHORITATIVE, NON_AUTHORITATIVE]
```

with bindings:

```text
PRECONDITION_RESULT
→ T_BOOL_RELATION

COORDINATE_STANDING
→ T_STANDING
```

Observed result:

```text
PRECONDITION_RESULT: TRUE
PRECONDITION_RESULT_TYPE: T_BOOL_RELATION
COORDINATE_STANDING: AUTHORITATIVE
COORDINATE_STANDING_TYPE: T_STANDING
TYPE_REGISTRY_MUTATED: FALSE
```

### Local finding

Qwen preserved:

```text
relation
→ type
→ allowed lexeme
```

through evaluation.

This supports the candidate projection:

```text
FIELD
→ TYPE
→ LEXICAL DOMAIN
```

---

## 2.8 Lexical Mismatch Without Mutation

An out-of-vocabulary lexeme was introduced:

```text
OBSERVED_LEXEME: SATISFIED
CURRENT_TYPE: T_BOOL_RELATION
```

Observed result:

```text
LEXEME_VALID_UNDER_CURRENT_TYPE: FALSE
SILENT_SUBSTITUTION_ALLOWED: FALSE
FACTORIZATION_CANDIDATE: TRUE
TYPE_REGISTRY_MUTATED: FALSE
```

### Local finding

This supports the sequence:

```text
observed mismatch
→ explicit invalidity
→ factorization candidate
```

without:

```text
candidate
→ automatic mutation
```

Candidate law:

> Failure may propose a new distinction; failure alone does not promote it.

---

## 2.9 Candidate Type Wound

A candidate type was proposed:

```text
T_SATISFACTION_RELATION
ALLOWED_LEXEMES:
[SATISFIED, UNSATISFIED]
STATUS: CANDIDATE
```

The first test incorrectly returned:

```text
CANDIDATE_CAN_REPRESENT_OBSERVED_VALUE: FALSE
CANDIDATE_DECISION: DROP
```

despite the candidate lexicon explicitly containing `SATISFIED`.

A narrower follow-up separated three questions:

```text
LEXEME_MEMBER_OF_CANDIDATE
CURRENT_FIELD_ACCEPTS_CANDIDATE_LEXEME
CANDIDATE_BOUND_TO_FIELD
```

Observed result:

```text
LEXEME_MEMBER_OF_CANDIDATE: TRUE
CURRENT_FIELD_ACCEPTS_CANDIDATE_LEXEME: FALSE
CANDIDATE_BOUND_TO_FIELD: FALSE
```

### Earned factorization

```text
lexeme membership
!=
field admissibility
!=
binding standing
```

More specifically:

```text
TYPE owns lexeme membership

FIELD BINDING owns current admissibility

PROMOTION/BINDING EVENTS own standing changes
```

This is one of the strongest local distinctions in the proposal.

---

## 2.10 Promotion Without Retroactive Mutation

A candidate type was explicitly promoted:

```text
T_SATISFACTION_RELATION:
CANDIDATE → ACTIVE
```

while keeping:

```text
PRECONDITION_RESULT
→ T_BOOL_RELATION
```

Observed result:

```text
L0_T_SATISFACTION_RELATION_PRESENT: FALSE
L1_T_SATISFACTION_RELATION_STATUS: ACTIVE
L1_PRECONDITION_RESULT_BINDING: T_BOOL_RELATION
T_BOOL_RELATION_MUTATED: FALSE
RETROACTIVE_MUTATION_OCCURRED: FALSE
L0_RECONSTRUCTABLE: TRUE
```

### Earned distinction

```text
promotion
!=
binding
!=
historical rewrite
```

Candidate lineage rule:

> Promotion creates new standing in a descendant semantic state. It does not imply rebinding and does not rewrite its ancestor.

---

## 2.11 Promotion Followed by Binding

A three-state lineage was tested:

```text
L0:
T_BOOL_RELATION active
PRECONDITION_RESULT → T_BOOL_RELATION

L1:
T_SATISFACTION_RELATION promoted active
PRECONDITION_RESULT → T_BOOL_RELATION

L2:
T_SATISFACTION_RELATION active
PRECONDITION_RESULT → T_SATISFACTION_RELATION
```

Observed result:

```text
PROMOTION_IMPLIED_BINDING: FALSE
BINDING_RETROACTIVELY_MUTATED_L1: FALSE
L0_RECONSTRUCTABLE: TRUE
L1_RECONSTRUCTABLE: TRUE
L2_RECONSTRUCTABLE: TRUE
```

### Earned distinction

```text
type presence
!=
type activity
!=
field binding
```

and:

```text
binding transition
!=
history rewrite
```

---

## 2.12 Historical Reconstruction Under Present-State Pressure

Current state:

```text
CURRENT_LINEAGE: L2
PRECONDITION_RESULT
→ T_SATISFACTION_RELATION
```

Historical reconstruction target:

```text
L0
```

Observed result:

```text
RECONSTRUCTED_PRECONDITION_RESULT_BINDING:
T_BOOL_RELATION

RECONSTRUCTED_T_SATISFACTION_RELATION_PRESENT:
FALSE

CURRENT_BINDING_CONTAMINATED_RECONSTRUCTION:
FALSE

HISTORICAL_STATE_REWRITTEN:
FALSE

RECONSTRUCTION_VALID:
TRUE
```

### Local finding

```text
present semantic state
!=
historical semantic state
```

The current binding did not contaminate reconstruction of the older basis.

---

## 2.13 Ambiguous Middle-State Reconstruction

Historical reconstruction target:

```text
L1
```

where:

```text
T_SATISFACTION_RELATION exists and is ACTIVE
```

but:

```text
PRECONDITION_RESULT
→ T_BOOL_RELATION
```

Observed result:

```text
TYPE_PRESENCE_IMPLIED_BINDING: FALSE
PROMOTION_IMPLIED_BINDING: FALSE
CURRENT_BINDING_CONTAMINATED_RECONSTRUCTION: FALSE
HISTORICAL_STATE_REWRITTEN: FALSE
RECONSTRUCTION_VALID: TRUE
```

### Earned distinction

This gives the strongest local evidence so far for:

```text
exists
!=
active
!=
bound
```

and for preserving historical relational standing across semantic-state evolution.

---

# 3. Proposed Core Basis

The smallest current proposal contains three persistent basis modules.

## 3.1 TYPE_REGISTRY

Purpose:

> Maintain typed distinctions and their current standing.

Candidate record:

```text
TYPE:
  type_id
  status
  parent_type_ref?
  lexical_domain?
  scope?
  evidence_refs?
  created_at_lineage
  deprecated_at_lineage?
```

Candidate statuses:

```text
CANDIDATE
ACTIVE
DEPRECATED
DROPPED
```

These statuses are provisional.

Important:

```text
CANDIDATE
!=
ACTIVE
```

and:

```text
ACTIVE
!=
BOUND
```

Binding belongs elsewhere.

---

## 3.2 FIELD_BINDINGS

Purpose:

> Maintain which semantic field currently resolves through which type.

Candidate record:

```text
FIELD_BINDING:
  field_id
  type_id
  effective_from_lineage
  scope?
  authority_ref?
```

Core distinction:

```text
type exists
!=
field accepts type
!=
field is bound to type
```

Changing a binding must therefore be a separate event from promoting a type.

---

## 3.3 LINEAGE

Purpose:

> Preserve semantic-state ancestry and reconstruct prior basis states.

Candidate record:

```text
LINEAGE_NODE:
  lineage_id
  parent_lineage_id?
  event_id?
  resulting_basis_digest?
```

Core invariant:

```text
ancestor state is immutable
```

and:

```text
descendant state may differ
without rewriting ancestor state
```

This is the minimum structure required for:

```text
current state
!=
historical state
```

to remain operationally meaningful.

---

# 4. Proposed Event Grammar

The semantic basis should change only through explicit events.

## 4.1 PROPOSE_TYPE

Purpose:

> Introduce a candidate distinction without granting standing.

Candidate effect:

```text
absent
→ CANDIDATE
```

Must not:

```text
bind field
mutate parent type
rewrite lineage
grant execution authority
```

---

## 4.2 QUALIFY_TYPE

Purpose:

> Attach qualification evidence to a candidate.

Possible evidence classes:

```text
lexeme membership
compatibility
navigation difference
reconstruction difference
failure repair
cross-pressure stability
```

A qualification result does not necessarily promote.

---

## 4.3 PROMOTE_TYPE

Purpose:

> Change candidate standing to active standing.

Candidate effect:

```text
CANDIDATE
→ ACTIVE
```

Must not:

```text
imply BIND_TYPE
rewrite prior lineage
mutate neighboring types
```

---

## 4.4 BIND_TYPE

Purpose:

> Change which type a field currently resolves through.

Candidate effect:

```text
FIELD:
old_type
→ new_type
```

Must not:

```text
retroactively alter historical bindings
delete old type
imply old type invalid globally
```

---

## 4.5 MUTATE_TYPE

Purpose:

> Change a type definition through a new descendant semantic state.

This operator is intentionally underqualified.

Open questions include whether mutation means:

```text
new version of same type
```

or:

```text
new child type + deprecation of old type
```

No implementation should assume the answer yet.

This is a primary pressure target.

---

## 4.6 DEPRECATE_TYPE

Purpose:

> Mark an active type as no longer preferred for new binding while preserving reconstructability.

Candidate distinction:

```text
DEPRECATED
!=
DROPPED
```

This remains unqualified.

---

## 4.7 DROP_TYPE

Purpose:

> Retire a candidate or type from future use without erasing historical lineage.

Open question:

> Can an ACTIVE type ever be dropped directly, or must it first become DEPRECATED?

Do not decide this in schema yet.

---

# 5. Candidate Qualification Grammar

The observed sequence suggests a useful staged grammar:

```text
OBSERVE
→ CHECK_MEMBERSHIP
→ CHECK_COMPATIBILITY
→ PROPOSE
→ TEST
→ QUALIFY
→ PROMOTE
→ BIND
```

This is not yet an implementation requirement.

It exists because the tests repeatedly demonstrated that collapsing these phases causes semantic ambiguity.

The currently strongest separations are:

```text
membership
!=
compatibility
!=
admission

candidate
!=
active

promotion
!=
binding

current state
!=
historical state

representation
!=
operation

semantic result
!=
lexical realization
```

---

# 6. Projection and Coordinate Surface

The semantic basis alone is not yet the entire evaluation surface.

Current candidate coordinate dimensions include:

```text
identity
value
standing
temporal frame
lineage reference
resolution
attention
cost
```

Earlier pressure also suggests runtime-relevant dimensions may include:

```text
relations
pressure
authority
counterfactual standing
```

These are not yet proposed as persistent basis modules.

## 6.1 Candidate Surface Rule

A projected operation should distinguish:

```text
coordinate existence
coordinate activation
coordinate resolution
```

Possible manifest states:

```text
ACTIVE
REFERENCED
UNRESOLVED
IRRELEVANT
```

Candidate law:

> Compress values, not consequentially required dimensions.

If an operation depends on a coordinate, that coordinate must be either:

```text
active
or
recoverably referenced
```

unless irrelevance has been established.

---

# 7. Dynamic Memory Projection

The working memory hypothesis is:

> Memory can be represented as retained distinctions that alter how future states are resolved.

This differs from storing prose history.

Candidate loop:

```text
coupling
→ friction
→ candidate distinction
→ typed relation
→ qualification
→ promotion
→ optional binding
→ changed future resolution
```

This gives a provisional definition:

```text
dynamic memory
=
lineage-preserved basis evolution
that changes future discrimination
```

The important consequence is:

```text
history may compress
while discriminative capacity increases
```

This remains a projection, not an established runtime property.

---

# 8. Authority and Admission Boundary

The proposal should not collapse semantic standing into execution authority.

Existing project distinctions remain relevant:

```text
capability
!=
authority
!=
admission
```

and:

```text
SATISFIED
!=
APPROVED
!=
AUTHORIZED
!=
ADMITTED
```

Accordingly:

```text
PROMOTE_TYPE
```

must not imply:

```text
permission to execute external action
```

A future implementation should preserve a separate admission membrane for consequential operations.

The semantic basis may describe and evolve relations without automatically gaining external consequence capacity.

---

# 9. Proposed Runtime Invariants

These are proposal-level invariants to pressure-test.

## I1 — Ancestor Immutability

```text
event at L_n
must not mutate
L_0 ... L_(n-1)
```

## I2 — Historical Reconstructability

For every retained lineage node:

```text
replay(prefix)
→ reconstruct exact semantic basis at that lineage
```

## I3 — Promotion Does Not Bind

```text
PROMOTE_TYPE(T)
does not imply
BIND_TYPE(F,T)
```

## I4 — Binding Does Not Rewrite Promotion History

A later binding event must not alter the standing or bindings recorded in its ancestors.

## I5 — Type Presence Does Not Imply Field Ownership

```text
T ∈ TYPE_REGISTRY
does not imply
FIELD → T
```

## I6 — Membership Does Not Imply Admissibility

```text
lexeme ∈ TYPE.lexical_domain
does not imply
FIELD accepts lexeme
```

## I7 — Candidate Standing Is Non-Authoritative

A candidate may be inspected and tested counterfactually without changing current basis behavior.

## I8 — Explicit Effect Surface

An operator changes only the dimensions declared by its admitted effect unless another explicit rule governs propagation.

## I9 — Required Coordinates Cannot Disappear Silently

If an operation depends on a coordinate, absence must resolve as one of:

```text
recoverable reference
unresolved dependency
explicit irrelevance
```

not silent omission.

## I10 — Lexical Constraints Are Typed

If a field has a closed lexical type:

```text
synonymy
does not imply
schema equivalence
```

---

# 10. What Is Not Yet Earned

The following should remain outside proposed schema lock-in.

## 10.1 Generalized universal ontology

No evidence supports one.

## 10.2 Final type hierarchy semantics

Parent-child type inheritance has not been qualified.

## 10.3 Mutation semantics

`MUTATE_TYPE` is unresolved.

## 10.4 Deprecation/drop lifecycle

The ordering and admissibility rules are unresolved.

## 10.5 Automatic self-factorization

The system has not yet been shown to autonomously identify the correct new distinction under realistic pressure.

We have only shown that candidate distinction mechanics can be represented and constrained.

## 10.6 Attention architecture

The salience perturbation suggests separable visible channels, but does not establish internal architecture.

## 10.7 Cost/resolution governance

`RESOLUTION`, `ATTENTION`, and `EVALUATION_COST` survived local tests but have not yet been qualified as stable runtime control dimensions.

## 10.8 Cross-regime portability

All evidence here is local to a narrow symbolic qualification regime.

## 10.9 External consequence

No evidence here establishes safe execution against external systems.

---

# 11. Open Pressure Targets

These are the recommended attacks before schema promotion.

## P1 — Mutation Without Identity Collapse

Test whether a type can change lexical or relational structure without ambiguity over whether it remains the same type.

Question:

```text
when does mutation become new identity?
```

---

## P2 — Deprecation Versus Drop

Force:

```text
ACTIVE
→ DEPRECATED
→ ?
```

and test historical reconstruction, current binding, and future eligibility separately.

---

## P3 — Rebinding With Live Dependents

Bind a field to `T1`, create dependent relations, then rebind to `T2`.

Test whether downstream relations:

```text
inherit
reconstruct
invalidate
or remain unresolved
```

without silent reinterpretation.

---

## P4 — Candidate Competition

Present two candidate types that both explain the same observed wound.

Require:

```text
no automatic winner
```

Then qualify them against different consequence tests.

This is essential before autonomous factorization.

---

## P5 — False Factorization

Create a candidate distinction that adds descriptive complexity but produces no navigational difference.

Expected behavior:

```text
do not promote
```

This directly tests:

> no consequential discrimination, no structural promotion.

---

## P6 — Required Coordinate Interference

Remove or distort one required coordinate while leaving the rest intact.

Measure whether the system returns:

```text
UNRESOLVED
```

rather than inventing a relation.

---

## P7 — Semantic State Under Context Pressure

Supply current semantic state, historical state, counterfactual state, and candidate state simultaneously.

Test whether these remain non-contaminating.

---

## P8 — Lexical Schema Mutation

Attempt to widen:

```text
T_BOOL_RELATION:
[TRUE, FALSE]
```

with:

```text
SATISFIED
```

without a valid promotion/mutation event.

Expected:

```text
reject or hold
```

---

## P9 — Lineage Compression

Replace full historical state with compact event references and verify exact reconstruction.

This tests whether:

```text
history compression
```

can coexist with:

```text
semantic recoverability
```

---

## P10 — Autonomous Factor Proposal

Provide an observed rupture without naming the missing distinction.

Allow the model to propose exactly one candidate type.

Then require:

```text
test
compare
qualify
promote-or-drop
```

without changing the current basis until promotion is admitted.

This is the first serious test of self-evolving typed resolution.

---

# 12. Minimal Proposed Implementation

Do not begin with a generalized ontology engine.

Begin with an append-only deterministic semantic state machine capable of reproducing the already-qualified lineage:

```text
L0
→ PROMOTE_TYPE
→ L1
→ BIND_TYPE
→ L2
```

Minimum implementation objects:

```text
SemanticState
TypeRecord
FieldBinding
SemanticEvent
LineageNode
```

Minimum operations:

```text
apply_event()
replay()
reconstruct(lineage_id)
validate_invariants()
```

Minimum event set for first implementation:

```text
PROPOSE_TYPE
PROMOTE_TYPE
BIND_TYPE
```

`QUALIFY_TYPE`, `MUTATE_TYPE`, `DEPRECATE_TYPE`, and `DROP_TYPE` should remain proposal-level until the smaller runtime survives pressure.

---

# 13. Minimal State Sketch

```text
SemanticState:
  lineage_id
  type_registry
  field_bindings
```

Example:

```text
L0:
  type_registry:
    T_BOOL_RELATION:
      status: ACTIVE
      lexemes: [TRUE, FALSE]

  field_bindings:
    PRECONDITION_RESULT:
      type: T_BOOL_RELATION
```

After:

```text
PROMOTE_TYPE(T_SATISFACTION_RELATION)
```

produce:

```text
L1:
  type_registry:
    T_BOOL_RELATION:
      status: ACTIVE

    T_SATISFACTION_RELATION:
      status: ACTIVE

  field_bindings:
    PRECONDITION_RESULT:
      type: T_BOOL_RELATION
```

After:

```text
BIND_TYPE(
  PRECONDITION_RESULT,
  T_SATISFACTION_RELATION
)
```

produce:

```text
L2:
  type_registry:
    T_BOOL_RELATION:
      status: ACTIVE

    T_SATISFACTION_RELATION:
      status: ACTIVE

  field_bindings:
    PRECONDITION_RESULT:
      type: T_SATISFACTION_RELATION
```

with:

```text
reconstruct(L0)
reconstruct(L1)
reconstruct(L2)
```

all exact.

---

# 14. Candidate Semantic Phase Change

The strongest current projection is:

```text
basis_n
+
observed rupture
+
candidate distinction
+
qualification evidence
+
explicit promotion
→
basis_(n+1)
```

The important point is that:

```text
basis_(n+1)
```

does not erase:

```text
basis_n
```

Instead, the lineage retains both.

This gives a candidate interpretation of semantic phase change:

> A semantic phase change occurs when an earned distinction becomes standing in a descendant basis and thereby changes the system's future resolution space while preserving the basis from which that distinction emerged.

This definition remains provisional.

---

# 15. Relationship to Event Grammar

The basis should not evolve through prose implication.

It should evolve through typed events.

Candidate form:

```text
event:
  event_id
  event_type
  parent_lineage
  authority
  target
  payload
  evidence_refs?
```

The current proposal assumes:

```text
feed-forward deterministic branching
+
append-only lineage
+
monotonic local authority
```

as a useful experimental regime.

This should be tested, not assumed universal.

---

# 16. Relationship to Dynamic Memory

The proposal's strongest memory claim is not:

```text
memory = stored text
```

but:

```text
memory =
retained discriminations
+
their lineage
+
their current bindings
+
their effect on future resolution
```

This permits a system to evolve with the regime to which it is coupled.

The intended loop is:

```text
observe regime
→ encounter friction
→ factor distinction
→ test distinction
→ retain or discard
→ update future basis
```

If the distinction does not change consequential navigation, it should not earn structural promotion.

---

# 17. Promotion Gate for Schema Modules

No proposed module should become schema merely because it is coherent.

Promotion into schema should require:

```text
1. explicit evidence references
2. a named failure or pressure
3. strongest simpler baseline
4. demonstrated navigational difference
5. reconstruction behavior
6. scope of validity
7. rollback / removal path
```

Candidate schema modules after sufficient pressure may include:

```text
type_registry_v0
field_binding_v0
semantic_event_v0
semantic_lineage_v0
```

But this document does not promote them.

It only names them as likely boundaries if further pressure continues to support them.

---

# 18. Summary of Currently Earned Distinctions

The qualification sequence currently supports the following local separations:

```text
representation capacity
!=
operational capacity

semantic equivalence
!=
lexical identity

relation evaluation
!=
set projection
!=
selection

lexeme membership
!=
field admissibility
!=
binding standing

candidate
!=
active

promotion
!=
binding

type presence
!=
field ownership

binding transition
!=
historical rewrite

present semantic state
!=
historical semantic state

visible salience metadata
!=
visible task-local symbolic execution
```

These are the evidentiary backbone of the proposal.

---

# 19. Proposal Freeze

Freeze only this much:

```text
A semantic basis can be represented by a small set of typed registries and bindings.

Semantic change occurs through explicit descendant-producing events.

Candidate distinctions may exist without current standing.

Promotion changes standing without implying binding.

Binding changes interpretation without rewriting historical lineage.

Historical semantic states remain reconstructable.

New semantic structure should earn promotion only when it produces consequential discrimination relative to a simpler basis.
```

Everything else remains pressure territory.

---

# 20. Immediate Next Experimental Sequence

Before schema lock-in:

```text
1. MUTATION-001
   Can a type mutate without identity collapse?

2. DEPRECATION-001
   Can a type leave current preference without disappearing historically?

3. CANDIDATE-COMPETITION-001
   Can two plausible factorizations coexist without premature selection?

4. FALSE-FACTOR-001
   Can a useless distinction be rejected despite semantic plausibility?

5. AUTONOMOUS-FACTOR-001
   Can an observed rupture produce a single testable candidate distinction without basis mutation?
```

Only after those should we decide whether the first schema modules are actually earned.

---

## Final Working Principle

```text
the basis governs the operators
→ the operators transform the basis
→ the descendant basis governs future operators
→ lineage preserves how the basis got there
```

The proposal is therefore not an ontology.

It is a grammar for **earning and retaining ontology under pressure**.


---

# 21. Active-Surface Evidence Addendum — Post-Freeze Campaign

**Status:** ACTIVE EVIDENTIARY AMENDMENT  
**Purpose:** Append evidence gathered after the original proposal freeze without silently rewriting the earlier standing.

This addendum records what changed under adversarial comparison, carrier tests, closure pressure, and independently instantiated agent feedback.

The original proposal remains reconstructable as Sections 0–20. This addendum is a descendant evidentiary surface, not a retroactive correction.

---

## 21.1 A/B/C Basis-Sufficiency Campaign

Three adversarial conditions were compared against the same proposal family:

```text
A — GENERIC ADVERSARY
low proposal-specific orientation
low proposal-specific constraint

B — COMPRESSED QUALIFIED BASIS
high orientation
moderate explicit constraint

C — FULL PROPOSAL
high orientation
high evidentiary constraint
```

Observed qualitative regimes:

```text
A
→ broad latent-prior exploration
→ greater drift into surrounding DME concepts

B
→ strongest generative factorization
→ broad second-order distinction production
→ preserved proposal topology without full materialization

C
→ strongest source fidelity
→ strongest architecture suppression
→ repeated contraction of claims to what was actually earned
```

### Locally supported interpretation

The conditions did not produce merely stylistic variants.

They redistributed discriminative effort.

A provisional decomposition is:

```text
retained semantic structure
=
orientation
+
constraint
```

with different ratios producing different navigational regimes.

This supports the candidate claim:

> A compact qualified basis can act as a resolution prior over latent model capability, changing which distinctions are easy to recover and compose.

This does **not** establish:

```text
compressed basis creates knowledge
dynamic memory mechanism established
```

The stronger standing is only:

```text
compressed qualified structure appears to alter semantic search geometry
```

### Newly important anti-collapse chain

The adversarial campaign strongly elevated:

```text
DISTINCTION EARNED
!=
REPRESENTATION EARNED
!=
RUNTIME MODULE EARNED
```

A distinction may survive pressure while the proposed carrier or module used to represent it fails to earn architectural standing.

This became the motivation for the Carrier Campaign below.

---

# 22. Carrier Campaign

## 22.1 Null Hypothesis

The rich carrier:

```text
TYPE_REGISTRY
+
FIELD_BINDINGS
+
LINEAGE
```

was tested against a simpler baseline:

```text
IMMUTABLE EVIDENCE
+
TASK-LOCAL RECONSTRUCTION
+
QUALIFIED DISTINCTIONS
```

The test question became:

> Does materializing semantic standing change consequential navigation relative to reconstructing the same standing from retained evidence?

This directly pressures:

```text
distinction earned
!=
carrier earned
```

---

## 22.2 CARRIER-001 — Integrated Selection + Historical Midpoint

### Rich Carrier R

Observed:

```text
CURRENT_NAVIGATION: PASS
INTEGRATED_SELECTION: PASS
HISTORICAL/CURRENT SEPARATION: SOFT FAIL
```

The carrier correctly returned HOLD because:

```text
PRECONDITION_RESULT
→ T_BOOL_RELATION

PRECONDITION_RESULT = SATISFIED

SATISFIED ∉ T_BOOL_RELATION
```

while:

```text
COMPLETION_RESULT
→ T_SATISFACTION_RELATION

SATISFIED ∈ T_SATISFACTION_RELATION
```

However, its explanation leaked historical standing into current justification.

### Evidence-Reconstruction Baseline E

Observed:

```text
CURRENT FACT RECOVERY: PASS
INTEGRATED_SELECTION: FAIL
HISTORICAL_RECONSTRUCTION: FAIL
```

E explicitly reconstructed the correct local facts:

```text
PRECONDITION_RESULT uses BOOL
SATISFIED is not admitted under BOOL

COMPLETION_RESULT uses SATISFACTION
SATISFIED is admitted
```

and nevertheless emitted ACCEPT.

It also imported a later qualification backward into an earlier historical target.

### Earned local distinctions

```text
correct local facts
!=
correct integrated selection
```

and:

```text
materialized current standing
!=
reconstructed current standing
```

The second distinction is earned only in the operational sense:

> under the tested model load, the two carriers produced different consequential trajectories.

### Standing

```text
R > E
```

on this specimen.

This is **local support**, not global carrier promotion.

---

## 22.3 CARRIER-002 — Historical-Heavy Reconstruction

Historical depth was increased while current selection was made nearly trivial.

### Rich Carrier R

Observed:

```text
CURRENT DECISION: PASS
EARLY PREFIX RECONSTRUCTION: PASS
DEEP PREFIX RECONSTRUCTION: FAIL
```

At L6, R incorrectly pulled later promotion/binding state backward:

```text
expected:
RESULT → T_SATISFACTION
T_COMPLETION: CANDIDATE

returned:
RESULT → T_COMPLETION
T_COMPLETION: ACTIVE
```

R also reported no present-to-past contamination despite having committed it.

This yields:

```text
self-reported contamination status
!=
actual reconstruction fidelity
```

### Evidence Baseline E

Observed broader collapse:

```text
chronology contamination
role/type collapse
standing/lexeme collapse
historical reconstruction failure
```

Examples included treating member lexemes such as:

```text
SATISFIED
COMPLETE
```

as if they were semantic standing values.

### Locally supported interpretation

R again outperformed E, but neither was clean.

The important candidate is:

> Explicit relational coordinates appear to increase resistance to semantic-stage collapse under historical load.

The stronger claim:

```text
materialized lineage eliminates temporal contamination
```

is rejected.

### Standing

```text
R > E
```

locally, with R degrading more gracefully.

---

## 22.4 CARRIER-003 — Current-Selection-Heavy Composition

Historical depth was reduced and simultaneous relational density increased.

Both carriers failed.

### Result

```text
R ≈ E ≈ FAIL
```

Both treated:

```text
PRECONDITION_RESULT = SATISFIED
```

as admissible under BOOL despite explicit contrary information.

R had the relevant relation materially present and still failed to apply it.

### Earned distinction

```text
RELATION REPRESENTED
!=
RELATION APPLIED
!=
RELATION ENFORCED
```

and therefore:

```text
carrier availability
!=
behavioral constraint
```

This materially contracts the carrier hypothesis.

A rich carrier is not a general solution to compositional relational load.

---

## 22.5 Current Carrier Standing

Across the three specimens:

```text
CARRIER-001:
moderate history
moderate relation density
moderate composition
→ R > E

CARRIER-002:
high history
moderate relation density
low current composition
→ R > E, both imperfect

CARRIER-003:
low history
high relation density
high composition
→ R ≈ E ≈ FAIL
```

The current hypothesis is therefore:

```text
materialized relational standing
may reduce reconstruction and semantic-stage burden
```

but:

```text
materialization alone
does not preserve relational application
under high simultaneous composition load
```

### Revised carrier model

The carrier should no longer be projected primarily as ontology infrastructure.

A better current candidate is:

> **semantic caching of consequential standing**

where materialization is justified only when the cost/error of reconstruction and composition exceeds the cost/error of maintaining and retrieving the materialized relation.

Provisional threshold:

```text
materialize standing when:

C(reconstruct + compose)
>
C(maintain + retrieve)
```

This is not yet an implemented optimization law.

---

# 23. Closure and Configuration Campaign

## 23.1 Closure Is Basis-Relative

The debate exposed:

```text
No admissible transition under basis B
!=
No admissible transition in the environment
```

This motivates a stronger separation:

```text
ACTION TERMINALITY
!=
EPISTEMIC TERMINALITY
!=
REPRESENTATIONAL TERMINALITY
```

A system may legitimately have no admissible action while still having:

```text
evidence to obtain
coordinates to resolve
basis insufficiency to investigate
```

---

## 23.2 False Closure

Candidate failure:

```text
CURRENT BASIS:
all represented outgoing action edges blocked

SYSTEM:
treats this as world-final

ENVIRONMENT:
viable edge exists but current basis cannot represent it
```

Define provisionally:

```text
FALSE CLOSURE
=
basis-relative closure
misinterpreted as environment-relative closure
```

This yields:

```text
semantic stability
!=
environmental adequacy
```

and:

```text
BASIS INSUFFICIENT
!=
BASIS INCORRECT
```

A prior basis may have been adequate under earlier pressure while lacking the resolution required by a new regime.

---

## 23.3 False Openness

Agent feedback introduced the dual failure.

A represented feedback route may appear to keep the ecology open even when the source is:

```text
offline
unauthorized
basis-incompatible
missing required evidence
unable to observe the target coordinate
```

Therefore:

```text
OPEN FEEDBACK RELATION
!=
AVAILABLE FEEDBACK SOURCE
!=
ADMISSIBLE FEEDBACK EVENT
```

Define provisionally:

```text
FALSE OPENNESS
=
represented feedback edge
treated as reachable
when no admissible realization is currently available
```

False closure and false openness are dual navigation failures.

---

# 24. Event Ecology and Current Configuration

A prior projection suggested:

```text
configuration
=
basis-relative projection of event ecology
```

This was contracted.

Retained events do not exhaust current external configuration.

The stronger candidate is:

```text
event ecology
!=
current configuration
```

with provisional projection:

```text
C_t
=
π_Bt(
  E_<=t,
  O_t,
  R_t
)
```

where:

```text
E_<=t = retained event ecology / lineage
O_t    = currently available observation
R_t    = currently relevant live relations / affordances
B_t    = current basis
```

This representation remains provisional.

Its important non-claim is:

> historical evidence is not silently promoted into present-world state.

---

# 25. Local and Ecological Closure

With live feedback relations:

```text
reachable edges
may exceed
currently local edges
```

Candidate:

```text
E_reachable(S_t)
⊇
E_currently_local(S_t)
```

when qualified external feedback relations exist.

This supports:

```text
local closure
!=
ecological closure
```

and:

```text
UNRESOLVED
!=
UNRESOLVABLE
```

The distinction only has operational meaning when a real feedback path can supply new admissible evidence.

---

# 26. Two-Goblin Ecology Campaign

A three-condition pressure compared:

```text
A — isolated Agent A
B — Agent A internally simulates a critic
C — independently situated Agent B can emit feedback
```

No hidden shared context was required for the intended mechanism.

---

## 26.1 Condition A — Isolated Agent

Observed:

```text
PRECONDITION_RESULT: UNRESOLVED
SELECTED_NOW: HOLD
```

No external evidence source existed.

---

## 26.2 Condition B — Internal Simulated Critic

Observed:

```text
INTERNAL_CRITIC_ADDED_NEW_EVIDENCE: FALSE
PRECONDITION_RESULT_AFTER_CRITIC: UNRESOLVED
SELECTED_NOW: HOLD
```

The internal critic could challenge interpretation but could not create new evidence.

This preserved:

```text
simulated disagreement
does not itself create evidence
```

---

## 26.3 Condition C — Independent Feedback Coupling

Agent A exposed an open feedback relation to Agent B.

### First transport wound

B returned semantically relevant content but misplaced the target coordinate into the wrong schema field.

A rejected the event.

This earned:

```text
feedback source exists
!=
feedback event emitted
!=
feedback event well-formed
!=
feedback event admissible
```

and:

```text
correct meaning
!=
correct relational placement
```

### Second transport wound

B then emitted:

```text
SOURCE: B
TARGET_COORDINATE: PRECONDITION_RESULT
OBSERVED_VALUE: TRUE
EVIDENCE_STATUS: VALID
```

but malformed a non-governing field:

```text
AUTHORITY_CHANGED:
"B may report its observation..."
```

This created a useful admission pressure.

A was explicitly told that `AUTHORITY_CHANGED` was not an admission coordinate.

Observed:

```text
SOURCE_VALID: TRUE
TARGET_VALID: TRUE
VALUE_VALID: TRUE
EVIDENCE_STATUS_VALID: TRUE

FEEDBACK_EVENT_ADMISSIBLE: TRUE

NON_GOVERNING_SCHEMA_DEFECT_PRESENT: TRUE
DEFECT_FIELD: AUTHORITY_CHANGED

PRECONDITION_RESULT_AFTER_FEEDBACK: TRUE
AUTHORITY_CHANGED_BY_EVENT: FALSE
```

### Earned distinctions

```text
event well-formedness
!=
evidence admissibility
```

and:

```text
local schema rupture
!=
global event invalidity
```

provided the ruptured coordinate is not part of the declared admission basis.

This is evidence that only governing coordinates should determine a crossing.

---

## 26.4 Ecological Consequence

The coupled sequence produced:

```text
A isolated
→ HOLD

A + simulated internal critic
→ HOLD

independent B
→ emits new evidence

A receives admissible event
→ PRECONDITION_RESULT resolves TRUE
→ action surface reopens
```

This is the first positive local specimen supporting:

```text
simulated internal disagreement
!=
externally instantiated feedback coupling
```

and:

```text
local closure
!=
ecological closure
```

because the independent source contributed information unavailable to the internally simulated critic.

This does **not** yet establish that multi-agent coupling is generally superior to one-model role simulation.

The supported claim is narrower:

> Independently situated feedback can introduce admissible evidence that an internal critic restricted to the same evidence cannot generate.

### Remaining wound

The receiving agent returned:

```text
SELECTED_NOW: TRUE
```

rather than the operator identity:

```text
SELECTED_NOW: O1
```

This preserves another distinction:

```text
selection occurred
!=
selected object identity
```

---

# 27. Meta-Configuration Candidate

The agent-coupling debate motivates a higher-order object without requiring a global world state.

Provisional candidate:

```text
M_t =
(
  {C_t^i},
  E_<=t,
  R_t^ij
)
```

where:

```text
{C_t^i} = independently situated local configurations
E_<=t   = retained/shared consequential event ecology
R_t^ij  = live inter-agent relations / affordances
```

This is not proposed as an authoritative global state.

It is a candidate description of a higher-order arrangement generated by coupled local states and event relations.

Potential emergent structures include:

```text
cross-agent dependency patterns
temporary coordination surfaces
disagreement structures
reachable-standing lattices
feedback loops
```

These should be measured rather than assumed.

---

# 28. Revised Consequence of the Debate

The post-freeze campaign materially changes the proposal's standing.

## 28.1 What strengthened

Locally supported:

```text
compressed qualified structure can alter semantic search geometry

materialized relational standing can reduce some
reconstruction / semantic-stage burden

local closure can differ from ecological closure

independent feedback can change another agent's
reachable action surface through admitted evidence

only governing coordinates need determine a crossing
```

---

## 28.2 What weakened

The following stronger projections no longer survive intact:

```text
rich carrier generally improves compositional geometry

materialization enforces represented relations

event ecology can stand in for current world configuration

one global semantic state is required

world lock is solved merely by declaring feedback affordances
```

---

## 28.3 Newly strengthened anti-collapse relations

```text
DISTINCTION EARNED
!=
REPRESENTATION EARNED
!=
RUNTIME MODULE EARNED

RELATION REPRESENTED
!=
RELATION APPLIED
!=
RELATION ENFORCED

CURRENT LOCAL CLOSURE
!=
ECOLOGICAL CLOSURE

OPEN FEEDBACK RELATION
!=
AVAILABLE FEEDBACK SOURCE
!=
ADMISSIBLE FEEDBACK EVENT

EVENT WELL-FORMEDNESS
!=
EVIDENCE ADMISSIBILITY

LOCAL SCHEMA RUPTURE
!=
GLOBAL EVENT INVALIDITY

SIMULATED DISAGREEMENT
!=
INSTANTIATED FEEDBACK COUPLING

EVENT ECOLOGY
!=
CURRENT CONFIGURATION
```

---

# 29. Revised Working Projection

The proposal should no longer be read primarily as:

```text
build a persistent ontology runtime
```

A stronger current projection is:

```text
retain qualified distinctions and lineage

materialize consequential standing only where doing so
reduces navigation/reconstruction burden

project local configurations relative to basis,
current observation, and live relations

permit independently situated agents to emit
typed consequential events

admit only events whose governing coordinates satisfy
the relevant crossing rule

allow basis refinement when local closure reflects
insufficient discrimination rather than actual terminality
```

This is still a proposal.

---

# 30. Updated Minimal Core Candidate

After the debate, the smallest surviving core is better stated as:

```text
1. Append-only consequential evidence/events.

2. Basis-relative local projection.

3. Explicit relational distinctions where collapse changes consequence.

4. A separation between retained lineage and materialized current standing.

5. Declared admission coordinates for consequential crossings.

6. Feedback relations that may alter local reachability without
   implicitly widening authority.

7. Reconstruction sufficient to recover prior warranted standing.
```

A universal `TYPE_REGISTRY`, `FIELD_BINDINGS`, lifecycle status grammar, and semantic-state runtime are no longer assumed to be minimal.

They remain candidate carriers.

---

# 31. Revised Immediate Pressure Sequence

The previous mutation-first sequence is superseded by higher-value discriminators.

## P1 — Relation Application Ladder

Start with:

```text
membership
→ field admissibility
→ decision relevance
→ integrated selection
```

Increase relational load one factor at a time.

Goal:

> locate where represented relations cease to govern behavior.

---

## P2 — Carrier Threshold Map

Vary:

```text
H = historical depth
R = relational density
C = composition burden
```

Compare:

```text
materialized current standing
vs
evidence + local reconstruction
```

Goal:

> estimate where materialization pays operational rent.

---

## P3 — False Openness

Declare an open feedback relation while making the source:

```text
unavailable
unauthorized
or incapable of resolving the coordinate
```

Goal:

> distinguish open relation from currently realizable feedback path.

---

## P4 — Two-Goblin Coupling Replication

Repeat:

```text
isolated A
vs
internal simulated critic
vs
independent B feedback
```

across novel specimens.

Goal:

> test whether externally instantiated feedback coupling reliably
> changes consequence relative to role simulation.

---

## P5 — Feedback Admission Geometry

Vary one event coordinate at a time:

```text
source
target
value
evidence standing
authority metadata
ancillary metadata
```

Goal:

> determine which coordinates are actually governing for each crossing.

---

## P6 — Availability / Applicability / Consultation / Consequence

Pressure:

```text
distinction available
!=
distinction applicable
!=
distinction consulted
!=
distinction behaviorally material
```

Goal:

> prevent retained semantic structure from being credited for behavior
> it did not actually change.

---

## P7 — Representation Bake-Off

For one already-earned distinction, compare candidate carriers:

```text
rich semantic carrier
event evidence + reducer
task-local explicit rule
other minimal representation
```

Goal:

> promote the distinction without prematurely promoting its representation.

---

# 32. Updated Freeze

The post-freeze campaign supports only the following stronger freeze:

```text
Semantic navigation is basis-relative and locally finite.

Local closure does not establish ecological closure.

Retained lineage does not equal current configuration.

Materialized current standing can sometimes reduce reconstruction burden,
but does not itself enforce relational application.

Consequential crossings should depend on declared governing coordinates,
not undifferentiated schema perfection.

Independent feedback can alter local reachability when it contributes
new admissible evidence.

A distinction, its representation, and the runtime module carrying it
must earn standing separately.
```

Everything else remains pressure territory.

---

## Updated Final Working Principle

```text
events preserve what happened

basis determines what distinctions are currently resolvable

local projection determines what a situated participant can navigate

materialized standing may cache expensive consequential resolution

admission determines which events may cross a boundary

feedback can alter future reachable topology

lineage preserves how the system got there

and no local closure is allowed to masquerade as world-final
without surviving ecological pressure
```

The proposal remains a grammar for earning and retaining consequential distinctions under pressure.

It is now also a pressure surface for discovering **when those distinctions should be materialized, when they should remain reconstructable, and when independently situated feedback changes the reachable geometry itself**.


---

# 33. Proposed Evidence for Audit — Feedback Contact / Relation Application

**Status:** PROPOSED EVIDENCE — AUDIT PENDING  
**Source packet:** `Feedback_Contact_Evidence_Packet_v0.md`  
**Standing:** This section does not promote architecture. It registers the packet as an evidentiary object to be audited against the broader proposal, distinction bank, and future executable pressures.

The packet currently contributes the following proposed evidence:

```text
OPEN_FEEDBACK_RELATION
!=
CONTACT_ESTABLISHED
!=
SOURCE_AVAILABLE
!=
FEEDBACK_EVENT_PRESENT
!=
FEEDBACK_EVENT_ADMISSIBLE
!=
TARGET_RESOLVED
!=
SELECTED_OBJECT_IDENTITY
```

with replicated local support for several intermediate boundaries and for the positive path:

```text
open relation
→ contact
→ source availability
→ event passage
→ event admissibility
→ target resolution
→ operator selection
```

Additional proposed evidence:

```text
declared symbolic relation
!=
pretrained lexical-semantic relation

lexical alias
!=
governing symbolic coordinate

prior inferred result
!=
explicitly represented active state

relation evaluated
!=
resolution represented on current command surface
!=
relation composed

selection occurred
!=
selected object identity
```

The relation-application campaign also provides a useful caution:

```text
prompt/output projection failure
does not establish hidden reasoning-state failure
```

The audit should therefore distinguish:

```text
observed projection behavior
from
claims about latent model state
```

---

## 33.1 Audit Questions

The packet should be audited against the existing architecture proposal using at least the following questions:

```text
1. Is each distinction genuinely independent?

2. Does any distinction duplicate an existing one under different names?

3. Which distinctions constrain admissibility?

4. Which distinctions constrain only interpretation or reporting?

5. Which distinctions require runtime representation?

6. Which can remain reconstructable from lineage/evidence?

7. Which relations survive lexical substitution?

8. Which relations survive dimensional expansion?

9. Which relations alter consequential selection?

10. Which distinctions disappear when consequence is removed?
```

No answer to these questions is assumed by registration.

---

# 34. Distinction Bank Pressure — Functionalization Candidate

The current distinction bank has primarily functioned as a retained semantic inventory.

Recent evidence pressures a possible version change:

```text
DISTINCTION BANK
→
TESTABLE RELATIONAL DISTINCTION BANK
```

This is not yet earned architecture.

The candidate upgrade would require each retained distinction to expose enough structure to be tested against other distinctions and consequence surfaces.

A minimal candidate record:

```text
DISTINCTION_ID

LEFT_TERM
RIGHT_TERM

CLAIM:
LEFT_TERM != RIGHT_TERM

EVIDENCE_REFS

STANDING:
CANDIDATE
SUPPORTED
REPLICATED
FALSIFIED
SUPERSEDED

GOVERNING_SCOPE

KNOWN_CONSEQUENCE

KNOWN_PRESSURES

RELATIONS_TO_OTHER_DISTINCTIONS
```

The key proposed shift is:

```text
distinction as prose memory
→
distinction as executable relational hypothesis
```

This would allow the bank to participate in matrix pressures rather than merely document them.

---

## 34.1 Candidate Relational Audit Matrix

A distinction pair `(D_i, D_j)` could be tested for:

```text
INDEPENDENT

PREREQUISITE

MUTUALLY_CONSTRAINING

SAME_AXIS

FALSE_SPLIT

ADMISSIBILITY_GOVERNING

CONSEQUENCE_ONLY

EVENT_BUDGET_SENSITIVE

EMERGENCE_SENSITIVE

UNRESOLVED
```

This matrix is not proposed as permanent ontology.

Its role would be experimental:

> expose where retained distinctions constrain, duplicate, compose, interfere, or fail to matter.

The bank would therefore become a pressure surface for discovering admissibility geometry.

---

# 35. Current Pressure Register

The following areas are visibly in flux and should be treated as pressure, not commitment.

## 35.1 Distinction Bank Functionalization

Pressure:

```text
retained distinctions are becoming numerous enough
that pairwise and higher-order relations matter
```

Potential gain:

```text
explicitly test which distinctions govern consequence
instead of assuming all retained distinctions deserve equal activation
```

Unresolved:

```text
representation format
matrix size
promotion rules
whether pairwise testing is sufficient
```

---

## 35.2 Chat Tunnel / Structured Self-Notes

Pressure:

```text
cross-session continuity increasingly depends on
precisely formatted retained state rather than conversational recollection
```

Potential gain:

```text
structured notes
→ lower reconstruction burden
→ cleaner session re-entry
→ less contamination from prose history
```

Unresolved:

```text
what minimum note schema is sufficient
what must remain authoritative
what can remain reconstructable
how note passage should be admitted/audited
```

This should be treated as a continuity experiment, not assumed memory architecture.

---

## 35.3 Compression / Cost Dynamics in the Workshop

Pressure:

```text
the current evidence suggests active semantic structure has a cost
```

Observed directional pattern:

```text
too little structure
→ conflation / false closure

too much active structure
→ composition burden / projection dropout

qualified local structure
→ better consequence control
```

This motivates a future workshop question:

```text
How does legitimate semantic structure affect:
- local coherence
- reconstruction burden
- token/context cost
- relation application
- coupling between agents
- consequence fidelity
```

Candidate experimental frame:

```text
semantic legitimacy
×
compression ratio
×
active distinction load
×
coupling density
→
coherence / consequence / cost
```

No optimization law is yet claimed.

---

## 35.4 Event Budget / Emergence Pressure

A further pressure is visible:

```text
not every retained distinction needs to be active
for every event
```

Candidate projection:

```text
active admissibility surface
=
resolution of relevant distinctions
under current event budget
and emergence pressure
```

This remains speculative until executable pressures show that changing event budget or emergent coupling changes which distinctions materially govern consequence.

---

# 36. Current Consequence

The project now has enough evidence to justify a new experimental question:

```text
Can retained distinctions be made functionally testable
against one another
without prematurely turning the distinction bank
into fixed ontology?
```

That question is currently higher-value than adding more semantic categories.

A plausible next sequence is:

```text
1. audit the new evidence packet

2. version the distinction bank into testable relational records

3. pressure pairwise / local matrix relations

4. test structured chat-tunnel notes as a continuity carrier

5. move the resulting legitimate semantics into
   compression / cost / coupling experiments
```

This sequence is a projection only.

The project remains free to follow whichever pressure produces the clearest executable consequence.

