"""House-shell modelling helpers: per-material bmesh collectors, lattice boxes, prisms, lathes, stones."""
import sys
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
import random, math
import mathutils.noise as mnoise
from contextlib import contextmanager

rng = random.Random(11)
CUR = {}
V3 = Vector


def B(mat):
    bm = CUR.get(mat)
    if bm is None:
        bm = bmesh.new()
        bm.loops.layers.uv.new('UVMap')
        bm.loops.layers.float_color.new('Col')
        CUR[mat] = bm
    return bm


@contextmanager
def part():
    global CUR
    old = CUR
    CUR = {}
    try:
        yield CUR
    finally:
        CUR = old


def nz3(p, f=1.0, o=0.0):
    return mnoise.noise(V3((p[0] * f + o, p[1] * f + o * 1.7, p[2] * f - o)))


def addface(bm, verts, center):
    f = bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(f.calc_center_median() - center) < 0:
        f.normal_flip()
    return f


_CURBM = [None]


def setbm(bm):
    _CURBM[0] = bm


def paint(faces, col=(1, 1, 1), cj=0.0, cfun=None, freq=2.3, seed=0.0):
    if not faces:
        return
    cl = _CURBM[0].loops.layers.float_color['Col']
    for f in faces:
        for l in f.loops:
            c = col
            if cfun is not None:
                c = cfun(l.vert.co)
            if cj:
                k = 1.0 + cj * nz3(l.vert.co, freq, seed) + cj * 0.35 * (rng.random() - 0.5)
                c = (c[0] * k, c[1] * k, c[2] * k)
            l[cl] = (c[0], c[1], c[2], 1.0)


