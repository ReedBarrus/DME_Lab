# AFFORDANCE_ADMISSIBILITY_PRESSURE_001

## Status

PRESSURE DESIGN ONLY

No Cockpit implementation repair, control invocation, selection, assignment, release, bell, wake, authority, standing, scheduler, execution, deployment, or promotion is authorized by this artifact.

## Exact observed basis

Basis commit:

`a9b4ed3d1086f7a7042ecdb7d358109f53938722`

`src/cockpit/observer/perceptual_instrument.mjs::deriveContextualAffordances()` derives control-facing affordances from selected address kinds plus a small amount of snapshot state:

- FOCUS: one addressed request and request absent from `current_selection`
- ASSIGN: one addressed request + one addressed seat and request present in `current_selection`
- RELEASE / RING: one addressed outstanding assignment

The function labels each of these `QUALIFIED_CONTROL_PREVIEW`.

The Cockpit control membrane is separately qualified and is responsible for exact preview construction, explicit confirmation, current-state revalidation, and append through existing stores. Therefore the current evidence does not establish that the shallow perceptual predicates above are extensionally equal to control-preview admissibility.

## Proposed distinction

```text
CONTEXTUAL AFFORDANCE PRESENT
!=
CONTROL PREVIEW ADMISSIBLE

CONTROL PREVIEW ADMISSIBLE
!=
CONTROL COMMIT ADMISSIBLE
```

The first relation is the pressure target. The second is retained as a causal membrane and is not under test here.

## Why current evidence does not settle it

Existing perceptual tests establish that affordances appear for simple positive fixtures. They do not pair each rendered affordance with the real control adapter's preview/revalidation result under adversarial state variants.

A label containing `QUALIFIED_CONTROL_PREVIEW` is not mechanical evidence that the underlying control membrane would admit the same action.

## Smallest discriminating pressure

For each control verb, hold the addressed coordinates fixed and vary only one control-relevant state predicate that the control adapter is expected to inspect but the perceptual affordance function does not necessarily inspect.

At minimum:

### Cell A — positive agreement

Construct a fixture already known to satisfy the real control adapter's preview requirements.

Observe:

1. whether `deriveContextualAffordances()` exposes the verb;
2. whether the real adapter can construct the corresponding preview from the same fixture and exact coordinates.

### Cell B — stale / invalid control basis

Preserve the same address kinds and identities while changing one current-state fact so the real adapter rejects preview or requires re-preview.

Observe the same two outputs.

### Cell C — ambiguous or already-satisfied relation

Preserve the same selected coordinate kinds while introducing a state in which the named relation is already satisfied, released, superseded, or otherwise non-admissible according to the real adapter.

Observe affordance presence versus preview admissibility.

### Cell D — control unavailable

Set `controlConfigured = false` while preserving all coordinates and operational state. Confirm no control affordance is exposed and no inference is made about whether the underlying action would otherwise be admissible.

## Expected observable matrix

```text
AFFORDANCE  PREVIEW
present     admitted   -> agreement in tested cell
present     rejected   -> affordance/admissibility divergence demonstrated
absent      admitted   -> perceptual false-negative demonstrated
absent      rejected   -> agreement in tested cell
```

## Earned claim ceiling

A divergence may earn only:

> The current perceptual affordance predicate is not extensionally equivalent to control-preview admissibility for the tested verb and state cell.

Agreement across tested cells may earn only bounded agreement for those cells. It does not establish universal equivalence.

Neither outcome earns authority, action priority, automatic control invocation, or commit admissibility.

## Dangerous neighboring inference

Do not infer:

```text
BUTTON / AFFORDANCE IS VISIBLE
=> ACTION IS CURRENTLY VALID
=> ACTION IS AUTHORIZED
=> ACTION WILL COMMIT
=> CONSEQUENCE WILL OCCUR
```

Also do not repair this by duplicating the control adapter's full policy into the perceptual layer unless a later contract explicitly earns that architecture. A safer eventual relation may be explicit affordance uncertainty or a read-only query into the qualified control membrane.

## Future campaign worthiness

YES, if any divergence is observed. This is directly relevant to Cockpit dogfood because perceptual confidence must not outrun the qualified control membrane.

If all bounded cells agree, retain the distinction and expand pressure only if future verbs or control predicates make the equality assumption consequential.
