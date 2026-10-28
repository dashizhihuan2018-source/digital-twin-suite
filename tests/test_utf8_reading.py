"""Keep original skills UTF-8 and serve explicit-charset human reading pages."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class UTF8Reading(unittest.TestCase):
    def test_source_is_valid_utf8_and_not_mojibake(self):
        text = (ROOT / 'skills/digital-twin/SKILL.md').read_bytes().decode('utf-8', errors='strict')
        self.assertIn('# 数字孪生全链路', text)
        self.assertNotIn('\ufffd', text)
        self.assertTrue(text.startswith('---\nname: digital-twin'))

    def test_reading_pages_have_charset_and_preserve_original(self):
        spec = importlib.util.spec_from_file_location('utf8_build', ROOT / 'scripts/build.py')
        b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(b)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'dist'
            b.build(ROOT, out)
            target = out / 'skills/digital-twin/index.html'
            self.assertTrue(target.is_file(), 'UTF-8 HTML skill reading page is missing')
            text = target.read_bytes().decode('utf-8', errors='strict')
            self.assertIn('<meta charset="utf-8">', text)
            self.assertIn('<h1>数字孪生全链路</h1>', text)
            self.assertNotIn('<p>---', text)
            self.assertIn('href="../../styles.css"', text)
            self.assertIn('href="references/changfeng-final.html"', text)
            self.assertTrue((out / 'skills/digital-twin/references/changfeng-final.html').is_file())
            self.assertEqual((out / 'skills/digital-twin/SKILL.md').read_bytes(), (ROOT / 'skills/digital-twin/SKILL.md').read_bytes())
            self.assertIn('skills/digital-twin/index.html', (out / 'index.html').read_text())

if __name__ == '__main__':
    unittest.main()
