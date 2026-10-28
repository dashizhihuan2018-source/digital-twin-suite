"""Conservative segment-versus-inflated-AABB clearance check, not mesh proof."""
import argparse
import json
import math
from pathlib import Path


def vector(value):
    return isinstance(value, list) and len(value) == 3 and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in value)


def intersects(a, b, low, high):
    enter, leave = 0.0, 1.0
    for axis in range(3):
        delta = b[axis] - a[axis]
        if abs(delta) < 1e-12:
            if a[axis] < low[axis] or a[axis] > high[axis]:
                return False
        else:
            t1, t2 = (low[axis] - a[axis]) / delta, (high[axis] - a[axis]) / delta
            enter, leave = max(enter, min(t1, t2)), min(leave, max(t1, t2))
            if enter > leave:
                return False
    return True


def check(data):
    points, boxes, radius = data.get('points', []), data.get('boxes', []), data.get('radius', 0)
    if not isinstance(radius, (int, float)) or isinstance(radius, bool) or not math.isfinite(radius) or radius < 0:
        return ['radius must be finite and nonnegative']
    if not isinstance(points, list) or len(points) < 2 or not all(vector(p) for p in points):
        return ['need at least two finite XYZ points']
    if not isinstance(boxes, list):
        return ['boxes must be a list']
    for box in boxes:
        if not isinstance(box, dict) or not vector(box.get('min')) or not vector(box.get('max')) or any(a > b for a, b in zip(box['min'], box['max'])):
            return ['invalid axis-aligned obstacle box']
    errors = []
    for i, (a, b) in enumerate(zip(points, points[1:])):
        for j, box in enumerate(boxes):
            low = [v - radius for v in box['min']]
            high = [v + radius for v in box['max']]
            if intersects(a, b, low, high):
                errors.append(f'segment {i} intersects inflated box {j}')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('route', type=Path)
    args = parser.parse_args()
    try:
        errors = check(json.loads(args.route.read_text()))
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, f'invalid route: {exc}\n')
    print(json.dumps({'errors': errors, 'method': 'segments vs radius-inflated AABB', 'meshCollisionVerified': False, 'cameraFrustumVerified': False}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))
