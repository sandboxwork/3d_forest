"""Food, plants, herbs, flowers.  bm builders return bmesh with 'Col' colours; placers put them into accumulators."""
from kt_lib import *
from kt_ware import G


def colorize(bm, fn, name='Col'):
    cl = bm.loops.layers.float_color.get(name) or bm.loops.layers.float_color.new(name)
    for f in bm.faces:
        for l in f.loops:
            c = fn(l.vert.co)
            l[cl] = (c[0], c[1], c[2], 1.0)
    return bm


def noise_push(bm, amp, s=14.0, seed=0, ax=(1, 1, 1)):
    for v in bm.verts:
        n = fbm(v.co.x, v.co.y, v.co.z, s, seed, 2)
        d = v.co.normalized() if v.co.length > 1e-6 else Vector((0, 0, 1))
        v.co += Vector((d.x * ax[0], d.y * ax[1], d.z * ax[2])) * (amp * n)
    return bm


def place(mat, bm, pos, rot=None, scale=1.0, free=True, col=(1, 1, 1), flat=False, skip_down=False):
    Mx = xf(pos, rot) @ Matrix.Diagonal((scale, scale, scale, 1.0)) if not isinstance(scale, tuple) else xf(pos, rot) @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
    put(mat, bm, Mx, col, flat=flat, skip_down=skip_down)
    if free:
        bm.free()


# ---------------------------------------------------------------- fruit & veg builders (local, base at z=0)
APPLE = [(0.001, 0.07), (0.16, 0.03), (0.42, 0.0), (0.76, 0.1), (0.97, 0.38), (1.0, 0.62), (0.9, 0.86), (0.62, 1.01), (0.34, 1.0), (0.14, 0.86), (0.001, 0.9)]
PEAR = [(0.001, 0.04), (0.2, 0.0), (0.55, 0.02), (0.82, 0.18), (0.88, 0.4), (0.7, 0.62), (0.48, 0.82), (0.36, 1.05), (0.34, 1.3), (0.28, 1.5), (0.2, 1.56), (0.001, 1.52)]
EGG = [(0.001, 0.0), (0.45, 0.04), (0.75, 0.2), (0.97, 0.5), (1.0, 0.75), (0.88, 1.1), (0.6, 1.5), (0.3, 1.78), (0.001, 1.85)]
TOMATO = [(0.001, 0.08), (0.4, 0.0), (0.85, 0.12), (1.0, 0.4), (0.92, 0.7), (0.55, 0.82), (0.2, 0.74), (0.001, 0.7)]
ONION = [(0.001, 0.0), (0.2, 0.02), (0.68, 0.1), (0.98, 0.42), (1.0, 0.7), (0.78, 1.0), (0.4, 1.18), (0.16, 1.34), (0.05, 1.5), (0.001, 1.56)]
LEMON = [(0.001, 0.0), (0.12, 0.02), (0.5, 0.16), (0.9, 0.42), (1.0, 0.6), (0.9, 0.78), (0.5, 1.04), (0.12, 1.2), (0.001, 1.24)]


def lathe_solid(prof, r, seg=10, sq=(1, 1, 1), seed=0, noise=0.0, colfn=None, nscale=9.0):
    bm = lathe_bm([(a * r, b * r) for a, b in prof], seg, cap=False)
    for v in bm.verts:
        v.co.x *= sq[0]; v.co.y *= sq[1]; v.co.z *= sq[2]
    if noise:
        for v in bm.verts:
            n = fbm(v.co.x, v.co.y, v.co.z, nscale / r * 0.1, seed, 2)
            ang = math.atan2(v.co.y, v.co.x)
            d = Vector((v.co.x, v.co.y, 0)) if math.hypot(v.co.x, v.co.y) > 1e-6 else Vector((0, 0, 0))
            if d.length > 0:
                v.co += d.normalized() * (noise * r * n)
            v.co.z += noise * r * 0.5 * n
    if colfn:
        colorize(bm, colfn)
    return bm


