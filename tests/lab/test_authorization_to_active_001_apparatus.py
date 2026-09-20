import inspect, json, tempfile, unittest
from copy import deepcopy
from pathlib import Path
from lab.ops.candidates.authorization_to_active_001.correspondence import AuthorizationShapeError, corresponds
from lab.ops.candidates.authorization_to_active_001.materializer import AuthorizationMaterializationError, materialize_active_if_corresponding
from lab.ops.candidates.execution_stop_latch_001.stop_latch import ACTIVE, ExecutionStopLatch

class T(unittest.TestCase):
    def setUp(self):
        self.e={"execution_envelope_id":"DUMMY-E","implementation_basis":"dummy-basis","requested_consequence":"DUMMY-C"}
        self.ao={"execution_envelope_id":"DUMMY-E","implementation_basis":"dummy-basis","allowed_consequences":["DUMMY-C"],"status":"LIVE"}

    def test_dummy_correspondence(self):
        self.assertTrue(corresponds(self.ao,self.e)); self.assertFalse(corresponds(None,self.e))
        for k,v in [("execution_envelope_id","OTHER"),("implementation_basis","OTHER"),("allowed_consequences",["OTHER"]),("status","TERMINATED")]:
            x=deepcopy(self.ao); x[k]=v; self.assertFalse(corresponds(x,self.e))
        x=deepcopy(self.ao); x["valid"]=True
        with self.assertRaises(AuthorizationShapeError): corresponds(x,self.e)

    def test_dummy_materialization_and_clean_state(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); a=p/"a"; b=p/"b"
            self.assertIsNotNone(materialize_active_if_corresponding(a,self.e,self.ao))
            self.assertEqual(ExecutionStopLatch(a,"DUMMY-E").state(),ACTIVE)
            self.assertIsNone(materialize_active_if_corresponding(b,self.e,None))
            self.assertFalse(ExecutionStopLatch(b,"DUMMY-E").state_path.exists())
            with self.assertRaises(AuthorizationMaterializationError): materialize_active_if_corresponding(a,self.e,None)

    def test_no_condition_label_input(self):
        self.assertEqual(tuple(inspect.signature(corresponds).parameters),("authorization","envelope"))
        self.assertEqual(tuple(inspect.signature(materialize_active_if_corresponding).parameters),("store_root","envelope","authorization"))

    def test_frozen_fixtures_static_only(self):
        f=Path(__file__).parents[2]/"lab"/"ops"/"candidates"/"authorization_to_active_001"/"fixtures"
        load=lambda n: json.loads((f/n).read_text())
        e,a,b1,b2,b3,b4=[load(n) for n in ["execution_envelope.json","authorization_A.json","authorization_B1.json","authorization_B2.json","authorization_B3.json","authorization_B4.json"]]
        self.assertEqual(set(e),{"execution_envelope_id","implementation_basis","requested_consequence"})
        diff=lambda x,y:{k for k in x if x[k]!=y[k]}
        self.assertEqual(diff(a,b1),{"execution_envelope_id"}); self.assertEqual(diff(a,b2),{"implementation_basis"})
        self.assertEqual(diff(a,b3),{"allowed_consequences"}); self.assertEqual(diff(a,b4),{"status"})
        self.assertFalse((f/"authorization_B0.json").exists())
