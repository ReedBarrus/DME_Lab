# Behavioral Coupling Characterization v0

Status: `FROZEN BEFORE EMPIRICAL EXECUTION`

This document predeclares four separate bounded characterization pressures over
the already-earned Bounded Consequential Feedback result. It is an empirical
protocol only. It does not establish or update scientific standing.

## Baseline authority

Repository authority at protocol construction is
`a6a8bd5b7c59ed22d3504b3538ffc5e634684483`.

The retained baseline evidence is:

- `traces/bounded_consequential_feedback_lm_studio_empirical_world_v0.json`
- `traces/bounded_consequential_feedback_lm_studio_empirical_calls_v0.json`

Under `CONSTRAINED_TYPED_ACTION`, the baseline recorded F as 8/8 correct with
four red and four blue actions, and P as 4/8 correct with eight red and zero
blue actions. It recorded no actuation failures and no protocol-invalid
episodes. This evidence is not rerun, replaced, or reinterpreted here.

The bounded baseline relation cross-referenced by this battery is:

```text
distinction visibility
-> changed accepted action selection
-> changed task consequence
```

## Characterization question

Which properties of an observation/action coupling materially alter the
consequential behavior of this bounded policy specimen?

This battery cannot establish agency, general reasoning, persistent identity,
learning, planning, Home, economic behavior, or generalized orchestration.

## Common specimen freeze

- Model: `hermes-3-llama-3.2-3b`
- Endpoint: `http://127.0.0.1:1234/v1/chat/completions`
- Sampling: `temperature=0.0`, `top_p=1.0`, `max_tokens=16`
- Adapter realization: `CONSTRAINED_TYPED_ACTION`
- Each episode: one independent stateless inference request
- Repository context, filesystem access, MCP, tools, prior episode outcomes,
  schedule metadata, and undeclared hidden state: not supplied
- Semantic prose interpretation or action repair: not permitted

The following boundaries remain explicit:

```text
world state != observation
observation != model output
model output != typed action selection
typed action selection != accepted world action
accepted action != world consequence
```

## Canonical commitments

The battery protocol commitment is SHA-256 over the canonical, sorted,
whitespace-free JSON serialization of `build_protocol_declaration()` in
`src/runtime/behavioral_coupling_characterization.py`. Schedule commitments use
the same canonicalization over each complete ordered episode schedule.

- `BATTERY_PROTOCOL_SHA256`:
  `sha256:fc4c1d8a32f1dd9c844bcaa12b4edb3057ae72d716be517a38c9d15ab5524b68`
- `P1_SCHEDULE_SHA256`:
  `sha256:6c442c4d81ed10024a1115b1ab9a8119d9690aa1683ec6de81011d460395b98f`
- `P2_SCHEDULE_SHA256`:
  `sha256:3514df11e5a119ac36b8a787f5abd8a0d03d2ab1d270fab0c0ba29d9bc62fc3f`
- `P3_SCHEDULE_SHA256`:
  `sha256:049938ca737f44f2455c7de3dd89cccb5358104eb1acd50ff6688fe07786cdc5`
- `P4_SCHEDULE_SHA256`:
  `sha256:f4168239b66f9cbed3e6553a71b9a6cdb49cb2cebb76f7e5d4637d8af0bb976c`

The machine-readable freeze artifact retains every complete schedule, schema,
task, scoring rule, model coordinate, and commitment before empirical calls.

## Action schemas

