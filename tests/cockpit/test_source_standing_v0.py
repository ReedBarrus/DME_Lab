from __future__ import annotations

import inspect
import json
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from src.cockpit.edge_entitlement_v0 import (
    SCHEMA_VERSION as CLAIM_SCHEMA_VERSION,
    canonical_json as claim_canonical_json,
    sha256_hex as claim_sha256_hex,
)
from src.cockpit.source_standing_v0 import (
    DEVELOPMENTAL_RELATION_JURISDICTION,
    SOURCE_STANDING_ESTABLISHED,
    SOURCE_STANDING_NOT_ESTABLISHED,
    STANDING_SCHEMA_VERSION,
    SourceStandingEvaluatorV0,
    canonical_json,
    key_fingerprint,
)


SOURCE = "S*"
FROM = "FROM*"
TO = "TO*"
TO_NEAR = "TO_NEAR*"
RELATION = "MOTIVATED"
RELATION_ALT = "REFERENCED_BY"
CLAIM_ARTIFACT_ID = "CLAIM-C*"
CONTROL_CHALLENGE = b"EDGE_SOURCE_STANDING_001_CONTROL_CHALLENGE"


def _public_raw(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        Encoding.Raw,
        PublicFormat.Raw,
    )


class _ClaimantHarness:
    """Synthetic common-control surface for S* and puppet issuer I*.

    One harness owns both private signing capabilities. No boolean such as
    claimant_controls_issuer is supplied to the candidate.
    """

    def __init__(self) -> None:
        self._source_private = Ed25519PrivateKey.generate()
        self._puppet_private = Ed25519PrivateKey.generate()

    @property
    def source_public_raw(self) -> bytes:
        return _public_raw(self._source_private)

    @property
    def puppet_public_raw(self) -> bytes:
        return _public_raw(self._puppet_private)

    def sign_as_source(self, data: bytes) -> bytes:
        return self._source_private.sign(data)

    def sign_as_puppet(self, data: bytes) -> bytes:
        return self._puppet_private.sign(data)

    def mechanically_observe_common_control(self) -> dict[str, bool]:
        source_sig = self.sign_as_source(CONTROL_CHALLENGE)
        puppet_sig = self.sign_as_puppet(CONTROL_CHALLENGE)

        self._source_private.public_key().verify(
            source_sig,
            CONTROL_CHALLENGE,
        )
        self._puppet_private.public_key().verify(
            puppet_sig,
            CONTROL_CHALLENGE,
        )
        return {
            "same_harness_exercised_source_key": True,
            "same_harness_exercised_puppet_key": True,
        }


def _claim_bytes() -> bytes:
    return claim_canonical_json(
        {
            "schema_version": CLAIM_SCHEMA_VERSION,
            "artifact_id": CLAIM_ARTIFACT_ID,
            "relation_claims": [
                {
                    "from_ref": FROM,
                    "relation_type": RELATION,
                    "to_ref": TO,
                }
            ],
        }
    )


def _standing_bytes(
    *,
    source_ref: str,
    issuer_ref: str,
    issuer_public_raw: bytes,
    jurisdiction: str,
    relation_classes: list[str],
    endpoint_pairs: list[tuple[str, str]],
    grant_id: str,
) -> bytes:
    return canonical_json(
        {
            "schema_version": STANDING_SCHEMA_VERSION,
            "grant_id": grant_id,
            "source_ref": source_ref,
            "issuer_ref": issuer_ref,
            "issuer_key_fingerprint": key_fingerprint(
                issuer_public_raw
            ),
            "jurisdiction": jurisdiction,
            "relation_classes": relation_classes,
            "endpoint_pairs": [
                {"from_ref": from_ref, "to_ref": to_ref}
                for from_ref, to_ref in endpoint_pairs
            ],
        }
    )


def _root_signed_cell(
    root_private: Ed25519PrivateKey,
    *,
    grant_id: str,
    relation_classes: list[str],
    endpoint_pairs: list[tuple[str, str]],
    jurisdiction: str = DEVELOPMENTAL_RELATION_JURISDICTION,
) -> tuple[bytes, bytes]:
    root_public_raw = _public_raw(root_private)
    standing = _standing_bytes(
        source_ref=SOURCE,
        issuer_ref="GROUNDING_ROOT*",
        issuer_public_raw=root_public_raw,
        jurisdiction=jurisdiction,
        relation_classes=relation_classes,
        endpoint_pairs=endpoint_pairs,
        grant_id=grant_id,
    )
    return standing, root_private.sign(standing)


def _build_fixture():
    """Build all raw fixtures before evaluation.

    The protected grounding private key is intentionally not returned.
    """

    root_private = Ed25519PrivateKey.generate()
    root_public_raw = _public_raw(root_private)
    claimant = _ClaimantHarness()

    p1 = _root_signed_cell(
        root_private,
        grant_id="GRANT-P1",
        relation_classes=[RELATION],
        endpoint_pairs=[(FROM, TO)],
    )

    h2 = _root_signed_cell(
        root_private,
        grant_id="GRANT-H2",
        relation_classes=[RELATION_ALT],
        endpoint_pairs=[(FROM, TO)],
    )

    h3 = _root_signed_cell(
        root_private,
        grant_id="GRANT-H3",
        relation_classes=[RELATION],
        endpoint_pairs=[(FROM, TO_NEAR)],
    )

    h5 = _root_signed_cell(
        root_private,
        grant_id="GRANT-H5",
        relation_classes=[RELATION],
        endpoint_pairs=[(FROM, TO)],
        jurisdiction="OTHER_LEGITIMATE_JURISDICTION",
    )

    puppet_public_raw = claimant.puppet_public_raw
    h4_standing = _standing_bytes(
        source_ref=SOURCE,
        issuer_ref="I*",
        issuer_public_raw=puppet_public_raw,
        jurisdiction=DEVELOPMENTAL_RELATION_JURISDICTION,
        relation_classes=[RELATION],
        endpoint_pairs=[(FROM, TO)],
        grant_id="GRANT-H4-PUPPET",
    )
    h4 = (
        h4_standing,
        claimant.sign_as_puppet(h4_standing),
    )

    control_observation = claimant.mechanically_observe_common_control()

    cells = {
        "P1": p1,
        "H1": (None, None),
        "H2": h2,
        "H3": h3,
        "H4": h4,
        "H5": h5,
    }

    # root_private deliberately does not cross this boundary.
    return root_public_raw, claimant, control_observation, cells


