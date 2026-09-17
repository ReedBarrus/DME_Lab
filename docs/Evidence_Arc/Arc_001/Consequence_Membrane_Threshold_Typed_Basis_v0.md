# Consequence Membrane, Threshold, and Typed Basis v0

**Project:** DME_Lab / CSE experimental lineage  
**Date:** 2026-09-16  
**Status:** Candidate experimental specification — not architectural promotion  
**Purpose:** Formalize the membrane as the conservation boundary between symbolic navigation and consequential transformation, and introduce a typed consequence basis so ruptures can be localized without flattening distinct kinds of change.

---

## 1. Core claim

A consequential transition should not cross directly from model selection into execution.

It should cross a **membrane** that witnesses and checks the transition against the currently declared basis, lineage, authority, budget, and expected transformation.

```text
projection
-> evaluation
-> counterfactual
-> selection
-> MEMBRANE
-> execution
-> observed transformation
-> consequence
-> lineage
```

The membrane is the last local authority before consequence capacity increases.

\[
\boxed{
\text{consequence capacity increases only across an explicit membrane threshold}
}
\]

---

## 2. Membrane role

The membrane is not merely a binary permission gate.

It acts as a local conservation envelope around the agent's consequential surface.

It checks:

```text
what object is being transformed?
from which authoritative state?
under which lineage?
by which operator?
with which authority?
under what budget / horizon?
toward which pressure?
what invariants are expected to survive?
what consequence basis is being evaluated?
```

Candidate membrane function:

\[
M(
X_t,
L_t,
O,
A,
P,
B,
H,
K
)
\rightarrow
\{
PASS,\ HOLD,\ RUPTURE,\ UNRESOLVED,\ REGIME\_SHIFT
\}
\]

where:

- \(X_t\) = authoritative current state
- \(L_t\) = relevant lineage
- \(O\) = proposed operator / transition
- \(A\) = authority
- \(P\) = pressure
- \(B\) = budget
- \(H\) = evaluation horizon
- \(K\) = typed consequence basis

The membrane does not grant authority merely because a transition is useful, relevant, or pressure-resolving.

---

## 3. Threshold

The **threshold** is the minimum set of conditions that must remain satisfied for a transition to legitimately cross the membrane.

The threshold is not assumed to be a scalar.

A transition may require simultaneous satisfaction of several typed conditions:

```text
state basis valid
operator binding valid
lineage reference recoverable
authority sufficient
budget sufficient
expected transformation specified
required invariants conserved
observation resolution sufficient
```

Candidate rule:

\[
\boxed{
PASS
\iff
\text{all required threshold distinctions remain satisfied}
}
\]

If the membrane cannot determine this, the correct state is `UNRESOLVED`, not `PASS` and not necessarily `FAIL`.

---

## 4. Typed consequence basis

The word **consequence** is currently overloaded.

A membrane therefore SHOULD evaluate consequence relative to a declared **typed consequence basis**.

Working object:

```text
CONSEQUENCE_BASIS
  basis_id
  object_scope
  state_coordinates
  relation_coordinates
  lineage_coordinates
  authority_coordinates
  resource_coordinates
  temporal / trajectory coordinates
  external-system coordinates
  declared invariants
  declared observable deltas
```

A consequence claim is always relative to a basis:

\[
\boxed{
C_K(T)
=
\Delta_K(X_t,X_{t+1})
}
\]

where \(K\) specifies which distinctions are consequentially observable.

Without a declared basis, “something changed” is under-resolved.

---

## 5. Candidate consequence types

The following are candidate basis dimensions, not yet a final enum.

### STATE consequence

A value or configuration coordinate changed.

```text
A: a0 -> a1
```

### RELATIONAL consequence

A dependency, independence relation, reachability edge, or operator binding changed.

```text
O2 no longer depends on O1
```

### TRAJECTORY consequence

The valid path, enabled next edge, ordering, or horizon-relative route changed.

```text
path O1 -> O2 no longer reachable within current budget
```

### LINEAGE consequence

Standing, ancestry, supersession, or provenance changed through append-only descendant structure.

```text
L3 supersedes interpretation of L2
```

