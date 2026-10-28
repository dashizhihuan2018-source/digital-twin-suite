import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class Installer(unittest.TestCase):
    def test_preview_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'skills'
            self.assertEqual(len(installer.install(ROOT, dest)), 5)
            self.assertFalse(dest.exists())

    def test_install_and_preserve_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            installer.install(ROOT, dest, True)
            self.assertEqual(len(list(dest.glob('*/SKILL.md'))), 5)
            before = (dest / 'digital-twin/SKILL.md').read_bytes()
            with self.assertRaises(FileExistsError): installer.install(ROOT, dest, True)
            self.assertEqual(before, (dest / 'digital-twin/SKILL.md').read_bytes())

    def test_failed_copy_leaves_no_partial_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            def fail(source, target, **kwargs):
                target.mkdir(exist_ok=True)
                raise OSError('simulated full disk')
            with patch.object(installer.shutil, 'copytree', side_effect=fail):
                with self.assertRaises(OSError): installer.install(ROOT, dest, True)
            self.assertEqual(list(dest.iterdir()), [])

if __name__ == '__main__': unittest.main()
