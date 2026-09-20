# Continuity Filter Stack v0 — Parked Projection

**Status:** PARKED NON-AUTHORITATIVE PROJECTION  
**Implementation:** none  
**Purpose:** retain a promising decomposition while MM-001 develops a memory
surface capable of representing the relations such checks would need.

This projection does not replace either `src/ledger/continuity.py` or
`tools/continuity.py`.

## Candidate layered distinction

```text
L0 STRUCTURAL CONTINUITY
sequence/index/record identity survives

L1 REFERENTIAL CONTINUITY
claimed dependency / lineage / authority refs
resolve to the intended immutable basis

L2 SEMANTIC CONTINUITY
the referenced distinction remains the same distinction
across representation / transformation

L3 AUTHORITY CONTINUITY
semantic content does not silently acquire or lose
standing / permission / warrant across passage
```

The layers are intentionally non-equivalent:

```text
L0 PASS != L1 PASS
L1 PASS != L2 PASS
L2 PASS != L3 PASS
```

A future diagnostic should therefore prefer a vector such as:

```text
STRUCTURAL
REFERENTIAL
SEMANTIC
AUTHORITY
```

over one collapsed continuity boolean.

## Structural baseline stays narrow

The existing ledger continuity checker may remain valuable precisely because it
asks a cheap structural question about gaps/collisions/identity coordinates.

Do not burden that primitive with semantic inference merely because higher-order
continuity exists.

## Basin / regime hypothesis

One candidate future interpretation of semantic continuity is regime/basin
membership: a distinction remains itself while transformations stay within an
earned invariant regime; a crossing becomes a potential identity transition.

This is **not operationally defined**.

No similarity metric, topology, signature, threshold, or basin detector is
earned here.

A crossing would also require separate licensing semantics:

```text
semantic transition
!=
semantic rupture

licensed / retained identity transition
!=
silent drift
```

## Why park this beside the memory work

Higher-order continuity checks require explicit relations such as:

- source and immutable basis;
- dependency / lineage edges;
- distinction identity;
- transformation relation;
- standing / authority status;
- amendment or licensing record.

MM-001 is testing whether those relations can be retained compactly before any
higher-order continuity machinery is built.

## Reopen condition

Reopen this projection only after memory pressure produces a concrete relational
surface that makes at least one L1/L2/L3 discriminator executable.

Until then:

```text
useful decomposition
!=
earned continuity architecture
```
