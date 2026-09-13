from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.runtime.ntfs_usn_q_operation_pressure import adjudicate_pressure


def arm(*, verdict: str, endpoint_hash: str = "A", qualifying: bool = False) -> dict:
    return {
        "verdict": verdict,
        "endpoint_content_observation": {
            "C0": {"sha256": endpoint_hash},
            "C1": {"sha256": endpoint_hash},
            "endpoint_equivalent": True,
        },
        "usn_operation_observation": {
            "qualifying_record_observed": qualifying,
        },
    }


class NtfsUsnQOperationPressureTest(unittest.TestCase):
    def test_case_1_recovers_distinction(self) -> None:
        result = adjudicate_pressure(
            arm(verdict="NO QUALIFYING RECORD", qualifying=False),
            arm(verdict="QUALIFYING RECORD", qualifying=True),
        )
        self.assertEqual(result["distinction_recovery_verdict"], "DISTINCTION RECOVERED")
        self.assertTrue(result["endpoint_collision"])
        self.assertTrue(result["usn_differential"])

    def test_cases_2_and_3_do_not_recover_distinction(self) -> None:
        both_positive = adjudicate_pressure(
            arm(verdict="QUALIFYING RECORD", qualifying=True),
            arm(verdict="QUALIFYING RECORD", qualifying=True),
        )
        both_absent = adjudicate_pressure(
            arm(verdict="NO QUALIFYING RECORD", qualifying=False),
            arm(verdict="NO QUALIFYING RECORD", qualifying=False),
        )
        self.assertEqual(
            both_positive["distinction_recovery_verdict"], "DISTINCTION NOT RECOVERED"
        )
        self.assertEqual(
            both_absent["distinction_recovery_verdict"], "DISTINCTION NOT RECOVERED"
        )

    def test_case_4_preserves_basis_instability_as_unresolved(self) -> None:
        result = adjudicate_pressure(
            arm(verdict="QUALIFYING RECORD", qualifying=True),
            arm(verdict="NO QUALIFYING RECORD", qualifying=False),
        )
        self.assertEqual(result["distinction_recovery_verdict"], "UNRESOLVED")

    def test_contract_fracture_is_invalid(self) -> None:
        result = adjudicate_pressure(
            {"verdict": "INVALID"},
            arm(verdict="QUALIFYING RECORD", qualifying=True),
        )
        self.assertEqual(result["distinction_recovery_verdict"], "INVALID")

    def test_endpoint_inequality_is_invalid(self) -> None:
        stasis = arm(verdict="NO QUALIFYING RECORD", qualifying=False)
        operation = arm(verdict="QUALIFYING RECORD", qualifying=True)
        operation["endpoint_content_observation"]["C1"]["sha256"] = "B"
        operation["endpoint_content_observation"]["endpoint_equivalent"] = False
        result = adjudicate_pressure(stasis, operation)
        self.assertEqual(result["distinction_recovery_verdict"], "INVALID")

    def test_retained_trace_supports_only_the_bounded_recovery(self) -> None:
        root = Path(__file__).resolve().parents[2]
        trace = json.loads(
            (root / "traces" / "ntfs_usn_q_operation_pressure_v0.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            trace["cross_arm"],
            {
                "endpoint_collision": True,
                "usn_differential": True,
                "distinction_recovery_verdict": "DISTINCTION RECOVERED",
            },
        )
        self.assertTrue(trace["Q_CONTENT_not_pressured"])
        self.assertFalse(
            trace["arms"]["S"]["usn_operation_observation"][
                "qualifying_record_observed"
            ]
        )
        self.assertTrue(
            trace["arms"]["O"]["usn_operation_observation"][
                "qualifying_record_observed"
            ]
        )
        self.assertEqual(
            trace["arms"]["S"]["file_identity"]["C0"]["fileID64"],
            trace["arms"]["O"]["file_identity"]["C0"]["fileID64"],
        )


if __name__ == "__main__":
    unittest.main()
