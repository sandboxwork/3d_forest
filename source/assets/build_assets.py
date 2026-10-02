#!/usr/bin/env python3
"""Inline assets/out/*.json bundles + assets/tex/*.jpg into riverside_forest.html between
<!--ASSETS_BEGIN--> and <!--ASSETS_END--> markers, and keep AssetLib in sync between
/*ASSETLIB_BEGIN*/ and /*ASSETLIB_END*/ markers. Usage: python3 assets/build_assets.py [bundle names...]"""
import json, os, re, sys, base64, glob
ROOT = os.path.dirname(os.path.abspath(__file__)); HTML = os.path.join(ROOT, '..', 'riverside_forest.html')
names = sys.argv[1:]
bundles = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'out', '*.json'))):
    n = os.path.basename(f)[:-5]
    if n.endswith('.meta') or n.startswith('_') or (names and n not in names) or (not names and n in ('house_interior',)): continue
    d = json.load(open(f))
    if 'parts' in d:                       # geometry bundle
        bundles[n] = d
        mp = os.path.join(ROOT, 'out', n + '.meta.json')
        if os.path.exists(mp): d['meta'] = {**d.get('meta', {}), **json.load(open(mp))}
for n in list(bundles): pass
tex = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'tex', '*.jpg'))):
    tex[os.path.basename(f)[:-4]] = 'data:image/jpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
import numpy as np, gzip
def b2a(a): return base64.b64encode(a.tobytes()).decode()
def a2n(s, dt): return np.frombuffer(base64.b64decode(s), dtype=dt)
def quantize(bundle):
    for part in bundle['parts']:
        for sub in part['subs']:
            pos = a2n(sub['pos'], np.float32).reshape(-1, 3)
            lo, hi = pos.min(0), pos.max(0); c = (lo + hi) / 2; h = np.maximum((hi - lo) / 2, 1e-6)
            q = np.round((pos - c) / h * 32767).astype(np.int16)
            sub['pos'] = b2a(q); sub['pq'] = [float(x) for x in c] + [float(x) for x in h]
            uv = a2n(sub['uv'], np.float32).reshape(-1, 2); umn = uv.min(0); ur = np.maximum(uv.max(0) - umn, 1e-6)
            sub['uv'] = b2a(np.round((uv - umn) / ur * 65535).astype(np.uint16)); sub['uq'] = [float(umn[0]), float(umn[1]), float(ur[0]), float(ur[1])]
            n = a2n(sub['nrm'], np.float32)
            sub['nrm'] = b2a(np.round(np.clip(n, -1, 1) * 127).astype(np.int8))
            if sub.get('col'):
                cc = a2n(sub['col'], np.float32); mx = float(max(cc.max(), 1e-6)); sub['col'] = b2a(np.round(np.clip(cc / mx, 0, 1) * 255).astype(np.uint8)); sub['cs'] = mx
    return bundle
DROP = {'flower_box': ['flower_bed_a', 'flower_bed_b']}
for n, parts in DROP.items():
    if n in bundles: bundles[n]['parts'] = [q for q in bundles[n]['parts'] if q['name'] not in parts]
pack = {}
for n, b in bundles.items():
    raw = json.dumps(quantize(b), separators=(',', ':')).encode()
    pack[n] = base64.b64encode(gzip.compress(raw, 9)).decode()
blob = '<!--ASSETS_BEGIN-->\n<script>\nwindow.ASSET_PACK=' + json.dumps(pack, separators=(',', ':')) + ';\nwindow.ASSET_BUNDLES={};\nwindow.ASSET_TEX=' + json.dumps(tex, separators=(',', ':')) + ';\n</script>\n<!--ASSETS_END-->'
h = open(HTML, encoding='utf-8').read()
if '<!--ASSETS_BEGIN-->' in h:
    h = re.sub(r'<!--ASSETS_BEGIN-->.*?<!--ASSETS_END-->', lambda m: blob, h, flags=re.S)
else:
    h = h.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>', blob + '\n<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>', 1)
MODS = ['assetlib.js', 'village_core.js', 'fauna.js', 'flora.js', 'cabin.js', 'village.js', 'fishing.js', 'minimap.js']
src = ''
for m in MODS:
    fp = os.path.join(ROOT, m)
    if os.path.exists(fp): src += '/* ---- ' + m + ' ---- */\n' + open(fp, encoding='utf-8').read() + '\n'
lib = '/*MODS_BEGIN*/\n' + src + '/*MODS_END*/'
h = re.sub(r'/\*ASSETLIB_BEGIN\*/.*?/\*ASSETLIB_END\*/\n*', '', h, flags=re.S)
marker = '/* =====================================================================\n   08_post.js'
if '/*MODS_BEGIN*/' in h:
    h = re.sub(r'/\*MODS_BEGIN\*/.*?/\*MODS_END\*/', lambda m: lib, h, flags=re.S)
else:
    assert marker in h; h = h.replace(marker, lib + '\n\n' + marker, 1)
open(HTML, 'w', encoding='utf-8').write(h)
print('bundles:', list(bundles), 'tex:', list(tex), 'html KB:', os.path.getsize(HTML) // 1024)
