from water_common import *


# ---------------------------------------------------------------- cattail
def cattail(v, rng):
    g = Geo()
    nl = {'a': 6, 'b': 5, 'c': 7}[v]
    for i in range(nl):
        L = rng.uniform(1.1, 1.65)
        az = rng.uniform(0, TAU)
        p = grass_blade(L, 0.017, rng, bend=(-1.1, -0.45), nu=12, fold=0.5, twist=(-0.9, 0.9),
                        cols=[(0, '#4a7a30'), (0.3, '#6fa43c'), (1, '#88b048')])
        blade_at(g, 'w_leaf', p, (0.004 * math.cos(az), 0.004 * math.sin(az), 0), az, rng.uniform(1.25, 1.5))
    heads = {'a': [1.7, 1.45], 'b': [1.85], 'c': [1.6, 1.78, 1.35]}[v]
    for hi, h in enumerate(heads):
        h *= rng.uniform(0.95, 1.05)
        pts = stem_path(h, rng, lean=0.05, sway=0.012, n=9)
        t = np.linspace(0, 1, len(pts))
        g.add('w_stem', tube(pts, 0.0058 - 0.0018 * t, sides=6, cols=grad(t, [(0, '#5a7f32'), (1, '#8aa648')]), lod=False))
        top = pts[-1]
        tan = pathpt(pts, 1.0)[1]
        xf = frame_z(top, tan, rng.uniform(0, TAU))
        HL = rng.uniform(0.12, 0.17)
        R = rng.uniform(0.017, 0.022)
        nz = make_noise(rng.randint(999))

        def prof(u, HL=HL, R=R):
            return R * np.sqrt(np.maximum(1 - (2 * u - 1) ** 8, 0)) * (0.95 + 0.05 * np.sin(u * 6)), HL * u
        g.add('cattail_brown', revolve(prof, 12, 12, lobe=lambda u, th: 1 + 0.05 * np.sin(th * 7 + u * 55) + 0.03 * np.sin(th * 11 - u * 31),
                                      cols=lambda u, th: grad(0.5 + 0.5 * np.sin(u * 40 + th * 3), [(0, '#3a2010'), (1, '#6a4020')]),
                                      lod=False), xf @ T(0, 0, 0.012))
        # male spike above
        sp = np.array([[0, 0, 0.012 + HL - 0.005], [0, 0, 0.012 + HL + 0.04], [0, 0, 0.012 + HL + 0.09]])
        if not (v == 'b' and hi == 0):
            g.add('cattail_spike', tube(sp, [0.0045, 0.0038, 0.0012], sides=6,
                                        cols=grad(np.array([0, 0.5, 1.0]), [(0, '#c0a850'), (1, '#e0c868')]), lod=False), xf)
        # spathe bract
        g.add('w_leaf', blade(0.09, 0.006, nu=4, nv=2, widthfn=TAPER, bend=(0.1, 0.4), lod=False, cols=[(0, '#7a9a40'), (1, '#b0a060')]),
              xf @ orient(np.array([0, 0, 0.012 + HL - 0.006]), np.array([0.3, 0, 1.0]), np.array([0, 0, 1.0])))
    # upright side shoots (sheaths)
    return g


