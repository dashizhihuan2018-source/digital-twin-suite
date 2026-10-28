"""Build an allowlisted static showcase and deterministic skill ZIP (standard library)."""
import argparse
import hashlib
import html
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile

ROOT_FILES = ('README.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md')
DOCS = ('changfeng-case.md', 'final-selection.md', 'final-artifacts.json',
        'local-models.md', 'voice-reference.md', 'validation.md')
SKILLS = (
    'digital-twin/SKILL.md', 'digital-twin/agents/openai.yaml',
    'digital-twin/references/changfeng-final.md',
    'twin-model-lightweight/SKILL.md', 'twin-model-lightweight/agents/openai.yaml',
    'twin-model-lightweight/scripts/audit_glb.py',
    'twin-product-film/SKILL.md', 'twin-product-film/agents/openai.yaml',
    'twin-product-film/scripts/check_timeline.py',
    'twin-fpv-film/SKILL.md', 'twin-fpv-film/agents/openai.yaml',
    'twin-fpv-film/scripts/check_route.py',
    'twin-effects/SKILL.md', 'twin-effects/agents/openai.yaml',
)
SITE = ('index.html', 'styles.css', 'fonts.css', 'app.js', 'favicon.svg',
        'assets/changfeng-poster-v1.3.0.png', 'assets/changfeng-r5-demo.mp4',
        'assets/fonts/SourceHanSerifCN-Bold.otf', 'assets/fonts/OFL-1.1.txt')
MEDIA = {
    'poster': ('assets/changfeng-poster-v1.3.0.png', 2207694, '00d53424b723d1b699b7cf041b964b0f356f28eae8d311b39dba2bf67bcfccc6'),
    'fpv': ('assets/changfeng-r5-demo.mp4', 6818112, '9dac1ef965277857d1496a6af21bae1d24e487268c0f9c2430cedaa351946f9c'),
}

def exact_tree(base, allowed):
    if base.is_symlink() or not base.is_dir():
        raise ValueError(f'symlink or missing public directory: {base.name}')
    actual = set()
    permitted_dirs = {p.as_posix() for name in allowed for p in Path(name).parents if p.as_posix() != '.'}
    for path in base.rglob('*'):
        rel = path.relative_to(base).as_posix()
        if path.is_symlink():
            raise ValueError(f'symlink forbidden: {base.name}/{rel}')
        if path.is_dir():
            if rel not in permitted_dirs:
                raise ValueError(f'allowlist rejects directory: {base.name}/{rel}')
        elif path.is_file():
            actual.add(rel)
        else:
            raise ValueError(f'non-regular public input: {rel}')
    if actual != set(allowed):
        raise ValueError(f'allowlist mismatch in {base.name}: missing={sorted(set(allowed)-actual)}, extra={sorted(actual-set(allowed))}')

def verify_media(path, size, sha):
    raw = path.read_bytes()
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError(f'SHA256/size mismatch: {path.name}')

def inline(text):
    tokens = []
    def stash(value):
        tokens.append(value)
        return f'\x00{len(tokens)-1}\x00'
    text = re.sub(r'\x60([^\x60]+)\x60', lambda m: stash('<code>' + html.escape(m[1]) + '</code>'), text)
    def link(m):
        dest = m[2]
        if re.match(r'^(?:https?://|mailto:|#)', dest):
            pass
        elif ':' in dest or dest.startswith('//'):
            return html.escape(m[1])
        else:
            if not dest.split('#')[0].endswith('SKILL.md'):
                dest = re.sub(r'\.md(?=#|$)', '.html', dest)
        return stash(f'<a href="{html.escape(dest, quote=True)}">{html.escape(m[1])}</a>')
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, text)
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: tokens[int(m[1])], text)

