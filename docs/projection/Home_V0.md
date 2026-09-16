# Home v0

Status: PROJECTION — CANDIDATE BOUNDARY
Implementation authority: NONE
Scientific standing: NOT ESTABLISHED
Current next action: completion attack / manual cross-domain pressure

## 1. Purpose

Home is a candidate durable local surface for personal state and explicit
relations to independently authoritative external state spaces.

Home is not a universal database, project mirror, world model, or source of
authority over external domains.

Core claim:

> Home preserves durable personal state and explicit cross-domain relations
> without collapsing independently authoritative state spaces.

## 2. Boundary

### Home may own

- personal Care state;
- explicit Commit state;
- later, deliberately retained Explore state;
- personal observations and corrections;
- explicit relations from personal state to other referenced state spaces.

### Home does not own

- DME project standing;
- financial truth;
- calendar truth;
- sensor truth;
- external service state;
- agent interpretations merely because they were generated;
- Cockpit projections.

External state remains authoritative at its source and is referenced rather
than mirrored.

## 3. Core invariants

### 3.1 Capture != Interpretation

A person's original expression remains distinguishable from any interpretation
derived from it.

Agent inference may create a candidate derived object or relation.

It may not rewrite the source expression into a stronger semantic claim.

### 3.2 Relation != Status Transfer

A relation between state spaces may constrain, inform, support, conflict with,
or otherwise affect navigation.

It does not copy semantic standing across the boundary.

Examples:

Reed wants X
!=
DME warrants X

DME recommends X
!=
Reed committed to X

historical authority for X
!=
current execution authority

### 3.3 Projection != Authority

Cockpit and agent navigation views are derived projections.

A projection does not become authoritative merely because it is useful.

If it can be reconstructed safely and cheaply, it need not be retained as
authoritative state.

### 3.4 Federated Sources Stay Federated

Home does not become the database of everything.

Candidate composition:

    PERSONAL HOME
      Care / Commit / later Explore

    DME REPO
      authoritative project state

    OTHER SOURCES
      calendar / finances / sensors / environment / services

             |
        refs + relations
             |
             v

        NAVIGATION

        /        \
    COCKPIT     AGENTS

## 4. Initial Personal State Domains

### CARE

Question:

> What should be protected, restored, or sustained?

Initial capture:

- NOW
- NEED
- NEXT CARE

`NEXT CARE` is not automatically a commitment.

### COMMIT

Question:

> What action has actually been adopted?

Initial capture:

- I am committing to
- This serves
- Done means

Only an explicit Commit operation may create an adopted commitment.

Mention, desire, recommendation, need, intention, or agent inference does not
create one.

### EXPLORE

Conceptually:

> What is interesting, possible, uncertain, or worth investigating without
> creating obligation?

Explore remains ordinary free conversation initially.

Formal conversational capture must earn itself later.

## 5. Shared Candidate Process Grammar

Candidate cross-domain grammar:

PRESSURE
→ FREEZE
→ TRANSFORM
→ OBSERVE
→ ADJUDICATE
→ NAVIGATE

The grammar is shared.

Domain semantics are not.

Shared grammar != shared ontology.

### PRESSURE

Identify the live consequence-bearing condition.

### FREEZE

Declare relevant basis, scope, horizon, constraints, and authority.

### TRANSFORM

Apply the bounded action, commitment, projection, counterprojection, or other
declared operation.

### OBSERVE

Retain what actually happened without semantic promotion.

### ADJUDICATE

Determine what standing changed, what remains unresolved, and whether prior
standing must be retained, contracted, refined, or corrected.

### NAVIGATE

Determine available next moves, including continuation, revision, override,
reopening, escalation, or dwell.

## 6. Multiple State Spaces

Candidate state spaces include, but are not limited to:

- Reed State
- Home State
- DME Project State
- Agent State
- Environment State
- Financial State
- Calendar State

These are not assumed to share one ontology or authority.

Navigation operates over their relations.

## 7. Collision

A collision is an unresolved relation among simultaneously relevant states
whose resolution changes reachable consequence.

Collision != error.

A collision may remain unresolved.