# ---------------------------------------------------------------- reed
def reed(v, rng):
    g = Geo()
    n = {'a': 11, 'b': 9, 'c': 13}[v]
    for i in range(n):
        h = rng.uniform(1.7, 2.5)
        ang = rng.uniform(0, TAU); rr = rng.uniform(0, 0.12) ** 1.0
        base = np.array([rr * math.cos(ang), rr * math.sin(ang), 0])
        pts = stem_path(h, rng, lean=rng.uniform(0.02, 0.12), sway=0.02, n=9, dirang=ang + rng.normal(0, 0.5)) + base
        t = np.linspace(0, 1, len(pts))
        g.add('reed_stem', tube(pts, 0.0048 - 0.0028 * t, sides=4, cols=grad(t, [(0, '#c4b070'), (0.5, '#a8b468'), (1, '#8aa058')]), lod=False))
        nleaf = 5
        for k in range(nleaf):
            tt = 0.12 + 0.8 * k / nleaf + rng.uniform(-0.03, 0.03)
            p = blade(rng.uniform(0.38, 0.6) * (1 - 0.3 * tt), 0.021, nu=8, nv=2, widthfn=TAPER_SOFT, bend=(-1.0, -0.4), fold=0.3,
                      twist=(-0.5, 0.5), cols=[(0, '#5a8a38'), (0.5, '#7aa648'), (1, '#9ab25a')], mid=0.25, lod=False)
            leaf_on_path(g, 'w_leaf', pts, tt, k * 2.4 + rng.uniform(-0.3, 0.3), rng.uniform(0.45, 0.85), p)
        if rng.rand() < (0.75 if v != 'b' else 0.5):
            top = pts[-1]; tan = pathpt(pts, 1.0)[1]
            xf = frame_z(top, unit(tan + np.array([rng.normal(0, 0.3), rng.normal(0, 0.3), 0])), rng.uniform(0, TAU))
            axis = bez([0, 0, 0], [0, 0, 0.08], [0.04, 0, 0.16], [0.09, 0, 0.2], 6)
            g.add('reed_stem', tube(axis, np.linspace(0.0022, 0.0008, 6), sides=3, lod=False), xf)
            for k in range(14):
                tt = 0.15 + 0.8 * k / 14
                pos, tn = pathpt(axis, tt)
                az = k * 2.4
                lat = np.array([math.cos(az), math.sin(az), 0])
                yd = unit(lat * 0.7 + tn * 0.75 + np.array([0, 0, -0.1 * 0]))
                M = orient(pos, yd, np.array([0, 0, 1.0]))
                p = blade(0.085 * (1 - 0.45 * tt) * rng.uniform(0.8, 1.15), 0.017, nu=4, nv=2, widthfn=lambda u: np.clip(1 - u ** 1.6, 0, 1) ** 0.7,
                          bend=(-0.9, -0.3), cols=[(0, '#8a6a58'), (0.5, '#b09078'), (1, '#d4c4a8')], lod=False, fold=0.1)
                g.add('reed_plume', p, xf @ M)
    return g


# ---------------------------------------------------------------- yellow flag iris
def iris_flower(g, xf, rng, scale=1.0, open_=1.0):
    s = scale
    petal_ring(g, 'iris_petal', 3, 0.062 * s, 0.05 * s, rng, r0=0.004, z0=0.0, elev=(-0.35, -0.15), elev_j=0.03, xf=xf, yaw0=0.3, jit=0.05,
               a=0.55, b=0.45, nu=5, nv=4, bend=(-0.9, -0.55), cup=0.25, wave=0.14, wavef=2.2, notch=0.03,
               cols=[(0, '#6a3c10'), (0.15, '#e8a010'), (0.4, '#f7cf1c'), (1, '#f9d92a')], mid=-0.08, edge=0.05)
    petal_ring(g, 'iris_petal', 3, 0.042 * s, 0.013 * s, rng, r0=0.004, z0=0.002, elev=(1.0, 1.25), xf=xf, yaw0=0.3 + PI / 3, jit=0.05,
               a=0.7, b=0.5, nu=4, nv=2, bend=(-0.25, 0.15), cup=0.3, cols=[(0, '#d8a010'), (1, '#f8d224')])
    petal_ring(g, 'iris_style', 3, 0.044 * s, 0.022 * s, rng, r0=0.003, z0=0.004, elev=(0.45, 0.6), xf=xf, yaw0=0.3, jit=0.03,
               a=0.6, b=0.45, nu=4, nv=2, bend=(0.15, 0.45), cup=0.35, wave=0.05, cols=[(0, '#f4d440'), (1, '#f9e060')])


