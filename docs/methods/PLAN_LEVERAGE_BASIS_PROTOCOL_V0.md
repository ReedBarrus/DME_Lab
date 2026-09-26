# Plan Leverage / Basis Protocol V0

**Status:** PROVISIONAL_METHOD — planning interface discipline only  
**Purpose:** make a proposed move legible before formal planning machinery or
execution is allowed to hide the reason for doing it.

## Human-readable front layer

Before presenting a formal plan, state:

1. **Leverage sought**  
   What capability, compression, observability, coordination, recovery, or
   consequence advantage is this move trying to create?

2. **Observed basis**  
   What current evidence, relation, failure, pressure result, or qualified
   invariant makes that leverage plausible *now*?

3. **Bounded move**  
   What exact transformation is being proposed?

4. **Expected consequence**  
   What should become easier, cheaper, more reliable, more observable, or more
   recoverable if the move works?

5. **Preserved relations**  
   What must remain unchanged or coherent while the move occurs?

6. **Unknown / pressure target**  
   What part is genuinely not yet known and therefore deserves pressure rather
   than assumption?

7. **Hold / stop condition**  
   What observation would make the plan pause, narrow, or fail?

Short form:

```text
LEVERAGE
→ BASIS
→ BOUNDED MOVE
→ EXPECTED CONSEQUENCE
→ PRESERVATIONS
→ UNKNOWN
→ HOLD / STOP
```

## Why this exists

A plan should not begin with:

```text
"next task = X"
```

It should begin with:

```text
"X is worth testing because it is expected to buy Y,
and current evidence Z gives us a bounded reason to expect that."
```

This makes the plan challengeable before execution and lets a human operator
catch obvious relations before the system spends a campaign rediscovering them.

## Candidate machine envelope

A future plan candidate may carry:

```text
PLAN_ID
LEVERAGE_SOUGHT
BASIS_HANDLES
CURRENTNESS
BOUNDED_MOVE
EXPECTED_CONSEQUENCE
PRESERVATION_OBLIGATIONS
UNKNOWN_COORDINATES
PRESSURE_TARGET
COST_BUDGET
HOLD_CONDITIONS
STOP_CONDITIONS
```

Do not require all fields universally until pressures show which ones carry load.

## Relation to relational stewardship

Planning selects or proposes a transformation.

Relational stewardship checks whether the transformation actually preserved the
declared local relation and flow.

```text
PLAN:
why this move / what leverage?

↓ if admitted elsewhere

TRANSFORM:
perform bounded change

↓ then

STEWARD:
did endpoint / counterpart / edge / flow remain coherent?

↓ then

MEMORY:
retain consequence and update standing
```

## Cost discipline

Leverage is not assumed merely because a move is technically possible.

Candidate leverage dimensions include:

- reduced reconstruction burden;
- reduced search branching;
- improved observability;
- improved recoverability;
- improved coordination;
- reduced hot-memory load;
- reduced model-token use;
- reduced tool calls;
- lower latency;
- stronger provenance closure;
- safer consequence handling.

Do not collapse these into one score without pressure evidence.

## Required noncollapses

```text
PLAN EXISTS != MOVE JUSTIFIED
INTERESTING IDEA != LEVERAGE
LEVERAGE CLAIM != OBSERVED BENEFIT
BASIS EXISTS != BASIS CURRENT
EXPECTED CONSEQUENCE != OBSERVED CONSEQUENCE
PLAN EXPLANATION != EXECUTION AUTHORITY
```

## Claim ceiling

This protocol is a presentation and planning-discipline proposal.

It does not:
- activate PLANNING_ECOLOGY_001;
- select work;
- admit work;
- grant authority;
- execute transformations;
- define a final planning ontology;
- establish that the candidate envelope is minimal or complete;
- establish that any stated leverage was actually achieved.

Its purpose is to make the reason for a proposed move visible before more formal
machinery is invoked.
