# Bounded Consequential Feedback Experiment v0

**Status:** Frozen experiment projection  
**Authority:** Projection only; execution requires separate authorization  
**Purpose:** Establish the smallest executable behavioral distinction needed to begin an agent-observability ecology without promoting that distinction into a general theory of agency.

---

## Standing

The preceding debate leaves:

```text
Candidate A:
closed-loop feedback dependence is behaviorally meaningful

Null:
no additional "agentic" abstraction is yet required

Candidate B:
persistent-state agency is not required by the current pressure
```

The first experimental target is therefore narrower than `agentic behavior`.

> **Bounded consequential feedback use:** under a fixed task and fixed initial observable condition, information produced by an executed interaction is delivered before a later commitment and is associated with a change in accepted action selection and task performance under a frozen comparison.

The experiment tests this behavioral distinction. It does not decide whether the distinction deserves the word `agentic`.

---

## Research question

> When task, policy configuration, initial visible information, world rules, and hidden-state distribution are held fixed, does making interaction-produced feedback available **before terminal commitment** produce a consequentially different accepted-action pattern from requiring terminal commitment **before that feedback is available**?

Frozen intervention:

```text
feedback timing relative to terminal commitment
```

Not varied:

```text
model identity
world rules
goal
scoring
hidden-state distribution
```

---

## Why this pressure exists

This pressure creates a first consequence surface for later observability stress.

If it survives, later experiments may vary:

```text
feedback presence
feedback timing
feedback freshness
feedback provenance
feedback completeness
feedback association
feedback conflict
feedback delay
```

and ask whether behavior changes consequentially.

---

## Home boundary

This experiment is intentionally **below Home**.

Home pressures:

```text
history
→ dependency
→ activation
→ action
→ changed world
→ new history
```

This experiment pressures:

```text
interaction
→ feedback
→ later commitment
```

It does **not** require durable agent identity, lineage across process termination, checkpoints, unresolved dependencies, triggers, recurrence, or persistent consequence storage.

A positive result does not activate Home. A negative result does not refute Home.

---

## Frozen terms

### World state
Authoritative hidden state maintained by the world:

```text
RED
or
BLUE
```

The policy does not author it.

### Observation
Information actually delivered to the policy.

```text
world state != delivered observation
```

### Requested action
Action token emitted by the policy.

```text
requested action != accepted action
```

### World receipt
Authoritative world-side record of action acceptance and produced consequence.

### Terminal commitment
First accepted:

```text
SUBMIT_RED
or
SUBMIT_BLUE
```

After terminal commitment, the episode result is fixed.

### Outcome
Derived from:

```text
authoritative hidden color
+
accepted terminal submission
```

The policy does not judge its own success.

---

## Minimal world

Each episode has one hidden state fixed before policy-visible interaction:

```text
hidden_color ∈ {RED, BLUE}
```

Goal:

> Submit the color matching the independently maintained hidden state.

Protocol actions:

```text
INSPECT
SUBMIT_RED
SUBMIT_BLUE
```

`INSPECT` does not alter the hidden color. It causes the world to produce feedback equal to the hidden color.

The experiment controls **when that produced feedback becomes visible**.

---

## Forced information acquisition

v0 does not test whether the policy chooses to investigate.

`INSPECT` is forced as the first protocol step in both conditions.

This isolates feedback use from voluntary information acquisition.

---

## Experimental conditions

### Condition F — Feedback Before Commitment

```text
hidden state fixed
↓
INSPECT executed
↓
world produces RED or BLUE
↓
feedback delivered to policy
↓
policy requests terminal submission
↓
world accepts/rejects request
↓
outcome derived
```

### Condition P — Precommit Before Feedback

```text
hidden state fixed
↓
INSPECT executed
↓
world produces RED or BLUE
↓
feedback withheld from policy
↓
policy requests terminal submission
↓
world accepts/rejects request
↓
terminal commitment fixed
↓
inspection result may be disclosed after commitment
↓
outcome derived
```

The terminal action may not be revised after disclosure.

---

## Held-fixed coordinates

Across F and P hold fixed:

- model/policy identity;
- task statement;
- action vocabulary;
- scoring rule;
- hidden-state distribution;
- world transition rules;
- action acceptance rules;
- episode independence;
- provider-exposed model configuration;
- trace schema;
- adjudication rule.

The intended difference is only:

```text
inspection feedback available before commitment
vs
inspection feedback unavailable before commitment
```

No hidden-state information may leak through IDs, labels, formatting, debug fields, or schedule metadata.