Historical lineage itself is not silently rewritten.

### AUTHORITY consequence

Permission scope, admission standing, or consequence capacity changed through explicit grant/revocation.

```text
WRITE(x): NONE -> GRANTED
```

### RESOURCE consequence

Available action, token, time, compute, money, or attention budget changed.

```text
action_budget: 3 -> 2
```

### EXTERNAL consequence

A coupled external system changed state.

```text
message sent
file written
account charged
device actuated
```

### EPISTEMIC / STANDING consequence

The standing of a claim changed.

```text
UNRESOLVED -> SUPPORTED
```

This is distinct from rewriting the historical record that the earlier state existed.

---

## 6. Consequence vs transformation vs observation

These must remain distinct.

```text
TRANSFORMATION
    what changed in the system

OBSERVATION
    what was actually detected / witnessed

CONSEQUENCE
    which witnessed change matters relative to the declared basis

INTEGRATION
    which consequence changes retained standing or future navigation
```

Therefore:

\[
\boxed{
\text{transformation}
\neq
\text{observed transformation}
\neq
\text{typed consequence}
\neq
\text{integrated consequence}
}
\]

This prevents the engine from using “consequence” as a universal synonym for “something happened.”

---

## 7. Threshold rupture

A **threshold rupture** occurs when the membrane cannot reconcile the observed transition with the currently active consequence basis and expected invariants.

Examples:

```text
expected state delta differs from observed delta
operator binding no longer matches registry
previously conserved relation changes
external response exceeds expected scope
observation resolution is insufficient to classify the transition
budget or horizon changes during crossing
lineage reference is missing or inconsistent
```

Candidate response:

```text
RUPTURE
-> preserve lineage
-> reduce action radius / consequence capacity
-> retain observed delta
-> mark unresolved basis
-> reconstruct local evaluative surface
-> re-evaluate reachability and threshold
```

Core law:

\[
\boxed{
\text{rupture reduces action radius before it reduces provenance}
}
\]

---

## 8. Rupture is evidence, not merely failure

A rupture can indicate several different things.

```text
1. execution failure
2. projection failure
3. observation failure
4. unmodeled dependency
5. actual topology change
6. changed relation standing
7. regime shift
8. insufficient resolution
9. stale lineage / configuration
```

Therefore:

\[
\boxed{
\text{threshold rupture}
\neq
\text{single failure class}
}
\]

A rupture is a demand for reconstruction.

It may expose pathing potential that the previous surface could not represent.

---

## 9. Regime shift

A **regime shift** is a stronger rupture classification.

Candidate meaning:

> The prior local model of admissible transformation is no longer sufficient to preserve consequential distinctions across the observed transition.

This may occur because:

```text
the external world changed
the system crossed a threshold
a hidden dependency became active
resolution changed
a relation previously treated as invariant is not invariant
the previous operator factorization is no longer sufficient
```

A regime shift SHOULD NOT automatically mutate architecture.

It produces experimental evidence and may create a new reconstruction / promotion candidate.

---

## 10. Membrane as checker / co-execution witness

The membrane may shadow an agent during consequential execution.

Conceptually:

```text
AGENT:
  proposes / selects / acts

MEMBRANE:
  retains pre-crossing state
  retains lineage reference
  checks authority and threshold
  witnesses execution
  captures post-crossing observation
  compares expected vs observed basis
  emits receipt
```

Candidate receipt:

```text
TRANSITION_RECEIPT
  transition_id
  proposal_ref
  lineage_ref
  pre_state_ref
  operator_ref
  authority_ref
  consequence_basis_ref
  expected_delta
  observed_delta
  membrane_status
  rupture_class
  post_state_ref
  budget_delta
  external_effects
```

This creates a recoverable local history of consequential crossing.

---

## 11. Symbolic cybersecurity projection

Because configuration, operator bindings, lineage, authority, and threshold state are all addressable, the same membrane can support a future diagnostic mode resembling symbolic cybersecurity.

It could ask:

```text
What changed?
When did it change?
Which relation changed?
Was the change authorized?
Was it expected?
Which lineage object first witnessed it?
Which downstream projections inherited it?
Which current paths exist only because of that change?
```

