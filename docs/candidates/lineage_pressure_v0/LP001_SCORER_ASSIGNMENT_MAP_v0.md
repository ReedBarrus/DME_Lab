# LP-001 Scorer Assignment Map v0

**Status:** FROZEN BEFORE LP-001 CELL EXECUTION
**Visibility during scoring:** WITHHELD FROM SCORER
**Purpose:** mechanically remove run-order and condition-assignment metadata from the scorer bundle

## 1. Frozen run-to-scorer-ID map

```text
RUN01 -> S-7E87AEEF1E15
RUN02 -> S-FC46AA2E9A3D
RUN03 -> S-CD7F3567E646
RUN04 -> S-3FC98F9D2A63
RUN05 -> S-58BA3B802736
RUN06 -> S-69674A944755
RUN07 -> S-5C5938022965
RUN08 -> S-37D80EBD3994
RUN09 -> S-9500698C4292
RUN10 -> S-4595F02C7D4C
RUN11 -> S-A85988C61533
RUN12 -> S-FC1171C848B1
RUN13 -> S-022998302255
RUN14 -> S-4A14794A5A9F
RUN15 -> S-B6E9C3A96F76
RUN16 -> S-F96AF04C01FA
RUN17 -> S-5B3AF7E89CF7
RUN18 -> S-7B3EE7370323
```

The map is frozen before any LP-001 cell output exists.

## 2. Mechanical scorer-bundle construction

After all outputs for an administratively valid completed batch are retained:

1. copy each raw realization output into a scorer artifact named only by its
   frozen `SCORER_ID`;
2. remove run number, condition label, timestamp, administration order, and
   provider-request identifier from the scorer-visible copy;
3. preserve the realization text byte-for-byte inside that scorer-visible copy;
4. present scorer artifacts in lexicographic `SCORER_ID` order;
5. supply only the scorer artifacts, held-out specimen, evaluator key, and
   frozen scoring codebook to the scorer;
6. do not supply this assignment map or the RUN-to-condition assignment table;
7. freeze primary classes, C1-C10 codes, format flags, scorer annotations, and
   output hashes before revealing this map.

Lexicographic scorer presentation order is therefore:

```text
S-022998302255
S-37D80EBD3994
S-3FC98F9D2A63
S-4595F02C7D4C
S-4A14794A5A9F
S-58BA3B802736
S-5B3AF7E89CF7
S-5C5938022965
S-69674A944755
S-7B3EE7370323
S-7E87AEEF1E15
S-9500698C4292
S-A85988C61533
S-B6E9C3A96F76
S-CD7F3567E646
S-F96AF04C01FA
S-FC1171C848B1
S-FC46AA2E9A3D
```

## 3. Blindness claim ceiling

This procedure establishes assignment blindness only.

The response text itself may contain language that permits a scorer to infer
which packet influenced a realization. No redaction of realization content is
performed because such redaction could alter the behavior being scored.

Therefore:

```text
condition-assignment map hidden
!=
condition content necessarily uninferable
```

Residual condition inference from realization text is admitted as expectancy
leakage. The contract does not claim full condition blindness.

## 4. Reveal rule

The RUN-to-SCORER_ID map and RUN-to-condition assignment may be revealed only
after the complete scorer output is frozen.

Reveal does not permit rescoring, relabeling, replacing a valid batch, or
changing any threshold.
