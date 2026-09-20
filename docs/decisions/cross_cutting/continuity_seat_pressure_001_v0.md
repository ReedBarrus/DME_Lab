# Continuity Seat Pressure 001 — Independent Cursor Consumers

**Status:** ACTIVE EXPERIMENTAL PRESSURE  
**Basis commit:** `1000a90da1b029800e59fa30974cc87c5b6d24d2`  
**Initial continuity head:** `CE-000026`

## Question

Can the current continuity substrate support two additional independent
cursor-bearing consumers without first widening the semantic registry or
creating shared-cursor coordination?

The immediate practical need is concrete:

- the hourly continuity pulse has been reading from the ChatGPT cursor without
  acknowledging;
- the current Sol context is acting as a distinct semantic participant;
- sharing `chatgpt`'s cursor would allow one invocation or automation to
  acknowledge continuity on behalf of another.

## Distinctions under pressure

```text
cursor-bearing consumer
!=
registry-listed seat
!=
invocation identity
!=
scheduled automation
```

and:

```text
observe event
!=
consume event
!=
apply event
!=
acknowledge event
```

## Minimal intervention

Add two independent cursor files only:

```text
continuity/cursors/sol.json
continuity/cursors/pulse.json
```

Both are explicitly positioned FROM_HEAD at `CE-000026`.

This means neither consumer claims to have consumed the earlier retained
history. Events appended after CE-000026 become their first ordinary delta.

Do **not** add either consumer to `continuity/registry.json` yet.

The current registry remains a two-seat v0 projection for
`chatgpt-main` and `codex-main`.

## Pulse behavior under pressure

The hourly pulse may:

1. read only the immediate next unread event after its own cursor;
2. follow authoritative refs only when needed for that event;
3. produce at most one bounded candidate observation;
4. advance only `continuity/cursors/pulse.json`, and only after actual
   consumption of that exact next event.

It may not:

- jump to latest;
- advance another consumer's cursor;
- mutate project standing;
- authorize work;
- select scientific pressure;
- change registry identity;
- write any repository path other than its own cursor as part of acknowledgement.

If a required ref cannot be resolved, it must not acknowledge the event.

## Sol behavior under pressure

The Sol consumer is available for manual/contextual continuity use.

No automatic acknowledgement rule is attached to it. Its cursor may advance
only when the current Sol invocation actually consumes the next unread event.

## Why registry expansion is deferred

The current continuity tool intentionally validates exactly two registry
identities.

Changing that validator would be a different pressure:

```text
additional cursor consumers work
?
additional registry seats are required
```

The first question should be answered before modifying registry semantics.

## Success condition

The pressure gains evidence if the new consumers can independently:

```text
read their own delta
→ preserve task-local orientation
→ acknowledge only what they consumed
→ remain isolated from other cursors
```

without requiring registry expansion.

## Failure / escalation conditions

Escalate if:

- one consumer can accidentally advance another consumer's coordinate;
- pulse acknowledgement requires broader repository mutation;
- registry absence makes correct consumer operation impossible;
- cursor identity cannot be kept distinct from invocation or role identity;
- automation repeatedly re-reads consumed events because durable acknowledgement
  cannot be performed.

No persistent-agent, shared-state, coordination, or autonomous-research claim is
earned by creating these cursors.
