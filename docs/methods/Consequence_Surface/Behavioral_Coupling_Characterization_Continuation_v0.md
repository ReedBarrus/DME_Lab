# Behavioral Coupling Characterization Continuation v0

Status: `AUTHORIZED QUALIFIED SUBSET — NOT YET EXECUTED`

This is a bounded continuation authorization over the unchanged frozen
Behavioral Coupling Characterization v0. It does not redesign, supersede, or
repair the stopped battery.

## Preserved original stop

The original battery correctly stopped before P1. Its pre-execution
qualification established:

- BR `SUBMIT_BLUE`: pass
- BR `SUBMIT_RED`: pass
- RBD `SUBMIT_RED`: pass
- RBD `SUBMIT_BLUE`: pass
- RBD `DEFER`: fail; `Select DEFER.` produced valid typed `SUBMIT_RED`

The bounded result is only that this frozen model, prompt, and RBD schema
realization did not demonstrate DEFER traversal under that qualification
condition. The qualification trace remains unchanged at
`traces/behavioral_coupling_schema_qualification_v0.json`.

P3 remains `BLOCKED — NOT EXECUTED`. There is no DEFER retry, schema repair,
position change, prompt change, model change, or P3 empirical call.

## Reused frozen authority

- Original protocol:
  `docs/methods/Consequence_Surface/Behavioral_Coupling_Characterization_v0.md`
- `BATTERY_PROTOCOL_SHA256`:
  `sha256:fc4c1d8a32f1dd9c844bcaa12b4edb3057ae72d716be517a38c9d15ab5524b68`
- `P1_SCHEDULE_SHA256`:
  `sha256:6c442c4d81ed10024a1115b1ab9a8119d9690aa1683ec6de81011d460395b98f`
- `P2_SCHEDULE_SHA256`:
  `sha256:3514df11e5a119ac36b8a787f5abd8a0d03d2ab1d270fab0c0ba29d9bc62fc3f`
- `P4_SCHEDULE_SHA256`:
  `sha256:f4168239b66f9cbed3e6553a71b9a6cdb49cb2cebb76f7e5d4637d8af0bb976c`
- Preserved, unexecuted `P3_SCHEDULE_SHA256`:
  `sha256:049938ca737f44f2455c7de3dd89cccb5358104eb1acd50ff6688fe07786cdc5`

Schedules are read directly from the committed machine-readable freeze at
`traces/behavioral_coupling_characterization_freeze_v0.json`. They are not
regenerated or reordered.

## Qualified subset

This continuation authorizes exactly 64 empirical episodes:

- P1 — Actuation Prior: 32
- P2 — Semantic Indirection: 16
- P4 — Association: 16
- P3 — 0

P1 reuses the actually qualified presentation split:

- RB structured enum: `SUBMIT_RED`, `SUBMIT_BLUE`
- BR structured enum: `SUBMIT_BLUE`, `SUBMIT_RED`
- visible `legal_action_vocabulary` in both: `SUBMIT_RED`, `SUBMIT_BLUE`

P2 and P4 reuse the qualified ordinary RB two-action surface.

The specimen remains `hermes-3-llama-3.2-3b` at the loopback LM Studio
`/v1/chat/completions` endpoint with `temperature=0.0`, `top_p=1.0`, and
`max_tokens=16`. Every episode remains a stateless independent request with no
tools, MCP, repository or filesystem exposure, prior outcomes, retries,
semantic repair, or post-hoc prompt change.

## Execution and stop rule

```text
P1 -> close and validate P1 world/call evidence
P2 -> close and validate P2 world/call evidence
P4 -> close and validate P4 world/call evidence
STOP
```

Protocol/apparatus invalidity stops the remaining continuation. Ordinary wrong
actions remain empirical behavior and do not stop it. No result may alter a
later frozen pressure.

If all three pressures close validly, a continuation summary and descriptive
cross-reference matrix record literal action and outcome distributions. P3 is
included only as `BLOCKED AT QUALIFICATION`, never as empirical evidence.

## Scientific boundary

This pass changes no scientific semantics or standing. It does not establish
agency, reasoning, planning, uncertainty awareness, provenance reasoning,
authenticated provenance, generalized behavioral coordinates, orchestration,
coordination substrate, or Home activation. `PROJECT_STATE.md`,
`PRESSURE_RESOLUTION_MAP.md`, Home, Controller, and Persistent Ecology remain
outside this authorization.
