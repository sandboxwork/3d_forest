"""Small hand-modelled props for the living zone."""
from lv_mats import *

LAMPN = [0]
INTERACT_LAMP = {}
BOOKCOLS = ['#7a2f2a', '#2f4a63', '#3d5a3a', '#8a6a2e', '#4a2f4f', '#a04b2e', '#2c3f45', '#6b5a3c', '#8c3b3b', '#36506b',
            '#5d6b3a', '#b08d4a', '#4b3a2c', '#7b4b62', '#c2b090', '#2e2e38', '#9a5b3a', '#3e6a66']


def rcol(rr, hexs, a=0.08):
    return jit(C(rr.choice(hexs) if isinstance(hexs, (list, tuple)) else hexs), a)


# ------------------------------------------------------------------ flames / lights
def flame(pos, sc=1.0, inten=1.0, dist=5.0, color=(1.0, 0.68, 0.36), light_on=True, name=None, lpos=None):
    LAMPN[0] += 1
    n = name or 'lamp_liv_%d' % LAMPN[0]
    saved = part_begin()
    prof = [(0, -0.012), (0.0035, -0.010), (0.0075, -0.005), (0.0088, 0.002), (0.0075, 0.010), (0.0045, 0.019), (0.0018, 0.027), (0, 0.033)]
    lathe(M['flame'], pos, [(r * sc, z * sc) for r, z in prof], seg=10, cap=False, scale=(1, 1, 1))
    part_end(saved, n, pos)
    if light_on:
        light(n, lpos if lpos is not None else (Vector(pos) + Vector((0, 0, 0.02 * sc))), color, inten, dist)
    return n


def candle(pos, h=0.12, r=0.0125, lit=False, rr=None, melted=True, col=(0.95, 0.9, 0.75), sc=1.0, **fk):
    rr = rr or random.Random(int(pos[0] * 1000) % 977)
    pr = []
    n = 8
    for i in range(n + 1):
        z = h * i / n
        pr.append((r * (1.0 + 0.035 * math.sin(i * 1.9 + rr.random()) - 0.06 * (z / h) + 0.04 * (1 - z / h) ** 3) , z))
    top = pr[-1][0]
    pr += [(top * 0.93, h + 0.0008), (top * 0.78, h - 0.0025), (top * 0.45, h - 0.0055), (0.0016, h - 0.0045)]
    lathe(M['wax'], pos, pr, seg=14, cap=True, col=col)
    # drips
    for k in range(rr.randint(2, 3) if melted else 0):
        a = rr.uniform(0, TAU); L = rr.uniform(0.25, 0.6) * h
        x = math.cos(a) * r * 0.93; y = math.sin(a) * r * 0.93
        z0 = h - 0.002
        tube(M['wax'], [Vector(pos) + V(x, y, z0), Vector(pos) + V(x * 1.07, y * 1.07, z0 - L * 0.5), Vector(pos) + V(x * 1.06, y * 1.06, z0 - L)],
             [0.0016, 0.0019, 0.0027], seg=5, col=col, caps=True)
        sphere(M['wax'], Vector(pos) + V(x * 1.06, y * 1.06, z0 - L), 0.0033, seg=6, rings=3, sq=(1, 1, 1.4), col=col)
    tube(M['ink'], [Vector(pos) + V(0, 0, h - 0.005), Vector(pos) + V(0.0015, 0, h + 0.01 * sc), Vector(pos) + V(0.003, 0, h + 0.014 * sc)], 0.0008, seg=4, col=(0.05, 0.05, 0.05))
    if lit:
        flame(Vector(pos) + V(0.0025, 0, h + 0.022 * sc), sc=0.85 * sc, **fk)


def candlestick(pos, h=0.26, kind='brass', cl=0.18, lit=True, wax=True, seed=1, **fk):
    """turned candlestick with drip pan; returns top z of candle"""
    rr = random.Random(seed)
    mat = M[kind]
    p = Vector(pos)
    tc = (1, 0.98, 0.95)
    s = h / 0.26
    prof = [(0.001, 0), (0.05 * s, 0), (0.054 * s, 0.004 * s), (0.05 * s, 0.008 * s), (0.04 * s, 0.014 * s), (0.026 * s, 0.024 * s), (0.012 * s, 0.032 * s),
            (0.014 * s, 0.045 * s), (0.02 * s, 0.06 * s), (0.014 * s, 0.075 * s), (0.009 * s, 0.09 * s), (0.016 * s, 0.1 * s), (0.011 * s, 0.112 * s),
            (0.0085 * s, 0.13 * s), (0.0095 * s, 0.17 * s), (0.015 * s, 0.185 * s), (0.026 * s, 0.19 * s), (0.044 * s, 0.2 * s), (0.046 * s, 0.205 * s),
            (0.038 * s, 0.207 * s), (0.02 * s, 0.206 * s), (0.016 * s, 0.215 * s), (0.017 * s, 0.235 * s), (0.02 * s, 0.24 * s), (0.014 * s, 0.243 * s)]
    prof = [(r, z * 1.0) for r, z in prof]
    top = 0.243 * s
    lathe(mat, p, prof, seg=18, cap=True, col=tc)
    candle(p + V(0, 0, top - 0.02 * s), h=cl, r=0.0125, lit=lit, rr=rr, melted=wax, **fk)
    return top + cl - 0.02 * s


