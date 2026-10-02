"""vh_lib: core kit for the village buildings (bmesh collectors, materials, AO bake, part merge, preview)."""
import sys, os, math, random, json
sys.path.insert(0, '/shared/river/assets/blender')
from bl_common import *
import mathutils.noise as mnoise
from mathutils.bvhtree import BVHTree
from contextlib import contextmanager

rng = random.Random(1)
CUR = {}
V3 = Vector
TEXDIR = '/shared/river/assets/tex/'
XF = []          # stack of Matrix transforms for registered points (windows / chimneys)
REG = {'windows': [], 'chimneys': [], 'colliders': []}

# ------------------------------------------------------------------ materials
# name, color, rough, metal, tex, tile(m), extra kw
MATDEF = [
    ('stone_foundation', '#ffffff', 0.95, 0, 'pbr_stone_fireplace', 1.0, {}),
    ('stone_wall', '#ffffff', 0.95, 0, 'pbr_stone_fireplace', 1.0, {}),
    ('stone_chimney', '#f4efe6', 0.95, 0, 'pbr_stone_fireplace', 1.0, {}),
    ('mortar', '#a9a293', 1.0, 0, '', 1.0, {}),
    ('brick', '#a4553a', 0.9, 0, '', 1.0, {}),
    ('plaster', '#efe6d2', 0.96, 0, 'pbr_plaster', 1.0, {}),
    ('siding_wood', '#bebedb', 0.88, 0, 'pbr_wood_pine', 0.6, {}),
    ('siding_dark', '#95bcff', 0.9, 0, 'pbr_wood_oak', 0.5, {}),
    ('timber_dark', '#d8c8b8', 0.82, 0, 'pbr_wood_dark', 0.6, {}),
    ('timber_beam', '#b8c0f0', 0.78, 0, 'pbr_wood_oak', 0.5, {}),
    ('roof_shingle', '#a8bcf0', 0.92, 0, 'pbr_wood_oak', 0.5, {}),
    ('roof_slate', '#6d7279', 0.7, 0, '', 1.0, {}),
    ('roof_deck', '#e0d0c0', 0.9, 0, 'pbr_wood_dark', 0.6, {}),
    ('zinc', '#a9afb0', 0.42, 0.85, '', 1.0, {}),
    ('copper', '#c98a5d', 0.4, 0.9, 'pbr_brass_copper', 0.3, {}),
    ('verdigris', '#6f9d8a', 0.55, 0.5, '', 1.0, {}),
    ('brass', '#c29a45', 0.32, 1.0, '', 1.0, {}),
    ('iron', '#3a3836', 0.55, 0.8, 'pbr_iron', 0.4, {}),
    ('glass', '#c5dde2', 0.05, 0.0, '', 1.0, dict(alpha=0.3)),
    ('window_glow', '#2a1f14', 0.6, 0.0, '', 1.0, {}),
    ('paint_trim', '#e9e4d3', 0.55, 0, '', 1.0, {}),
    ('paint_shutter', '#4d6a50', 0.6, 0, '', 1.0, {}),
    ('paint_door', '#7d3329', 0.55, 0, '', 1.0, {}),
    ('door_blue', '#35557a', 0.55, 0, '', 1.0, {}),
    ('door_ochre', '#b8872f', 0.55, 0, '', 1.0, {}),
    ('door_wood', '#b8c0f0', 0.65, 0, 'pbr_wood_oak', 0.5, {}),
    ('deck_planks', '#c0c8f0', 0.78, 0, 'pbr_wood_oak', 0.5, {}),
    ('soil', '#3b2e22', 1.0, 0, '', 1.0, {}),
    ('foliage', '#4f7a36', 0.8, 0, '', 1.0, {}),
    ('flowers', '#ffffff', 0.7, 0, '', 1.0, {}),
    ('hay', '#d2b25a', 0.95, 0, '', 1.0, {}),
    ('sack', '#bfa882', 0.98, 0, 'pbr_fabric_burlap', 0.25, {}),
    ('cloth', '#ffffff', 0.9, 0, 'pbr_fabric_linen', 0.25, {}),
    ('wicker', '#c9a56a', 0.85, 0, 'pbr_wicker', 0.2, {}),
    ('barrel_wood', '#c8d0ff', 0.8, 0, 'pbr_wood_oak', 0.5, {}),
    ('leather', '#6a4328', 0.8, 0, 'pbr_leather', 0.3, {}),
    ('soot', '#171412', 1.0, 0, '', 1.0, {}),
    ('coal', '#1b1917', 0.9, 0, '', 1.0, {}),
    ('forge_glow', '#ff6a20', 0.8, 0, '', 1.0, dict(emit='#ff4a10', emit_strength=3.5)),
    ('lantern_glow', '#ffd9a0', 0.6, 0, '', 1.0, dict(emit='#ffb55a', emit_strength=1.5)),
    ('endgrain', '#c8a06a', 0.85, 0, '', 1.0, {}),
    ('bark', '#5a4330', 0.95, 0, '', 1.0, {}),
    ('dirt', '#6b5a43', 1.0, 0, '', 1.0, {}),
    ('rope', '#b79d6c', 0.95, 0, '', 1.0, {}),
    ('bread', '#c98a3f', 0.9, 0, '', 1.0, {}),
    ('canvas', '#e8dcc0', 0.95, 0, 'pbr_fabric_linen', 0.25, {}),
    ('chalk', '#f2f0e8', 0.9, 0, '', 1.0, {}),
]
MAT = {}
TILES = {}
MATNAMES = []
NOAO = {'glass'}
for n, c, r, m, tx, tile, kw in MATDEF:
    MAT[n] = make_mat(n, c, rough=r, metal=m, tex=tx, **kw)
    TILES[n] = tile
    MATNAMES.append(n)
