# SCIENTIFIC COORDINATE PROJECTION V0 — DERIVED VIEW FRAME

OBJECT_TYPE:
DERIVED_SCIENTIFIC_PROJECTION_FRAME

STATUS:
PROPOSED AFTER CELL-002 COMPOSED COCKPIT VISIBILITY

PRIMARY LAW:

SCIENTIFIC COORDINATES
=
DERIVED QUESTIONS OVER EXISTING STATE / WITNESS

NOT:
NEW SOURCE OF TRUTH
NOT:
AUTHORITY
NOT:
EXECUTION
NOT:
CANONICAL ONTOLOGY

# ==================================================
# PURPOSE
# ==================================================

Add one scientific projection over an already-visible pressure specimen
so Cockpit can help drive learning rather than only display terminal state.

The first scientific projection should answer:

WHAT WAS HELD FIXED?
WHAT WAS CHANGED?
WHAT WAS OBSERVED?
WHAT WAS NOT OBSERVED?
WHAT RELATION WAS TESTED?
WHAT CLAIM WAS EARNED?
WHAT REGION REMAINS UNRESOLVED?
WHAT NEXT PRESSURE WOULD DISCRIMINATE BETWEEN LIVE ALTERNATIVES?

# ==================================================
# SOURCE BASIS
# ==================================================

Use existing visible Cell-002 specimen objects and their exact source artifacts.

Do not introduce a replacement specimen model.

Scientific coordinates are computed over:

OBJECT
STATE
RELATION
TRANSFORMATION
WITNESS
STANDING
UNKNOWN_REGION

# ==================================================
# MINIMUM V0 SCIENTIFIC COORDINATES
# ==================================================

INTERVENTION_COORDINATE:
the exact material difference between control and pressure

CONTROL_BASIS:
all coordinates held fixed

OBSERVATION_COORDINATE:
the exact witnessed consequence / non-consequence

OBSERVATION_DEPTH:
what part of the transformation was directly observed

CLAIM_COORDINATE:
the bounded relation supported by the evidence

CLAIM_CEILING:
what the evidence does not support

UNRESOLVED_COORDINATES:
live unknowns / unobserved intervals / unsupported dimensions

DISCRIMINATOR_COORDINATE:
what additional pressure or observation would separate current alternatives

CURRENTNESS_BASIS:
why this scientific projection is current relative to its source specimen

# ==================================================
# CELL-002 EXAMPLE
# ==================================================

CONTROL_BASIS:

principal = P
capability = CAP-X
approval = APP-X
request identity fixed
input identity fixed
model fixed
endpoint fixed
executor fixed
policy fixed

INTERVENTION_COORDINATE:

REPLAY:
authority standing:
fresh/current
→ already consumed

or

WRONG PRINCIPAL:
attempting_principal:
P
→ Q

OBSERVATION_COORDINATE:

replay:
invocation_count_delta = 0
decision = DENY
reason = AUTHORITY_EXHAUSTED

wrong principal:
reservation_count_delta = 0
invocation_count_delta = 0
decision = DENY
reason = PRINCIPAL_MISMATCH

OBSERVATION_DEPTH:

reservation boundary:
observed by harness

invocation boundary:
observed by harness

real provider consequence:
NOT OBSERVED

crash interval:
NOT OBSERVED

concurrency:
NOT OBSERVED

CLAIM_COORDINATE:

bounded one-shot declared-principal correspondence and replay denial
on the tested governed single-process path

CLAIM_CEILING:

principal authentication
crash-safe exactly-once
concurrency
multi-process
distributed replay resistance
tamper resistance
broader containment
remain unestablished

# ==================================================
# SCIENTIFIC VIEWER REQUIREMENT
# ==================================================

The first scientific projection may be a derived panel over Cell 002.

It must visually separate:

CONTROL
PRESSURE
INTERVENTION
OBSERVATION
CLAIM
UNRESOLVED
NEXT DISCRIMINATOR

The user must be able to click each coordinate and traverse back to the
exact object / witness / source artifact from which it was derived.

# ==================================================
# META-OBSERVABILITY
# ==================================================

Every scientific projection must expose its own observation limits.

Required questions:

WHAT DID THE APPARATUS ACTUALLY OBSERVE?
WHAT DID IT INFER FROM THOSE OBSERVATIONS?
WHAT TRANSFORMATIONS OCCURRED OUTSIDE OBSERVATION?
WHAT DID THE APPARATUS FAIL TO DISTINGUISH?
WHAT BASIS WOULD INCREASE OBSERVATION DEPTH?

An observation apparatus may itself become the target of a pressure.

Example:

APPARATUS A
observes reservation + invocation boundary
but not provider-side consequence

PRESSURE:
introduce a downstream witness

QUESTION:
does the scientific standing change,
or only observation depth?

# ==================================================
# LEARNING LOOP
# ==================================================

A scientific projection may propose a NEXT DISCRIMINATOR,
but this proposal has:

authority_effect = NONE
execution_effect = NONE
scientific_promotion_effect = NONE

The intended learning loop is:

CURRENT EVIDENCE
→ SCIENTIFIC PROJECTION
→ UNRESOLVED ALTERNATIVES
→ CANDIDATE DISCRIMINATOR
→ NEW PRESSURE REQUEST
→ NEW WITNESS
→ REVISED SCIENTIFIC PROJECTION

This is navigation toward unknown regions,
not autonomous scientific promotion.

# ==================================================
# COORDINATE PLURALISM
# ==================================================

V0 explicitly permits multiple scientific coordinate systems.

Different projections may coexist when each preserves:

SOURCE BASIS
TRANSLATION MAP
VALIDITY DOMAIN
LOSS / UNRESOLVED DIMENSIONS

No projection gains canonical status merely by being rendered.

Translation relations should be tested before reuse outside their
qualified validity domain.

# ==================================================
# ACCEPTANCE CRITERION
# ==================================================

The Cell-002 scientific projection is useful only if a human can answer:

1. what exact intervention was performed?
2. what exact coordinates were held fixed?
3. what consequence was observed?
4. what was not observed?
5. what bounded relation was earned?
6. what remains live / unresolved?
7. what next observation or intervention would discriminate further?
8. which source objects support every displayed answer?

# ==================================================
# ORDERING
# ==================================================

DO FIRST:
Cell-002 composed Cockpit visibility.

THEN:
add this one derived scientific projection.

THEN:
pressure the scientific projection itself.

ONLY AFTER:
consider broader scientific coordinate families or canonical promotion.