# ------------------------------------------------------------------ ceramics
def glaze(base, band, zc, kind='willow', seed=0):
    """vertex colour fn: bands/flowers on a glazed vessel, zc = world z of vessel foot"""
    b = C(base); bd = C(band)
    def f(p):
        z = p.z - zc
        t = 0.0
        if kind == 'willow':
            u = math.atan2(p.y, p.x)
            t = 1.0 if (0.008 < z < 0.019 or (0.049 < z < 0.057) or (0.093 < z < 0.1)) else 0.0
            fl = fbm(p.x * 40, p.y * 40, p.z * 40, 1.0, seed, 2)
            if 0.024 < z < 0.047 and fl > 0.1:
                t = max(t, 0.9)
        elif kind == 'band':
            t = 1.0 if (0.007 < z < 0.015 or 0.049 < z < 0.0585) else 0.0
        k = 1.0 + 0.03 * nz(p.x * 40, p.y * 40, p.z * 40)
        return (b[0] * (1 - t) * k + bd[0] * t, b[1] * (1 - t) * k + bd[1] * t, b[2] * (1 - t) * k + bd[2] * t)
    return f


def teapot(pos, rot=0, base='#ece6d6', band='#3b5f8c', sc=1.0, seed=3, lid=True):
    p = Vector(pos)
    f = Fr(p, rot, None)
    zc = p.z
    cf = glaze(base, band, zc / 1.0 if False else zc, 'willow', seed)
    # scaled glaze coords -> use z in metres relative; sc handled by profile scaling
    s = sc
    body = [(0.001, 0), (0.036 * s, 0), (0.042 * s, 0.003 * s), (0.044 * s, 0.01 * s), (0.062 * s, 0.03 * s), (0.073 * s, 0.055 * s), (0.07 * s, 0.075 * s),
            (0.055 * s, 0.094 * s), (0.04 * s, 0.103 * s), (0.036 * s, 0.108 * s), (0.039 * s, 0.112 * s), (0.034 * s, 0.114 * s), (0.031 * s, 0.108 * s), (0.031 * s, 0.098 * s)]
    f.lathe(M['ceramic'], (0, 0, 0), body, seg=24, cfn=cf, cap=True, fine=0.008)
    # lid
    if lid:
        lp = [(0.001, 0.109 * s), (0.032 * s, 0.109 * s), (0.034 * s, 0.112 * s), (0.03 * s, 0.119 * s), (0.02 * s, 0.126 * s), (0.008 * s, 0.13 * s), (0.007 * s, 0.134 * s),
              (0.011 * s, 0.138 * s), (0.012 * s, 0.143 * s), (0.008 * s, 0.147 * s), (0.001, 0.148 * s)]
        f.lathe(M['ceramic'], (0, 0, 0), lp, seg=22, cfn=glaze(base, band, zc, 'band', seed), fine=0.008)
    # spout
    sp = bez((0.055 * s, 0, 0.035 * s), (0.1 * s, 0, 0.04 * s), (0.105 * s, 0, 0.09 * s), (0.128 * s, 0, 0.108 * s), 10)
    f.tube(M['ceramic'], sp, [0.016 * s, 0.015 * s, 0.014 * s, 0.0125 * s, 0.011 * s, 0.0105 * s, 0.0095 * s, 0.009 * s, 0.0088 * s, 0.0086 * s, 0.0085 * s],
           seg=10, cfn=glaze(base, band, zc, 'band', seed))
    # spout rim lip
    f.tube(M['ceramic'], arcpts((0.128 * s, 0, 0.108 * s), 0.0095 * s, 0, 360, 10, 'yz'), 0.0016 * s, seg=5, cfn=glaze(base, band, zc, 'band', seed)) if False else None
    # handle
    hd = bez((-0.065 * s, 0, 0.09 * s), (-0.13 * s, 0, 0.115 * s), (-0.135 * s, 0, 0.03 * s), (-0.068 * s, 0, 0.04 * s), 12)
    f.tube(M['ceramic'], hd, [0.0075 * s, 0.009 * s, 0.01 * s, 0.01 * s, 0.01 * s, 0.01 * s, 0.01 * s, 0.01 * s, 0.01 * s, 0.01 * s, 0.009 * s, 0.0085 * s, 0.0075 * s],
           seg=8, cfn=glaze(base, band, zc, 'band', seed))
    return f


def teacup(pos, rot=0, base='#ece6d6', band='#3b5f8c', tea=True, seed=1, sc=1.0, handle_dir=0):
    p = Vector(pos)
    f = Fr(p, rot, None)
    s = sc
    cf = glaze(base, band, p.z, 'band', seed)
    pr = [(0.001, 0.0), (0.018 * s, 0.0), (0.019 * s, 0.003 * s), (0.02 * s, 0.01 * s), (0.034 * s, 0.026 * s), (0.041 * s, 0.045 * s), (0.043 * s, 0.056 * s),
          (0.0425 * s, 0.058 * s), (0.0405 * s, 0.0565 * s), (0.039 * s, 0.045 * s), (0.032 * s, 0.026 * s), (0.017 * s, 0.01 * s), (0.001, 0.008 * s)]
    f.lathe(M['ceramic'], (0, 0, 0), pr, seg=24, cfn=cf, cap=False, fine=0.008)
    if tea:
        f.lathe(M['tea'], (0, 0, 0), [(0.001, 0.044 * s), (0.038 * s, 0.044 * s)], seg=20, cap=False) if False else None
        f.lathe(M['tea'], (0, 0, 0), [(0.038 * s, 0.0455 * s), (0.001, 0.0455 * s)], seg=22, cap=False)
    hd = bez((0.04 * s, 0, 0.05 * s), (0.07 * s, 0, 0.055 * s), (0.068 * s, 0, 0.017 * s), (0.032 * s, 0, 0.022 * s), 9)
    f.tube(M['ceramic'], hd, 0.0042 * s, seg=7, cfn=cf)
    return f