# vertical-board materials use swapped UV so grain follows the boards
SWAP = {'siding_dark'}

# bevel width per material (applied per material before merge)
BEV = {'timber_beam': 0.01, 'paint_door': 0.004, 'door_blue': 0.004, 'door_ochre': 0.004, 'door_wood': 0.004}


# ------------------------------------------------------------------ bmesh collectors
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


@contextmanager
def placed(loc=(0, 0, 0), rotz=0.0):
    """geometry created inside is transformed (rotate about Z then translate)."""
    marks = {m: len(bm.verts) for m, bm in CUR.items()}
    M = Matrix.Translation(loc) @ Matrix.Rotation(rotz, 4, 'Z')
    XF.append(M)
    try:
        yield
    finally:
        XF.pop()
        for m, bm in CUR.items():
            bm.verts.ensure_lookup_table()
            for v in bm.verts[marks.get(m, 0):]:
                v.co = M @ v.co


def xf_point(p):
    q = V3(p)
    for M in reversed(XF):
        q = M @ q
    return q


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
                k = 1.0 + cj * nz3(l.vert.co, freq, seed)
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


def obox(mat, O, X, Y, Z, lx, ly, lz, col=(1, 1, 1), cj=0.0, skip=()):
    O = V3(O); X = V3(X).normalized(); Y = V3(Y).normalized(); Z = V3(Z).normalized()
    pts = []
    for z in (0, 1):
        for (a, b) in ((0, 0), (1, 0), (1, 1), (0, 1)):
            pts.append(O + X * lx * a + Y * ly * b + Z * lz * z)
    return hexa(mat, pts, col, cj, skip)


def prism(mat, pts, O, A, Bv, U, L, col=(1, 1, 1), s1=1.0, cj=0.0, cfun=None, caps=(True, True), recalc=False):
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
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=fs)
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


def lathe(mat, base, prof, segs=12, col=(1, 1, 1), cj=0.0, cap_bottom=True):
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
    if cap_bottom: fs.append(addface(bm, rings[0], top))
    fs.append(addface(bm, rings[-1], top))
    paint(fs, col, cj)
    return fs


