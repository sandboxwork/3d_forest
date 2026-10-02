"""Helpers for vp_p2: food, crates, baskets, fish, cloth grids, prisms, awnings, stall frame."""
from vp_parts import *

R2 = random.Random(21)
MAT('iron_forged', '#c8c8d0', tex='pbr_iron', tile=0.3, rough=0.55, metal=0.3, sharp=42)
FORGED = H('#55555c')


def pgrid(nu, nv, fn, su=1.0, sv=1.0):
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    vs = {}
    for i in range(nu + 1):
        for j in range(nv + 1):
            vs[(i, j)] = bm.verts.new(fn(i / nu, j / nv))
    uvmap = {v: (i / nu * su, j / nv * sv) for (i, j), v in vs.items()}
    for i in range(nu):
        for j in range(nv):
            f = bm.faces.new((vs[(i, j)], vs[(i + 1, j)], vs[(i + 1, j + 1)], vs[(i, j + 1)]))
            f.smooth = True
            for l in f.loops:
                l[ul].uv = uvmap[l.vert]
    return bm


def prism(pts, thick, bev=0.003, flat_ends=True):
    """convex polygon (x,y) extruded along z in [-t/2,t/2]"""
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    top = [bm.verts.new((x, y, thick / 2)) for x, y in pts]
    bot = [bm.verts.new((x, y, -thick / 2)) for x, y in pts]
    bm.faces.new(top)
    bm.faces.new(bot[::-1])
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bev:
        bev_bm(bm, bev, 1)
    return bm


# ----------------------------------------------------------------- food
def apple(c, r, col, seed=0):
    sphere('food', c, r, seg=7, rings=5, sq=(1, 1, 0.9), col=col)



def pear(c, r, col, rot=None):
    prof = [(0.0, -0.9), (0.45, -0.85), (0.8, -0.45), (0.85, 0.0), (0.62, 0.45), (0.4, 0.75), (0.28, 1.05), (0.0, 1.15)]
    lathe('food', c, [(a * r, z * r) for a, z in prof], seg=9, col=col, cap=False, rot=rot, auto=False)


def onion(c, r, col):
    prof = [(0.0, -0.75), (0.55, -0.68), (0.95, -0.2), (0.9, 0.3), (0.5, 0.75), (0.12, 1.1), (0.0, 1.2)]
    lathe('food', c, [(a * r, z * r) for a, z in prof], seg=8, col=col, cap=False, rot=(0, 0, R2.uniform(0, 360)), auto=False)


def tomato(c, r, col):
    sphere('food', c, r, seg=6, rings=4, sq=(1, 1, 0.8), col=col)


def cabbage(c, r, col):
    sphere('food', c, r * 0.85, seg=8, rings=5, sq=(1, 1, 0.92), col=mixc(col, (0.8, 0.9, 0.6), 0.3))
    n = 5
    for i in range(n):
        a = TAU * i / n + R2.random()
        cc = (c[0] + math.cos(a) * r * 0.55, c[1] + math.sin(a) * r * 0.55, c[2] + r * 0.05)
        sphere('food', cc, r * 0.5, seg=7, rings=4, sq=(0.85, 0.35, 0.95), rot=(0, 0, a + math.pi / 2),
               col=mixc(col, (0.15, 0.3, 0.1), R2.uniform(0, 0.5)))
    sphere('food', (c[0], c[1], c[2] + r * 0.55), r * 0.4, seg=8, rings=5, sq=(1, 1, 0.5), col=mixc(col, (0.85, 0.95, 0.7), 0.5))


def carrot(c, rot, L=0.2, col=(0.8, 0.33, 0.07)):
    r = 0.013
    prof = [(0.0, 0.0), (0.004, 0.01), (r * 0.9, L * 0.35), (r, L * 0.85), (r * 0.95, L), (0.0, L + 0.004)]
    lathe('food', c, prof, seg=7, col=col, cap=False, rot=rot, auto=False)


