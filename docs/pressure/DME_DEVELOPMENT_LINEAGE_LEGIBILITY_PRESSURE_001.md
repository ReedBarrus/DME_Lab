# DME_DEVELOPMENT_LINEAGE_LEGIBILITY_PRESSURE_001

## Status

```text
NIGHT ROAM PRESSURE DESIGN
IMPLEMENTATION REPAIR: NONE
SCIENTIFIC PROMOTION: NONE
AUTHORITY EFFECT: NONE
EXECUTION EFFECT: NONE
```

## Exact observed basis

Default branch reconstructed at:

```text
main
d7ae8134cf7b41610b6fc3da57ecd93c9bb53986
```

The current development campaign says Cockpit work should build projections over earned state and that the Cockpit is derived operational visibility, not authority.

A separate Cockpit perceptual implementation exists in PR #56:

```text
PR: #56
TITLE: Implement COCKPIT_PERCEPTUAL_INSTRUMENT_001
HEAD: cockpit-perceptual-instrument-v0
HEAD SHA: 6dff701cd06ad19ce42c7e1fdd32917f61396af4
BASE: cockpit-perceptual-instrument-campaign-v0
BASE SHA AT PR: 8d5c56c61f17361d76221d23c5f58e44402e9e27
MERGED: true
MERGE COMMIT: a9b4ed3d1086f7a7042ecdb7d358109f53938722
```

Crucially, PR #56 was merged into `cockpit-perceptual-instrument-campaign-v0`, not into `main`.

Current `main` still exposes the pre-campaign observer file set (`app.mjs`, `index.html`, `model.mjs`, `render.mjs`, `styles.css`) and does not contain the perceptual-instrument files shown by PR #56 such as `perceptual_instrument.mjs`, `runtime_live.mjs`, or `control_live.mjs`.

Therefore a GitHub state of `MERGED` is insufficient to infer that the default Cockpit runtime lineage contains the implementation.

This is a lineage observation only. It does not imply that PR #56 should be merged to `main`, that the campaign branch is stale, or that the default runtime ought to advance.

## Proposed distinction

```text
PR MERGED
!=
CHANGE PRESENT ON DEFAULT BRANCH
!=
CHANGE PRESENT IN CURRENT RUNTIME LINEAGE
!=
CHANGE DEPLOYED / OBSERVED BY USER
```

Related cut:

```text
DEVELOPMENT COMPLETION INSIDE CAMPAIGN LINEAGE
!=
INTEGRATION AUTHORIZATION
```

## Why current evidence does not settle integration

PR #56 demonstrates that a bounded implementation was materialized and merged into its campaign base. That proves neither:

```text
campaign adjudication complete
main integration authorized
runtime launched from campaign lineage
user-visible observer sourced from campaign lineage
```

The repository currently provides enough evidence to identify lineage divergence, but not enough to infer the intended integration step.

## Smallest discriminating pressure

Hold implementation bytes constant and vary only the inspected lineage coordinate.

### Cells

```text
A — DEFAULT LINEAGE
ref = main
expectation under current observation:
perceptual-instrument files absent

B — CAMPAIGN LINEAGE
ref = cockpit-perceptual-instrument-campaign-v0
inspect whether merge commit a9b4ed3... is reachable and perceptual files are present

C — IMPLEMENTATION HEAD CONTROL
ref = 6dff701cd06ad19ce42c7e1fdd32917f61396af4
perceptual files should be present by PR evidence
```

Record only:

```text
resolved commit
merge-base / ancestry relation where available
presence of campaign-specific files
relevant qualification artifacts
CI/status evidence
```

Do not launch the Cockpit, merge branches, or infer deployment from file presence.

## Possible outcomes and claim ceilings

If B contains the perceptual implementation while A does not:

```text
COCKPIT PERCEPTUAL IMPLEMENTATION
IS MATERIALIZED IN CAMPAIGN LINEAGE
BUT NOT DEFAULT LINEAGE
AT THE TESTED COORDINATES
```

If both A and B contain it despite the current file observation, the initial divergence observation is falsified and the exact ancestry/path evidence must be reconstructed.

If B no longer contains the merge or campaign files, earn only:

```text
PR MERGE RECORD EXISTS
BUT CURRENT CAMPAIGN REF DOES NOT CONSERVE EXPECTED IMPLEMENTATION
```

and investigate branch movement before any repair.

## Dangerous neighboring inference

Do not infer:

```text
MERGED == MAIN
MAIN == DEPLOYED
FILE PRESENT == FEATURE ACTIVE
FEATURE ACTIVE == SEMANTICALLY QUALIFIED
QUALIFIED == AUTHORIZED FOR INTEGRATION
USER DID NOT SEE CHANGE == UI BUG
```

A visually unchanged Cockpit is compatible with correct behavior when the launched/default runtime lineage does not contain the campaign implementation.

## Disposition

```text
FUTURE CAMPAIGN VALUE: HIGH
IMPLEMENTATION CHANGE NOW: HELD
REASON: lineage state is observable; integration intent/authority is not established
```

The smallest next step is lineage qualification, not UI repair: mechanically establish where the perceptual merge is reachable and which exact source coordinate the observed Cockpit uses. Only then can integration or runtime-launch work be proposed without confusing development state with deployed state.
