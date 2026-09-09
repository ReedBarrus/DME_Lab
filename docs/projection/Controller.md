# Controller

> Non-authoritative projection.
>
> This document preserves a possible future action boundary for DME_Lab.
>
> It does not authorize implementation of a controller, orchestrator, scheduler,
> planner, autonomous agent loop, action engine, or external-system mutation
> surface.
>
> Reopen only when concrete pressure independently requires action authority.

## Purpose

The projected Controller is a separate module responsible for attributable,
authorized mutation of external systems.

The Controller is not the Cockpit.

```text
COCKPIT
observation / reconstruction / navigation

CONTROLLER
authorization / action / execution boundary

The separation exists to preserve causal clarity.

A viewer should never have to wonder whether inspecting state changed it.

Projected Relationship
external world / repository
↓
observation
↓
DME reconstruction
↓
Cockpit
↓
human understanding

             separate boundary

reconstructed state
↓
candidate action
↓
authorization / admissibility
↓
Controller
↓
external effect
↓
new observation
↓
DME reconstruction
↓
Cockpit changes

The Controller should never directly edit the Cockpit's projection model as a
substitute for observing consequence.

Core Projected Rule

Capability does not establish admissibility.

can perform action
!=
should perform action

A controller may know how to execute an operation while lacking:

authorization;
sufficient source freshness;
preconditions;
consequence bounds;
identity confidence;
acknowledgement;
retry safety.

The Controller should preserve those differences.

Possible Future Action Record

A future attributable action may need enough structure to recover:

requested operation
actor / authority
target
basis / reconstructed state
preconditions
permissions
expected consequence
attempt identity
execution start
external acknowledgement
observed consequence
completion standing
residue

This is only a candidate shape.

Do not implement it from this projection.

Action Loop

A possible future bounded loop is:

state S0
↓
candidate operation A
↓
preconditions
permissions
admissibility
↓
authorization
↓
execution attempt
↓
external acknowledgement / observation
↓
state S1
↓
compare expected ↔ observed consequence
↓
update reconstruction

The loop must tolerate:

attempted
!=
completed

acknowledged
!=
actually changed world

historically recovered
!=
currently fresh

retry requested
!=
retry safe
Lost Acknowledgement

One projected high-value pressure is:

action attempted
↓
external effect may occur
↓
acknowledgement lost
↓
worker interrupted
↓
new worker resumes

The Controller must not blindly retry.

A competent replacement should establish the current external state before
deciding whether another action is admissible.

This problem should be experimentally pressured before generalized retry or
transaction semantics are implemented.

Controller Authority

Controller authority should be explicit and bounded.

Potential dimensions include:

who authorized?
what target?
what operation class?
what consequence boundary?
what time / state basis?
what retry policy?
what revocation condition?

No implicit universal agent authority.

No action should become authorized merely because it is reachable.

Thin Kernel, Domain Adapters

The projected Controller should not contain native operational semantics for
every external system.

Prefer:

DME reconstructed state
↓
bounded action interface
↓
domain adapter
↓
external system

Possible future domains:

Git
filesystem
browser
email
calendar
AV systems
applications
network services
robots
physical actuators

Each domain should earn its own observation and action boundary.

Relationship to Agents

Agents may eventually:

propose action
inspect evidence
evaluate alternatives
request authorization
interpret consequence

They should not implicitly become the Controller.

agent proposal
!=
authorized action

agent confidence
!=
admissibility

agent memory
!=
current external state

A Controller may execute an authorized operation without containing an LLM.

Relationship to Cockpit

The Cockpit remains read-only.

The Controller may eventually have a separate control surface.

Do not place operative controls inside the Cockpit merely because they are
convenient.

A later composition may visually connect:

Cockpit
→ inspect reachable action

Controller
→ request / receive authority

Controller
→ execute

Cockpit
→ observe resulting reconstruction

Composition should occur only after both sides independently earn their roles.

Reopening Conditions

Reopen Controller development only when a real pressure requires at least one
of:

repeated manual execution becomes a meaningful bottleneck;
ambiguity over whether an external action completed;
unsafe or costly retry risk;
stale state can invalidate an intended action;
multiple agents or workers need shared execution authority;
permissions or consequence boundaries need explicit enforcement;
a real process requires sustained observe → act → observe consequence loops;
human reconstruction and execution latency becomes consequential.

Do not reopen merely because automation would be entertaining.

First Legitimate Pressure

When action pressure actually arrives, begin with one bounded consequence.

Prefer something:

reversible
low consequence
externally observable
easy to attribute
easy to verify

Compare:

manual execution
vs
Controller-mediated execution

Ask whether the Controller improves:

provenance;
completion certainty;
retry safety;
reconstruction after interruption;
consequence attribution.

Do not begin with generalized automation.

Non-Goals

This projection does not authorize:

autonomous world control;
universal orchestration;
generalized task planning;
persistent agent consciousness;
a global world state;
unrestricted computer use;
hidden action;
self-expanding permissions;
a universal consequence engine.
Standing

PARKED.

The Cockpit may be implemented independently.

The Controller should remain absent from the operational system until concrete
action pressure earns reopening.

Until then:

observe
reconstruct
visualize
understand

before:

authorize
act
observe consequence