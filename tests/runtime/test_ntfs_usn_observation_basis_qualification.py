from __future__ import annotations

import json
from pathlib import Path
import struct
import unittest

from src.runtime.ntfs_usn_observation_basis_qualification import (
    QualificationError,
    USN_REASON_CLOSE,
    USN_REASON_DATA_OVERWRITE,
    adjudicate_cross_arm,
    compose_file_id64,
    parse_v2_records,
    record_acceptance,
)


def v2_record(
    *,
    file_id: int = 0xFEDCBA9876543210,
    usn: int = 150,
    reason: int = USN_REASON_CLOSE | USN_REASON_DATA_OVERWRITE,
    source_info: int = 0,
    name: str = "fixture.bin",
) -> bytes:
    encoded_name = name.encode("utf-16-le")
    header_size = 60
    record_length = header_size + len(encoded_name)
    return struct.pack(
        "<IHHQQqqIIIIHH",
        record_length,
        2,
        0,
        file_id,
        1,
        usn,
        0,
        reason,
        source_info,
        0,
        0x80,
        len(encoded_name),
        header_size,
    ) + encoded_name


class NtfsUsnObservationBasisUnitTests(unittest.TestCase):
    def test_unsigned_file_id_composition_matches_v2_width(self) -> None:
        self.assertEqual(compose_file_id64(0xFEDCBA98, 0x76543210), 0xFEDCBA9876543210)

    def test_parser_uses_continuation_and_preserves_v2_fields(self) -> None:
        continuation, records = parse_v2_records(struct.pack("<q", 200) + v2_record())
        self.assertEqual(continuation, 200)
        self.assertEqual(records[0]["major_version"], 2)
        self.assertEqual(records[0]["file_name"], "fixture.bin")
        self.assertEqual(
            int(records[0]["file_reference_number"]["decimal"]),
            0xFEDCBA9876543210,
        )

    def test_acceptance_enforces_reason_conjunction_not_reason_mask_alone(self) -> None:
        _, records = parse_v2_records(
            struct.pack("<q", 200) + v2_record(reason=USN_REASON_CLOSE)
        )
        result = record_acceptance(
            records[0], start_usn=100, end_usn=200, file_id64=0xFEDCBA9876543210
        )
        self.assertFalse(result["accepted"])
        self.assertTrue(result["checks"]["reason_contains_close"])
        self.assertFalse(result["checks"]["reason_contains_data_overwrite"])

    def test_acceptance_rejects_end_exclusive_record_and_nonzero_source_info(self) -> None:
        _, records = parse_v2_records(
            struct.pack("<q", 201) + v2_record(usn=200, source_info=1)
        )
        result = record_acceptance(
            records[0], start_usn=100, end_usn=200, file_id64=0xFEDCBA9876543210
        )
        self.assertFalse(result["accepted"])
        self.assertFalse(result["checks"]["within_frozen_interval"])
        self.assertFalse(result["checks"]["source_info_policy_satisfied"])

    def test_parser_rejects_unsupported_major_version(self) -> None:
        record = bytearray(v2_record())
        struct.pack_into("<H", record, 4, 3)
        with self.assertRaises(QualificationError):
            parse_v2_records(struct.pack("<q", 200) + record)

    def test_cross_arm_outcome_table_preserves_aa_ab_meaning(self) -> None:
        both = adjudicate_cross_arm("QUALIFYING RECORD", "QUALIFYING RECORD")
        self.assertEqual(both["basis"], "LOCAL BASIS QUALIFIED")
        self.assertIn("does not discriminate", both["operation_vs_content"])

        narrower = adjudicate_cross_arm("NO QUALIFYING RECORD", "QUALIFYING RECORD")
        self.assertEqual(narrower["basis"], "LOCAL BASIS QUALIFIED FOR NARROWER ARM AB REGIME")

        inverse = adjudicate_cross_arm("QUALIFYING RECORD", "NO QUALIFYING RECORD")
        self.assertEqual(inverse["basis"], "BASIS NOT QUALIFIED")

    def test_retained_trace_supports_the_bounded_local_verdict(self) -> None:
        root = Path(__file__).resolve().parents[2]
        trace = json.loads(
            (root / "traces" / "ntfs_usn_observation_basis_qualification_v0.json").read_text(
                encoding="utf-8"
            )
        )
        aa = trace["arms"]["AA"]
        ab = trace["arms"]["AB"]
        self.assertEqual(trace["cross_arm"]["basis"], "LOCAL BASIS QUALIFIED")
        self.assertEqual(aa["verdict"], "QUALIFYING RECORD")
        self.assertEqual(ab["verdict"], "QUALIFYING RECORD")
        self.assertEqual(
            aa["baseline_endpoint"]["identity"]["fileID64"],
            ab["baseline_endpoint"]["identity"]["fileID64"],
        )
        self.assertEqual(aa["baseline_endpoint"]["sha256"], aa["final_endpoint"]["sha256"])
        self.assertNotEqual(ab["baseline_endpoint"]["sha256"], ab["final_endpoint"]["sha256"])
        for arm in (aa, ab):
            self.assertTrue(arm["qualifying_records"])
            self.assertTrue(arm["qualifying_records"][0]["acceptance"]["accepted"])
            self.assertEqual(arm["qualifying_records"][0]["source_info"]["decimal"], "0")


if __name__ == "__main__":
    unittest.main()
