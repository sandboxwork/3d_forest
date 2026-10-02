import json, base64, sys
import numpy as np
d = json.load(open('/shared/river/assets/out/village_houses.json'))
meta = json.load(open('/shared/river/assets/out/village_houses.meta.json'))
print('mats', sorted(d['mats'].keys()))
for need in ('paint_trim', 'paint_shutter', 'paint_door', 'glass', 'window_glow'):
    assert need in d['mats'], need
print('glass alpha', d['mats']['glass']['alpha'])
for p in d['parts']:
    tot = 0; bad_wind = 0; degen = 0; nan = 0
    mn = np.array([1e9] * 3); mx = -mn
    for s in p['subs']:
        pos = np.frombuffer(base64.b64decode(s['pos']), dtype=np.float32).reshape(-1, 3)
        nrm = np.frombuffer(base64.b64decode(s['nrm']), dtype=np.float32).reshape(-1, 3)
        uv = np.frombuffer(base64.b64decode(s['uv']), dtype=np.float32).reshape(-1, 2)
        idx = np.frombuffer(base64.b64decode(s['idx']), dtype=np.uint16 if s['idx16'] else np.uint32).reshape(-1, 3)
        assert idx.max() < len(pos) and len(pos) == len(nrm) == len(uv)
        nan += int(np.isnan(pos).sum() + np.isnan(nrm).sum() + np.isnan(uv).sum())
        a, b, c = pos[idx[:, 0]], pos[idx[:, 1]], pos[idx[:, 2]]
        n = np.cross(b - a, c - a)
        ln = np.linalg.norm(n, axis=1)
        degen += int((ln < 1e-9).sum())
        vn = nrm[idx[:, 0]] + nrm[idx[:, 1]] + nrm[idx[:, 2]]
        dot = (n * vn).sum(1)
        ok = ln > 1e-9
        bad_wind += int((dot[ok] < 0).sum())
        tot += len(idx)
        mn = np.minimum(mn, pos.min(0)); mx = np.maximum(mx, pos.max(0))
    print('%-22s tris %6d  badwinding %5d (%.2f%%) degenerate %4d nan %d  bbox x[%.1f,%.1f] y[%.1f,%.1f] z(three -z)[%.1f,%.1f]' % (
        p['name'], tot, bad_wind, 100.0 * bad_wind / max(tot, 1), degen, nan, mn[0], mx[0], mn[1], mx[1], mn[2], mx[2]))
