import importlib.util
from pathlib import Path
import unittest
TOOL=Path(__file__).resolve().parents[1]/'skills/twin-product-film/scripts/check_timeline.py'
class Timing(unittest.TestCase):
    def load(self):
        self.assertTrue(TOOL.exists(),'timeline checker missing')
        spec=importlib.util.spec_from_file_location('timeline',TOOL)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    def test_correct_anchors(self):
        self.assertEqual(self.load().check({'fps':30,'frames':1075,'shots':[{'id':'solar','start':705,'end':851}],'anchors':[{'wordSeconds':24.52,'fullyVisibleFrame':735}]}),[])
    def test_late_visibility_rejected(self):
        self.assertTrue(self.load().check({'fps':30,'frames':1075,'shots':[],'anchors':[{'wordSeconds':24.52,'fullyVisibleFrame':754}]}))
    def test_bounds_and_ids(self):
        errors=self.load().check({'fps':30,'frames':100,'shots':[{'id':'a','start':0,'end':101},{'id':'a','start':8,'end':8}]})
        self.assertGreaterEqual(len(errors),3)
    def test_invalid_clock(self):
        self.assertTrue(self.load().check({'fps':0,'frames':100,'shots':[]}))
if __name__=='__main__':unittest.main()