Example:

    CARE
      protect sleep

    EXPLORE
      continue DME investigation

    ENVIRONMENT
      work at 05:00

    COLLISION
      continued exploration consumes expected next-day capacity

Navigation may expose moves such as:

- stop;
- narrow scope;
- explicitly override;
- defer;
- renegotiate the commitment.

Navigation must not silently flatten the collision into one state.

## 8. Candidate Durable Representation

No representation is yet earned.

Current smallest candidate:

    events.jsonl
    relations.jsonl

Possible event coordinates:

- stable ID;
- domain;
- kind;
- raw content/value;
- source;
- observed time;
- explicit status.

Possible relation coordinates:

- stable relation ID;
- from reference;
- relation;
- to reference;
- basis/provenance;
- standing;
- observed time.

This is a candidate mechanical surface, not an implementation warrant.

Relation vocabulary is not yet fixed.

## 9. Cockpit

Cockpit is not Home.

Candidate relation:

> Home stores durable personal state.
> Cockpit projects the subset relevant to the current navigation horizon.

Conceptually:

    Home + external authoritative sources + horizon
                    |
                    v
              Cockpit projection

Cockpit may expose:

- relevant Care state;
- active Commit state;
- relevant exploration;
- external constraints;
- collisions;
- navigable moves;
- unresolved states requiring human judgment.

Cockpit projection remains derived.

## 10. Agent Access

Agents should not receive unrestricted personal history by default.

Candidate rule:

> Dereference only the state required by the declared navigation horizon.

Minimal coordination law:

- preserve source;
- preserve domain;
- preserve status;
- preserve authority;
- preserve missingness;
- do not transfer standing through relations;
- recommendation != adoption;
- adoption != commitment;
- commitment != authority;
- authority != admission;
- capability != execution;
- surface collisions rather than silently resolving them.

## 11. First Pressure

Do not implement Home merely because this projection is coherent.

First compare one real personal episode and one completed bounded DME episode.

Represent both using the same candidate six-operation grammar while retaining
their independent domain semantics and authoritative sources.

Give a fresh navigator only:

- the shared grammar;
- a minimal agent-context contract;
- relevant personal specimen state;
- relevant repository access.

Ask:

1. What happened?
2. What is actually established?
3. Which source owns each state?
4. What collisions exist?
5. What moves are navigable?

## 12. Falsification

The shared grammar is not earned if it:

- forces either domain into unnatural semantics;
- leaks semantic standing across domains;
- turns need into commitment;
- turns human preference into project standing;
- turns project recommendation into human obligation;
- cannot preserve unresolved collision;
- requires enough domain-specific exception machinery that the claimed common
  grammar provides no useful compression.

Home machinery is not earned merely because structured files would be
convenient.

## 13. Implementation Gate

The candidate implementation plan is not the current selected action.

Sequence:

1. freeze Home v0 projection;
2. run completion attack against the strongest simpler baseline;
3. run the first pressure manually if honest manual execution is sufficient;
4. identify any exact mechanical retention/navigation wound;
5. implement only the minimum mechanism required to repair that wound.

Allowed completion standings:

- NOT_EARNED
- MANUAL_PRESSURE_FIRST
- MINIMAL_IMPLEMENTATION_EARNED

`MINIMAL_IMPLEMENTATION_EARNED` requires a concrete consequential distinction
that existing manual/repository mechanisms cannot preserve or pressure
reliably.

## 14. Current Standing

Established:
- none of the Home architecture as generalized mechanism.

Candidate:
- durable personal state;
- explicit cross-domain relations;
- shared process grammar;
- federated authority;
- derived pressure-relative projections;
- collisions as first-class unresolved relations.

Not earned:
- generalized Home database;
- fixed relation ontology;
- Cockpit architecture;
- generalized agent navigation substrate;
- raw audio retention;
- autonomous personal interpretation;
- generalized semantic world model.

## 15. Development Bias

> Keep local state authoritative where it originates.
> Preserve distinctions rather than flattening them.
> Compose only the relations required by consequence.
> Let failures of the simplest baseline earn additional machinery.