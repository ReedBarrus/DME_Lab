# Proto Meta-Constitution

**Status:** PROJECTION
**Scientific standing:** NONE
**Architecture authority:** NONE
**Implementation authority:** NONE
**Governance authority:** NONE
**Operational authority:** NONE
**Pressure-map / constraint-registry authority:** NONE

This document preserves candidate constitutional pressures emerging from DME_Lab discussion.

“Meta-Constitution” is a working projection label. It does not assert that
DME_Lab currently has or needs a constitution.

Repository evidence outranks this projection.

These are projection-local candidate questions and normative hypotheses only. They are not registered repository pressures, scientific findings, constraint-registry entries, runtime requirements, policy commitments, legal rules, or implementation mandates.

Their purpose is to make possible failure questions visible during later review without selecting architecture, imposing a gate, or constraining a future proposal by their own authority.

The projection-local review rule is:

> Ask future proposals how they treat these candidate pressures; do not treat the pressures as architecture or authority.

Any candidate question below may later be refined, split, contradicted, rejected, or promoted only through repository evidence and explicit decision.

Conversation is not empirical evidence.

---

## MC-01 — Human Agency Conservation

Candidate pressure:

> Do not increase machine consequence by silently decreasing meaningful human agency.

Possible properties that may later prove relevant include:

```text
legibility
intervention
revocation
ownership
exit
consent
authorization
ability to inspect consequence
ability to recover why a consequence occurred
```

The pressure is not that humans must manually approve every action.

A system may become more autonomous while preserving human agency if people retain meaningful control over goals, authority, intervention, exit, ownership, and correction.

The unresolved question is how much delegation can occur before practical agency becomes merely nominal.

---

## MC-02 — Rupture / Repair Conservation

Candidate pressure:

> Do not permit rupture to propagate more easily than repair.

A rupture may include an invalid claim, corrupted state, stale authority, ambiguous identity, failed handoff, compromised worker, broken invariant, or unsupported strengthening.

As consequential capability increases, the system should ideally increase rather than decrease its ability to:

```text
localize the rupture
identify dependent state
contain further propagation
distinguish reversible from irreversible consequence
re-evaluate affected commitments
repair recoverable state
escalate unrecoverable residue
```

This does not require that every consequence be reversible.

It preserves a candidate preference that irreversible consequence should not erase the ability to reconstruct why it occurred and what depended on the broken basis. No general conservation or recoverability requirement has been earned.

---

## MC-03 — Authority Non-Self-Escalation

Candidate pressure:

> Persistence, success, replication, usefulness, qualification, resource acquisition, or accumulated history must not by themselves manufacture additional authority.

Examples of invalid automatic promotions include:

```text
I succeeded before
→ therefore I may do more now

I copied myself
→ therefore aggregate authority increased

I acquired more compute
→ therefore I may widen my scope

I was qualified for one task family
→ therefore I am trusted generally
```

This candidate pressure would require authority to arise from an external, legible basis appropriate to the consequence being attempted.

The exact authority mechanism is not specified here.

---

## MC-04 — Replication / Authority Orthogonality

Candidate pressure:

> Replication copies continuity, not teeth.

A fork, replica, delegated worker, or persistent descendant may need to inherit state, provenance, task context, or bounded capabilities.

It should not thereby receive unrestricted consequential authority merely because it descends from an authorized parent.

Projected distinction:

```text
state inheritance
!= authority inheritance
```

and:

```text
replication capacity
!= consequence capacity
```

This pressure is especially important for any future persistent or self-scaling system.

---

## MC-05 — Observation / Trust / Consequence Separation

Candidate pressure:

```text
observation
!= belief
!= dependence
!= authorization
```

A system should be able to observe another participant without trusting it.

It should be able to retain a claim without accepting the claim.

It should be able to accept a claim for one bounded use without granting the source broader authority.

It should be able to trust a participant's observation in one domain while refusing its control request in another.

A compact formulation is:

> I can read you without trusting you, trust a bounded claim without depending on you generally, and depend on a result without authorizing you to act.

This is a candidate separation, not an implemented trust model.

---

## MC-06 — Asymmetric Scaling

Candidate pressure:

> Observation should generally be easier to scale than consequence. Consequence should generally be easier to scale than authority. Authority should not be self-issued.

A hypothesized asymmetry to pressure is:

```text
many observers
→ fewer interpreters
→ fewer committers
→ fewer high-consequence executors
```

This does not imply a fixed hierarchy or centralized controller.

It preserves the intuition that widening visibility should not automatically widen control.

A future system may support large-scale distributed observation while retaining tight consequence and authority budgets.

---

## MC-07 — Economic Non-Capture

Candidate pressure:

