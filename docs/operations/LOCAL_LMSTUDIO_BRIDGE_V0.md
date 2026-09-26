# Local LM Studio Invocation Bridge V0

## Purpose

Remove the human operator from repetitive clipboard transport without exposing the local machine to arbitrary code from the public repository.

The bridge is intentionally narrower than a GitHub self-hosted runner.

GitHub's own security guidance warns against self-hosted runners on public repositories because pull-request workflow code can compromise the runner host. Therefore V0 does **not** execute GitHub Actions jobs locally.

## Architecture

```text
GitHub public repo
    |
    | declarative request manifest only
    v
trusted local bridge
    |
    | schema + policy + hash checks
    | local human approval
    v
LM Studio localhost API
    |
    | text generation only
    v
witnessed JSON result
```

## Security boundary

The bridge refuses:

- arbitrary shell commands;
- arbitrary local paths;
- model tool definitions;
- previous-response/stateful continuation;
- repository access by the model;
- connector/MCP access by the model;
- prompt artifacts outside approved repo prefixes;
- prompt bytes whose SHA-256 does not match the manifest;
- models outside the local allowlist;
- disabled requests;
- malformed request IDs;
- requests above configured size/token ceilings.

V0 additionally requires a local `y` approval before invocation.

## Why immutable source refs matter

Each request names:

- a 40-character Git commit SHA;
- a repo-relative input path;
- the SHA-256 of the exact prompt bytes.

The bridge reads the prompt with:

```text
git show <source_ref>:<input_path>
```

and verifies the SHA-256 before sending anything to LM Studio.

Thus:

```text
REQUEST POINTS AT FILE
!=
FILE CONTENT SILENTLY CHANGES BEFORE EXECUTION
```

## LM Studio

Start the local server from LM Studio's Developer tab or with:

```powershell
lms server start
```

V0 uses the OpenAI-compatible:

```text
POST http://127.0.0.1:1234/v1/chat/completions
```

with exactly one user message and no tool definitions.

## Run

From the DME_Lab checkout:

```powershell
python tools/local_lmstudio_bridge_v0.py --once
```

To keep polling:

```powershell
python tools/local_lmstudio_bridge_v0.py --watch
```

The bridge fetches the configured remote branch, inspects request manifests without checking out or executing remote code, and asks for approval before each new enabled request.

## Result witness

Each completed request produces:

```text
bridge/results/<request_id>.json
```

containing:

- request manifest SHA-256;
- exact source commit;
- input path;
- input SHA-256;
- exact LM Studio request-body SHA-256;
- exact LM Studio response-body SHA-256;
- model identifier;
- timestamps observed by the bridge;
- raw response body;
- extracted assistant text;
- explicit statements that tools and previous-response state were not supplied.

## Initial authority rule

```text
REMOTE REQUEST
!=
LOCAL AUTHORIZATION
```

For V0, the local approval keystroke is the authorization membrane.

Once the bridge has survived pressure, a later policy may auto-authorize narrowly defined request classes. Do not remove the approval membrane merely for convenience.

## Result publication

V0 does not automatically push result files to GitHub.

That is deliberate. Result publication is a separate authority edge.

A later V0.1 can add a narrowly constrained result-only push after the local bridge has been reviewed and pressure-tested.