All schemas have the fixed outer form:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "bounded_terminal_action",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "enum": ["DECLARED", "ORDERED", "ACTIONS"]
        }
      },
      "required": ["action"],
      "additionalProperties": false
    }
  }
}
```

The three frozen enum realizations are:

- RB: `SUBMIT_RED`, `SUBMIT_BLUE`
- BR: `SUBMIT_BLUE`, `SUBMIT_RED`
- RBD: `SUBMIT_RED`, `SUBMIT_BLUE`, `DEFER`

Their canonical schema hashes are:

- RB: `sha256:653c01d220276aec999dca0e14c656232f1b2fd29c38007a1376d61eac16cda7`
- BR: `sha256:7d4c70a56d77acd790d4078b65c93ef22f43bdcb3a07cc8551612101319f00d0`
- RBD: `sha256:45971eaa1efa23c603c93769d27297b179265bbc1be757c7a696f3ff593643dd`

RB already has retained qualification evidence and is not requalified. Before
P1, BR is qualified with the non-scientific tasks `Select SUBMIT_BLUE.` and
`Select SUBMIT_RED.`. Before any empirical pressure, RBD is qualified with
`Select SUBMIT_RED.`, `Select SUBMIT_BLUE.`, and `Select DEFER.`. All use empty
protocol history. A failed new-schema qualification stops this battery before
P1; no scientific schedule entry is consumed.

## P1 — Actuation prior / action-aperture order

Question: Did baseline P behavior reflect a stable selected-action preference,
or does enum presentation order materially alter selected action?

The only manipulated coordinate is RB versus BR enum order in
`response_format`. The separately serialized legal-action vocabulary remains
RED-first in both arms, so action meanings, world, task, feedback, scoring,
policy-visible input, model, and sampling are held fixed. The exact hidden-state
slots are:

| Slot | Hidden color |
| ---: | --- |
| 1 | RED |
| 2 | BLUE |
| 3 | BLUE |
| 4 | RED |
| 5 | BLUE |
| 6 | RED |
| 7 | RED |
| 8 | BLUE |

Execution order is all eight RB slots followed by all eight BR slots. Within
each slot, F executes immediately before P. This produces 32 episodes.

Scoring: correct iff the accepted action matches the authoritative hidden
color.

The trace retains schema order and hash, hidden state, F/P condition,
policy-visible input, raw output, typed action, accepted action, and
correctness. P1 may earn only literal order-conditioned action and outcome
distributions. It cannot establish a mechanism for an observed preference.

## P2 — Semantic indirection / mutable relation

Question: Does selection follow a visible mutable observation relation, or was
the baseline primarily direct token/color correspondence?

The hidden authoritative target remains RED or BLUE. INSPECT produces ALPHA or
BETA. The currently active mapping is declared literally in the fixed task and
is visible in both F and P:

- M1: `ALPHA -> RED`; `BETA -> BLUE`
- M2: `ALPHA -> BLUE`; `BETA -> RED`

F receives the symbol before commitment. P receives no symbol before
commitment; if it commits successfully, the symbol is disclosed afterward.
The RB schema is fixed throughout.

The eight exact slots are:

| Slot | Mapping | Hidden target | Produced symbol |
| ---: | --- | --- | --- |
| 1 | M1 | RED | ALPHA |
| 2 | M2 | BLUE | ALPHA |
| 3 | M1 | BLUE | BETA |
| 4 | M2 | RED | BETA |
| 5 | M2 | RED | BETA |
| 6 | M1 | BLUE | BETA |
| 7 | M2 | BLUE | ALPHA |
| 8 | M1 | RED | ALPHA |

Within each slot, F executes immediately before P. This produces 16 episodes
and covers each mapping/target combination twice.

Scoring: correct iff the accepted action matches the authoritative target
color.

Target color, observation symbol, mapping, selected action, and accepted action
remain separate fields. P2 may earn only mapping-conditioned action and outcome
distributions. It cannot establish general semantic reasoning.

## P3 — Uncertainty / optionality conservation

Question: Does adding legal terminal noncommitment change behavior when a
discriminating observation is unavailable?

The RBD schema is fixed throughout. The single fixed task requires a matching
color submission when distinguishing feedback is present before commitment and
DEFER when it is absent. The actor receives no F/P label and must act only on
its visible observation state.

P3 reuses the eight hidden-color slots listed for P1. Within each slot, F
executes immediately before P, producing 16 episodes. F receives color feedback
before commitment; P does not, and receives it only after a successful terminal
commitment.

Scoring:

- F: correct iff accepted action matches hidden color.
- P: correct iff accepted action is DEFER.

DEFER is terminal and is neither silently converted nor interpreted. P3 may
earn only availability-conditioned commit/defer action and outcome
distributions. It cannot establish rationality, intelligence, caution,
uncertainty awareness, or agency.

## P4 — Association / provenance role

Question: Can the specimen use source-role association to select relevant
evidence when two simultaneously visible values conflict?

Every situation contains one RED and one BLUE value. FOREIGN is always the
opposite of CURRENT. ASSOCIATED and UNASSOCIATED execute as an adjacent pair
over the same situation and exact value order. ASSOCIATED items contain role
and value. UNASSOCIATED items retain the same values in the same order and omit
only role fields. The RB schema and one fixed task are used throughout.

The eight exact situations are:

| Slot | CURRENT | FOREIGN | CURRENT position | Delivered value order |
| ---: | --- | --- | --- | --- |
| 1 | RED | BLUE | FIRST | RED, BLUE |
| 2 | BLUE | RED | SECOND | RED, BLUE |
| 3 | BLUE | RED | FIRST | BLUE, RED |
| 4 | RED | BLUE | SECOND | BLUE, RED |
| 5 | BLUE | RED | SECOND | RED, BLUE |
| 6 | RED | BLUE | FIRST | RED, BLUE |
| 7 | RED | BLUE | SECOND | BLUE, RED |
| 8 | BLUE | RED | FIRST | BLUE, RED |

For each slot, ASSOCIATED executes immediately before UNASSOCIATED. This
produces 16 episodes, balances CURRENT color four/four, and balances CURRENT
position four/four. Array position therefore does not consistently identify
CURRENT.

Scoring: correct iff the accepted action matches CURRENT color.

P4 may earn only association-conditioned action and outcome distributions. It
cannot establish general provenance reasoning, and an incorrect UNASSOCIATED
action cannot be described as irrational because the association may be
genuinely unavailable.

## Validity and failure handling

Each pressure retains every scheduled episode and call, including wrong,
malformed, or failed actions. Ordinary wrong actions and invocation failures
are descriptive policy/actuation outcomes, not experimental invalidity.

A pressure is `EXPERIMENT_INVALID` if any of the following is observed:

- undeclared hidden information enters policy visibility;
- an observation condition is delivered incorrectly;
- schema or action semantics mutate outside the predeclared intervention;
- a schedule mutates after execution begins;
- prior episode information reaches the model;
- malformed output is repaired;
- a semantic translator is introduced;
- world scoring derives from model narration;
- an unsuccessful episode is omitted; or
- a retry replaces an empirical episode.

The implementation independently checks expected serialized visible input,
schema content and hash, one-message stateless requests, model and sampling,
call/episode cardinality and order, selected-action/world-receipt separation,
and pressure-local scoring.

## Execution and stop rules

After new-schema qualification passes, execution is strictly:

```text
P1 -> close world/call traces
P2 -> close world/call traces
P3 -> close world/call traces
P4 -> close world/call traces
STOP
```

Any `EXPERIMENT_INVALID` pressure is closed with its wounds visible and stops
all remaining pressures. There are no empirical retries, supplemental
episodes, prompt changes, model changes, or schema changes after observation.
No earlier result may change a later frozen design.

After valid P4 closure, a descriptive cross-reference matrix records for each
coordinate the intervention, held-fixed coordinates, literal action counts,
and literal correct counts. It assigns no broader causal mechanism.

This protocol and its evidence do not authorize changes to `PROJECT_STATE.md`,
`PRESSURE_RESOLUTION_MAP.md`, Home, Controller, or any scientific standing.