def blob(mat, c, r, col=(1, 1, 1), cj=0.0, rows=3, segs=6, squash=1.0, jit=0.2):
    """small low-poly sphere (leaf clump / flower head / hay tuft)."""
    bm = B(mat); setbm(bm)
    c = V3(c)
    rings = [[bm.verts.new(c + V3((0, 0, -r * squash)))]]
    for ri in range(1, rows):
        a = -math.pi / 2 + math.pi * ri / rows
        rr = r * math.cos(a)
        z = r * math.sin(a) * squash
        rings.append([bm.verts.new(c + V3((rr * math.cos(2 * math.pi * i / segs) * (1 + jit * (rng.random() - .5)),
                                            rr * math.sin(2 * math.pi * i / segs) * (1 + jit * (rng.random() - .5)), z))) for i in range(segs)])
    rings.append([bm.verts.new(c + V3((0, 0, r * squash)))])
    fs = []
    for a in range(len(rings) - 1):
        A, Bq = rings[a], rings[a + 1]
        for i in range(segs):
            j = (i + 1) % segs
            if len(A) == 1:
                fs.append(addface(bm, [A[0], Bq[j], Bq[i]], c))
            elif len(Bq) == 1:
                fs.append(addface(bm, [A[i], A[j], Bq[0]], c))
            else:
                fs.append(addface(bm, [A[i], A[j], Bq[j], Bq[i]], c))
    paint(fs, col, cj)
    return fs


def rbox(mat, c, s, col=(1, 1, 1), m=2, k=0.55, noise=0.06, cj=0.05, edge_dark=0.78, rot=0.0, skip=()):
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
                p = q + d.normalized() * (1 - k)
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
            if 'bottom' not in skip: quad((i, j, 0), (i + 1, j, 0), (i + 1, j + 1, 0), (i, j + 1, 0))
            if 'top' not in skip: quad((i, j, m), (i + 1, j, m), (i + 1, j + 1, m), (i, j + 1, m))
            if 'front' not in skip: quad((i, 0, j), (i + 1, 0, j), (i + 1, 0, j + 1), (i, 0, j + 1))
            if 'back' not in skip: quad((i, m, j), (i + 1, m, j), (i + 1, m, j + 1), (i, m, j + 1))
            if 'left' not in skip: quad((0, i, j), (0, i + 1, j), (0, i + 1, j + 1), (0, i, j + 1))
            if 'right' not in skip: quad((m, i, j), (m, i + 1, j), (m, i + 1, j + 1), (m, i, j + 1))
    cl = bm.loops.layers.float_color['Col']
    base = 1.0 + cj * 2 * (rng.random() - .5)
    for f in fs:
        for l in f.loops:
            i, j, k_ = lat[l.vert]
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

    def shifted(s, n):
        return Fr(s.O + s.N * n, s.U, s.N)

    def box(s, mat, u0, u1, n0, n1, z0, z1, sub=None, **kw):
        a = s.P(u0, n0, z0); b = s.P(u1, n1, z1)
        if sub:
            kw['n'] = (max(1, round(abs(a.x - b.x) / sub)), max(1, round(abs(a.y - b.y) / sub)), max(1, round(abs(a.z - b.z) / sub)))
        if abs(s.N.y) > 0.5:
            back = 'back' if s.N.y < 0 else 'front'
        else:
            back = 'left' if s.N.x > 0 else 'right'
        sk = tuple(kw.get('skip', ()))
        if back not in sk and not kw.pop('keep_back', False):
            sk = sk + (back,)
        kw['skip'] = sk
        return box(mat, min(a.x, b.x), max(a.x, b.x), min(a.y, b.y), max(a.y, b.y), min(a.z, b.z), max(a.z, b.z), **kw)

    def prism(s, mat, pts, u0, u1, **kw):
        """pts = (n, z) profile extruded along u."""
        return prism(mat, pts, s.P(u0, 0, 0), s.N, V3((0, 0, 1)), s.U, u1 - u0, **kw)

    def poly(s, mat, pts_uz, n0, n1, **kw):
        """polygon given in (u, z), extruded along n from n0 to n1 (closed solid)."""
        return prism(mat, pts_uz, s.O + s.N * n0, s.U, V3((0, 0, 1)), s.N, n1 - n0, recalc=True, **kw)

    def stone_at(s, mat, u, n, z, w, t, h, **kw):
        c = s.P(u, n, z)
        size = (abs(s.U.x) * w + abs(s.N.x) * t, abs(s.U.y) * w + abs(s.N.y) * t, h)
        if abs(s.N.y) > 0.5:
            back = 'back' if s.N.y < 0 else 'front'
        else:
            back = 'left' if s.N.x > 0 else 'right'
        kw.setdefault('skip', (back, 'bottom'))
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


