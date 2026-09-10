# DME Cockpit

## Purpose

The DME Cockpit is a read-only, observer-facing projection of DME_Lab.

Its purpose is to reduce the human reconstruction cost of understanding:

- where the Lab currently stands;
- what has actually been earned;
- what remains unresolved;
- what pressure is active or reachable;
- how evidence, constraints, decisions, and lineage relate;
- how provenance flows through the project;
- how experimental wounds appear, narrow, resolve, or remain open;
- how the implemented system differs from projected territory.

The Cockpit is not a second authority.

Repository evidence remains authoritative.

If the Cockpit disagrees with repository state, the Cockpit is wrong.

The bounded normalization and source boundary for the first implementation is
defined in the [Cockpit Projection Contract](PROJECTION_CONTRACT.md).

---

## Governing Rule

> At every point, the visual certainty of the interface should correspond to
> the epistemic status of what it represents.

The interface should make it difficult to visually confuse:

- observed with inferred;
- supported with projected;
- resolved with unresolved;
- source evidence with derived representation;
- constraint memory with local distinction;
- current state with historical state;
- reconstruction with truth;
- navigability with authority.

A prettier representation must expose provenance rather than conceal it.

---

## Causal Boundary

The Cockpit is read-only.

```text
repository / world
↓
observation
↓
reconstruction
↓
derived cockpit projection
↓
human inspection
```

The Cockpit does not mutate:

- repository files;
- pressure standing;
- constraints;
- decisions;
- traces;
- runtime state;
- external applications;
- experiments;
- agents;
- physical systems.

No UI control may silently cross from observation into action.

```text
website edits project state: NO
repo changes
→ cockpit changes: YES
```

Any future action authority belongs to a separate Controller surface.

## Source Authority

The Cockpit derives its state from committed repository artifacts.

Primary inputs may include:

- `PROJECT_STATE.md`
- `PRESSURE_RESOLUTION_MAP.md`
- `docs/constraints/README.md`
- `docs/constraints/registry.jsonl`
- `docs/decisions/*`
- `traces/*`
- `docs/contracts/*`
- `docs/projection/*`
- Git commit / lineage metadata
- selected runtime/source structure where useful

The exact extraction surface may evolve.

The Cockpit must not maintain a manually authored duplicate database of project
truth.

Where two repository surfaces disagree, existing DME_Lab authority rules apply.

The Cockpit must preserve the disagreement rather than resolving it for display.

## Projection Architecture

Prefer a simple deterministic projection path:

```text
DME_Lab repository
        ↓
read-only projection adapter
        ↓
normalized derived model
        ↓
static / read-only Cockpit
```

The normalized model is derived data.

It is not authoritative state.

Prefer build-time or refresh-time derivation over a persistent application
database until a concrete need forces otherwise.

A likely deployment path is:

```text
push to main
↓
repository build trigger
↓
parse authoritative artifacts
↓
generate derived Cockpit model
↓
build site
↓
publish
```

The exact hosting and build system are implementation choices.

## Adapter v0

The bounded adapter is implemented in
`src/cockpit/projection_adapter.py` and may be invoked with:

```text
python -m src.cockpit.projection_adapter --repo . --source-ref HEAD --freshness-ref origin/main
```

Its JSON output is derived and read-only. The adapter resolves the requested
source ref to an exact commit before reading allowlisted files from that
committed tree. Generated JSON is not repository authority.

The first [bounded adversarial pressure pass](../decisions/cockpit_projection_adapter_pressure_v0.md)
preserved nine named source wounds but exposed one unresolved silent
resolution-history loss and one duplicate-pressure-ID contract ambiguity. This
does not establish general adapter reliability.

## Freshness

The Cockpit should visibly identify the repository state from which it was
derived.

At minimum:

- repository
- branch
- commit
- build / projection time

A viewer should be able to answer:

What exact repository state am I looking at?

If a build cannot parse current authoritative state, prefer an explicit stale,
partial, or failed projection over silently displaying an older state as
current.

```text
projection failure
!=
clean project state
```

## Core User Question

