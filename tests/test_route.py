import importlib.util
from pathlib import Path
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'skills/twin-fpv-film/scripts/check_route.py'

class Route(unittest.TestCase):
    def tool(self):
        self.assertTrue(TOOL.exists(), 'route checker missing')
        spec = importlib.util.spec_from_file_location('route', TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_clear_route(self):
        self.assertEqual(self.tool().check({'radius': .2, 'points': [[-2, 2, 0], [2, 2, 0]], 'boxes': [{'min': [-1, -1, -1], 'max': [1, 1, 1]}]}), [])

    def test_segment_crosses_even_with_clear_endpoints(self):
        self.assertTrue(self.tool().check({'radius': 0, 'points': [[-2, 0, 0], [2, 0, 0]], 'boxes': [{'min': [-1, -1, -1], 'max': [1, 1, 1]}]}))

    def test_radius_applied(self):
        self.assertTrue(self.tool().check({'radius': .3, 'points': [[-2, 1.2, 0], [2, 1.2, 0]], 'boxes': [{'min': [-1, -1, -1], 'max': [1, 1, 1]}]}))

    def test_nonfinite_points(self):
        self.assertTrue(self.tool().check({'points': [[0, 0, 0], [float('nan'), 0, 0]], 'boxes': []}))

if __name__ == '__main__': unittest.main()
