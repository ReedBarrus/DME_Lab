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
