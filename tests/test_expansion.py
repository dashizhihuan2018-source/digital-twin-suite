"""Nine portable skills and the single combined launch website entry."""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
NEW = {'poster-production', 'pdfmaster-moments-poster', 'video-cover-poster', 'product-launch-website'}

class Expansion(unittest.TestCase):
    def test_install_catalog_and_public_cards_agree(self):
        spec = importlib.util.spec_from_file_location('install_expansion', ROOT / 'scripts/install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(NEW <= set(module.NAMES), 'four additional independent skills missing')
        self.assertEqual(len(module.NAMES), 9)
        html = (ROOT / 'site/index.html').read_text()
        for name in module.NAMES:
            self.assertTrue((ROOT / 'skills' / name / 'SKILL.md').is_file())
            self.assertIn('skills/' + name + '/index.html', html)
        self.assertNotIn('product-launch-ui', module.NAMES)

    def test_skill_relative_references_resolve(self):
        for source in (ROOT / 'skills').rglob('*.md'):
            for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', source.read_text()):
                if '://' not in link and not link.startswith('#'):
                    self.assertTrue((source.parent / link.split('#')[0]).is_file(), f'{source.name}: {link}')

if __name__ == '__main__':
    unittest.main()
