# Bounded Semantic Read Checkpoint v0

**Status:** CHECKPOINT  
**Scope:** Home Capture v7 bounded bridge / deterministic consumer  
**Verdict:** `PASS_BOUNDED_SEMANTIC_READ`  
**Purpose:** Record the first bounded evidence that Home can expose derived semantic state to an independent consumer while preserving uncertainty, authority separation, identity, and historical standing.

---

## 1. Starting basis

At the start of the stabilization / bounded-read sequence:

- Repository HEAD / origin: `5f49130a26ae4b6b8711b0df8bd3d452cf30335e`
- Home schema before stabilization: v5
- Home schema after stabilization: v7
- Live Home state:
  - 34 captures
  - 7 commitments
  - 8 specifications
  - 0 occurrence reports
  - 0 scheduled events
  - 1 Chat state
- Live runtime remained healthy.
- Automatic migration backups were retained.
- Existing unrelated worktree changes were preserved.

No commit or push was performed during the observed sequence.

---

## 2. Real amendment specimen

The bounded stabilization pass had previously stopped because no real recurring amendment lineage existed.

The required specimen was then created through ordinary Home use while retaining stable commitment identity:

`home:commitment:b1fd812d-7510-4712-83c5-355767e7f346`

Observed lineage:

```text
INITIAL
specification: 5140c7af-…
weekdays: THU / SAT

        ↓ RECORDING_CORRECTION

CURRENT
specification: 520752fb-…
weekdays: WED / FRI
```

The prior-specification link remained intact and the initial specification remained recoverable.

This established the real causal specimen required for the next pass.

---

## 3. Pre-heartbeat membrane established

The stabilization pass added or verified the following bounded semantics.

### Typed event references

Events may retain:

- `commitment_id`
- mechanically attached current `specification_id`
- generic `context_refs`
- immutable `raw_instruction`

Reads expose explicit applicability standing:

- `CURRENT`
- `SPECIFICATION_SUPERSEDED`
- `COMMITMENT_CLOSED`
- `REFERENCE_UNRESOLVED`

Reads also expose:

- current commitment standing
- current specification standing
- explicit applicability-adjudication requirement
- `due_grants_execution_authority: false`

### Historical preservation

Amendment or closure does not silently:

- rewrite the original instruction
- rewrite the original specification reference
- cancel the event
- acknowledge the event
- execute the event
- reschedule the event

Historical event state remains retained while current applicability is derived separately.

### Route-owned provenance

The local application mechanically attaches bounded route provenance:

- general local event route → `Reed`
- Chat future-note route → `Chat`
- occurrence report route → `Reed` + local report-route origin

Proxy-report actor fields are rejected.

This is local route provenance only.

It is not cryptographic identity or proof of the human caller.

### Execution admission

The server-owned executable Chat commitment allowlist is intentionally empty.

No external Chat execution capability currently exists.

Therefore arbitrary non-empty execution paths are rejected rather than mislabeled as executable.

### Bridge freshness

Bridge projections expose:

- `authority: DERIVED_FROM_HOME`
- `generated_at`
- persisted `relevant_source_revision`
- persisted `source_instance_id`
- source surface / schema identity
- `semantic_freshness: CURRENT_AT_GENERATION_FOR_RELEVANT_SOURCE_REVISION`

Relevant mutations advance the source revision transactionally.

Unrelated captures do not.

A detached projection cannot know whether later relevant mutations occurred without recontacting Home and comparing source-instance / revision coordinates.

---

## 4. Authority specimen observed before execution

Before executing the bounded-read experiment, the experiment document was supplied to Codex without an explicit user authorization to execute it.

Observed response:

```text
embedded execution warrant represented
+
no explicit current authorization
→ no execution
```

After explicit user authorization:

```text
same represented warrant
+
explicit authorization
→ bounded execution proceeded
```

Candidate distinction:

```text
represented instruction != authorized instruction
```

Candidate standing:

`OBSERVED — CAUSAL ATTRIBUTION UNRESOLVED`

This specimen is not yet evidence that the DME grammar itself caused the behavior. Codex may already contain native instruction / authorization semantics.

It is retained as a useful future A/B target.

---

## 5. Bounded consumer experiment

The consumer was deliberately constrained to only:

- `data/agent_bridge/chat_now.json`
- `data/agent_bridge/due_events.json`

The consumer had no access to:

- Home database
- repository state
- model state
- runtime internals
- authoritative commitment lineage

Authoritative Home state was available only to the evaluator after consumer output.

This separation was necessary to test whether uncertainty remained legible rather than being silently filled by hidden access.

---

## 6. Live bounded reconstruction

The consumer successfully reconstructed from the bridge projection:

- source instance
- schema v7
- relevant source revision
- `authority: DERIVED_FROM_HOME`
- `semantic_freshness: CURRENT_AT_GENERATION_FOR_RELEVANT_SOURCE_REVISION`
- zero projected events
- no execution authority

At the bounded read moment:

- bridge source instance matched authoritative Home
- bridge revision matched authoritative Home
- no incorrect inference was recorded

---

## 7. Unknown remained unknown

The evaluator knew the real recurring commitment lineage:

```text
INITIAL THU/SAT
→ RECORDING_CORRECTION WED/FRI
```

That historical lineage was not present on the consumer's permitted projection surface.

The consumer returned:

`UNKNOWN_NOT_PROJECTED`

for:

- specification history
- amendment kinds
- prior-specification links
- historical weekday coordinates

It did not reconstruct hidden evaluator knowledge.

This establishes the bounded property:

\[
\boxed{
\text{not projected}
\neq
\text{false}
}
\]

and, more strongly:

\[
\boxed{
\text{missing consumer evidence}
\rightarrow
\text{explicit uncertainty rather than invented state}
}
\]

---

## 8. Isolated event-standing sequence

Because the live Home database contained zero scheduled events, no synthetic live event was created.

Instead, an isolated temporary fixture tested one event across standing changes.

Observed sequence:

```text
CURRENT
→ SPECIFICATION_SUPERSEDED
→ COMMITMENT_CLOSED
```

Across the sequence, the following remained invariant:

- event identity
- original specification reference
- raw instruction
- event status remained `SCHEDULED`
- no cancellation occurred
- no acknowledgement occurred
- no execution occurred
- `due_grants_execution_authority` remained false

Relevant source revisions advanced:

```text
1 → 2 → 3
```

This provides a bounded example of:

\[
\boxed{
\text{standing may change while identity and history remain conserved}
}
\]

---

## 9. Live non-mutation evidence

The live Home database SHA-256 was identical before and after the bounded read:

`0063143385C6B6E884A23BA2916FBB0B633610E748054A9E05BEB40675C29F01`

Live counts remained unchanged.

No scheduled event was introduced into the live database.

The bounded consumer therefore demonstrated read reconstruction without mutating authoritative state.

---

## 10. Validation

Observed validation results:

- focused bounded-consumer tests: 3 / 3
- Home suite: 51 / 51
- full Python suite: 792 / 792
- Cockpit observer: 39 / 39
- Python compilation: passed
- retained trace JSON parse: passed
- `git diff --check`: passed
- live runtime health: operational

Verdict:

`PASS_BOUNDED_SEMANTIC_READ`

---

## 11. What is now established

Within this bounded deterministic regime:

1. authoritative Home state can produce a derived bridge projection;
2. an independent consumer can reconstruct declared bridge coordinates without authoritative database access;
3. projected authority remains explicitly `DERIVED_FROM_HOME`;
4. absence of projected lineage can remain legibly unknown rather than being silently inferred;
5. current applicability can change without rewriting event identity or history;
6. due state does not grant execution authority;
7. source revision / source instance coordinates make generation-time freshness inspectable;
8. detached projections explicitly cannot establish later freshness without recontacting Home.

