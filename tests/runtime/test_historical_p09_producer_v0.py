import unittest
from tools.historical_p09_producer_v0 import load_json, qualify

FIXTURES="docs/candidates/historical_p09_producer_v0/fixtures/RAW_FIXTURES_v0.json"
KEY="docs/candidates/historical_p09_producer_v0/fixtures/EVALUATION_KEY_v0.json"

class HistoricalP09ProducerTests(unittest.TestCase):
    def test_frozen_cells(self):
        observed=qualify(load_json(FIXTURES))
        key=load_json(KEY)["cells"]
        self.assertEqual(set(observed),set(key))
        for cell_id, expected in key.items():
            self.assertEqual(observed[cell_id]["status"],expected["status"])
            self.assertEqual(observed[cell_id]["standing"],expected["standing"])

    def test_witness_membrane(self):
        observed=qualify(load_json(FIXTURES))
        for value in observed.values():
            self.assertEqual(value["relation_type"],"ACTIVE_OWNERSHIP_EFFECT_STATUS")
            self.assertTrue(value["basis_ref"])
            self.assertTrue(value["producer"])
            self.assertTrue(value["version"])

    def test_scope_closure_and_temporal_cells(self):
        observed=qualify(load_json(FIXTURES))
        self.assertEqual(observed["F"]["status"],"ADMINISTRATION_INVALID")
        self.assertEqual(observed["G"]["standing"],"UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP")
        self.assertEqual(observed["H"]["standing"],"UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP")

if __name__=="__main__":
    unittest.main()
