# Atlas five-node local candidate v0

This package is a bounded implementation candidate for the first five-node
coordinate-transfer surface.

It deliberately does **not** instantiate five agents, five model seats, five
roles, five live processes, or five network services.

The first implementation boundary is:

```text
five explicit coordinates
+
explicit directed transfer edges
+
deterministic route resolution
+
deterministic transfer envelope construction
```

## Non-collapse rules

```text
NODE != AGENT
NODE != ROLE
NODE != MODEL
NODE != SEAT
NODE != PROCESS
NODE != AUTHORITY

ADDRESSABLE != LIVE
ROUTE EXISTS != TRANSFER AUTHORIZED
TRANSFER ENVELOPE != EXECUTION
TRANSFER ENVELOPE != DELIVERY
TRANSFER ENVELOPE != ACKNOWLEDGEMENT
TRANSFER ENVELOPE != STANDING CHANGE
```

This preserves the current repository rule that generalized Atlas runtime,
generalized router/scheduler behavior, autonomous agent architecture, and
automatic execution remain unearned.

## Candidate fixture

`five_node_fixture_v0.json` contains exactly five local unbound nodes:

```text
NODE_01 <-> NODE_02 <-> NODE_03 <-> NODE_04 <-> NODE_05
```

Each node has:

- a unique `node_id`;
- a unique `coordinate_ref`;
- no role binding;
- no runtime instance;
- no authority reference.

Each edge is exactly:

```text
transition_kind = TRANSFER_ONLY
authority_effect = NONE
execution_effect = NONE
```

The topology is intentionally boring. Its only purpose is to pressure coordinate
resolution and multi-hop transfer description before adding real role, runtime,
network, or authority semantics.

## Implementation

`atlas.py` provides:

- strict manifest parsing;
- five-node cardinality enforcement;
- unique node / coordinate / edge checks;
- explicit endpoint validation;
- deterministic breadth-first route resolution over declared edges;
- deterministic transfer-envelope identities bound to the manifest digest;
- explicit zero-effects for authority, execution, and standing.

The library performs no sockets, subprocesses, model calls, external network
access, role invocation, repository mutation, or authority transition.

A transfer envelope answers only:

```text
FROM WHICH COORDINATE?
TO WHICH COORDINATE?
THROUGH WHICH DECLARED EDGES?
CARRYING WHICH REFERENCES?
AGAINST WHICH MANIFEST?
```

It does not answer:

```text
MAY THE TARGET ACT?
DID THE TARGET RECEIVE IT?
DID A MODEL RUN?
DID AUTHORITY CHANGE?
DID SCIENTIFIC STANDING CHANGE?
```

## Proposed next pressure after implementation review

Only after the implementation and tests are reviewed should a separate
qualification ask whether five local runtime endpoints can instantiate against
these coordinates without collapsing:

```text
coordinate identity
!=
runtime identity
!=
role identity
!=
authority
```

No local runtime activation, role binding, network access, external service
binding, or five-node execution is authorized by this candidate package.
