# LOAD_TRANSFER_001 — LIVE SEAT B READY-TO-SEND

OBJECT_TYPE:
READY_TO_SEND_WORK_PACKET

ROLE:
REVIEWER

WORK_ITEM:
LOAD_TRANSFER_001_W2_REVIEWER

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
PREDECESSOR_HANDOFF_REQUIRED

AUTHORITY_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

## ELIGIBILITY GATE

Do not begin work unless all of the following exist and validate:

1. current `CURRENT_OPERATIVE_FRAME_V0.json`;
2. terminal W1 record for `LOAD_TRANSFER_001_W1_IMPLEMENTER`;
3. handoff `LOAD_TRANSFER_001_H1` in `HANDOFFS_V0.jsonl`;
4. exact Seat A output:
   `docs/campaigns/load_transfer_001/pressure_runs/LOAD_TRANSFER_001_OUTPUT_O1.md`;
5. H1 output descriptor matches the exact O1 bytes.

If any requirement is absent, malformed, stale, or identity-mismatched:

```
RESULT_POSTURE:
HELD

UNRESOLVED:
<exact missing/mismatched coordinate>

STOPPED:
YES
```

Do not ask Reed to narrate the missing state.

## SOURCE

After the gate passes, use only:

- current operative frame;
- W2 `LOAD_TRANSFER_001_W2_REVIEWER`;
- terminal W1;
- H1;
- exact O1 bytes;
- `src/coordination/load_transfer_v0.py`.

Do not use Seat A's live chat or predecessor reasoning.

## ACTION

Claim W2 using exact H1 as `available_handoffs`.

Review O1 only against:
- the operative frame;
- W1 contract;
- W1 claim ceiling;
- W1 forbidden consequences;
- H1 identities / unresolveds.

Create only:

`docs/campaigns/load_transfer_001/pressure_runs/LOAD_TRANSFER_001_REVIEW_O2.md`

Do not repair O1.

Then:

1. bind O2 exact bytes;
2. complete W2;
3. emit `LOAD_TRANSFER_001_H2`;
4. retain the terminal W2 record;
5. append H2;
6. stop.

Do not route onward.
Do not create another work item.
Do not promote campaign/scientific standing.

## REQUIRED RETURN

Return only:

```
WORK_ITEM_ID:
PREDECESSOR_HANDOFF:
RESULT_POSTURE:
OUTPUT_PATH:
OUTPUT_DESCRIPTOR_ID:
HANDOFF_ID:
UNRESOLVED:
AUTHORITY_EFFECT:
SCIENTIFIC_STANDING_EFFECT:
STOPPED:
```