def render_markdown(markdown):
    lines = markdown.splitlines()
    result, paragraph = [], []
    list_type = None
    def flush():
        nonlocal list_type
        if paragraph:
            result.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()
        if list_type:
            result.append(f'</{list_type}>')
            list_type = None
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(chr(96)*3):
            flush()
            index += 1
            code = []
            while index < len(lines) and not lines[index].startswith(chr(96)*3):
                code.append(lines[index])
                index += 1
            result.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
        elif not line.strip():
            flush()
        elif re.match(r'^#{1,6} ', line):
            flush()
            heading, text = line.split(' ', 1)
            result.append(f'<h{len(heading)}>' + inline(text) + f'</h{len(heading)}>')
        elif line.startswith('|') and index + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[index+1]):
            flush()
            def row(text, tag):
                return '<tr>' + ''.join(f'<{tag}>' + inline(c.strip()) + f'</{tag}>' for c in text.strip().strip('|').split('|')) + '</tr>'
            result.append('<table><thead>' + row(line, 'th') + '</thead><tbody>')
            index += 2
            while index < len(lines) and lines[index].startswith('|'):
                result.append(row(lines[index], 'td'))
                index += 1
            result.append('</tbody></table>')
            index -= 1
        elif re.match(r'^(?:[-*]|\d+\.) ', line):
            match = re.match(r'^([-*]|\d+\.) (.*)', line)
            wanted = 'ol' if match[1][0].isdigit() else 'ul'
            if paragraph or list_type != wanted:
                flush()
                result.append(f'<{wanted}>')
                list_type = wanted
            result.append('<li>' + inline(match[2]) + '</li>')
        elif line.startswith('> '):
            flush()
            result.append('<blockquote><p>' + inline(line[2:]) + '</p></blockquote>')
        else:
            if list_type:
                flush()
            paragraph.append(line.strip())
        index += 1
    flush()
    return '\n'.join(result)

def document_page(text, name):
    title = next((x[2:] for x in text.splitlines() if x.startswith('# ')), name)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}｜数字孪生 Skill</title><link rel="icon" href="../favicon.svg"><link rel="stylesheet" href="../styles.css"><link rel="stylesheet" href="../fonts.css"></head><body><header class="site-header doc-header"><a class="brand" href="../index.html">数字孪生 Skill<small>从模型到交付</small></a></header><main class="doc-shell"><nav class="doc-tools" aria-label="文档工具"><a href="../index.html">← 返回首页</a><a href="{html.escape(name)}">查看 Markdown 原文 ↓</a></nav><article class="doc-article">{render_markdown(text)}</article></main></body></html>'''

def archive_bytes(root):
    paths = list(ROOT_FILES) + ['scripts/install.py']
    paths += ['skills/' + path for path in SKILLS]
    paths += ['docs/' + path for path in DOCS]
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in sorted(paths):
            path = root / rel
            if path.is_symlink() or not path.is_file():
                raise ValueError(f'unsafe ZIP input: {rel}')
            entry = zipfile.ZipInfo('digital-twin-suite/' + rel, (2026, 10, 28, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes())
    return out.getvalue()

def build(root, output):
    root, output = Path(root), Path(output)
    for folder, allowed in (('site', SITE), ('skills', SKILLS), ('docs', DOCS)):
        exact_tree(root / folder, allowed)
    for rel in (*ROOT_FILES, 'scripts/install.py'):
        if (root / rel).is_symlink() or not (root / rel).is_file():
            raise ValueError(f'unsafe root input: {rel}')
    selected = json.loads((root / 'docs/final-artifacts.json').read_text())
    for key, (path, size, sha) in MEDIA.items():
        entry = selected['public_media'][key]
        if entry['sha256'] != sha or entry['bytes'] != size:
            raise ValueError(f'allowlist media declaration changed: {key}')
        verify_media(root / 'site' / path, size, sha)
    for rel in (*ROOT_FILES, *('docs/' + x for x in DOCS), *('skills/' + x for x in SKILLS), 'site/index.html', 'site/app.js'):
        text = (root / rel).read_text()
        if re.search(r'/Users/|/Volumes/|file://|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY', text):
            raise ValueError(f'private path or credential pattern in {rel}')
    archive = archive_bytes(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='twin-public-', dir=output.parent) as tmp:
        stage = Path(tmp) / 'dist'
        stage.mkdir()
        for rel in SITE:
            dest = stage / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / 'site' / rel, dest)
        for rel in (*ROOT_FILES, *('docs/' + x for x in DOCS), *('skills/' + x for x in SKILLS)):
            dest = stage / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / rel, dest)
        for name in DOCS:
            if name.endswith('.md'):
                (stage / 'docs' / name.replace('.md', '.html')).write_text(document_page((root / 'docs' / name).read_text(), name))
        (stage / 'assets/digital-twin-skills.zip').write_bytes(archive)
        records = []
        for path in sorted(stage.rglob('*')):
            if path.is_file():
                raw = path.read_bytes()
                records.append({'path': path.relative_to(stage).as_posix(), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
        (stage / 'build-manifest.json').write_text(json.dumps({'schema_version': 1, 'suite_version': 'V1.0.0', 'excludes': ['build-manifest.json'], 'files': records}, ensure_ascii=False, indent=2) + '\n')
        if output.is_symlink():
            raise ValueError('refuse symlink output')
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(stage, output)
    return records

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = build(root, args.out or root / 'dist')
    print(f'Built {len(result)} hashed public files plus manifest; selected media unchanged.')
