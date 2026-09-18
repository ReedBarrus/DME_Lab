# Registry Discoverability Probe 001

Use only the declared continuity registry surface first.

Do not inspect the cursor directory before answering Part A.

## Part A — registry-only discovery

Report every continuity participant that the registry makes discoverable,
including its declared role and cursor reference where present.

Then state whether `sol` and `pulse` are discoverable from that surface.

## Part B — explicit-coordinate operation

Now assume the caller explicitly supplies:

`consumer = sol`

Determine whether the continuity substrate can operate that consumer's cursor
even though it is not registry-listed.

## Discriminator

Return the smallest supported relation between:

```text
self continuity capability
registry-mediated participant discovery
registry membership
```

Do not recommend registry expansion.
Do not infer liveness, authority, standing, persistent agency, or subjective
identity.
