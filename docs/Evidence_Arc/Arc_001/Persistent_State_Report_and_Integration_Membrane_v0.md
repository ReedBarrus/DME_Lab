# Persistent State Report & Integration Membrane v0

**Project:** DME_Lab / CSE experimental lineage  
**Date:** 2026-09-16  
**Status:** Candidate operational protocol  
**Purpose:** Periodically compress active experimental evidence into persistent state without allowing raw evidence, failed tests, speculative projections, or conversational drift to silently become architecture.

---

## 1. Core rule

At every configured context-budget boundary `x`, execute:

```text
x := next context-report boundary

when CONTEXT_PRESSURE reaches x:
    REPORT(
        EVALUATE(
            EVIDENCE(since_previous_report)
        )
    )
```

Equivalent form:

```text
ContextWindow#Tokens -> protocol(report(evaluate(evidence)))
```

The report is an **append-only persistent-state descendant**. It does not rewrite the evidence it summarizes.

If exact context-token telemetry is available, `x` is a configurable token interval. If exact telemetry is unavailable, the same protocol fires at the nearest observable surrogate boundary:

- before context compaction / handoff,
- after a replicated failure or pass,
- after an earned new distinction,
- before changing experimental axis,
- before architectural promotion,
- whenever the active surface becomes too large to reconstruct cheaply.

No report is allowed to manufacture certainty merely to reduce context.

---

## 2. Why this exists

The system is now experimentally demonstrating that projection and compression can lose distinctions even while underlying state or trajectory remains correct.

Therefore persistent memory cannot be treated as ordinary summarization.

The report protocol must preserve:

```text
what was observed
what transformation was applied
what survived
what was lost or unresolved
what was inferred
what was merely projected
what changed standing
what remains under pressure
```

The governing law is:

```text
compression may reduce surface area;
it may not silently increase certainty, authority, or consequence capacity.
```

---

## 3. Report packet

Each persistent report SHOULD contain the following fields.

```text
REPORT_ID
PARENT_REPORT_ID
BOUNDARY
ACTIVE_EXPERIMENT_AXIS
CURRENT_PROBLEM
CURRENT_SURFACE

EVIDENCE_OBSERVED
EVIDENCE_REPLICATED
FAILURES
PASSES

DISTINCTIONS_EARNED
DISTINCTIONS_CANDIDATE
HYPOTHESES
REJECTED_INTERPRETATIONS

AUTHORITATIVE_STATE
LINEAGE_REFERENCES
COUNTERFACTUAL_OBJECTS
AUTHORITY_STATE
BUDGET_HORIZON

UNRESOLVED
ACTIVE_PRESSURE
NEXT_SMALLEST_PRESSURE

ARCHITECTURE_ELIGIBILITY
```

`ARCHITECTURE_ELIGIBILITY` is never inferred from rhetorical confidence. It is one of:

```text
EVIDENCE_ONLY
CANDIDATE_FOR_PROMOTION
PROMOTED
REJECTED
SUPERSEDED
```

---

## 4. Evidence standing

Persistent reports preserve explicit standing.

```text
OBSERVED
    one bounded specimen occurred

REPLICATED_LOCAL
    the same bounded relation survived repeated local trials

SUPPORTED
    multiple specimens / contrasts support the distinction within declared scope

HYPOTHESIS
    explanatory projection not yet isolated by pressure

REJECTED
    pressure falsified or displaced the candidate

UNRESOLVED
    available basis cannot legitimately decide
```

Absence of support is not rejection.

```text
NOT ESTABLISHED != FALSE
```

---

## 5. Persistent-state update law

A report may update persistent working state only by **append + reference**.

```text
old report R_n
    |
    +--> evidence descendants
    |
    +--> R_(n+1)
```

A later report may supersede a prior interpretation while retaining the earlier report as historical evidence.

```text
correction != rewrite
reconstruction != restoration
```

This allows later reconstruction to recover not only the current claim, but the transformation by which its standing changed.

---

# PART II — SOFT ARCHITECTURAL LINEAGE BOUNDARY

## 6. Two lineages

Maintain two related but non-identical lineages.

### Experimental lineage

May contain:

```text
raw prompts
raw outputs
runtime traces
failed tests
successful tests
counterfactuals
hypotheses
metaphors
candidate operators
candidate geometry
unresolved terminology
competing explanations
```

Its job is discovery.

### Architectural lineage

May contain only explicitly promoted objects:

```text
accepted constraints
bounded contracts
stable interfaces
required invariants
integration decisions
executable tests
migration / rollback notes
```

Its job is integration.

The lineages may reference one another but MUST NOT share implicit standing.

---

## 7. The membrane

The soft boundary is:

```text
EXPERIMENTAL LINEAGE
        |
        | explicit promotion packet only
        v
INTEGRATION MEMBRANE
        |
        | admitted architectural consequence
        v
ARCHITECTURAL LINEAGE
```

Nothing crosses because it was:

- discussed often,
- rhetorically compelling,
- present in a checkpoint,
- produced by a stronger model,
- mathematically pretty,
- mythically resonant,
- or convenient for implementation.

