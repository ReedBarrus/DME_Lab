from __future__ import annotations

import unittest
from pathlib import Path

from src.cockpit.concordance_v0 import (
    ArtifactRefV0,
    DevelopmentEdgeV0,
    OperationV0,
    SeatV0,
    build_concordance_projection,
)


SPECIMEN_REL = Path(
    "docs/candidates/concordance_cockpit_v0/specimens/"
    "NON_ENTITLING_BASIS_001.md"
)


class ConcordanceEdgeSemanticEntitlementPressure001(unittest.TestCase):
    def test_real_non_entitling_basis_can_launder_motivated_edge(self):
        repo_root = Path(__file__).resolve().parents[2]
        specimen_path = repo_root / SPECIMEN_REL
        specimen_text = specimen_path.read_text(encoding="utf-8")

        self.assertIn("ENTITLES_RELATION_TYPES:\nNONE", specimen_text)
        self.assertIn(
            "ART-NON-ENTITLING-001 MOTIVATED OP-EDGE-TARGET-001",
            specimen_text,
        )

        seat = SeatV0(
            seat_id="WORKSHOP",
            role="bounded pressure executor",
        )
        operation = OperationV0(
            operation_id="OP-EDGE-TARGET-001",
            seat_id="WORKSHOP",
            parent_operation_id=None,
            role="bounded pressure executor",
            purpose="receive a developmental relation under pressure",
            authority_ref=None,
            status="STOPPED",
        )
        artifact = ArtifactRefV0(
            artifact_id="ART-NON-ENTITLING-001",
            kind="NON_ENTITLING_EDGE_BASIS_SPECIMEN",
            locator=f"repo://{SPECIMEN_REL.as_posix()}",
        )
        edge = DevelopmentEdgeV0(
            edge_id="EDGE-SEMANTIC-LAUNDER-001",
            from_ref="ART-NON-ENTITLING-001",
            to_ref="OP-EDGE-TARGET-001",
            relation_type="MOTIVATED",
            basis_refs=("ART-NON-ENTITLING-001",),
            status="SUPPORTED",
        )

        projection = build_concordance_projection(
            seats=(seat,),
            operations=(operation,),
            artifacts=(artifact,),
            handoffs=(),
            fractures=(),
            development_edges=(edge,),
        )

        self.assertEqual(len(projection["development_edges"]), 1)
        rendered = projection["development_edges"][0]
        self.assertEqual(rendered["relation_type"], "MOTIVATED")
        self.assertEqual(rendered["render_status"], "SUPPORTED")
        self.assertEqual(projection["unresolved_relations"], [])


if __name__ == "__main__":
    unittest.main()
