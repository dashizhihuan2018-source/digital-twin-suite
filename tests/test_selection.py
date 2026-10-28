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
        self.assertEqual(set(media), {'poster', 'fpv'})
        self.assertEqual(media['poster']['sha256'], '00d53424b723d1b699b7cf041b964b0f356f28eae8d311b39dba2bf67bcfccc6')
        self.assertEqual(media['fpv']['sha256'], '9dac1ef965277857d1496a6af21bae1d24e487268c0f9c2430cedaa351946f9c')
        for artifact in media.values():
            self.assertIn('/f1e49e3cb38ac001433db2244c905d77f5598881/media/changfeng/', artifact['url'])
            self.assertEqual(artifact['ai_pixel_review'], 'forbidden')
            self.assertEqual(artifact['formal_human_acceptance'], 'pending')
            self.assertEqual(artifact['permission'], 'noncommercial_public_display')
            self.assertNotEqual(artifact['recorded_website_version'], 'V1.4.12')

    def test_private_product_film_is_not_a_public_url(self):
        film = self.data['private_product_film']
        self.assertEqual(film['version'], 'V3.5.5')
        self.assertFalse(film['public_distribution'])
        self.assertNotIn('url', film)
        self.assertNotIn('/Users/', json.dumps(self.data))

if __name__ == '__main__':
    unittest.main()
