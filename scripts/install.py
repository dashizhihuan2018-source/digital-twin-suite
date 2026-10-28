"""Install nine self-contained skills without replacing existing directories."""
import argparse
import os
from pathlib import Path
import shutil

NAMES = ('digital-twin', 'twin-model-lightweight', 'twin-product-film', 'twin-fpv-film', 'twin-effects',
         'poster-production', 'pdfmaster-moments-poster', 'video-cover-poster', 'product-launch-website')


def install(root, dest, apply=False, names=None):
    selected = list(NAMES if names is None else names)
    if not selected or len(selected) != len(set(selected)) or any(name not in NAMES for name in selected):
        raise ValueError('choose unique skill names from the install catalog')
    sources = [root / 'skills' / name for name in selected]
    for source in sources:
        if not (source / 'SKILL.md').is_file():
            raise ValueError(f'missing SKILL.md: {source.name}')
        if any(p.is_symlink() for p in source.rglob('*')):
            raise ValueError('skill source must not contain symlinks')
    conflicts = [name for name in selected if (dest / name).exists() or (dest / name).is_symlink()]
    if conflicts:
        raise FileExistsError('existing skills preserved: ' + ', '.join(conflicts))
    if not apply:
        return selected
    dest.mkdir(parents=True, exist_ok=True)
    installed = []
    try:
        for source in sources:
            target = dest / source.name
            target.mkdir()  # Atomic reservation; never replace a concurrent install.
            installed.append(target)
            shutil.copytree(source, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    except Exception:
        # Only directories created by this invocation are rolled back.
        for target in installed:
            shutil.rmtree(target)
        raise
    return selected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--only', nargs='+', choices=NAMES, help='install selected skills, preserving all other existing skills')
    args = parser.parse_args()
    try:
        names = install(Path(__file__).resolve().parents[1], args.dest.expanduser(), args.apply, args.only)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    print(('Installed: ' if args.apply else 'Preview only: ') + ', '.join(names))
    print(f'Destination: {args.dest.expanduser()}')
