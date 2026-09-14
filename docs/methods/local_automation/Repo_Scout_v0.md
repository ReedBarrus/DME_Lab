# Repo Scout v0

**Status:** bounded read-only apparatus contract
**Scientific authority:** NONE
**Pressure-selection authority:** NONE
**Repository mutation authority:** NONE
**Acceptance authority:** external Codex / frontier / human review

## Purpose

Repo Scout v0 is the smallest functional auxiliary worker for a declared
repository-evidence question. It inspects an exact committed basis through a
caller-frozen read-only plan, then gives the retained observations to one
identified model/runtime realization for one candidate evidence packet.

The apparatus implements:

```text
declared invocation
→ exact HEAD basis guard
→ operation / path / budget preflight
→ bounded read-only Git observations
→ one serialized model request
→ raw response retention
→ separate strict mechanical evaluation
→ external acceptance or rejection
```

It is not a scheduler, router, planner, daemon, persistent worker, retry
engine, Controller, autonomous research loop, or qualification authority.
`Persistent_Research_Autonomy.md` and `Local_Model_Workshop.md` remain
non-authoritative projections.

## Invocation contract

An invocation contains exactly:

```text
task_id
repository_basis
question
allowed_paths
allowed_operations
inspection_plan
execution_budget
realization_basis
output_contract
```

`repository_basis` must be an exact 40-character commit. It must resolve and
equal committed `HEAD` before any inspection or model call. A mismatch rejects
the invocation; it does not become descriptive metadata.

`allowed_paths` contains canonical repository-relative POSIX paths. `.` is an
explicit whole-repository scope and is required for repository-level
`git_status` or `git_rev_parse`. A narrower path permits that path and its
descendants only. Absolute paths, traversal, `.git`, option-shaped path
segments, and implicit scope widening are rejected.

`inspection_plan` is complete before execution. The model cannot add an
operation, request another observation, widen scope, or change a budget. There
is no model-directed tool loop in v0.

The execution budget declares:

```text
max_operations
max_operation_output_bytes
max_model_response_bytes
max_model_calls = 1
wall_time_seconds
```

The apparatus passes the remaining declared wall-time allowance to the
injected model interface. It records elapsed time and rejects mechanically
observable budget excess. There is no retry.

## Permitted operations

Only these operation identifiers exist:

- `git_status` — porcelain status of the execution worktree; requires `.`
  scope.
- `git_rev_parse` — resolve only `HEAD` or the declared repository basis;
  requires `.` scope.
- `git_log` — bounded commit log at the declared basis and one scoped path;
  maximum 50 entries.
- `git_show` — read one scoped UTF-8 file from the declared basis with an
  explicit line interval; maximum 500 lines.
- `git_diff` — inspect one scoped path between an explicitly identified
  ancestor and the declared basis.
- `git_grep` — fixed-string search at the declared basis over one scoped path;
  maximum 20 matches per file.

The exact inspection-plan request shapes are:

```json
{"operation":"git_status"}
{"operation":"git_rev_parse","ref":"HEAD"}
{"operation":"git_log","path":"docs/","max_count":10}
{"operation":"git_show","path":"PROJECT_STATE.md","start_line":1,"end_line":80}
{"operation":"git_diff","from_commit":"<exact ancestor commit>","path":"src/"}
{"operation":"git_grep","pattern":"bounded term","path":"docs/","max_matches_per_file":10}
```

Each object rejects extra fields. `git_diff.from_commit` must resolve and be an
ancestor of the declared repository basis. The `git_rev_parse.ref` value may be
only `HEAD` or the declared basis.

Every Git process uses an explicit argument vector with no shell. Lazy object
fetch, terminal prompting, pagers, fsmonitor helpers, external diff, and text
conversion are disabled. Network, fetch, pull, checkout, switch, reset, clean,
commit, push, branch mutation, file writing, and unrestricted command
execution have no wrapper and are rejected during preflight.

## Model-visible boundary

The injected model receives one canonical JSON request containing only:

- the task ID, exact repository basis, and bounded question;
- the declared path and operation scope;
- the observations produced by the predeclared inspection plan;
- explicit attempt, proposal, commit, and acceptance boundaries;
- the exact result contract.

It receives no repository handle, filesystem handle, Git executable, shell,
tool/MCP surface, network surface, prior conversation, retry channel, or
authority to accept its own result.

The model/runtime interface is injected as:

```text
model_call(serialized_request, remaining_timeout_seconds) -> raw_response
```

This keeps deterministic apparatus tests independent of live inference. A
specific live transport is intentionally not selected or invoked in this
pass.

## Result contract

The raw response must be one complete JSON object containing exactly:

```text
task_id
execution_basis
evidence
bounded_interpretation
unresolved
scope_used
operations_used
escalation
terminal_action
```

Each evidence entry contains exactly:

```text
source_path
location
observation
```

The source path must fall within an actually accessed scope. `scope_used` and
`operations_used` must exactly reproduce the apparatus record. The terminal
action is `STOP` or `ESCALATE`; escalation requires a reason and must agree
with the terminal action.

No prose extraction, duplicate-field collapse, missing-field completion,
token repair, or semantic correction is performed.

## Retained separation

The returned run record keeps two surfaces separate:

```text
observation
!=
mechanical_evaluation
```

The observation retains the declaration, resolved basis, realization basis,
operation attempts, commands, accessed paths, outputs, exact serialized model
request, raw response, call count, duration, and before/after repository
fingerprints. It performs no semantic evaluation.

The mechanical evaluation retains the parsed result when valid, parse or
budget failure otherwise, individual contract checks, and a terminal state of
`PASS`, `ESCALATED`, or `FAIL`. Mechanical success does not establish semantic
validity, usefulness, qualification, or acceptance.

## Rejection boundary

Repo Scout v0 rejects or fails closed on:

- unresolved, non-exact, or stale repository basis;
- undeclared, unsupported, mutation, or network operation;
- non-canonical or out-of-scope path;
- missing path at the declared basis;
- operation-count, output, response, or wall-time budget excess;
- failed or binary operation output;
- malformed, incomplete, duplicate-field, or extra-field model response;
- missing or inconsistent `STOP` / `ESCALATE` state;
- result basis, task, scope, operation, or evidence-path mismatch;
- any detected repository-state change across the run.

An escalation is a candidate packet state only. It performs no authoritative
action.

## Authority

Repo Scout v0 has bounded attempt authority to execute the frozen read-only
inspection plan and proposal authority to return a candidate packet. It has no
authority to commit, change repository state, select pressure, alter standing,
change qualification, or accept its own interpretation.

Codex, frontier review, or human review may accept, reject, reinterpret, or
ignore the packet. The first live utility pressure remains separately gated.
