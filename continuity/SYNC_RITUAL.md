# Synchronization Ritual v0

Purpose: make durable continuity not only available, but reliably instantiated at the start of consequential work.

This ritual is a consumer-start protocol. It does not create project standing, transfer authority, or imply shared internal state.

## Core distinction

```text
DURABLY_AVAILABLE
!=
RETRIEVED
!=
CONSUMED
!=
APPLIED
!=
BEHAVIORALLY_MATERIAL
```

The ritual exists to pressure the transition from durable availability to reliable task-local instantiation.

## Start ritual

Before consequential work, each continuity-aware consumer should perform:

```text
1. IDENTIFY_SELF
2. READ_CURSOR
3. READ_DELTA
4. ORIENT
5. RESOLVE_REQUIRED_REFS
6. DECLARE_LOCAL_CONTINUITY
7. WORK
```

### 1. IDENTIFY_SELF

Use only the named consumer identity for the current surface, e.g. `chatgpt`, `codex`, or `grep-kitty`.

Do not silently borrow another consumer's cursor.

### 2. READ_CURSOR

Read `continuity/cursors/<consumer>.json`.

If missing, malformed, or ahead of the event stream, report continuity state as unresolved before consequential work.

### 3. READ_DELTA

Read all continuity events strictly after `last_seen_event_id`.

If no events exist, state that no recorded continuity delta is present. Do not infer that no activity occurred outside the stream.

### 4. ORIENT

Produce a compact local orientation with exactly these semantic slots:

```text
SINCE_LAST_SEEN:
- recorded activity that matters to this task

CURRENTLY_RELEVANT:
- unresolved pressure / active work / changed artifact relevant now

MUST_NOT_ASSUME:
- reported deltas or summaries that still require source inspection

MISSING_FOR_THIS_TASK:
- required coordinates not supplied by the delta
```

This orientation is a task-local projection, not an authoritative project summary.

### 5. RESOLVE_REQUIRED_REFS

Follow only durable refs required by the current operation.

Examples:

- inspect a commit when current code state matters;
- inspect a trace when observed execution matters;
- inspect an adjudication artifact when bounded standing matters.

Do not expand into broad repository reconstruction unless a missing dependency requires it.

### 6. DECLARE_LOCAL_CONTINUITY

Before consequential work, the consumer should be able to state:

```text
I am synchronized through: <event_id or NONE>
I have consumed: <bounded delta summary>
I still need to verify: <refs or NONE>
My present task-local frontier is: <frontier or UNRESOLVED>
```

This declaration is the operational meaning of "felt continuity" in v0: a legible task-local sense of where this invocation joins the retained activity stream.

It is not a claim of consciousness, memory identity, or shared global cognition.

### 7. WORK

Only after the above should the consumer perform consequential work that depends on continuity.

After work:

```text
append consequential activity
-> verify event append
-> advance cursor only through events actually consumed
```

## Failure behavior

The ritual should fail legibly rather than silently reconstructing around a continuity fault.

Pressure at least these failures:

```text
cursor missing
cursor stale
cursor ahead of stream
event stream unavailable
event malformed
required ref missing
reported standing treated as verified without source
consumer skips delta and begins work
consumer reads delta but does not apply a task-relevant distinction
```

A continuity failure does not automatically prohibit all work. It blocks only work whose legitimacy depends on the missing continuity coordinate.

## CONTINUITY-002 — Instantiation Reliability

Question:

> Does the durable continuity surface become reliably instantiated before consequential work without Reed manually reminding the consumer?

Compare repeated fresh invocations and interruptions.

Measure:

```text
startup attempts
delta read success
orientation produced
required refs followed when needed
continuity faults surfaced before action
manual Reed prompts required
false continuity assumptions
task errors attributable to missed continuity
```

The carrier begins to earn reliable instantiation only if normal consumer startup repeatedly performs the ritual without manual transport by Reed.

## Non-claims

This ritual does not establish:

- automatic delivery;
- global shared state;
- semantic agreement between consumers;
- inter-agent coordination;
- consciousness or subjective continuity;
- authority widening;
- truth from repetition.

Those remain pressure territory.
