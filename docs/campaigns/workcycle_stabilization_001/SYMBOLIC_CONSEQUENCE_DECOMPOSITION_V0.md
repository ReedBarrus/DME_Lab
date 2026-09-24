# SYMBOLIC CONSEQUENCE DECOMPOSITION V0 — CANDIDATE

OBJECT_TYPE:
DECOMPOSITION_THEORY_CANDIDATE

OBJECT_ID:
SYMBOLIC_CONSEQUENCE_DECOMPOSITION_V0

STANDING:
PROVISIONAL / PRESSUREABLE

# 1. PURPOSE

Define the missing relation between:

- Atlas dependence/load;
- distinctions;
- relational horizons;
- campaigns;
- bounded executable work;
- observed consequences.

This document is not a planner implementation.

# 2. BOTTOM-UP STRUCTURAL ORDER

Current Atlas refinement already suggests:

```
RELATION
→ DEPENDENCE
→ LOAD
→ RUPTURE / CONSEQUENCE POSSIBILITY
→ OBSERVATION / WITNESS
→ DISTINCTION
→ CORRECTION / ACTION
→ INVARIANCE TEST
```

Therefore:

```
DISTINCTION
!=
TASK
```

A distinction is a local resolution operator that makes some structure
legible.

A work item is a consequence-oriented application of one or more distinctions
to a bounded region of the addressed world.

# 3. CANDIDATE FORMALIZATION

Represent the Atlas at frame t as a typed addressed relational structure:

```
A_t = (V_t, E_t, S_t, P_t)
```

where provisionally:

- V_t = addressed objects;
- E_t = typed relations / dependencies;
- S_t = symbolic standing, distinctions, unresolveds, claim ceilings;
- P_t = provenance / lineage / evidence coordinates.

Each load-bearing relation/object may carry a non-scalar load vector:

```
L_t(x) =
(functional,
 semantic,
 authority,
 provenance,
 temporal,
 coordination)
```

No requirement is made that these coordinates be numeric in V0.

# 4. RELATIONAL HORIZON

A relational horizon is not merely filesystem distance or graph adjacency.

For subject/subsystem q and capability/recovery predicate k, define a candidate
horizon as the frontier across transformations/relations after which k is no
longer supported or recoverable.

Examples already projected by Atlas:

```
H_observe(q)
H_correct(q)
H_reconstruct(q)
H_authority(q)
H_operate(q)
```

Thus a horizon can be represented operationally by a predicate:

```
H_k(q) = boundary where Support_k(q, A_t) changes posture
```

Examples:

- observation becomes insufficient;
- corrective path ceases to cover the failure region;
- provenance no longer supports reconstruction;
- authority becomes stale/unresolved;
- operation fails.

The exact mathematics remain a candidate until pressure earns a formal metric.

# 5. DISTINCTION

A candidate distinction d is not free text.

Provisionally:

```
d =
(scope,
 typed relation / non-collapse,
 support handles,
 applicability,
 claim ceiling,
 dependencies,
 unresolved boundary)
```

Examples:

```
PATH_IDENTITY != CONTENT_IDENTITY
REFERENCE_REACHABILITY != REFERENCE_ADMISSION
HISTORICAL_AUTHORITY != CURRENT_AUTHORITY
```

A distinction becomes task-relevant when it changes what transformations are
lawful or useful near the active horizon.

# 6. CAMPAIGN AS RELATIONAL DELTA ENVELOPE

A campaign should not be reduced to a list of tasks.

Candidate representation:

```
C =
(current addressed frame,
 target relational condition,
 conserved distinctions,
 horizon(s),
 authority ceiling,
 consequence ceiling,
 success conditions,
 unresolveds)
```

The campaign specifies a desired relational/consequence movement, not the exact
low-level action sequence.

# 7. WORK ITEM AS CONSEQUENCE ENVELOPE

Candidate work item:

```
τ =
(
  campaign/horizon identity,
  input addresses,
  preconditions,
  applicable distinctions,
  bounded operator,
  expected consequence Δ_hat,
  conservation envelope K,
  evidence debt,
  authority requirement,
  budget,
  stop condition,
  repair destination
)
```

Execution produces:

```
τ(A_t) → A_(t+1) + W
```

where W is the witnessed consequence/evidence surface.

The evaluator then compares:

```
Δ_hat
vs
Δ_observed(A_t, A_(t+1), W)
```

under K.

# 8. CONSERVATION ENVELOPE

For each task, K asks what must survive over the provisional seven surfaces:

```
K = {
  identity/address,
  mechanical,
  symbolic/semantic,
  relational/topological,
  consequence/environmental,
  provenance,
  invariance/meta-conservation
}
```

A task may intentionally change some coordinates.

It must declare those intended changes and preserve/re-evaluate the others.

Compression is the canonical example:

```
MECHANICAL SIZE:
expected to decrease

SYMBOLIC / RELATIONAL OPERATIVE POSTURE:
expected to survive

PROVENANCE:
must remain challengeable

IDENTITY:
must remain explicitly related, not silently substituted

INVARIANCE:
must be pressure-tested
```