def iris_yellow(v, rng):
    g = Geo()
    nl = {'a': 8, 'b': 9, 'c': 7}[v]
    fan_az = rng.uniform(0, TAU)
    for i in range(nl):
        f = (i - (nl - 1) / 2) / ((nl - 1) / 2)
        az = fan_az + f * 0.9 + rng.normal(0, 0.06)
        L = rng.uniform(0.65, 1.0) * (1 - 0.15 * abs(f))
        p = blade(L, 0.027, nu=12, nv=2, widthfn=lambda u: np.clip(1 - u ** 4, 0, 1) * (1 - 0.35 * u) + 0.02, bend=(-0.5, -0.2), fold=0.55,
                  twist=(-0.2, 0.2), cols=[(0, '#7a9a48'), (0.15, '#4a8a3a'), (1, '#5a9a40')], mid=0.25, lod=False, side=(-0.06, 0.06))
        blade_at(g, 'w_leaf', p, (0.006 * math.cos(az) * (i % 3), 0.006 * math.sin(az), 0), az + rng.normal(0, 0.15), rng.uniform(1.2, 1.4))
    spec = {'a': [(1.05, 'f'), (0.8, 'f')], 'b': [(1.15, 'f'), (0.95, 'f'), (0.78, 'b')], 'c': [(1.1, 'f'), (0.9, 'b'), (0.6, 'p')]}[v]
    main = stem_path(spec[0][0], rng, lean=0.1, sway=0.03, n=9)
    t = np.linspace(0, 1, len(main))
    g.add('w_stem', tube(main, 0.0055 - 0.002 * t, sides=6, cols=grad(t, [(0, '#5a8a38'), (1, '#8aac48')]), lod=False))
    for k, (h, kind) in enumerate(spec):
        if k == 0:
            pts = main
        else:
            pts = side_branch_w(main, 0.5 + 0.12 * k, rng, h - 0.5)
            tt = np.linspace(0, 1, len(pts))
            g.add('w_stem', tube(pts, 0.0038 - 0.0015 * tt, sides=5, cols=grad(tt, [(0, '#5a8a38'), (1, '#8aac48')]), lod=False))
        pos = pts[-1]; tan = pathpt(pts, 1.0)[1]
        nod = unit(tan + np.array([rng.normal(0, 0.35), rng.normal(0, 0.35), 0.0]))
        xf = frame_z(pos, nod, rng.uniform(0, TAU))
        if kind == 'f':
            iris_flower(g, xf, rng, scale=rng.uniform(0.9, 1.05))
            g.add('iris_bud', ellipsoid(0.01, 0.01, 0.018, nu=4, nseg=8, lod=False), xf @ T(0, 0, -0.012))
        elif kind == 'b':
            g.add('iris_petal', ellipsoid(0.011, 0.011, 0.04, nu=6, nseg=8, cols=lambda u, th: grad(u, [(0, '#7aa040'), (0.6, '#c8c040'), (1, '#e8d030')]), lod=False), xf @ T(0, 0, 0.02))
            g.add('iris_bud', blade(0.055, 0.016, nu=5, nv=2, widthfn=TAPER, bend=(0.05, 0.2), cols=[(0, '#7a9a40'), (1, '#a0b050')], lod=False),
                  xf @ orient(np.array([0, 0, 0.0]), np.array([0.4, 0, 1.0]), np.array([0, 0, 1.0])))
        else:  # seed pod
            pp = np.array([[0, 0, 0.0], [0, 0, 0.05]])
            g.add('iris_bud', ellipsoid(0.013, 0.013, 0.035, nu=6, nseg=6, cols=lambda u, th: grad(u, [(0, '#5a8a38'), (1, '#8aa848')]), lod=False), xf @ T(0, 0, 0.03))
    return g


