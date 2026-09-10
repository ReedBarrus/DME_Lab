from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.cockpit.generate_projection import generate_projection


class GenerateCockpitProjectionTest(unittest.TestCase):
    def test_success_writes_one_normalized_json_file(self) -> None:
        model = {
            "repository_state": {
                "source_commit": "a" * 40,
                "projection_status": "complete",
                "freshness": {"status": "current"},
            },
            "pressure_nodes": [],
            "pressure_relations": [],
            "constraints": [],
            "evidence_refs": [],
            "projection_documents": [],
            "projection_diagnostics": [],
        }
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "generated" / "cockpit_projection.json"
            with patch(
                "src.cockpit.generate_projection.build_projection",
                return_value=model,
            ):
                returned = generate_projection(
                    repo=".",
                    source_ref="a" * 40,
                    freshness_ref="origin/main",
                    output=output,
                    projection_time="2026-09-09T12:00:00Z",
                )

            self.assertEqual(returned, model)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), model)
            self.assertFalse(output.with_name(output.name + ".tmp").exists())

    def test_generation_failure_removes_stale_output(self) -> None:
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "cockpit_projection.json"
            output.write_text('{"stale": true}\n', encoding="utf-8")

            with patch(
                "src.cockpit.generate_projection.build_projection",
                side_effect=RuntimeError("synthetic adapter failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic adapter failure"):
                    generate_projection(
                        repo=".",
                        source_ref="HEAD",
                        freshness_ref="origin/main",
                        output=output,
                    )

            self.assertFalse(output.exists())
            self.assertFalse(output.with_name(output.name + ".tmp").exists())


if __name__ == "__main__":
    unittest.main()
