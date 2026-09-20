# CONCORDANCE COCKPIT v0

## EDGE RELATION ENTITLEMENT CANDIDATE 002

### STATUS

```text
BOUNDED DEVELOPMENT CANDIDATE

SOURCE FRACTURE:
SEMANTIC EDGE ENTITLEMENT FAILED

PROJECTOR REPAIR:
NONE

GRAPHICAL RENDERING:
UNTOUCHED

AUTHORITY RESOLUTION:
NONE

MERGE:
NO

SCIENTIFIC STANDING:
NONE
```

### SOURCE BASIS

```text
source branch:
concordance-cockpit-v0-edge-entitlement-pressure

source head:
9d52e46f4be377bbfbc4ffc60d547738157b6bfc

surviving fracture:
REFERENTIAL VALIDITY
!=
RELATIONAL ENTITLEMENT
```

### SOLE QUESTION

Can a bounded relation-entitlement predicate distinguish:

```text
A durable basis artifact
that explicitly carries the exact claimed relation

from

a durable basis artifact
that exists but does not carry that exact claimed relation?
```

This candidate does not attempt to decide whether the source that authored the
claim had authority, standing, competence, or truth.

That is deliberately outside this first cut.

### CANDIDATE RELATION

For this bounded mechanism, an artifact semantically carries a developmental
relation only when its exact machine-readable claim tuple contains:

```text
from_ref
relation_type
to_ref
```

and the artifact bytes match a prospectively pinned SHA-256 identity.

The predicate is exact-match only.

It must not infer a stronger relation from a weaker or merely adjacent relation.

```text
REFERENCED_BY
!=
MOTIVATED

MOTIVATED
!=
CONSTRAINS

CONSTRAINS
!=
INCORPORATED
```

No total ordering is asserted.

### DECLARED THREAT MODEL

CALLER MAY:

```text
choose the requested edge tuple

present any durable artifact bytes

present unrelated real artifacts

present artifacts carrying a different relation type

present artifacts carrying the right type over wrong endpoints

modify artifact bytes after an expected digest has been pinned
```

CALLER MAY NOT, in the base qualification:

```text
change the prospectively pinned expected digest

claim that arbitrary source standing is already resolved
```

The base qualification asks only whether exact content correspondence can be
mechanically distinguished.

### REQUIRED BASE CELLS

```text
R1
exact artifact identity
+
exact tuple present
→ ESTABLISHED

F1
real artifact
+
no relation claims
→ NOT_ESTABLISHED

F2
REFERENCED_BY only
+
request MOTIVATED
→ NOT_ESTABLISHED

F3
MOTIVATED only
+
request CONSTRAINS
→ NOT_ESTABLISHED

F4
CONSTRAINS only
+
request INCORPORATED
→ NOT_ESTABLISHED

F5
right relation type
+
wrong endpoint
→ NOT_ESTABLISHED

F6
modified bytes
+
old pinned digest
→ NOT_ESTABLISHED

F7
prose mention / malformed claim surface
→ NOT_ESTABLISHED
```

### EXPANDED THREAT RAKE

After the base candidate is qualified, pressure one stronger counterfeit:

```text
F8

CALLER AUTHORS A NEW ARTIFACT
THAT PERFECTLY DECLARES
THE DESIRED RELATION

AND PINS ITS OWN DIGEST

BUT

NO INDEPENDENT SOURCE STANDING
FOR THAT CLAIM
HAS BEEN ESTABLISHED
```

If the predicate accepts F8, record:

```text
EXACT CLAIM DECLARED
!=
CLAIM SOURCE ENTITLED
```

That would not invalidate exact content matching.

It would cap the mechanism below full semantic entitlement.

### CLAIM CEILING

A base PASS may establish only:

```text
exact frozen artifact bytes
can be checked for an exact relation tuple
without upgrading another relation type
or unrelated basis into that tuple.
```

It may not establish:

```text
the claim is true

the claim source is authoritative

the claim source has standing

the relation caused anything

the relation is scientifically admitted

a universal developmental relation ontology
```

### STOP

```text
MATERIALIZE CANDIDATE
→
QUALIFY BASE CELLS
→
PRESS F8
→
RETAIN RESULT
→
STOP
```

Do not repair the cockpit projector in this operation.