def apple_bm(seed=0, r=0.037, kind=None, seg=10):
    rr = random.Random(seed)
    kind = kind if kind is not None else rr.choice(['red', 'red', 'deep', 'green', 'russet', 'red'])
    pal = {'red': ((0.55, 0.05, 0.035), (0.78, 0.55, 0.12)), 'deep': ((0.36, 0.03, 0.03), (0.6, 0.18, 0.05)),
           'green': ((0.38, 0.52, 0.08), (0.62, 0.62, 0.12)), 'russet': ((0.5, 0.2, 0.05), (0.62, 0.45, 0.1))}[kind]
    ox, oy = rr.uniform(0, 50), rr.uniform(0, 50)

    def cf(p):
        a = math.atan2(p.y, p.x)
        t = 0.5 + 0.5 * fbm(math.cos(a) * 3 + ox, math.sin(a) * 3 + oy, p.z * 30, 1.0, seed, 2) * 1.4
        t = max(0, min(1, t))
        tt = 0.2 + 0.8 * t
        sh = 0.75 + 0.5 * (p.z / (r * 1.0))
        return tuple(max(0.0, (pal[0][i] * tt + pal[1][i] * (1 - tt)) * min(1.1, sh)) for i in range(3))
    sc = (rr.uniform(0.94, 1.06), rr.uniform(0.94, 1.06), rr.uniform(0.9, 1.0))
    bm = lathe_solid(APPLE, r, seg, sc, seed, 0.035, cf)
    # stem
    st = bmesh.new()
    sp = [Vector((0, 0, r * 0.85)), Vector((0.002, 0, r * 1.1)), Vector((0.006, 0.001, r * 1.28))]
    stem = bmesh.new()
    pr = [(0.0017 * math.cos(TAU * k / 4), 0.0017 * math.sin(TAU * k / 4)) for k in range(4)]
    for i, p in enumerate(sp):
        pass
    # inline tiny tube
    rings = []
    for i, p in enumerate(sp):
        rings.append([bm.verts.new(p + Vector((0.0017 * math.cos(TAU * k / 4), 0.0017 * math.sin(TAU * k / 4), 0))) for k in range(4)])
    cl = bm.loops.layers.float_color['Col']
    for i in range(len(rings) - 1):
        for k in range(4):
            f = bm.faces.new([rings[i][k], rings[i][(k + 1) % 4], rings[i + 1][(k + 1) % 4], rings[i + 1][k]])
            for l in f.loops:
                l[cl] = (0.18, 0.1, 0.04, 1)
    st.free(); stem.free()
    return bm


def pear_bm(seed=0, r=0.03):
    rr = random.Random(seed)

    def cf(p):
        t = 0.5 + 0.5 * fbm(p.x * 40, p.y * 40, p.z * 40, 1, seed, 2)
        return (0.62 + 0.15 * t, 0.62 + 0.1 * t, 0.12 + 0.06 * t)
    return lathe_solid(PEAR, r, 10, (1, 1, 1), seed, 0.03, cf)


def egg_bm(r=0.021, col=(0.9, 0.78, 0.6), seed=0):
    def cf(p):
        k = 1 + 0.06 * fbm(p.x * 90, p.y * 90, p.z * 90, 1, seed, 2)
        return (col[0] * k, col[1] * k, col[2] * k)
    return lathe_solid(EGG, r, 10, (1, 1, 1), seed, 0.0, cf)


def onion_bm(seed=0, r=0.032, col=(0.42, 0.2, 0.06)):
    def cf(p):
        a = math.atan2(p.y, p.x)
        k = 1 + 0.18 * fbm(math.cos(a) * 4, math.sin(a) * 4, p.z * 8, 1.0, seed, 2)
        up = max(0, p.z / r - 0.9)
        c = (col[0] * k, col[1] * k, col[2] * k)
        return mixc(c, (0.5, 0.38, 0.2), min(1, up * 1.5))
    return lathe_solid(ONION, r, 10, (1, 1, 1), seed, 0.02, cf)


def tomato_bm(seed=0, r=0.035):
    def cf(p):
        k = 1 + 0.1 * fbm(p.x * 30, p.y * 30, p.z * 30, 1, seed, 2)
        return (0.7 * k, 0.07 * k, 0.04 * k)
    bm = lathe_solid(TOMATO, r, 10, (1, 1, 0.9), seed, 0.02, cf)
    cl = bm.loops.layers.float_color['Col']
    for i in range(5):
        a = TAU * i / 5
        c0 = Vector((0, 0, r * 0.72))
        tip = Vector((math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, r * 0.78))
        s1 = Vector((math.cos(a + 0.35) * r * 0.1, math.sin(a + 0.35) * r * 0.1, r * 0.76))
        s2 = Vector((math.cos(a - 0.35) * r * 0.1, math.sin(a - 0.35) * r * 0.1, r * 0.76))
        f = bm.faces.new([bm.verts.new(s1), bm.verts.new(tip), bm.verts.new(s2)])
        for l in f.loops:
            l[cl] = (0.2, 0.4, 0.08, 1)
    return bm


def potato_bm(seed=0, r=0.035):
    rr = random.Random(seed)
    bm = sphere_bm(r, 10, 7, (rr.uniform(1.1, 1.4), rr.uniform(0.85, 1.0), rr.uniform(0.75, 0.9)))
    for v in bm.verts:
        n = fbm(v.co.x * 30 + seed, v.co.y * 30, v.co.z * 30, 1, seed, 2)
        v.co *= 1 + 0.1 * n
    colorize(bm, lambda p: tuple(c * (1 + 0.14 * fbm(p.x * 60, p.y * 60, p.z * 60, 1, seed + 3, 2)) for c in (0.34, 0.22, 0.11)))
    bm.normal_update()
    return bm


def lemon_bm(seed=0, r=0.033):
    return lathe_solid(LEMON, r, 10, (1, 1, 1), seed, 0.015, lambda p: (0.85, 0.72 + 0.05 * fbm(p.x * 50, p.y * 50, p.z * 50, 1, seed, 1), 0.08))


