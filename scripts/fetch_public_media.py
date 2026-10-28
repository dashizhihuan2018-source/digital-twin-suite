"""Fetch or verify the immutable, authorized public 4K film; never add it to Git."""
import argparse
import hashlib
from pathlib import Path
import tempfile
import urllib.request

NAME = 'changfeng-digital-twin-V3.5.5-4K.mp4'
SIZE = 102288446
SHA256 = 'f21473bafde5710bafb4eb1ae69b043218d7adc03937ce8f4b75c0833825b83b'
URL = 'https://github.com/dashizhihuan2018-source/digital-twin-suite/releases/download/changfeng-film-v3.5.5/' + NAME

def verify(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size != SIZE:
        raise ValueError('4K film missing, unsafe, or wrong size')
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != SHA256:
        raise ValueError('4K film SHA256 mismatch')

def fetch(directory, verify_only=False):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError('unsafe media directory')
    target = directory / NAME
    if target.exists() or target.is_symlink() or verify_only:
        verify(target)
        return target
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='download-', dir=directory) as tmp:
        candidate = Path(tmp) / NAME
        request = urllib.request.Request(URL, headers={'User-Agent': 'digital-twin-public-media/1.2'})
        with urllib.request.urlopen(request, timeout=60) as response, candidate.open('xb') as output:
            count = 0
            while chunk := response.read(1024 * 1024):
                count += len(chunk)
                if count > SIZE:
                    raise ValueError('4K film response exceeds expected size')
                output.write(chunk)
        verify(candidate)
        candidate.rename(target)
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    fetch(Path(__file__).resolve().parents[1] / '.release-media', args.verify_only)
    print('Exact authorized 4K film verified (size and SHA256).')
