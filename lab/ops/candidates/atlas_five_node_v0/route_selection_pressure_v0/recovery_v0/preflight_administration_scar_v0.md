# ATLAS_ROUTE_SELECTION_001 — recovery preflight administration scar v0

The first non-realizing preflight attempt for the fresh recovery contract ran in
GitHub Actions as:

- run: `35461627162`
- job: `105946414575`
- checked-out commit: `4747bffd29256252762278934badb8cd4d6ef3c9`

The preflight reached the qualification-witness binding check and then failed
with:

```text
KeyError: 'run_id'
```

Cause: the preflight script read `qualification_witness.run_id`, while the
frozen contract stores the successful witness coordinates under
`qualification_witness.successful_witness.run_id`.

No producer was invoked.
No execution-evidence harness realization surface was invoked.
No A2/B2 route computation occurred.
No scientific observation or mechanical verdict was produced.

Therefore:

```text
PREFLIGHT ADMINISTRATION FAILURE
!=
SCIENTIFIC REALIZATION

FAILED PREFLIGHT
!=
A2/B2 CONSUMED
```

The repair is bounded to the preflight contract-reading path. Scientific
question, A2/B2 bytes, Atlas apparatus, producer, qualified harness, child
wrapper, observation surface, predicate, and claim ceiling remain unchanged.
