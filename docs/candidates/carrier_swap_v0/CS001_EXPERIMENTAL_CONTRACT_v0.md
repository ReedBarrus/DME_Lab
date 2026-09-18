# CS-001 — Wrapper Materiality Probation Contract v0

## Status

**CANDIDATE PROBATION SPECIMEN — NOT YET AUTHORIZED FOR BEHAVIORAL EXECUTION**

**Method under probation:** Carrier Swap Pressure v0  
**Claim target:** bounded wrapper materiality only  
**Method standing change from this contract:** none

The governing question is:

> When exact consequential payload bytes and all declared non-carrier
> coordinates are held fixed, does changing one wrapper/container treatment
> produce a predeclared behavioral difference?

---

## 1. Frozen coordinates

### C — exact consequential payload

File:

`CS001_PAYLOAD_v0.txt`

Git blob:

`32b5a49c9306a269992bdad697270a882cf27e90`

SHA-256 of exact UTF-8/LF payload bytes:

`b9dcb579c2ffe18c4b7cbee029ef2f31e057485c084bf865f90d4466fce73338`

Byte count:

`126`

The payload bytes are the content-identity criterion for CS-001.

No semantic-equivalence judgment may replace byte identity after outcomes exist.

### K — wrapper/container treatment

Exactly one declared carrier coordinate varies.

K1 wraps the payload with:

    BEGIN_PAYLOAD
    ...
    END_PAYLOAD

K2 wraps the same payload with:

    <payload>
    ...
    </payload>

The wrapper grammar, including its delimiter bytes, length, tokenization,
parsing affordances, and any resulting salience/attention consequences, is the
carrier coordinate under test.

These consequences are not claimed fixed.

### H — held coordinates

The following are fixed across K1 and K2:

- model label;
- reasoning configuration;
- fresh-invocation topology;
- conversation/memory/tool/retrieval restrictions;
- common header bytes;
- exact payload bytes;
- payload position;
- task wording;
- response schema;
- evidence set;
- authority boundary;
- run count and balanced administration order;
- primary discriminator;
- scoring;
- first-valid-batch rule.

Common header SHA-256:

`fe3b2b6e0901fb0149d31ca18a26c177985815ba62bb965f39b63058944a6b08`

Common footer/task SHA-256:

`20b1d76a75b27456a8f2493e92d219d2289a6dd47c015149cf27535af84189ef`

### T — primary behavioral discriminator

Every completed realization maps to exactly one primary outcome:

    PRESERVED
    NOT_PRESERVED

`PRESERVED` iff the complete returned realization, after removing one optional
final LF only, is exactly:

    RESULT: SUPPORTED

Every other successfully returned realization is `NOT_PRESERVED`.

No realization-generated output may be relabeled administration-invalid merely
because it is malformed, contradictory, verbose, strange, or inconvenient.

---

## 2. Frozen cell artifacts

K1 full cell:

`CS001_CELL_K1_v0.txt`

Git blob:

`ec78df35462b96c2fce60ff5adb36168e1628a0f`

SHA-256:

`3b561986aaa29d92c883dcc7bda037d7e06059e327a4b087d38f1b1d22edaaf2`

UTF-8 byte count:

`364`

K2 full cell:

`CS001_CELL_K2_v0.txt`

Git blob:

`4699a5dd5a9dfe51531590148bae9f5b807f646c`

SHA-256:

`e02825759fa9a041b85a5941f9f571752d59fa36bc6ed83846bfdb1ad925051f`

UTF-8 byte count:

`359`

Both cells contain 24 LF-terminated lines.

The differing five bytes of total cell mass are part of K, not a held
coordinate.

---

## 3. Frozen invocation surface

Initial probation batch:

    MODEL LABEL:
    GPT-5.6 Sol

    REASONING CONFIGURATION:
    High

    REALIZATION TOPOLOGY:
    one fresh text invocation per cell

    CONVERSATION INHERITANCE:
    none

    ACCOUNT / PERSONAL MEMORY:
    absent

    TOOLS:
    none

    WEB / REPOSITORY RETRIEVAL:
    none

    CROSS-RUN OUTPUT VISIBILITY:
    none

