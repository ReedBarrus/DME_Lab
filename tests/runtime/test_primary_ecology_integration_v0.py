from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from tools.primary_ecology_v0 import (
    authority_standing,
    clean_bundle,
    run_pressure,
)

ROOT = Path(__file__).resolve().parents[2]

SOURCE_SPECIMEN = "94096f1a2b00cd6a8f72947352fa1a5ce9006a4e"
TARGET_BASE = "f36261e17790b853a91c81bc2f7d0e63e8ee8436"
TRANSPLANT_COMMIT = "e185c3872f589b88c5d878f37b2dcc3f74a4ef0a"

SOURCE_BLOBS = {
    ".github/workflows/primary-ecology-grammar-001.yml": "dda7275a5dbea5158ca3e383e6578127d8d8a076",
    "docs/candidates/primary_ecology_v0/PRESSURE_DESIGN_001.md": "bb112fee093ef4d39b4d33137449511fa1db56ed",
    "docs/candidates/primary_ecology_v0/PRIMARY_ECOLOGY_CONTRACT_v0.md": "cae39b8e493b2e84710ad3e0efcf795e032fd765",
    "docs/candidates/primary_ecology_v0/QUALIFICATION_EVIDENCE_001.json": "5531f315454f5d181d020b01020a1c61898bd317",
    "docs/candidates/primary_ecology_v0/fixtures/EVALUATION_KEY_v0.json": "33f38bab4363507a0c924d0e04f037f82e2d8181",
    "docs/candidates/primary_ecology_v0/fixtures/RAW_FIXTURES_v0.json": "225965c6c42c1718e969f531f58fcde4159342d7",
    "docs/candidates/primary_ecology_v0/fixtures/ROLE_CATALOG_v0.json": "c5589955111b82a22df77aa7ede7ef3844b5cbdb",
    "docs/candidates/primary_ecology_v0/fixtures/SEAT_CATALOG_v0.json": "6843e09e30952ca4ecbc2da8ea507a7567fa2ae1",
    "schemas/ecology_engagement_binding_v0.schema.json": "30ce8dd40f78c1dc54fa953f033f16d2b89d1a34",
    "schemas/ecology_role_v0.schema.json": "250f155fc342463be7ebc6ca5f40b63b2e5f2c06",
    "schemas/ecology_seat_v0.schema.json": "70888b03eca8285a4f5549d87c32c31bda3e6a92",
    "schemas/missingness_witness_encounter_v0.schema.json": "cf012951a765025a742e8dfcdbf3d0471353ef6d",
    "schemas/missingness_witness_v0.schema.json": "73273eefcfeeb148e3ddb62f7db0b082d28a0255",
    "schemas/observation_basis_v0.schema.json": "e6db3c4a65c7d1b76b3721fb62ca08416bf9d040",
    "schemas/observation_source_v0.schema.json": "fcb2439c9a63e4a3b697aec68e573c1eb8af2900",
    "schemas/source_encounter_v0.schema.json": "e5ccfbc7af6059de28d9429cee2e14c4d1f54b0d",
    "tests/runtime/test_primary_ecology_v0.py": "edfcdb41a969b36e3bd8c26ef8d60992e26b1a07",
    "tools/primary_ecology_v0.py": "713de70882caa3aefc5ff3d2064a49c480c9a873",
}

INTEGRATION_ONLY_PATHS = {
    ".github/workflows/primary-ecology-integration-001.yml",
    "docs/integration/PRIMARY_ECOLOGY_GRAMMAR_001_INTEGRATION_001.md",
    "tests/runtime/test_primary_ecology_integration_v0.py",
}

