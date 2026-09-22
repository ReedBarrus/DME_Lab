# Local Invocation Bridge — Current Surface

STATUS: BOOTSTRAP

## Boundary

PUBLIC REPO MAY:
- contain declarative invocation requests;
- contain immutable prompt artifacts;
- receive witnessed text results.

PUBLIC REPO MAY NOT:
- supply shell commands to the local bridge;
- select arbitrary local files;
- enable model tools;
- enable repository tools;
- enable external retrieval;
- execute GitHub self-hosted workflow code on the local machine.

## Local authority

V0 requires a human approval keystroke before each invocation.

No request is executed merely because it exists in GitHub.

## Active policy

`bridge/policy_v0.json`

## Request queue

`bridge/requests/`

## Result queue

`bridge/results/`

## Trusted executor

`tools/local_lmstudio_bridge_v0.py`

## Current authority ceiling

```text
REMOTE REQUEST
!=
LOCAL AUTHORIZATION

MODEL INVOCATION
!=
TOOL AUTHORITY

MODEL OUTPUT
!=
REPO MUTATION AUTHORITY
```

## LOCAL TRUST ROOT STATUS

NOT YET INSTALLED.

The repository currently contains only the public/reference bridge implementation and request surface.
The intended authority-bearing local trust root must be created separately on the operator machine outside the repository.

Recommended location:

```text
%USERPROFILE%\\.dme_lab_bridge\\
```

The local trust root should contain the pinned executor and local policy and must not auto-update from the public repository.
