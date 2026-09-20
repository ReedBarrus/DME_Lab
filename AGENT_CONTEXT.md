# Agent Context

Repository:
https://github.com/ReedBarrus/DME_Lab

DME_Theory:
https://github.com/ReedBarrus/DME_Theory

DME_Theory is lineage, not authority.

## Durable continuity startup

Do not begin by reconstructing the entire project from a fixed document precedence chain.

Before consequential work, perform the synchronization ritual in `continuity/SYNC_RITUAL.md`.

Then begin from the consumer-relative continuity delta:

```text
identify consumer
-> read continuity/cursors/<consumer>.json
-> if UNINITIALIZED, stop ordinary delta and explicitly bootstrap
-> if POSITIONED, read continuity/events.jsonl after the established coordinate
-> orient to the bounded delta
-> follow only authoritative refs required by the present operation
-> declare local continuity
-> work
-> append consequential activity
-> advance the consumer cursor after consumption
```

The continuity contract is documented in `continuity/README.md`.

If a named consumer cursor does not exist, treat that as explicit missing continuity state. Do not silently substitute another consumer's cursor.

Continuity transports recorded claims about activity. It does not adjudicate them.

```text
ACTIVITY_RECORDED
!=
ARTIFACT_EXISTS
!=
RESULT_VERIFIED
!=
STANDING_CHANGED
!=
FRONTIER_CHANGED
```

A reported standing/frontier delta in the continuity stream is not authoritative merely because it was recorded.

## Authority by semantic ownership

There is no single global document precedence chain.

Use the source that owns the fact required by the current operation:

- repository tree / commits own committed repository-state facts;
- executable tests and traces own their bounded observed execution results;
- decision/adjudication artifacts own only the bounded standing they explicitly establish;
- `continuity/events.jsonl` owns only the fact that a participant recorded the listed activity/claim;
- `PROJECT_STATE.md`, `PRESSURE_RESOLUTION_MAP.md`, Cockpit, and similar surfaces are derived navigation/projection aids unless a narrower contract says otherwise;
- Home owns only the personal state explicitly admitted into Home;
- conversation is source material and coordination context, not automatic project standing;
- DME_Theory is historical lineage only when explicitly consulted.

When an operation depends on standing, evidence, current repository state, or execution fact, follow the relevant continuity refs and inspect the owning source rather than treating the continuity summary as proof.

## Current intention

Build a provenance-preserving observability system that begins with bounded event/evidence capture, stabilizes reconstruction and consequence legibility, and expands only where executable pressure earns additional structure.

The current continuity pressure is narrower:

> Test whether consumer-relative delta recovery can reduce cross-invocation reconstruction burden while preserving equal or better standing fidelity, and whether that durable state is reliably instantiated without Reed manually transporting it.

## Development posture

Keep the system minimal.
Do not infer semantics before evidence supports them.
Prefer runtime pressure over speculative schema growth.
Preserve missingness.
Preserve provenance.
Treat all current structures as amendable under evidence.

## Fallback when continuity is insufficient

If the continuity delta does not provide enough basis for the current task:

1. state what required coordinate is missing;
2. follow referenced evidence if available;
3. inspect `PROJECT_STATE.md`, `README.md`, `WORKFLOW.md`, active contracts/projections, recent commits/traces, or constraints only as demanded by the missing dependency;
4. do not convert broader reconstruction into automatic startup ritual.

Consult `docs/contracts/README.md` when determining boundary maturity or evidence status.
Consult `docs/constraints/README.md` and `docs/constraints/registry.jsonl` when current work may collide with conserved constraints.
Consult DME_Theory only for useful lineage or comparison.

Repository: https://github.com/ReedBarrus/DME_Lab

This file answers: **how should a participant enter the Lab?**

## Startup / navigation order

1. Read [PROJECT_STATE.md](PROJECT_STATE.md) for current standing.
2. Read [README.md](README.md) for identity / objective and
   [WORKFLOW.md](WORKFLOW.md) for movement / authority transitions.
3. Follow only the contract, projection, decision, trace, test, constraint, or
   source relevant to the current question.
4. Inspect recent commits/runtime evidence when implementation state matters.
5. Consult DME_Theory only for useful lineage or comparison.

This is a navigation order, not evidential precedence.

## Evidential precedence

When claims conflict, distinguish:

```text
direct retained evidence / executable behavior
↓
adjudicated bounded standing
↓
scoped contracts / conserved constraints
↓
derived current-state / navigation projections
↓
conversation / orientation
↓
lineage
```

Precedence does not mean raw evidence interprets or adjudicates itself.

A contradictory projection must yield to its evidence basis, but changed
current standing still requires adjudication.

## Authority routing

For transition semantics, use [WORKFLOW.md](WORKFLOW.md).

In current development governance:

```text
interpretation != authorization != execution
```

Reed is the current Executive authorization point.

A reachable pressure, Council recommendation, passing test, successful
implementation, or current projection does not by itself create execution
authority or semantic promotion.

## Entry discipline

Preserve provenance, scope, missingness, and unresolvedness.

Prefer executable pressure to speculative architecture.

Do not broaden a bounded result merely because the repository contains adjacent
concepts.

Treat current structures as amendable under better evidence.

DME_Theory is lineage, not authority.

## Continuity-aware entry

If the participant occupies a retained continuity consumer identity and the
current task depends on prior retained activity, follow
`continuity/SYNC_RITUAL.md` before consequential work.

Continuity transports recorded activity and consumer-relative position. It does
not replace repository evidence, adjudicated standing, or authority routing.

continuity available
!=
continuity consumed
!=
semantic application
!=
acknowledgement
