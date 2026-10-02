#!/usr/bin/env python3
"""Generate robust far-LOD impostor parts '<part>_lod2' for flora bundles (no decimation):
   stem + leaf tuft (green) + flower head (disc / crossed quads) colored from the non-green materials.
   uv run --with numpy python3 assets/make_lod2.py flowers_meadow plants_water_edge"""
import sys, json, base64, re, os
import numpy as np
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'out')
GREEN = re.compile(r'stem|leaf|sepal|blade|grass|frond|foliage|bract|calyx|reed_|sedge|horsetail|fern|w_stem|w_leaf|stalk|thorn|lilypad|needle', re.I)
KEEP = re.compile(r'^(lilypad|waterlily)')
def a2n(s, dt): return np.frombuffer(base64.b64decode(s), dtype=dt)
def b2a(a): return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
def lin(c): return np.array(c, np.float32)

def sub_data(s):
    pos = a2n(s['pos'], np.float32).reshape(-1, 3)
    col = a2n(s['col'], np.float32).reshape(-1, 3) if s.get('col') else None
    return pos, col

class Mesh:
    def __init__(self): self.p, self.n, self.c, self.i = [], [], [], []
    def tri(self, a, b, c, n, col):
        k = len(self.p); self.p += [a, b, c]; self.n += [n, n, n]; self.c += [col, col, col]; self.i += [k, k + 1, k + 2]
    def quad(self, a, b, c, d, n, col): self.tri(a, b, c, n, col); self.tri(a, c, d, n, col)
    def sub(self, mat):
        p = np.array(self.p, np.float32); n = np.array(self.n, np.float32); c = np.array(self.c, np.float32)
        idx = np.array(self.i, np.uint16)
        return {'mat': mat, 'n': int(len(p)), 'tris': int(len(idx) // 3), 'pos': b2a(p), 'nrm': b2a(n), 'uv': b2a(np.zeros((len(p), 2), np.float32)), 'idx': b2a(idx), 'idx16': True, 'col': b2a(c)}

def build(part, mats):
    greens, heads = [], []
    for s in part['subs']:
        pos, col = sub_data(s); m = mats.get(s['mat'], {'color': [0.3, 0.3, 0.3]})
        base = lin(m['color']); mean_c = (col.mean(0) if col is not None else np.ones(3, np.float32))
        avg = np.clip(base * mean_c, 0, 1)
        isg = bool(GREEN.search(s['mat'])) or (avg[1] > avg[0] * 1.05 and avg[1] > avg[2] * 1.3 and avg.max() < 0.45)
        (greens if isg else heads).append((pos, avg, s['mat']))
    allp = np.concatenate([p for p, _, _ in greens + heads]); top = float(allp[:, 1].max()); base_r = float(np.hypot(allp[:, 0], allp[:, 2]).max())
    M = Mesh(); up = (0.0, 1.0, 0.0)
    gcol = tuple(np.clip(np.mean([c for _, c, _ in greens], 0), 0, 1)) if greens else (0.05, 0.2, 0.03)
    gcol = tuple(float(x) for x in gcol)
    if heads:
        hp = np.concatenate([p for p, _, _ in heads]); lo, hi = hp.min(0), hp.max(0); ctr = (lo + hi) / 2; half = np.maximum((hi - lo) / 2, 1e-3)
        w = np.array([c.sum() for _, c, _ in heads], np.float32); nv = np.array([len(p) for p, _, _ in heads], np.float32)
        sat = np.array([(c.max() - c.min()) + 0.12 for _, c, _ in heads], np.float32); wgt = np.sqrt(nv) * sat * sat
        hcol = tuple(float(x) for x in np.clip(sum(c * g for (_, c, _), g in zip(heads, wgt)) / wgt.sum() * 1.25, 0, 1))
        cx, cy, cz = [float(x) for x in ctr]; hx, hy, hz = [float(x) for x in half]
        # stem: two crossed thin quads from base to head
        sw = max(0.004, top * 0.01); sx, sy, sz = cx * 0.9, cy - hy * 0.4, cz * 0.9
        for ang in (0.0, np.pi / 2):
            ox, oz = np.cos(ang) * sw, np.sin(ang) * sw
            M.quad((-ox, 0, -oz), (ox, 0, oz), (sx + ox, sy, sz + oz), (sx - ox, sy, sz - oz), (-np.sin(ang), 0, np.cos(ang)), gcol)
        # leaf tuft
        lr = min(max(base_r, 0.05), 0.25) * 0.9; lh = min(top * 0.25, 0.22)
        for k in range(3):
            a = k * 2.094 + 0.4; M.tri((0, 0, 0), (np.cos(a + 0.35) * lr, lh * 0.5, np.sin(a + 0.35) * lr), (np.cos(a - 0.35) * lr, lh * 0.5, np.sin(a - 0.35) * lr), up, gcol)
        aspect = hy / max(max(hx, hz), 1e-3)
        if aspect > 1.7:     # spike / raceme / elongated head: crossed vertical quads
            r = max(hx, hz) * 0.5
            for ang in (0.0, np.pi / 2):
                ox, oz = np.cos(ang) * r, np.sin(ang) * r
                M.quad((cx - ox, cy - hy, cz - oz), (cx + ox, cy - hy, cz + oz), (cx + ox * 0.35, cy + hy, cz + oz * 0.35), (cx - ox * 0.35, cy + hy, cz - oz * 0.35), (-np.sin(ang), 0, np.cos(ang)), hcol)
        else:                # rosette / umbel / ball head: tilted octagonal disc + crossed quad
            r = max(hx, hz) * 0.55; tilt = 0.75
            ring = []
            for k in range(8):
                a = k * np.pi / 4; x, z = np.cos(a) * r, np.sin(a) * r
                ring.append((cx + x, cy + z * np.sin(tilt) * 0.6 + hy * 0.3, cz + z * np.cos(tilt) * 0.2 + 0.0))
            for k in range(8): M.tri((cx, cy + hy * 0.3, cz), ring[k], ring[(k + 1) % 8], up, hcol)
            rr = max(r, hy) * 0.5
            M.quad((cx - rr, cy - hy * 0.5, cz), (cx + rr, cy - hy * 0.5, cz), (cx + rr * 0.7, cy + hy * 0.8, cz), (cx - rr * 0.7, cy + hy * 0.8, cz), (0, 0, 1), hcol)
    else:                    # foliage only: radiating blades
        r = max(base_r * 0.7, 0.04); n = 5
        for k in range(n):
            a = k * 2 * np.pi / n + 0.3
            M.tri((np.cos(a) * 0.02, 0, np.sin(a) * 0.02), (np.cos(a + 0.25) * 0.02, 0, np.sin(a + 0.25) * 0.02), (np.cos(a) * r, top * 0.95, np.sin(a) * r), (-np.sin(a), 0, np.cos(a)), gcol)
    return [M.sub('impostor')]

for name in sys.argv[1:]:
    path = os.path.join(OUT, name + '.json'); B = json.load(open(path))
    B['parts'] = [p for p in B['parts'] if not (p['name'].endswith('_lod2') and not KEEP.match(p['name']))]
    B['mats']['impostor'] = {'color': [1, 1, 1], 'rough': 0.75, 'metal': 0.0, 'alpha': 1.0, 'tex': '', 'uvscale': 1.0, 'double': True}
    new = []
    for p in list(B['parts']):
        nm = p['name']
        if nm.endswith('_lod1') or nm.endswith('_lod2') or KEEP.match(nm): continue
        if sum(s['tris'] for s in p['subs']) < 400: continue
        new.append({'name': nm + '_lod2', 'parent': None, 'pivot': list(p['pivot']), 'subs': build(p, B['mats'])})
    B['parts'] += new
    fixed = 0
    for p in B['parts']:
        for sub in p['subs']:
            n = a2n(sub['nrm'], np.float32).reshape(-1, 3).copy(); ln = np.linalg.norm(n, axis=1)
            bad = ~np.isfinite(ln) | (ln < 0.5)
            if bad.any():
                n[bad] = (0.0, 1.0, 0.0); fixed += int(bad.sum())
            ok = ~bad; n[ok] /= ln[ok][:, None]
            sub['nrm'] = b2a(n)
    print(name, 'fixed normals:', fixed)
    json.dump(B, open(path, 'w'), separators=(',', ':'))
    print(name, 'lod2 impostors:', len(new), 'tris', sum(s['tris'] for q in new for s in q['subs']))
