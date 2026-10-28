"""Public packaging must reject unselected inputs before changing output."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'scripts/build.py'

class PublicBuild(unittest.TestCase):
    def load(self):
        self.assertTrue(BUILDER.is_file(), 'strict final-artifact builder is missing')
        spec = importlib.util.spec_from_file_location('public_build', BUILDER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_build_and_reproducible_installable_zip(self):
        b = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'dist'
            b.build(ROOT, output)
            archive = output / 'assets/digital-twin-skills.zip'
            before = archive.read_bytes()
            manifest = json.loads((output / 'build-manifest.json').read_text())
            for item in manifest['files']:
                raw = (output / item['path']).read_bytes()
                self.assertEqual(len(raw), item['bytes'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), item['sha256'])
            with zipfile.ZipFile(archive) as z:
                self.assertFalse(any(p.endswith(('.mp4', '.png', '.jpg', '.glb')) for p in z.namelist()))
                self.assertEqual(len([p for p in z.namelist() if p.endswith('/SKILL.md')]), 9)
                z.extractall(Path(tmp) / 'unpack')
            unpacked = Path(tmp) / 'unpack/digital-twin-suite'
            result = subprocess.run(['python3', '-B', str(unpacked / 'scripts/install.py'), '--dest', str(Path(tmp) / 'installed'), '--apply'], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertEqual(len(list((Path(tmp) / 'installed').glob('*/SKILL.md'))), 9)
            b.build(ROOT, output)
            self.assertEqual(before, archive.read_bytes())

    def test_reject_unapproved_docs_and_preserve_existing_output(self):
        b = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'source'
            root.mkdir()
            for folder in ('site', 'docs', 'skills', 'scripts'):
                shutil.copytree(ROOT / folder, root / folder)
            for name in ('README.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md'):
                shutil.copyfile(ROOT / name, root / name)
            out = Path(tmp) / 'out'
            out.mkdir()
            (out / 'sentinel').write_text('preserve')
            (root / 'docs/private-notes.md').write_text('must never be copied')
            with self.assertRaisesRegex(ValueError, 'allowlist'):
                b.build(root, out)
            self.assertEqual((out / 'sentinel').read_text(), 'preserve')
            (root / 'docs/private-notes.md').unlink()
            (root / 'site/leaked').symlink_to(root / 'docs', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                b.build(root, out)
            self.assertEqual((out / 'sentinel').read_text(), 'preserve')

    def test_markdown_tutorial_keeps_code_and_local_links(self):
        b = self.load()
        html = b.render_markdown('# 教程\n\n[声音](voice-reference.md)\n\n```bash\necho "<safe>"\n```\n')
        self.assertIn('href="voice-reference.html"', html)
        self.assertIn('&lt;safe&gt;', html)
        self.assertIn('<pre>', html)
        self.assertNotIn('<script', b.render_markdown('[x](javascript:alert)\n<script>'))

    def test_media_integrity_is_not_only_a_filename_check(self):
        b = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'same-name.mp4'
            path.write_bytes(b'wrong media')
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                b.verify_media(path, 11, '0' * 64)

if __name__ == '__main__':
    unittest.main()