def box(mat, x0, x1, y0, y1, z0, z1, col=(1, 1, 1), n=(1, 1, 1), cj=0.0, skip=(), post=None, cfun=None,
        freq=2.3, seed=0.0):
    if x1 < x0: x0, x1 = x1, x0
    if y1 < y0: y0, y1 = y1, y0
    if z1 < z0: z0, z1 = z1, z0
    x1 = max(x1, x0 + 1e-4); y1 = max(y1, y0 + 1e-4); z1 = max(z1, z0 + 1e-4)
    bm = B(mat)
    setbm(bm)
    nx, ny, nz = n
    cache = {}

    def Vt(i, j, k):
        key = (i, j, k)
        v = cache.get(key)
        if v is None:
            v = bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, z0 + (z1 - z0) * k / nz))
            cache[key] = v
        return v

    cen = V3(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    faces = []

    def quad(a, b, c, d):
        faces.append(addface(bm, [Vt(*a), Vt(*b), Vt(*c), Vt(*d)], cen))

    for i in range(nx):
        for j in range(ny):
            if 'bottom' not in skip: quad((i, j, 0), (i + 1, j, 0), (i + 1, j + 1, 0), (i, j + 1, 0))
            if 'top' not in skip: quad((i, j, nz), (i + 1, j, nz), (i + 1, j + 1, nz), (i, j + 1, nz))
    for i in range(nx):
        for k in range(nz):
            if 'front' not in skip: quad((i, 0, k), (i + 1, 0, k), (i + 1, 0, k + 1), (i, 0, k + 1))
            if 'back' not in skip: quad((i, ny, k), (i + 1, ny, k), (i + 1, ny, k + 1), (i, ny, k + 1))
    for j in range(ny):
        for k in range(nz):
            if 'left' not in skip: quad((0, j, k), (0, j + 1, k), (0, j + 1, k + 1), (0, j, k + 1))
            if 'right' not in skip: quad((nx, j, k), (nx, j + 1, k), (nx, j + 1, k + 1), (nx, j, k + 1))
    if post:
        for (i, j, k), v in cache.items():
            post(v, i, j, k)
    paint(faces, col, cj, cfun, freq, seed)
    return faces


def hexa(mat, p, col=(1, 1, 1), cj=0.0, skip=()):
    """p: 8 points, bottom 0..3 (ccw from top), top 4..7."""
    bm = B(mat); setbm(bm)
    vs = [bm.verts.new(q) for q in p]
    cen = sum((V3(q) for q in p), V3()) / 8
    quads = {'bottom': (0, 3, 2, 1), 'top': (4, 5, 6, 7), 'f': (0, 1, 5, 4), 'r': (1, 2, 6, 5), 'b': (2, 3, 7, 6), 'l': (3, 0, 4, 7)}
    fs = [addface(bm, [vs[i] for i in q], cen) for k, q in quads.items() if k not in skip]
    paint(fs, col, cj)
    return fs


def obox(mat, O, X, Y, Z, lx, ly, lz, col=(1, 1, 1), cj=0.0):
    O = V3(O); X = V3(X).normalized(); Y = V3(Y).normalized(); Z = V3(Z).normalized()
    pts = []
    for z in (0, 1):
        for (a, b) in ((0, 0), (1, 0), (1, 1), (0, 1)):
            pts.append(O + X * lx * a + Y * ly * b + Z * lz * z)
    return hexa(mat, pts, col, cj)


def prism(mat, pts, O, A, Bv, U, L, col=(1, 1, 1), s1=1.0, cj=0.0, cfun=None, caps=(True, True)):
    bm = B(mat); setbm(bm)
    O = V3(O); A = V3(A); Bv = V3(Bv); U = V3(U)
    r0 = [bm.verts.new(O + A * a + Bv * b) for a, b in pts]
    r1 = [bm.verts.new(O + U * L + (A * a + Bv * b) * s1) for a, b in pts]
    pc = sum((A * a + Bv * b for a, b in pts), V3()) / len(pts)
    cen = O + U * (L / 2) + pc * (1 + s1) / 2
    fs = []
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        fs.append(addface(bm, [r0[i], r0[j], r1[j], r1[i]], cen))
    if caps[0]: fs.append(addface(bm, r0, cen))
    if caps[1]: fs.append(addface(bm, r1, cen))
    paint(fs, col, cj, cfun)
    return fs


def circle(r, segs, jit=0.0):
    return [(r * (1 + jit * (rng.random() - .5)) * math.cos(2 * math.pi * i / segs),
             r * (1 + jit * (rng.random() - .5)) * math.sin(2 * math.pi * i / segs)) for i in range(segs)]


def cyl(mat, p0, p1, r, segs=10, col=(1, 1, 1), s1=1.0, cj=0.0, caps=(True, True), jit=0.0):
    p0 = V3(p0); p1 = V3(p1)
    d = p1 - p0
    L = d.length
    U = d.normalized()
    t = V3((0, 0, 1)) if abs(U.z) < 0.95 else V3((1, 0, 0))
    A = U.cross(t).normalized(); Bv = U.cross(A).normalized()
    return prism(mat, circle(r, segs, jit), p0, A, Bv, U, L, col, s1, cj, caps=caps)


def lathe(mat, base, prof, segs=12, col=(1, 1, 1), cj=0.0):
    bm = B(mat); setbm(bm)
    base = V3(base)
    rings = []
    for z, r in prof:
        rings.append([bm.verts.new((base.x + r * math.cos(2 * math.pi * i / segs), base.y + r * math.sin(2 * math.pi * i / segs), base.z + z)) for i in range(segs)])
    fs = []
    for a in range(len(prof) - 1):
        za = base.z + (prof[a][0] + prof[a + 1][0]) / 2
        cen = V3((base.x, base.y, za))
        for i in range(segs):
            j = (i + 1) % segs
            fs.append(addface(bm, [rings[a][i], rings[a][j], rings[a + 1][j], rings[a + 1][i]], cen))
    top = base + V3((0, 0, prof[-1][0] * 0.5 + prof[0][0] * 0.5))
    fs.append(addface(bm, rings[0], top))
    fs.append(addface(bm, rings[-1], top))
    paint(fs, col, cj)
    return fs


def rbox(mat, c, s, col=(1, 1, 1), m=2, k=0.55, noise=0.06, cj=0.05, edge_dark=0.78, rot=0.0):
    """rounded irregular stone centred at c with full size s (sx,sy,sz)."""
    bm = B(mat); setbm(bm)
    cache = {}
    sx, sy, sz = s[0] / 2, s[1] / 2, s[2] / 2
    cos_r, sin_r = math.cos(rot), math.sin(rot)
    lat = {}

    def Vt(i, j, k_):
        key = (i, j, k_)
        v = cache.get(key)
        if v is None:
            p = V3((2 * i / m - 1, 2 * j / m - 1, 2 * k_ / m - 1))
            q = V3((max(-k, min(k, p.x)), max(-k, min(k, p.y)), max(-k, min(k, p.z))))
            d = p - q
            if d.length > 1e-6:
                p = q + d.normalized() * (1 - k) * min(1.0, d.length / (1 - k) * 0.999 + 0.0) if False else q + d.normalized() * (1 - k)
            x = p.x * sx * (1 + noise * (rng.random() - .5))
            y = p.y * sy * (1 + noise * (rng.random() - .5))
            z = p.z * sz * (1 + noise * (rng.random() - .5))
            x, y = x * cos_r - y * sin_r, x * sin_r + y * cos_r
            v = bm.verts.new((c[0] + x, c[1] + y, c[2] + z))
            cache[key] = v
            lat[v] = (i, j, k_)
        return v

    cen = V3(c)
    fs = []

    def quad(a, b, c_, d):
        fs.append(addface(bm, [Vt(*a), Vt(*b), Vt(*c_), Vt(*d)], cen))

    for i in range(m):
        for j in range(m):
            quad((i, j, 0), (i + 1, j, 0), (i + 1, j + 1, 0), (i, j + 1, 0))
            quad((i, j, m), (i + 1, j, m), (i + 1, j + 1, m), (i, j + 1, m))
            quad((i, 0, j), (i + 1, 0, j), (i + 1, 0, j + 1), (i, 0, j + 1))
            quad((i, m, j), (i + 1, m, j), (i + 1, m, j + 1), (i, m, j + 1))
            quad((0, i, j), (0, i + 1, j), (0, i + 1, j + 1), (0, i, j + 1))
            quad((m, i, j), (m, i + 1, j), (m, i + 1, j + 1), (m, i, j + 1))
    cl = bm.loops.layers.float_color['Col']
    base = 1.0 + cj * 2 * (rng.random() - .5)
    for f in fs:
        for l in f.loops:
            i, j, k_ = lat[l.vert]
            # darker where the stone turns away (edges), lighter flat centre
            e = 0
            for q in (i, j, k_):
                if q == 0 or q == m: e += 1
            dk = 1.0 if e <= 1 else (edge_dark + 0.1 if e == 2 else edge_dark)
            kk = base * dk * (1 + cj * (rng.random() - .5))
            l[cl] = (col[0] * kk, col[1] * kk, col[2] * kk, 1.0)
    return fs


class Fr:
    """Wall frame: origin O on outer face plane, u along U, n along N (outward), z world up."""

    def __init__(s, O, U, N):
        s.O = V3(O); s.U = V3(U); s.N = V3(N)

    def P(s, u, n, z):
        return s.O + s.U * u + s.N * n + V3((0, 0, z))

    def box(s, mat, u0, u1, n0, n1, z0, z1, sub=None, **kw):
        a = s.P(u0, n0, z0); b = s.P(u1, n1, z1)
        if sub:
            kw['n'] = (max(1, round(abs(a.x - b.x) / sub)), max(1, round(abs(a.y - b.y) / sub)), max(1, round(abs(a.z - b.z) / sub)))
        return box(mat, min(a.x, b.x), max(a.x, b.x), min(a.y, b.y), max(a.y, b.y), min(a.z, b.z), max(a.z, b.z), **kw)

    def prism(s, mat, pts, u0, u1, **kw):
        return prism(mat, pts, s.P(u0, 0, 0), s.N, V3((0, 0, 1)), s.U, u1 - u0, **kw)

    def ext(s, n, u, z):
        """size vector for abs axes helper"""
        return s.P(u, n, z)

    def stone_at(s, mat, u, n, z, w, t, h, **kw):
        c = s.P(u, n, z)
        size = (abs(s.U.x) * w + abs(s.N.x) * t, abs(s.U.y) * w + abs(s.N.y) * t, h)
        return rbox(mat, c, size, **kw)


def free_intervals(u0, u1, z0, z1, holes):
    iv = [(u0, u1)]
    for (a, b, c, d) in holes:
        if d <= z0 or c >= z1:
            continue
        nv = []
        for (p, q) in iv:
            if b <= p or a >= q:
                nv.append((p, q)); continue
            if a > p: nv.append((p, a))
            if b < q: nv.append((b, q))
        iv = nv
    return [x for x in iv if x[1] - x[0] > 0.02]


def split_widths(total, lo, hi):
    ws = []
    t = 0.0
    while total - t > hi * 1.3:
        w = rng.uniform(lo, hi); ws.append(w); t += w
    rem = total - t
    if rem < lo * 0.7 and ws:
        ws[-1] += rem
    else:
        ws.append(rem)
    return ws


def masonry(F, mat, u0, u1, z0, z1, n0, n1, holes=(), hs=(0.17, 0.25), ws=(0.28, 0.55), pal=None, gap=0.014, m=2, k=0.55, noise=0.07, rough=0.03):
    """course masonry of individual rounded stones on frame F; stones span n0..n1 (n1 = visible face)."""
    pal = pal or [(1, 1, 1)]
    nc = max(1, round((z1 - z0) / ((hs[0] + hs[1]) / 2)))
    hh = (z1 - z0) / nc
    z = z0
    cnt = 0
    for c in range(nc):
        h = hh * rng.uniform(0.94, 1.06) if c < nc - 1 else z1 - z
        h = min(h, z1 - z)
        for (a, b) in free_intervals(u0, u1, z, z + h, holes):
            for w in split_widths(b - a, ws[0], ws[1]):
                pass
            u = a
            for w in split_widths(b - a, ws[0], ws[1]):
                t = (n1 - n0) * rng.uniform(0.8, 1.0)
                prot = rng.uniform(0.0, rough)
                col = rng.choice(pal)
                F.stone_at(mat, u + w / 2, n1 - t / 2 + prot, z + h / 2, w - gap, t, h - gap, col=col, m=m, k=k, noise=noise,
                           rot=rng.uniform(-0.04, 0.04) if False else 0.0)
                u += w; cnt += 1
        z += h
    return cnt


def nailhead(mat, x, y, z, s=0.012, col=(0.25, 0.23, 0.22)):
    bm = B(mat); setbm(bm)
    h = s * 0.3
    c = [bm.verts.new((x + dx * s / 2, y + dy * s / 2, z)) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    t = bm.verts.new((x, y, z + h))
    cen = V3((x, y, z + h / 3))
    fs = [addface(bm, [c[i], c[(i + 1) % 4], t], cen) for i in range(4)]
    paint(fs, col)


def finalize_uv(bm):
    uv = bm.loops.layers.uv['UVMap']
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            c = l.vert.co
            l[uv].uv = ((c.y, c.z), (c.x, c.z), (c.x, c.y))[ax]


def make_part(name, bms, mats, pivot=None, bevel=None, smooth_angle=math.radians(38), parent=None):
    """merge dict mat->bm into ONE object with one slot per material."""
    dst = bmesh.new()
    uvd = dst.loops.layers.uv.new('UVMap'); cold = dst.loops.layers.float_color.new('Col')
    order = [m for m in mats if m in bms]
    for mi, mn in enumerate(order):
        src = bms[mn]
        finalize_uv(src)
        uvs = src.loops.layers.uv['UVMap']; cols = src.loops.layers.float_color['Col']
        vm = {}
        for v in src.verts:
            vm[v] = dst.verts.new(v.co)
        for f in src.faces:
            nf = dst.faces.new([vm[v] for v in f.verts])
            nf.material_index = mi
            for l0, l1 in zip(f.loops, nf.loops):
                l1[uvd].uv = l0[uvs].uv
                l1[cold] = l0[cols]
        src.free()
    me = bpy.data.meshes.new(name)
    dst.to_mesh(me); dst.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for mn in order:
        ob.data.materials.append(bpy.data.materials[mn])
    if bevel:
        mod = ob.modifiers.new('Bev', 'BEVEL')
        mod.width = bevel; mod.segments = 1; mod.limit_method = 'ANGLE'; mod.angle_limit = math.radians(40)
        apply_modifiers(ob)
    shade_smooth(ob, smooth_angle)
    if pivot is not None:
        set_origin(ob, pivot)
    if parent is not None:
        set_parent(ob, parent)
    return ob
