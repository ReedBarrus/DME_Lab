# Agent Trajectory

**Status:** PROJECTION  
**Scientific standing:** NONE  
**Architecture authority:** NONE  
**Implementation authority:** NONE

Repository evidence outranks this projection.

This note preserves a minimal candidate object for observing how one identified realization transforms one admitted basis into a consequential successor without collapsing observation, realization, action, and consequence into one opaque event.

The projection is intentionally underpowered. It does not define agent identity, policy, geometry, regime membership, trajectory distance, or a learning mechanism.

---

## 1. Core Question

Can DME_Lab retain a machine-readable relation of the form:

```text
A
--[identified realization / actual transformation]-->
B
```

while preserving the basis and consequence strongly enough to ask later:

```text
what changed?
what remained invariant?
which part belonged to observation?
which part belonged to the realization?
which part belonged to consequence?
```

The smallest useful trajectory is therefore not merely:

```text
input -> output
```

but:

```text
admitted start basis
        ↓
identified realization + known parameters
        ↓
actual transformation / action
        ↓
observed consequence
        ↓
retained successor state
```

---

## 2. Minimal Relation

Let:

```text
A = admitted starting basis
R = identified realization and known operating parameters
T = actual transformation or action produced by R
C = observed consequence associated with that action
B = retained successor-state reference
```

The candidate relation is:

```text
A --[R,T]--> B
       |
       C
```

This notation is descriptive only.

It does not yet establish that:

```text
R caused all of B
T uniquely determines C
A and B are complete world states
two trajectories are comparable
a trajectory belongs to a stable agent identity
```

---

## 3. Candidate Machine-Readable Surface

A minimal candidate record may resemble:

```json
{
  "trajectory_id": "...",

  "start_basis": {
    "observation_ref": "...",
    "regime_ref": "...",
    "realization_ref": "...",
    "known_parameters": {}
  },

  "transformation": {
    "task_or_action_ref": "...",
    "actual_output_ref": "..."
  },

  "consequence": {
    "observation_ref": "...",
    "preserved": [],
    "ruptured": [],
    "unresolved": []
  },

  "end_state_ref": "..."
}
```

No field above is authoritative merely because it appears here.

For a first implementation, even this may be too large. The strongest candidates are the exact references for start basis, realization, actual transformation, consequence observation, and successor state.

`preserved`, `ruptured`, and similar labels are candidate derived interpretations. They should not outrank the observations from which they were produced.

---

## 4. Distinctions to Preserve

The projection exists mainly to prevent several collapses.

```text
observation basis
!=
regime basis

realization identity
!=
inference parameters

requested transformation
!=
actual transformation

actual transformation
!=
observed consequence

observed consequence
!=
interpreted consequence

trajectory variation
!=
regime departure
```

The same realization may produce different transformations while remaining inside the same consequence-relevant regime.

Conversely, a superficially similar transformation may constitute a regime departure if it crosses a protected boundary such as scope, provenance, missingness, authorization, or another declared invariant.

---

## 5. Why Regime and Realization Must Remain Distinct

Training data, weight updates, inference configuration, retained context, external consequence history, and current regime constraints can all affect behavior.

A later experimental surface may therefore need to distinguish at least:

```text
model / checkpoint
adapter or other training intervention
inference parameters
prompt / context basis
tool surface
retained consequence history
regime constraints
```

The purpose is not to model every cause in advance.

It is to make later behavioral change attributable enough that the Lab can ask whether a trajectory changed because:

```text
the realization changed
or
the observation basis changed
or
the regime changed
or
the retained consequence environment changed
```

rather than treating all adaptation as one undifferentiated agent property.

---

## 6. Candidate Departure Surface

A future trajectory comparison may make agent-mediated departure visible between observation dynamics and consequence dynamics.

Conceptually:

```text
observation dynamics
        ↓
regime expectation
        ↓
agent transformation
        ↓
departure analysis
        ↓
consequence dynamics
```

This projection does not define a numeric departure measure.

The first useful distinction is only:

```text
regime-conformant variation
!=
regime departure
```

Any stronger geometry should be earned from repeated retained trajectories rather than imposed by notation.

---

## 7. What Repeated Trajectories Might Later Support

If enough trajectories are retained under sufficiently controlled bases, later pressure may ask whether the evidence supports notions such as:

```text
stable transformation family
realization-specific tendency
regime boundary
rupture point
repair path
recoverable invariant region
```

These are future questions, not current claims.

A useful later comparison could include:

```text
same or similar A, different R -> how does B differ?
same R, varied A -> what transformation tendencies persist?
same regime, varied trajectories -> which invariants survive?
apparent boundary crossing -> what actually ruptured?
```

No such comparison is authorized by this projection alone.

---

## 8. Relationship to Agent Identity

An agent trajectory is evidence about a realized transformation, not proof of an enduring agent identity.

A future notion of identity might eventually be pressured through recoverable transformation tendencies across changing bases, but this projection preserves only the weaker claim:

> An identified realization produced this transformation from this admitted basis, and this consequence was later observed under the retained evidence available.

Therefore:

```text
trajectory
!=
identity

repeated trajectory pattern
!=
persistent self
```

---

## 9. Deliberate Omissions

This projection does not define:

- trajectory distance;
- trajectory equivalence;
- state-space geometry;
- regime geometry;
- numerical departure magnitude;
- agent personality;
- policy extraction;
- causal attribution beyond retained evidence;
- autonomous learning;
- weight updates;
- routing;
- multi-agent coordination;
- authority promotion.

Those should be introduced only if executable pressure requires them.

---

## 10. Reopening Condition

Implementation becomes interesting when DME_Lab has at least one concrete agent-mediated consequence trace for which retaining only input/output is insufficient to explain or compare what happened.

The smallest warranted pressure would likely be:

```text
freeze one admitted start basis
freeze one realization basis + known parameters
retain one actual transformation
retain one observed consequence
retain one successor reference
```

Then ask whether the resulting trajectory record preserves distinctions that would otherwise be lost during comparison or reconstruction.

Until then:

```text
preserve A -> [R,T] -> B with consequence C
formalize nothing stronger
```

---

## 11. Current Projected Principle

> **An agent trajectory is a basis-relative record of how an identified realization transformed an admitted starting basis into an observed consequential successor. It does not by itself establish agent identity, policy, regime membership, causation, or geometry.**

The intended value is simple: keep the transformation legible enough that later consequence can pressure what the agent actually did rather than treating the agent as an opaque interval between observation and result.
