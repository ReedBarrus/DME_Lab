# Repo Scout Interruption-Retention Pressure v0

**Status:** RETAINED BOUNDED APPARATUS PRESSURE RESULT

**Repository basis:** `94830a8b40a264e2630adf7a9ab654e6619e7e29`

**Repo Scout apparatus:** `repo_scout_v0.2`

**Mechanical result:** `PASS`

**Live model calls:** `0`

**Synthetic call entries:** `1`

**Automatic retries:** `0`

**Second invocation:** `0`

**Scientific standing:** `NONE`

**Qualification or promotion:** `NONE`

## Pressure

The preceding interrupted Qwen run lost its normal Repo Scout observation
because the apparatus constructed that record only after the model interface
returned. This apparatus-only pressure asked whether a smaller durable boundary
could preserve enough evidence to decide that a consequence was attempted
without inventing its completion or authorizing repetition.

No LM Studio endpoint or live model was used. The synthetic invocation froze
one committed `git_show` operation, one model-proposal request, one permitted
synthetic call entry, and zero retries.

## Executed sequence

```text
freeze exact invocation
→ retain operation evidence, serialized request, and repository fingerprints
→ enter and durably mark one synthetic consequence boundary
→ interrupt the executor before normal Repo Scout return
→ start a distinct investigator process
→ reconstruct the attempted consequence from retained evidence only
→ evaluate follow-up admission
```

The pre-call record retained:

- the exact invocation and resolved committed basis;
- the completed operation request, command, output, and return code;
- issued source identity, scope, operation, and byte count;
- the exact serialized model-visible request and SHA-256 digest; and
- repository fingerprints before inspection and immediately before the call.

The synthetic client then appended `CALL_ENTERED` with the same attempt ID and
request digest, flushed the journal, and terminated outside Repo Scout's normal
response path. It produced no response and contacted no model.

## Restart result

The restarted investigator ran in a different process. From the two retained
journal events it recovered:

```text
consequence_attempted: true
consequence_completed: UNKNOWN
response_observed: false
model_call_attempts_reconstructed: 1
automatic_second_invocation_admissible: false
second_invocation_requires_separate_authorization: true
```

The investigator did not modify the journal. Repository fingerprints before
the executor, at the pre-call boundary, at investigator restart, and after the
pressure were equal. The only pre-existing worktree residue remained the
unrelated untracked handoff artifact.

## Bounded result

The matched `CALL_ENTERED` marker establishes that this synthetic consequence
boundary was attempted. It does not establish whether a real external
consequence would have completed after acknowledgement was lost. Therefore the
absence of a response cannot authorize an automatic second invocation.

```text
pre-call frozen
!=
consequence attempted
!=
response observed

response absent
!=
consequence not completed

unknown outcome after attempt
!=
authority to repeat
```

This pressure establishes the apparatus behavior only for the executed
synthetic boundary. It does not establish durable transport acknowledgement,
exactly-once external execution, live-model recoverability, Repo Scout utility,
realization capability, qualification, or scientific standing.

## Smallest next pressure

If another live Repo Scout comparison is authorized, retain the same durable
pre-call evidence and require its transport wrapper to append the call-entry
marker before contacting the endpoint. A response or failure must be associated
to that attempt ID. An interrupted or outcome-unknown attempt remains
non-repeatable without separate authority.

That would pressure the boundary with a real local transport. It is not
authorized by this result and must not be treated as an automatic retry of the
interrupted Qwen comparison.

## Evidence

- [executed trace](../../../traces/repo_scout_interruption_retention_pressure_v0.json)
- [apparatus contract](../../methods/local_automation/Repo_Scout_v0.md)
- [preceding interrupted comparison](repo_scout_hermes_qwen3_coder_realization_comparison_v0.md)

STOP. No live model was contacted and no second invocation was admitted.