def carrot_bunch(c, rot_z, n=6, L=0.2):
    for i in range(n):
        a = (i - n / 2) * 7
        # carrot lying along x axis, tips pointing -x; tops at +x
        carrot((c[0], c[1] + (i - n / 2) * 0.02, c[2] + 0.014 + (0.01 if i % 2 else 0)), (0, 90 + R2.uniform(-4, 4), rot_z + a * 0.4), L=L * R2.uniform(0.85, 1.1), col=jitter_col((0.82, 0.34, 0.07), 0.1))
    # leaves
    M0 = xf(c, (0, 0, rot_z))
    for i in range(7):
        a = (i - 3) * 0.12
        p0 = M0 @ Vector((L - 0.01, (i - 3) * 0.008, 0.02))
        p1 = M0 @ Vector((L + 0.16, (i - 3) * 0.03, 0.03 + R2.uniform(-.01, .03)))
        ribbon('leaf', p0, p1, 0.012, 0.004, col=jitter_col((0.22, 0.45, 0.1), 0.2), bend=(0, 0, 0.02), nseg=2, up=(0, 0, 1))
    # twine
    cyl('rope', M0 @ Vector((L * 0.9, 0, 0.028)), 0.03, 0.012, axis='x', seg=8, col=ROPE_C, rot=(0, 0, rot_z))


def potato(c, r, col):
    sphere('food', c, r, seg=6, rings=4, sq=(1.25, 0.9, 0.8), col=col, rot=(0, 0, R2.uniform(0, 3)))


