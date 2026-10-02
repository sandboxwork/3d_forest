from meadow_common import *

UP = np.array([0, 0, 1.0])


def init_box_mats():
    init_mats()
    mat('petal_soft', '#ffffff', rough=0.55, sss=0.25)
    mat('petal_gloss', '#ffffff', rough=0.4, sss=0.2)
    mat('leaf_geranium', '#7ab84a', rough=0.5, sss=0.15)
    mat('leaf_ivy', '#4a8a3c', rough=0.35, sss=0.1)
    mat('leaf_small', '#6aa83c', rough=0.5)
    mat('planter_wood', '#b48c5e', rough=0.8)
    mat('planter_wood_dark', '#6a4a30', rough=0.85)
    mat('timber_edge', '#8a6a44', rough=0.85)
    mat('terracotta', '#c2643a', rough=0.85)
    mat('soil_dark', '#4a3324', rough=0.95)


def cuboid(c, s, col=(0.6, 0.45, 0.3)):
    cx, cy, cz = c; sx, sy, sz = s
    V = []; F = []; C = []
    for n, u, v in (((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
                    ((0, 1, 0), (0, 0, 1), (1, 0, 0)), ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
                    ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (0, 1, 0), (1, 0, 0))):
        n, u, v = [np.array(a, float) for a in (n, u, v)]
        dims = np.array([sx, sy, sz]) / 2
        ctr = np.array(c) + n * dims
        uu = u * dims; vv = v * dims
        i = len(V)
        V += [ctr - uu - vv, ctr + uu - vv, ctr + uu + vv, ctr - uu + vv]
        F.append((i, i + 1, i + 2, i + 3))
    V = np.array(V)
    UV = np.tile([[0, 0], [1, 0], [1, 1], [0, 1]], (6, 1)).astype(float)
    return (V, F, np.ones_like(V) * np.asarray(col) if col is not None else -np.ones_like(V), UV)


def stalk(g, p0, p1, r=0.0012, m='stem_green', sides=4, n=4, bow=0.3):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = np.linalg.norm(p1 - p0)
    pts = bez(p0, p0 + UP * d * bow, p1 - unit(p1 - p0) * d * 0.2 - UP * d * 0.1 * 0, p1, n)
    t = np.linspace(0, 1, n)
    g.add(m, tube(pts, r * (1 - 0.3 * t), sides=sides, cols=grad(t, [(0, '#4d7a2a'), (1, '#7aa83c')]), lod=False))
    return pts


PET = {'purple': ('#8a3cc8', '#2a0f40'), 'pink': ('#ee5fa7', '#7a1a4a'), 'white': ('#f8f3f8', '#b8c870'),
       'magenta': ('#c8207a', '#4a0a30'), 'violet': ('#6a48d0', '#1c0f50'), 'red': ('#e0302a', '#6a0a10'),
       'salmon': ('#f58a70', '#c84a30')}


def petunia(g, pos, axis, rng, size=1.0, color='purple'):
    base, throat = PET[color]
    xf = frame_z(pos, axis, rng.uniform(0, TAU))
    lb, lt = lin(base), lin(throat)

    def prof(u):
        return (0.004 * np.minimum(1, u * 8) + 0.034 * u ** 1.6) * size, 0.042 * u * size

    def lobe(u, th):
        return 1 - 0.1 * (0.5 - 0.5 * np.cos(5 * th)) * u ** 3

    def cols(u, th):
        t = np.clip(u * 1.6, 0, 1)[..., None]
        c = lt * (1 - t) ** 1.4 + lb * (1 - (1 - t) ** 1.4)
        vein = 1 - 0.14 * np.maximum(0, np.cos(5 * th)) ** 6 * u
        if color == 'white':
            c = np.where(u[..., None] < 0.3, lt * 0.9 + 0.1, lb * 0.96) * 1.0
        return c * vein[..., None] * (0.97 + 0.03 * np.sin(th * 11))[..., None]
    g.add('petal_soft', revolve(prof, 3, 10, lobe=lobe, cols=cols, lod=False), xf)


def geranium_umbel(g, c, axis, rng, col='#d8242a', n=13, R=0.03, fl=0.012):
    lb = lin(col); lc_ = lin('#ffe6dc')
    for i in range(n):
        d = unit(unit(axis) * rng.uniform(0.3, 1.0) + rng.normal(0, 0.8, 3))
        if np.dot(d, axis) < 0.1:
            d = unit(d + axis)
        pos = c + d * R * rng.uniform(0.85, 1.0)

        def cols(u, th, lb=lb):
            t = np.clip(u * 2.2, 0, 1)[..., None]
            cc = lc_ * (1 - t) + lb * t
            return cc * (1 - 0.12 * np.maximum(0, np.cos(5 * th)) ** 4)[..., None] * rng.uniform(0.9, 1.05)
        g.add('petal_soft', lobed_disc(fl * rng.uniform(0.9, 1.15), 5, 1, 12, depth=0.16, cup=0.4, sharp=0.6, cols=cols, lod=False),
              frame_z(pos, d, rng.uniform(0, TAU)))


def geranium_leaf(g, p, normal, rng, R=0.035):
    def cols(u, th):
        c = grad(u, [(0, '#8cc85a'), (0.25, '#4f9a32'), (0.55, '#2f6a24'), (0.85, '#4a8a30'), (1, '#6aa83c')])
        return c * (1 + 0.15 * np.maximum(0, np.cos(9 * th)) ** 4)[..., None]
    g.add('leaf_geranium', lobed_disc(R, 9, 2, 14, depth=0.14, cup=0.3, cols=cols, lod=False, wave=0.06), frame_z(p, normal, rng.uniform(0, TAU)))


def ivy_leaf(g, p, normal, rng, R=0.02):
    def cols(u, th):
        c = grad(u, [(0, '#9ac870'), (0.3, '#2f6a2a'), (1, '#285c24')])
        return c * (1 + 0.5 * np.maximum(0, np.cos(5 * th)) ** 8 * np.clip(u * 2, 0, 1))[..., None] * rng.uniform(0.85, 1.1)
    g.add('leaf_ivy', lobed_disc(R * rng.uniform(0.8, 1.2), 5, 1, 10, depth=0.5, cup=0.15, cols=cols, lod=False), frame_z(p, normal, rng.uniform(0, TAU)))


def pansy(g, pos, axis, rng, size=1.0, scheme=0):
    xf = frame_z(pos, axis, rng.uniform(0, TAU))
    S = {0: ('#6a2a9a', '#f4d21c', '#2a0a40'), 1: ('#f2c21a', '#fff2a0', '#5a2a1a'), 2: ('#a8a0e8', '#fff4c0', '#3a2a7a'),
         3: ('#d8d0f8', '#f8e060', '#5a3a9a')}[scheme]
    c1, c2, cd = S
    # (angle from +Y, L, W, y0)
    for ang, L, W in ((0.55, 0.019, 0.022), (-0.55, 0.019, 0.022), (1.75, 0.017, 0.02), (-1.75, 0.017, 0.02), (3.14, 0.021, 0.025)):
        lower = abs(ang) > 3
        stops = [(0, S[1]), (0.22, S[1] if lower else S[0]), (0.26, S[0] if not lower else S[0]), (1, S[0])]
        if lower and scheme == 1:
            stops = [(0, S[2]), (0.15, S[1]), (0.6, S[0]), (1, S[0])]
        p = blade(L * size, W * size, nu=2, nv=2, a=0.6, b=0.3, bend=-0.35, cup=0.15, wave=0.12, wavef=1.5, cols=stops, lod=False)
        g.add('petal_gloss', p, xf @ Rz(-ang) @ T(0, 0.001, 0) @ Rx(0.12))
    # dark blotch center
    g.add('petal_gloss', lobed_disc(0.004 * size, 5, 1, 6, depth=0.2, cols=lambda u, th: np.ones(u.shape + (3,)) * lin(cd), lod=False), xf @ T(0, 0, 0.002))


def box_soil_top(x0, x1, y0, y1, z, rng, nx=16, ny=4, amp=0.006):
    xs = np.linspace(x0, x1, nx + 1); ys = np.linspace(y0, y1, ny + 1)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    nz = make_noise(rng.randint(999))
    Z = z + amp * nz(np.stack([X, Y, 0 * X], -1), 12)
    P = np.stack([X, Y, Z], -1)
    C = np.ones_like(P) * lin('#4a3526') * (0.8 + 0.25 * nz(np.stack([X, Y, 0 * X], -1) + 3, 40)[..., None])
    p = grid(P, C)
    return (p[0], [f[::-1] for f in p[1]], p[2], p[3])


def foliage_mound(g, c, rx, rz, rng, col=('#2c5a22', '#4a8a30')):
    ph = rng.uniform(0, 6)
    g.add('leaf_small', ellipsoid(rx, rx * rng.uniform(0.8, 1.1), rz, nu=4, nseg=8,
          lobe=lambda u, th: 1 + 0.14 * np.sin(th * 5 + ph + u * 7),
          cols=lambda u, th: grad(u, [(0, col[0]), (0.55, col[0]), (1, col[1])]) * (0.85 + 0.3 * (0.5 + 0.5 * np.sin(th * 7 + ph * 2 + u * 9)))[..., None]), T(c))
