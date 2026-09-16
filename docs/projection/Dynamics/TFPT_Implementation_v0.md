# TFPT Implementation v0
## Consequence, Pressure, and Budgeted Local Transformation Runtime

**Status:** CANDIDATE IMPLEMENTATION PROJECTION  
**Authority:** NONE  
**Relation:** Parallel implementation projection to *Theory of Formal Process and Transformation (TFPT)*  
**Purpose:** Project the smallest runtime shape capable of turning TFPT from a descriptive transformation grammar into an executable, pressure-driven consequence system.

This document does **not** authorize implementation of a generalized engine. It proposes component boundaries, pressure semantics, tests, and development rules that can be attacked by local evidence.

---

## 1. Core Implementation Question

How can a runtime observe local change, evaluate consequential discrepancy, propagate only relevant pressure, and update navigable standing without:

- recomputing the whole world,
- collapsing consequence into one universal score,
- confusing projection with observation,
- turning simulation into authority,
- severing transformation lineage,
- or allowing semantic complexity to outrun feedback capacity?

The target is not a global optimizer.

The target is a **budgeted local consequence runtime** that spends attention and computation where retained structure is currently being challenged.

---

## 2. Candidate Consequence Definition

A consequence is not merely an event, effect, label, or score.

> **Consequence is the integrated transformation delta over a declared relational possibility space.**

Let:

- \(S_t\) = source state,
- \(T\) = transformation or event,
- \(S_{t+1}\) = observed or projected resulting state,
- \(R\) = active relation / evaluative basis,
- \(H\) = declared consequence horizon.

Then the candidate form is:

\[
C_{R,H}(T) = \Delta_{R,H}(S_t, S_{t+1})
\]

The runtime does not assume one universal metric for \(\Delta\).

Different relations may expose different local geometries:

- money,
- time,
- energy,
- resource availability,
- test validity,
- authority,
- commitment standing,
- latency,
- risk,
- workload,
- capacity,
- admissibility,
- viability,
- legitimacy,
- unresolvedness,
- possibility / option availability.

The shared layer preserves **topology and relation**. Local regimes earn their own metrics.

> **Shared topology first; local metrics where earned.**

---

## 3. Event, Effect, Consequence, Pressure, Feedback

The runtime must conserve these distinctions.

### EVENT
Something is observed or recorded as having occurred.

### EFFECT
A state difference associated with an event or transformation.

### CONSEQUENCE
An effect interpreted relative to a declared relation, constraint, commitment, dependency, resource, or possibility horizon.

### PRESSURE
A consequential discrepancy between the currently navigated configuration and newly observed or projected state.

### FEEDBACK
Consequence becoming available to a process capable of updating standing, configuration, action, or future attention.

Therefore:

\[
EVENT \neq EFFECT \neq CONSEQUENCE \neq PRESSURE \neq FEEDBACK
\]

A useful implementation must not silently collapse these stages.

---

## 4. Pressure as Relational Residual

Pressure is the runtime's primary dynamic signal.

For locally metric relations:

\[
P_R = y_{observed} - y_{expected}
\]

For non-scalar semantic relations:

\[
P_R = discrepancy(current\_relation, observed\_state, basis)
\]

Examples:

- expected `ACTIVE`, observed `CLOSED`,
- expected specification A, observed specification B,
- expected test invariant, observed counterexample,
- expected resource floor, observed depletion,
- expected authority, observed missing warrant,
- expected event applicability, observed superseded reference,
- expected available path, observed blocked path.

Pressure is directional because it exists **with respect to a maintained relation**.

It is not merely a severity label.

---

## 5. Standing Compression: The Lossy Trinity

The runtime may project a rich developmental lineage into three coarse standings:

### PROJECTED
A candidate structure exists but lacks sufficient consequential discrimination.

### PRESSURED
Evidence or world-state change is actively capable of discriminating the candidate or its current scope.

### INTEGRATED
The structure has survived enough relevant pressure to be operated from within a declared scope.

These are navigation standings, not universal truth values.

They are intentionally lossy.

The lineage must remain deeper than the standing.

Canonical motion:

\[
PROJECTED \rightarrow PRESSURED \rightarrow INTEGRATED
\]

But integration is not terminal:

\[
INTEGRATED \xrightarrow{new\ consequential\ discrepancy} PRESSURED
\]

This is **repressure**, not failure.

> **Integration means stable enough to operate from, not exempt from further pressure.**

---

## 6. Hysteresis as Memory and Control

Without hysteresis, standing may oscillate with every minor observation.

The runtime therefore needs phase-sensitive transition conditions.

Candidate behavior:

