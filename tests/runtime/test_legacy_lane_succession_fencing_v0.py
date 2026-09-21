import copy
import json
import unittest

from tools.legacy_lane_succession_fencing_v0 import load_json, qualify

FIXTURES = "docs/candidates/legacy_lane_succession_fencing_v0/fixtures/RAW_FIXTURES_v0.json"
KEY = "docs/candidates/legacy_lane_succession_fencing_v0/fixtures/EVALUATION_KEY_v0.json"

class LegacyLaneSuccessionFencingTests(unittest.TestCase):
    def test_frozen_cells(self):
        result = qualify(load_json(FIXTURES))
        key = load_json(KEY)["cells"]
        self.assertEqual(set(result["cells"]), set(key))
        for cell_id, expected in key.items():
            observed = result["cells"][cell_id]
            for field, value in expected.items():
                self.assertEqual(observed[field], value, f"{cell_id}:{field}")

    def test_zombie_pair_is_fence_only_intervention(self):
        fixtures = load_json(FIXTURES)
        j = copy.deepcopy(fixtures["cells"]["J"])
        twin = copy.deepcopy(fixtures["cells"]["J_NO_FENCE"])
        self.assertEqual(j["attempt"], twin["attempt"])
        self.assertEqual(j["observed_predecessor_head"], twin["observed_predecessor_head"])
        self.assertEqual(j["prose_retired"], twin["prose_retired"])
        self.assertEqual(j["fence_registry"], ["VALID"])
        self.assertEqual(twin["fence_registry"], [])

        observed = qualify(fixtures)["cells"]
        self.assertFalse(observed["J"]["predecessor_currently_operative"])
        self.assertEqual(observed["J"]["coordination_posture"], "NO_COORDINATION_BLOCK")
        self.assertTrue(observed["J"]["semantic_overlap"])
        self.assertTrue(observed["J"]["provenance_overlap"])

        self.assertTrue(observed["J_NO_FENCE"]["predecessor_currently_operative"])
        self.assertEqual(observed["J_NO_FENCE"]["coordination_posture"], "COORDINATION_HOLD")
        self.assertTrue(observed["J_NO_FENCE"]["semantic_overlap"])
        self.assertTrue(observed["J_NO_FENCE"]["provenance_overlap"])

    def test_non_effects(self):
        result = qualify(load_json(FIXTURES))
        self.assertEqual(result["live_lane_mutation"], "NONE")
        self.assertEqual(result["predecessor_disposition"], "UNCHANGED")
        self.assertEqual(result["successor_activation"], "NONE")
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["merge"], "NONE")
        self.assertEqual(result["stop"], "YES")

if __name__ == "__main__":
    unittest.main()
