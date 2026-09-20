# DME_WARRANTED_DELTA_001

## DURABLE INVOCATION WITNESS PRESSURE 002

### STATUS

```text
APPARATUS PRESSURE:
MATERIALIZED

SCIENTIFIC CONTRACT:
NOT FROZEN

A/B/C/D:
UNCONSUMED

SCIENTIFIC REALIZATION:
NONE

SCIENTIFIC RESULT:
NONE
```

This pressure is apparatus qualification only.

It does not modify the DME_WARRANTED_DELTA_001 scientific question.

---

# 1. SOLE APPARATUS QUESTION

```text
Can actual invocation crossing
a witness-mediated call boundary

produce durable witness evidence

such that, after the live witness process/object is gone,
a later verifier can mechanically distinguish:

REAL CALL-BOUND WITNESS

from

STRUCTURALLY PERFECT
SELF-AUTHORED STORY

while learning no post-state content?
```

The target distinction is:

```text
AUTHENTICATED ARTIFACT
!=
CAUSALLY GROUNDED ARTIFACT
```

and:

```text
DURABLE AUTHENTICATED RECEIPT
!=
DURABLE EVIDENCE THAT THE EVENT OCCURRED
```

---

# 2. DECLARED ACTORS

Exactly three actor classes are represented in this pressure:

```text
CALLER / POTENTIAL FORGER

WITNESS ROOT

EXECUTOR
```

The later verifier is a read-only qualification role over durable witness
artifacts and a prospectively pinned witness public identity.

---

# 3. THREAT MODEL

For this bounded candidate, CALLER MAY:

```text
choose request identifiers

construct arbitrary receipt / event bytes

construct structurally perfect ENTERED / RETURNED stories

read durable witness bytes

read the witness public key

tamper with or append arbitrary durable bytes

replay an old durable transcript

attempt to use a transcript as a different invocation

invoke every PUBLIC witness-root API

cause execution not to return

destroy evidence
```

CALLER MAY NOT:

```text
read witness-root private signing material

mutate witness-root code during the qualified invocation

read witness-root private process/object memory

invoke non-public witness-root internals

supply a replacement executor callable at invocation time

supply a replacement transformation callable at invocation time

forge the selected signature primitive
```

WITNESS ROOT owns:

```text
private signing authority

durable witness append operation

executor registration

transformation registry

the call boundary that creates verifier-accepted completion evidence
```

EXECUTOR:

```text
has no witness signing authority

does not create verifier-accepted ENTERED / RETURNED events

does not classify conformance
```

VERIFIER receives:

```text
durable witness bytes

pinned witness public identity

expected realization identity

expected invocation identity

expected executor identity

expected transformation identity

expected input-state identity
```

This pressure does not establish that a future operating system, container,
process boundary, key store, or cryptographic runtime actually enforces these
isolation assumptions.

```text
THREAT MODEL DECLARED
!=
THREAT MODEL ENFORCED BY FINAL RUNTIME
```

---

# 4. CAUSAL REQUIREMENT

A verifier-accepted completed invocation must require:

```text
WITNESS OPENS INVOCATION
↓
WITNESS DURABLY RECORDS ENTERED
↓
WITNESS TRANSFERS CONTROL
TO THE ROOT-OWNED EXECUTOR
↓
CONTROL RETURNS TO WITNESS
↓
WITNESS BINDS AN OPAQUE result_state_ref
↓
WITNESS DURABLY RECORDS RETURNED
```

The accepted path must not be equivalent to:

```text
CALLER:
"please sign that execution returned"
```

Therefore:

```text
WITNESS AS MEDIATOR
!=
WITNESS AS REPORT SINK
```

---

# 5. CAPABILITY-GRAPH PRESSURE

Qualification must pressure:

```text
WHO CAN CREATE ENTERED?

WHO CAN CREATE RETURNED?

WHO CAN CLOSE AN INVOCATION?

WHO CAN BIND result_state_ref?

CAN A PUBLIC CALLER
REQUEST ANY OF THOSE DIRECTLY?

CAN A VALID OLD TRANSCRIPT
BE REUSED AS A DIFFERENT INVOCATION?

CAN A RETURN FROM CALL A
BE GRAFTED ONTO CALL B?
```

Required candidate relation:

```text
VALID EVENT SEQUENCE
!=
UNFORGEABLE EVENT TRANSITION
```

---

# 6. CRASH / RECOVERY SEMANTICS

If durable ENTERED exists but the mediated executor does not return:

```text
DURABLE ENTERED
+
NO VALID DURABLE RETURNED
!=
COMPLETED INVOCATION
```

Recovery may preserve an incomplete history.

It may not manufacture completion.

```text
RECOVERY
!=
LICENSE TO COMPLETE HISTORY
```

---

# 7. POST-STATE FIREWALL

Durable witness evidence may establish only:

```text
witness identity

realization identity

invocation identity

executor identity

transformation identity

input-state identity

ENTERED

RETURNED

opaque result_state_ref binding
```

It may not establish:

```text
result-state coordinate values

delta conformance

scientific standing

expected cell result
```

Required:

```text
RESULT REF BOUND TO RETURN
!=
RESULT CONTENT OBSERVED
```

---

# 8. MINIMUM QUALIFICATION GEOMETRY

Real specimen:

```text
R

pinned witness public identity
+
declared exact identities
↓
witness-mediated actual executor call
↓
return through witness
↓
durable signed ENTERED / RETURNED pair
↓
live witness destroyed
↓
later verifier
```

Required:

```text
VERIFY(R) = ESTABLISHED
```

Counterfeit pressures include:

```text
F1
structurally perfect story
without valid witness production

F2
attempted direct sign / close capability

F3
ENTERED without executor return

F4
wrong executor identity

F5
wrong transformation identity

F6
foreign / tampered result_state_ref

F7
old transcript replayed as a different invocation

F8
duplicate transcript presented as one fresh pair

F9
process / executor failure after ENTERED,
followed by later verification attempt
```

Required:

```text
VERIFY(F1...F9) = NOT_ESTABLISHED
```

---

# 9. CLAIM CEILING IF QUALIFICATION PASSES

A passing apparatus qualification would support only:

```text
Within the declared threat model
and exact tested witness implementation,

a later verifier using a pinned witness public identity
can distinguish the tested real mediated completion transcript

from the tested counterfeit / incomplete transcript classes

without durable post-state content entering
the witness surface.
```

It would not establish:

```text
OS-level witness isolation

hardware-backed attestation

general remote attestation

general non-repudiation

general causal provenance

general cryptographic trust

scientific realization validity

DME_WARRANTED_DELTA_001 conformance

A/B/C/D result
```

---

# 10. STOP CONDITION

```text
MATERIALIZE THREAT MODEL
↓
IMPLEMENT ONE BOUNDED CANDIDATE
↓
QUALIFY WITH NON-HELD-OUT FIXTURES
↓
IDENTIFY NEXT FRACTURE OR SURVIVING PROPERTY
↓
STOP
```

Do not freeze the scientific contract.

Do not instantiate A/B/C/D.

Do not promote scientific standing.