def carrot_bm(L=0.16, r=0.017, seed=0, tops=True):
    rr = random.Random(seed)
    pts = [Vector((0, 0, 0)), Vector((0.004 * rr.uniform(-1, 1), 0, L * 0.5)), Vector((0.008 * rr.uniform(-1, 1), 0.003, L))]
    bm = bmesh.new()
    cl = bm.loops.layers.float_color.new('Col')
    n = 8
    rings = []
    for i in range(n + 1):
        t = i / n
        c = Vector((0.007 * math.sin(t * 3 + seed), 0.004 * math.cos(t * 4 + seed), t * L))
        rad = r * (0.18 + 0.82 * (1 - t) ** 0.55) * (1.0 if t < 0.97 else 0.7)
        rad *= 1 + 0.06 * math.sin(t * 40 + seed)
        rings.append([bm.verts.new(c + Vector((rad * math.cos(TAU * k / 7), rad * math.sin(TAU * k / 7), 0))) for k in range(7)])
    for i in range(n):
        for k in range(7):
            f = bm.faces.new([rings[i][k], rings[i][(k + 1) % 7], rings[i + 1][(k + 1) % 7], rings[i + 1][k]])
            for l in f.loops:
                kk = 1 + 0.1 * fbm(l.vert.co.x * 80, l.vert.co.y * 80, l.vert.co.z * 80, 1, seed, 1)
                l[cl] = (0.66 * kk, 0.2 * kk, 0.025 * kk, 1)
    f = bm.faces.new(rings[-1][::-1])
    for l in f.loops:
        l[cl] = (0.7, 0.24, 0.04, 1)
    if tops:
        for k in range(4):
            a = TAU * k / 4 + seed
            sp = [rings[-1][0].co + Vector((0, 0, 0.0)), rings[-1][0].co + Vector((0.012 * math.cos(a), 0.012 * math.sin(a), 0.045)), rings[-1][0].co + Vector((0.025 * math.cos(a), 0.025 * math.sin(a), 0.075))]
            r2 = []
            for j, p in enumerate(sp):
                w = 0.0035 * (1 - j / 3)
                r2.append((bm.verts.new(p + Vector((-w * math.sin(a), w * math.cos(a), 0))), bm.verts.new(p + Vector((w * math.sin(a), -w * math.cos(a), 0)))))
            for j in range(2):
                f = bm.faces.new([r2[j][0], r2[j][1], r2[j + 1][1], r2[j + 1][0]])
                for l in f.loops:
                    l[cl] = (0.25, 0.45, 0.12, 1)
    bm.normal_update()
    return bm


def garlic_bm(seed=0, r=0.026):
    def prof(r_):
        return [(0.001, 0.0), (r_ * 0.2, 0.0), (r_ * 0.6, 0.06 * r_), (r_ * 0.98, 0.4 * r_), (r_ * 1.0, 0.7 * r_), (r_ * 0.8, 1.05 * r_), (r_ * 0.4, 1.4 * r_), (r_ * 0.12, 1.75 * r_), (0.001, 1.85 * r_)]
    bm = lathe_bm(prof(r), 14, cap=False)
    for v in bm.verts:   # clove lobes
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.09 * math.cos(6 * a) * min(1, v.co.z / (r * 0.6))
        v.co.x *= k; v.co.y *= k
    colorize(bm, lambda p: mixc((0.88, 0.84, 0.76), (0.62, 0.48, 0.4), 0.5 + 0.5 * math.cos(6 * math.atan2(p.y, p.x)) * 0.8) if p.z < r * 1.4 else (0.78, 0.7, 0.58))
    return bm


def mushroom_bm(r=0.03, seed=0):
    bm = lathe_bm([(0.001, 0), (r * 0.28, 0), (r * 0.3, r * 0.5), (r * 0.36, r * 1.0), (r * 0.9, r * 1.1), (r * 1.2, r * 1.3), (r * 1.15, r * 1.6), (r * 0.6, r * 1.95), (0.001, r * 2.0)], 10, cap=False)
    colorize(bm, lambda p: (0.8, 0.72, 0.58) if p.z > r * 1.05 else (0.85, 0.82, 0.74))
    return bm


# ---------------------------------------------------------------- sliced things
def slice_disc(pos, r, h, col, core, rot=None, seg=10):
    """sliced vegetable round (carrot, cucumber, onion ring)"""
    Mx = xf(pos, rot)
    prof = [(0.001, 0.0), (r, 0.0), (r, h), (r * 0.55, h), (r * 0.54, h), (0.001, h)]
    bm = lathe_bm([(0.001, h), (r * 0.62, h), (r * 0.64, h), (r, h - 0.0003), (r, 0.0), (0.001, 0.0)], seg, cap=False)
    colorize(bm, lambda p: core if (p.z > h * 0.9 and math.hypot(p.x, p.y) < r * 0.7) else col)
    put('food_vc', bm, Mx)
    bm.free()