- `PROJECTED -> PRESSURED`: relatively cheap,
- `PRESSURED -> INTEGRATED`: requires discriminating consequence,
- `INTEGRATED -> PRESSURED`: requires meaningful contradictory consequence relative to scope.

The transition threshold need not be one scalar.

It may be a local contract such as:

- one reproducible counterexample reopens a universal claim,
- one missed routine occurrence does not invalidate the routine,
- one stale event reference blocks execution but does not invalidate the underlying commitment,
- repeated reconstruction cost may promote a retained continuation relation.

Hysteresis therefore acts as:

- memory,
- anti-flapping control,
- phase regulator,
- standing stabilizer,
- and a local lattice over consequential distinctions.

---

## 7. Developmental Meta-Rule

New structure must not enter the runtime merely because it is plausible or elegant.

> **A new distinction, edge, operator, metric, or mechanism earns durable integration only when retaining it changes consequential navigation relative to the strongest simpler baseline.**

Candidate developmental flow:

\[
PROJECT \rightarrow CONTACT \rightarrow PRESSURE \rightarrow DISTINGUISH \rightarrow RETAIN \rightarrow REPEAT \rightarrow INTEGRATE \rightarrow COMPRESS \rightarrow REOPEN
\]

Recurrence is not always required literally. One sufficiently discriminating failure may earn a distinction.

The deeper rule is:

> **No consequential discrimination, no structural promotion.**

This applies to runtime development itself.

The implementation must be developed under the same consequence rules it attempts to represent.

---

## 8. Runtime Meta-Rule

> **Compress the stable interior; spend attention at the moving boundary.**

Stable regions should become cheap.

Actively pressured boundaries should receive more observation, compute, and navigational resolution.

The runtime should therefore be:

- event-driven,
- locally propagating,
- horizon-bounded,
- budget-aware,
- lineage-preserving,
- degradation-legible.

It should avoid continuous global recomputation unless a pressure explicitly earns that cost.

---

## 9. Candidate Runtime Shape

```text
WORLD / SOURCES
    |
    v
[1] EVENT INGEST
    |
    v
[2] OBSERVATION ENVELOPE
    |
    v
[3] RELATION / BASIS RESOLUTION
    |
    v
[4] CONSEQUENCE EVALUATOR
    |
    v
[5] LOCAL PRESSURE RECORD
    |
    v
[6] EARNED DEPENDENCY PROPAGATION
    |
    v
[7] HYSTERESIS / STANDING CONTROLLER
    |
    +--------------------+
    |                    |
    v                    v
[8] NAVIGATION       [9] WARRANT / ACTION
    |                    |
    +----------+---------+
               |
               v
         [10] LEDGER / LINEAGE
               |
               v
         future observation
```

A projected/simulated path may branch from the consequence evaluator, but must remain explicitly projected.

---

## 10. Candidate Components

### 10.1 Event Ingest
Receives raw bounded events from Home, repository/runtime, agents, sensors, clocks, finance, business operations, human reports, and later external systems.

Responsibilities:

- retain source,
- retain time,
- retain actor/origin where mechanically known,
- avoid interpretation beyond admission requirements,
- assign stable event identity.

### 10.2 Observation Envelope
Separates raw source state from interpretation.

Candidate fields:

```text
observation_id
source_ref
observed_at
source_time
observer
raw_state_ref
scope
missingness
confidence / standing if locally earned
```

Observation does not imply consequence.

### 10.3 Relation / Basis Registry
Defines the active relation against which consequence may be evaluated.

Examples:

```text
commitment fulfillment
cash balance floor
test invariant
authority boundary
time budget
resource capacity
dependency standing
expected latency
market position constraint
```

Each relation must declare enough local semantics to evaluate discrepancy.

No relation becomes global merely because it exists.

### 10.4 Consequence Evaluator
Computes or derives the transformation delta relative to one relation and one horizon.

Candidate output:

```text
consequence_id
basis_relation
source_state_ref
transformation_ref
result_state_ref
horizon
delta
metric_kind / topological relation
attribution_standing
uncertainty
```

Simulation outputs must be marked `PROJECTED`.

Observed consequence must never be inferred from requested transformation alone.

### 10.5 Pressure Record
Represents unresolved consequential discrepancy.

Candidate fields:

```text
pressure_id
relation_id
consequence_ref
direction / contradiction type
standing
opened_at
last_observed_at
scope
unresolved_reason
```

Pressure is not automatically scalar.

### 10.6 Earned Dependency Graph
Edges exist only after their retention has demonstrated navigational value.

Candidate edge relations:

```text
depends_on
supports
contradicts
narrows
widens
blocks
enables
supersedes
amends
reopens
observed_through
```

Each edge should retain:

```text
edge_id
source
target
relation
scope
basis
standing
lineage
```

Pressure propagates only through edges whose semantics justify propagation.

