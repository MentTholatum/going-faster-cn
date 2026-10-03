"""Validate the reader using only the files included in the repository."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import base64
import hashlib
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
release = '--release' in sys.argv
errors = []
chapters = json.loads((ROOT / 'content/book.json').read_text())['chapters']
assets = json.loads((ROOT / 'content/figures.json').read_text())
fonts = json.loads((ROOT / 'assets/reader-fonts/manifest.json').read_text())
expected_counts = {1:25,2:14,3:22,4:10,5:17,6:18,7:41,8:13,9:15,10:8,11:11,12:8,13:5,14:17,15:22,16:1}
pages = [p for c in chapters for p in c['pages']]
figures = [f for p in pages for f in p['figures']]
page_ids = [p['pdf'] for p in pages]
figure_ids = [f[0] for f in figures]
if len(page_ids) != len(set(page_ids)):
    errors.append('Duplicate content page IDs')
if not set(range(21, 275)) <= set(page_ids):
    errors.append('Missing chapter pages')
if len(figure_ids) != len(set(figure_ids)) or set(figure_ids) != set(assets):
    errors.append('Figure IDs differ between book and asset manifest')
if {c['chapter'] for c in chapters} != set(range(21)):
    errors.append('Missing or unexpected reading sections')
for chapter, count in expected_counts.items():
    actual = {i for i in figure_ids if i.startswith(f'{chapter}-')}
    if actual != {f'{chapter}-{i}' for i in range(1, count + 1)}:
        errors.append(f'Figure numbering differs in chapter {chapter}')
for entry in [*assets.values(), *fonts['files']]:
    path = ROOT / entry['path']
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        errors.append('Asset checksum mismatch: ' + entry['path'])

class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.images = [], [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a' and a.get('href', '').startswith('#'):
            self.links.append(a['href'][1:])
        if tag == 'img':
            self.images.append(a)

htmlpath = ROOT / ('index.html' if release else 'book-preview.html')
source = htmlpath.read_text()
r = Reader()
r.feed(source)
if any(count > 1 for count in Counter(r.ids).values()):
    errors.append('Duplicate HTML IDs')
if set(r.links) - set(r.ids):
    errors.append('Broken local anchors')
if len(r.images) != len(figures):
    errors.append('Rendered figure count differs')
by_path = {a['path']: a for a in assets.values()}
for image in r.images:
    entry = by_path.get(image.get('src'))
    if not entry:
        errors.append('Unexpected image path: ' + image.get('src', ''))
    elif any(image.get(k) != str(entry[k]) for k in ('width', 'height')):
        errors.append('Image dimensions differ: ' + entry['path'])
font_paths = [f['path'] for f in fonts['files'] if f['path'].endswith('.woff2')]
for path in font_paths:
    if "url('" + path + "')" not in source:
        errors.append('Missing font reference: ' + path)
license_text = html.escape((ROOT / 'assets/reader-fonts/MiSans-LICENSE.txt').read_text())
if license_text not in source:
    errors.append('Missing font license')
for marker in ('已确认彩图', '原图确认', '原书插图', '新增解读', '新增阅读演示', '用户提供', '工作译稿', '/Users/', 'color-review-', 'work/'):
    if marker in source:
        errors.append('Internal production text in reader: ' + marker)

if release:
    portable_path = ROOT / 'Going-Faster-全书中文阅读版.html'
    if not portable_path.is_file():
        errors.append('Missing portable edition; run python3 scripts/build.py')
    else:
        portable = portable_path.read_text()
        p = Reader()
        p.feed(portable)
        if p.ids != r.ids or p.links != r.links or len(p.images) != len(r.images):
            errors.append('Portable structure differs')
        for embedded, original in zip(p.images, r.images):
            value = embedded.get('src', '')
            if not value.startswith('data:image/') or ';base64,' not in value:
                errors.append('Portable image is not embedded')
            elif base64.b64decode(value.split(',', 1)[1]) != (ROOT / original['src']).read_bytes():
                errors.append('Portable image bytes differ: ' + original['src'])
        embedded_fonts = re.findall(r"url\('data:font/woff2;base64,([^']+)'\)", portable)
        if len(embedded_fonts) != len(font_paths):
            errors.append('Portable font count differs')
        for embedded, path in zip(embedded_fonts, font_paths):
            if base64.b64decode(embedded) != (ROOT / path).read_bytes():
                errors.append('Portable font bytes differ: ' + path)
        if license_text not in portable:
            errors.append('Portable font license missing')
        if any(not u.startswith(('data:', '#')) for u in re.findall(r"url\(['\"]?(.*?)['\"]?\)", portable)):
            errors.append('Portable CSS has external dependencies')

report = {'status':'failed' if errors else 'passed', 'reading_sections':len(chapters), 'content_pages':len(pages), 'content_blocks':sum(len(p['blocks']) for p in pages), 'figures':len(figures), 'font_files':len(font_paths), 'errors':errors}
(ROOT / 'output').mkdir(exist_ok=True)
(ROOT / 'output/validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(bool(errors))