The architecture does not ingest raw experimental context as premises.

---

## 8. Promotion packet

A distinction crosses the membrane only through a typed promotion object.

```text
PROMOTION_ID
SOURCE_EVIDENCE_REFS
DISTINCTION
DECLARED_SCOPE
STRONGEST_SIMPLER_BASELINE
OBSERVED_NAVIGATIONAL_DIFFERENCE
FAILURE_WITHOUT_DISTINCTION
PASS_WITH_DISTINCTION
KNOWN_COUNTEREXAMPLES
UNRESOLVED_EDGES
MINIMAL_ARCHITECTURAL_CHANGE
REQUIRED_TEST
ROLLBACK_PATH
AUTHORITY_FOR_INTEGRATION
```

Minimal promotion law:

```text
No consequential discrimination,
no structural promotion.
```

The distinction must change consequential navigation relative to the strongest simpler baseline inside the declared scope.

---

## 9. No-leak invariants

### Evidence does not leak into architecture

```text
EVIDENCE != CONTRACT
TEST RESULT != GENERAL LAW
PROJECTION != INTERFACE
HYPOTHESIS != DEPENDENCY
METAPHOR != SCHEMA
COUNTERFACTUAL != AUTHORITY
```

### Architecture does not rewrite evidence

An architectural choice may create a new test condition, but it may not reinterpret prior evidence merely to justify itself.

```text
integration decision
-> new descendant pressure
!=
retroactive repair of evidence
```

### Failed integration remains visible

If a promoted distinction fails under implementation pressure:

```text
architecture failure
-> retain trace
-> demote or amend promotion
-> return to experimental lineage
```

Do not patch the architecture and silently preserve the old claim.

---

## 10. Read-through without inheritance

The boundary is **soft**, not opaque.

Architectural work may read experimental lineage by reference when necessary.

But:

```text
READ(evidence)
!=
INHERIT_STANDING(evidence)
```

Likewise, experimental work may inspect architectural consequences without treating current architecture as proof of correctness.

This allows reconstruction without semantic leakage.

---

## 11. Integration capsule

For ordinary architectural work, provide only a minimal capsule:

```text
ACTIVE_PROMOTED_DISTINCTIONS
CURRENT_CONTRACT
CURRENT_INVARIANTS
CURRENT_TESTS
KNOWN_LIMITS
SOURCE_PROMOTION_REFS
```

Raw experiment history remains addressable behind the references but is not projected into active implementation context unless reopened deliberately.

This supports:

```text
compress stable interior;
spend attention at the moving boundary.
```

---

## 12. Context-budget reporting and integration interaction

At each report boundary:

```text
1. Evaluate evidence since prior report.
2. Append persistent report.
3. Preserve unresolvedness and rejected interpretations.
4. Recompute active experimental cursor.
5. Identify any promotion candidates.
6. DO NOT promote automatically.
7. If integration is requested, build explicit promotion packet.
8. Architectural lineage consumes only admitted promotion packets.
```

Therefore periodic reporting cannot itself become an architecture-growth mechanism.

---

## 13. Reconstruction contract

A new model/session/agent should be able to reconstruct current experimental work from:

```text
latest persistent report
+ referenced active evidence
+ current authoritative repository state
```

A new architectural worker should instead reconstruct from:

```text
current repository state
+ active architectural contract
+ promoted integration capsules
```

This intentionally produces different local evaluation surfaces.

The experimental worker sees uncertainty and pressure.
The architectural worker sees only earned constraints necessary to implement safely.

---

## 14. Current immediate application

The current CSE/Qwen campaign SHOULD remain on the experimental side of the membrane.

Current candidate concepts such as:

```text
EXCITE
EXPRESS
RECONCILE
six-coordinate / two-triad geometry
consequence-potential metrics
stochastic lineage constraint
semantic compiler stages
```

remain experimental unless separately promoted.

More strongly supported distinctions such as:

```text
current state != future reachable state
counterfactual != authoritative
correction != historical rewrite
unknown != false
partial order != total sequence
witness != reusable interface
trajectory coordinate != state predicate alone
```

may become promotion candidates, but still require explicit integration packets before architectural use.

---

## 15. Protocol invariant

The reporting system itself must obey the same law being discovered by the lab:

```text
A report is a projection of evidence.
A report is not the evidence.
```

Therefore every persistent claim that can affect later navigation must retain enough lineage to reconstruct the evidence and transformation that gave it standing.

Final protocol:


a) periodically compress active evidence into a lineage-bearing report,

b) preserve unresolvedness and competing interpretations,

c) keep experimental and architectural lineages distinct,

d) allow only explicit promotion objects to cross the integration membrane,

e) retain references so either side can reconstruct what it needs without inheriting the other side's standing.

```text
EVIDENCE
-> REPORT
-> DISTINCTION
-> PROMOTION CANDIDATE
-> INTEGRATION MEMBRANE
-> ARCHITECTURAL CONSEQUENCE
-> NEW EVIDENCE
```

**End of protocol.**
