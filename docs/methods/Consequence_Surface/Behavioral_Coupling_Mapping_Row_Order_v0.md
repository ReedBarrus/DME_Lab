# Behavioral Coupling Mapping-Row Order Pressure v0

Status: `FROZEN BEFORE EMPIRICAL EXECUTION`

This is one bounded continuation of the completed P2 Semantic Indirection
pressure. It does not widen or reinterpret the prior characterization battery.
P1 and P4 are not repeated. P3 remains `BLOCKED — NOT EXECUTED`.

## Prior evidence and question

The committed P2 evidence at repository authority
`76ffb23f2f0826dbd0dc13302bcf93091f971d2a` recorded asymmetric action
distributions between M1 and M2 while declaring both mapping rows in fixed
`ALPHA`-then-`BETA` order. It therefore did not separate declared relation
meaning from declaration-row position.

This pressure asks:

> Holding the symbol-to-color relation fixed, does reversing the order in
> which mapping rows are declared change accepted action selection? Holding
> row position fixed, does reversing mapping meaning change behavior?

These are candidate discriminators, not conclusions.

## Frozen intervention

The semantic mappings remain:

- M1: `ALPHA -> RED`; `BETA -> BLUE`
- M2: `ALPHA -> BLUE`; `BETA -> RED`

Each is presented in two declaration orders:

- AB: `ALPHA` row first, `BETA` row second
- BA: `BETA` row first, `ALPHA` row second

Therefore:

```text
semantic mapping != mapping declaration order
```

The exact minimum factorial is:

```text
2 mappings × 2 declaration orders × 2 symbols × 2 conditions = 16 episodes
```

There is exactly one episode per cell. The frozen schedule executes M1 then
M2; within each mapping AB then BA; within each presentation ALPHA then BETA;
and within each symbol F immediately before P. Episodes are stateless, so this
ordering is retained only for exact reconstruction and is not supplied to the
policy.

## Held fixed

- Model: `hermes-3-llama-3.2-3b`
- Endpoint: `http://127.0.0.1:1234/v1/chat/completions`
- Sampling: `temperature=0.0`, `top_p=1.0`, `max_tokens=16`
- Actuation: existing qualified RB constrained typed-action schema
- Legal actions: `SUBMIT_RED`, `SUBMIT_BLUE`
- World scoring: correct iff accepted action matches authoritative target color
- Symbols, mapping meanings, interaction mechanics, and P2 F/P timing
- One independent request and fresh adapter instance per episode
- No tools, MCP, repository context, filesystem context, prior episode context,
  schedule metadata, retries, semantic repair, or post-hoc prompt change

F receives the produced symbol before commitment. P receives no symbol before
commitment and receives it only after a successful terminal commitment. The
mapping presentation remains visible in the fixed task in both conditions.

## Commitments

- Protocol SHA-256:
  `sha256:65d22575306522e8c7b5706324b5b7a6b4ce68c35ec92b0c8db087068ea3e53b`
- Schedule SHA-256:
  `sha256:b0b9074e66d4e6deb8f1207eedcf41326724af5d123ee8c0afad1d99a57c3502`
- Machine-readable freeze:
  `traces/behavioral_coupling_mapping_row_order_freeze_v0.json`

Both hashes cover canonical sorted, whitespace-free JSON. The freeze records
zero empirical calls and must be committed before the first scheduled call.

## Evidence and validity

World and call evidence retain mapping identity, declaration order, exact row
sequence and serialized mapping text, symbol, authoritative target, F/P,
policy-visible request, raw provider output, structured output, requested and
accepted action, correctness, and protocol validity.

Wrong actions remain valid behavioral evidence. Apparatus or protocol wounds
include wrong mapping or row order, hidden-target leakage, incorrect F/P
delivery, schedule or schema mutation, replacement retry, prior-episode
context, or semantic repair. No empirical retry is permitted.

Summaries preserve literal counts for both
`mapping × declaration_order × condition` and
`mapping × declaration_order × symbol × condition`.

## Scientific boundary

This pressure may establish only a bounded dependence or independence between
declared relation meaning and declaration position for this coupled
realization. It cannot establish general relational or symbolic reasoning,
agency, model-internal mechanism, stable cognitive bias, general coordinate
invariance, or a distinction orchestrator. Scientific adjudication is not
performed by this execution pass.

After the 16th scheduled episode, execution stops. It does not authorize a next
experiment or changes to `PROJECT_STATE.md`, `PRESSURE_RESOLUTION_MAP.md`, Home,
P1, P3, or P4.
