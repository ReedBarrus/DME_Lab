# Local–Global Recoverability Pressure

**Status:** Projection / future pressure source  
**Authority:** Not repository evidence. External mathematical analogue only.  
**Do not promote to architecture, theorem about DME, or current experimental standing.**

## External trigger

A 2026 counterexample to the Jacobian Conjecture in dimension three provides a sharp local/global separation:

- a polynomial map \(F:\mathbb{C}^3\to\mathbb{C}^3\) has constant nonzero Jacobian determinant;
- hence it is locally nondegenerate / locally invertible in the analytic sense;
- yet multiple distinct source points share the same image;
- therefore local invertibility does not imply global injectivity or unique global predecessor recovery.

The explicit Alpöge map was independently formally verified in Isabelle/HOL. Subsequent work characterizes the new family geometrically as étale but non-proper: local unramified behavior survives while global injectivity can fail through behavior at infinity.

This is useful to DME only as an **analogue that exposes a distinction**.

## Candidate distinction

> **Local recoverability under a declared chart or basis does not by itself guarantee global lineage recoverability.**

Equivalent warning forms:

```text
local nondegeneracy
!=
global uniqueness

local inverse available
!=
unique global predecessor

step-local sufficiency
!=
path/global recoverability

locally admissible chart transition
!=
globally warranted lineage reconstruction
```

A projected endpoint may be locally well behaved while still belonging to multiple globally distinct predecessor branches.

## Important non-equivalence

Do **not** formulate the DME analogue as:

```text
globally injective transform
+
globally injective transform
→
noninjective composition
```

That is false: compositions of injective maps remain injective.

The relevant analogue must instead involve one or more of:

- local invertibility rather than global injectivity;
- chart-relative sufficiency rather than domain-wide uniqueness;
- detached projection lacking chart/source association;
- multiple disconnected predecessor branches;
- basis-relative reconstruction that suppresses a global branch distinction;
- boundary / non-properness-like information escaping the retained representation.

The pressure is therefore about **what local evidence fails to certify globally**, not about ordinary injective function composition.

## Translation into current DME language

A consumer may receive a projection \(y\) for which:

```text
given chart/source association:
    a local predecessor is recoverable

without that association:
    multiple predecessor branches remain compatible
```

Formally, for a consumer question \(Q\):

\[
|P_Q(y,e_{\mathrm{local}})| = 1
\]

may hold only after supplying a local chart/source witness, while detached global reconstruction satisfies:

\[
|P_Q(y)| > 1.
\]

The missing distinction is not necessarily the endpoint value. It may be the **branch, chart, source, interval, or lineage association that makes inversion unique**.

## Smallest executable pressure

### Pressure question

> Can two distinct warranted source lineages remain locally reconstructable under their own declared charts while collapsing to the same exposed projection, such that a detached consumer cannot recover which lineage produced the result?

### Minimal synthetic world

Construct two source branches:

```text
BRANCH A                  BRANCH B
source state a            source state b
local chart C_A           local chart C_B
      \                      /
       \                    /
        ---- projection y ---
```

Requirements:

1. \(a \neq b\).
2. Each branch has a valid local reconstruction rule when its chart/source witness is supplied.
3. Both branches produce the same exposed projection \(y\).
4. The detached projection omits the branch/chart association.
5. No hidden oracle is allowed to restore identity after detachment.

### Consumer questions

Run at least two consumer bases:

```text
Q_LOCAL:
Given y + declared chart/source witness,
recover the source state.

Q_GLOBAL:
Given detached y alone,
recover which source lineage produced it.
```

Expected discriminating pattern:

```text
Q_LOCAL:
recoverable

Q_GLOBAL:
basis insufficient / predecessor ambiguity
```

If both are uniquely recoverable, the construction failed to create the intended collision.

If neither is locally recoverable, the apparatus does not isolate the local/global distinction.

## Stronger pathwise variant

After the minimal branch collision is understood, a later pressure may use two multi-step histories:

