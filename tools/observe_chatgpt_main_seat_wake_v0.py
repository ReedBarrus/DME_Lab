#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.chatgpt_main_seat import build_wake
from src.cockpit.workcycle_projection import build_workcycle_projection

OUT = ROOT / "docs" / "evidence" / "for_planner" / "chatgpt_main_seat_wake_v0_observation.json"

EXPECTED_BLOBS = {
    "seat_manifest": (
        "continuity/seats/chatgpt-main.json",
        "5851425b1ff2815caed14db108eb7ebddd6d02d2",
    ),
    "working_state": (
        "continuity/current_state/chatgpt_main_working_state_v0.json",
        "547fcdf3f3eb8ce76c7d87e87a17b4632ed4bd7d",
    ),
    "registry": (
        "continuity/registry.json",
        "fb671155740821a9aab9ceed30ac42014bdf2ebf",
    ),
    "cursor": (
        "continuity/cursors/chatgpt.json",
        "c25101bf46f0c2937c657ef154696889cf8e1602",
    ),
    "events": (
        "continuity/events.jsonl",
        "a646fb8521627e0ebda63766f38a30aadb3d6797",
    ),
    "inbox": (
        "continuity/queues/chatgpt-main/inbox.jsonl",
        "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    ),
    "outbox": (
        "continuity/queues/chatgpt-main/outbox.jsonl",
        "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    ),
    "wake_membrane": (
        "tools/chatgpt_main_seat.py",
        "5f5b78eecf8f7dca34c9e215e83ded4d4862d653",
    ),
    "horizon": (
        "docs/campaigns/chatgpt_main_seat_activation_001/HORIZON_SELECTION_CMS1_V0.md",
        "445621fa07aad2cab110ba3f8294cebe92bb7ed5",
    ),
    "contract": (
        "docs/campaigns/chatgpt_main_seat_activation_001/CMS1_CONTRACT_V0.md",
        "d2fa82317b1cb67327fa12183531ce3d7ad8ebac",
    ),
}


def git_blob(path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def event_ids(rows: list[dict]) -> list[str]:
    return [str(row["event_id"]) for row in rows]


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"remove existing {OUT.relative_to(ROOT)} first")

    actual_blobs = {
        name: git_blob(path)
        for name, (path, _) in EXPECTED_BLOBS.items()
    }
    blob_checks = {
        name: actual_blobs[name] == expected
        for name, (_, expected) in EXPECTED_BLOBS.items()
    }
    if not all(blob_checks.values()):
        raise SystemExit(f"frozen blob mismatch: {blob_checks}")

    wake = build_wake(ROOT, "HEAD")
    projection = build_workcycle_projection(ROOT)

    durable_seats = projection.get("seat_ecology", {}).get("durable_seats", [])
    occupied_runtime_seats = projection.get("seat_ecology", {}).get(
        "occupied_runtime_seats", []
    )

    chatgpt_rows = [
        seat for seat in durable_seats if seat.get("seat_id") == "CHATGPT_MAIN"
    ]
    chatgpt_seat = chatgpt_rows[0] if len(chatgpt_rows) == 1 else None

    unread_ids = event_ids(wake["unread_continuity_events"])
    prepared_ids = event_ids(wake["working_state_prepared_delta_events"])
    newer_ids = event_ids(wake["newer_than_working_state_events"])
    occupied_ids = {
        seat.get("seat_id")
        for seat in occupied_runtime_seats
        if isinstance(seat, dict)
    }

    checks = {
        "frozen_blobs_match": all(blob_checks.values()),
        "wake_status_ready": wake["status"] == "READY",
        "wake_seat_id": wake["seat_id"] == "CHATGPT_MAIN",
        "registry_identity": (
            wake["registry_identity"].get("consumer_id") == "chatgpt-main"
        ),
        "registry_working_state_ref": (
            wake["registry_identity"].get("working_state_ref")
            == "continuity/current_state/chatgpt_main_working_state_v0.json"
        ),
        "cursor_held_at_ce000006": (
            wake["cursor"].get("last_seen_event_id") == "CE-000006"
        ),
        "continuity_head_ce000041": wake["continuity_head"] == "CE-000041",
        "unread_count_35": len(unread_ids) == 35,
        "unread_range_exact": (
            unread_ids
            and unread_ids[0] == "CE-000007"
            and unread_ids[-1] == "CE-000041"
        ),
        "prepared_count_33": len(prepared_ids) == 33,
        "prepared_range_exact": (
            prepared_ids
            and prepared_ids[0] == "CE-000007"
            and prepared_ids[-1] == "CE-000039"
        ),
        "newer_events_exact": newer_ids == ["CE-000040", "CE-000041"],
        "fresh_occupant_reconstruction_required": (
            wake["fresh_occupant_reconstruction_required"] is True
        ),
        "cursor_advancement_not_authorized": (
            wake["cursor_advancement_authorized"] is False
        ),
        "manual_invocation_stays_opaque": (
            wake["registry_identity"].get("association_basis") == "MANUAL_ASSERTION"
            and wake["registry_identity"].get("resolution_status") == "OPAQUE"
        ),
        "planning_not_activated": wake["planning_activation_effect"] == "NONE",
        "authority_neutral": wake["authority_effect"] == "NONE_BY_WAKE",
        "execution_neutral": wake["execution_effect"] == "NONE_BY_WAKE",
        "cockpit_has_one_chatgpt_main_durable_seat": len(chatgpt_rows) == 1,
        "cockpit_consumer_identity": (
            chatgpt_seat is not None
            and chatgpt_seat.get("consumer_id") == "chatgpt-main"
        ),
        "cockpit_occupant_binding_visible": (
            chatgpt_seat is not None
            and chatgpt_seat.get("occupant_binding")
            == "MANUAL_TETHER_CANDIDATE"
        ),
        "durable_presence_does_not_imply_runtime_occupancy": (
            "CHATGPT_MAIN" not in occupied_ids
        ),
    }

    observation = {
        "object_type": "CHATGPT_MAIN_SEAT_WAKE_V0_OBSERVATION",
        "pressure_id": "CHATGPT_MAIN_SEAT_WAKE_V0_PRESSURE_001",
        "frozen_basis": {
            "expected_blobs": {
                name: expected
                for name, (_, expected) in EXPECTED_BLOBS.items()
            },
            "actual_blobs": actual_blobs,
            "blob_checks": blob_checks,
        },
        "wake": wake,
        "cockpit_projection": {
            "chatgpt_main_durable_seat": chatgpt_seat,
            "durable_seat_count": projection.get("seat_ecology", {}).get(
                "durable_seat_count"
            ),
            "runtime_seat_count": projection.get("seat_ecology", {}).get(
                "runtime_seat_count"
            ),
            "occupied_seat_count": projection.get("seat_ecology", {}).get(
                "occupied_seat_count"
            ),
            "chatgpt_main_runtime_occupied": "CHATGPT_MAIN" in occupied_ids,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "candidate_relations": {
            "durable_seat_basis_ne_live_occupant": "YES",
            "cursor_position_ne_working_semantic_state": "YES",
            "working_state_prepared_through_ne_current_continuity_head": "YES",
            "wake_ready_ne_fresh_occupant_reconstruction": "YES",
            "registry_working_state_binding_ne_native_invocation_binding": "YES",
            "cockpit_seat_discoverability_ne_live_occupancy": "YES",
        },
        "effects": {
            "cursor_advancement_effect": "NONE",
            "semantic_reconstruction_effect": "NONE",
            "planning_activation_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "One deterministic read-only wake over the exact ChatGPT-main durable "
            "seat candidate plus the existing Cockpit workcycle projection. A pass "
            "establishes only that the durable seat basis, registry binding, cursor-"
            "relative delta, snapshot/newer-event split, and Cockpit discoverability "
            "are mechanically reconstructable. It does not establish fresh-model "
            "semantic continuity, native ChatGPT context injection, live occupancy, "
            "cursor acknowledgement, planner-role qualification, authority, execution, "
            "or subjective/model-instance continuity."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] seat {wake['seat_id']} wake {wake['status']}")
    print(f"[OK] cursor {wake['cursor']['last_seen_event_id']}")
    print(f"[OK] continuity head {wake['continuity_head']}")
    print(f"[OK] unread events {len(unread_ids)}")
    print(f"[OK] prepared events {len(prepared_ids)}")
    print(f"[OK] newer events {newer_ids}")
    print(f"[OK] cockpit durable seat present {len(chatgpt_rows) == 1}")
    print(f"[OK] cockpit runtime occupied {'CHATGPT_MAIN' in occupied_ids}")
    print(f"[OK] cursor advancement authorized {wake['cursor_advancement_authorized']}")
    print(f"[OK] all_checks_pass {observation['all_checks_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
