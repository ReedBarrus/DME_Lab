# NIGHT_ROAM_SELECTOR_ATTRIBUTION_AUTHENTICATION_001

## Status

```text
PRESSURE DESIGN ONLY
IMPLEMENTATION REPAIR: NONE
EXECUTION AUTHORITY: NONE
STANDING EFFECT: NONE
```

## Observed basis

Development campaign head inspected:

```text
b6fb925e3a3590d094d65770e3260d9c46b427c0
```

`tools/envelope_selection_v0.py` defines:

```text
EXECUTIVE = "REED"
```

and accepts a selection event when its `selected_by` field equals that literal value. Both `build_selection_event()` and `SelectionStore._validate()` enforce equality to the literal, but the event contains no independently established signer, authenticated principal, capability, session identity, or other provenance relation establishing who actually caused the event to be formed or appended.

The qualified S10 pressure demonstrates rejection of `selected_by = LABBOIB`. It does not discriminate a genuine Reed-originated event from bytes produced by another caller containing `selected_by = REED`.

## Compressed assumption

```text
SELECTOR LABEL ACCEPTED
!=
SELECTOR IDENTITY AUTHENTICATED

EVENT ATTRIBUTES selected_by = REED
!=
REED CAUSED / APPROVED THE EVENT

SCHEMA-VALID EXECUTIVE ATTRIBUTION
!=
HUMAN ATTENTION PROVENANCE
```

This does not establish that authentication belongs inside `EnvelopeSelection_v0`. It establishes only that the current fixture cannot earn an authentication claim from literal-field validation.

## Smallest discriminating pressure

Hold campaign identity, request identity, selection kind, basis refs, and all event bytes except event-formation provenance constant.

### A — ordinary fixture construction

Construct an otherwise-valid event through the current helper with default `selected_by = REED` and append it.

Expected current behavior:

```text
ACCEPTED
```

### B — alternate caller, same asserted selector

From an independent test call path with no Reed-authentication evidence, construct byte-equivalent valid selection content carrying:

```text
selected_by = REED
```

and append it under a fresh `selection_id`.

Question:

```text
CAN THE STORE DISTINGUISH B FROM A?
```

Under the inspected v0 mechanism, no discriminator is presently visible in the event contract or append boundary.

### C — alternate caller, alternate selector label

Construct the same event with:

```text
selected_by = LABBOIB
```

Expected current behavior:

```text
REJECTED
```

This is the already-qualified attribution-policy cell and acts as a control.

## Observables

Record only:

```text
A append accepted / rejected
B append accepted / rejected
C append accepted / rejected
exact rejection reason
stored event bytes
whether any independent selector-provenance evidence was consumed
```

Do not infer human intent from the label.

## Outcome interpretation

If A and B are both accepted while C is rejected:

```text
EARNED:
current v0 enforces an allowed selector ATTRIBUTE value
but does not distinguish authenticated event origin.
```

If B is rejected because an already-existing independent provenance mechanism is mechanically consumed:

```text
EARNED:
the tested append boundary discriminates asserted selector label
from the tested alternate-origin event under that mechanism.
```

If B cannot be constructed because a lower layer supplies authenticated provenance before this API:

```text
EARNED:
only that the missing discriminator may live outside this module;
trace and freeze that boundary before changing this candidate.
```

## Claim ceiling

A passing pressure may establish only the exact selector-attribution/authentication behavior of the tested boundary.

It does not establish:

```text
general identity
human intent
legal authorization
execution authority
standing
priority
packet preparation authority
secure multi-user operation
```

## Dangerous neighboring inference

```text
selected_by = REED
→ REED selected this
→ Reed authorized downstream work
```

Neither arrow is earned by literal-field validation.

Likewise:

```text
LACK OF AUTHENTICATION IN THIS MODULE
!=
SYSTEM MUST ADD AUTHENTICATION HERE
```

The correct repair boundary, if any, must be earned from the composition path.

## Mutation boundary

This artifact changes no runtime, schema, workflow, selector policy, authentication mechanism, authority relation, standing relation, scheduler, wake path, packet preparation, or external effect.
