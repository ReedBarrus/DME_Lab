import unittest
from tools.historical_p11_producer_v0 import load_json, qualify

FIXTURES="docs/candidates/historical_p11_producer_v0/fixtures/RAW_FIXTURES_v0.json"
KEY="docs/candidates/historical_p11_producer_v0/fixtures/EVALUATION_KEY_v0.json"

class HistoricalP11ProducerTests(unittest.TestCase):
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
            self.assertEqual(value["relation_type"],"REFERENCE_RETENTION_STATUS")
            self.assertTrue(value["basis_ref"])
            self.assertTrue(value["producer"])
            self.assertTrue(value["version"])

    def test_exact_p10_set_binding(self):
        observed=qualify(load_json(FIXTURES))
        for cell_id in ("F","G","H"):
            self.assertEqual(observed[cell_id]["status"],"ADMINISTRATION_INVALID")
            self.assertIsNone(observed[cell_id]["standing"])
        self.assertEqual(observed["I"]["standing"],"RETAINABLE")

if __name__=="__main__":
    unittest.main()