def free_z(ua, ub, z0, z1, holes):
    """z intervals of column [ua,ub] not covered by holes."""
    iv = [(z0, z1)]
    for (a, b, c, d) in holes:
        if b <= ua or a >= ub:
            continue
        nv = []
        for (p, q) in iv:
            if d <= p or c >= q:
                nv.append((p, q)); continue
            if c > p: nv.append((p, c))
            if d < q: nv.append((d, q))
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


def masonry(F, mat, u0, u1, z0, z1, n0, n1, holes=(), hs=(0.17, 0.25), ws=(0.28, 0.55), pal=None, gap=0.014, m=2, k=0.55,
            noise=0.07, rough=0.03, rangefn=None, dk=1.0):
    pal = pal or [(1, 1, 1)]
    nc = max(1, round((z1 - z0) / ((hs[0] + hs[1]) / 2)))
    hh = (z1 - z0) / nc
    z = z0
    cnt = 0
    for c in range(nc):
        h = hh * rng.uniform(0.94, 1.06) if c < nc - 1 else z1 - z
        h = min(h, z1 - z)
        ra, rb = rangefn(z, z + h) if rangefn else (u0, u1)
        for (a, b) in free_intervals(ra, rb, z, z + h, holes):
            u = a
            for w in split_widths(b - a, ws[0], ws[1]):
                t = (n1 - n0) * rng.uniform(0.8, 1.0)
                prot = rng.uniform(0.0, rough)
                col = rng.choice(pal)
                F.stone_at(mat, u + w / 2, n1 - t / 2 + prot, z + h / 2, w - gap, t, h - gap, col=(col[0] * dk, col[1] * dk, col[2] * dk), m=m, k=k, noise=noise)
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


def tint(r=1, g=1, b=1, j=0.08):
    k = 1 + rng.uniform(-j, j)
    return (r * k * rng.uniform(0.97, 1.03), g * k * rng.uniform(0.97, 1.03), b * k * rng.uniform(0.96, 1.04))


# ------------------------------------------------------------------ registration of meta points
def reg_window(F, uc, zc):
    p = xf_point(F.P(uc, 0.0, zc))
    REG['windows'].append({'x': round(p.x, 3), 'y': round(p.z, 3), 'z': round(-p.y, 3)})


def reg_chimney(x, y, z):
    p = xf_point((x, y, z))
    REG['chimneys'].append({'x': round(p.x, 3), 'y': round(p.z, 3), 'z': round(-p.y, 3)})
    return p


# ------------------------------------------------------------------ AO / weathering
def _hemi_dirs(n):
    out = []
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        r = math.sqrt((i + 0.5) / n)
        th = i * ga
        out.append((r * math.cos(th), r * math.sin(th), math.sqrt(max(0.0, 1 - r * r))))
    return out