LANE_IMPLEMENTATION_PATHS = (
    "tools/two_lane_coordination_v0.py",
    "tools/two_lane_coordination_v1.py",
    "tools/lane_b_successor_engagement_v0.py",
    "tools/lane_b_successor_engagement_repressure_v1.py",
    "tools/lane_lifecycle_disposition_v0.py",
    "tools/lane_lifecycle_disposition_oracle_v0.py",
    "tools/run_lane_lifecycle_disposition_pressure_v0.py",
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class PrimaryEcologyIntegrationTests(unittest.TestCase):
    def test_integration_branch_descends_from_exact_target_base(self):
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", TARGET_BASE, "HEAD"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def test_integration_diff_is_exactly_transplant_plus_pressure_harness(self):
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{TARGET_BASE}..HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        observed = {line for line in result.stdout.splitlines() if line}
        expected = set(SOURCE_BLOBS) | INTEGRATION_ONLY_PATHS
        self.assertEqual(observed, expected)

    def test_Y1_ecology_and_lane_bindings_coexist_without_type_conflation(self):
        ecology = json.loads(
            (ROOT / "schemas/ecology_engagement_binding_v0.schema.json").read_text(
                encoding="utf-8"
            )
        )
        lane = json.loads(
            (ROOT / "schemas/lane_engagement_binding_v0.schema.json").read_text(
                encoding="utf-8"
            )
        )
        ecology_type = ecology["properties"]["schema"]["const"]
        lane_type = lane["properties"]["schema"]["const"]
        self.assertEqual(ecology_type, "ecology_engagement_binding_v0")
        self.assertEqual(lane_type, "LANE_ENGAGEMENT_BINDING_v0")
        self.assertNotEqual(ecology_type, lane_type)
        self.assertNotEqual(ecology["$id"], lane["$id"])

        ecology_tool = (ROOT / "tools/primary_ecology_v0.py").read_text(encoding="utf-8")
        self.assertNotIn("LANE_ENGAGEMENT_BINDING_v0", ecology_tool)
        self.assertNotIn("lane_engagement_binding_v0", ecology_tool)

    def test_Y2_ecology_role_metadata_does_not_govern_lane_runtime(self):
        forbidden = (
            "primary_ecology_v0",
            "ecology_engagement_binding_v0",
            "ecology_role_v0",
        )
        for rel in LANE_IMPLEMENTATION_PATHS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, msg=f"{token} leaked into {rel}")

    def test_Y3_current_main_machinery_does_not_give_ecology_new_effects(self):
        bundle = clean_bundle()

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"authority_effect", "execution_effect"}:
                        self.assertEqual(child, "NONE")
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(bundle)
        self.assertEqual(bundle["binding"]["authority_refs"], [])
        self.assertEqual(
            authority_standing(bundle["binding"]),
            "NO_AUTHORITY_REF_REPRESENTED",
        )

        result = run_pressure()
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")
        self.assertEqual(result["integration_effect"], "NONE")
        self.assertEqual(result["occupant_binding_effect"], "NONE")
        self.assertEqual(result["work_claim_effect"], "NONE")
        self.assertFalse(result["durable_ecology_installed"])

    def test_Y4_lane_b_historical_precondition_is_unchanged_from_target_main(self):
        current_manifest = ROOT / "coordination/lane_manifest.json"
        self.assertFalse(current_manifest.exists())

        target_probe = subprocess.run(
            [
                "git",
                "cat-file",
                "-e",
                f"{TARGET_BASE}:coordination/lane_manifest.json",
            ],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertNotEqual(target_probe.returncode, 0)

        unchanged_paths = (
            "tools/lane_b_successor_engagement_v0.py",
            "tools/lane_b_successor_engagement_repressure_v1.py",
            "tests/runtime/test_lane_b_successor_engagement_v0.py",
            "tests/runtime/test_lane_b_successor_engagement_repressure_v1.py",
            "schemas/lane_engagement_binding_v0.schema.json",
            "coordination/predecessor_fences/LANE_B_LEGACY_INSTANCE_001.json",
        )
        diff = subprocess.run(
            ["git", "diff", "--quiet", f"{TARGET_BASE}..HEAD", "--", *unchanged_paths],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(diff.returncode, 0)

    def test_Y5_all_18_transplanted_artifacts_are_exact_source_blobs(self):
        self.assertEqual(len(SOURCE_BLOBS), 18)
        for rel, expected_sha in SOURCE_BLOBS.items():
            path = ROOT / rel
            self.assertTrue(path.is_file(), msg=rel)
            self.assertEqual(git_blob_sha(path), expected_sha, msg=rel)


if __name__ == "__main__":
    unittest.main()