```text
H_A:
s0 → s1 → s2 → y

H_B:
t0 → t1 → t2 → y
```

Every transition must be locally admissible under its declared basis, but the final detached projection must not encode enough information to determine whether \(H_A\) or \(H_B\) occurred.

The question becomes:

> Does preserving every locally required distinction also preserve the global history distinction needed by the consumer?

This is stronger than endpoint stasis-versus-hidden-traversal because both histories may be internally valid and richly observed while still becoming globally conflated at the exposed projection boundary.

## Relationship to existing DME pressures

### PR-009 — public-history association

This pressure is adjacent to PR-009.

PR-009 already distinguishes:

```text
record identifiers present
!=
authoritative history association recoverable
```

The local/global pressure generalizes the same failure shape:

```text
locally sufficient reconstruction data
!=
globally sufficient lineage association
```

Do not claim PR-009 is resolved by the mathematical analogy.

### PR-001 / hidden traversal

PR-001 established that endpoint snapshots can collapse distinct histories such as:

```text
A → A

vs

A → B → A
```

The proposed pressure differs by asking whether **locally legitimate and reconstructable branches themselves** can collapse under a later projection.

That is:

```text
hidden traversal:
same endpoint conceals different interior history

local/global recoverability:
same projection conceals multiple locally valid predecessor branches
```

These may later compose, but should remain distinct until an experiment requires both.

## Candidate geometry language

If future evidence repeatedly supports this distinction, the following vocabulary may become useful:

```text
local chart recoverability
global lineage recoverability
branch association
projection collision
recoverability scope
boundary loss
```

Avoid prematurely importing:

```text
manifold
covering space
étale map
properness
monodromy
```

as DME architecture.

Those mathematical concepts may inspire pressures, but DME should earn its own operational meanings through executable evidence.

## Potential properness-like question

The external mathematics suggests a future question:

> What additional boundary condition prevents locally valid transformations from losing global predecessor uniqueness?

A DME analogue of "properness" should not be named or implemented until a concrete failure requires something like:

```text
bounded source region
+
preserved branch/source association
+
no untracked escape across projection boundary
→
global recoverability under declared scope
```

This is only a projection.

## What this pressure could earn

A positive result could establish, under a bounded synthetic basis:

- local reconstruction can succeed while detached global lineage recovery fails;
- chart/source association can be a consequential discriminator;
- endpoint/projection equality does not imply predecessor identity;
- recoverability claims require an explicit scope or basis.

## What it cannot earn

It cannot establish:

- a general DME geometry;
- a manifold or atlas architecture;
- universal non-properness;
- a generalized consequence engine;
- agency;
- global provenance recovery;
- that all local DME transformations risk this failure;
- that the Jacobian counterexample is mathematically "the same thing" as DME lineage ambiguity.

## Candidate standing

For now:

```text
EXTERNAL MATHEMATICAL ANALOGUE:
strong

DME CONCEPTUAL DISTINCTION:
plausible and already adjacent to existing pressure evidence

DME EXECUTABLE PRESSURE:
well-posed candidate

DME SHARED ABSTRACTION:
not yet earned
```

## Compression

The useful conserved sentence is:

> **A representation can be locally invertible yet globally ambiguous; recoverability therefore has a scope, basis, and association boundary.**

Or in Lab shorthand:

```text
local warrant
!=
global identity
```

---

## External references

- Levent Alpöge, explicit 2026 counterexample to the Jacobian Conjecture in \(\mathbb{C}^3\), with constant Jacobian determinant and a three-point collision.
- Arthur Freitas Ramos, David Barros Hulak, and Ruy Jose Guerra Barretto de Queiroz, *Formal Verification of an Explicit Counterexample to the Jacobian Conjecture*, Archive of Formal Proofs, 2026.
- Shuhong Gao, *Counterexamples to the Jacobian conjecture in dimensions greater than two*, arXiv:2608.00222, 2026.