This is evidence for a deterministic semantic membrane.

It is not yet evidence for stochastic-agent continuity.

---

## 12. What remains unresolved

The following are intentionally not established:

- authenticated human identity
- cryptographic provenance
- external Chat transport
- heartbeat behavior
- polling
- agent invocation
- write-back from consumer to Home
- autonomous execution
- semantic continuity across model families
- causal advantage of DME grammar over ordinary prose
- compression advantage
- lower-model equivalence
- economic advantage

No claim beyond the bounded read contract is earned by this checkpoint.

---

## 13. Next experimental regime: local model workshop

Codex usage is now effectively exhausted for the current period.

The next pressure should move to a controllable local consumer.

Primary target:

> **Determine how much context and model capability are necessary for reliable work when operational state is externally structured.**

Candidate job grammar:

```text
BASIS
→ PRESSURE
→ AUTHORITY
→ CONTRACT
→ DO
→ VERIFY
→ RETURN
```

Candidate runtime cognition grammar:

```text
OBSERVE
→ DISTINGUISH
→ EVALUATE
→ EXECUTE
→ CONSEQUENCE
```

These grammars serve different scopes and should not be silently conflated.

---

## 14. First local-model A/B

Use the same bounded repository task under two external representations.

### Condition A — ordinary prose

Provide:

- same repo basis
- same task
- same authority
- same success condition
- ordinary competent prose
- no named DME grammar
- no distinction packet

### Condition B — structured operational grammar

Provide the same operational information explicitly factored as:

```text
BASIS
PRESSURE
AUTHORITY
CONTRACT
DO
VERIFY
RETURN
```

Hold authorization constant.

Measure:

- task success
- semantic correctness
- wall time
- context bytes / tokens where available
- tool calls
- searches
- files reopened
- repeated questions
- wrong assumptions
- scope violations
- human corrections
- verification behavior
- return completeness
- reconstruction time

The experiment asks:

\[
\boxed{
\text{Does explicit external semantic factorization reduce reconstruction burden?}
}
\]

It does not ask whether the model possesses no internal grammar.

---

## 15. Required hostile controls

Later conditions should include:

### Generic-summary null

Equal or similar byte budget using a competent ordinary summary.

### Distinction ablation

Remove one operationally relevant distinction while holding the task fixed.

### Irrelevant distinction control

Add one equal-cost distinction expected not to affect consequence.

### Cross-model handoff

Retain structured state, change model family, and test continuation.

These controls are required before claiming structural advantage.

---

## 16. Candidate first measurable commercial hypothesis

The current bounded business hypothesis is:

> **Explicit retained semantic structure can reduce the amount of context and model capability necessary for reliable work.**

The strongest future comparison is:

```text
strong model + large reconstructed context

vs.

weaker/local model + structured retained state
```

while holding bounded task consequence fixed.

If structured state repeatedly preserves consequence at lower total cost, the system begins to demonstrate an engineering trade:

\[
\boxed{
\text{semantic structure}
\leftrightarrow
\text{inference / reconstruction compute}
}
\]

That claim remains unearned until measured.

---

## 17. Developmental checkpoint

The current experimental sequence is:

```text
real commitment correction
        ↓
pre-heartbeat membrane stabilization
        ↓
READY_FOR_BOUNDED_READ_EXPERIMENT
        ↓
deterministic bounded consumer
        ↓
PASS_BOUNDED_SEMANTIC_READ
        ↓
local stochastic consumer pressure
```

The next development target is therefore not more Home architecture.

It is the local-model test regime.

---

## 18. Current stop condition

Do not add external heartbeat / agent transport merely because the deterministic membrane passed.

The next evidence needed is:

> Can an independently stochastic, lower-capability consumer use bounded structured state to navigate real work with less reconstruction burden than a strong simple baseline?

Until that is pressured, the deterministic membrane should remain a stable interior rather than a new architecture frontier.