def onion_ring(pos, r, rot=None):
    Mx = xf(pos, rot)
    torus('food_vc', None, r, 0.0016, plane='xy', seg=14, rseg=5, M=Mx, col=(0.9, 0.82, 0.78))


# ---------------------------------------------------------------- bread
def loaf_bm(L=0.28, W=0.12, H=0.085, seed=0, score=3, kind='batard', res=0.0075):
    """metaball body (capsule + balls) -> decimate -> noise displacement (crust) -> scored slashes with 'ears' + flour colour"""
    if kind == 'boule':
        els = [(0, 0, H * 0.45, W * 0.5, 'BALL'), (W * 0.18, 0, H * 0.4, W * 0.4, 'BALL'), (-W * 0.18, W * 0.05, H * 0.4, W * 0.38, 'BALL')]
        bm = metaball_bm(els, res=res, threshold=0.5)
    else:
        els = [(-L * 0.28, 0, H * 0.42, W * 0.42, 'BALL'), (0, 0, H * 0.5, W * 0.5, 'BALL'), (L * 0.28, 0, H * 0.42, W * 0.42, 'BALL'),
               (-L * 0.15, 0, H * 0.45, W * 0.5, 'BALL'), (L * 0.15, 0, H * 0.45, W * 0.5, 'BALL')]
        bm = metaball_bm(els, res=res, threshold=0.5)
    # flatten bottom, scale to target dims
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    sx = L / (max(xs) - min(xs)) if kind != 'boule' else W / (max(xs) - min(xs))
    sy = W / (max(ys) - min(ys)); sz = H / (max(zs) - min(zs)) * 1.0
    zmin = min(zs)
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy; v.co.z = (v.co.z - zmin) * sz
    bm = disp(bm, 0.0035, 0.035, 3, seed_loc=(seed * 3.1, seed * 1.7, 0.3))
    rr = random.Random(seed)
    # scoring: thin slanted Boolean cutters along the top (cut only where the dome rises above the cutter -> naturally tapered slashes)
    slashes = []
    if score:
        for i in range(score):
            off = (i - (score - 1) / 2) * (L * 0.2 if kind != 'boule' else W * 0.27)
            if kind == 'boule':
                slashes.append(((off, -W * 0.3), (off, W * 0.3)))
            else:
                slashes.append(((off - L * 0.05, -W * 0.34), (off + L * 0.05, W * 0.34)))
    cutters = []
    for (a, b) in slashes:
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        cb = cube_bm(ln * 1.0, 0.0055, 0.03, off=(0, 0, 0.015))
        ang = math.atan2(dy, dx)
        Mc = Matrix.Translation(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, H - 0.0105)) @ Matrix.Rotation(ang, 4, 'Z') @ Matrix.Rotation(math.radians(28), 4, 'X')
        cutters.append((cb, Mc))
    if cutters:
        bm = boolean(bm, cutters, solver='EXACT')
        for cb, _ in cutters:
            cb.free()
    def dist_seg(p, a, b):
        ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(p[0] - ax - dx * t, p[1] - ay - dy * t), t
    bm.normal_update()
    cl = bm.loops.layers.float_color.get('Col') or bm.loops.layers.float_color.new('Col')
    for f in bm.faces:
        for l in f.loops:
            c = l.vert.co
            near = 9
            for (a, b) in slashes:
                d, t = dist_seg((c.x, c.y), a, b)
                near = min(near, d)
            k = 1.0
            col = (k, k, k)
            if c.z > H * 0.5:
                k = 1 + 0.08 * fbm(c.x * 50, c.y * 50, 0, 1, seed, 2)
                col = (k, k, k)
            if near < 0.0075 and c.z > H * 0.82:
                col = (0.82, 0.62, 0.38)       # opened 'ear' of the slash: pale, barely baked
            l[cl] = (col[0], col[1], col[2], 1.0)
    bm.normal_update()
    return bm


def loaf(pos, rot=0, L=0.28, W=0.12, H=0.085, seed=0, score=3, kind='batard'):
    bm = loaf_bm(L, W, H, seed, score, kind)
    put('crust', bm, xf(pos, (0, 0, rot)), g=0)
    bm.free()


