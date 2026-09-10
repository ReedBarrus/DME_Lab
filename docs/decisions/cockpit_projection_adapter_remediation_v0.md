# Cockpit Projection Adapter Remediation v0

## Scope and repository gate

This Stage 4B pass remediated exactly two licensed Cockpit Projection Adapter
wounds: P8 silent loss of unsupported resolution-history structure and P11
ambiguous duplicate pressure identity.

After `git fetch origin main`, local `HEAD` and `origin/main` were identical at
`d3c9db69d701dfea7237282b38b78b9d12bd4f3b` with a clean worktree. The exact
committed source basis remained authoritative throughout the pass.

This is bounded Cockpit implementation development. It is not a scientific
pressure, UI pass, Controller pass, generalized Markdown parser, identity
system, or graph resolver.

## Lineage

The retained Stage 3 decision,
[`cockpit_projection_adapter_pressure_v0.md`](cockpit_projection_adapter_pressure_v0.md),
records P8 as a contract violation and P11 as a contract ambiguity. Its compact
trace remains unchanged historical evidence.

Stage 4A tightened the existing
[`PROJECTION_CONTRACT.md`](../cockpit/PROJECTION_CONTRACT.md): duplicate current
pressure occurrences must all survive with local provenance and no canonical
winner, while an explicit relation to a duplicated ID must remain uniquely
unresolved.

Stage 4B did not change either prior artifact. Historical observation remains
distinct from current implementation behavior.

## Implementation change

### P8 — unsupported history residue

The exact supported `Resolution history` form continues to parse normally. The
parser now records the R-entry lines consumed within that exact section and,
within the same PR node extent, detects any remaining lines matching the
existing strong R-entry structure:

```text
R<number> — `STANDING`: ...
```

Those unconsumed lines are not parsed as history and their heading is not
treated as a synonym. One `unsupported_structure` diagnostic identifies the
affected PR, retains the raw lines with committed line coordinates, and makes
the projection operationally partial.

### P11 — duplicate pressure identity

The adapter counts parsed current pressure occurrences without merging them.
Every duplicate node survives with its original fields, source anchor, and
committed heading line. Each duplicate carries an ambiguous identity state and
one `duplicate_pressure_id` diagnostic retains all occurrence provenance. No
standing, title, section, ordinal, or file position is used to select authority.

An explicit pressure relation remains one relation. When its target ID has
multiple current occurrences, the relation preserves its kind, source, target,
raw source field, and provenance while adding only:

```text
target_resolution:
  status: ambiguous
  candidate_count: <current occurrences>
```

It is not duplicated into asserted edges and no relations are invented among
the duplicate nodes.

## Regression evidence

The new remediation regressions used the Stage 3 semantic wounds without
special-casing a heading phrase, pressure ID, or standing:

- unsupported renamed history heading plus intact R0/R1-shaped entries:
  current standing survived, supported history remained empty, and the raw
  non-recoverable material became diagnostic residue;
- exact supported history heading: R0 `BASIS_INSUFFICIENT` and R1
  `BOUNDED_RESOLUTION` parsed normally with no new diagnostic;
- two textually identical pressure headings with one ID: both nodes survived
  with distinct source lines, one duplicate diagnostic, and no canonical node;
- one explicit relation to that duplicated ID: the relation survived once and
  unique target resolution was `ambiguous` with candidate count two.

The live Stage 3 pressure test now treats repaired P8 behavior as a regression
survival while the committed Stage 3 decision and trace retain the original
violation. Its P11 classification remains the historical Stage 3 contract
ambiguity while also checking that the remediated adapter emits the later
contracted diagnostic.

Verification completed:

- focused adapter, Stage 3 pressure, and remediation tests: 25/25 passed;
- full hardware-free suite: 533/533 passed;
- `git diff --check`: passed;
- compact remediation trace:
  `traces/cockpit_projection_adapter_remediation_v0.json`.

## Current repository smoke

The remediated worktree adapter projected the exact starting commit and checked
it against `origin/main`. The projection remained complete and current with
zero diagnostics.

The healthy specimen retained explicit no active pressure, PR-018 `OPEN` and
inactive, PR-019 current `BOUNDED_RESOLUTION`, R0 `BASIS_INSUFFICIENT`, R1
`BOUNDED_RESOLUTION`, 46 represented constraints, and the Controller as a
`PARKED` projection document. It retained 19 current pressure nodes, 24 explicit
relations, 214 evidence references, and three projection documents on this
source basis. No duplicate diagnostic, unsupported-history diagnostic, relation
target ambiguity, or accidental relation appeared.

These counts describe this committed specimen and are not universal adapter
invariants.

## Bounded adjudication

Stage 4B succeeds within the named wound classes:

```text
unsupported history-entry-shaped residue
-> rejected as history
-> visible diagnostic residue

duplicate current pressure ID
-> every occurrence preserved
-> unique identity unresolved
-> explicit duplicate target preserved once and marked ambiguous
```

The strongest behavior now supported is that the exact P8 and P11 structural
failure classes can no longer appear cleanly recoverable while healthy
supported repository structure retains its meaning.

The strongest behavior still not supported is general Markdown robustness or
general projection safety. Similar-looking prose is not accepted as history;
arbitrary malformed structures, generalized identity semantics, consumer
candidate selection, and generalized graph resolution remain outside this
pass.

## Repository standing and stop boundary

This pass changed no Pressure / Resolution Map node, projection contract,
constraint registry, scientific evidence, acoustic artifact, canonical ledger,
Controller code or standing, website code, chart, or `D-*` constraint. It did
not create a new scientific pressure.

A fresh independent adversarial re-pressure pass remains required before UI
construction. Stop here; do not begin Stage 4C in this pass.
