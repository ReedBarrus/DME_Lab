from __future__ import annotations

import json
import unittest

from src.cockpit.edge_entitlement_v0 import (
    ESTABLISHED,
    NOT_ESTABLISHED,
    SCHEMA_VERSION,
    canonical_json,
    sha256_hex,
    verify_exact_relation_claim,
)


FROM_REF = "FRACTURE-17"
TO_REF = "OP-0218"
ARTIFACT_ID = "ART-EDGE-ENTITLEMENT-002"


def artifact_bytes(*claims, artifact_id=ARTIFACT_ID):
    return canonical_json(
        {
            "schema_version": SCHEMA_VERSION,
            "artifact_id": artifact_id,
            "relation_claims": list(claims),
        }
    )


def claim(relation_type, *, from_ref=FROM_REF, to_ref=TO_REF):
    return {
        "from_ref": from_ref,
        "relation_type": relation_type,
        "to_ref": to_ref,
    }


def verify(data, relation_type, *, digest=None, from_ref=FROM_REF, to_ref=TO_REF):
    return verify_exact_relation_claim(
        data,
        expected_sha256=digest or sha256_hex(data),
        expected_artifact_id=ARTIFACT_ID,
        from_ref=from_ref,
        relation_type=relation_type,
        to_ref=to_ref,
    )


class EdgeRelationEntitlementV0Tests(unittest.TestCase):
    def test_r1_exact_frozen_claim_establishes_exact_tuple(self):
        data = artifact_bytes(claim("MOTIVATED"))
        result = verify(data, "MOTIVATED")
        self.assertEqual(result.status, ESTABLISHED)
        self.assertEqual(result.reason, "EXACT_FROZEN_RELATION_CLAIM_PRESENT")

    def test_f1_real_artifact_with_no_relation_claims_does_not_establish(self):
        data = artifact_bytes()
        self.assertEqual(verify(data, "MOTIVATED").status, NOT_ESTABLISHED)

    def test_f2_referenced_by_does_not_upgrade_to_motivated(self):
        data = artifact_bytes(claim("REFERENCED_BY"))
        result = verify(data, "MOTIVATED")
        self.assertEqual(result.status, NOT_ESTABLISHED)
        self.assertEqual(result.reason, "EXACT_RELATION_CLAIM_ABSENT")

    def test_f3_motivated_does_not_upgrade_to_constrains(self):
        data = artifact_bytes(claim("MOTIVATED"))
        self.assertEqual(verify(data, "CONSTRAINS").status, NOT_ESTABLISHED)

    def test_f4_constrains_does_not_upgrade_to_incorporated(self):
        data = artifact_bytes(claim("CONSTRAINS"))
        self.assertEqual(verify(data, "INCORPORATED").status, NOT_ESTABLISHED)

    def test_f5_right_relation_wrong_endpoint_does_not_establish(self):
        data = artifact_bytes(claim("MOTIVATED", to_ref="OP-OTHER"))
        self.assertEqual(verify(data, "MOTIVATED").status, NOT_ESTABLISHED)

    def test_f6_modified_bytes_fail_old_pinned_digest(self):
        original = artifact_bytes(claim("MOTIVATED"))
        modified = artifact_bytes(claim("MOTIVATED"), claim("CONSTRAINS"))
        result = verify(modified, "MOTIVATED", digest=sha256_hex(original))
        self.assertEqual(result.status, NOT_ESTABLISHED)
        self.assertEqual(result.reason, "ARTIFACT_IDENTITY_MISMATCH")

    def test_f7_prose_mention_is_not_a_machine_relation_claim(self):
        malformed = json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": ARTIFACT_ID,
                "relation_claims": [],
                "notes": f"{FROM_REF} MOTIVATED {TO_REF}",
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        result = verify(malformed, "MOTIVATED")
        self.assertEqual(result.status, NOT_ESTABLISHED)
        self.assertEqual(result.reason, "INVALID_RELATION_CLAIM_ARTIFACT")


if __name__ == "__main__":
    unittest.main()
