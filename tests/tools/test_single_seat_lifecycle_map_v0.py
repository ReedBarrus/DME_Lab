from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "docs" / "campaigns" / "sca001" / "SINGLE_SEAT_ATLAS_LIFECYCLE_OPERATOR_MAP_V0_CANDIDATE.md"


def main() -> None:
    text = MAP.read_text(encoding="utf-8")

    required_states = [
        "S0 DORMANT",
        "S1 RECOVERING",
        "S2 READY",
        "S3 PRESSURE_SELECTED",
        "S4 INVOCATION_PROPOSED",
        "S5 AUTHORIZED",
        "S6 INVOCATION_STARTED",
        "S7 RESULT_WITNESSED",
        "S8 SETTLEMENT_PENDING",
        "S9 CANDIDATE_SETTLED",
        "S10 ADJUDICATION_PENDING",
        "S11 QUALIFIED_UPDATE",
        "S12 ATLAS_UPDATED",
        "S13 PAUSED",
        "S14 STOPPED",
    ]
    required_operators = [f"O{i} " for i in range(1, 19)]
    required_failure_states = [f"F{i} " for i in range(1, 8)]

    for token in required_states + required_operators + required_failure_states:
        assert token in text, f"missing lifecycle token: {token}"

    invariants = [
        "MODEL OUTPUT\n!=\nMETABOLIZED STATE",
        "BUDGET_EXHAUSTED\n→ PAUSE OR STOP\n→ NO SILENT CONTINUATION",
        "Seat lineage must remain distinct from occupant identity.",
        "Model selection does not modify seat authority.",
        "automatic replay denied",
    ]
    for invariant in invariants:
        assert invariant in text, f"missing lifecycle invariant: {invariant}"

    print("PASS: single-seat lifecycle map V0 structural invariants")


if __name__ == "__main__":
    main()