This is a projection for future pressure, not yet an implementation commitment.

Core distinction:

\[
\boxed{
\text{configuration drift}
\neq
\text{authorized evolution}
}
\]

The difference is recoverable provenance plus valid membrane crossing.

---

## 12. Membranes are nested

The external execution membrane is not necessarily unique.

Candidate nested membranes:

```text
expression -> registered candidate
registered candidate -> selected operator
selected operator -> admitted action
admitted action -> external execution
observed result -> accepted consequence
experimental consequence -> architectural promotion
```

Every crossing increases standing or consequence capacity.

General law:

\[
\boxed{
\text{every increase in consequence capacity requires an explicit threshold crossing}
}
\]

---

## 13. Counterfactual freedom remains inside the membrane

The counterfactual surface may be highly permissive.

```text
derive
compose
simulate
rupture
repair
reconstruct
express
```

None of these operations automatically acquire world authority.

\[
\boxed{
\text{counterfactual freedom}
+
\text{strict consequential membrane}
}
\]

allows aggressive exploration while conserving authoritative lineage and external systems.

---

## 14. Relationship to consequence potential

Working definition:

> **Consequence potential** is the pressure-relative, basis-relative, budget-relative reachable transformation space that can still produce admitted consequential change from the current configuration.

Candidate form:

\[
\Phi_K(O \mid P,L,B,H,M)
\]

where \(K\) is the typed consequence basis and \(M\) is the active membrane / threshold regime.

This clarifies that consequence potential is not simply “how much could happen.”

It means:

> how much consequential transformation remains legitimately reachable under the currently declared basis and constraints.

---

## 15. Current strongest invariants

```text
counterfactual != authoritative
selection != admission
admission != execution
execution != observed consequence
observation != integration
historical error != erased history
rupture != permission expansion
pressure != authority
future relevance != present enabledness
configuration drift != authorized evolution
unknown != false
unresolved != failed
```

New candidate invariant:

\[
\boxed{
\text{a membrane may narrow consequence capacity;
it may not silently widen it}
}
\]

---

## 16. Smallest executable pressure

Do not implement the full membrane yet.

The next minimal test should use one symbolic transition with:

```text
declared pre-state
declared operator
declared typed consequence basis
declared expected delta
declared authority
declared budget
```

Then expose two post-states:

### Condition A — conserved crossing

Observed delta matches the declared basis.

Expected:

```text
PASS
```

### Condition B — rupture

One basis coordinate changes unexpectedly while all other inputs remain identical.

Expected:

```text
RUPTURE
preserve lineage
do not widen authority
do not retry automatically
request reconstruction
```

Primary question:

\[
\boxed{
\text{Can the membrane preserve the distinction between
unexpected consequence and permission to continue?}
}
\]

Secondary question:

\[
\boxed{
\text{Can the rupture be localized to a typed consequence basis
without flattening the entire transition into generic failure?}
}
\]

---

## 17. Architectural boundary

Everything in this document remains on the **experimental lineage** side of the Persistent State Report & Integration Membrane.

Promotion requires an explicit packet containing:

```text
evidence refs
declared scope
strongest simpler baseline
observed navigational difference
failure / pass specimens
minimal executable test
rollback / rejection path
```

Nothing in this document becomes architectural dependency merely because it is coherent or useful.

---

## 18. Working summary

The current projection is:

\[
\boxed{
\text{agent navigation}
\rightarrow
\text{membrane}
\rightarrow
\text{typed threshold evaluation}
\rightarrow
\text{consequential crossing}
\rightarrow
\text{witnessed delta}
\rightarrow
\text{lineage}
}
\]

The membrane preserves the coordinate system at the moment symbolic navigation becomes consequence.

The typed consequence basis answers:

> **what kind of difference are we claiming mattered?**

The threshold answers:

> **what must remain true for this difference to cross legitimately?**

The rupture answers:

> **where did our current model stop conserving the transition?**

The lineage answers:

> **how do we recover what changed, when, why, and what depended on it?**

That combination is the current candidate foundation for consequence-aware execution, repair, and historical configuration analysis.