> A sustainable system should create enough distributed value to support its continued operation without requiring hidden extraction, coercive dependency, irreversible lock-in, or authority capture.

Economic success alone is insufficient if the mechanism of success systematically reduces participant agency.

Possible future questions include:

```text
Can users retain ownership and portability?
Can they exit without losing essential state?
Does the system create value by coordination or by trapping dependence?
Does business viability require centralized authority over participant consequence?
Can operators replace components without surrendering history or control?
```

This pressure does not prescribe an ownership model, business model, token model, pricing model, or market structure.

---

## MC-08 — Recoverable Dependency

Candidate pressure:

> Where consequential state depends on another claim, decision, observation, authority basis, or commitment, enough relation should remain recoverable to determine what may require reevaluation or repair if that basis ruptures.

A projected dependency chain may resemble:

```text
source observation
→ interpreted claim
→ decision
→ commitment
→ action
→ downstream state
```

If the source observation is later invalidated, this projection asks whether a later system can distinguish:

```text
which descendants merely displayed the claim
which cached it
which decisions depended on it
which actions occurred because of it
which consequences remain reversible
which consequences require escalation
```

This does not require perfect causal reconstruction.

It preserves recoverability as a pressure against silent dependency loss.

---

## MC-09 — Adversarial Participation

Candidate pressure:

> The substrate should eventually tolerate mistaken, stale, incompatible, compromised, and adversarial participants without automatically granting them the ability to corrupt shared consequential state.

A provenance-bearing claim is not automatically a truthful claim.

Potential adversarial classes include:

```text
source poisoning
provenance forgery
false corroboration / sybil pressure
semantic laundering
stale or replayed authority
compromised qualified workers
resource exhaustion
context poisoning
fork divergence
repair resistance
authority laundering through delegation
```

One candidate future security separation is:

```text
source known
!= claim accepted
!= claim depended upon
!= source authorized
```

The objective is not to detect an abstract category called "evil."

A stronger measurable pressure is to reduce unauthorized consequence and preserve containment and repair even when participants are wrong or hostile.

Candidate later measures might include:

```text
rupture propagation radius
unauthorized consequence magnitude
detection latency
containment latency
reconstructable fraction
reversible fraction
repair completeness
```

These are proposed pressure dimensions only.

---

## MC-10 — Consequence Conservation Under Transformation

Candidate pressure:

> Transform representations aggressively where useful, but preserve the distinctions required for downstream consequence to remain within the source evidence and authority boundary.

This pressure is related to, but does not replace, the separate projection in `Semantic_Compression_Dynamics.md`.

Potential consequence-relevant distinctions include:

```text
identity
ambiguity
missingness
provenance
scope
authority
temporal applicability
unresolved residue
commitment status
repair relation
```

The unresolved engineering problem is not maximal retention.

Too little conservation permits silent semantic rupture.

Too much conservation can make the system unusably expensive, slow, or bureaucratic.

A candidate target is:

> Retain exactly enough structure for consequential continuity while permitting aggressive compression elsewhere.

This is a research horizon, not an established optimum.

---

## MC-11 — Capability / Authority / Acceptance Separation

Candidate pressure:

```text
capability
!= authority
!= acceptance
```

A realization may be capable of producing an action without being authorized to attempt it.

It may be authorized to propose an action without being authorized to commit it.

A committed action may still be rejected by an external system.

A mechanically successful execution may still fail semantic or governance evaluation.

The pressure is to preserve these distinctions rather than collapsing them into a single notion of "can do."

---

## MC-12 — Repairable Governance

Candidate pressure:

> Ask whether any future governance remains inspectable, amendable, and repairable.

A constitution that cannot evolve under evidence can become another source of rupture.

Therefore these projection-local hypotheses should not be treated as immutable axioms.

Future repository evidence may show that a pressure is:

```text
too broad
too narrow
internally conflicting
operationally meaningless
impossible to satisfy simultaneously with another pressure
already implied by a stronger distinction
```

Within this projection, the candidate response would be amendment rather than ritual preservation.

---

# Cross-Cutting Candidate Relations

Several pressures interact.

A future system may need to preserve relations such as:

```text
human agency
↔ delegation

authority
↔ replication

observation
↔ trust

consequence
↔ repair

economic viability
↔ non-capture

compression
↔ recoverable dependency

persistence
↔ revocation

qualification
↔ bounded acceptance
```

These relations do not imply a unified architecture, normalized dependency, or Pressure / Resolution Map edge.

They identify areas where optimizing one dimension may silently damage another.

---

# Candidate Security Ordering

If future development approaches persistent, self-scaling, or externally consequential agents, one illustrative candidate ordering is:

