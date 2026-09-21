# TWO_LANE_COORDINATION_001 — Operating Bootstrap

The qualified coordination substrate does not itself create an occupant,
authority grant, or active work claim.

Two operating branches may be created from the exact qualified coordination
head:

```text
LANE_A
horizon:
Cockpit / coordination / operator interaction

LANE_B
horizon:
seat continuity / invocation recovery / successor-cost pressure
```

Each begins:

```text
status = READY_UNCLAIMED
occupant_binding = null
active_work_claim = absent
peer_cursor = absent
```

A future explicitly assigned invocation activates only its own lane.

Activation sequence:

```text
reconstruct exact lane branch
→ bind current invocation by explicit human assignment
→ create exact ACTIVE work claim
→ read current peer lane claim
→ retain peer cursor
→ run pre-mutation guard
→ separately verify system-write authority
→ mutate only inside granted envelope
```

The first lane may be activated while the other remains READY_UNCLAIMED.

When both are ACTIVE:

```text
parallel isolated development:
allowed within separately granted envelopes

authoritative integration:
serialized
```

No lane may infer occupancy from seeing this bootstrap document.
