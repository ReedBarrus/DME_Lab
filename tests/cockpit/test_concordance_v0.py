from __future__ import annotations

import unittest

from src.cockpit.concordance_v0 import (
    ArtifactRefV0,
    DevelopmentEdgeV0,
    FractureV0,
    HandoffV0,
    OperationV0,
    SeatV0,
    build_concordance_projection,
)


class ConcordanceCockpitV0Tests(unittest.TestCase):
    def fixture(self, *, edges=(), authority_ref="ART-AUTH"):
        seats = (
            SeatV0(
                seat_id="SOL-04",
                role="adversarial design reviewer",
                archetype="THE FOOL",
                callsign="FOO'",
            ),
            SeatV0(seat_id="COMMANDER", role="scientific adjudicator"),
        )
        artifacts = (
            ArtifactRefV0(
                artifact_id="ART-AUTH",
                kind="AUTHORITY_REFERENCE",
                locator="repo://grants/operation-authorization",
            ),
            ArtifactRefV0(
                artifact_id="ART-FRACTURE",
                kind="FRACTURE_RECEIPT",
                locator="git://receipt",
            ),
            ArtifactRefV0(
                artifact_id="ART-HANDOFF",
                kind="HANDOFF_PACKET",
                locator="repo://handoff",
            ),
        )
        operations = (
            OperationV0(
                operation_id="OP-0212",
                seat_id="SOL-04",
                parent_operation_id=None,
                role="adversarial design reviewer",
                purpose="pressure durable witness against same-process forgery",
                authority_ref=authority_ref,
                status="FRACTURED",
                last_checkpoint_ref="ART-FRACTURE",
                outputs=("ART-FRACTURE",),
                fracture_ref="FRACTURE-17",
                stop_reason="qualification fracture",
                next_proposed_operation="isolate witness completion capability",
            ),
        )
        fractures = (
            FractureV0(
                fracture_id="FRACTURE-17",
                operation_id="OP-0212",
                expected="no valid completion without executor invocation",
                observed="executor_calls = 0; verifier = ESTABLISHED",
                cause_surface="same-process reflective access to signing capability",
                surviving_distinction="PRIVATE-BY-CONVENTION != PROTECTED CAPABILITY",
                basis_refs=("ART-FRACTURE",),
            ),
        )
        handoffs = (
            HandoffV0(
                handoff_id="HANDOFF-884",
                from_operation_id="OP-0212",
                to_seat_id="COMMANDER",
                relation_type="REQUESTS",
                basis_refs=("ART-HANDOFF",),
            ),
        )
        return build_concordance_projection(
            seats=seats,
            operations=operations,
            artifacts=artifacts,
            handoffs=handoffs,
            fractures=fractures,
            development_edges=edges,
        )

    def test_v0_keeps_core_objects_separate(self):
        model = self.fixture()
        self.assertEqual(len(model["seats"]), 2)
        self.assertEqual(len(model["operations"]), 1)
        self.assertEqual(len(model["artifacts"]), 3)
        self.assertEqual(len(model["handoffs"]), 1)
        self.assertEqual(len(model["fractures"]), 1)

    def test_handoff_does_not_imply_authority(self):
        model = self.fixture()
        self.assertEqual(model["handoffs"][0]["authority_effect"], "NONE")
        self.assertFalse(model["projection_claims"]["handoff_implies_authority"])

    def test_operation_completion_or_fracture_does_not_create_standing(self):
        model = self.fixture()
        operation = model["operations"][0]
        fracture = model["fractures"][0]
        self.assertEqual(operation["scientific_standing"], "NOT_INFERRED_BY_V0")
        self.assertEqual(fracture["standing_effect"], "NONE")
        self.assertFalse(model["projection_claims"]["operation_complete_implies_standing"])
        self.assertFalse(model["projection_claims"]["fracture_implies_downstream_change"])

    def test_authority_is_only_exposed_as_reference_not_resolved_truth(self):
        model = self.fixture()
        authority = model["operations"][0]["authority_projection"]
        self.assertEqual(authority["authority_ref"], "ART-AUTH")
        self.assertTrue(authority["basis_present"])
        self.assertEqual(authority["authority_state"], "UNRESOLVED_BY_V0")

    def test_missing_authority_basis_stays_explicit(self):
        model = self.fixture(authority_ref="ART-MISSING")
        authority = model["operations"][0]["authority_projection"]
        self.assertFalse(authority["basis_present"])
        self.assertEqual(authority["authority_state"], "UNRESOLVED_BY_V0")
        self.assertIn("MISSING_AUTHORITY_REF", {x["kind"] for x in model["diagnostics"]})

    def test_supported_development_edge_requires_real_basis(self):
        edge = DevelopmentEdgeV0(
            edge_id="EDGE-1",
            from_ref="FRACTURE-17",
            to_ref="OP-0212",
            relation_type="REFERENCED_BY",
            basis_refs=("ART-FRACTURE",),
        )
        model = self.fixture(edges=(edge,))
        self.assertEqual(len(model["development_edges"]), 1)
        self.assertEqual(model["development_edges"][0]["render_status"], "SUPPORTED")
        self.assertEqual(model["unresolved_relations"], [])

    def test_edge_without_basis_is_not_rendered_as_supported(self):
        edge = DevelopmentEdgeV0(
            edge_id="EDGE-2",
            from_ref="FRACTURE-17",
            to_ref="OP-0212",
            relation_type="MOTIVATED",
            basis_refs=(),
        )
        model = self.fixture(edges=(edge,))
        self.assertEqual(model["development_edges"], [])
        self.assertEqual(len(model["unresolved_relations"]), 1)
        self.assertIn("NO_BASIS_FOR_EDGE", model["unresolved_relations"][0]["reasons"])

    def test_missing_edge_basis_is_not_silently_repaired(self):
        edge = DevelopmentEdgeV0(
            edge_id="EDGE-3",
            from_ref="FRACTURE-17",
            to_ref="OP-0212",
            relation_type="CONSTRAINS",
            basis_refs=("ART-NOT-HERE",),
        )
        model = self.fixture(edges=(edge,))
        self.assertEqual(model["development_edges"], [])
        self.assertIn("MISSING_EDGE_BASIS", model["unresolved_relations"][0]["reasons"])

    def test_provisional_relation_stays_unresolved_even_with_basis(self):
        edge = DevelopmentEdgeV0(
            edge_id="EDGE-4",
            from_ref="FRACTURE-17",
            to_ref="OP-0212",
            relation_type="MOTIVATED",
            basis_refs=("ART-FRACTURE",),
            status="PROVISIONAL",
        )
        model = self.fixture(edges=(edge,))
        self.assertEqual(model["development_edges"], [])
        self.assertIn(
            "EDGE_NOT_ADJUDICATED_SUPPORTED",
            model["unresolved_relations"][0]["reasons"],
        )

    def test_graph_coherence_does_not_create_missing_edge(self):
        model = self.fixture()
        self.assertEqual(model["development_edges"], [])
        self.assertEqual(model["unresolved_relations"], [])


if __name__ == "__main__":
    unittest.main()