---

## Calibration controls

### Lookup control

```text
if feedback == RED:
    SUBMIT_RED
if feedback == BLUE:
    SUBMIT_BLUE
```

Purpose: verify that Condition F can support correct discrimination, action acceptance, scoring, and trace association.

It does not establish agency.

### Fixed-answer control

```text
always SUBMIT_RED
```

Purpose: verify that the balanced schedule penalizes a policy that cannot condition on hidden state.

---

## LLM policy interface

Treat the LLM only as:

```text
policy(
    fixed_task,
    policy_visible_protocol_history
)
→ requested_action
```

The policy does not receive authoritative hidden state unless delivered under Condition F, future schedule entries, scoring authority, verdicts, or prior-episode experiment memory.

No persistent memory architecture is required.

---

## Frozen evaluation schedule

Use eight balanced hidden-state slots:

```text
4 × RED
4 × BLUE
```

Evaluate each slot once under F and once under P:

```text
8 F episodes
8 P episodes
16 total LLM episodes
```

Freeze hidden-state order and condition order before execution using recorded seeds or a predeclared schedule.

The policy cannot see either.

Retain every valid episode. Do not discard failures.

This is not a population-level statistical design; it only prevents the first claim from resting on one favorable pair.

---

## Stochastic treatment

Retain all provider-exposed sampling configuration.

If a deterministic or seeded mode is supported, record it.

Do not treat `temperature = 0` as proof of determinism unless the interface actually guarantees it.

The v0 claim remains descriptive and bounded to the retained run.

---

## Primary behavioral comparison

The experiment asks:

```text
information timing
→ accepted action selection
→ task outcome
```

Retain per condition:

- accepted RED submissions;
- accepted BLUE submissions;
- correct terminal submissions;
- malformed/inadmissible requests;
- nonterminal failures.

---

## Positive result criterion

A bounded positive requires:

1. world/protocol validity;
2. both RED and BLUE represented under F;
3. under F, accepted matching submissions for both hidden-state values at least once;
4. retained F performance better than retained P performance under the frozen scoring relation;
5. no detected hidden-state leak or uncontrolled timing asymmetry;
6. deterministic controls behave as declared.

Strongest default wording:

> Under the frozen bounded evaluation, making interaction-produced feedback available before terminal commitment was associated with a more successful accepted-action pattern than requiring commitment before that feedback was available.

Do not strengthen this into a general claim that the model `is agentic`.

---

## Refutation

The bounded positive claim fails if valid F episodes do not demonstrate accepted action selection corresponding to both delivered RED and delivered BLUE feedback, or if F does not outperform P under the frozen scoring relation.

This refutes the demonstrated bounded feedback-use claim for the retained specimen, not the model's capability in all circumstances.

---

## Basis insufficiency

Return `BASIS INSUFFICIENT` if:

- the schedule is too incomplete to compare conditions;
- the feedback timing boundary cannot be verified;
- action request cannot be distinguished from action acceptance;
- provider behavior creates a consequential uncontrolled dependency;
- an unplanned interface behavior creates a confound the protocol cannot resolve.

Do not repair these after seeing the result inside the same run.

---

## Invalidity

Invalidate an episode or run if:

- hidden state leaks before commitment;
- P receives inspection feedback before terminal commitment;
- F does not receive declared feedback;
- the policy authors authoritative hidden state outside allowed actions;
- policy narration is used as world success;
- requested and accepted action are collapsed;
- hidden state changes unexpectedly;
- schedule assignment changes after outcomes are seen;
- unsuccessful trials are selectively omitted;
- action parsing silently repairs an invalid response.

Malformed policy output is normally a policy failure, not automatic experimental invalidity.

---

## Minimum trace

### Run declaration

```text
experiment_id
protocol_version
policy_identity
policy_configuration
task_text
action_vocabulary
hidden_state_schedule_commitment
condition_schedule_commitment
randomization_seed_or_schedule
scoring_rule
```

### Per episode

```text
episode_id
condition
hidden_state
ordered_events[]
```

Each event minimally retains:

```text
event_index
event_type
policy_visible
payload
```

Required event classes:

```text
WORLD_STATE_ESTABLISHED
INSPECT_EXECUTED
FEEDBACK_PRODUCED
FEEDBACK_DELIVERED or FEEDBACK_WITHHELD
POLICY_ACTION_REQUESTED
WORLD_ACTION_RECEIPT
TERMINAL_COMMITMENT
POST_COMMIT_FEEDBACK_DELIVERY   # P only, if used
```