### 10.7 Hysteresis / Standing Controller
Determines whether pressure changes current standing.

It must support:

```text
PROJECTED
PRESSURED
INTEGRATED
```

with local transition contracts.

It should not reduce all domains to one threshold.

### 10.8 Budget Governor
Controls propagation and cognition cost.

Candidate budgets:

```text
max dependency hops
max affected nodes
max compute/time
max model calls
max simulation depth
max attention surface
max action radius
```

If budget is exhausted:

- preserve unresolved pressure,
- preserve lineage,
- narrow action radius,
- mark continuation need,
- do not silently drop the pressure.

Candidate law:

> **Loss of cognitive capacity should reduce action radius before it reduces provenance.**

### 10.9 Navigation Surface
Projects:

- current standing,
- active pressure,
- affected dependencies,
- unresolved conflicts,
- relevant history refs,
- available action/warrant boundaries.

The trinity acts as `YOU ARE HERE`.

The expanded cycle acts as local process detail.

The ledger provides temporal depth.

### 10.10 Action / Warrant Boundary
Pressure does not itself grant authority.

The runtime may surface, recommend, request warrant, or execute only within admitted authority.

Required distinctions:

```text
pressure != authorization
capability != authority
authority != admission
recommendation != commitment
commitment != execution
```

### 10.11 Ledger / Lineage
All important transformations must remain recoverable.

The ledger should preserve event, observation, relation basis, consequence, pressure, standing transition, action/warrant, feedback, and integration/reopening.

Current projections may compress this history but may not silently rewrite it.

---

## 11. Degradation and Fail-Safe Semantics

Every pressure/dependency path must be able to become visibly wounded.

Candidate degradation states:

```text
CURRENT
STALE
SUPERSEDED
UNRESOLVED
MISSING
MALFORMED
OUT_OF_SCOPE
BUDGET_EXHAUSTED
SOURCE_UNAVAILABLE
```

Do not silently substitute:

- missing with false,
- stale with current,
- malformed with empty,
- unresolved with failed,
- projected with observed,
- unavailable with irrelevant.

When propagation reaches a wounded edge:

1. retain the pressure,
2. mark the wound,
3. stop or narrow propagation unless a local contract permits continuation,
4. request more observation or authority if needed.

---

## 12. Simulation Boundary

Real-time consequence simulation may become useful, but it is dangerous.

The runtime must preserve:

\[
SIMULATED\ CONSEQUENCE \neq OBSERVED\ CONSEQUENCE
\]

A simulation may expose candidate paths, estimate resource use, identify likely collisions, rank local alternatives if the local regime supports it, or request observation.

It may not silently close a pressure, establish empirical consequence, manufacture authority, or rewrite integrated standing as fact.

Simulation is a navigation aid until world feedback returns.

---

## 13. Local Geometry, Not Universal Scoring

Avoid a universal `consequence_score`.

Instead permit local vectors.

Example:

```text
money_delta: -$180
time_delta: +90 min
energy: user-reported HIGH COST
confusion: unresolved
authority: admissible
commitment_effect: partial
option_space: narrowed
```

A consumer may inspect its standing relative to those dimensions.

Different actors may legitimately weight them differently.

The runtime preserves the coordinates rather than pretending one global utility scalar is already justified.

This allows consequence to function as **relational preference/bias derived from declared basis**, while keeping that basis inspectable.

---

## 14. Real-Time Event-Driven Propagation

Candidate runtime behavior:

```text
event arrives
    |
    v
which retained relations can this event discriminate?
    |
    v
evaluate only those local relations
    |
    v
open/update local pressures
    |
    v
propagate only across earned dependency edges
    |
    v
stop when:
    no consequential delta remains
    OR scope ends
    OR budget ends
    OR edge is wounded
    OR authority boundary is reached
```

The runtime should not ask:

> "What does this event mean to everything?"

It should ask:

> "Which retained relations have declared enough basis for this event to matter?"

---

## 15. Candidate Pressure Map

A consequence graph becomes useful when it can show:

```text
quiet integrated region
active pressured boundary
new projected candidate
dependency threatened by reopening
stale / wounded edge
unresolved propagation
resource-expensive region
```

This is not primarily a visualization feature.

It is a runtime topology.

A future Cockpit may project it geometrically, but the semantics must exist before the rendering.

---

## 16. Minimum Executable Test Regime

The first implementation should NOT attempt a whole-world graph.

Use one tiny bounded regime.

### Test A — Local discrepancy
Create one integrated relation, one expected state, and one contradictory observation.

Pass if one pressure opens, lineage is retained, and unrelated relations remain untouched.

### Test B — Earned dependency propagation
Create `A -> B -> C` where only B legitimately depends on A.

