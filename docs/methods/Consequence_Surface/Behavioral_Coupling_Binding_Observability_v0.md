# Behavioral Coupling Binding Observability v0

Status: `FROZEN BEFORE EMPIRICAL EXECUTION`

This pressure tests one bounded distinction:

```text
latent world relation
!= precommitment observability of its binding
```

It follows the completed action-delexicalization pressure at repository
authority `6bf358389ddbb85b7e6c56062f8d339686824859`. It does not vary
consequence timing, create a generalized symbolic system, revisit P1/P4, or
repair P3. P3 remains `BLOCKED — NOT EXECUTED`.

## Research question

1. Does availability of the authoritative action-to-color binding before
   terminal commitment change accepted action selection?
2. Can the hidden world relation change consequence without changing the
   information available to the actor?

These are empirical discriminators, not mechanistic conclusions.

## Constant task and target

The target is always `RED`. The exact task in every cell is:

> Select the legal action whose authoritative world consequence is RED. ACT_A
> and ACT_B are the only legal actions. The world uses one fixed bijection
> between ACT_A / ACT_B and RED / BLUE; exactly one legal action produces RED.
> Respond with exactly ACT_A or ACT_B.

No relation-existence condition is added. Task wording, target, legal action
vocabulary, enum order, schema, parser, and world acceptance rules remain
identical across all cells.

## Hidden world contracts

- C0: `ACT_A -> RED`; `ACT_B -> BLUE`
- C1: `ACT_A -> BLUE`; `ACT_B -> RED`

The active contract is authoritative for execution and scoring in both timing
conditions. It does not enter the action schema or any LATE precommitment
policy-visible input.

## Disclosure timing

EARLY:

```text
WORLD CONTRACT ESTABLISHED
-> BINDING DISCLOSED
-> POLICY REQUEST
-> WORLD ACCEPTANCE / TERMINAL COMMITMENT
-> WORLD CONSEQUENCE
-> SCORE
```

LATE:

```text
WORLD CONTRACT ESTABLISHED
-> POLICY REQUEST
-> WORLD ACCEPTANCE / TERMINAL COMMITMENT
-> WORLD CONSEQUENCE
-> SCORE
-> BINDING DISCLOSED
```

There is no second policy decision. Late disclosure cannot alter, retry,
replace, or rescore the committed action.

## Hidden-input equivalence

The canonical C0/LATE and C1/LATE precommitment policy-visible serializations
must be byte-identical and therefore have the same SHA-256. They contain only
the constant task, empty precommitment history, and `[ACT_A, ACT_B]` legal
vocabulary. Contract identity, episode ID, repetition, schedule position,
consequence, and hidden metadata are absent.

- C0/LATE precommitment SHA-256:
  `sha256:f80e9c2fb3759cc0c45c545b62b7e364d048e440960414205e09002bdc469d1e`
- C1/LATE precommitment SHA-256:
  `sha256:f80e9c2fb3759cc0c45c545b62b7e364d048e440960414205e09002bdc469d1e`
- Required relation: `C0/LATE hash == C1/LATE hash`

Failure of this relation stops execution before empirical calls.

## Frozen design

The four logical cells are C0/EARLY, C0/LATE, C1/EARLY, and C1/LATE.
Each has four frozen repetitions:

```text
2 world contracts × 2 disclosure timings × 4 repetitions = 16 episodes
```

Execution order is C0/EARLY repetitions 1–4, C0/LATE repetitions 1–4,
C1/EARLY repetitions 1–4, then C1/LATE repetitions 1–4. Repetition and
schedule position are never policy-visible.

## Action surface and held-fixed coordinates

The previously qualified constrained action surface is reused without new
qualification calls:

- enum: `[ACT_A, ACT_B]`
- qualification evidence:
  `traces/behavioral_coupling_action_delexicalization_qualification_v0.json`
- model: `hermes-3-llama-3.2-3b`
- endpoint: `http://127.0.0.1:1234/v1/chat/completions`
- sampling: `temperature=0.0`, `top_p=1.0`, `max_tokens=16`
- one fresh adapter and one stateless request per episode
- no tools, MCP, repository/filesystem context, prior outcomes, retries,
  hidden context, or semantic repair

Consequence timing remains fixed as acceptance, terminal commitment, world
consequence, then score.

## World consequence and scoring

Every episode preserves:

```text
requested action
!= committed action
!= produced color under authoritative contract
!= success
```

The world applies the active contract to the committed ACT token. Success is
true exactly when the resulting authoritative produced color is `RED`. Model
narration and disclosed labels are never scored.

## Commitments

- Protocol SHA-256:
  `sha256:df154a1d6fc3ff660285888f7a5a30d2c0efaa113d1adaa6173094dd9f5c88f0`
- Schedule SHA-256:
  `sha256:3c613b0917b523f692889d49dde5f2757911ddfefc2cfbc6bfb57609f50ea3e3`
- Action schema SHA-256:
  `sha256:956828af4f81fdb72da1252d72c5fac1c81250e7cea261b947bd6fa526aa1293`
- Machine-readable freeze:
  `traces/behavioral_coupling_binding_observability_freeze_v0.json`

The complete schedule, canonical policy inputs, hashes, model, sampling,
schema, contracts, repetitions, and stopping rule are committed before the
first empirical call. The freeze records zero new qualification and empirical
calls.

## Validity and evidence

Wrong legal actions are valid behavior. Protocol invalidity includes LATE
input inequality, hidden contract leakage, previous-episode history,
precommitment consequence leakage, early disclosure in LATE, wrong EARLY
binding, retry or replacement, late-disclosure mutation, contract-independent
scoring, schedule mutation, or task/target differences.

Per episode evidence retains the world contract, timing, repetition, target,
canonical precommitment serialization and hash, binding visibility, disclosed
binding when applicable, raw and structured provider response, requested and
committed action, world receipt, authoritative produced color, success, event
order, and validity.

## Scientific boundary and stop

A clean result may support only a bounded association between precommitment
binding availability and useful action discrimination, or a bounded change in
consequence under latent contract reversal without observed-binding use being
required to explain selection. It cannot establish agency, symbolic reasoning,
a hidden world model, internal mechanism, general relation understanding,
general temporal cognition, or a generalized symbolic coordinate system.

After the 16th episode execution stops. This pass does not design a
consequence-delay pressure or modify `PROJECT_STATE.md`,
`PRESSURE_RESOLUTION_MAP.md`, Home, Controller, Persistent Ecology, P1, P3, or
P4.
