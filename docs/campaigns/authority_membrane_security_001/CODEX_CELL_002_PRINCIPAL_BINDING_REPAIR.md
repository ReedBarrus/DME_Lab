# CODEX CELL 002 PRINCIPAL-BINDING REPAIR

ROLE:
IMPLEMENTATION / APPARATUS

TARGET:
AUTHORITY_MEMBRANE_SECURITY_CELL_002

MODE:
MINIMAL REPAIR

BASIS:

Exact pushed-byte inspection found that the current V0
authority envelope does not include principal_id /
authorized-consumer identity.

Lane A requires the operative authority relation to bind:

capability
× principal
× scope
× current policy
× current executor
× remaining consumable use.

CURRENTLY EARNED:

- pre-invocation CONSUMING reservation
- one-shot current-authority exhaustion
- exact consumed-envelope replay denial
- historical receipt survival
- single-process local state

MISSING:

PRINCIPAL BINDING

OBJECTIVE:

Add the smallest principal-binding relation without changing
the existing replay geometry or widening the capability class.

REQUIRED CHANGES:

1. Add principal_id to AUTHORITY_ENVELOPE_KEYS.
2. Validate principal_id with the same bounded identity discipline.
3. Persist principal_id in:
   - issuance record
   - reservation record
   - consumption receipt
   - replay-denial witness
   - invocation-failure / recovery record where applicable
4. Consumption must receive / observe the attempting principal identity.
5. Before reservation, require:
   attempting_principal_id == issued principal_id
6. Wrong-principal attempt must:
   - make no reservation
   - decrement no authority
   - invoke zero times
   - leave current authority unchanged
   - emit a denial witness with exact reason such as PRINCIPAL_MISMATCH
7. Preserve existing exact replay pressure unchanged:
   same principal
   same consumed envelope
   second invocation count = 0

MATCHED TESTS:

CONTROL:
principal P
fresh envelope bound to P
remaining=1
→ consume once
→ invoke once
→ consumed

PRESSURE A — REPLAY:
principal P
same consumed envelope
→ deny
→ invoke 0

PRESSURE B — WRONG PRINCIPAL:
principal Q != P
fresh active envelope bound to P
→ deny before reservation
→ remaining still 1
→ status still ACTIVE
→ invoke 0

REQUIRED WITNESS FIELDS FOR WRONG-PRINCIPAL DENIAL:

capability_id
approval_id
issued_principal_id
attempting_principal_id
remaining_uses_before
remaining_uses_after
status_before
status_after
decision
reason
lmstudio_invoked
invocation_count
executor_sha256
policy_sha256

DO NOT:
- add multi-user identity infrastructure
- add authentication protocol
- add process identity attestation
- add seat spawning
- add network / CLI / repo-write authority
- modify installed trust root
- start Cell 003

CLAIM CEILING AFTER REPAIR:

Candidate single-process apparatus binds one-shot invocation
authority to one declared principal identity, consumes the one
available use before invocation, rejects exact replay after
consumption, and rejects a mismatched principal before
reservation or invocation.

This does NOT establish authentication of real-world principal
identity or resistance to identity forgery. It establishes only
the explicit principal-binding relation within the tested apparatus.
