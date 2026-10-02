"""Mesh sanity: inverted closed components (negative signed volume), count of loose parts etc.  blender -b --python kt_check.py"""
import sys, time
sys.path.insert(0, '/shared/river/assets/blender')
from kt_lib import *
from kt_mats import init_mats
import kt_lib
import kt_dining, kt_stove, kt_counter, kt_storage, kt_hang, kt_decals, kt_meta
t0 = time.time()
reset_scene(); init_mats()
for m in (kt_dining, kt_stove, kt_counter, kt_storage, kt_hang, kt_decals, kt_meta):
    m.build()
print('built', tri_count(), round(time.time() - t0, 1))
bad = {}
tot_comp = 0
for mn, (bm, mat) in kt_lib.ACC.items():
    bm.faces.ensure_lookup_table(); bm.faces.index_update()
    seen = set()
    for f0 in bm.faces:
        if f0.index in seen:
            continue
        comp = []
        stack = [f0]
        seen.add(f0.index)
        closed = True
        while stack:
            f = stack.pop()
            comp.append(f)
            for e in f.edges:
                if len(e.link_faces) != 2:
                    closed = False
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index)
                        stack.append(g)
        tot_comp += 1
        if not closed or len(comp) < 4:
            continue
        vol = 0.0
        cen = Vector()
        n = 0
        for f in comp:
            cen += f.calc_center_median(); n += 1
        c0 = cen / n
        for f in comp:
            vs = [Vector(v.co) - c0 for v in f.verts]
            for i in range(1, len(vs) - 1):
                a, b, c = [(float(x.x), float(x.y), float(x.z)) for x in (vs[0], vs[i], vs[i + 1])]
                vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        if vol < -1e-9:
            xs = [v.co.x for f in comp for v in f.verts]; ys = [v.co.y for f in comp for v in f.verts]; zs = [v.co.z for f in comp for v in f.verts]
            bad.setdefault(mn, []).append((len(comp), tuple(round(x, 3) for x in (cen / n)), (round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3), round(max(zs) - min(zs), 3))))
print('components', tot_comp)
for mn, l in bad.items():
    print('INVERTED', mn, len(l), l[:10])
print('done', round(time.time() - t0, 1))