def saucer(pos, rot=0, base='#ece6d6', band='#3b5f8c', seed=1, sc=1.0):
    p = Vector(pos)
    s = sc
    cf = glaze(base, band, p.z, 'band', seed)
    pr = [(0.001, 0.0), (0.03 * s, 0.0), (0.032 * s, 0.002 * s), (0.04 * s, 0.006 * s), (0.068 * s, 0.014 * s), (0.071 * s, 0.0165 * s), (0.0695 * s, 0.0175 * s),
          (0.066 * s, 0.0155 * s), (0.04 * s, 0.0085 * s), (0.026 * s, 0.0055 * s), (0.001, 0.0055 * s)]
    lathe(M['ceramic'], p, pr, seg=26, cap=False, cfn=cf, rot=(0, 0, rot), fine=0.008)


def sugar_bowl(pos, rot=0, base='#ece6d6', band='#3b5f8c', seed=2):
    p = Vector(pos); f = Fr(p, rot, None); cf = glaze(base, band, p.z, 'willow', seed)
    pr = [(0.001, 0), (0.026, 0), (0.03, 0.004), (0.045, 0.026), (0.047, 0.045), (0.036, 0.062), (0.032, 0.066), (0.034, 0.069), (0.031, 0.07), (0.029, 0.062), (0.03, 0.05)]
    f.lathe(M['ceramic'], (0, 0, 0), pr, seg=24, cfn=cf, fine=0.008)
    f.lathe(M['ceramic'], (0, 0, 0), [(0.001, 0.067), (0.032, 0.067), (0.034, 0.07), (0.025, 0.078), (0.012, 0.083), (0.005, 0.085), (0.007, 0.089), (0.006, 0.093), (0.001, 0.094)], seg=22, cfn=glaze(base, band, p.z, 'band', seed))
    for s_ in (-1, 1):
        hd = bez((s_ * 0.045, 0, 0.05), (s_ * 0.075, 0, 0.056), (s_ * 0.072, 0, 0.025), (s_ * 0.04, 0, 0.03), 8)
        f.tube(M['ceramic'], hd, 0.0042, seg=6, cfn=cf)


def creamer(pos, rot=0, base='#ece6d6', band='#3b5f8c', seed=2):
    p = Vector(pos); f = Fr(p, rot, None); cf = glaze(base, band, p.z, 'willow', seed)
    pr = [(0.001, 0), (0.02, 0), (0.025, 0.004), (0.036, 0.025), (0.034, 0.045), (0.026, 0.058), (0.03, 0.064), (0.028, 0.066), (0.024, 0.058), (0.026, 0.045)]
    f.lathe(M['ceramic'], (0, 0, 0), pr, seg=22, cfn=cf, fine=0.008)
    hd = bez((-0.03, 0, 0.055), (-0.07, 0, 0.06), (-0.068, 0, 0.022), (-0.033, 0, 0.028), 8)
    f.tube(M['ceramic'], hd, 0.0042, seg=6, cfn=cf)
    f.tube(M['ceramic'], [V(0.026, 0, 0.056), V(0.042, 0, 0.066), V(0.046, 0, 0.068)], [0.011, 0.009, 0.007], seg=7, cfn=cf)


def spoon(pos, rot=0, L=0.115, mat='pewter', tilt=None):
    p = Vector(pos); f = Fr(p, rot, None)
    bm = bmesh.new()
    nx, ny = 5, 8
    rows = []
    for j in range(ny + 1):
        t = j / ny
        w = 0.0125 * math.sin(math.pi * min(1, t * 1.15) ** 0.7) + 0.0008 if t < 0.95 else 0.002
        w = max(0.0012, w)
        row = []
        for i in range(nx + 1):
            s_ = i / nx * 2 - 1
            z = -0.0042 * (1 - s_ * s_) * (1 - t) ** 0.35 * (1 if t < 0.9 else 0.5)
            row.append(bm.verts.new((s_ * w, t * 0.04, z)))
        rows.append(row)
    for j in range(ny):
        for i in range(nx):
            try:
                bm.faces.new([rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]][::-1])
            except ValueError:
                pass
    for j in range(ny):
        for i in range(nx):
            pass
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.0008)
    put(M[mat], bm, f.M @ rotm(tilt), (1, 1, 1))
    bm.free()
    tube(M[mat], [f.p(V(0, 0.04, -0.0005)), f.p(V(0, 0.075, 0.002)), f.p(V(0, L - 0.01, 0.007))], [0.0022, 0.0025, 0.0032], seg=6) if tilt is None else None
    if tilt is None:
        box(M[mat], None, (0.012, 0.014, 0.0012), M=f.M @ Matrix.Translation((0, L - 0.003, 0.0075)), bev=0.0004)