def side_branch_w(pts, t, rng, length, out=0.35):
    pos, tan = pathpt(pts, t)
    az = rng.uniform(0, TAU)
    rad = np.array([math.cos(az), math.sin(az), 0.0]); Z = np.array([0, 0, 1.0])
    p3 = pos + rad * length * out + Z * length
    return bez(pos, pos + rad * length * out * 0.8 + Z * length * 0.1, p3 - Z * length * 0.35, p3, 6)


# ---------------------------------------------------------------- lily pad
def pad_patch(R, rng, notch=0.35, rot=0.0, segs=30, rings=4, rim=0.008, wave=0.004):
    th = np.linspace(rot + notch / 2, rot + TAU - notch / 2, segs + 1)
    u = np.linspace(0, 1, rings + 1)
    U, TH = np.meshgrid(u, th, indexing='ij')
    r = R * U
    nz = make_noise(rng.randint(999))
    zz = 0.003 + rim * U ** 5 + 0.002 * (1 - U) + wave * np.sin(TH * 5 + U * 2) * U ** 2
    P = np.stack([r * np.cos(TH), r * np.sin(TH), zz], -1)
    C = grad(U, [(0, '#5c9a3a'), (0.6, '#3f8434'), (1, '#2f6e2c')])
    vein = 0.85 + 0.15 * np.cos((TH - rot) * 15)
    C = C * vein[..., None] * (1 + 0.15 * np.exp(-((U) / 0.12) ** 2))[..., None]
    return grid(P, C, flip=True)


def lilypad(v, rng):
    g = Geo()
    if v == 'a':
        g.add('lilypad', pad_patch(0.17, rng, rot=rng.uniform(0, TAU)))
    elif v == 'b':
        g.add('lilypad', pad_patch(0.24, rng, notch=0.25, rot=rng.uniform(0, TAU), segs=34))
    elif v == 'c':
        g.add('lilypad', pad_patch(0.15, rng, rot=1.0), T(-0.02, 0.0, 0.0))
        g.add('lilypad', pad_patch(0.1, rng, rot=3.2, rings=3, segs=22), T(0.16, 0.09, 0.004))
    else:
        g.add('lilypad', pad_patch(0.2, rng, notch=0.3, rot=4.0, rim=0.02, wave=0.007, segs=34))
        # curled young leaf
        g.add('lilypad', pad_patch(0.06, rng, notch=0.8, rot=0.5, rings=2, segs=14, rim=0.03), T(0.27, -0.04, 0.0))
    return g


def lily_flower(g, m, rng, cols_out, cols_in, scale=1.0, closed=0.0, n=(5, 7, 8)):
    s = scale
    z0 = 0.006
    yaw = rng.uniform(0, TAU)
    e = closed
    petal_ring(g, 'sepal_w', 4, 0.05 * s, 0.022 * s, rng, r0=0.008 * s, z0=z0, elev=(0.05 + e * 0.6), xf=None, yaw0=yaw, a=0.8, b=0.6, nu=4, nv=2,
               bend=(-0.1, 0.1), cols=[(0, '#6a9a4a'), (1, '#a0b070')]) if False else None
    petal_ring(g, m, n[0], 0.058 * s, 0.024 * s, rng, r0=0.008 * s, z0=z0, elev=(0.06 + e * 0.5, 0.2 + e * 0.5), a=0.75, b=0.6, nu=5, nv=4, bend=(-0.2, 0.2),
               cup=0.3, cols=cols_out, yaw0=yaw, mid=0.03, edge=0.04)
    petal_ring(g, m, n[1], 0.05 * s, 0.024 * s, rng, r0=0.007 * s, z0=z0 + 0.003, elev=(0.35 + e * 0.35, 0.55 + e * 0.35), a=0.75, b=0.55, nu=5, nv=4,
               bend=(0.1, 0.45), cup=0.35, cols=cols_out, yaw0=yaw + 0.4)
    petal_ring(g, m, n[2], 0.036 * s, 0.018 * s, rng, r0=0.005 * s, z0=z0 + 0.006, elev=(0.8 + e * 0.2, 1.05 + e * 0.2), a=0.7, b=0.5, nu=4, nv=2,
               bend=(0.15, 0.45), cup=0.3, cols=cols_in, yaw0=yaw + 0.2)
    g.add('lily_stamen', lobed_disc(0.012 * s, lobes=8, rings=2, segs=16, depth=0.0, cols=lambda u, th: np.ones(u.shape + (3,)) * lin('#e8b818')), T(0, 0, z0 + 0.008))
    petal_ring(g, 'lily_stamen', 26, 0.02 * s, 0.0032 * s, rng, r0=0.004 * s, z0=z0 + 0.008, elev=(0.9, 1.4), a=0.6, b=0.5, nu=2, nv=2, bend=(0.2, 0.5),
               cols=[(0, '#f0c818'), (1, '#f8e040')], lj=0.25)


