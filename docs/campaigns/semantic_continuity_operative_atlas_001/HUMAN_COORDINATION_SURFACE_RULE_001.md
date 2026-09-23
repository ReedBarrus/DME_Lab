# HUMAN COORDINATION SURFACE RULE

STATUS: ACTIVE

## Core distinction

```text
CANONICAL STORAGE
!=
RELIABLE HUMAN COORDINATION SURFACE
```

A canonical artifact may exist and still be operationally unusable if the human coordinator must:

- remember where it lives;
- distinguish among similarly named versions;
- assemble multiple files manually;
- preserve exact ordering across seats;
- copy/paste long brittle payloads;
- infer which supporting artifacts belong to which warrant;
- detect whether one wrong artifact was mixed into a bundle.

## Required coordination surface

Every multi-seat experiment must expose, before routing:

1. **ONE CURRENT POINTER**
   - names the active experiment;
   - names the exact current artifacts;
   - states which prior artifacts are superseded.

2. **ONE READY-TO-SEND BUNDLE PER SEAT**
   - contains everything that seat needs;
   - requires no manual document assembly;
   - preserves exact packet ordering and labels;
   - includes explicit "DO NOT ADD" boundaries.

3. **ONE RETURN ROUTE**
   - says exactly where the seat's output goes next;
   - identifies whether the returned output is frozen, provisional, or administrative.

## Operator burden ceiling

The human operator should normally perform at most:

```text
OPEN ONE BUNDLE
COPY twice
PASTE twice
RETURN RESULT ONCE
```

If an experiment requires repeated manual assembly of multiple source documents, the coordination surface is not qualified.

## Failure rule

```text
HUMAN COPY ERROR
!=
SCIENTIFIC COUNTEREVIDENCE
```

If routing depends on fragile manual transport and the operator sends the wrong artifact, the apparatus has failed coordination.

## Consequence

Future campaign work must optimize not only for:

```text
CANONICALITY
PROVENANCE
EXACTNESS
```

but also for:

```text
DISCOVERABILITY
CURRENTNESS
BUNDLE COMPLETENESS
ROUTING LEGIBILITY
HUMAN ERROR TOLERANCE
```

The coordinator should prepare seat-ready packets rather than asking the human operator to reconstruct packet membership from repo history or chat history.


---

## Transport Friction Clarification

The earlier shorthand:

```text
OPEN ONE BUNDLE
COPY ONCE
PASTE ONCE
RETURN RESULT ONCE
```

was a coordination-direction target, not a literal lower bound on physical copy/paste actions.

A normal manual seat round has at least two transport directions:

```text
COORDINATOR → SEAT
SEAT → COORDINATOR
```

Therefore a realistic low-friction target is:

```text
ONE OUTBOUND TRANSFER
+
ONE RETURN TRANSFER

PER SEAT
PER ROUND
```

Typical manual realization:

```text
OPEN CURRENT BUNDLE
→ COPY SEND PACKET
→ PASTE TO SEAT
→ COPY RETURNED RESULT
→ PASTE BACK TO COORDINATOR
```

The governing objective is:

```text
MINIMIZE COORDINATION FRICTION
AND OPERATOR TRANSPORT BURDEN

NOT

MINIMIZE COPY/PASTE COUNT
TO AN IMPOSSIBLE ABSTRACT NUMBER
```

Especially:

```text
NECESSARY HUMAN COORDINATION
!=
AVOIDABLE HUMAN TRANSPORT BURDEN
```

and:

```text
HUMAN COORDINATION TARGET
!=
RIGID VALIDITY CONDITION
```

A scientifically valid round is not invalidated because it required additional transport actions.
The surface should reduce unnecessary coordination work, especially work concentrated on the human operator, without forcing agents to optimize against a counterfeit one-copy/one-paste constraint.
