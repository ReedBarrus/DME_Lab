# AUTHORIZATION_TO_ACTIVE_001

Bounded apparatus for a later authorization-correspondence pressure. This surface is implementation only; the frozen experimental cells are not realized here.

## Target

```text
raw AO + raw E
→ derive CORRESPONDS(AO,E)
→ true  : initial ACTIVE(E) may materialize
→ false : ACTIVE(E) remains absent
```

The frozen correspondence relation is:

```text
AO exists
AND AO.execution_envelope_id == E.execution_envelope_id
AND AO.implementation_basis == E.implementation_basis
AND E.requested_consequence ∈ AO.allowed_consequences
AND AO.status == LIVE
```

No supplied `valid`, `authorized`, or `corresponds` field is accepted.

## Separation

```text
AO artifact != execution-state artifact
AO presence != AO↔E correspondence
correspondence != human authentication
ACTIVE materialization != execution
apparatus qualification != held-out pressure realization
```

The existing `execution_stop_latch_001/fixture_setup.py` is not used as the discriminator. This candidate derives correspondence first and writes the existing STOP-latch ACTIVE state representation only when the derived relation is true.

## Frozen future conditions

`fixtures/execution_envelope.json` is the common E fixture. `authorization_A.json` is the matching AO. `authorization_B1.json` through `authorization_B4.json` each vary exactly one claimed correspondence term. B0 is represented by AO absence and therefore has no fixture file.

These fixtures may be statically checked for shape and one-factor differences during apparatus qualification. Qualification must not pass them through `corresponds()` or `materialize_active_if_corresponding()`.

## Clean state

Every future realization must use a clean state root. If the target execution-state artifact already exists, the bounded materializer rejects rather than overwriting or interpreting it.

## Non-goals

```text
human authentication
authorization registry
general policy
delegation
retry / recovery
reauthorization
new-envelope issuance
Coordinator behavior
Workshop execution
STOP integration
scientific standing
```

## Qualification

```bash
python -m unittest tests.lab.test_authorization_to_active_001_apparatus -v
```

Qualification uses non-held-out dummy AO/E values for correspondence and materialization behavior. The frozen fixtures are only structurally compared.

## Held-out status after qualification

```text
A correspondence: UNOBSERVED
B0 correspondence: UNOBSERVED
B1 correspondence: UNOBSERVED
B2 correspondence: UNOBSERVED
B3 correspondence: UNOBSERVED
B4 correspondence: UNOBSERVED

A ACTIVE materialization: UNOBSERVED
B0-B4 ACTIVE materialization: UNOBSERVED

experimental result: NONE
```
