# CODEX CELL 002 IMPLEMENTATION RESULT

STATUS:
LOCAL / UNCOMMITTED / UNPUSHED

CANDIDATE APPARATUS:

src/runtime/local_authority_consumption_v0.py
tests/runtime/test_authority_membrane_security_cell_002.py
traces/authority_membrane_security_cell_002_consumption_receipt_v0.json
traces/authority_membrane_security_cell_002_replay_denial_v0.json

BEHAVIOR:

- exact V0 envelope validation
- local atomic JSON state store
- single-process lock
- pre-invocation CONSUMING reservation
- consumption receipt
- replay-denial history

ENVELOPE V0:

object_type
capability_id
approval_id
request_sha256
input_sha256
model
endpoint_identity
executor_sha256
policy_sha256
use_limit
remaining_uses
status
issued_at
expires_at

V0 REQUIRES:

object_type = LOCAL_MODEL_INVOCATION_AUTHORITY_ENVELOPE_V0
use_limit = 1
remaining_uses = 1
status = ACTIVE
expires_at = null

LOCAL STATE:

%USERPROFILE%\.dme_lab_bridge\authority_state_v0\<capability_id>.json

STATE WRITE:

process-wide RLock
→ temporary file
→ flush + fsync
→ atomic os.replace

CONTROL RESULT:

approval calls = 1
pre-use remaining_uses = 1
durable reservation written before invocation
invoke calls = 1
post-use remaining_uses = 0
status = CONSUMED
current_authority = NONE
consumption receipt persisted
PASS

REPLAY RESULT:

same capability_id = preserved
same approval_id = preserved
same issued-envelope hash = preserved
pre-use remaining_uses = 0
second invoke calls = 0
decision = DENY
reason = AUTHORITY_EXHAUSTED
historical receipt = readable
current_authority = NONE
PASS

CONSUMPTION RECEIPT:

receipt_id:
receipt:sha256:d4287d4a050788693d1b83cc4d4a49cfff5d6282b735d5dad7a4fbe8963a7a89

artifact SHA-256:
eb0562637e43d9280183947a844fdb36be4b052fceb5a2c88167184536fd2a2f

REPLAY DENIAL:

denial_id:
denial:sha256:364d6d257a0961eda4ebfa4a4ec570c588881015bb00fa58c1ab0f353b214598

artifact SHA-256:
402d3c8e957d64ea6524ddf594de08f1180a154b042e14d292cab8686b3c1253

decision = DENY
lmstudio_invoked = false
invocation_count = 0
current_authority = NONE

REGRESSIONS:

Cell 001 + Cell 002 + invocation witness + LM Studio adapter:
42/42 PASS

Python compilation:
PASS

git diff --check:
PASS

CLAIM CEILING:

Under this candidate single-process apparatus,
one exact use_limit=1 authority envelope permitted
one mocked invocation-boundary crossing,
persisted zero remaining uses,
and rejected reuse of that same consumed envelope
before a second crossing.

UNTESTED:

- multi-process / distributed races
- independent executor processes sharing state
- power-loss semantics beyond fsync + os.replace
- crash after reservation before invocation
- crash after invocation before receipt
- CONSUMING reconciliation
- ACL / local-state tamper resistance
- expiry / freeze / revocation / restoration
- real LM Studio HTTP invocation
- installed trust-root promotion

No commit or push performed.
Cell 003 not started.
