# DME_WARRANTED_DELTA_001

## DURABLE INVOCATION WITNESS QUALIFICATION 002

### AUTHORIZED PHASE

```text
BOUNDED APPARATUS DESIGN / IMPLEMENTATION / QUALIFICATION

NOT AUTHORIZED:
contract freeze
A/B/C/D realization
scientific promotion
merge to main
```

### BASIS

```text
branch:
dme-warranted-delta-001-apparatus-v0

pressure materialization commit:
9b7378a4cc01ef371c00466caa0149e103994682

implementation commit:
569e95b691016511f1638736574816a661a6a4ec

qualification-test commit:
38070df493113bfc82bfc00a087530dff35376ee

expanded-threat characterization commit:
dfffd724591bdee65c87c1ef7cc56d089c883ded
```

Exact committed blobs:

```text
pressure:
cc6e99aad31f195b17f423bba73c8c81d2fe5dd0

durable_invocation_witness.py:
f6a8360dcf370299d48bc37024e463b079fdf33c

declared-model qualification test:
04664c8c101135ab405308536e72e7d56cb76847

expanded-threat characterization:
a8ecb862e57363d891a1f95bd628efb3a7cb2228
```

The locally executed files reproduced the committed Git blob identities exactly.

---

# 1. DECLARED-MODEL QUALIFICATION

Executed:

```text
python -m unittest -v
tests.lab.test_dme_warranted_delta_001_durable_invocation_witness

10 tests
10 passed
0 failed
```

Within the prospectively materialized threat model, the candidate established:

```text
real witness-mediated call
→ durable ENTERED / RETURNED pair
→ later verification after live root deletion

structurally perfect unsigned story
→ NOT_ESTABLISHED

no public sign / close API

unknown transformation
→ no witness event

ENTERED + executor failure
→ NOT_ESTABLISHED

tampered result_state_ref
→ NOT_ESTABLISHED

old transcript used as different invocation
→ NOT_ESTABLISHED

duplicated transcript
→ NOT_ESTABLISHED

wrong pinned public key
→ NOT_ESTABLISHED

durable witness bytes contain no tested post-state content
```

Thus, under the declared assumption that caller cannot invoke non-public
witness-root internals:

```text
DECLARED-MODEL DURABLE VERIFICATION:
SURVIVES TESTED SCOPE
```

---

# 2. EXPANDED-THREAT PRESSURE

The declared threat model explicitly stated:

```text
CALLER MAY NOT:
invoke non-public witness-root internals
```

The implementation did not mechanically enforce that boundary against a
same-process reflective Python caller.

A separate characterization pressure used the exact committed implementation
and reflectively obtained:

```text
_DurableWitnessRoot__append_signed_event
```

The adversary then produced a correctly signed ENTERED / RETURNED pair directly,
without invoking the executor.

Observed:

```text
executor_calls:
0

later verifier verdict:
ESTABLISHED
```

The characterization test intentionally passes only if this fracture remains
observable.

Executed together:

```text
python -m unittest -v
tests.lab.test_dme_warranted_delta_001_durable_invocation_witness
tests.lab.test_dme_warranted_delta_001_durable_invocation_witness_expanded_threat

11 tests
11 passed
0 failed
```

The eleventh passing test is evidence of the fracture, not evidence that the
mechanism is acceptable.

---

# 3. MECHANICAL RESULT

```text
THREAT MODEL DECLARED
!=
THREAT MODEL MECHANICALLY ENFORCED
```

and:

```text
PRIVATE-BY-CONVENTION PYTHON METHOD
!=
PROTECTED WITNESS CAPABILITY
```

The current candidate permits, under same-process reflective access:

```text
VALID SIGNATURE
+
VALID EVENT SHAPE
+
VALID PINNED PUBLIC KEY

WITHOUT

EXECUTOR INVOCATION
```

Therefore:

```text
AUTHENTICATED ARTIFACT
!=
CAUSALLY GROUNDED ARTIFACT
```

was not merely represented; the implementation produced the counterfeit
condition under the expanded threat pressure.

---

# 4. DISPOSITION

```text
DURABLE INVOCATION WITNESS 002

DECLARED-MODEL QUALIFICATION:
PASS

POST-STATE FIREWALL IN DURABLE JOURNAL:
SURVIVES TESTED SCOPE

LATER VERIFICATION:
WORKS FOR TESTED REAL TRANSCRIPT

SAME-PROCESS CAPABILITY ISOLATION:
FRACTURE

COUNTERFEIT VALID COMPLETION
WITHOUT EXECUTOR CALL:
OBSERVED

FINAL DURABLE CAUSAL WITNESS:
NOT QUALIFIED

EXECUTION-PROVENANCE MECHANISM:
DO NOT PIN FOR FREEZE

APPARATUS SUFFICIENTLY PINNED FOR FREEZE:
NO

A/B/C/D:
UNCONSUMED

CONTRACT FREEZE:
NO

SCIENTIFIC REALIZATION:
NONE

SCIENTIFIC RESULT:
NONE
```

---

# 5. NEXT BOUNDED PRESSURE

The next apparatus question is now narrower:

```text
CAN WITNESS-ROOT SIGNING / COMPLETION CAPABILITY
BE MECHANICALLY ISOLATED FROM THE CALLER

SUCH THAT THE CALLER CANNOT
DIRECTLY OR REFLECTIVELY OBTAIN

VERIFIER-ACCEPTED RETURNED

WITHOUT CONTROL ACTUALLY RETURNING
THROUGH THE WITNESS-MEDIATED EXECUTOR PATH?
```

Candidate mechanism family remains unselected.

Possible future mechanisms may include a separately isolated witness process,
restricted IPC surface, or another mechanically protected root, but this receipt
does not select one.

Stop before repair, freeze, or held-out realization.
