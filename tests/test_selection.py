"""Release selection regression: published artifacts are not formal acceptance."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Selection(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'docs/final-artifacts.json').read_text())

    def test_final_website_is_canonical_not_synthetic(self):
        web = self.data['website']
        self.assertEqual(web['version'], 'V1.4.12')
        self.assertEqual(web['url'], 'https://szls-changfeng.maip.top/EMS-changfeng/?twin=1#/page/ems-overview')
        self.assertFalse(self.data['redistribute_source_models'])

    def test_only_latest_published_media_allowlisted(self):
        media = self.data['public_media']
        self.assertEqual(set(media), {'poster', 'fpv', 'product_film'})
        self.assertEqual(media['poster']['sha256'], '00d53424b723d1b699b7cf041b964b0f356f28eae8d311b39dba2bf67bcfccc6')
        self.assertEqual(media['fpv']['sha256'], '9dac1ef965277857d1496a6af21bae1d24e487268c0f9c2430cedaa351946f9c')
        for key in ('poster', 'fpv'):
            artifact = media[key]
            self.assertIn('/f1e49e3cb38ac001433db2244c905d77f5598881/media/changfeng/', artifact['url'])
            self.assertEqual(artifact['ai_pixel_review'], 'forbidden')
            self.assertEqual(artifact['formal_human_acceptance'], 'pending')
            self.assertEqual(artifact['permission'], 'noncommercial_public_display')
            self.assertNotEqual(artifact['recorded_website_version'], 'V1.4.12')

    def test_authorized_exact_product_film_is_public_not_its_sources(self):
        film = self.data['public_media']['product_film']
        self.assertEqual(film['version'], 'V3.5.5')
        self.assertTrue(film['public_distribution'])
        self.assertEqual(film['bytes'], 102288446)
        self.assertEqual(film['sha256'], 'f21473bafde5710bafb4eb1ae69b043218d7adc03937ce8f4b75c0833825b83b')
        self.assertEqual(film['dimensions'], [3840, 2160])
        self.assertIn('/releases/download/changfeng-film-v3.5.5/', film['url'])
        self.assertEqual(film['ai_pixel_review'], 'forbidden')
        self.assertNotIn('private_product_film', self.data)
        self.assertNotIn('/Users/', json.dumps(self.data))

    def test_pages_workflow_builds_verified_large_media_outside_git(self):
        workflow = (ROOT / '.github/workflows/pages.yml').read_text()
        self.assertIn('actions/deploy-pages@v4', workflow)
        self.assertIn('scripts/fetch_public_media.py', workflow)
        self.assertIn('python3 -B scripts/build.py', workflow)
        self.assertIn('digital-twin-suite/', (ROOT / 'README.md').read_text())
        self.assertNotIn('chatgpt.site', (ROOT / 'README.md').read_text())

if __name__ == '__main__':
    unittest.main()