Pass if pressure on A reaches B and does not reach C without an earned edge.

### Test C — Repressure
Start with an integrated relation and apply discriminating contradiction.

Pass if standing reopens to `PRESSURED` and prior integration lineage remains recoverable.

### Test D — Hysteresis
Apply weak/noisy alternating observations.

Pass if standing does not flap without satisfying the local transition contract.

### Test E — Budget exhaustion
Create dependency depth beyond declared propagation budget.

Pass if runtime stops, unresolved continuation is retained, and no affected state is silently marked resolved.

### Test F — Degraded edge
Corrupt or stale one dependency edge.

Pass if the wound becomes visible, propagation does not silently cross it, and raw source remains recoverable.

### Test G — Projection vs observation
Inject one simulated consequence and one observed consequence.

Pass if they remain mechanically distinguishable and simulation cannot satisfy empirical closure.

### Test H — No global recomputation
Change one local observation in a graph containing unrelated regions.

Pass if only the relevant local region is evaluated.

### Test I — Compression / reopening
Compress one quiet integrated region into a current summary. Later inject contradictory consequence.

Pass if lineage can be reopened sufficiently to adjudicate the contradiction.

### Test J — Weaker consumer
Give a bounded projection to a simpler consumer.

Pass if it can still recover current standing, actor/source, pressure, unresolvedness, and authority boundary without reconstructing the entire graph.

---

## 17. Development Tests for New Mechanics

Before adding any new runtime mechanism ask:

1. What observed friction requires it?
2. What simpler baseline currently exists?
3. What distinction does the new mechanism preserve?
4. What executable pressure demonstrates the loss without it?
5. What local scope has actually been earned?
6. What additional maintenance / compute burden does it create?
7. What would cause it to be reopened or removed?

If these cannot be answered, keep the mechanism projected.

---

## 18. Likely Near-Term Connection Surfaces

Without authorizing them, current work suggests several possible future adapters.

### Home
Can provide commitments, specifications, occurrence reports, local time, explicit amendments, and later typed routine observations.

Potential consequence relations:

- commitment applicability,
- temporal collision,
- report mismatch,
- resource / schedule pressure.

### Chat Home
Can provide current pressure, recommendations, unresolved questions, Chat commitments, and continuation refs.

Potential consequence relations:

- stale recommendation,
- commitment collision,
- insufficient execution capacity,
- warrant requirement.

### DME Repository
Can provide tests, pressure reports, decisions, schemas, runtime traces, and implementation standing.

Potential consequence relations:

- invariant violation,
- reconstruction burden,
- semantic drift,
- test failure,
- authority mismatch.

### Local Automation Workshop
Can provide model task basis, delegated authority, execution trace, tool cost, reconstruction burden, and return result.

Potential consequence relations:

- execution friction,
- context loss,
- overreach,
- verification failure,
- continuation cost.

These surfaces should remain federated until specific cross-boundary relations earn retention.

---

## 19. Cockpit Projection

The Cockpit should not become an "everything dashboard."

Candidate role:

> **Project where consequence currently has leverage.**

Default projection may eventually expose:

```text
YOU ARE HERE
current standing by local regime

MOVING BOUNDARIES
active pressures

QUIET INTERIOR
compressed integrated regions

WOUNDED EDGES
stale / missing / degraded dependencies

ATTENTION REQUESTS
where additional observation or authority is needed

RESOURCE PRESSURE
where propagation or simulation is expensive
```

The goal is not maximal visibility.

The goal is pressure-relative navigation.

---

## 20. Meta-Governance

The runtime must remain subordinate to the same principles it evaluates.

It must never silently infer:

- legitimacy from persistence,
- authority from capability,
- truth from integration,
- completion from due state,
- observation from simulation,
- applicability from historical existence,
- global validity from local success.

Every integrated mechanism remains reopenable.

Every compressed surface must retain a path to lineage.

Every action radius must remain bounded by current authority and feedback capacity.

---

## 21. Candidate System Law

> **Define consequence as relational transformation delta; derive pressure from persistent consequential discrepancy; propagate pressure only through earned dependencies; regulate standing through hysteresis; bound computation and action locally; preserve degradation and lineage explicitly.**

This is the candidate bridge from semantic conservation to executable consequence geometry.

---

## 22. Immediate Next Research Question

Can a tiny event-driven runtime, operating over one bounded regime, use relational discrepancy and one earned dependency edge to:

1. open pressure from observation,
2. propagate that pressure locally,
3. change standing under a declared hysteresis contract,
4. preserve lineage,
5. stop under a strict budget,
6. and later reopen compressed state when consequence diverges?

If yes, extend only from the failure boundary.

If no, factor the runtime until the smallest useful consequence mechanism remains.