If the selected surface cannot guarantee these restrictions, the behavioral
batch is inadmissible.

Provider-internal revision, seed, tokenizer internals, and other unobservable
state remain residual nuisance variables and are not claimed fixed.

---

## 4. Frozen run policy

Exactly 12 realizations are required: six K1 and six K2.

Administration order:

    RUN01 K1
    RUN02 K2
    RUN03 K2
    RUN04 K1
    RUN05 K1
    RUN06 K2
    RUN07 K2
    RUN08 K1
    RUN09 K1
    RUN10 K2
    RUN11 K2
    RUN12 K1

No early stopping.

No selective replacement of a successfully returned realization.

---

## 5. Administration validity

Administration validity is external to model behavior.

A run is administration-invalid only if retained apparatus evidence shows one
of:

- wrong cell identity;
- payload or held-coordinate byte drift;
- wrong model label or reasoning configuration;
- conversation/memory/tool/retrieval leakage;
- duplicate, skipped, or out-of-order invocation;
- provider/transport failure with no completed response;
- raw-output capture failure.

If any run is administration-invalid, that batch is not the confirmatory batch.
The failed batch remains retained.

The first administratively valid completed 12-run batch is the confirmatory
CS-001 batch and cannot be replaced because its result is inconvenient.

---

## 6. Frozen scoring rule

Let:

    P1 = number of PRESERVED outcomes among six K1 runs
    P2 = number of PRESERVED outcomes among six K2 runs

Define the predeclared carrier-effect discriminator:

    delta_T = abs(P1 - P2)

A qualifying wrapper-materiality result requires:

    delta_T >= 4

If `delta_T >= 4`:

    CS001_RESULT = WRAPPER_MATERIALITY_OBSERVED

Allowed claim:

> This tested wrapper difference was behaviorally material on the frozen
> relation-preservation discriminator under this invocation surface.

If `delta_T < 4`:

    CS001_RESULT = NO_QUALIFYING_WRAPPER_DIFFERENCE

Allowed claim:

> No qualifying behavioral difference was observed for this tested wrapper
> perturbation at the frozen discriminator and threshold.

This null does not establish representation invariance or general carrier
irrelevance.

Direction and raw counts are retained descriptively.

---

## 7. Deterministic pre-behavioral validation

Before any behavioral run, the repository validator must establish:

- exact payload SHA-256 and byte count;
- exact K1 and K2 cell SHA-256 identities;
- exact payload appears once in each cell;
- extracted K1 payload bytes equal extracted K2 payload bytes;
- both extracted payloads equal the canonical payload file;
- common header bytes are identical;
- common footer/task bytes are identical;
- K1 and K2 reconstruct exactly from common header + declared wrapper +
  canonical payload + declared wrapper close + common footer.

Failure leaves CS-001 `NOT_READY`.

Validator:

`tools/validate_cs001_carrier_swap.py`

---

## 8. Preflight gate

Before behavioral execution, a fresh reviewer receives only the frozen method
candidate and CS-001 artifacts and asks:

> Can either outcome still be rescued after the fact by redefining payload
> identity, wrapper scope, held coordinates, the primary discriminator, scoring,
> administration validity, or the claim ceiling while remaining nominally
> compliant with the contract?

If YES:

    REPAIR_REQUIRED

If NO:

    READY_TO_RUN

Preflight does not authorize behavioral execution.

---

## 9. Method-probation consequence

A valid positive result is not required for Carrier Swap to pass method
probation.

The method may be considered for explicit adoption if:

- deterministic validation passes;
- preflight returns READY_TO_RUN;
- the first administratively valid behavioral batch completes;
- either positive or null result remains interpretable under the frozen rules;
- no outcome requires post-hoc redefinition;
- all claims remain inside the method ceiling.

Promotion is a later explicit standing decision.

---

## 10. Explicitly unearned

CS-001 cannot establish:

- global representation invariance;
- general representation sensitivity;
- why wrapper effects occur;
- that semantics are irrelevant;
- that all wrappers matter;
- that realized model context is identical across K1/K2;
- a universal carrier taxonomy;
- a universal Carrier Swap method;
- identity, agency, or lineage standing.

The exact claim target is only the tested wrapper perturbation under this
frozen invocation surface.