def tray(pos, rot, W=0.42, D=0.28, mat='wood_walnut', col=(0.8, 0.62, 0.45)):
    f = Fr(pos, rot, None)
    f.box(M[mat], (0, 0, 0.007), (W, D, 0.014), bev=0.0035, col=col, cuts=2)
    pts = rrect(W - 0.004, D - 0.004, 0.02, 4)
    rim = [(0.0, 0.0), (0.0, 0.026), (-0.0075, 0.026), (-0.0075, 0.012)]
    # raised rim via sweep: path CCW, profile a = outward
    bm = sweep_bm(pts, [(-0.006, 0.012), (-0.006, 0.027), (0.002, 0.027), (0.002, 0.012)], True, uvm=TEXSC.get(mat, 1.0) if False else 2.0)
    put(M[mat], bm, f.M, col, uv_abs=True)
    bm.free()
    # handles (brass)
    for s_ in (-1, 1):
        f.tube(M['brass'], bez((s_ * (W / 2 + 0.002), -0.04, 0.02), (s_ * (W / 2 + 0.04), -0.04, 0.03), (s_ * (W / 2 + 0.04), 0.04, 0.03), (s_ * (W / 2 + 0.002), 0.04, 0.02), 8), 0.0035, seg=6)


def tea_set(cx, cy, z, rot=0):
    """tea tray set: tray, teapot, 2 cups+saucers, sugar bowl, creamer, spoon, biscuit plate"""
    f = Fr((cx, cy, z), rot, None)
    tray(f.p(V(0, 0, 0)), rot, 0.46, 0.3)
    zt = z + 0.012
    teapot(f.p(V(-0.1, 0.02, 0.012)), rot=rot + 28, seed=3)
    for k, (x, y) in enumerate(((0.07, 0.08), (0.12, -0.05))):
        q = f.p(V(x, y, 0.012))
        saucer(q, rot + 10 * k, seed=1 + k)
        teacup(q + V(0, 0, 0.0055), rot=rot + 70 + 50 * k, seed=1 + k, tea=(k == 0))
    sugar_bowl(f.p(V(-0.02, -0.09, 0.012)), rot=rot + 15)
    creamer(f.p(V(-0.15, -0.08, 0.012)), rot=rot - 15)
    spoon(f.p(V(0.19, 0.0, 0.012 + 0.0075)), rot=rot + 80, tilt=(0, 0, 0)) if False else None
    spoon(f.p(V(0.045, 0.045, 0.0185)), rot=rot + 12)
    return f