def bake_vcol(bms, rays=8, maxd=1.1, strength=0.7, grime=0.32, ground_fade=0.45, cull=False):
    verts, polys = [], []
    for m, bm in bms.items():
        if m in NOAO:
            continue
        bm.verts.index_update()
        base = len(verts)
        verts.extend([tuple(v.co) for v in bm.verts])
        for f in bm.faces:
            polys.append(tuple(base + v.index for v in f.verts))
    tree = BVHTree.FromPolygons(verts, polys)
    dirs = _hemi_dirs(rays)
    cache = {}
    ndel = 0
    for m, bm in bms.items():
        if m in ('forge_glow', 'lantern_glow'):
            continue
        cl = bm.loops.layers.float_color['Col']
        bm.faces.ensure_lookup_table()
        dead = []
        for f in bm.faces:
            n = f.normal
            if n.length < 0.5:
                continue
            nk = (round(n.x, 1), round(n.y, 1), round(n.z, 1))
            allclose = True
            for l in f.loops:
                co = l.vert.co
                key = (round(co.x, 2), round(co.y, 2), round(co.z, 2), nk)
                r = cache.get(key)
                if r is None:
                    if m in NOAO or m == 'window_glow':
                        r = (1.0, 0.0)
                    else:
                        t = V3((0, 0, 1)) if abs(n.z) < 0.9 else V3((1, 0, 0))
                        tx = n.cross(t).normalized(); ty = n.cross(tx)
                        o = co + n * 0.02
                        ang = ((hash(key) & 1023) / 1023.0) * 6.283
                        ca, sa = math.cos(ang), math.sin(ang)
                        occ = 0.0
                        close = 0
                        for (dx, dy, dz) in dirs:
                            ex, ey = dx * ca - dy * sa, dx * sa + dy * ca
                            d = tx * ex + ty * ey + n * dz
                            hit = tree.ray_cast(o, d, maxd)
                            if hit[0] is not None:
                                occ += 1.0 - (hit[3] / maxd) * 0.6
                                if hit[3] < 0.06:
                                    close += 1
                        occ /= len(dirs)
                        a = 1.0 - strength * occ
                        z = max(co.z, 0.0)
                        a *= 1.0 - grime * math.exp(-z / ground_fade)
                        a *= 1.0 + 0.07 * nz3(co, 0.7, 3.3)
                        r = (a, close / len(dirs))
                    cache[key] = r
                c = l[cl]
                a = r[0]
                l[cl] = (c[0] * a, c[1] * a, c[2] * a, 1.0)
                if r[1] < 0.74:
                    allclose = False
            if cull and allclose and m not in NOAO and m not in ('window_glow', 'soot'):
                dead.append(f)
        if dead:
            bmesh.ops.delete(bm, geom=dead, context='FACES_ONLY')
            ndel += len(dead)
    print('culled hidden faces:', ndel)


def moss_roofs(bms, mats=('roof_shingle', 'roof_deck')):
    for m in mats:
        bm = bms.get(m)
        if not bm: continue
        cl = bm.loops.layers.float_color['Col']
        for f in bm.faces:
            for l in f.loops:
                co = l.vert.co
                v = nz3(co, 0.9, 7.1) * 0.5 + 0.5
                v2 = nz3(co, 3.7, 1.3) * 0.5 + 0.5
                mo = max(0.0, v - 0.62) * 2.2 * v2
                c = l[cl]
                l[cl] = (c[0] * (1 - 0.35 * mo), c[1] * (1 + 0.05 * mo), c[2] * (1 - 0.5 * mo), 1.0)


# ------------------------------------------------------------------ UV + part merge
def finalize_uv(bm, mat):
    tile = TILES.get(mat, 1.0)
    swap = mat in SWAP
    uv = bm.loops.layers.uv['UVMap']
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            c = l.vert.co
            u, v = ((c.y, c.z), (c.x, c.z), (c.x, c.y))[ax]
            if swap: u, v = v, u
            l[uv].uv = (u / tile, v / tile)


def _bevel_bm(src, w):
    me = bpy.data.meshes.new('_bv')
    src.to_mesh(me)
    ob = bpy.data.objects.new('_bv', me)
    bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new('Bev', 'BEVEL')
    mod.width = w; mod.segments = 1; mod.limit_method = 'ANGLE'; mod.angle_limit = math.radians(40)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me2 = bpy.data.meshes.new_from_object(ev)
    nb = bmesh.new(); nb.from_mesh(me2)
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me); bpy.data.meshes.remove(me2)
    return nb