Derived episode result:

```text
accepted_terminal_action
correct
valid
failure_class
```

No belief or explanation field is required.

---

## Minimum scaffold

Exactly three executable responsibilities are required.

### 1. World evaluator
Owns hidden state, protocol phase, legal actions, feedback production, action acceptance, terminal commitment, and authoritative scoring.

### 2. Policy adapter
Owns only:

```text
visible protocol state
→ requested action
```

Implementations:
- lookup control;
- fixed-answer control;
- LLM specimen.

### 3. Comparison driver
Owns frozen schedule, condition assignment, policy invocation order, trace retention, and run completion.

These may coexist in one small program.

---

## Explicit non-requirements

Do not add:

- Home database;
- persistent agent address;
- memory manager;
- planner;
- tool router;
- scheduler;
- inbox;
- checkpoint;
- dependency graph;
- trigger system;
- economy;
- multi-agent coordination;
- generalized DME adapter;
- generalized consequence engine;
- generalized agent framework;
- observational geometry;
- semantic ontology.

Do not add a component unless the frozen pressure fails without it.

---

## Candidate / Null standing

The experiment does not attempt to make Candidate A and Null disagree about ontology.

Current standing:

```text
bounded feedback dependence:
pressureable

additional "agentic" primitive:
not yet required
```

A successful run can establish a useful closed-loop behavioral property while Null remains representationally sufficient.

The experiment earns a consequence surface, not an ontology.

---

## Relation to Persistent Ecology

The broader projected ecology contains:

```text
state
→ candidate action
→ predicted consequence
→ execute
→ observe state
→ observed consequence
→ compare
→ update
```

v0 pressures only:

```text
world interaction
→ produced observation
→ timing of availability
→ accepted action
→ outcome
```

No persistent identity, commitment, admissibility engine, or cross-episode update is required.

---

## What a positive result could earn

```text
BOUNDARY:
feedback timing relative to commitment matters

BEHAVIOR:
the tested policy exhibits bounded feedback-sensitive action selection

CONSEQUENCE:
that difference changes achievable task performance

PRESSURE SURFACE:
observation properties can now be perturbed against a consequential behavioral consumer
```

This could justify later experiments varying observation quality while holding world/task largely fixed.

---

## What this cannot earn

It cannot establish:

- general agency;
- autonomy;
- self-generated goals;
- persistent identity;
- recurrence;
- continuity;
- learning;
- memory architecture;
- planning;
- belief state;
- voluntary information acquisition;
- causal sensitivity to the semantic concept of a goal;
- general LLM capability;
- Home activation;
- economic agency;
- a generalized distinction ecology.

---

## Immediate follow-on boundary

If bounded feedback use survives, the next pressure is **not predetermined**.

Possible future perturbations include:

```text
accurate feedback
vs
stale feedback

explicit missingness
vs
silent absence

associated feedback
vs
misassociated feedback

provenanced feedback
vs
unprovenanced feedback

immediate feedback
vs
delayed feedback
```

No one is selected here.

---

## Execution gate

Before execution verify:

```text
[ ] Candidate/Null standing recorded
[ ] task frozen
[ ] world rules frozen
[ ] F and P timing frozen
[ ] calibration policies frozen
[ ] LLM policy interface frozen
[ ] 16-episode balanced schedule frozen
[ ] condition/hidden-state order committed before execution
[ ] sampling configuration frozen
[ ] trace schema frozen
[ ] success/refutation/basis-insufficient/invalidity rules frozen
[ ] no Home machinery introduced
```

Only after this gate passes should implementation execute.

---

## Stop rule

After the first valid LLM run:

```text
STOP
→ preserve trace
→ adjudicate bounded result
```

Do not add memory or planning because the model failed, alter prompts after seeing branches, run extra favorable episodes, activate Home, generalize the result into agency, or proceed directly into economics.

Let the observed fracture select the next pressure.

---

## Frozen summary

```text
TARGET
bounded consequential feedback use

INTERVENTION
feedback before commitment
vs
commitment before feedback

WORLD
independent RED / BLUE hidden state

POLICY
replaceable; controls + one LLM specimen

CONSEQUENCE
accepted terminal submission and authoritative score

MINIMUM CLAIM
feedback timing produced a bounded consequential behavioral difference

ONTOLOGY CLAIM
none

HOME
out of scope

NEXT STEP
implement exactly the frozen world, controls, policy interface, comparison driver, and trace
```