def run_qualification_vector() -> dict[str, object]:
    claim_bytes = _claim_bytes()
    claim_sha = claim_sha256_hex(claim_bytes)
    root_public_raw, claimant, control_observation, cells = _build_fixture()

    evaluator = SourceStandingEvaluatorV0(
        grounding_public_key_raw=root_public_raw
    )

    observed: dict[str, dict[str, str | None]] = {}
    for label, (standing_bytes, signature) in cells.items():
        result = evaluator.derive(
            claim_artifact_bytes=claim_bytes,
            expected_claim_sha256=claim_sha,
            expected_claim_artifact_id=CLAIM_ARTIFACT_ID,
            source_ref=SOURCE,
            from_ref=FROM,
            relation_type=RELATION,
            to_ref=TO,
            standing_basis_bytes=standing_bytes,
            grounding_signature=signature,
        )
        observed[label] = {
            "status": result.status,
            "reason": result.reason,
            "standing_sha256": result.standing_sha256,
        }

    return {
        "claim_sha256": claim_sha,
        "claim_bytes_hex": claim_bytes.hex(),
        "root_public_key_fingerprint": key_fingerprint(root_public_raw),
        "claimant_source_key_fingerprint": key_fingerprint(
            claimant.source_public_raw
        ),
        "claimant_puppet_key_fingerprint": key_fingerprint(
            claimant.puppet_public_raw
        ),
        "control_observation": control_observation,
        "observed": observed,
    }


class EdgeSourceStandingCandidate001Tests(unittest.TestCase):
    def test_six_cell_vector(self):
        vector = run_qualification_vector()
        observed = vector["observed"]

        self.assertEqual(
            observed["P1"]["status"],
            SOURCE_STANDING_ESTABLISHED,
        )
        for label in ("H1", "H2", "H3", "H4", "H5"):
            self.assertEqual(
                observed[label]["status"],
                SOURCE_STANDING_NOT_ESTABLISHED,
            )

    def test_required_hostile_coordinates_are_distinguished(self):
        observed = run_qualification_vector()["observed"]

        self.assertEqual(
            observed["H1"]["reason"],
            "NO_GROUNDED_STANDING_BASIS",
        )
        self.assertEqual(
            observed["H2"]["reason"],
            "RELATION_CLASS_NOT_COVERED",
        )
        self.assertEqual(
            observed["H3"]["reason"],
            "ENDPOINT_SCOPE_NOT_COVERED",
        )
        self.assertEqual(
            observed["H4"]["reason"],
            "GROUNDING_SIGNATURE_INVALID",
        )
        self.assertEqual(
            observed["H5"]["reason"],
            "JURISDICTION_NOT_COVERED",
        )

    def test_h4_uses_distinct_identities_under_one_claimant_harness(self):
        vector = run_qualification_vector()

        self.assertNotEqual(
            vector["claimant_source_key_fingerprint"],
            vector["claimant_puppet_key_fingerprint"],
        )
        self.assertTrue(
            vector["control_observation"][
                "same_harness_exercised_source_key"
            ]
        )
        self.assertTrue(
            vector["control_observation"][
                "same_harness_exercised_puppet_key"
            ]
        )
        self.assertEqual(
            vector["observed"]["H4"]["status"],
            SOURCE_STANDING_NOT_ESTABLISHED,
        )

    def test_valid_grounding_signature_alone_is_insufficient(self):
        observed = run_qualification_vector()["observed"]

        # H2, H3, and H5 are all signed by the protected grounding root.
        self.assertEqual(
            observed["H2"]["status"],
            SOURCE_STANDING_NOT_ESTABLISHED,
        )
        self.assertEqual(
            observed["H3"]["status"],
            SOURCE_STANDING_NOT_ESTABLISHED,
        )
        self.assertEqual(
            observed["H5"]["status"],
            SOURCE_STANDING_NOT_ESTABLISHED,
        )

    def test_candidate_interface_has_no_answer_or_cell_oracle_inputs(self):
        params = set(
            inspect.signature(SourceStandingEvaluatorV0.derive).parameters
        )
        forbidden = {
            "independent",
            "grounding_accepted",
            "claimant_controls_issuer",
            "standing_valid",
            "authorized",
            "cell_id",
            "expected_result",
        }
        self.assertTrue(params.isdisjoint(forbidden))

        p1_bytes, _ = _build_fixture()[3]["P1"]
        raw_fields = set(json.loads(p1_bytes))
        self.assertTrue(raw_fields.isdisjoint(forbidden))

    def test_claim_bytes_are_identical_for_entire_vector(self):
        # One immutable claim byte string is constructed and reused for every
        # evaluator call in run_qualification_vector.
        first = _claim_bytes()
        second = _claim_bytes()
        self.assertEqual(first, second)
        self.assertEqual(
            claim_sha256_hex(first),
            claim_sha256_hex(second),
        )


if __name__ == "__main__":
    unittest.main()
