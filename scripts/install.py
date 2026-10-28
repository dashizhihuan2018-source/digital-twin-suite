"""Install five self-contained skills without replacing existing directories."""
import argparse
import os
from pathlib import Path
import shutil

NAMES = ('digital-twin', 'twin-model-lightweight', 'twin-product-film', 'twin-fpv-film', 'twin-effects')


def install(root, dest, apply=False):
    sources = [root / 'skills' / name for name in NAMES]
    for source in sources:
        if not (source / 'SKILL.md').is_file():
            raise ValueError(f'missing SKILL.md: {source.name}')
        if any(p.is_symlink() for p in source.rglob('*')):
            raise ValueError('skill source must not contain symlinks')
    conflicts = [name for name in NAMES if (dest / name).exists() or (dest / name).is_symlink()]
    if conflicts:
        raise FileExistsError('existing skills preserved: ' + ', '.join(conflicts))
    if not apply:
        return list(NAMES)
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
    return list(NAMES)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        names = install(Path(__file__).resolve().parents[1], args.dest.expanduser(), args.apply)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    print(('Installed: ' if args.apply else 'Preview only: ') + ', '.join(names))
    print(f'Destination: {args.dest.expanduser()}')