def waterlily(pink):
    base = 'lily_pink' if pink else 'lily_white'
    co = [(0, '#f6f0a0'), (0.25, '#fbe8ee'), (0.7, '#f7a8c8' if pink else '#fffdfa'), (1, '#f08cb4' if pink else '#fffffc')] if pink else \
        [(0, '#f4ee90'), (0.25, '#fffef0'), (1, '#ffffff')]
    ci = [(0, '#f8f0a0'), (0.3, '#fdeaf0' if pink else '#fffff2'), (1, '#f5a0c4' if pink else '#fffffe')]

    def fn(v, rng):
        g = Geo()
        if v == 'a':
            lily_flower(g, base, rng, co, ci, 1.3)
        elif v == 'b':
            lily_flower(g, base, rng, co, ci, 1.1, closed=0.25, n=(5, 7, 9))
        elif v == 'c':
            lily_flower(g, base, rng, co, ci, 1.5, closed=0.0, n=(6, 8, 9))
        else:
            lily_flower(g, base, rng, co, ci, 1.0, closed=0.6, n=(4, 6, 7))
        # one nearby small pad for context
        g.add('lilypad', pad_patch(0.09, rng, rot=rng.uniform(0, TAU), rings=3, segs=20), T(0.15, -0.07, 0.0))
        return g
    return fn


