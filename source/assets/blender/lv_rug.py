"""Oval (stadium) braided rug: spiral-like concentric cord rows with crest/groove relief, per-cord colour, path-aligned UVs."""
from lv_fire import *


def braided_rug(cx, cy, a, b, rot=0, S=118, pitch=0.034, seed=4):
    rr = random.Random(seed)
    L0 = a - b
    nrows = int(b / pitch)
    pal = ['#8c3a2e', '#d9c7a0', '#3f5f55', '#c7a04a', '#5a4632', '#b8a27a', '#7a2f2a', '#e0d4b8', '#4a6b5c', '#a8793a']
    # colour zones from the edge toward the centre
    zones = []
    k = 0
    pi = 0
    while k < nrows + 2:
        wd = rr.randint(2, 5)
        zones.append((k, k + wd, C(pal[pi % len(pal)])))
        k += wd
        pi += 1 if rr.random() < 0.8 else 2
    def zone_col(kf):
        for (k0, k1, c) in zones:
            if k0 <= kf < k1:
                return c
        return zones[-1][2]
    def stadium(r, u):
        """point on the stadium path (centre-line radius r) at fraction u of the perimeter, starting at +x end going CCW"""
        P = 4 * L0 + TAU * r
        s = (u % 1.0) * P
        # segments: right semicircle (angle -90..90), top straight, left semicircle, bottom straight; start at (L0 + r, 0)
        seg0 = math.pi * r / 2          # quarter-circle from angle 0 to 90
        if s < seg0:
            t = s / r
            return Vector((L0 + r * math.cos(t), r * math.sin(t))), Vector((-math.sin(t), math.cos(t)))
        s -= seg0
        if s < 2 * L0:
            return Vector((L0 - s, r)), Vector((-1, 0))
        s -= 2 * L0
        if s < math.pi * r:
            t = math.pi / 2 + s / r
            return Vector((-L0 + r * math.cos(t), r * math.sin(t))), Vector((-math.sin(t), math.cos(t)))
        s -= math.pi * r
        if s < 2 * L0:
            return Vector((-L0 + s, -r)), Vector((1, 0))
        s -= 2 * L0
        t = -math.pi / 2 + s / r
        return Vector((L0 + r * math.cos(t), r * math.sin(t))), Vector((-math.sin(t), math.cos(t)))
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    cl = bm.loops.layers.float_color.new('Col')
    # radial profile samples: (distance from edge in cords, height, groove flag)
    samples = []
    for k in range(nrows):
        samples.append((k + 0.0, 'g'))
        samples.append((k + 0.5, 'c'))
    samples.append((nrows + 0.0, 'g'))
    rowsv = []
    cols_row = []
    for (kd, typ) in samples:
        d = kd * pitch
        r = max(b - d, 0.012)
        ring = []
        for j in range(S):
            u = j / S
            p, tg = stadium(r, u)
            nrm = Vector((tg.y, -tg.x))     # outward
            rad_off = (b - d - r)
            z = 0.0035 if typ == 'g' else 0.0125
            # edge roll-off + gentle wear undulation
            edge = sstep(0.0, 1.2, kd)
            z = z * (0.45 + 0.55 * edge) if kd < 1.5 else z
            z += 0.0016 * mnoise.noise(Vector((p.x * 3.2 + seed, p.y * 3.2, 0.5)))
            if typ == 'c':
                # twisted-braid undulation along the path
                z += 0.0011 * math.sin(u * S * 1.15 + kd * 1.7)
            ring.append(bm.verts.new((p.x, p.y, z)))
        rowsv.append((kd, typ, ring))
    for i in range(len(rowsv) - 1):
        k0, t0, r0 = rowsv[i]
        k1, t1, r1 = rowsv[i + 1]
        for j in range(S):
            j2 = (j + 1) % S
            try:
                f = bm.faces.new([r0[j], r0[j2], r1[j2], r1[j]][::-1])
            except ValueError:
                continue
            f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # per-loop uv/colour: uv u = arc length along the row (m)/tile, v = radial metres/tile
    tile = 0.4
    for f in bm.faces:
        for l in f.loops:
            v = l.vert
            pass
    vinfo = {}
    for (kd, typ, ring) in rowsv:
        r = max(b - kd * pitch, 0.012)
        P = 4 * L0 + TAU * r
        for j, v in enumerate(ring):
            vinfo[v.index if False else v] = (kd, typ, j / S * P)
    for f in bm.faces:
        for l in f.loops:
            kd, typ, s = vinfo[l.vert]
            l[ul].uv = (s / tile, kd * pitch / tile)
            kc0 = zone_col(int(kd + 0.001))
            mx_ = max(kc0) + 1e-6
            kc = tuple(0.66 + 0.34 * c_ / mx_ for c_ in kc0)     # the braided texture already carries the cord colours: only a gentle zone tint
            # braid look: slightly lighter crest, darker groove, strand-to-strand variation
            sh = 0.62 if typ == 'g' else 0.8
            sh *= 0.95 + 0.08 * (0.5 + 0.5 * math.sin(s * 11 + kd * 2.3))
            sh *= 1 + 0.08 * nz(l.vert.co.x * 6, l.vert.co.y * 6, 2.0)
            l[cl] = (kc[0] * sh, kc[1] * sh, kc[2] * sh, 1.0)
    # skirt and underside
    outer = rowsv[0][2]
    sk = [bm.verts.new((v.co.x, v.co.y, 0.0)) for v in outer]
    for j in range(S):
        j2 = (j + 1) % S
        try:
            f = bm.faces.new([outer[j], sk[j], sk[j2], outer[j2]][::-1])
            f.smooth = True
            kc = zone_col(0)
            for l in f.loops:
                l[cl] = (0.5, 0.5, 0.5, 1.0)
                l[ul].uv = (0, 0)
        except ValueError:
            pass
    # dump straight into the accumulator (colours/uv are set), transform to world
    bm2 = get_bm(M['rug_braided'])
    c2 = bm2.loops.layers.float_color['Col']
    u2 = bm2.loops.layers.uv['UVMap']
    Mx = xf((cx, cy, F_ + 0.0015), (0, 0, rot))
    vm = {v: bm2.verts.new(Mx @ v.co) for v in bm.verts}
    for f in bm.faces:
        try:
            nf = bm2.faces.new([vm[v] for v in f.verts])
        except ValueError:
            continue
        nf.smooth = True
        for ls, l in zip(f.loops, nf.loops):
            l[c2] = ls[cl]
            l[u2].uv = ls[ul].uv
    bm.free()
