import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'skills/twin-model-lightweight/scripts/audit_glb.py'

class GLBAudit(unittest.TestCase):
    def load(self):
        self.assertTrue(TOOL.exists(), 'GLB auditor not implemented')
        spec = importlib.util.spec_from_file_location('audit', TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def fixture(self, data, bad_length=False):
        encoded = json.dumps(data).encode()
        encoded += b' ' * (-len(encoded) % 4)
        n = 20 + len(encoded)
        return struct.pack('<III', 0x46546C67, 2, n + int(bad_length)) + struct.pack('<II', len(encoded), 0x4E4F534A) + encoded

    def test_counts_and_semantics(self):
        m = self.load()
        data = {'asset': {'version':'2.0'}, 'nodes':[{'name':'A','extras':{'stableId':'one'},'translation':[1,2,3]}], 'meshes':[{'primitives':[{'attributes':{'POSITION':0},'indices':1}]}], 'accessors':[{'count':9},{'count':6}], 'materials':[{}]}
        r = m.audit(self.fixture(data))
        self.assertEqual(r['triangles'], 2)
        self.assertEqual(r['nodes'],1)
        self.assertEqual(r['semanticNodes'][0]['extras']['stableId'], 'one')
        self.assertEqual(r['semanticNodes'][0]['translation'], [1,2,3])
        self.assertFalse(r['decodedGeometryVerified'])

    def test_bad_length_rejected(self):
        with self.assertRaises(ValueError): self.load().audit(self.fixture({'asset':{'version':'2.0'}},True))

    def test_bad_magic_rejected(self):
        with self.assertRaises(ValueError): self.load().audit(b'not a glb')

    def test_non_triangle_modes_not_miscounted(self):
        r=self.load().audit(self.fixture({'asset':{'version':'2.0'},'meshes':[{'primitives':[{'mode':1,'attributes':{'POSITION':0}}]}],'accessors':[{'count':12}]}))
        self.assertEqual(r['triangles'],0)
        self.assertEqual(r['otherPrimitiveModes'],[1])

    def test_node_index_retained(self):
        result=self.load().audit(self.fixture({'asset':{'version':'2.0'},'nodes':[{}, {'name':'A'}]}))
        self.assertEqual(result['semanticNodes'][1]['nodeIndex'],1)

    def test_bad_accessor_rejected(self):
        for index in (-1, 7):
            with self.assertRaises(ValueError):
                self.load().audit(self.fixture({'asset':{'version':'2.0'},'meshes':[{'primitives':[{'indices':index}]}],'accessors':[{'count':3}]}))

if __name__ == '__main__': unittest.main()