# ---------------------------------------------------------------- marsh marigold
def marsh_marigold(v, rng):
    g = Geo()
    nl = {'a': 9, 'b': 7, 'c': 11}[v]
    for i in range(nl):
        ang = rng.uniform(0, TAU)
        rad = np.array([math.cos(ang), math.sin(ang), 0.0]); Z = np.array([0, 0, 1.0])
        ln = rng.uniform(0.07, 0.19)
        p0 = rad * 0.005
        p3 = rad * ln * 0.9 + Z * rng.uniform(0.07, 0.15)
        pts = bez(p0, p0 + Z * 0.06, p3 - Z * 0.03 - rad * 0.02, p3, 6)
        g.add('w_stem', tube(pts, np.linspace(0.0024, 0.0014, 6), sides=4, cols=grad(np.linspace(0, 1, 6), [(0, '#5a8a38'), (1, '#88a848')]), lod=False))
        tan = pathpt(pts, 1.0)[1]
        ydir = unit(rad * 0.85 + Z * 0.2)
        M = orient(pts[-1] + ydir * 0.0, ydir, Z) @ Rx(0.0)
        s = rng.uniform(0.7, 1.15)
        p = blade(0.095 * s, 0.105 * s, nu=8, nv=6, a=0.45, b=0.5, baseW=0.42, serr=0.06, cup=0.1, bend=(-0.5, -0.1), wave=0.06, wavef=2,
                  cols=[(0, '#2f6a2a'), (0.5, '#3a8030'), (1, '#4a9038')], mid=0.25, edge=0.1, lod=False)
        g.add('w_leaf_glossy', p, M @ T(0, -0.012 * s, 0))
    nf = {'a': 3, 'b': 4, 'c': 2}[v]
    for k in range(nf):
        h = rng.uniform(0.2, 0.3)
        pts = stem_path(h, rng, lean=0.25, sway=0.05, n=6, dirang=rng.uniform(0, TAU)) + np.array([0, 0, 0.02])
        pts[0, 2] = 0
        gstem_w(g, pts, 0.0028, 0.002)
        xf = frame_z(pts[-1], unit(pathpt(pts, 1.0)[1] + np.array([0.2, 0.0, 0.3])), rng.uniform(0, TAU))
        petal_ring(g, 'marigold_petal', 5 + (k % 2), 0.028, 0.026, rng, r0=0.002, z0=0.0, elev=(0.85, 1.1), a=0.5, b=0.3, nu=5, nv=4, bend=(0.1, 0.5), cup=0.45,
                   xf=xf, cols=[(0, '#d8a010'), (0.3, '#ffd020'), (1, '#ffe040')], mid=-0.04, lj=0.08)
        petal_ring(g, 'stamen_yellow_w', 22, 0.009, 0.0012, rng, r0=0.002, z0=0.001, elev=(1.0, 1.4), xf=xf, a=0.6, b=0.5, nu=2, nv=2, bend=(0.1, 0.5),
                   cols=[(0, '#d8c020'), (1, '#f8e040')], lj=0.3)
        g.add('leaf_green_w', ellipsoid(0.004, 0.004, 0.005, nu=3, nseg=6, cols=lambda u, th: np.ones(u.shape + (3,)) * lin('#7aa030'), lod=False), xf @ T(0, 0, 0.003))
        if k == 0 and v != 'c':
            # bud
            bp = side_branch_w(pts, 0.6, rng, 0.08)
            gstem_w(g, bp, 0.0016, 0.0012)
            bx = frame_z(bp[-1], pathpt(bp, 1.0)[1], 0)
            g.add('marigold_petal', ellipsoid(0.0075, 0.0075, 0.011, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#8aa830'), (0.6, '#d8c820'), (1, '#f0d818')]), lod=False), bx @ T(0, 0, 0.006))
    return g


def gstem_w(g, pts, r0, r1, sides=5):
    t = np.linspace(0, 1, len(pts))
    g.add('w_stem', tube(pts, r0 + (r1 - r0) * t, sides=sides, cols=grad(t, [(0, '#5a8a38'), (1, '#88aa48')]), lod=False))


def init_extra_mats():
    mat('sepal_w', '#8ab060', rough=0.55)
    mat('stamen_yellow_w', '#f4d23a', rough=0.6)
    mat('leaf_green_w', '#7aa030', rough=0.5)


DEFS = [
    dict(sp='cattail', fn=cattail, variants=['a', 'b', 'c'], ko='부들', weight=0.8, habitat='water_edge', sway=0.45),
    dict(sp='reed', fn=reed, variants=['a', 'b', 'c'], ko='갈대', weight=0.9, habitat='water_edge', sway=0.5),
    dict(sp='iris_yellow', fn=iris_yellow, variants=['a', 'b', 'c'], ko='노랑꽃창포', weight=0.5, habitat='water_edge', sway=0.35),
    dict(sp='lilypad', fn=lilypad, variants=['a', 'b', 'c', 'd'], ko='수련 잎', weight=1.0, habitat='water_edge', sway=0.0),
    dict(sp='waterlily_white', fn=None, variants=['a', 'b', 'c', 'd'], ko='흰수련', weight=0.35, habitat='water_edge', sway=0.0),
    dict(sp='waterlily_pink', fn=None, variants=['a', 'b', 'c', 'd'], ko='분홍수련', weight=0.25, habitat='water_edge', sway=0.0),
    dict(sp='marsh_marigold', fn=marsh_marigold, variants=['a', 'b', 'c'], ko='동의나물', weight=0.5, habitat='wet', sway=0.2),
]
DEFS[4]['fn'] = waterlily(False)
DEFS[5]['fn'] = waterlily(True)