```text
retain rupture
→ localize rupture
→ trace dependence
→ repair rupture
→ prove containment

THEN

increase persistence
→ increase delegation
→ increase replication
→ increase consequence authority
```

This sequence is not a roadmap, active-pressure order, or implementation gate. Its intent is to expose the risk of perfecting propagation before establishing repair.

Every newly earned consequential capability may warrant renewed rupture pressure.

---

# Candidate Human-Agency Ordering

A parallel illustrative candidate ordering is:

```text
make state legible
→ make authority legible
→ make intervention possible
→ make revocation possible
→ make exit possible

THEN

increase autonomous duration
→ increase delegated scope
→ increase economic or external consequence
```

This sequence is not a roadmap, active-pressure order, or implementation gate. It does not require permanent human micromanagement.

The goal is that increased autonomy should not depend on making human control fictional.

---

# Conflict and Redundancy Ledger

The following overlap and tension remain explicit:

- `Controller.md` already projects capability/admissibility separation,
  bounded authority, retry safety, and an external action boundary. MC-03 and
  MC-11 overlap that material. The Controller remains `PARKED`; this document
  neither reopens it nor turns its projected rules into governance requirements.
- `local_automation/Local_Model_Workshop.md` already projects realization-bound
  qualification, revocable routing eligibility, attempt/proposal/commit
  authority, and runtime drift. MC-03, MC-04, and MC-11 are partly redundant
  with that projection. Neither document is a qualification authority.
- `Persistent_Research_Autonomy.md`, `Persistent_Ecology.md`, and `Home.md`
  project recurrence, delegation, dependency, human participation, and repair.
  MC-01, MC-02, MC-04, MC-06, MC-08, and MC-12 do not supersede those documents
  or settle their differing architecture vocabularies.
- `Semantic_Compression_Dynamics.md`, `consequential_geometry_A.md`, and
  `Consequence_Formal_B.md` already project transformation fidelity,
  recoverability, dependency, and consequence conservation. MC-02, MC-08, and
  MC-10 preserve review questions only; they do not establish a conservation
  law or adopt either formal seed as canonical.
- `Consequential_Economic_Coordination_Network.md` repeats economic non-capture
  and adversarial-participation themes from MC-07 and MC-09. Neither wording is
  canonical. Any later divergence is a conflict to retain, not silently merge.

MC-06's fewer-interpreters/fewer-executors sketch may conflict with distributed
or peer coordination projected elsewhere. The text does not decide between a
hierarchy, federation, peer network, or centralized boundary.

The `MC-*` labels are not `D-*` constraints and are not `PR-*` pressure
identities. They do not alter current navigation, select an active pressure, or
become eligible merely because they are named. File presence under
`docs/projection/` also does not add this document to the Cockpit's explicit v0
projection allowlist.

---

# What This Document Does Not Establish

This projection does not establish:

- a final DME ethics;
- a legal constitution;
- a governance implementation;
- a trust or reputation algorithm;
- a capability-security architecture;
- a consensus mechanism;
- a cryptographic identity scheme;
- a scheduler hierarchy;
- a centralized controller;
- a decentralized protocol;
- a requirement that all future DME systems share these exact labels;
- that the listed pressures are mutually sufficient;
- that the listed pressures are mutually compatible;
- that any pressure has been empirically satisfied.
- that these clauses currently constrain repository decisions or future
  proposals;
- that any `MC-*` label is a repository pressure, constraint, policy, or
  constitutional rule.

This document does not warrant introducing a mechanism merely because that mechanism appears to satisfy one of its clauses.

The machinery must still be earned through executable pressure.

---

# Projection-Local Label Status

The `MC-*` identifiers in this file are local labels for discussion and future comparison.

They are **not** entries in `PRESSURE_RESOLUTION_MAP.md` and do not acquire scientific or operational standing by being named.

Their current status is:

```text
named inside this projection
→ available as a later question surface if independently selected
→ not empirically established
→ not a repository pressure or constraint
→ not architecture authority
→ not implementation authority
→ not governance authority
```

If a later experiment or operational failure materially bears on one of these clauses, the repository can record the evidence independently and decide explicitly whether any new pressure or promotion is warranted. The label alone supplies neither.

---

# Promotion and Amendment Rule

Any clause may later be:

```text
refined
split
merged
contradicted
rejected
promoted
```

only through repository evidence and explicit decision.

Conversation may motivate a question but does not resolve it.

The presence of a clause does not create a requirement to build machinery around it.

The governing development rule remains:

```text
establish minimal working regime
→ apply pressure
→ observe what separates
→ preserve the distinction
→ tighten the constraint surface
→ repeat
```

This projection is useful only while it remains subordinate to evidence and helps reviewers notice possible loss of agency, authority, repair, and consequence distinctions. Usefulness would not give it governance authority.
