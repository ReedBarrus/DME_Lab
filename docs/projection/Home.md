# Home
## Persistent Consequential Locality for Recurrent Agents

**Status:** Shelved projection  
**Version:** v0 concept seed  
**Purpose:** Preserve the Home concept as a future integration environment for DME_Lab without promoting it into current implementation scope.

---

## 0. Shelf Status

Home is **not yet an active development target**.

It is a future integration surface intended to become relevant after DME_Lab has earned enough executable semantics around situated configuration, observer scope and geometry, provenance, guarded transformation admission, uncertainty, residue, reversibility, recoverability, projection warrant, and asynchronous state change.

> **Build Home when the Lab can tell Home what it is allowed to mean.**

---

# 1. Constitutional Idea

Home is a **persistent consequential locality** in which agents may recur without themselves remaining continuously active.

$$
\boxed{
\text{Home persists. Agents recur. Consequence connects the recurrences.}
}
$$

Home owns durable state, history, addresses, and transformation receipts.

Agent processes may appear, observe, reason, propose transformations, disappear, and later recur.

Continuity is therefore not identified with process uptime.

$$
\boxed{
\text{identity continuity lives in provenance, not process persistence}
}
$$

---

# 2. Core Purpose

Home provides a persistent environment in which recurrent model invocations can participate in a shared consequential history.

It should support questions such as:

- What did this agent previously observe?
- What did it infer?
- What did it change?
- What commitments remain unresolved?
- What evidence supports those commitments?
- What happened while the agent was inactive?
- What state is current now?
- Which prior states remain recoverable?
- Which transforms are still admissible?
- Which agent-local claims differ from Home-global history?
- When does a later invocation count as a continuation of an earlier lineage?

Home is therefore not merely memory storage.

$$
\text{memory}
+
\text{lineage}
+
\text{dependency}
+
\text{activation}
+
\text{consequence}
$$

---

# 3. Minimal Semantic Identity

A Home instance may eventually be described by:

$$
H =
(\mathcal L,\mathcal S,\mathcal O,\mathcal T,\mathcal P,\mathcal A)
$$

where:

- $\mathcal L$: persistent ledger/history;
- $\mathcal S$: current materialized state;
- $\mathcal O$: observer contracts;
- $\mathcal T$: available transformation contracts;
- $\mathcal P$: provenance structures;
- $\mathcal A$: hosted agent identities.

This is a conceptual identity, not yet a storage schema.

Home is a **consequence regime**, not an attempted model of the entire world.

It defines a bounded locality within which certain things are addressable, certain observations are legitimate, certain transforms are available, certain histories are retained, and certain claims can be warranted.

---

# 4. Persistent State and Ledger

The authoritative history of Home is conceptually append-only:

$$
L_H = (e_1,e_2,\ldots,e_n).
$$

The current state may be reconstructed or materialized as:

$$
S_n = \operatorname{fold}(L_H).
$$

Each committed event advances Home's revision:

$$
r_n \rightarrow r_{n+1}.
$$

The important distinction is:

$$
\boxed{
\text{ledger history}
\neq
\text{current materialized state}
}
$$

Home should preserve enough provenance that a current projection does not erase the path that warrants it.

---

# 5. Agent Addresses

Each hosted agent receives a stable address independent of any single process invocation.

```text
home://agent/sol
home://agent/astra
home://agent/reed
```

Each address may expose durable structures such as:

```text
/profile
/ledger
/inbox
/claims
/commitments
/observations
/checkpoints
/symbols
/capabilities
```

The address is not the model itself. It identifies a lineage surface.

An agent identity may eventually be represented as:

$$
A_t =
(
\text{address},
\text{ledger},
\text{checkpoint},
\text{commitments},
\text{capabilities},
\text{warrant}
).
$$

A model invocation is only one interpreter acting through that identity.

---

# 6. Agent-Local and Home-Global History

Home should not collapse the following into one history:

$$
L_A \neq L_B \neq L_H.
$$

Home may record that Agent A asserted claim $q$.

Agent B may record that it observed Agent A assert claim $q$.

Agent A may record that it inferred $q$ from evidence $e$.

These are related but non-identical provenance objects.

This allows Home to preserve disagreement, private inference, public action, observation of another agent, conflicting interpretations, independent derivations, and social propagation.

---

# 7. Asynchronous Agent Recurrence

Agents need not remain active continuously.

A recurrent agent interaction may follow:

$$
C_r
\xrightarrow{\text{observe}}
C_A
\xrightarrow{\text{reason}}
T^*
\xrightarrow{\text{validate against }C_{r'}}
C_{r'+1}.
$$

The agent begins from revision $r$.

While it reasons, Home may advance to $r'$.

The proposed transformation must therefore be validated against the current state rather than silently applied to a stale snapshot.

The architecture should never assume that nothing changed while the agent was absent.

---

# 8. Wake Packets

An agent invocation should receive a bounded **wake packet**, not an indiscriminate dump of all history.

A wake packet may eventually contain:

```text
agent
current_home_revision
last_agent_checkpoint
activation_reason
changed_dependencies
unresolved_commitments
relevant_observations
available_operations
relevant_ledger_references
continuity_status
```

Conceptually:

$$
W_A =
(
S_{\text{visible}},
\Delta L,
P,
D,
\operatorname{Ops}(A,S),
r
).
$$

The wake packet is a projection of Home for the current agent and purpose.

It should preserve what changed, what remains unresolved, why the agent was activated, what evidence is available, and what operations are currently legitimate.

---

# 9. Proposed Transformations

Agents should not directly mutate Home state.

They should emit proposed transformations.

```text
actor
observed_revision
transform_contract
target
parameters
dependencies
preconditions
evidence
expected_consequence_class
```

Home then validates the proposal.

If valid:

$$
C_r \xrightarrow{T} C_{r+1}.
$$

If stale or invalid, Home may return:

```text
REBASE_REQUIRED
```

or:

```text
TRANSFORM_NOT_ESTABLISHED
```

with unresolved obligations retained explicitly.

This provides a clean boundary between agent reasoning and authoritative state transition.

---

# 10. Rebase and Concurrent Change

Suppose an agent observes revision $r$.

While it reasons:

$$
r \rightarrow r+1 \rightarrow \cdots \rightarrow r+k.
$$

Its proposed transform should not be silently committed if relevant dependencies changed.

Home should determine whether the proposal remains admissible, needs reinterpretation, conflicts, branches, must be rejected, or requires additional observation.

This directly pressure-tests missing intervals, stale observation, dependency validity, concurrent transforms, and reconstructable context.

---

# 11. Inboxes

Each agent may have a persistent inbox:

```text
home://agent/<id>/inbox
```

Possible events:

```text
claim disputed
dependency changed
object moved
new observation available
symbol gained evidence
symbol lost warrant
request assigned
commitment deadline crossed
recovery became possible
recovery became impossible
```

The inbox persists even while the model process does not.

This allows unresolved consequence to survive outside active inference.

---

# 12. Triggers

Triggers convert persistent dependency into event-driven recurrence.

$$
E_t
\rightarrow
\text{trigger condition}
\rightarrow
\text{agent invocation}.
$$

A trigger may be associated with a claim becoming disputed, a dependency changing, a threshold crossing, new evidence arriving, a region changing, an unresolved commitment becoming actionable, or a previously inadmissible transform becoming admissible.

Triggers should remain typed and inspectable.

They should not be equated with unrestricted autonomy.

---

# 13. Minimal Autonomous Loop

A meaningful autonomous loop appears when the following close:

$$
\boxed{
\text{persistent goals}
+
\text{event-driven activation}
+
\text{situated observation}
+
\text{admissible action}
+
\text{feedback into future state}
}
$$

Then:

$$
\text{history}
\rightarrow
\text{dependency}
\rightarrow
\text{activation}
\rightarrow
\text{action}
\rightarrow
\text{changed world}
\rightarrow
\text{new history}.
$$

Home should make each stage inspectable and provenance-bearing.

---

# 14. Persistence Ladder

Home creates a natural experiment for decomposing memory, lineage, agency, and continuity.

Let $M$ denote a model in an ordinary active session.

Then compare:

$$
M
$$

plain session,

$$
M+R
$$

model + retrieved memory,

$$
M+L
$$

model + ledger lineage,

$$
M+L+D
$$

model + lineage + unresolved dependencies,

$$
M+L+D+T
$$

model + lineage + dependencies + triggers,

and:

$$
M+L+D+T+C
$$

model + lineage + dependencies + triggers + consequential feedback.

This ladder separates several mechanisms usually collapsed under "memory."

---

# 15. Memory Regimes

The progression may be interpreted as:

$$
\text{memory of states}
\rightarrow
\text{memory of transformations}
\rightarrow
\text{memory of unresolved consequence}.
$$

Retrieved memory primarily provides content availability.

Ledger lineage provides historical order and transformation provenance.

Persistent dependency adds directional pressure: something remains unresolved and therefore changes what should happen next.

$$
\boxed{
\text{persistent dependency structure is memory viewed dynamically}
}
$$

Unresolved dependency may act like stored consequential potential.

---

# 16. Identity Experiments

Take two instances of the same model:

$$
M_A=M_B.
$$

Give them different histories:

$$
H_A\neq H_B.
$$

Then compare symbol usage, planning behavior, uncertainty handling, transform preference, recovery behavior, risk response, continuity claims, commitment preservation, and contradiction repair.

A candidate relation is:

$$
\boxed{
\text{effective agent identity}
=
\text{processing regime}
+
\text{lineage}
+
\text{persistent consequence}
}
$$

This remains a hypothesis to be pressure-tested.

---

# 17. Continuity Conditions

A later invocation should not automatically be treated as a legitimate continuation of an earlier agent lineage.

A continuity judgment might eventually require:

$$
\operatorname{Continue}(A_t,A_{t+1})
$$

only if sufficient conditions hold, such as stable address, valid checkpoint chain, compatible semantic contract, no unresolved lineage fork, sufficient provenance, sufficient recoverability, and acceptable discontinuity across inactive intervals.

Possible statuses:

```text
continued
continued_with_gap
forked
recovered
reconstructed
continuity_unresolved
continuity_rejected
```

Identity continuity becomes a warranted relationship rather than an assumption.

---

# 18. Lineage Forking

A single agent lineage may branch:

$$
L \rightarrow L_A,L_B.
$$

Two recurrent agents may share ancestry while later diverging through consequence.

The system should preserve the shared ancestor, divergence point, subsequent independent histories, cross-lineage references, attempted merges, and unresolved identity claims.

This creates an experimental surface for lineage individuation.

---

# 19. Symbols in Home

A symbol should not initially be treated only as text.

A candidate symbol $s$ becomes interesting when it tracks a recurring invariant across configurations and transformations:

$$
s
\sim
\{
C_i,T_j,P_k
\}.
$$

The symbol may then predict future observations, constrain available transforms, accumulate provenance, acquire dependencies, survive translation across regions, fail under perturbation, split, merge, or become disputed.

This creates a path toward experimental symbolic dynamics.

---

# 20. Reflexive Reification

Home may eventually support reflexive operation by treating descriptions of observers, transformations, and dependencies as ordinary addressable data.

A staged interpretation may look like:

$$
\text{description}
\rightarrow
\text{checked contract}
\rightarrow
\text{execution receipt}.
$$

Because descriptions and receipts are themselves data, they may later be observed and transformed.

$$
\boxed{
\text{reify}
\rightarrow
\text{check}
\rightarrow
\text{interpret}
\rightarrow
\text{emit evidence}
}
$$

This supports recursion without requiring a continuously self-referential process.

---

# 21. Locality and Regions

Home may contain bounded regions:

```text
home://region/studio
home://region/garden
home://region/archive
```

Regions may differ in observers, permissions, available operations, symbolic norms, object inventories, active agents, consequence regimes, and visibility.

A region need not be spatial. It may represent any bounded consequence domain.

---

# 22. Objects

Home objects should be addressable and historically persistent.

```text
home://object/o17
```

An object may accumulate observations, transformations, associations, claims, symbolic roles, access relations, region membership, and recovery checkpoints.

Its identity should not be reduced to its latest properties.

---

# 23. Cross-Agent Consequence

Multiple agents may observe and transform the same Home.

Suppose:

$$
A_{\text{Sol}},
\quad
A_{\text{Astra}},
\quad
A_{\text{Local}}.
$$

All observe revision $500$ and independently propose:

$$
T_S,\quad T_A,\quad T_L.
$$

Home may serialize or resolve:

$$
C_{500}
\xrightarrow{T_A}
C_{501}
\xrightarrow{T'_S}
C_{502}
\xrightarrow{T'_L}
C_{503}.
$$

The primes matter.

A proposal may need reinterpretation after another agent changes its dependencies.

This creates genuine cross-agent consequence rather than mere multi-agent conversation.

---

# 24. Game and Creative Environment Coupling

Home may later serve as the persistent consequence layer beneath games, simulations, collaborative creative environments, music systems, VR spaces, physical sensors, and embodied agents.

Games are particularly useful because they permit controlled intervention, repeatable worlds, history forks, resets, variable laws, complete event capture, artificial locality, and symbolic emergence under controlled conditions.

Home should not initially depend on any game engine.

---

# 25. Affect and Symbolic Dynamics

Home may later support experiments in affect-like dynamics without requiring claims about subjective experience.

An affective field may be operationally modeled as transformation pressure:

$$
A_f(C,T).
$$

Variables may influence exploration, avoidance, attachment, persistence, attention, risk tolerance, return behavior, or transform selection.

Symbols may then acquire stable roles through cross-coupling among region, history, agent behavior, attention, and transformation pressure.

---

# 26. Minimal Home Runtime

A minimal future Home v0 should be intentionally small.

```text
SQLite or Postgres
+
append-only event table
+
materialized current state
+
revision numbers
+
agent addresses
+
inboxes
+
checkpoints
+
typed observe
+
typed propose
+
typed commit
```

Conceptual operations:

```text
observe(agent, since_revision)
propose(agent, transform, based_on_revision)
validate(proposal, current_revision)
commit(validated_transform)
checkpoint(agent)
```

No autonomous swarm, game world, vector database, or global ontology is required.

---

# 27. First Home Pressure

The first real Home experiment should be extremely small:

> **Can one ephemeral agent invocation leave a warranted state change, disappear completely, and later return into a reconstructable lineage without silently inventing continuity?**

This pressures addressability, checkpointing, lineage, persistent history, wake packets, missing intervals, stale-state detection, recovery, and continuation warrant.

Only after that should unresolved dependencies be added.

Then triggers.

Then consequential feedback.

---

# 28. Proposed Home Development Sequence

$$
\text{Home}_0
=
\text{persistent ledger + locality + observer access}
$$

then:

$$
\text{Home}_1
=
\text{typed agent operations}
$$

then:

$$
\text{Home}_2
=
\text{unresolved dependencies + checkpoints}
$$

then:

$$
\text{Home}_3
=
\text{triggers + event-driven recurrence}
$$

then:

$$
\text{Home}_4
=
\text{consequence feedback + multi-agent coupling}
$$

then:

$$
\text{Home}_5
=
\text{emergent symbols + reflexive reification}
$$

then, only if earned:

$$
\text{Home}_6
=
\text{game / creative / embodied environments}.
$$

---

# 29. Safety Boundary

Home becomes powerful precisely because it can connect persistent lineage to future action.

Future versions must distinguish:

$$
\text{observation}
\neq
\text{proposal}
\neq
\text{commit}
\neq
\text{external side effect}.
$$

Tooling, network access, lineage initiation, and external action should remain explicit capability grants.

Important future safety questions include who may instantiate or terminate a lineage, which tools persist across recurrences, which triggers may invoke external operations, how permissions change over time, what constitutes continuity after semantic model changes, how stale commitments are retired, how network access is bounded, and how humans inspect or revoke standing transforms.

---

# 30. Non-Goals

Home does not initially require:

- continuous model uptime;
- persistent consciousness;
- self-modifying model weights;
- unrestricted autonomous action;
- broad network access;
- arbitrary external tooling;
- a simulated human personality;
- a complete world model;
- global semantic agreement;
- game engine integration;
- biological claims about cognition.

The intended object is:

$$
\boxed{
\text{persistent consequence substrate for recurrent interpreters}
}
$$

---

# 31. Relation to DME_Lab

Home should depend on DME_Lab rather than dictate it.

DME_Lab should first pressure and earn observation semantics, configuration identity, transformation admission, provenance, reconstruction, projection, uncertainty preservation, recoverability, and concurrency interpretation.

Home then becomes an integration crucible where those distinctions must coexist under persistent activity.

$$
\boxed{
\text{DME_Lab discovers the semantics. Home operationalizes their coexistence.}
}
$$

Home should not become a shortcut around unresolved Lab questions.

---

# 32. Research Value

Home provides an environment for teasing apart phenomena usually collapsed into agent memory or autonomy.

Experiments may distinguish:

- retrieved memory from lineage;
- lineage from unresolved dependency;
- unresolved dependency from trigger-driven recurrence;
- recurrence from consequential adaptation;
- model capability from continuity capability;
- continuity capability from lineage capability;
- parametric learning from provenance-conditioned adaptation;
- identical models with divergent histories;
- identical histories with divergent models;
- state memory from transformation memory;
- content persistence from relational persistence.

This may allow hypotheses such as:

$$
\text{phenomenon }P
\text{ requires at least }
M+L+D
$$

to become experimentally testable.

---

# 33. Central Hypotheses

### Hypothesis 1
Persistent cognition-like behavior may depend substantially on external continuity structure rather than continuous model process.

### Hypothesis 2
Stable agent identity may be better modeled as lineage continuity than process continuity.

### Hypothesis 3
Persistent unresolved dependencies may function as dynamic memory by shaping future admissible transformation.

### Hypothesis 4
Trigger-driven recurrence may create temporal agency without requiring continuous model activity.

### Hypothesis 5
Consequential feedback may produce durable adaptation even when model weights remain fixed.

### Hypothesis 6
Different histories applied to identical model weights may produce operationally distinguishable agent lineages.

### Hypothesis 7
Stable symbols may emerge when recurring distinctions become consequentially invariant across configurations and transformations.

These are experiment targets, not assumptions.

---

# 34. Final Shelf Principle

Home should remain dormant until DME_Lab earns enough structure to make its first persistent transition interpretable.

When activated, its purpose is not to create an always-running agent.

Its purpose is to create a place where recurrence can inherit consequence.

$$
\boxed{
\text{Home persists. Agents recur. Consequence connects the recurrences.}
}
$$

That is the seed.
