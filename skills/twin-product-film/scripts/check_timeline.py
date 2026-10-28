"""Validate declared frame intervals and speech anchors; no audio recognition."""
import argparse
import json
import math
from pathlib import Path


def check(data):
    errors = []
    fps, frames = data.get('fps'), data.get('frames')
    if not isinstance(fps, (int, float)) or isinstance(fps, bool) or not math.isfinite(fps) or fps <= 0:
        return ['fps must be finite and positive']
    if not isinstance(frames, int) or isinstance(frames, bool) or frames <= 0:
        return ['frames must be a positive integer']
    seen = set()
    for i, shot in enumerate(data.get('shots', [])):
        identity = shot.get('id')
        if not isinstance(identity, str) or not identity or identity in seen:
            errors.append(f'shot {i}: missing or duplicate id')
        if isinstance(identity, str):
            seen.add(identity)
        start, end = shot.get('start'), shot.get('end')
        if any(not isinstance(v, int) or isinstance(v, bool) for v in (start, end)) or not 0 <= start < end <= frames:
            errors.append(f'shot {i}: invalid half-open [start,end) frame range')
    for i, anchor in enumerate(data.get('anchors', [])):
        word, visible = anchor.get('wordSeconds'), anchor.get('fullyVisibleFrame')
        if not isinstance(word, (int, float)) or isinstance(word, bool) or not math.isfinite(word) or not 0 <= word < frames / fps:
            errors.append(f'anchor {i}: invalid wordSeconds')
        elif not isinstance(visible, int) or isinstance(visible, bool) or not 0 <= visible < frames:
            errors.append(f'anchor {i}: invalid fullyVisibleFrame')
        elif visible / fps > word:
            errors.append(f'anchor {i}: target fully visible after spoken word')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('timeline', type=Path)
    args = parser.parse_args()
    try:
        errors = check(json.loads(args.timeline.read_text()))
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, f'invalid timeline: {exc}\n')
    print(json.dumps({'errors': errors, 'audioRecognized': False, 'visualVerified': False}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))
