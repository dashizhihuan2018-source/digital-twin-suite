"""A portfolio-style real-site preview must remain an accessible product link."""
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FINAL = 'https://szls-changfeng.maip.top/EMS-changfeng/?twin=1#/page/ems-overview'

class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.items = []
        self.stack = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        item = {'tag': tag, 'attrs': dict(attrs), 'parents': list(self.stack)}
        self.items.append(item)
        if tag not in ('img', 'source', 'meta', 'link', 'br', 'input'):
            self.stack.append(item)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i]['tag'] == tag:
                self.stack = self.stack[:i]
                break

class CasePreview(unittest.TestCase):
    def test_linked_preview_between_case_and_skills(self):
        html = (ROOT / 'site/index.html').read_text()
        elements = Elements(html).items
        video = next((x for x in elements if x['attrs'].get('id') == 'case-preview'), None)
        self.assertIsNotNone(video, 'the final-site preview is missing')
        attrs = video['attrs']
        for key in ('muted', 'loop', 'playsinline', 'data-human-only'):
            self.assertIn(key, attrs)
        self.assertNotIn('controls', attrs)
        self.assertTrue(attrs.get('poster', '').endswith('.jpg'))
        link = next(x for x in reversed(video['parents']) if x['tag'] == 'a')
        self.assertEqual(link['attrs']['href'], FINAL)
        self.assertEqual(link['attrs']['target'], '_blank')
        self.assertTrue({'noopener', 'noreferrer'} <= set(link['attrs']['rel'].split()))
        self.assertIn('新窗口', link['attrs']['aria-label'])
        self.assertLess(html.index('id="case"'), html.index('id="case-preview"'))
        self.assertLess(html.index('id="case-preview"'), html.index('id="skills"'))
        pause = next(x for x in elements if x['attrs'].get('id') == 'case-preview-toggle')
        self.assertEqual(pause['tag'], 'button')
        self.assertFalse(any(x['tag'] == 'a' for x in pause['parents']))
        self.assertEqual(pause['attrs']['aria-controls'], 'case-preview')

    def test_preview_is_recorded_from_current_final_and_has_no_voice(self):
        selected = json.loads((ROOT / 'docs/final-artifacts.json').read_text())
        preview = selected['public_media'].get('website_preview')
        self.assertIsNotNone(preview, 'fresh final-website recording must be selected')
        self.assertEqual(preview['recorded_website_version'], selected['website']['version'])
        self.assertEqual(preview['source_url'], FINAL)
        self.assertEqual(preview['dimensions'], [1280, 720])
        self.assertFalse(preview['audio'])
        self.assertEqual(preview['frames'], 1080)
        self.assertFalse(preview['source_assets_distribution'])

if __name__ == '__main__':
    unittest.main()
