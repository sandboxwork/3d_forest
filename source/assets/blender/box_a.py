from box_common import *


def W(xf, pts):
    return xfv(xf, np.asarray(pts))


def petunia_leaf(g, p, rng, L=0.035):
    d = unit(np.array([rng.normal(), rng.normal(), 0.5 + rng.uniform(0, 0.5)]))
    n = unit(d + UP * 0.8)
    g.add('leaf_small', blade(L * rng.uniform(0.8, 1.2), L * 0.5, nu=3, nv=2, a=0.6, b=0.7, bend=-0.3, fold=0.2, cols=[(0, '#3a7028'), (1, '#6aa83c')], mid=0.2, lod=False),
          orient(p, d, n))


# ------------------------------------------------------------------ flower box
def flower_box(v, rng):
    g = Geo()
    X, Y, Z = 1.1, 0.25, 0.22
    wt = 0.018
    # wooden planter
    g.add('planter_wood', cuboid((0, -Y / 2 + wt / 2, 0.11 + 0.008), (X, wt, 0.098), col=lin('#d2a878') * 0.9))
    g.add('planter_wood', cuboid((0, -Y / 2 + wt / 2, 0.11 + 0.008 + 0.105), (X, wt, 0.098), col=lin('#c79c6c') * 0.95))
    g.add('planter_wood', cuboid((0, -Y / 2 + wt / 2, 0.11), (X, wt * 0.9, 0.012), col=lin('#5a3c26')))
    g.add('planter_wood', cuboid((0, Y / 2 - wt / 2, 0.11), (X, wt, Z), col=lin('#a8825a')))
    for sx in (-1, 1):
        g.add('planter_wood', cuboid((sx * (X / 2 - wt / 2), 0, 0.11), (wt, Y - 0.002, Z), col=lin('#b48c5e')))
    g.add('planter_wood', cuboid((0, 0, 0.008), (X - 0.02, Y - 0.02, 0.016), col=lin('#6a4a30')))
    # trim rail
    g.add('planter_wood_dark', cuboid((0, -Y / 2 + wt / 2 - 0.003, Z - 0.006), (X + 0.012, wt + 0.006, 0.012), col=lin('#d8b48a') * 0.85))
    for sx in (-1, 1):
        for x in (sx * 0.48,):
            g.add('planter_wood_dark', cuboid((x, -Y / 2 - 0.004, 0.11), (0.03, 0.008, Z - 0.02), col=lin('#8a6a46')))
    # soil
    g.add('soil_dark', cuboid((0, 0, 0.1), (X - 0.04, Y - 0.04, 0.18), col=lin('#3c2a1e')))
    g.add('soil_dark', box_soil_top(-X / 2 + 0.02, X / 2 - 0.02, -Y / 2 + 0.02, Y / 2 - 0.02, 0.194, rng))
    pal = {'a': ['purple', 'pink', 'violet', 'purple', 'magenta', 'pink'], 'b': ['white', 'salmon', 'white', 'pink', 'white', 'red']}[v]
    geo_col = {'a': ['#d8242a', '#e0303a'], 'b': ['#f26a52', '#f58a70', '#e84a4a']}[v]
    sz = 0.194
    # geranium clumps at back
    xs = np.linspace(-0.4, 0.4, 4) + rng.uniform(-0.03, 0.03, 4)
    for i, x in enumerate(xs):
        base = np.array([x, 0.05 + rng.uniform(-0.01, 0.02), sz])
        for k in range(8):
            az = k * 2.4 + rng.uniform(0, 1)
            rad = np.array([math.cos(az), math.sin(az), 0])
            tip = base + rad * rng.uniform(0.03, 0.065) + UP * rng.uniform(0.07, 0.11)
            tip[1] = min(tip[1], 0.1)
            stalk(g, base, tip, r=0.0014, m='stem_green')
            geranium_leaf(g, tip, unit(UP * 1.0 + rad * 0.3), rng, R=rng.uniform(0.032, 0.042))
        for k in range(2):
            c = base + np.array([rng.uniform(-0.04, 0.04), rng.uniform(-0.01, 0.03), rng.uniform(0.15, 0.2)])
            stalk(g, base + UP * 0.02, c - UP * 0.03, r=0.0018)
            geranium_umbel(g, c, unit(UP + np.array([0, -0.4, 0])), rng, col=geo_col[(i + k) % len(geo_col)], n=16, R=0.036, fl=0.014)
    # dense foliage: scalloped leaves
    for k in range(46):
        p = np.array([rng.uniform(-0.51, 0.51), rng.uniform(-0.09, 0.085), sz + rng.uniform(0.01, 0.05)])
        geranium_leaf(g, p, unit(UP + rng.normal(0, 0.35, 3) * np.array([1, 1, 0.3])), rng, R=rng.uniform(0.028, 0.04))
    # petunias
    n_pet = 26 if v == 'a' else 22
    xs = np.linspace(-0.48, 0.48, n_pet) + rng.uniform(-0.012, 0.012, n_pet)
    for i, x in enumerate(xs):
        front = i % 2 == 0
        y = -0.065 + rng.uniform(-0.02, 0.02) if front else 0.0 + rng.uniform(-0.02, 0.02)
        base = np.array([x, y, sz])
        h = rng.uniform(0.05, 0.085) if front else rng.uniform(0.08, 0.125)
        axis = unit(np.array([rng.normal(0, 0.25), -0.75 if front else -0.45, 0.8]))
        pos = base + np.array([0, -0.03 if front else -0.01, h])
        stalk(g, base, pos, r=0.0016)
        petunia(g, pos, axis, rng, size=rng.uniform(0.9, 1.15), color=pal[i % len(pal)])
        for k in range(3):
            q = base + (pos - base) * rng.uniform(0.3, 0.8) + np.array([rng.normal(0, 0.008), rng.normal(0, 0.008), 0])
            petunia_leaf(g, q, rng, 0.04)
    # extra leaf filler on soil
    for k in range(12):
        p = np.array([rng.uniform(-0.5, 0.5), rng.uniform(-0.09, 0.09), sz + rng.uniform(0.0, 0.03)])
        petunia_leaf(g, p, rng, 0.04)
    # pansies
    n_p = 12
    for i in range(n_p):
        x = -0.48 + 0.96 * (i + rng.uniform(0, 0.8)) / n_p
        base = np.array([x, -0.085 + rng.uniform(-0.01, 0.01), sz])
        pos = base + np.array([0, -0.03, rng.uniform(0.03, 0.06)])
        stalk(g, base, pos, r=0.001, n=3)
        pansy(g, pos, unit(np.array([rng.normal(0, 0.2), -1.0, 0.45])), rng, size=1.0, scheme=rng.randint(0, 4) if v == 'a' else rng.choice([1, 1, 3, 0]))
        for k in range(2):
            petunia_leaf(g, base + UP * 0.012 + np.array([rng.normal(0, 0.012), rng.normal(0, 0.01), 0]), rng, 0.028)
    # lobelia mounds (blue) near front edge
    for c in np.linspace(-0.42, 0.42, 6) + rng.uniform(-0.03, 0.03, 6):
        cx = np.array([c, -0.095, sz + 0.03])
        g.add('leaf_small', ellipsoid(0.035, 0.03, 0.028, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#2f6226'), (1, '#4f8a30')])), T(cx))
        for k in range(9):
            d = unit(np.array([rng.normal(), rng.normal() - 0.6, rng.uniform(0.2, 1.0)]))
            pos = cx + d * 0.038
            col = lin('#2d4fd8') if v == 'a' else lin('#f6f2ff')
            g.add('petal_soft', lobed_disc(0.0085, 5, 1, 10, depth=0.35, cup=0.3,
                  cols=lambda u, th, col=col: np.where((u < 0.3)[..., None], lin('#f4f4ff'), col), lod=False), frame_z(pos, d, rng.uniform(0, TAU)))
    # trailing ivy
    n_iv = 8
    for i in range(n_iv):
        x = -0.45 + 0.9 * (i + rng.uniform(0.1, 0.9)) / n_iv
        Ls = rng.uniform(0.22, 0.38)
        sx = rng.uniform(-0.05, 0.05)
        pts = bez((x, -0.06, sz), (x, -0.16, 0.27), (x + sx, -0.15, 0.17), (x + sx * 2, -0.142, 0.2 - Ls), 11)
        pts[:, 0] += 0.012 * np.sin(np.linspace(0, 6, 11) + i)
        t = np.linspace(0, 1, 11)
        g.add('stem_green', tube(pts, 0.0016 * (1 - 0.5 * t), sides=4, cols=grad(t, [(0, '#4a6a2a'), (1, '#6a8a3a')]), lod=False))
        for j in range(1, 11):
            for s in (-1, 1):
                p = pts[j] + np.array([s * 0.013, -0.006, 0])
                nrm = unit(np.array([s * 0.25, -1.0, 0.25 + rng.uniform(-0.2, 0.3)]))
                ivy_leaf(g, p, nrm, rng, R=0.03 * (1.0 - 0.4 * (j / 10)))
    return g


# ------------------------------------------------------------------ flower pot
def flower_pot(v, rng):
    g = Geo()
    keys = [(0.058, 0.0), (0.064, 0.006), (0.078, 0.06), (0.098, 0.186), (0.107, 0.19), (0.118, 0.198), (0.12, 0.222), (0.108, 0.226), (0.103, 0.213)]
    kr = np.array([k[0] for k in keys]); kz = np.array([k[1] for k in keys])
    idx = np.arange(len(keys))

    def prof(u):
        s = u * (len(keys) - 1)
        return np.interp(s, idx, kr), np.interp(s, idx, kz)
    noise = make_noise(rng.randint(100))

    def cols(u, th):
        c = grad(u, [(0, '#8a4226'), (0.4, '#b85a34'), (0.8, '#c9683c'), (1, '#b8714f')])
        n = 1 + 0.08 * np.sin(th * 7 + u * 13)
        salt = np.clip((u - 0.3) * 0.25 * (0.5 + 0.5 * np.sin(th * 5 + 1)), 0, 0.2)[..., None]
        return c * n[..., None] + salt * 0.25
    g.add('terracotta', revolve(prof, 24, 28, cols=cols, lod=False))
    g.add('soil_dark', lobed_disc(0.104, 6, 2, 16, depth=0.0, cup=0.0, cols=lambda u, th: np.ones(u.shape + (3,)) * lin('#3c2a1e') * (0.85 + 0.2 * np.sin(th * 7 + u * 9))[..., None], lod=False), T(0, 0, 0.206))
    base = np.array([0, 0, 0.206])
    col = {'a': ['#d8242a', '#e0303a'], 'b': ['#f58aa8', '#ffb0c8', '#f07090']}[v]
    nl = 20
    for k in range(nl):
        az = k * 2.4 + rng.uniform(-0.2, 0.2)
        rad = np.array([math.cos(az), math.sin(az), 0])
        rr = rng.uniform(0.02, 0.085)
        tip = base + rad * rr + UP * rng.uniform(0.07, 0.16) * (1.1 - rr * 5)
        stalk(g, base, tip, r=0.0019)
        geranium_leaf(g, tip, unit(UP + rad * 0.45), rng, R=rng.uniform(0.04, 0.055))
    for k in range(6):
        az = k * 1.1 + 0.4
        rad = np.array([math.cos(az), math.sin(az), 0])
        c = base + rad * rng.uniform(0.0, 0.05) + UP * rng.uniform(0.2, 0.27)
        stalk(g, base, c - UP * 0.035, r=0.0024, n=5)
        geranium_umbel(g, c, unit(UP + rad * 0.3), rng, col=col[k % len(col)], n=15, R=0.038, fl=0.015)
    # drooping spent leaves/buds
    for k in range(3):
        az = rng.uniform(0, TAU)
        rad = np.array([math.cos(az), math.sin(az), 0])
        tip = base + rad * 0.09 + UP * 0.02
        stalk(g, base, tip, r=0.0015)
        geranium_leaf(g, tip + rad * 0.02, unit(UP * 0.4 + rad * 0.6), rng, R=0.04)
    return g


# ------------------------------------------------------------------ bed plants
def soil_z(x, y):
    return 0.05 * (1 - (y / 0.3) ** 2) * (1 - 0.3 * (x / 1.0) ** 2) + 0.01


def hf(pts, rng, nod=0.3):
    return head_frame(pts, nod=nod, rng=rng)


def p_foxglove(g, xf, rng, s, col=('#b03a8a', '#e888c0')):
    h = 0.65 * s
    pts = W(xf, stem_path(h, rng, lean=0.03, sway=0.01, n=6))
    gstem(g, pts, 0.004, 0.0015, sides=4)
    for k in range(4):
        rosette_leaf = blade(0.16, 0.055, nu=5, nv=2, a=0.8, b=0.7, bend=-0.6, fold=0.25, serr=0.0, cols=[(0, '#3a6a28'), (1, '#6aa03c')], mid=0.3, lod=False)
        ang = k * 1.6 + rng.uniform(0, 1); el = 0.35
        rad = np.array([math.cos(ang), math.sin(ang), 0])
        g.add('leaf_green', rosette_leaf, xf @ orient(rad * 0.004, rad * math.cos(el) + UP * math.sin(el), UP))
    nb = 10
    for k in range(nb):
        t = 0.42 + 0.56 * k / (nb - 1)
        pos, tan = pathpt(pts, t)
        az = k * 2.4
        rad = np.array([math.cos(az), math.sin(az), 0])
        size = 1.2 * (1 - 0.6 * (k / nb))
        if k > nb - 3:
            g.add('sepal_green', ellipsoid(0.005, 0.005, 0.009, nu=2, nseg=5), frame_z(pos + rad * 0.008 + tan * 0.006, tan + rad * 0.5))
            continue
        axis = unit(rad * 0.8 - UP * 0.65)
        c0, c1 = lin(col[0]), lin(col[1])
        g.add('petal_soft', revolve(lambda u, size=size: ((0.003 + 0.011 * u ** 1.3) * size, 0.032 * size * u), 2, 6,
              cols=lambda u, th, c0=c0, c1=c1: (c0 * (1 - u[..., None]) + c1 * u[..., None]) * (1 - 0.3 * (np.cos(th) > 0.6)[..., None] * (u[..., None] > 0.6)), lod=False),
              frame_z(pos + rad * 0.006, axis))


def p_delphinium(g, xf, rng, s, col=('#3a48c8', '#8a9af0')):
    h = 0.6 * s
    pts = W(xf, stem_path(h, rng, lean=0.03, sway=0.01, n=5))
    gstem(g, pts, 0.0035, 0.002, sides=4)
    for k in range(4):
        p = blade(0.09, 0.07, nu=3, nv=2, a=0.6, b=0.5, bend=-0.5, fold=0.3, cols=[(0, '#3a6a28'), (1, '#6aa03c')], mid=0.2, lod=False)
        ang = k * 1.6; el = 0.4; rad = np.array([math.cos(ang), math.sin(ang), 0])
        g.add('leaf_green', p, xf @ orient(rad * 0.004 + UP * 0.03, rad * math.cos(el) + UP * math.sin(el), UP))
    c0, c1 = lin(col[0]), lin(col[1])
    L = 0.26 * s
    pos, tan = pathpt(pts, 1.0 - L / h * 1.0)
    nz = make_noise(rng.randint(99))

    def prof(u):
        return 0.022 * (1 - 0.75 * u ** 1.5) * np.sin(np.clip(u * 40, 0, 1.57)) * (1 + 0), L * u

    def lobe(u, th):
        return 1 + 0.25 * np.sin(th * 4 + u * 26)

    def cols(u, th):
        return (c0 * (1 - u[..., None]) + c1 * u[..., None]) * (0.85 + 0.25 * np.sin(th * 4 + u * 26))[..., None]
    g.add('petal_soft', revolve(prof, 8, 8, lobe=lobe, cols=cols, lod=False), frame_z(pos, tan))


def p_cosmos(g, xf, rng, s, col=('#c02a80', '#f7a8cc')):
    h = 0.62 * s
    pts = W(xf, stem_path(h, rng, lean=0.08, sway=0.03, n=6))
    gstem(g, pts, 0.0025, 0.0012, sides=4)
    for t in (0.25, 0.5):
        for p, M in feather_leaf(0.07, 0.003, rng, nb=5):
            leaf_on_path(g, 'leaf_green', pts, t, rng.uniform(0, TAU), 0.6, p, roll=0)
    f = hf(pts, rng, 0.4)
    petal_ring(g, 'petal_soft', 8, 0.04, 0.038, rng, r0=0.004, z0=0, elev=(0.05, 0.2), xf=f, a=0.7, b=0.35, nu=3, nv=2, cup=0.15, notch=0.1, bend=(-0.3, 0.1), wave=0.06,
               cols=[(0, col[0]), (0.45, col[1]), (1, col[1])], lj=0.05, wj=0.05, edge=0.0)
    g.add('disc_yellow', dome(0.01, 0.007, nu=2, nseg=10), f)
    for bp in (0.18,):
        bpts = side_branch(pts, 0.6, rng, 0.14, out=0.4)
        gstem(g, bpts, 0.0012, 0.0008, sides=3, n=5) if False else None
        g.add('stem_green', tube(bpts, np.linspace(0.0012, 0.0008, len(bpts)), sides=3, lod=False))
        f2 = head_frame(bpts, nod=0.5, rng=rng)
        petal_ring(g, 'petal_soft', 8, 0.024, 0.022, rng, r0=0.003, elev=(0.05, 0.2), xf=f2, a=0.7, b=0.35, nu=3, nv=2, cup=0.15, notch=0.1, cols=[(0, col[0]), (0.45, col[1]), (1, col[1])])
        g.add('disc_yellow', dome(0.006, 0.004, nu=2, nseg=8), f2)


def p_daisy(g, xf, rng, s):
    h = 0.30 * s
    pts = W(xf, stem_path(h, rng, lean=0.08, sway=0.03, n=5))
    gstem(g, pts, 0.0017, 0.001, sides=4)
    f = hf(pts, rng, 0.35)
    petal_ring(g, 'petal_white', 15, 0.03, 0.0085, rng, r0=0.009, elev=(0.05, 0.2), xf=f, a=0.5, b=0.4, nu=2, nv=2, bend=(-0.3, 0.1), cols=[(0, '#e9dc8e'), (0.25, '#fbf9ee'), (1, '#ffffff')])
    g.add('disc_yellow', dome(0.012, 0.0085, nu=2, nseg=10), f)
    for i in range(3):
        p = blade(0.07, 0.018, nu=4, nv=2, a=1.2, b=0.7, bend=-0.4, cols=[(0, '#3d6a24'), (1, '#68a43a')], mid=0.3, lod=False)
        ang = i * 2.1 + rng.uniform(0, 0.5); el = 0.3; rad = np.array([math.cos(ang), math.sin(ang), 0])
        g.add('leaf_green', p, xf @ orient(rad * 0.004, rad * math.cos(el) + UP * math.sin(el), UP))


def p_marigold(g, xf, rng, s, col='petal_orange', stops=((0, '#c05a08'), (0.5, '#f58a14'), (1, '#ffab2c'))):
    h = 0.21 * s
    pts = W(xf, stem_path(h, rng, lean=0.05, sway=0.02, n=4))
    gstem(g, pts, 0.002, 0.0012, sides=4)
    f = hf(pts, rng, 0.2)
    for n, L, el, z0 in ((9, 0.036, 0.05, 0.0), (11, 0.031, 0.3, 0.003), (12, 0.024, 0.6, 0.006)):
        petal_ring(g, col, n, L, 0.014, rng, r0=0.005, z0=z0, elev=(el - 0.05, el + 0.1), xf=f, a=0.5, b=0.35, nu=2, nv=2, bend=(-0.2, 0.3), cup=0.3, cols=list(stops), lj=0.1)
    petal_ring(g, 'sepal_green', 7, 0.012, 0.005, rng, r0=0.002, z0=-0.004, elev=-0.7, xf=f, nu=2, nv=2, cols=[(0, '#4c7a2a'), (1, '#7fa84a')])
    for i in range(6):
        p = blade(0.07, 0.02, nu=3, nv=2, a=0.9, b=0.6, bend=-0.3, cols=[(0, '#4a7a30'), (1, '#7aa84a')], mid=0.3, lod=False)
        ang = i * 1.05 + rng.uniform(0, 0.5); el = rng.uniform(0.2, 0.6); rad = np.array([math.cos(ang), math.sin(ang), 0])
        g.add('leaf_green', p, xf @ orient(rad * 0.004 + UP * 0.02 * i / 6, rad * math.cos(el) + UP * math.sin(el), UP))


def p_lavender(g, xf, rng, s):
    for i in range(6):
        h = rng.uniform(0.22, 0.34) * s
        a = rng.uniform(0, TAU); d = np.array([math.cos(a), math.sin(a), 0]) * rng.uniform(0.02, 0.07)
        pts = W(xf, stem_path(h, rng, lean=0.12, sway=0.02, n=4) + d * np.array([[1, 1, 0]]) * 0.5)
        g.add('stem_grey', tube(pts, np.linspace(0.0011, 0.0008, len(pts)), sides=3, lod=False))
        f = frame_z(pts[-1] - unit(pts[-1] - pts[-2]) * 0.05, pts[-1] - pts[-2])
        g.add('petal_soft', revolve(lambda u: (0.008 * np.sin(np.clip(u * 12, 0, 1.57)) * (1 - 0.5 * u ** 2), 0.055 * u), 3, 6,
              lobe=lambda u, th: 1 + 0.25 * np.sin(th * 3 + u * 22),
              cols=lambda u, th: grad(u, [(0, '#7a4ac0'), (0.8, '#8a60d0'), (1, '#9a90b0')]) * (0.85 + 0.2 * np.sin(th * 3 + u * 22))[..., None], lod=False), f)
    for i in range(12):
        p = blade(0.08, 0.004, nu=3, nv=2, a=0.6, b=0.6, bend=-0.5, cols=[(0, '#6a8a5c'), (1, '#8aa880')], lod=False)
        ang = i * 1.3 + rng.uniform(0, 0.4); el = rng.uniform(0.3, 1.0); rad = np.array([math.cos(ang), math.sin(ang), 0])
        g.add('leaf_grey', p, xf @ orient(rad * 0.006, rad * math.cos(el) + UP * math.sin(el), UP))


def p_geranium(g, xf, rng, s, col='#d8242a'):
    base = np.zeros(3)
    for k in range(7):
        az = k * 2.4 + rng.uniform(0, 1)
        rad = np.array([math.cos(az), math.sin(az), 0])
        tip = rad * rng.uniform(0.02, 0.06) + UP * rng.uniform(0.05, 0.10) * s
        geranium_leaf(g, xfv(xf, tip[None])[0], unit(UP + rad * 0.3), rng, R=0.04)
        stalk(g, xfv(xf, base[None])[0], xfv(xf, tip[None])[0], r=0.0015, n=3)
    for k in range(2):
        c = np.array([rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), 0.15 * s + 0.04 * k])
        c = xfv(xf, c[None])[0]
        stalk(g, xfv(xf, base[None])[0], c - UP * 0.03, r=0.002, n=4)
        geranium_umbel(g, c, UP, rng, col=col, n=10, R=0.03)


def p_pansymound(g, xf, rng, s):
    for k in range(3):
        d = np.array([rng.uniform(-0.05, 0.05), rng.uniform(-0.04, 0.04), 0])
        b = xfv(xf, d[None])[0]
        pos = b + UP * rng.uniform(0.035, 0.06)
        stalk(g, b, pos, r=0.001, n=3)
        pansy(g, pos, unit(np.array([rng.normal(0, 0.2), -0.8, 0.7])), rng, scheme=rng.randint(0, 4))
    for k in range(6):
        petunia_leaf(g, xfv(xf, np.array([[rng.normal(0, 0.03), rng.normal(0, 0.03), 0.012]]))[0], rng, 0.035)


def flower_bed(v, rng):
    g = Geo()
    X, Yd = 2.0, 0.6
    # soil mound
    nx, ny = 40, 10
    xs = np.linspace(-X / 2 + 0.02, X / 2 - 0.02, nx + 1); ys = np.linspace(-Yd / 2 + 0.02, Yd / 2 - 0.02, ny + 1)
    XX, YY = np.meshgrid(xs, ys, indexing='ij')
    nzf = make_noise(3)
    ZZ = soil_z(XX, YY) + 0.008 * nzf(np.stack([XX, YY, 0 * XX], -1), 6)
    P = np.stack([XX, YY, ZZ], -1)
    C = np.ones_like(P) * lin('#4a3526') * (0.8 + 0.25 * nzf(np.stack([XX, YY, 0 * XX], -1) + 5, 30)[..., None])
    p = grid(P, C)
    g.add('soil_dark', (p[0], [f[::-1] for f in p[1]], p[2], p[3]))
    # timber edging
    for (c, s) in (((0, -Yd / 2 + 0.02, 0.04), (X, 0.04, 0.08)), ((0, Yd / 2 - 0.02, 0.04), (X, 0.04, 0.08)),
                   ((-X / 2 + 0.02, 0, 0.04), (0.04, Yd, 0.08)), ((X / 2 - 0.02, 0, 0.04), (0.04, Yd, 0.08))):
        g.add('timber_edge', cuboid(c, s, col=lin('#8a6a44') * rng.uniform(0.85, 1.05)))
    cool = v == 'a'
    plants = []

    def place(fn, n, y0, y1, **kw):
        xs = np.linspace(-0.88, 0.88, n) + rng.uniform(-0.05, 0.05, n)
        rng.shuffle(xs)
        for x in xs:
            y = rng.uniform(y0, y1)
            plants.append((fn, x, y, kw))
    if cool:
        place(p_foxglove, 5, 0.14, 0.25, col=('#b03a8a', '#e888c0'))
        place(p_delphinium, 5, 0.14, 0.25)
        place(p_cosmos, 7, 0.1, 0.24)
        place(p_daisy, 12, -0.05, 0.12)
        place(p_lavender, 7, -0.08, 0.08)
        place(p_marigold, 9, -0.25, -0.05)
        place(p_geranium, 4, -0.23, -0.1, col='#e0303a')
        place(p_pansymound, 6, -0.26, -0.15)
    else:
        place(p_foxglove, 5, 0.14, 0.25, col=('#f4e8f0', '#fff6fa'))
        place(p_delphinium, 5, 0.14, 0.25, col=('#e8a0d0', '#f8d0ea'))
        place(p_cosmos, 7, 0.1, 0.24, col=('#d8d0d8', '#ffffff'))
        place(p_daisy, 11, -0.05, 0.12)
        place(p_lavender, 7, -0.08, 0.08)
        place(p_marigold, 12, -0.25, -0.03, stops=((0, '#b84a06'), (0.5, '#f27810'), (1, '#ff9a20')))
        place(p_geranium, 4, -0.23, -0.1, col='#f26a52')
        place(p_pansymound, 4, -0.26, -0.15)
    for k in range(85):
        x = rng.uniform(-0.93, 0.93); y = rng.uniform(-0.26, 0.26)
        p = np.array([x, y, soil_z(x, y) + rng.uniform(0.01, 0.05)])
        geranium_leaf(g, p, unit(UP + rng.normal(0, 0.4, 3) * np.array([1, 1, 0.3])), rng, R=rng.uniform(0.035, 0.06))
    for fn, x, y, kw in plants:
        s = rng.uniform(0.85, 1.15)
        xf = T(x, y, soil_z(x, y) - 0.005) @ Rz(rng.uniform(0, TAU))
        fn(g, xf, rng, s, **kw)
    return g


DEFS = [
    dict(sp='flower_box', fn=flower_box, variants=['a', 'b'], ko='창가 화분 상자(플라워박스)', weight=0.5, habitat='garden', sway=0.1),
    dict(sp='flower_pot', fn=flower_pot, variants=['a', 'b'], ko='화분(제라늄)', weight=0.5, habitat='garden', sway=0.1),
    dict(sp='flower_bed', fn=flower_bed, variants=['a', 'b'], ko='화단', weight=0.5, habitat='garden', sway=0.15),
]