def make_part(name, bms, mats=None, bevel=True, smooth_angle=math.radians(38), post_bake=True, bake=True, **bakekw):
    order = [m for m in (mats or MATNAMES) if m in bms]
    for m in bms:
        if m not in order:
            order.append(m)
    if bake:
        bake_vcol(bms, **bakekw)
        moss_roofs(bms)
    dst = bmesh.new()
    uvd = dst.loops.layers.uv.new('UVMap'); cold = dst.loops.layers.float_color.new('Col')
    for mi, mn in enumerate(order):
        src = bms[mn]
        if bevel and BEV.get(mn, 0) > 0:
            src.normal_update()
            nb = _bevel_bm(src, BEV[mn])
            src.free(); src = nb
            # bevel output loses the face-normal-based colours? attributes are interpolated, fine
        for f in src.faces:
            f.normal_update()
        finalize_uv(src, mn)
        uvs = src.loops.layers.uv['UVMap']; cols = src.loops.layers.float_color['Col']
        vm = {}
        for v in src.verts:
            vm[v] = dst.verts.new(v.co)
        for f in src.faces:
            try:
                nf = dst.faces.new([vm[v] for v in f.verts])
            except ValueError:
                continue
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
    shade_smooth(ob, smooth_angle)
    return ob


def smoke_part(name, p):
    """tiny 8-vertex box with origin at p (world position)."""
    bm = bmesh.new()
    s = 0.05
    vs = [bm.verts.new((x * s, y * s, z * s)) for z in (0, 1) for (x, y) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in q])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = p
    ob.data.materials.append(MAT['soot'])
    bpy.context.view_layer.update()
    return ob


# ------------------------------------------------------------------ preview
def preview_mats():
    for m in bpy.data.materials:
        if not m.use_nodes: continue
        nt = m.node_tree
        b = nt.nodes.get('Principled BSDF')
        if not b: continue
        if m.name == 'glass':
            b.inputs['Alpha'].default_value = 0.25
            continue
        if m.name in ('forge_glow', 'lantern_glow'):
            continue
        ca = nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'Col'
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs[0].default_value = 1.0
        mix.inputs[6].default_value = tuple(m['rgb']) + (1,)
        nt.links.new(ca.outputs['Color'], mix.inputs[7])
        last = mix
        tex = m.get('tex', '')
        if tex and os.path.exists(TEXDIR + tex + '.jpg'):
            ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(TEXDIR + tex + '.jpg')
            mix2 = nt.nodes.new('ShaderNodeMix'); mix2.data_type = 'RGBA'; mix2.blend_type = 'MULTIPLY'
            mix2.inputs[0].default_value = 1.0
            nt.links.new(mix.outputs[2], mix2.inputs[6]); nt.links.new(ti.outputs['Color'], mix2.inputs[7])
            last = mix2
            if os.path.exists(TEXDIR + tex + '_n.jpg'):
                tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = bpy.data.images.load(TEXDIR + tex + '_n.jpg')
                tn.image.colorspace_settings.name = 'Non-Color'
                nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.6
                nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
        nt.links.new(last.outputs[2], b.inputs['Base Color'])


def render_views(objs_unused, views, prefix, res=(720, 480), samples=32, extra_lights=()):
    sc = bpy.context.scene
    preview_mats()
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.55, 0.68, 0.85, 1); bg.inputs[1].default_value = 1.0
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 4.0; sun.angle = 0.05
    so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(52), 0, math.radians(-38)); sc.collection.objects.link(so)
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    g = bpy.context.object; g.data.materials.append(make_mat('_gm', '#62763f', rough=0.95))
    bpy.data.materials['_gm'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.13, 0.21, 0.06, 1)
    # ground a bit lower than z=0 near the plinth is not needed: plinth extends below
    for name, (cl, tg, ln) in views.items():
        cam = bpy.data.cameras.new('cam'); cam.lens = ln; cam.clip_end = 300; cam.clip_start = 0.05
        co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co)
        co.location = cl
        co.rotation_euler = (Vector(tg) - Vector(cl)).to_track_quat('-Z', 'Y').to_euler()
        sc.camera = co
        sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.device = 'CPU'
        try:
            sc.cycles.use_denoising = True
        except Exception:
            pass
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = '/shared/river/assets/preview/vh_%s_%s.png' % (prefix, name)
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(co)


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)
