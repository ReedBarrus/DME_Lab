# LOAD_TRANSFER_001 — LIVE SEAT A READY-TO-SEND

OBJECT_TYPE:
READY_TO_SEND_WORK_PACKET

ROLE:
IMPLEMENTER

WORK_ITEM:
LOAD_TRANSFER_001_W1_IMPLEMENTER

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
ONE_BOUNDED_REPO_TRANSFORMATION

AUTHORITY_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

## SOURCE

Read only:

1. `docs/campaigns/load_transfer_001/CURRENT_OPERATIVE_FRAME_V0.json`
2. work item `LOAD_TRANSFER_001_W1_IMPLEMENTER` from
   `docs/campaigns/load_transfer_001/WORK_QUEUE_V0.jsonl`
3. `docs/campaigns/load_transfer_001/LOAD_TRANSFER_001_FRAME.md`
4. `src/coordination/load_transfer_v0.py`

Do not use prior conversation context.

## ACTION

Execute the work item's declared transformation exactly.

Create only:

`docs/campaigns/load_transfer_001/pressure_runs/LOAD_TRANSFER_001_OUTPUT_O1.md`

Then:

1. bind the exact output bytes with `artifact_descriptor`;
2. complete W1 using the declared lifecycle;
3. emit handoff id `LOAD_TRANSFER_001_H1`;
4. append the terminal W1 record to the retained work history;
5. append H1 to `HANDOFFS_V0.jsonl`;
6. stop.

Do not start W2.
Do not repair unrelated files.
Do not change campaign standing.
Do not modify trust-root / bridge / authority surfaces.

## REQUIRED RETURN

Return only:

```
WORK_ITEM_ID:
RESULT_POSTURE:
OUTPUT_PATH:
OUTPUT_DESCRIPTOR_ID:
HANDOFF_ID:
UNRESOLVED:
AUTHORITY_EFFECT:
SCIENTIFIC_STANDING_EFFECT:
STOPPED:
```
