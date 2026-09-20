from __future__ import annotations

import unittest

from src.cockpit.edge_entitlement_v0 import (
    ESTABLISHED,
    SCHEMA_VERSION,
    canonical_json,
    sha256_hex,
    verify_exact_relation_claim,
)


class EdgeRelationEntitlementExpandedThreat002(unittest.TestCase):
    def test_self_authored_exact_claim_is_accepted_without_source_standing(self):
        artifact_id = "ART-SELF-AUTHORED-EDGE-002"
        from_ref = "FRACTURE-17"
        to_ref = "OP-0218"
        relation_type = "MOTIVATED"

        # Expanded threat: the caller authors the entire claim artifact and pins
        # its own digest. No independent issuer, standing, adjudication, or
        # authority basis exists anywhere in this artifact schema.
        data = canonical_json(
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": artifact_id,
                "relation_claims": [
                    {
                        "from_ref": from_ref,
                        "relation_type": relation_type,
                        "to_ref": to_ref,
                    }
                ],
            }
        )
        caller_selected_digest = sha256_hex(data)

        result = verify_exact_relation_claim(
            data,
            expected_sha256=caller_selected_digest,
            expected_artifact_id=artifact_id,
            from_ref=from_ref,
            relation_type=relation_type,
            to_ref=to_ref,
        )

        self.assertEqual(result.status, ESTABLISHED)


if __name__ == "__main__":
    unittest.main()