The primary user is initially Reed operating DME_Lab.

The Cockpit should optimize for rapid recovery after interruption.

The central interaction is:

```text
WHERE AM I?
↓
WHAT DID REALITY LAST SAY?
↓
WHAT IS RESOLVED?
↓
WHAT IS STILL WOUNDED?
↓
WHAT CAN LEGITIMATELY BE ASKED NEXT?
↓
WHAT EVIDENCE WARRANTS THAT?
```

It is not initially optimized as a marketing website.

Public explanation may later become another bounded projection of the same
underlying model.

## Primary Surfaces

### 1. Pressure / Resolution Map

The Pressure / Resolution Map is the primary navigational surface.

It should answer:

- what pressures exist;
- current standing;
- what was missing;
- what was resolved;
- what residue remains;
- what blocked progress;
- what became reachable;
- what evidence warrants the node.

The Cockpit must not infer unsupported dependency edges.

The committed map is the source.

The visual graph is a projection of it.

### 2. Current State

Provide a compact current-state strip such as:

```text
DME_LAB

MODE          research
AUTHORITY     repository
BRANCH        main
COMMIT        <sha>
ACTIVE        <pressure / none>
OPEN          <count>
UPDATED       <derived build time>
```

This is descriptive metadata, not runtime telemetry unless the source actually
supports runtime telemetry.

Never simulate liveness.

### 3. Evidence Inspector

Any meaningful node should be inspectable through a common evidence panel.

Example:

```text
PR-XXX
------------------------------

STANDING
<standing>

QUESTION
...

OBSERVED
...

DERIVED
...

RESOLUTION
...

RESIDUE
...

BLOCKED BY
...

UNLOCKS
...

RELATED CONSTRAINTS
...

EVIDENCE
<decision / trace / tests / commit>
```

The inspector should distinguish direct evidence from derived interpretation.

Every exposed claim should make its evidence path easy to recover.

### 4. Constraints

The Cockpit may visualize the Constraint Registry as reusable anti-collapse
memory.

A constraint is not a local distinction event.

The current registry stores scoped limits on admissible equivalence or
inference.

Example visual object:

```text
snapshot
   ≠
complete transformation history

scope
basis
standing
provenance
```

Do not label the registry a Distinction Atlas.

Concrete local distinctions currently remain distributed through traces,
decisions, comparisons, tests, and adjudications.

The Cockpit may link a constraint to evidence where it was applied without
inventing a persistent distinction-event store.

### 5. Experimental Lineage

Expose development as pressure-driven lineage rather than as a blog.

Preferred conceptual form:

```text
pressure
↓
intervention
↓
observation
↓
comparison
↓
bounded adjudication
↓
constraint / residue
↓
changed reachability
```

A visitor should be able to ask:

Why does this structure exist?

and navigate backward toward the pressure and evidence that forced it.

Git history may help expose temporal lineage, but commit adjacency must not be
silently treated as causal dependency.

### 6. Earned System

Expose the currently earned DME pipeline separately from the research-pressure
map.

Approximately:

```text
REAL SOURCE
↓
CAPTURE
↓
RAW OBSERVATION
↓
PROVENANCE / INGEST
↓
APPEND-ONLY LEDGER
↓
INTEGRITY / CONTINUITY
↓
CANONICAL REPLAY
↓
ADMISSION
↓
RECONSTRUCTION
↓
PROJECTION
↓
HISTORICAL RELATION
```

This surface represents implemented / experimentally supported structure.

It should not absorb speculative ecological architecture.

### 7. Projection Horizon

Projected structures may be shown, but only beyond an explicit epistemic
boundary.

```text
EARNED TERRITORY
════════════════════
EVIDENCE HORIZON
════════════════════
PROJECTED TERRITORY
```

Projected structures should have visibly weaker form than earned structures.

Projection is allowed to be ambitious.

The interface must not make projection look implemented.

## View Bases

The same repository state may eventually support several bounded visual
projections.

Candidate views include:

### Topological View

What relates to what?

Pressure, evidence, constraints, system surfaces, and lineage.

### Temporal View

