# Admission Port v0

A deliberately tiny executable membrane for the DME_Lab operator-grammar experiments.

The model may **propose** a transition. It does not decide whether that transition reaches the world.

```text
MODEL PROPOSAL
      ↓
canonical operator
      ↓
AUTHORITY
      ↓
CAPABILITY
      ↓
RESOURCE
      ↓
PRESSURE STATE
      ↓
ADMIT / REJECT
      ↓
EXECUTE only after ADMIT
```

Every rejected proposal is retained and returned as a witnessed rejection receipt. The proposer therefore learns that the attempted transition was observed and recorded, without allowing the transition to change the repository.

## Why there is no semantic passkey yet

v0 deliberately does **not** allow the model to modify authority through the same port. A linguistic passphrase generated or repeated by the model is not a security boundary.

Instead:

```text
proposal channel can request actions
proposal channel cannot mutate grants
```

That structural dependence is the smallest useful protection. Portable/signed capability grants can be investigated later if remote mobility actually requires them.

## Run it

Copy `admission_port_v0.py` into the root of `DME_Lab`, then from the repo root run:

```text
python admission_port_v0.py --demo
```

The demo attempts:

```text
read_full → REJECT / RESOURCE_BLOCKED
list      → REJECT / MISSING_AUTHORITY
grep      → ADMIT → EXECUTE → PRESSURE OPEN→RESOLVED
list      → REJECT / PRESSURE_RESOLVED
```

Trace output appends to:

```text
traces/admission_port_v0.jsonl
```

Interactive mode:

```text
python admission_port_v0.py
```

Paste one proposal per line, for example:

```json
{"operator":"repo.grep:v1","object":"src/home/home_capture_v0/server.py","args":{"pattern":"SCHEMA_VERSION"}}
```

Unauthorized example:

```json
{"operator":"repo.list:v1","object":"src/home","args":{}}
```

## Standing

This is not a general agent runtime, external transport, autonomous execution, cryptographic identity system, or grant manager. It is only the smallest executable pressure needed to make `MISSING_AUTHORITY` mean **the tool does not execute**, while preserving the attempted transition as evidence.

A later experiment can compare **witnessed rejection** versus silent rejection to see whether knowing that a rejected path was recorded changes subsequent model navigation.
