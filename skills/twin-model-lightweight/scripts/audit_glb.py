"""Read-only GLB inventory. This is not a decoder or glTF Validator."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

def audit(raw):
    if len(raw) < 20: raise ValueError('Truncated GLB')
    magic, version, length = struct.unpack_from('<III', raw)
    if magic != 0x46546C67 or version != 2 or length != len(raw):
        raise ValueError('Invalid GLB magic, version or declared length')
    offset, document, chunks = 12, None, []
    while offset < length:
        if offset + 8 > length: raise ValueError('Truncated chunk header')
        size, kind = struct.unpack_from('<II', raw, offset)
        offset += 8
        if size % 4 or offset + size > length: raise ValueError('Invalid chunk size')
        payload = raw[offset:offset + size]
        if not chunks and kind != 0x4E4F534A: raise ValueError('First chunk must be JSON')
        if kind == 0x4E4F534A:
            if document is not None: raise ValueError('Duplicate JSON chunk')
            document = json.loads(payload)
        chunks.append({'type': hex(kind), 'bytes': size})
        offset += size
    if not isinstance(document, dict) or document.get('asset', {}).get('version') != '2.0':
        raise ValueError('Expected glTF 2.0 JSON')
    accessors, triangles, modes = document.get('accessors', []), 0, set()
    for mesh in document.get('meshes', []):
        for p in mesh.get('primitives', []):
            mode = p.get('mode', 4)
            if mode != 4:
                modes.add(mode)
                continue
            a = p.get('indices', p.get('attributes', {}).get('POSITION'))
            if a is not None:
                if not isinstance(a, int) or isinstance(a, bool) or not 0 <= a < len(accessors):
                    raise ValueError('Primitive references an invalid accessor')
                count = accessors[a].get('count')
                if not isinstance(count, int) or isinstance(count, bool) or count < 0 or count % 3:
                    raise ValueError('Triangle accessor count must be a nonnegative multiple of three')
                triangles += count // 3
    nodes = document.get('nodes', [])
    external = []
    for key in ('buffers', 'images'):
        external += [x['uri'] for x in document.get(key, []) if 'uri' in x and not x['uri'].startswith('data:')]
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            **{k:len(document.get(k, [])) for k in ('scenes','nodes','meshes','materials','textures','images','animations')},
            'triangles':triangles,'triangleMetric':'Sum of mesh primitive declarations, not scene instances',
            'otherPrimitiveModes':sorted(modes),'chunks':chunks,
            'extensionsRequired':document.get('extensionsRequired', []), 'externalResources':external,
            'semanticNodes':[{'nodeIndex':i, **{k:n[k] for k in ('name','extras','matrix','translation','rotation','scale','children','mesh') if k in n}} for i,n in enumerate(nodes)],
            'decodedGeometryVerified':False,'visualVerified':False,
            'limits':'Counts use JSON declarations; compressed accessors, world bounds, actual pixels and semantic equivalence require a target loader and independent comparison.'}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('glb',type=Path)
    args=p.parse_args()
    print(json.dumps(audit(args.glb.read_bytes()),ensure_ascii=False,indent=2))