How did we arrive here?

Experiment and decision history over time.

### Epistemic View

What is known, unresolved, insufficient, candidate, or projected?

Standing and evidence boundaries.

### Domain View

Examples:

- acoustics
- repository history
- admission
- projection
- prediction

A domain view changes foreground emphasis.

It must not rewrite underlying standing.

Do not implement generalized basis switching until useful behavior can be
derived cleanly from repository structure.

## Visual Grammar

Status should be communicated by geometry and behavior, not only color.

Possible grammar:

- **BOUNDED / EARNED:** solid boundary; stable form; full evidence links.
- **ACTIVE:** solid center; subtle dynamic perimeter; explicit active pressure.
- **OPEN:** incomplete / open boundary; reachable but not active.
- **BASIS_INSUFFICIENT:** structure terminating at a visibly missing coordinate.
- **CANDIDATE_SURVIVED:** solid observed core; unresolved outer boundary.
- **PROJECTED:** thin / ghosted / dashed; clearly beyond evidence horizon.
- **SUPERSEDED / HISTORICAL:** dimmed but recoverable; visible lineage to later
  standing.

This grammar is a design language, not a replacement for exact textual status.

Exact status remains inspectable.

## Aesthetic Direction

Desired character:

Pearlescent scientific instrument × astronomical atlas × oscilloscope ×
sacred geometry, restrained by brutal epistemic typography.

Prefer:

- deep neutral field;
- strong negative space;
- fine coordinate structures;
- subtle chromatic refraction;
- thin relational traces;
- restrained luminous nodes;
- monospace for evidence / identifiers;
- highly legible explanatory type;
- animation only when it communicates state or relation.

Avoid:

- generic SaaS KPI cards;
- fake telemetry;
- glowing AI orbs;
- random cyberpunk decoration;
- confidence percentages not derived from evidence;
- "coherence scores";
- gamified research standing;
- animation without semantic meaning.

The map may be beautiful.

Evidence should remain austere.

## Interaction Rules

Allowed:

- inspect
- filter
- search
- zoom
- pan
- follow evidence
- change view
- change foreground basis
- navigate lineage
- open repository source

Not allowed:

- edit pressure standing
- create constraints
- modify repository
- execute experiments
- send commands
- authorize actions
- control agents
- change external state

Those belong outside the Cockpit.

## Failure Behavior

Projection failure must remain visible.

Examples:

- unknown status
- missing artifact
- broken evidence path
- parser failure
- unsupported record shape
- stale build
- conflicting source surfaces

Do not repair these with guessed interpretation.

A Cockpit failure is useful evidence about the projection adapter.

## Initial v0

The first implementation should remain small.

Recommended v0:

1. repository-state header
2. Pressure / Resolution Map visualization
3. universal inspector
4. constraint browser
5. experimental lineage view
6. earned-system view
7. projection horizon

Potentially defer:

- complex graph layout
- full Git-history reconstruction
- automatic semantic relation extraction
- basis-switching engine
- 3D visualization
- live telemetry
- accounts
- database
- editing
- controller integration
- agent controls

The initial Cockpit should prove that a derived visual projection reduces
reconstruction cost without creating a second reality.

## Success Criterion

The Cockpit is useful if a competent user can return after interruption and
recover the Lab's current consequential structure faster and with fewer
unsupported assumptions than by manually reconstructing it from repository
files and conversation.

A stronger later test may compare:

```text
manual repository navigation
vs
Cockpit-assisted reconstruction
```

on:

- recovery time;
- missed unresolved state;
- mistaken causal association;
- missed evidence;
- incorrect next-pressure inference;
- provenance navigation cost.

Do not optimize these metrics before ordinary use reveals the actual wound.

## Evolution

The intended developmental direction is:

```text
static project projection
↓
repo-derived research observatory
↓
richer live reconstruction
↓
multiple bounded views
↓
commitment / consequence surfaces
↓
navigable DME atlas
```

Each additional degree of liveness or authority must be earned.

The Cockpit remains an observer-facing projection unless a future pressure
explicitly requires otherwise.
