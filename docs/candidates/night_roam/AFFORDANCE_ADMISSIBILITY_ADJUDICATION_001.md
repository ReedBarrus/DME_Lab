# AFFORDANCE_ADMISSIBILITY_ADJUDICATION_001

## Status

```text
PRESSURE:
EXECUTED

DIVERGENCE:
DEMONSTRATED

REPAIR:
BOUNDED LEGIBILITY REPAIR

CONTROL POLICY DUPLICATION:
NONE

AUTHORITY EFFECT:
NONE

EXECUTION EFFECT:
NONE
```

## Basis

The pressure began from:

```text
cockpit-perceptual-instrument-campaign-v0
a9b4ed3d1086f7a7042ecdb7d358109f53938722
```

After topology-representability resolution advanced the campaign, this branch
was recomposed against the resulting perceptual state rather than relying on
the stale original base.

Composed pressure head:

```text
5b28d11d7bed1fdcc0ff5cade18e5b80f62d0915
```

## Mechanical divergence

The perceptual layer derives contextual control verbs from shallow selected
address / snapshot predicates.

For an outstanding assignment with:

```text
preparation_kind = DRAFT_PACKET
```

the perceptual layer can expose:

```text
RELEASE
RING
```

because the assignment is an exact currently outstanding address.

The qualified control adapter independently requires for `RING`:

```text
assignment_state = OUTSTANDING
wake_eligible = true
preparation_kind = RESOLVE_REFS
```

The executable control pressure now constructs a real outstanding
`DRAFT_PACKET` assignment and confirms that exact `RING` preview is rejected.

Therefore the tested relation is mechanically established:

```text
CONTEXTUAL AFFORDANCE PRESENT
!=
CONTROL PREVIEW ADMISSIBLE
```

## Repair

The perceptual layer no longer labels FOCUS / ASSIGN / RELEASE / RING as:

```text
QUALIFIED_CONTROL_PREVIEW
```

They are now labeled:

```text
effect:
CONTROL_PREFILL_ONLY

admissibility:
UNVERIFIED_UNTIL_EXACT_PREVIEW
```

The UI may still expose a useful contextual verb and prefill the already
qualified control membrane.

It may not claim that the exact preview will be admitted.

The control membrane remains the owner of:

```text
exact preview construction
current-state checks
preview identity
confirmation
revalidation before append
```

No control-adapter policy was copied into the perceptual layer.

## Executed evidence

Perceptual workflow on exact composed head:

```text
COCKPIT_PERCEPTUAL_INSTRUMENT_001
run 35557554789
job 106204039415
SUCCESS
```

Relevant results include:

```text
topology representability exact-basis pressure:
PASS

control affordances are prefill candidates, not admissibility claims:
PASS

perceptual instrument tests:
11 / 11 PASS

observer tests:
39 / 39 PASS

control UI tests:
8 / 8 PASS

control adapter tests within workflow:
13 / 13 PASS

live runtime projection:
9 / 9 PASS

development horizon projection:
11 / 11 PASS
```

Control workflow on the same head:

```text
COCKPIT_CONTROL_ADAPTER_001
run 35557554829
job 106204039612
SUCCESS
```

The new exact rejection cell:

```text
test_c13_ring_preview_rejects_non_resolve_refs_assignment
PASS
```

and the control-adapter suite reports:

```text
13 / 13 PASS
```

## Earned claim

```text
FOR THE TESTED CONTROL SURFACE,

A CONTEXTUAL COCKPIT VERB MAY BE PRESENT
WITHOUT THE QUALIFIED CONTROL MEMBRANE
ADMITTING AN EXACT PREVIEW.

THE PERCEPTUAL SURFACE NOW LABELS
THOSE VERBS AS PREFILL CANDIDATES,
NOT AS PREVIEW-ADMISSIBILITY VERDICTS.
```

## Not earned

This does not establish:

```text
universal affordance/admissibility equivalence
commit admissibility from preview admissibility
authority from visible controls
priority from visible controls
automatic invocation
automatic assignment
automatic bell / wake
```

## Conserved scars

```text
CONTEXTUAL AFFORDANCE PRESENT
!=
CONTROL PREVIEW ADMISSIBLE

CONTROL PREVIEW ADMISSIBLE
!=
CONTROL COMMIT ADMISSIBLE

VISIBLE
!=
AUTHORIZED

LEGIBILITY
MUST NOT
OUTRUN MECHANICAL WARRANT
```