# 9. DECOMPOSITION

Decomposition seeks a family of bounded tasks:

```
D(C, A_t) = {τ_1, τ_2, ..., τ_n}
```

such that:

1. every τ_i binds to C and an exact horizon/decomposition basis;
2. dependencies are explicit;
3. each τ_i has bounded consequence;
4. expected consequences compose toward campaign progress;
5. conservation debt is visible;
6. failure can route to a typed repair level.

Do not require tasks to be globally linear.

The first operational regime may materialize a linear or DAG-like subset while
retaining dependencies explicitly.

# 10. INTERFERENCE / EFFECT

The user's proposed intuition can be made pressureable without claiming a
physical wave equation.

For a candidate transformation τ and active horizon H, ask:

```
Which relations/load coordinates would τ perturb?
Which horizon predicates could move?
Which distinctions constrain interpretation of that movement?
```

Define a candidate effect signature:

```
I(τ | A_t, H)
=
{
  addressed region,
  dependencies touched,
  load dimensions exposed,
  expected horizon movement,
  conservation surfaces at risk
}
```

This "interference" object is initially symbolic/relational and evidence-bound.

It does not need a scalar score.

Later pressure may earn mathematical operators over typed graph/hypergraph
structure.

# 11. DISTINCTION → TASK TRANSLATION

A distinction alone does not create work.

Candidate translation:

```
ACTIVE HORIZON
+
OBSERVED DEPENDENCE / LOAD
+
DISTINCTION THAT MAKES THE WOUND OPERABLE
+
CAMPAIGN TARGET
→
CANDIDATE CONSEQUENCE TRANSFORMATION
→
WORK ITEM
```

Example:

```
OBSERVATION:
docs region contains redundant historic artifacts

DEPENDENCE:
fresh seats require only a subset of relations for reconstruction

DISTINCTION:
SOURCE RETENTION
!=
HOT CONTEXT RETENTION

HORIZON:
H_reconstruct is threatened if provenance/relations are lost

CAMPAIGN TARGET:
reduce contextual load without reducing reconstructability

WORK ITEM:
construct one smaller hot-memory candidate,
cold-retain originals,
run fresh reconstruction,
compare conservation surfaces
```

# 12. TASK → CAMPAIGN RECOMPOSITION

After task execution, do not infer progress from completion.

Candidate recomposition:

```
WORK RECEIPT
+
OBSERVED CONSEQUENCE
+
CONSERVATION RESULT
+
UNRESOLVED LOAD
→
CAMPAIGN-RELATIVE EVALUATION
```

Possible outputs:

```
ADVANCE_SUPPORTED
PARTIAL_ADVANCE
NO_DEMONSTRATED_ADVANCE
DECOMPOSITION_DEFECT
CAMPAIGN_ASSUMPTION_CHALLENGED
APPARATUS_DEFECT
HOLD
```

These are candidate campaign-routing postures, not automatic scientific
promotion.

# 13. WHY COMPRESSION IS THE FIRST REAL TASK FAMILY

Compression directly pressures whether symbolic consequence survives
representation reduction.

It produces immediate operational rent if successful.

Candidate compression work item class:

```
COMPRESSION_WORK_ITEM
```

Required inputs:

- exact source region;
- current reconstruction target;
- known distinctions / claim ceilings;
- dependence/load hints;
- cold-retention destination.

Required output:

- smaller candidate representation;
- source→candidate lineage;
- reconstruction packet;
- conservation comparison;
- observed size/context reduction;
- unresolved losses.

Forbidden early consequence:

- delete authoritative originals;
- declare equivalence without reconstruction pressure;
- erase disagreement/history merely because it appears redundant.

# 14. EXECUTIVE AUTOMATION DEFERRED

The future executive process may operate over:

```
QUALIFIED OBSERVATION
+
ATLAS MEMORY / EVIDENCE
+
DEPENDENCE / LOAD
+
RELATIONAL HORIZONS
+
CURRENT CAMPAIGNS
+
OBSERVED CONSEQUENCES
→
PROPOSE / REPAIR CAMPAIGN
→
DECOMPOSE WORK
```

But V0 intentionally stops before automatic campaign creation.

The immediate pressure is whether deterministic work objects can conserve the
relational meaning of manually/planner-authored campaign packets.

# 15. ACCEPTANCE TARGET

Before executive automation, demonstrate:

```
ONE CAMPAIGN/HORIZON
→
ONE DECOMPOSITION
→
ONE WORK ITEM
→
ONE OBSERVED CONSEQUENCE
→
ONE CONSERVATION EVALUATION
→
ONE TYPED ROUTE
```

with:

```
NO HIDDEN LIVE-CHAT CONTEXT
NO AUTO-AUTHORITY
NO AUTO-PROMOTION
NO SILENT RETRY
NO UNBOUNDED CONTINUATION
```