def bread_slice(pos, rot=None, W=0.11, H=0.085, t=0.014, seed=0):
    """cross-section slice: crust ring + crumb faces"""
    pts = []
    n = 16
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((math.cos(a) * W / 2, math.sin(a) ** 0.7 * H * (0.95 + 0.05 * math.cos(a * 3))))
    outline = [(-W / 2, 0)] + pts + []
    outline = [(x, z) for x, z in pts[::-1]] + [(-W / 2 * 0.0 + 0, 0)] if False else None
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    ring = pts + [(-W / 2, 0.0), (W / 2, 0.0)][:0]
    # build crumb face (inner) and crust band
    inner = [(x * 0.9, z * 0.9 + 0.003) for x, z in pts]
    # closed outline: pts (right->left along dome) then back along the bottom
    P = [(x, z) for x, z in pts] + [(-W / 2, 0.0), (W / 2, 0.0)]
    crumb = bmesh.new()
    cul = crumb.loops.layers.uv.new('UVMap')
    Pin = [(x * 0.93, z * 0.9 + 0.004) for x, z in pts] + [(-W / 2 * 0.93, 0.0), (W / 2 * 0.93, 0.0)]
    vf = [crumb.verts.new((x, 0, z)) for x, z in Pin]
    f = crumb.faces.new(vf)
    for l in f.loops:
        l[cul].uv = (l.vert.co.x * 10, l.vert.co.z * 10)
    cr = bmesh.new()
    cr_u = cr.loops.layers.uv.new('UVMap')
    vo = [cr.verts.new((x, 0, z)) for x, z in P]
    vi = [cr.verts.new((x, 0, z)) for x, z in Pin]
    m = len(P)
    for i in range(m):
        j = (i + 1) % m
        ff = cr.faces.new([vo[i], vo[j], vi[j], vi[i]])
    # thickness: extrude both
    r2 = bmesh.ops.extrude_face_region(cr, geom=cr.faces[:])
    for v in [e for e in r2['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += t
    bmesh.ops.recalc_face_normals(cr, faces=cr.faces[:])
    r3 = bmesh.ops.extrude_face_region(crumb, geom=crumb.faces[:])
    for v in [e for e in r3['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += t * 0.98
    bmesh.ops.recalc_face_normals(crumb, faces=crumb.faces[:])
    for b in (cr, crumb):
        bmesh.ops.translate(b, verts=b.verts[:], vec=(0, -t / 2, 0))
    Mx = xf(pos, rot)
    put('crust', cr, Mx, g=0, uvs=3.3)
    put('crumb', crumb, Mx, g=0)
    cr.free(); crumb.free(); bm.free()


def cheese_wedge(pos, rot=0, R=0.09, ang=48, H=0.055, seed=0, holes=7, mat_rind=True):
    """wheel segment: Boolean-subtract spheres for eyes, rind band darker (vertex colours)"""
    bm = bmesh.new()
    n = 8
    vs0, vs1 = [], []
    a0, a1 = -math.radians(ang) / 2, math.radians(ang) / 2
    pts = [(0, 0)] + [(R * math.cos(a0 + (a1 - a0) * i / n), R * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    f = bm.faces.new([bm.verts.new((x, y, 0)) for x, y in pts])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z = H
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    rr = random.Random(seed)
    cut = []
    for i in range(holes):
        ra = rr.uniform(0.01, 0.019)
        p = Vector((rr.uniform(R * 0.3, R * 0.85), rr.uniform(-R * 0.3, R * 0.3), rr.uniform(H * 0.25, H * 0.8)))
        p.y *= (p.x / R)
        sb = sphere_bm(ra, 6, 4)
        cut.append((sb, Matrix.Translation(p)))
    bm = boolean(bm, cut, solver='EXACT')
    for cb, _ in cut:
        cb.free()
    # bevel soft edges
    bm = modbm(bm, [('BEVEL', {'width': 0.0016, 'segments': 1, 'limit_method': 'ANGLE', 'angle_limit': math.radians(40)})])
    ul = bm.loops.layers.uv.verify()
    colorize(bm, lambda p: (0.78, 0.44, 0.16) if math.hypot(p.x, p.y) > R * 0.985 and abs(p.y) < R else (1, 1, 1))
    for f in bm.faces:
        for l in f.loops:
            c = l.vert.co
            l[ul].uv = ((c.x + c.z) * 5, (c.y + c.z * 0.7) * 5)
    put('cheese', bm, xf(pos, (0, 0, rot)))
    bm.free()


def butter_block(pos, rot=0, L=0.1, W=0.055, H=0.035):
    bm = cube_bm(L, W, H, off=(0, 0, H / 2))
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)
    bev_bm(bm, 0.003, 2)
    for v in bm.verts:
        if v.co.z > H * 0.9:
            v.co.z += 0.0012 * math.sin(v.co.x * 160) * 0.5 + 0.001 * fbm(v.co.x * 90, v.co.y * 90, 0, 1, 2, 1)
        # knife drag cut at one end
        if v.co.x > L * 0.18 and v.co.z > H * 0.35:
            v.co.z -= 0.006 * (v.co.x / (L * 0.5))
    colorize(bm, lambda p: (0.96, 0.84, 0.42) if p.z > H * 0.9 else (0.93, 0.8, 0.38))
    put('food_vc', bm, xf(pos, (0, 0, rot)))
    bm.free()


# ---------------------------------------------------------------- leaves and flowers
def leaf_bm(L, W, curl=0.2, n=4, fold=0.12, col=(0.2, 0.4, 0.1), tip=1.0, seed=0, vein=True):
    bm = bmesh.new()
    cl = bm.loops.layers.float_color.new('Col')
    rows = []
    for i in range(n + 1):
        t = i / n
        w = W * 0.5 * (math.sin(math.pi * min(1.0, t ** 0.75 * 1.0)) ** 0.8 if t < 1 else 0.0) * (1 if tip >= 1 else 1)
        w = max(w, 0.0)
        y = t * L
        z = curl * L * t * t - 0.0
        fz = w * fold
        rows.append((bm.verts.new((-w, y, z)), bm.verts.new((0, y, z + fz)), bm.verts.new((w, y, z))))
    for i in range(n):
        a, b = rows[i], rows[i + 1]
        for (p, q, r_, s_) in ((a[0], a[1], b[1], b[0]), (a[1], a[2], b[2], b[1])):
            try:
                f = bm.faces.new([p, q, r_, s_]) if len({p, q, r_, s_}) == 4 else bm.faces.new([x for x in (p, q, r_, s_) if True][:3])
            except ValueError:
                continue
            for l in f.loops:
                k = 1 + 0.15 * fbm(l.vert.co.x * 50, l.vert.co.y * 50, seed, 1, seed, 1)
                lt = l.vert.co.y / max(L, 1e-6)
                c = (col[0] * k * (0.8 + 0.3 * lt), col[1] * k * (0.85 + 0.25 * lt), col[2] * k)
                l[cl] = (c[0], c[1], c[2], 1)
    return bm


def petal_bm(L, W, droop=0.3, col=(1, 1, 1), tipcol=None, n=3):
    bm = bmesh.new()
    cl = bm.loops.layers.float_color.new('Col')
    rows = []
    for i in range(n + 1):
        t = i / n
        w = W * 0.5 * (math.sin(math.pi * (0.15 + 0.85 * t) * 0.95) ** 0.7 if t < 1 else 0.05)
        rows.append((bm.verts.new((-w, t * L, -droop * L * t * t)), bm.verts.new((w, t * L, -droop * L * t * t))))
    for i in range(n):
        f = bm.faces.new([rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]])
        for l in f.loops:
            t = l.vert.co.y / L
            c = mixc(col, tipcol, t) if tipcol else col
            l[cl] = (c[0], c[1], c[2], 1)
    return bm


def flower(pos, kind, stem_pts, seed=0, sc=1.0, face_dir=None):
    """stem_pts: list of Vectors (world) from bottom to head; head placed at the last point oriented along last tangent"""
    rr = random.Random(seed)
    pts = polyline_smooth(stem_pts, 3)
    tube('herb_vc', pts, 0.0017 * sc, seg=4, caps=False, col=(0.22, 0.42, 0.12))
    tip = pts[-1]
    tang = (pts[-1] - pts[-2]).normalized()
    # orientation: local z along tang
    zax = tang
    xax = Vector((0, 0, 1)).cross(zax)
    if xax.length < 1e-4:
        xax = Vector((1, 0, 0))
    xax.normalize()
    yax = zax.cross(xax)
    Mh = Matrix(((xax.x, yax.x, zax.x, tip.x), (xax.y, yax.y, zax.y, tip.y), (xax.z, yax.z, zax.z, tip.z), (0, 0, 0, 1)))
    # leaves on the stem
    for k in range(2):
        t = rr.uniform(0.25, 0.6)
        base = pts[int(len(pts) * t)]
        a = rr.uniform(0, TAU)
        lb = leaf_bm(0.045 * sc, 0.008 * sc, curl=-0.3, n=3, col=(0.2, 0.38, 0.1), seed=seed + k)
        Ml = Matrix.Translation(base) @ rotm((rr.uniform(20, 40), 0, math.degrees(a)))
        # leaf points up-out
        put('herb_vc', lb, Matrix.Translation(base) @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(math.radians(-60), 4, 'X') @ Matrix.Rotation(0, 4, 'Z'))
        lb.free()
    if kind == 'daisy':
        for i in range(13):
            a = TAU * i / 13 + rr.uniform(-0.05, 0.05)
            pb = petal_bm(0.02 * sc, 0.0055 * sc, droop=0.25, col=(0.97, 0.96, 0.92), tipcol=(0.9, 0.9, 0.86))
            put('herb_vc', pb, Mh @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Translation((0, 0.004 * sc, 0)) @ Matrix.Rotation(math.radians(-14), 4, 'X'))
            pb.free()
        lathe('food_matte', None, [(0.001, 0.003 * sc), (0.0065 * sc, 0.0015 * sc), (0.0075 * sc, 0.0), (0.0075 * sc, -0.002 * sc), (0.001, -0.002 * sc)], 8, M=Mh, col=(0.9, 0.7, 0.1), cap=False)
    elif kind == 'corn':   # cornflower
        for i in range(9):
            a = TAU * i / 9 + rr.uniform(-0.1, 0.1)
            pb = petal_bm(0.017 * sc, 0.006 * sc, droop=0.05, col=(0.25, 0.32, 0.78), tipcol=(0.3, 0.38, 0.86), n=2)
            put('herb_vc', pb, Mh @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(math.radians(28), 4, 'X'))
            pb.free()
        for i in range(5):
            a = TAU * i / 5
            pb = petal_bm(0.011 * sc, 0.005 * sc, droop=0.0, col=(0.45, 0.4, 0.82), n=2)
            put('herb_vc', pb, Mh @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(math.radians(58), 4, 'X'))
            pb.free()
        lathe('herb_vc', None, [(0.001, 0.0), (0.005 * sc, -0.002 * sc), (0.006 * sc, -0.007 * sc), (0.001, -0.01 * sc)], 7, M=Mh, col=(0.28, 0.4, 0.16), cap=False)
    elif kind == 'poppy':
        for i in range(4):
            a = TAU * i / 4 + 0.4 * rr.random()
            pb = petal_bm(0.026 * sc, 0.03 * sc, droop=-0.5, col=(0.8, 0.08, 0.05), tipcol=(0.9, 0.12, 0.06), n=3)
            put('herb_vc', pb, Mh @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Translation((0, 0.003, 0)) @ Matrix.Rotation(math.radians(38), 4, 'X'))
            pb.free()
        lathe('food_matte', None, [(0.001, 0.008 * sc), (0.005 * sc, 0.006 * sc), (0.006 * sc, 0.0), (0.001, 0.0)], 7, M=Mh, col=(0.18, 0.2, 0.1), cap=False)
        for i in range(8):
            a = TAU * i / 8
            tube('ink', [Mh @ Vector((0.004 * sc * math.cos(a), 0.004 * sc * math.sin(a), 0.001)), Mh @ Vector((0.008 * sc * math.cos(a), 0.008 * sc * math.sin(a), 0.007 * sc))], 0.0004, seg=3, caps=False)
    elif kind == 'lav':
        for i in range(14):
            t = i / 13
            a = TAU * i * 0.382
            q = Mh @ Vector((0.004 * sc * math.cos(a), 0.004 * sc * math.sin(a), -t * 0.04 * sc))
            sphere('herb_vc', q, 0.0032 * sc, seg=5, rings=3, sq=(1, 1, 1.5), col=(0.45, 0.35, 0.7) if i % 3 else (0.55, 0.42, 0.78))
    elif kind == 'grass':
        for i in range(3):
            a = TAU * i / 3
            lb = leaf_bm(0.07 * sc, 0.003 * sc, curl=0.5, n=4, col=(0.5, 0.6, 0.25), fold=0.0)
            put('herb_vc', lb, Mh @ Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(math.radians(40), 4, 'X'))
            lb.free()


def flower_bunch(pos, base_r, n=9, h0=0.1, seed=3, spread=0.06, up=0.2, kinds=('daisy', 'corn', 'poppy', 'lav', 'grass', 'daisy', 'corn')):
    rr = random.Random(seed)
    p0 = Vector(pos)
    for i in range(n):
        a = TAU * i / n + rr.uniform(-0.3, 0.3)
        d = rr.uniform(0.3, 1.0)
        top_h = rr.uniform(0.1, 0.2) + up
        sx = math.cos(a) * spread * d
        sy = math.sin(a) * spread * d
        pts = [p0 + Vector((0, 0, 0)), p0 + Vector((sx * 0.25, sy * 0.25, top_h * 0.45)), p0 + Vector((sx * 0.7, sy * 0.7, top_h * 0.8)), p0 + Vector((sx, sy, top_h))]
        flower(p0, kinds[i % len(kinds)], pts, seed + i, sc=1.0)


# ---------------------------------------------------------------- herb bundles
def herb_bundle(top, L=0.32, kind='lav', n=7, seed=1, spread=0.045, hang=True):
    """upside-down bundle tied with twine; top = tie point.  individual stems + leaves."""
    rr = random.Random(seed)
    top = Vector(top)
    sgn = -1 if hang else 1
    cols = {'lav': (0.2, 0.22, 0.16), 'herb': (0.12, 0.2, 0.06), 'dry': (0.3, 0.22, 0.1), 'wheat': (0.5, 0.36, 0.14), 'chili': (0.2, 0.2, 0.08),
            'sage': (0.2, 0.26, 0.2), 'rose': (0.28, 0.14, 0.12)}
    sc_ = cols.get(kind, (0.35, 0.4, 0.2))
    for i in range(n):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0.3, 1.0) * spread
        ln = L * rr.uniform(0.8, 1.05)
        end = top + Vector((math.cos(a) * d * 1.8, math.sin(a) * d * 1.8, sgn * ln))
        mid = top + Vector((math.cos(a) * d * 0.9 + rr.uniform(-0.004, 0.004), math.sin(a) * d * 0.9, sgn * ln * 0.5))
        pts = [top + Vector((math.cos(a) * 0.004, math.sin(a) * 0.004, sgn * -0.03)), top, mid, end]
        pts = polyline_smooth(pts, 3)
        tube('herb_vc', pts, 0.0016, seg=4, caps=False, col=jit(sc_, 0.15))
        # foliage along the lower 2/3
        if kind in ('herb', 'sage', 'rose', 'dry'):
            nl = 4 if kind != 'sage' else 3
            for k in range(nl):
                t = 0.35 + 0.65 * k / nl
                base = pts[int(len(pts) * t) - 1]
                aa = rr.uniform(0, TAU)
                ll = (0.05 if kind != 'sage' else 0.065) * rr.uniform(0.8, 1.2)
                ww = ll * (0.4 if kind != 'rose' else 0.5)
                lb = leaf_bm(ll, ww, curl=0.25, n=2, col=jit(sc_, 0.2), seed=i * 7 + k)
                Mx = Matrix.Translation(base) @ Matrix.Rotation(aa, 4, 'Z') @ Matrix.Rotation(math.radians(rr.uniform(120, 150)) if hang else math.radians(45), 4, 'X')
                put('herb_vc', lb, Mx)
                lb.free()
        elif kind == 'lav':
            # flower spike on the lower end
            lathe('herb_vc', pts[-1], [(0.001, 0.0), (0.0035, -sgn * 0.006), (0.004, -sgn * 0.02), (0.0035, -sgn * 0.034), (0.0028, -sgn * 0.046), (0.001, -sgn * 0.056)] if hang else [(0.001, 0.0), (0.0035, 0.006), (0.004, 0.02), (0.0035, 0.034), (0.0028, 0.046), (0.001, 0.056)], 5, col=jit((0.16, 0.12, 0.24), 0.2), cap=False, auto=False)
        elif kind == 'wheat':
            lathe('herb_vc', pts[-1], [(0.001, 0.0), (0.0045, -sgn * 0.005), (0.0055, -sgn * 0.03), (0.004, -sgn * 0.055), (0.001, -sgn * 0.065)] if hang else [(0.001, 0.0), (0.0045, 0.005), (0.0055, 0.03), (0.004, 0.055), (0.001, 0.065)], 5, col=jit((0.5, 0.36, 0.14), 0.1), cap=False, auto=False)
            for s_ in (-1, 1):
                tube('herb_vc', [pts[-1] + Vector((s_ * 0.003, 0, 0)), pts[-1] + Vector((s_ * 0.007, 0, -sgn * 0.09))], 0.0004, seg=3, caps=False, col=(0.8, 0.7, 0.4))
        elif kind == 'chili':
            q = pts[-1]
            lathe('food_vc', q, [(0.001, 0.0), (0.006, -0.004 * sgn), (0.0055, -0.04 * sgn), (0.001, -0.065 * sgn)] if False else [(0.001, 0.0), (0.0065, 0.004), (0.006, 0.04), (0.001, 0.07)],
                  7, col=jit((0.65, 0.08, 0.04), 0.2), cap=False, rot=(180 if hang else 0, 0, 0))
    # twine tie + bow
    for k in range(3):
        torus('rope', top + Vector((0, 0, sgn * 0.006 * k - sgn * 0.01)), spread * 0.9, 0.0016, seg=12, rseg=4, col=(0.46, 0.34, 0.19))
    tube('rope', [top + Vector((spread * 0.9, 0, 0)), top + Vector((spread * 1.2, 0.01, sgn * 0.03)), top + Vector((spread * 1.15, 0.015, sgn * 0.05))], 0.0016, seg=4, col=(0.46, 0.34, 0.19))
    tube('rope', [top + Vector((spread * 0.9, 0, 0)), top + Vector((spread * 0.6, 0.02, sgn * 0.025)), top + Vector((spread * 0.8, 0.03, sgn * 0.05))], 0.0016, seg=4, col=(0.46, 0.34, 0.19))


def crumbs(Mx, hx, hy, n=40, seed=1, kind='bread'):
    """tiny crumbs / grains scattered with a Geometry-Nodes tree (random point distribution -> instance -> realize)"""
    surf = bmesh.new()
    bmesh.ops.create_grid(surf, x_segments=1, y_segments=1, size=1.0)
    for v in surf.verts:
        v.co.x *= hx; v.co.y *= hy
    cols = {'bread': ((0.62, 0.4, 0.18), (0.82, 0.66, 0.42), (0.72, 0.55, 0.32)), 'flour': ((0.9, 0.88, 0.8),) * 3, 'pepper': ((0.05, 0.04, 0.04),) * 3,
            'salt': ((0.92, 0.92, 0.9),) * 3}[kind]
    vars_ = []
    for j in range(3):
        bb = sphere_bm(0.0024 + 0.0006 * j, 4, 3, (1.0, 0.8, 0.55))
        c = cols[j]
        colorize(bb, lambda p, c=c: c)
        vars_.append({'parts': [(bb, 'food_matte')]})
    outs = gn_scatter(surf, vars_, mode='RANDOM', density=n / (4 * hx * hy), seed=seed, scale=(0.6, 1.5), tilt=0.5, tint=0.15, surf_M=Mx)
    for v in vars_:
        for (bb, mn) in v['parts']:
            bb.free()
    surf.free()
    put_outs(outs, Matrix.Identity(4))