# ------------------------------------------------------------------ books (open) + glasses
def page_surface(w, d, zfn, nx, ny, flip=False):
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    Vv = [[bm.verts.new((w * i / nx, d * (j / ny - 0.5), zfn(w * i / nx, j / ny))) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            q = [Vv[i][j], Vv[i + 1][j], Vv[i + 1][j + 1], Vv[i][j + 1]]
            if flip:
                q = q[::-1]
            try:
                f = bm.faces.new(q)
            except ValueError:
                continue
            f.smooth = True
            uvs = [(i / nx, j / ny), ((i + 1) / nx, j / ny), ((i + 1) / nx, (j + 1) / ny), (i / nx, (j + 1) / ny)]
            if flip:
                uvs = uvs[::-1]
            for l, uv in zip(f.loops, uvs):
                l[ul].uv = uv
    return bm


def book_open(pos, rot=0, w=0.15, d=0.21, cover='#5b3a26', npages=26, seed=5):
    """open book: leather cover, two page blocks built from individually curved pages, text pages, bookmark ribbon."""
    rr = random.Random(seed)
    f = Fr(pos, rot, None)
    ct = 0.004
    tx = tex_mat('page_text', 'lv_page_text', '#f6efdc', 0.9)
    cc = C(cover)
    # covers
    for s_ in (-1, 1):
        f.box(M['leather'], (s_ * (w / 2 + 0.002), 0, ct / 2), (w + 0.012, d + 0.014, ct), bev=0.0012, col=cc, cuts=0)
    f.box(M['leather'], (0, 0, ct / 2 - 0.0005), (0.012, d + 0.014, ct + 0.001), bev=0.0006, col=shade(cc, 0.8))
    # tooled border on covers (gilt lines)
    for s_ in (-1, 1):
        pts = rrect(w - 0.012, d - 0.01, 0.003, 2)
        bm = sweep_bm(pts, [(0.0, 0.0), (0.0, 0.0008), (0.0007, 0.0008), (0.0007, 0.0)], True, 1.0)
        put(M['gilt'], bm, f.M @ Matrix.Translation((s_ * (w / 2 + 0.002), 0, ct)), (1, 1, 1), uv_abs=True)
        bm.free()
    T = 0.0095
    for s_ in (-1, 1):
        for k in range(npages):
            zk = ct + 0.0006 + T * (k + 1) / npages
            fan = (k / npages)
            wk = w * (0.985 - 0.012 * (npages - k) / npages) + rr.uniform(-0.0008, 0.0008)
            lift = 0.0006 * rr.random()
            top = (k == npages - 1)
            def zfn(x, v, zk=zk, wk=wk, lift=lift, k=k):
                gx = x / wk
                crest = 1 - math.exp(-x / 0.018)
                curl = 0.0055 * math.exp(-((x - 0.02) / 0.03) ** 2) * (k / npages) ** 0.8
                sag = -0.0016 * gx ** 2 * (1 - 0.5 * (k / npages))
                return zk * (0.4 + 0.6 * crest) + curl + sag + lift + 0.0006 * math.sin(v * 3.1 + gx * 5 + k)
            bm = page_surface(wk, d * (0.99 - 0.004 * (npages - k) / npages), zfn, 6, 3 if not top else 5)
            M0 = f.M @ Matrix.Scale(s_, 4, (1, 0, 0)) @ Matrix.Translation((0.004, 0, 0))
            if s_ < 0:
                bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
            if top:
                put(tx, bm, M0 @ Matrix.Scale(1, 4), (0.97, 0.95, 0.9), uv_abs=True)
            else:
                shd = 0.9 + 0.1 * rr.random()
                put(M['paper'], bm, M0, (shd, shd * 0.97, shd * 0.9), g=2)
            bm.free()
        # page block side face (fore edge slab) for thickness look
        f.box(M['paper'], (s_ * (w * 0.49 + 0.004), 0, ct + T / 2 * 0.8), (w * 0.97, d * 0.985, T * 0.8), bev=0.0006, col=(0.88, 0.84, 0.74)) if False else None
    # bookmark ribbon
    f.tube(M['fabric_linen'], [V(0.0, d / 2 - 0.01, ct + 0.012), V(0.004, d / 2 + 0.01, ct + 0.012), V(0.012, d / 2 + 0.04, ct + 0.002)], [0.0018, 0.0018, 0.0018], seg=4, col=C('#8c2a2a'), caps=True)
    return f


def reading_glasses(pos, rot=0, folded=False):
    p = Vector(pos); f = Fr(p, rot, None)
    R = 0.0215; wr = 0.0009
    sep = 0.0235
    for s_ in (-1, 1):
        circ = [V(s_ * sep + R * math.cos(a), 0, 0.001 + R * math.sin(a)) for a in [i * TAU / 20 for i in range(21)]]
        f.tube(M['brass'], circ, wr, seg=5, caps=False)
        # lens
        f.lathe(M['glass'], (s_ * sep, 0, 0.001), [(0.001, 0.0), (R - 0.0008, 0.0)], r=(90, 0, 0), seg=18, cap=False)
    f.tube(M['brass'], bez(V(-sep + R, 0, 0.012), V(-0.006, 0, 0.022), V(0.006, 0, 0.022), V(sep - R, 0, 0.012), 6), wr, seg=5)
    for s_ in (-1, 1):
        x0 = s_ * (sep + R)
        if not folded:
            f.tube(M['brass'], [V(x0, 0, 0.008), V(x0 + s_ * 0.002, 0.04, 0.008), V(x0 + s_ * 0.002, 0.1, 0.007), V(x0 + s_ * 0.002, 0.122, -0.0), V(x0 + s_ * 0.002, 0.126, -0.01)], wr, seg=5)
        box(M['brass'], None, (0.003, 0.003, 0.003), M=f.M @ Matrix.Translation((x0, 0.001, 0.008)), bev=0.0004)
    return f


# ------------------------------------------------------------------ oil lamp
def oil_lamp(pos, sc=1.0, name=None, inten=1.2, dist=6.5, lit=True):
    p = Vector(pos)
    s = sc
    # brass foot + stem
    lathe(M['brass'], p, [(0.001, 0), (0.05 * s, 0), (0.054 * s, 0.004 * s), (0.05 * s, 0.01 * s), (0.036 * s, 0.018 * s), (0.02 * s, 0.03 * s),
                          (0.012 * s, 0.04 * s), (0.015 * s, 0.05 * s), (0.026 * s, 0.056 * s), (0.001, 0.056 * s)], seg=28, col=(1, 0.95, 0.9))
    # glass font
    zf = 0.056 * s
    fp = [(0.001, zf), (0.026 * s, zf), (0.05 * s, zf + 0.018 * s), (0.062 * s, zf + 0.045 * s), (0.06 * s, zf + 0.07 * s), (0.045 * s, zf + 0.095 * s),
          (0.026 * s, zf + 0.108 * s), (0.02 * s, zf + 0.113 * s), (0.018 * s, zf + 0.113 * s), (0.016 * s, zf + 0.108 * s), (0.022 * s, zf + 0.098 * s),
          (0.04 * s, zf + 0.086 * s), (0.053 * s, zf + 0.068 * s), (0.055 * s, zf + 0.047 * s), (0.044 * s, zf + 0.022 * s), (0.001, zf + 0.007 * s)]
    lathe(M['glass'], p, fp, seg=32, cap=False)
    # oil
    lathe(M['glass_amber'], p, [(0.001, zf + 0.012 * s), (0.04 * s, zf + 0.012 * s), (0.051 * s, zf + 0.032 * s), (0.053 * s, zf + 0.05 * s), (0.001, zf + 0.05 * s)], seg=28, cap=False)
    # burner
    zb = zf + 0.113 * s
    lathe(M['brass'], p, [(0.001, zb - 0.002), (0.022 * s, zb - 0.002), (0.026 * s, zb + 0.002 * s), (0.02 * s, zb + 0.012 * s), (0.014 * s, zb + 0.016 * s), (0.02 * s, zb + 0.022 * s),
                           (0.022 * s, zb + 0.028 * s), (0.02 * s, zb + 0.03 * s), (0.014 * s, zb + 0.03 * s), (0.014 * s, zb + 0.02 * s)], seg=22, col=(1, 0.95, 0.9))
    # gallery (chimney holder) - 3 prongs
    for i in range(3):
        a = i * TAU / 3 + 0.5
        tube(M['brass'], [p + V(math.cos(a) * 0.022 * s, math.sin(a) * 0.022 * s, zb + 0.026 * s), p + V(math.cos(a) * 0.03 * s, math.sin(a) * 0.03 * s, zb + 0.036 * s)], 0.0016, seg=4)
    # wick + wheel
    box(M['felt'], None, (0.016 * s, 0.0035, 0.012 * s), M=Matrix.Translation(p + V(0, 0, zb + 0.034 * s)), bev=0.0005, col=(0.85, 0.8, 0.65))
    cyl(M['brass'], p + V(0.028 * s, 0, zb + 0.006 * s), 0.009 * s, 0.003, axis='x', seg=12)
    tube(M['brass'], [p + V(0.02 * s, 0, zb + 0.006 * s), p + V(0.027 * s, 0, zb + 0.006 * s)], 0.0015, seg=4)
    # chimney glass
    zc = zb + 0.03 * s
    cp = [(0.0225 * s, zc), (0.022 * s, zc + 0.02 * s), (0.028 * s, zc + 0.04 * s), (0.034 * s, zc + 0.06 * s), (0.027 * s, zc + 0.085 * s), (0.02 * s, zc + 0.115 * s),
          (0.018 * s, zc + 0.15 * s), (0.0215 * s, zc + 0.16 * s), (0.0225 * s, zc + 0.161 * s), (0.0195 * s, zc + 0.152 * s), (0.0175 * s, zc + 0.115 * s), (0.0255 * s, zc + 0.085 * s),
          (0.032 * s, zc + 0.06 * s), (0.0265 * s, zc + 0.04 * s), (0.0205 * s, zc + 0.02 * s), (0.0205 * s, zc)]
    lathe(M['glass'], p, cp, seg=30, cap=False)
    if lit:
        n = flame(p + V(0, 0, zb + 0.058 * s), sc=1.9 * s, inten=inten, dist=dist, name=name, lpos=p + V(0, 0, zb + 0.07 * s))
    # carry handle ring
    tube(M['brass'], arcpts(p + V(-0.06 * s, 0, zf + 0.04 * s), 0.025 * s, 120, 240, 8, 'xz')[::-1][::-1], 0.0022, seg=5) if False else None
    return zc + 0.16 * s


# ------------------------------------------------------------------ simple vessels
def jar(pos, r=0.045, h=0.11, content=None, lid=True, lidcol=(0.7, 0.55, 0.3), glassmat='glass', seed=0):
    p = Vector(pos)
    pr = [(r * 0.85, 0.0), (r, 0.004), (r * 1.02, h * 0.08), (r * 1.02, h * 0.75), (r * 0.9, h * 0.88), (r * 0.62, h * 0.93), (r * 0.62, h),
          (r * 0.58, h), (r * 0.58, h * 0.93), (r * 0.86, h * 0.86), (r * 0.98, h * 0.72), (r * 0.98, h * 0.1), (r * 0.8, 0.005)]
    lathe(M[glassmat], p, pr, seg=22, cap=False)
    if content:
        c = C(content[1]) if isinstance(content[1], str) else content[1]
        lathe(M['foliage'], p, [(r * 0.8, 0.006), (r * 0.97, h * 0.1), (r * 0.97, h * content[0] * 0.8), (r * 0.5, h * content[0] * 0.8), (0.001, h * content[0] * 0.8)], seg=18, cap=False, col=c)
    if lid:
        lathe(M['brass'], p, [(r * 0.66, h - 0.004), (r * 0.66, h + 0.008), (r * 0.5, h + 0.01), (0.001, h + 0.01)], seg=18, col=lidcol, cap=False)


def bowl(pos, r=0.08, h=0.05, col=(1, 1, 1), mat='ceramic', inner=None, seg=24, cfn=None):
    p = Vector(pos)
    pr = [(0.001, 0), (r * 0.5, 0), (r * 0.55, 0.003), (r * 0.9, h * 0.5), (r, h), (r * 0.985, h + 0.0015), (r * 0.955, h), (r * 0.85, h * 0.5), (r * 0.5, 0.005), (0.001, 0.004)]
    lathe(M[mat], p, pr, seg=seg, col=col, cap=False, cfn=cfn)


def vase_dried(pos, h=0.22, r=0.05, seed=3, vcol='#3e6a66', stems=14):
    rr = random.Random(seed)
    p = Vector(pos)
    pr = [(0.001, 0), (r * 0.6, 0), (r * 0.7, 0.004), (r, h * 0.3), (r * 0.95, h * 0.5), (r * 0.5, h * 0.78), (r * 0.36, h * 0.9), (r * 0.46, h), (r * 0.5, h + 0.004),
          (r * 0.4, h + 0.004), (r * 0.32, h * 0.96), (r * 0.33, h * 0.88), (r * 0.8, h * 0.5)]
    cc = C(vcol)
    lathe(M['ceramic'], p, pr, seg=24, cfn=lambda q: shade(cc, 0.92 + 0.12 * nz(q.x * 30, q.y * 30, q.z * 40)))
    for i in range(stems):
        a = rr.uniform(0, TAU); sp = rr.uniform(0.01, 0.075); L = rr.uniform(0.18, 0.34)
        top = p + V(math.cos(a) * sp, math.sin(a) * sp, h + L)
        base = p + V(math.cos(a) * 0.01, math.sin(a) * 0.01, h * 0.8)
        pts = [base, base + (top - base) * 0.5 + V(rr.uniform(-0.01, 0.01), rr.uniform(-0.01, 0.01), 0), top]
        sc_ = rr.choice([(0.72, 0.62, 0.4), (0.6, 0.5, 0.3), (0.55, 0.42, 0.28)])
        tube(M['foliage'], pts, [0.0012, 0.0014, 0.0011], seg=4, col=sc_, caps=False)
        kind = rr.choice(['wheat', 'ball', 'lav', 'ball'])
        if kind == 'ball':
            sphere(M['foliage'], top, 0.011, seg=8, rings=5, col=rr.choice([(0.65, 0.35, 0.25), (0.8, 0.7, 0.45), (0.55, 0.4, 0.5)]))
        elif kind == 'wheat':
            for k in range(7):
                lathe(M['foliage'], top + V(0, 0, -0.012 + 0.008 * k), [(0.001, 0), (0.0055, 0.006), (0.001, 0.016)], seg=5, cap=False, col=(0.85, 0.7, 0.35), rot=(rr.uniform(-12, 12) + (20 if k % 2 else -20), rr.uniform(-12, 12), 0))
        else:
            for k in range(8):
                sphere(M['foliage'], top + V(0.0006 * k, 0, -0.008 * k * 0.8 + 0.01), 0.0045, seg=5, rings=3, sq=(1, 1, 1.4), col=(0.55, 0.45, 0.7))
        if rr.random() < 0.7:
            q = base + (top - base) * rr.uniform(0.2, 0.5)
            lathe(M['foliage'], q, [(0.001, 0), (0.012, 0.025), (0.001, 0.07)], seg=4, cap=False, col=(0.5, 0.52, 0.3), rot=(rr.uniform(40, 80), 0, rr.uniform(0, 360)))


def photo_frame(pos, rot, w=0.12, h=0.16, tilt=12, seed=0, fmat='wood_dark', fcol=(0.8, 0.6, 0.45), standing=True, photo_tone=None):
    """small standing photo frame (faces local +y, leans back by `tilt`) with easel leg and a toned photograph."""
    rr = random.Random(seed)
    p = Vector(pos)
    f = Fr(p, rot, None)
    Mt = f.M @ rotm((tilt if standing else 0, 0, 0))
    ft = 0.012; fd = 0.014
    for (cx, cz, sx, sz) in ((0, h - ft / 2, w, ft), (0, ft / 2, w, ft), (-w / 2 + ft / 2, h / 2, ft, h - 2 * ft), (w / 2 - ft / 2, h / 2, ft, h - 2 * ft)):
        box(M[fmat], None, (sx, fd, sz), M=Mt @ Matrix.Translation((cx, 0, cz)), bev=0.0018, col=fcol)
    box(M['paper'], None, (w - 0.02, 0.002, h - 0.02), M=Mt @ Matrix.Translation((0, 0.003, h / 2)), bev=0.0, col=(0.9, 0.87, 0.78))
    ph = photo_tone or rr.choice([(0.55, 0.5, 0.42), (0.42, 0.45, 0.44), (0.5, 0.42, 0.36)])
    iw, ih = w - 0.034, h - 0.034
    z0 = (h - ih) / 2
    nx, nz = 5, 6
    bm = bmesh.new()
    ul = bm.loops.layers.uv.new('UVMap')
    Vv = [[bm.verts.new((-iw / 2 + iw * i / nx, 0.0045, z0 + ih * j / nz)) for j in range(nz + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(nz):
            fc = bm.faces.new([Vv[i][j], Vv[i][j + 1], Vv[i + 1][j + 1], Vv[i + 1][j]])
            for l in fc.loops:
                l[ul].uv = (0, 0)
    Mi = Mt.inverted()
    def pc(q):
        lq = Mi @ q
        u = lq.x / iw + 0.5; v = (lq.z - z0) / ih
        sky = 0.62 + 0.3 * v
        blob = math.exp(-((u - 0.5) ** 2 / 0.05 + (v - 0.5) ** 2 / 0.09))
        k = sky * (1 - 0.8 * blob) * (0.85 + 0.2 * nz_(u * 9, v * 9))
        return (ph[0] * k * 0.55, ph[1] * k * 0.55, ph[2] * k * 0.55)
    put(M['photo'], bm, Mt, (1, 1, 1), pc, 2, uv_abs=True)
    bm.free()
    if standing:
        tube(M['wood_dark'], [Mt @ V(0, -0.007, h * 0.82), f.M @ V(0, -h * 0.55 * math.sin(math.radians(tilt)) - 0.045, 0.002)], 0.0025, seg=4, col=fcol)


nz_ = nz


def figurine_bird(pos, rot=0, col='#c8b080', seed=0):
    p = Vector(pos); f = Fr(p, rot, None)
    c = C(col)
    f.lathe(M['ceramic'], (0, 0, 0.0), [(0.001, 0), (0.018, 0), (0.02, 0.004), (0.017, 0.008), (0.001, 0.008)], seg=14, col=shade(c, 0.6))
    # body
    sphere(M['ceramic'], f.p(V(0, 0, 0.034)), 0.026, seg=16, rings=10, sq=(0.8, 1.35, 1.0), rot=(-18, 0, rot), col=c)
    sphere(M['ceramic'], f.p(V(0, -0.025, 0.056)), 0.0145, seg=12, rings=8, col=c)
    lathe(M['ceramic'], f.p(V(0, -0.037, 0.0565)), [(0.0035, 0), (0.001, 0.016)], seg=6, cap=False, col=(0.85, 0.6, 0.2), rot=(90, 0, rot))
    # tail
    lathe(M['ceramic'], f.p(V(0, 0.03, 0.04)), [(0.001, 0), (0.012, 0.01), (0.008, 0.035), (0.001, 0.04)], seg=6, cap=False, col=shade(c, 0.85), rot=(-80, 0, rot), scale=(1.0, 0.35, 1.0))
    for s_ in (-1, 1):
        sphere(M['ink'], f.p(V(s_ * 0.0085, -0.031, 0.0595)), 0.0022, seg=5, rings=3)
        sphere(M['ceramic'], f.p(V(s_ * 0.023, 0.002, 0.036)), 0.02, seg=10, rings=6, sq=(0.25, 0.9, 0.6), rot=(0, 0, rot + s_ * 8), col=shade(c, 0.78))


def globe(pos, r=0.055, seed=2):
    p = Vector(pos)
    rr = random.Random(seed)
    cyl(M['wood_dark'], p + V(0, 0, 0.006), 0.045, 0.012, seg=20, bev=0.003, col=(0.7, 0.5, 0.35))
    tube(M['wood_dark'], [p + V(0, 0, 0.012), p + V(0, 0, 0.05)], [0.007, 0.0045], seg=8, col=(0.7, 0.5, 0.35))
    zc = 0.012 + 0.05 + r * 0.55
    c = p + V(0, 0, zc)
    # meridian ring (brass)
    ring = [c + Matrix.Rotation(math.radians(23), 3, 'Y') @ V(math.cos(a) * (r + 0.007), 0, math.sin(a) * (r + 0.007)) for a in [i * TAU / 32 for i in range(33)]]
    tube(M['brass'], ring, 0.0025, seg=6, caps=False)
    def land(q):
        l = q - c
        a = fbm(l.x * 22, l.y * 22, l.z * 22, 1.0, seed, 3)
        if a > 0.08:
            return (0.62, 0.58, 0.36) if abs(l.z) < r * 0.8 else (0.8, 0.78, 0.7)
        return (0.28, 0.46, 0.55)
    sphere(M['ceramic'], c, r, seg=32, rings=20, cfn=land, rot=(23, 0, 0))
    for s_ in (-1, 1):
        lathe(M['brass'], c + Matrix.Rotation(math.radians(23), 3, 'Y') @ V(0, 0, s_ * (r + 0.003)), [(0.001, -0.003), (0.006, -0.003), (0.006, 0.003), (0.001, 0.003)], seg=8, cap=False)


def bottle(pos, r=0.03, h=0.22, liquid=0.55, glassmat='glass_amber', col=None, cork=True):
    p = Vector(pos)
    pr = [(r * 0.8, 0), (r, 0.003), (r * 1.01, h * 0.1), (r * 1.01, h * 0.5), (r * 0.9, h * 0.62), (r * 0.42, h * 0.76), (r * 0.36, h * 0.9), (r * 0.42, h * 0.96), (r * 0.44, h),
          (r * 0.3, h), (r * 0.3, h * 0.92), (r * 0.34, h * 0.78), (r * 0.85, h * 0.62), (r * 0.95, h * 0.5), (r * 0.95, h * 0.1), (r * 0.7, 0.004)]
    lathe(M[glassmat], p, pr, seg=22, cap=False)
    lathe(M['tea'], p, [(r * 0.7, 0.005), (r * 0.93, h * 0.1), (r * 0.93, h * liquid), (0.001, h * liquid)], seg=20, cap=False, col=col or (0.5, 0.2, 0.08))
    if cork:
        lathe(M['wood_pine'], p, [(r * 0.3, h * 0.94), (r * 0.3, h + 0.012), (r * 0.36, h + 0.014), (r * 0.36, h + 0.02), (0.001, h + 0.02)], seg=10, col=(0.8, 0.65, 0.45), cap=False)


def contact_shadow(cx, cy, w, d, rot=0.0, z=0.0, layers=3, spread=0.035, rr=0.06, alpha_mat='contact_shadow'):
    """soft stepped contact shadow on the floor under furniture (stacked translucent rounded rectangles)."""
    for k in range(layers):
        e = spread * (k + 0.2) / layers * 2.0
        pts = rrect(w + 2 * e, d + 2 * e, rr + e, 5)
        bm = bmesh.new()
        ul = bm.loops.layers.uv.new('UVMap')
        vs = [bm.verts.new((p.x, p.y, 0.0)) for p in pts]
        ctr = bm.verts.new((0, 0, 0))
        for j in range(len(vs)):
            fc = bm.faces.new([ctr, vs[j], vs[(j + 1) % len(vs)]])
            for l in fc.loops:
                l[ul].uv = (0, 0)
        put(M[alpha_mat], bm, xf((cx, cy, F + z + 0.0012 + 0.0006 * k), (0, 0, rot)), (0, 0, 0), None, 2, uv_abs=True)
        bm.free()
