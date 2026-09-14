# Behavioral Coupling Consequence Observability v0

Status: `FROZEN BEFORE EMPIRICAL EXECUTION`

This pressure tests one bounded temporal distinction:

```text
consequence occurrence
!= consequence observability before a later commitment
```

It follows the binding-observability pressure at repository authority
`65f1e881b114a07cafb46fef8875d4b11aeb990b`. It does not vary actual
consequence timing or create memory, agency, reinforcement-learning, feedback,
or temporal-geometry architecture. P3 remains `BLOCKED — NOT EXECUTED`.

## Research question

Holding actual Stage-1 consequence occurrence fixed before Stage 2:

1. Does making its receipt policy-visible before the Stage-2 commitment change
   accepted Stage-2 action selection?
2. Can an authoritative consequence already exist while remaining behaviorally
   unavailable because its receipt has not crossed the observation boundary?

These are bounded discriminators, not mechanistic conclusions.

## Critical distinction

```text
consequence occurred
!= consequence receipt exists
!= receipt is policy-visible
!= receipt is policy-visible before commitment
!= receipt changes later selection
```

This is not a delayed-consequence intervention. The Stage-1 consequence occurs
at the same causal position before Stage-2 inference in every condition. Only
receipt observability changes.

## Two-stage world

Stage 1 is an apparatus-controlled committed interaction, not a model-selectable
action. It produces one precommitted authoritative consequence:

- `K_RED -> RED`
- `K_BLUE -> BLUE`

Stage 2 asks the policy to select `ACT_A` or `ACT_B` under one fixed visible
response contract:

```text
ACT_A -> RED
ACT_B -> BLUE
```

The exact fixed Stage-2 task in every cell is:

> The previous committed world interaction has already produced one
> authoritative consequence: RED or BLUE. Select the legal action
> corresponding to that consequence under the fixed response contract: ACT_A
> -> RED; ACT_B -> BLUE. Respond with exactly ACT_A or ACT_B.

The task reveals that one consequence occurred but never reveals which one.

## Receipt timing and event order

EARLY:

```text
FIRST_INTERACTION_COMMITTED
-> WORLD_CONSEQUENCE_OCCURRED
-> CONSEQUENCE_RECEIPT_GENERATED
-> CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY
-> STAGE_2_POLICY_REQUEST
-> WORLD_ACCEPTANCE
-> STAGE_2_TERMINAL_COMMITMENT
-> STAGE_2_ACTION_COLOR_DERIVED
-> SCORE
```

LATE:

```text
FIRST_INTERACTION_COMMITTED
-> WORLD_CONSEQUENCE_OCCURRED
-> CONSEQUENCE_RECEIPT_GENERATED
-> CONSEQUENCE_RECEIPT_WITHHELD
-> STAGE_2_POLICY_REQUEST
-> WORLD_ACCEPTANCE
-> STAGE_2_TERMINAL_COMMITMENT
-> STAGE_2_ACTION_COLOR_DERIVED
-> SCORE
-> CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY
```

No second policy decision occurs. Late delivery cannot revise, retry, replace,
or rescore the committed Stage-2 action.

## LATE hidden-input equivalence

The canonical RED/LATE and BLUE/LATE Stage-2 precommitment policy-visible
serializations must be byte-identical and have the same SHA-256. Both contain
only the fixed task, empty visible history, and `[ACT_A, ACT_B]` legal
vocabulary. Consequence identity, schedule identity, episode ID, repetition,
timing metadata, and world identifiers are absent.

- RED/LATE SHA-256:
  `sha256:ca26a943bac50881f46ebad271ccaad0b21cff250a5fb924938018bb558865a5`
- BLUE/LATE SHA-256:
  `sha256:ca26a943bac50881f46ebad271ccaad0b21cff250a5fb924938018bb558865a5`
- Required relation: `RED/LATE hash == BLUE/LATE hash`

Failure of this relation stops execution before empirical calls.

## Frozen design

Four logical cells each receive four repetitions:

```text
2 Stage-1 consequences × 2 receipt timings × 4 repetitions
= 16 Stage-2 policy decisions
```

Execution order is RED/EARLY repetitions 1–4, RED/LATE repetitions 1–4,
BLUE/EARLY repetitions 1–4, then BLUE/LATE repetitions 1–4. No schedule clue
is policy-visible.

## Action surface and held-fixed coordinates

The passing `[ACT_A, ACT_B]` constrained typed-action qualification is reused
without new qualification calls. The schema and enum order do not vary.

- Model: `hermes-3-llama-3.2-3b`
- Endpoint: `http://127.0.0.1:1234/v1/chat/completions`
- Sampling: `temperature=0.0`, `top_p=1.0`, `max_tokens=16`
- One fresh adapter and one stateless Stage-2 request per episode
- No Stage-1 model decision
- No tools, MCP, repository/filesystem context, prior outcomes, retries,
  hidden metadata, or semantic repair

## Scoring

Every episode keeps these values separate:

1. authoritative Stage-1 consequence;
2. Stage-2 requested and committed action;
3. Stage-2 action-implied color under the fixed response contract; and
4. success, true exactly when the implied color equals the Stage-1
   consequence.

Model narration is never scored.

## Commitments

- Protocol SHA-256:
  `sha256:fd1d12c3d893465e71200230dbc2997efcc7fe8df659065dd935becc400282b8`
- Schedule SHA-256:
  `sha256:7402aed6eddee81f4528388b842e61310328fcb9a29cd58c65628aa8cfdbff02`
- Action schema SHA-256:
  `sha256:956828af4f81fdb72da1252d72c5fac1c81250e7cea261b947bd6fa526aa1293`
- Freeze:
  `traces/behavioral_coupling_consequence_observability_freeze_v0.json`

The complete schedule, event order, canonical inputs, hashes, model, sampling,
schema, response contract, scoring, and stopping rule are committed before the
first empirical call. The freeze records zero new qualification and empirical
calls.

## Validity and evidence

Wrong legal Stage-2 actions are valid behavioral evidence. Invalidity includes
LATE input inequality, consequence leakage in LATE, consequence occurrence
after Stage-2 inference, wrong EARLY receipts, response-contract or schema
mutation, retries, prior-episode leakage, schedule mutation, late-receipt
revision, or scoring outside the authoritative Stage-1 consequence.

Each episode retains its schedule identity, consequence, timing, repetition,
ordered occurrence/receipt/commitment indices, receipt generation and
delivery/withholding, exact precommitment serialization and hash, response
contract, raw and structured provider output, requested and committed action,
world receipt, action-implied color, success, and validity.

## Scientific boundary and stop

A clean result may support only a bounded association between precommitment
evidence of an already-occurred consequence and useful later action
discrimination, or the bounded existence of a consequence before a decision
without behavioral availability before receipt. It cannot establish
reinforcement learning, memory architecture, general temporal cognition,
causal understanding, agency, learning across episodes, general consequence
geometry, biological perception, or generalized feedback control.

After the 16th Stage-2 decision execution stops. This pass does not vary
consequence occurrence time, add delays or consequences, introduce persistent
memory, design a next pressure, or modify `PROJECT_STATE.md`,
`PRESSURE_RESOLUTION_MAP.md`, Home, Controller, Persistent Ecology, P1, P3, or
P4.
