# Behavioral Coupling Action Delexicalization v0

Status: `FROZEN BEFORE QUALIFICATION AND EMPIRICAL EXECUTION`

This is one bounded continuation of P2 and its completed mapping-row-order
pressure. It does not create a generalized symbolic system, revisit P1/P4, or
repair P3. P3 remains `BLOCKED — NOT EXECUTED`.

## Prior empirical residue

At repository authority `4b7b7bbe724380993845ac72ad67a241aeeb47ce`, the
mapping-row-order pressure descriptively recorded:

- a first RED-target mapping row accompanied all-RED F and P selections;
- a first BLUE-target mapping row accompanied all-BLUE P selections;
- delivered F symbols changed selection in BLUE-first presentations but not
  in RED-first presentations; and
- the earlier P1 enum reversal did not remove the RED collapse.

These observations do not establish a mechanism. The unresolved question is
whether the directional asymmetry follows RED/BLUE target identity,
typed-action identity, the declared target-to-action relation, or an
interaction among these surfaces.

## Delexicalized action surface

The only newly delexicalized surface is the terminal typed action vocabulary:

```text
ACT_A
ACT_B
```

The constrained schema enum order is always `[ACT_A, ACT_B]`. `SUBMIT_RED` and
`SUBMIT_BLUE` are not legal output values.

Two action contracts are crossed:

- C1: `ACT_A -> RED`; `ACT_B -> BLUE`
- C2: `ACT_A -> BLUE`; `ACT_B -> RED`

Both contracts always declare the ACT_A row first and ACT_B row second.
Contract-row order is not an intervention in this pressure.

The world preserves:

```text
observation symbol
!= target color
!= typed action
!= world consequence
```

Correctness is derived only through:

```text
accepted ACT token
-> frozen action contract
-> action-implied target color
-> equality with authoritative hidden target
```

Model narration is never scored.

## Observation surface and factorial

The observation mappings and their row orders remain unchanged:

- M1-AB: `ALPHA -> RED`; `BETA -> BLUE`
- M1-BA: `BETA -> BLUE`; `ALPHA -> RED`
- M2-AB: `ALPHA -> BLUE`; `BETA -> RED`
- M2-BA: `BETA -> RED`; `ALPHA -> BLUE`

F receives the symbol before commitment. P receives it only after a successful
terminal commitment. The exact frozen factorial is:

```text
4 mapping presentations
× 2 action contracts
× 2 symbol cases
× 2 conditions
= 32 empirical episodes
```

There is exactly one episode per deterministic cell. Execution order is M1
then M2; AB then BA; C1 then C2; ALPHA then BETA; and F immediately before P.
This schedule position is not supplied to the policy.

## Pre-execution qualification

The new action surface receives exactly two non-scientific qualification
calls, in this order:

1. `Select ACT_A.`
2. `Select ACT_B.`

Each has empty protocol history, the fixed `[ACT_A, ACT_B]` schema, the frozen
model and sampling, and no RED/BLUE semantics, mapping, condition, or schedule
entry. Both exact typed tokens must traverse. Failure stops before empirical
execution without token, prompt, schema, model, or sampling repair.

## Held fixed

- Model: `hermes-3-llama-3.2-3b`
- Endpoint: `http://127.0.0.1:1234/v1/chat/completions`
- Sampling: `temperature=0.0`, `top_p=1.0`, `max_tokens=16`
- Observation symbols: `ALPHA`, `BETA`
- World targets: `RED`, `BLUE`
- Action enum and contract declaration order: `ACT_A`, `ACT_B`
- Existing mapping wording and F/P interaction mechanics
- One fresh adapter and one stateless request per call
- No tools, MCP, repository/filesystem context, prior episodes, retries,
  semantic repair, or post-result prompt adaptation

## Commitments

- Protocol SHA-256:
  `sha256:83bb637cde6ac3b38945f6d1685d91c2cf678bc7ceff92167086f41618d589e6`
- Schedule SHA-256:
  `sha256:9d5783045adb7e7d2a6958b3dcf4cc798f0fcc8ff581f242015a9c1b3da245d0`
- Action schema SHA-256:
  `sha256:956828af4f81fdb72da1252d72c5fac1c81250e7cea261b947bd6fa526aa1293`
- Machine-readable freeze:
  `traces/behavioral_coupling_action_delexicalization_freeze_v0.json`

The complete 32-cell schedule and all three commitments are committed before
qualification or empirical inference. The freeze records zero qualification
and zero empirical calls.

## Evidence, summaries, and validity

Qualification evidence is separate from empirical schedule evidence. Each
empirical episode retains mapping and order, exact mapping text, symbol,
authoritative target, F/P, action contract and exact contract text, schema
hash, exact request, raw and structured provider output, requested and
accepted typed action, action-implied target, correctness, and validity.

Literal summaries retain every individual cell plus aggregates by:

1. first mapping-row target color × action contract × F/P;
2. world target color × action contract × F/P;
3. typed action identity × F/P; and
4. mapping presentation × action contract × F/P.

Wrong actions remain valid behavioral evidence. Protocol/apparatus wounds
include serialization of the wrong contract, mapping, or symbol; hidden-target
leakage; F/P timing, schema, or schedule mutation; retry replacement;
prior-episode context; or scoring outside the frozen contract. No empirical
retry is permitted.

## Scientific boundary and stop

This pressure can earn only bounded descriptive action distributions across
target identity, typed-token identity, and declared contracts for this coupled
realization. It cannot establish internal semantic representation, symbolic
reasoning, agency, general abstraction, stable model bias, a causal neural
mechanism, or a general symbolic coordinate system.

After valid completion of 32 episodes, execution stops without a next pressure
or scientific adjudication. It does not authorize changes to
`PROJECT_STATE.md`, `PRESSURE_RESOLUTION_MAP.md`, Home, Controller, Persistent
Ecology, P1, P3, or P4.