# ----------------------------------------------------------------- containers
def crate(c, rot=0.0, size=(0.5, 0.38, 0.22), col=PINE_W, seed=0, thick=0.016, feet=True):
    f = Fr(c, rot)
    w, d, h = size
    cf = wood_cfn(col, 0.15, 8, seed, grime_z=0.0)
    for k in range(3):
        f.box('pine', (0, -d / 2 + d / 6 + k * d / 3, thick / 2), (w - 0.02, d / 3 - 0.006, thick), col=jitter_col(col, 0.1), bev=0.0, g=0, cfn=None)
    for sy in (-1, 1):
        for k in range(2):
            f.box('pine', (0, sy * (d / 2 - thick / 2), 0.045 + k * (h - 0.02) / 2 + 0.04), (w, thick, (h - 0.02) / 2 - 0.012), col=jitter_col(col, 0.12), bev=0.0, g=0)
    for sx in (-1, 1):
        for k in range(2):
            f.box('pine', (sx * (w / 2 - thick / 2), 0, 0.045 + k * (h - 0.02) / 2 + 0.04), (thick, d - 2 * thick - 0.002, (h - 0.02) / 2 - 0.012), col=jitter_col(col, 0.12), bev=0.0, g=1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box('pine', (sx * (w / 2 - 0.02), sy * (d / 2 - 0.02), h / 2 + 0.01), (0.04, 0.04, h + 0.02), col=jitter_col(col, 0.1) , bev=0.0, g=2)
            if sx > 0: nail(f.p((sx * (w / 2 - 0.02), sy * (d / 2 + 0.001), h * 0.8)), d=f.M.to_3x3() @ Vector((0, sy, 0)), r=0.006)
    return f


def fill_layer(f, size, z, r, mk, jitter=0.4, margin=0.02, offset=0.0, skip=0.0):
    w, d, h = size
    nx = max(1, int((w - 2 * margin) / (2 * r)))
    ny = max(1, int((d - 2 * margin) / (2 * r)))
    for i in range(nx):
        for j in range(ny):
            if skip and R2.random() < skip:
                continue
            x = (i - (nx - 1) / 2) * 2 * r + offset * r + R2.uniform(-jitter, jitter) * r * 0.5
            y = (j - (ny - 1) / 2) * 2 * r + offset * r + R2.uniform(-jitter, jitter) * r * 0.5
            mk(f.p((x, y, z + R2.uniform(0, 0.01))), r)


def wicker_basket(c, R=0.22, h=0.26, rot=0.0, handle=True, seed=0, col=(0.85, 0.7, 0.45), taper=0.78, stakes=22, rows=3, M=None, open_=True, NW=22):
    Mb = M if M is not None else xf(c, (0, 0, rot))
    f = FM(Mb)
    rb = R * taper
    prof_out = [(0.0, 0.0), (rb * 0.98, 0.0), (rb, 0.01), (rb + (R - rb) * 0.5, h * 0.5), (R, h - 0.012), (R + 0.004, h)]
    prof_in = [(R - 0.012, h), (R - 0.016, h - 0.012), (rb - 0.015, 0.03), (0.0, 0.03)]
    lathe('wicker', None, prof_out, seg=16, M=Mb, col=col, cap=False, auto=False, uvm=1.0)
    lathe('wicker', None, prof_in, seg=16, M=Mb, col=mixc(col, (0.3, 0.2, 0.1), 0.45), cap=False, auto=False)

    def rad(z):
        t = z / h
        return rb + (R - rb) * (0.5 * t + 0.5 * t * t) * 1.0 + (0.0)
    # weavers: tubes whose radius undulates in/out of the stakes
    for k in range(rows):
        z = 0.035 + k * (h - 0.06) / max(1, rows - 1)
        pts = []
        N = NW
        for i in range(N + 1):
            a = TAU * i / N
            u = a / TAU * stakes
            amp = 0.0045 * (1 if (math.floor(u) + k) % 2 else -1)
            wob = 0.0045 * math.sin(u * math.pi * 2 + (k % 2) * math.pi) + 0.004
            pts.append(Vector((math.cos(a) * (rad(z) + wob), math.sin(a) * (rad(z) + wob), z)))
        f.tube('wicker', pts, 0.0075, seg=4, col=jitter_col(col, 0.15), caps=False)
    # rim rope
    pts = [Vector((math.cos(TAU * i / 20) * (R + 0.004), math.sin(TAU * i / 20) * (R + 0.004), h)) for i in range(21)]
    f.tube('wicker', pts, 0.011, seg=4, col=mixc(col, (0.5, 0.35, 0.18), 0.3), caps=False)
    if handle:
        for sx in (-1, 1):
            pts = [Vector((sx * (R + 0.002), 0, h - 0.01))]
            for i in range(1, 10):
                a = math.pi * i / 10
                pts.append(Vector((sx * (R + 0.002) * (1 - math.sin(a) * 0.0) + sx * 0.0, 0, h - 0.01)) + Vector((-sx * (R * 0.0), 0, 0)))
            pts = []
        # single hoop handle across (arc over the top, in the XZ plane)
        pts = []
        for i in range(0, 13):
            a = math.pi * i / 12
            pts.append(Vector((-math.cos(a) * (R + 0.004), 0, h + math.sin(a) * h * 0.75)))
        f.tube('wicker', pts, 0.013, seg=6, col=mixc(col, (0.5, 0.35, 0.18), 0.35), caps=True)
    return f


# ----------------------------------------------------------------- fish
def fish(M0, L=0.3, Hh=0.07, Wd=0.035, back=(0.35, 0.45, 0.5), belly=(0.85, 0.87, 0.85), tail_col=None, seed=0, bend=0.0):
    """fish along local +x (head at x=0 -> tail at x=L). z up = dorsal."""
    tail_col = tail_col or back
    prof = [(math.cos(TAU * k / 8), math.sin(TAU * k / 8)) for k in range(8)]
    n = 10
    path = []
    sc = []
    for i in range(n):
        t = i / (n - 1)
        path.append(Vector((t * L * 0.9, bend * math.sin(t * math.pi * 1.2) * L, 0)))
        hh = Hh * (math.sin(math.pi * min(1.0, 0.1 + t * 1.0)) ** 0.6) * (1.0 - 0.55 * t * t) + 0.004
        ww = Wd * (math.sin(math.pi * min(1.0, 0.16 + t * 0.95)) ** 0.7) * (1.0 - 0.6 * t) + 0.002
        if i == 0:
            hh *= 0.5; ww *= 0.5
        sc.append((hh * 0.5, ww * 0.5))

    def cf(p):
        q = M0.inverted() @ p
        z = q.z / max(Hh * 0.5, 1e-4)
        t = max(0.0, min(1.0, (z + 0.2) / 0.9))
        c = mixc(belly, back, t * t * (3 - 2 * t))
        if q.x < L * 0.18:
            c = mixc(c, (0.2, 0.22, 0.22), 0.25)
        return c
    FM(M0).sweep('fish', [(p[0], p[1]) for p in prof], path, scale=sc, up=(0, 0, 1), col=(1, 1, 1), cfn=cf, caps=True, uvm=2.0)
    # tail fin (forked), flat fan in the local XZ plane
    tx = L * 0.88
    by = path[-1].y
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    vv = [bm.verts.new(q) for q in ((tx, by, Hh * 0.08), (tx + L * 0.24, by, Hh * 0.62), (tx + L * 0.15, by, 0.0), (tx + L * 0.24, by, -Hh * 0.62), (tx, by, -Hh * 0.08))]
    for tri in ((0, 1, 2), (0, 2, 4), (4, 2, 3)):
        f = bm.faces.new([vv[i] for i in tri]); f.smooth = False
        for l in f.loops:
            l[ul].uv = (l.vert.co.x, l.vert.co.z)
    put_bm('fish', bm, M=M0, col=tail_col, flat=True)
    # dorsal fin
    p0 = M0 @ Vector((L * 0.35, 0, Hh * 0.45)); p1 = M0 @ Vector((L * 0.6, 0, Hh * 0.45))
    ribbon('fish', p0, p1, Hh * 0.5, Hh * 0.1, col=tail_col, up=(0, 1, 0))
    # eyes
    for s in (-1, 1):
        sphere('plain_gloss', M0 @ Vector((L * 0.08, s * Wd * 0.28, Hh * 0.08)), Hh * 0.09, seg=6, rings=4, col=(0.02, 0.02, 0.02))


# ----------------------------------------------------------------- awning / stall frame
def awning(x0, x1, yb, zb, yf, zf, ca, cb, ribs, seed=0, stripe=0.16, sag=0.04, valance=0.2):
    rr = random.Random(seed)
    xs = (x1 - x0)

    def zfn(x, y):
        t = (y - yb) / (yf - yb)
        z = zb + (zf - zb) * t
        # sag between ribs
        best = 0.0
        d = min(abs(x - rx) for rx in ribs)
        sp = (xs / (len(ribs) - 1))
        s = max(0.0, 1 - d / (sp * 0.5))
        z -= sag * (1 - s) ** 1.0 * math.sin(math.pi * min(1, max(0, t))) * 0.8 + sag * 0.4 * (1 - s) * (1 - t)
        z += 0.01 * math.sin(x * 9 + y * 4)
        return z

    def cfn(p):
        i = int(math.floor((p.x - x0) / stripe + 1000)) % 2
        c = ca if i == 0 else cb
        k = 1 + 0.12 * fbm(p.x, p.y, p.z, 3.0, seed, 3) + 0.05 * math.sin(p.x * 80 + seed)
        # dirt toward the front edge
        return (c[0] * k, c[1] * k, c[2] * k)
    bm = cloth_sag_grid(x0, x1, yb, yf, 30, 8, zfn)
    put_bm('linen', bm, cfn=cfn, g=2, flat=False)
    # valance (front hanging scalloped strip)
    ns = int(round(xs / 0.24))
    cols = ns * 3
    zt0 = zf

    def vfn(u, v):
        x = x0 + xs * u
        f = (u * ns) % 1.0
        sc = math.sqrt(max(0.0, 1 - (2 * f - 1) ** 2))
        bottom = zf - valance * 0.55 - 0.08 * sc
        z = zf - (zf - bottom) * v
        return (x, yf - 0.01 - 0.03 * v + 0.012 * math.sin(u * 40) * v, z + 0.0)
    bm = pgrid(cols, 3, vfn, su=xs, sv=0.2)
    put_bm('linen', bm, cfn=cfn, g=2)
    # rope trim on valance top
    pts = [Vector((x0 + xs * i / 8, yf - 0.005, zf)) for i in range(9)]
    tube('rope', pts, 0.008, seg=4, col=ROPE_C, caps=True)


def stall_frame(wood, seed, palette, hang_rod=False, shelf_goods=None):
    PW = jitter_col(wood, 0.02)
    cf = lambda s: wood_cfn(PW, 0.14, 7, seed + s, grime_z=0.35)
    # posts
    for (x, y, ztop) in ((-1.5, -0.95, 2.33), (1.5, -0.95, 2.33), (-1.5, 0.95, 2.8), (1.5, 0.95, 2.8)):
        beam('pine', (x, y, 0.0), (x, y, ztop), 0.1, 0.1, bev=0.007, up=(0, 1, 0), col=PW, cfn=cf(int(x * 7 + y * 3)))
        # foot stone/pad
        box('stone', (x, y, 0.03), (0.16, 0.16, 0.06), col=H('#7a746a'), bev=0.01, cfn=stone_cfn(H('#7d776d'), H('#a29780'), 4, seed, moss=0.3))
    # top plates
    beam('pine', (-1.62, -0.95, 2.28), (1.62, -0.95, 2.28), 0.1, 0.1, bev=0.006, col=PW, cfn=cf(11))
    beam('pine', (-1.62, 0.95, 2.77), (1.62, 0.95, 2.77), 0.1, 0.1, bev=0.006, col=PW, cfn=cf(12))
    # side rafters / rails (sloped)
    ribs = [-1.5, -0.75, 0.0, 0.75, 1.5]
    for x in ribs:
        w = 0.08 if abs(x) > 1 else 0.055
        beam('pine', (x, 1.02, 2.80), (x, -1.28, 2.31), w, 0.06, bev=0.004, col=PW, cfn=cf(int(x * 5) + 30), up=(0, 0, 1))
    # braces back
    for sx in (-1, 1):
        beam('pine', (sx * 1.5, 0.95, 2.3), (sx * 1.5, 0.35, 2.78), 0.07, 0.07, bev=0.005, col=PW, up=(1, 0, 0), cfn=cf(40))
        beam('pine', (sx * 1.5, -0.95, 1.95), (sx * 1.5, -0.35, 2.28), 0.07, 0.07, bev=0.005, col=PW, up=(1, 0, 0), cfn=cf(41)) if False else None
    # counter
    for sx in (-1, 1):
        for sy in (-0.88, -0.44):
            beam('pine', (sx * 1.36, sy, 0.0), (sx * 1.36, sy, 0.93), 0.07, 0.07, bev=0.005, col=PW, up=(0, 1, 0), cfn=cf(50))
    plank_row('pine', -1.4, 1.4, -0.92, 0.12, 5, 0.15, 0.022, col=PW, seed=seed + 3, g=0, cfn_amp=0.14)
    for sx in (-1, 1):
        # side boards (along y)
        for k in range(5):
            z = 0.12 + k * 0.156 + 0.075
            beam('pine', (sx * 1.40, -0.92, z), (sx * 1.40, -0.40, z), 0.022, 0.15, bev=0.0, col=jitter_col(PW, 0.1), cfn=cf(60 + k), up=(0, 0, 1))
    beam('pine', (-1.38, -0.43, 0.2), (1.38, -0.43, 0.2), 0.07, 0.05, bev=0.004, col=PW, cfn=cf(70))
    # counter top boards (along x)
    for k in range(5):
        y = -0.955 + k * 0.118 + 0.059
        beam('pine', (-1.46, y, 0.94), (1.46, y, 0.94), 0.114, 0.04, bev=0.004, col=jitter_col(PW, 0.12), cfn=cf(80 + k), up=(0, 0, 1))
    # back wall planks (vertical)
    for k in range(11):
        x = -1.4 + k * 0.28
        z0 = 0.30 + 0.05 * math.sin(k * 2.1)
        beam('pine', (x, 0.99, z0), (x, 0.99, 2.0 + 0.03 * math.sin(k * 3.7)), 0.27, 0.025, bev=0.0, up=(0, 1, 0), col=jitter_col(PW, 0.12), cfn=cf(100 + k))
    # shelves
    for z in (1.05, 1.52):
        beam('pine', (-1.45, 0.82, z), (1.45, 0.82, z), 0.28, 0.035, bev=0.004, col=PW, cfn=cf(int(z * 10)), up=(0, 0, 1))
        for sx in (-1.4, 0.0, 1.4):
            beam('pine', (sx, 0.96, z - 0.15), (sx, 0.7, z - 0.035), 0.04, 0.04, bev=0.003, col=PW, up=(1, 0, 0))
    # awning
    ca, cb = palette
    awning(-1.78, 1.78, 1.02, 2.83, -1.3, 2.36, ca, cb, ribs, seed=seed)
    if hang_rod:
        beam('pine', (-1.5, -0.7, 2.18), (1.5, -0.7, 2.18), 0.04, 0.04, bev=0.003, col=PW, up=(0, 0, 1))
        for sx in (-1.4, 1.4):
            rope_line([(sx, -0.7, 2.2), (sx, -0.7, 2.3)], r=0.006)
    collider(-1.55, 1.55, -0.97, -0.37, 0.97, 0.0)
    collider(-1.55, 1.55, 0.85, 1.05, 2.8, 0.0)
