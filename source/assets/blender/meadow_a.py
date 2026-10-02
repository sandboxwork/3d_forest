from meadow_common import *


# ------------------------------------------------------------------ DAISY
def daisy_head(g, xf, rng, n=22, R=0.0235, elev=0.12, scale=1.0, open_=1.0):
    L = R * scale
    petal_ring(g, 'petal_white', n, L, 0.0058 * scale, rng, r0=0.007 * scale, z0=0.0005, elev=(elev - 0.05, elev + 0.12), elev_j=0.05,
               xf=xf, a=0.5, b=0.42, nu=4, nv=2, bend=(-0.35, 0.15), cup=0.25, notch=0.04, wave=0.05, wavef=1.5,
               cols=[(0, '#e9dc8e'), (0.22, '#fbf9ee'), (1, '#ffffff')], edge=0.08, mid=-0.05, lj=0.1, wj=0.12, roll=0.05)
    petal_ring(g, 'petal_white', lc(9, 0.4), L * 0.85, 0.0056 * scale, rng, r0=0.006 * scale, z0=-0.0004, elev=(elev + 0.2, elev + 0.4), elev_j=0.05,
               xf=xf, a=0.5, b=0.42, nu=3, nv=2, bend=(-0.3, 0.1), cols=[(0, '#e0d27e'), (0.3, '#f7f4e4'), (1, '#fbfbf5')], lj=0.1)
    # disc
    nz = make_noise(rng.randint(1000))

    def lobe(u, th):
        return 1 + 0.05 * np.sin(th * 13 + u * 9) * (u < 0.98)

    def cols(u, th):
        c = grad(u, [(0, '#b9780a'), (0.35, '#e8a912'), (0.8, '#f6c81c'), (1, '#f0b810')])
        return c * (0.92 + 0.08 * np.sin(th * 13 + u * 9)[..., None])
    g.add('disc_yellow', dome(0.0092 * scale, 0.0068 * scale, nu=4, nseg=14, cols=cols, lobe=lobe), xf @ T(0, 0, -0.0006))
    petal_ring(g, 'sepal_green', lc(12, 0.5), 0.0075 * scale, 0.0035 * scale, rng, r0=0.002, z0=-0.0025, elev=-0.65, xf=xf, a=0.6, b=0.5, nu=2, nv=2,
               cols=[(0, '#4c7a2a'), (1, '#7fa84a')], bend=0.2)


def daisy(v, rng):
    g = Geo()
    spec = {'a': (0.50, 22, 0.35), 'b': (0.64, 26, 0.6), 'c': (0.44, 23, 0.25), 'd': (0.56, 29, 0.15)}[v]
    h = spec[0] * rng.uniform(0.96, 1.05)
    pts = stem_path(h, rng, lean=0.09, sway=0.035, n=8)
    gstem(g, pts, 0.0019, 0.0011, sides=5, c0='#4d6d28', c1='#7ba43e')
    daisy_head(g, head_frame(pts, nod=spec[2], rng=rng), rng, n=lc(spec[1], 0.75), scale=1.0 if v != 'c' else 0.95)
    if v == 'c':
        bp = side_branch(pts, 0.55, rng, 0.17, out=0.5)
        gstem(g, bp, 0.0012, 0.0008, sides=4)
        daisy_head(g, head_frame(bp, nod=0.6, rng=rng), rng, n=lc(18, 0.75), scale=0.8)
        bp2 = side_branch(pts, 0.35, rng, 0.11, out=0.4)
        gstem(g, bp2, 0.001, 0.0007, sides=4)
        # bud
        bxf = head_frame(bp2, nod=0.2, rng=rng)
        g.add('sepal_green', ellipsoid(0.0075, 0.0075, 0.0085, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#527d2c'), (0.8, '#7da84a'), (1, '#e9efdc')])), bxf @ T(0, 0, 0.004))
    # leaves
    for i in range(lc(4, 0.75)):
        rosette_leaf = blade(0.075, 0.019, nu=10, nv=2, a=1.25, b=0.75, serr=0.14, bend=(-0.45, -0.1), fold=0.2, cols=[(0, '#3d6a24'), (0.5, '#558f2e'), (1, '#68a43a')], mid=0.35, edge=0.12)
        ang = i * 1.7 + rng.uniform(0, 0.6)
        el = rng.uniform(0.2, 0.55)
        rad = np.array([math.cos(ang), math.sin(ang), 0])
        g.add('leaf_green', rosette_leaf, orient(rad * 0.004, rad * math.cos(el) + np.array([0, 0, math.sin(el)]), np.array([0, 0, 1.0])))
    lance_leaves(g, pts, rng, lc(4, 0.75), 0.06, 0.009, t0=0.12, t1=0.6, a=0.6, b=0.9, serr=0.12, nu=8)
    return g


mat('petal_lavender', '#8468cc', rough=0.7, sss=0.15)
mat('ovary_green', '#93ad5e', rough=0.6)
mat('stamen_poppy', '#7a6a8a', rough=0.5)
mat('stigma_grey', '#b4abbb', rough=0.6)
mat('petal_poppy', '#f0301a', rough=0.55, sss=0.3)
mat('petal_corn', '#4a6cf0', rough=0.6, sss=0.2)
mat('corn_inner', '#8a3ab0', rough=0.6)
mat('corn_bract', '#8ea56a', rough=0.7)
mat('clover_pink', '#ee72b2', rough=0.65, sss=0.1)
mat('clover_white', '#f7f3ea', rough=0.65, sss=0.1)
mat('clover_leaf', '#5c9a3c', rough=0.5, sss=0.15)
mat('pappus', '#f4f4ee', rough=0.8)
mat('dand_leaf', '#5c9433', rough=0.5, sss=0.15)
mat('hair_grey', '#9cae86', rough=0.7)


def ribbon(pts, widths, cols=None, side_ref=(0, 0, 1.0)):
    pts = np.asarray(pts, float)
    n = len(pts)
    widths = np.broadcast_to(np.asarray(widths, float), (n,))
    Tg = np.gradient(pts, axis=0)
    P = np.zeros((n, 2, 3))
    for i in range(n):
        t = unit(Tg[i]); sr = np.array(side_ref)
        sd = np.cross(t, sr)
        if np.linalg.norm(sd) < 1e-6:
            sd = np.cross(t, [1.0, 0, 0])
        sd = unit(sd)
        P[i, 0] = pts[i] - sd * widths[i] / 2; P[i, 1] = pts[i] + sd * widths[i] / 2
    C = None
    if cols is not None:
        C = np.repeat(np.asarray(cols)[:, None, :], 2, 1)
    return grid(P, C)


def stamens(g, m, xf, rng, n, r0, L, elev, cols, w=0.0005, w1=0.0011, spread=0.25):
    for i in range(n):
        ang = rng.uniform(0, TAU)
        rad = np.array([math.cos(ang), math.sin(ang), 0.0])
        el = elev + rng.uniform(-spread, spread)
        d = math.cos(el) * rad + math.sin(el) * np.array([0, 0, 1.0])
        l = L * rng.uniform(0.8, 1.1)
        p0 = rad * r0
        pts = np.array([p0, p0 + d * l * 0.5 + np.array([0, 0, 0.0]), p0 + d * l + np.array([0, 0, -0.0005])])
        g.add(m, ribbon(pts, [w, w, w1], cols=grad(np.array([0, 0.6, 1]), cols), side_ref=np.cross(d, rad) + 0.01 * rad), xf)


def urn(g, xf, R, H, m='ovary_green', top='stigma_grey', lobes=8, cols=None):
    prof = lambda u: (R * (1 + 0.3 * np.sin(u * PI * 0.8)) * (1 - 0.3 * u ** 3), H * u)
    g.add(m, revolve(prof, 3, 9, cols=lambda u, th: grad(u, [(0, '#6f8f3e'), (1, '#9bb668')])), xf)
    g.add(top, lobed_disc(R * 1.45, lobes=lobes, rings=1, segs=2 * lobes if LOD == 0 else lobes, depth=0.1, cup=-0.15,
                          cols=lambda u, th: grad(u, [(0, '#403848'), (0.4, '#9e95a6'), (1, '#c6bfcc')]) * (0.75 + 0.25 * np.cos(lobes * th))[..., None]),
          xf @ T(0, 0, H * 0.98))


def hook_path(h, hook, rng, n=9, az=None):
    az = rng.uniform(0, TAU) if az is None else az
    d = np.array([math.cos(az), math.sin(az), 0.0])
    jx = rng.uniform(-0.03, 0.03) * h
    p0 = np.zeros(3); p1 = np.array([jx, 0, 0.45 * h]); p2 = d * 0.0 + np.array([0, 0, 1.0 * h]); p3 = d * hook + np.array([0, 0, h - hook * 0.45])
    if LOD: n = 5
    return bez(p0, p1 + d * 0.01 * h, p2, p3, n)


# ------------------------------------------------------------------ POPPY
def poppy_head(g, xf, rng, size=1.0, elev=(0.3, 0.55), cupamt=0.4, bend=(0.05, 0.3), n_st=34, pod=True):
    nzf = make_noise(rng.randint(10000))
    base = rng.uniform(0, TAU)
    for i in range(4):
        ang = base + i * PI / 2 + rng.uniform(-0.25, 0.25)
        inner = i % 2
        L = size * 0.040 * (0.92 if inner else 1.0) * rng.uniform(0.93, 1.07)
        W = L * (1.3 if not inner else 1.2)
        el = rv(elev, rng) + (0.1 if inner else 0)
        rad = np.array([math.cos(ang), math.sin(ang), 0.0]); Z = np.array([0, 0, 1.0])
        ydir = math.cos(el) * rad + math.sin(el) * Z
        nrm = -math.sin(el) * rad + math.cos(el) * Z
        M = orient(0.002 * rad * size + Z * (0.0012 * inner), ydir, nrm)
        p = blade(L, W, nu=10, nv=10, a=0.6, b=0.42, bend=rv(bend, rng), cup=cupamt, wave=0.08, wavef=rng.uniform(2.5, 4), wph=rng.uniform(0, TAU),
                  nz=0.06, noise=nzf, nzf=1.3, notch=0.03, baseW=0.14,
                  cols=[(0, '#140606'), (0.14, '#3a0a08'), (0.26, '#d11a10'), (0.55, '#ee2e18'), (1, '#f8452a')], edge=0.12)
        g.add('petal_poppy', p, xf @ M)
    if pod:
        urn(g, xf, 0.0058 * size, 0.012 * size)
        stamens(g, 'stamen_poppy', xf, rng, lc(n_st, 0.5), 0.0085 * size, 0.013 * size, 0.9, [(0, '#8a7a9a'), (0.6, '#3a2f4a'), (1, '#150f1c')], spread=0.45)


def poppy(v, rng):
    g = Geo()
    h = {'a': 0.58, 'b': 0.70, 'c': 0.52, 'd': 0.46}[v] * rng.uniform(0.95, 1.05)
    cols = lambda n: grad(np.linspace(0, 1, n), [(0, '#58703a'), (1, '#8ea060')])
    if v == 'c':
        pts = hook_path(h, 0.045, rng, n=9)
    else:
        pts = stem_path(h, rng, lean=0.1, sway=0.04, n=8)
    g.add('stem_grey', tube(pts, np.linspace(0.0021, 0.0011, len(pts)), sides=5, cols=cols(len(pts))))
    if v == 'a':
        poppy_head(g, head_frame(pts, nod=0.35, rng=rng), rng, size=1.0)
    elif v == 'b':
        poppy_head(g, head_frame(pts, nod=0.75, rng=rng), rng, size=1.12, elev=(0.15, 0.4), cupamt=0.3, bend=(-0.05, 0.2))
    elif v == 'd':
        poppy_head(g, head_frame(pts, nod=0.15, rng=rng), rng, size=0.9, elev=(0.6, 0.85), cupamt=0.55, bend=(0.25, 0.5))
    else:
        bxf = head_frame(pts, rng=rng)
        g.add('sepal_green', ellipsoid(0.0085, 0.0085, 0.0135, nu=5, nseg=9, cols=lambda u, th: grad(u, [(0, '#5a7a38'), (0.7, '#86a058'), (1, '#9ab068')]) * (0.9 + 0.1 * np.sin(th * 2))[..., None]), bxf @ T(0, 0, 0.011))
        g.add('petal_poppy', ellipsoid(0.0062, 0.0062, 0.006, nu=3, nseg=8, cols=lambda u, th: grad(u, [(0, '#d22a16'), (1, '#f0402a')])), bxf @ T(0, 0, 0.0245))
        bp = side_branch(pts, 0.5, rng, 0.2, out=0.5)
        g.add('stem_grey', tube(bp, np.linspace(0.0014, 0.0009, len(bp)), sides=4, cols=cols(len(bp))))
        poppy_head(g, head_frame(bp, nod=0.5, rng=rng), rng, size=0.82, elev=(0.35, 0.6), cupamt=0.45)
        bp2 = side_branch(pts, 0.3, rng, 0.12, out=0.4)
        g.add('stem_grey', tube(bp2, np.linspace(0.0012, 0.0008, len(bp2)), sides=4, cols=cols(len(bp2))))
        bx2 = head_frame(bp2, rng=rng)
        urn(g, bx2, 0.0075, 0.02, lobes=9)
    if v == 'd':
        bp = side_branch(pts, 0.42, rng, 0.14, out=0.45)
        g.add('stem_grey', tube(bp, np.linspace(0.0012, 0.0008, len(bp)), sides=4, cols=cols(len(bp))))
        urn(g, head_frame(bp, rng=rng), 0.008, 0.022, lobes=9)
    # leaves: lobed, hairy grey-green
    for i in range(lc(3, 0.7)):
        ang = i * 2.2 + rng.uniform(0, 0.8); el = rng.uniform(0.2, 0.5)
        rad = np.array([math.cos(ang), math.sin(ang), 0.0])
        g.add('leaf_green', blade(0.11, 0.032, nu=14, nv=2, a=0.8, b=0.7, serr=0.45, bend=(-0.5, -0.2), fold=0.2,
                                  cols=[(0, '#4f7430'), (1, '#7a9a4a')], mid=0.3), orient(rad * 0.004, rad * math.cos(el) + np.array([0, 0, math.sin(el)]), [0, 0, 1.0]))
    lance_leaves(g, pts, rng, lc(3, 0.7), 0.08, 0.022, t0=0.12, t1=0.5, a=0.8, b=0.7, serr=0.4, nu=10)
    return g


# ------------------------------------------------------------------ CORNFLOWER
def corn_head(g, xf, rng, size=1.0, n_out=10, open_=1.0):
    nzf = make_noise(rng.randint(10000))
    # involucre
    def lobe(u, th):
        return 1 + 0.045 * np.sin(u * 30) * np.cos(th * 0 + 1) + 0.03 * np.sin(th * 9)
    g.add('corn_bract', ellipsoid(0.0062 * size, 0.0062 * size, 0.0088 * size, nu=6, nseg=10, lobe=lobe,
                                  cols=lambda u, th: grad(u, [(0, '#7a9a54'), (0.45, '#9ab474'), (0.75, '#7a6446'), (1, '#3a2a20')]) * (0.92 + 0.08 * np.sin(u * 30))[..., None]),
          xf @ T(0, 0, 0.0075 * size))
    # outer large ray florets
    petal_ring(g, 'petal_corn', lc(n_out, 0.7), 0.0195 * size, 0.0115 * size, rng, r0=0.004 * size, z0=0.012 * size, elev=(0.05 + 0.25 * (1 - open_), 0.35 + 0.3 * (1 - open_)), elev_j=0.12, xf=xf,
               a=1.2, b=0.3, nu=4, nv=4, bend=(-0.5, -0.1), cup=0.35, notch=0.14, wave=0.12, wavef=2, baseW=0.04, lj=0.15, wj=0.15,
               cols=[(0, '#6a3eaa'), (0.3, '#4a58d8'), (1, '#3d70f4')], edge=0.06)
    # inner disc florets (purple tufts)
    petal_ring(g, 'corn_inner', lc(14, 0.6), 0.0105 * size, 0.0028 * size, rng, r0=0.0015 * size, z0=0.0165 * size, elev=(0.75, 1.15), elev_j=0.15, xf=xf,
               a=0.6, b=0.4, nu=2, nv=2, bend=(-0.2, 0.1), cols=[(0, '#5a2a8a'), (0.6, '#8a3ab8'), (1, '#c060d8')], notch=0.1, lj=0.25)


def corn_bud(g, xf, size=0.8, open_=0.0):
    g.add('corn_bract', ellipsoid(0.0065 * size, 0.0065 * size, 0.011 * size, nu=5, nseg=8,
                                  cols=lambda u, th: grad(u, [(0, '#7a9a54'), (0.5, '#9ab474'), (0.85, '#6a5a40'), (1, '#8a5a8a')]) * (0.92 + 0.08 * np.sin(u * 26))[..., None]), xf @ T(0, 0, 0.008 * size))
    g.add('petal_corn', ellipsoid(0.0035 * size, 0.0035 * size, 0.004 * size, nu=3, nseg=6, cols=lambda u, th: grad(u, [(0, '#5a48c0'), (1, '#3d70f4')])), xf @ T(0, 0, 0.0185 * size))


def cornflower(v, rng):
    g = Geo()
    h = {'a': 0.68, 'b': 0.78, 'c': 0.62, 'd': 0.72}[v] * rng.uniform(0.95, 1.05)
    pts = stem_path(h, rng, lean=0.07, sway=0.05, n=9)
    cols = lambda n: grad(np.linspace(0, 1, n), [(0, '#5b7a42'), (1, '#8ea870')])
    g.add('stem_grey', tube(pts, np.linspace(0.0018, 0.0009, len(pts)), sides=4, cols=cols(len(pts))))
    plan = {'a': [('h', 1), ('h', .85), ('h', .8)], 'b': [('h', 1), ('b', .9), ('h', .85)], 'c': [('h', 1), ('h', .95), ('h', .8), ('b', .8)], 'd': [('h', .95), ('b', .9), ('b', .8), ('b', .7)]}[v]
    # main head
    kind, sc = plan[0]
    (corn_head if kind == 'h' else corn_bud)(g, head_frame(pts, nod=0.35, rng=rng), *((rng,) if kind == 'h' else ()), size=sc) if kind == 'h' else corn_bud(g, head_frame(pts, nod=0.2, rng=rng), size=sc)
    ts = [0.72, 0.5, 0.33]
    for (kind, sc), t in zip(plan[1:], ts):
        bp = side_branch(pts, t, rng, rng.uniform(0.14, 0.24), out=0.55)
        g.add('stem_grey', tube(bp, np.linspace(0.0011, 0.0007, len(bp)), sides=3, cols=cols(len(bp))))
        if kind == 'h':
            corn_head(g, head_frame(bp, nod=0.5, rng=rng), rng, size=sc)
        else:
            corn_bud(g, head_frame(bp, nod=0.2, rng=rng), size=sc)
    # narrow grey-green linear leaves
    for i in range(lc(6, 0.6)):
        ang = i * 1.3 + rng.uniform(0, 0.5); el = rng.uniform(0.3, 0.9)
        rad = np.array([math.cos(ang), math.sin(ang), 0.0])
        g.add('leaf_grey', blade(rng.uniform(0.1, 0.16), 0.007, nu=8, nv=2, a=0.6, b=0.8, bend=(-0.6, -0.2), fold=0.4, serr=0.12,
                                 cols=[(0, '#6a8a5a'), (1, '#9cb690')], mid=0.25), orient(rad * 0.003, rad * math.cos(el) + np.array([0, 0, math.sin(el)]), [0, 0, 1.0]))
    lance_leaves(g, pts, rng, lc(6, 0.6), 0.075, 0.005, t0=0.1, t1=0.75, m='leaf_grey', a=0.5, b=0.9, nu=6, cols=[(0, '#6a8a5a'), (1, '#a2bb96')], bend=-0.25)
    return g


# ------------------------------------------------------------------ BUTTERCUP
def bc_leaf(L, rng, lobes=5, scale=1.0):
    """palmate leaf in local frame (+Y forward, normal +Z): returns list of (mat, patch, xf)"""
    out = []
    pet = L * 0.62
    out.append(('leaf_green', blade(pet, 0.0032, nu=3, nv=2, a=0.3, b=0.15, bend=0.1, cols=[(0, '#5a7a30'), (1, '#6f9638')], fold=0.0, baseW=1.0), np.eye(4)))
    tip = np.array([0, pet * 0.97, 0.008])
    for k in range(lobes):
        f = (k - (lobes - 1) / 2) / ((lobes - 1) / 2)
        ang = f * 1.15
        ll = L * 0.38 * (1 - 0.3 * abs(f)) * rng.uniform(0.9, 1.1)
        M = mm(T(tip), Rz(-ang), Rx(rng.uniform(0.0, 0.12)))
        out.append(('leaf_green', blade(ll, ll * 0.45, nu=5, nv=2, a=0.55, b=0.7, serr=0.3, fold=0.25, bend=-0.25,
                                        cols=[(0, '#3f7228'), (0.6, '#5a9434'), (1, '#6ea840')], mid=0.25, edge=0.1), M))
    return out


def bc_flower(g, xf, rng, size=1.0, open_=1.0):
    petal_ring(g, 'petal_yellow_glossy', 5, 0.0125 * size, 0.0135 * size, rng, r0=0.0015, z0=0.0, elev=(0.3, 0.55) if open_ > 0.5 else (0.95, 1.2), elev_j=0.06, xf=xf,
               a=0.45, b=0.2, nu=5, nv=6, bend=(0.0, 0.3), cup=0.6, baseW=0.12, cols=[(0, '#d6c000'), (0.3, '#ffd60a'), (1, '#ffe650')], edge=0.05, jit=0.06)
    petal_ring(g, 'sepal_green', 5, 0.0075 * size, 0.004 * size, rng, r0=0.002, z0=-0.0012, elev=-0.35, xf=xf, a=0.6, b=0.5, nu=2, nv=2,
               cols=[(0, '#7a9a3a'), (1, '#c4c860')], bend=0.25, jit=0.05)
    g.add('ovary_green', dome(0.0028 * size, 0.0034 * size, nu=3, nseg=9, cols=lambda u, th: grad(u, [(0, '#8aa83a'), (1, '#b6cc50')])), xf @ T(0, 0, 0.0005))
    stamens(g, 'stamen_yellow', xf, rng, lc(24, 0.5), 0.0032 * size, 0.0052 * size, 1.15, [(0, '#e0b800'), (0.7, '#f4d018'), (1, '#c08a00')], w=0.0004, w1=0.0009, spread=0.35)


def buttercup(v, rng):
    g = Geo()
    h = {'a': 0.46, 'b': 0.52, 'c': 0.58, 'd': 0.36}[v] * rng.uniform(0.95, 1.05)
    pts = stem_path(h, rng, lean=0.06, sway=0.04, n=8)
    cols = lambda n: grad(np.linspace(0, 1, n), [(0, '#6a8a3a'), (1, '#9ab84a')])
    g.add('stem_green', tube(pts, np.linspace(0.0018, 0.0010, len(pts)), sides=5, cols=cols(len(pts))))
    plan = {'a': ['f', 'f', 'f', 'b'], 'b': ['f', 'f', 'b'], 'c': ['f', 'f', 'f', 'f', 'b'], 'd': ['f', 'f', 'b']}[v]
    sz = {'a': 1.15, 'b': 1.2, 'c': 1.05, 'd': 1.25}[v]
    bc_flower(g, head_frame(pts, nod=0.45 if v != 'd' else 0.9, rng=rng), rng, size=sz) if plan[0] == 'f' else None
    ts = [0.78, 0.6, 0.45, 0.32]
    for kind, t in zip(plan[1:], ts):
        bp = side_branch(pts, t, rng, rng.uniform(0.09, 0.18), out=0.6)
        g.add('stem_green', tube(bp, np.linspace(0.0011, 0.0007, len(bp)), sides=3, cols=cols(len(bp))))
        xf = head_frame(bp, nod=0.5, rng=rng)
        if kind == 'f':
            bc_flower(g, xf, rng, size=sz * rng.uniform(0.85, 1.0))
        else:
            g.add('sepal_green', ellipsoid(0.0042, 0.0042, 0.0058, nu=4, nseg=7, cols=lambda u, th: grad(u, [(0, '#7a9a3a'), (0.7, '#b0c050'), (1, '#e8d030')])), xf @ T(0, 0, 0.0045))
        # small bract leaf at fork
        pos, tan = pathpt(pts, t)
        for (m, p, M) in bc_leaf(0.05, rng, lobes=3):
            leaf_on_path(g, m, pts, t - 0.03, rng.uniform(0, TAU), 0.7, p) if False else None
    # basal palmate leaves
    for i in range(lc(4, 0.6)):
        ang = i * 1.6 + rng.uniform(0, 0.7); el = rng.uniform(0.4, 0.8)
        rad = np.array([math.cos(ang), math.sin(ang), 0.0])
        ydir = rad * math.cos(el) + np.array([0, 0, math.sin(el)])
        base = orient(rad * 0.004, ydir, [0, 0, 1.0])
        for (m, p, M) in bc_leaf(rng.uniform(0.11, 0.15), rng, lobes=5 if LOD == 0 else 3):
            g.add(m, p, base @ M)
    # stem leaves (3-lobed, sessile)
    for i in range(lc(2, 0.5)):
        t = 0.25 + 0.2 * i
        pos, tan = pathpt(pts, t)
        e1, e2 = stem_frame(tan)
        az = i * 3.0 + 1
        radial = math.cos(az) * e1 + math.sin(az) * e2
        ydir = radial * 0.75 + tan * 0.65
        base = orient(pos, ydir, tan * 0.7 - radial * 0.3)
        for (m, p, M) in bc_leaf(0.055, rng, lobes=3):
            g.add(m, p, base @ M)
    return g


# ------------------------------------------------------------------ DANDELION
def fib_sphere(n, zmin=-0.3):
    i = np.arange(n) + 0.5
    z = 1 - (1 - zmin) * i / n
    phi = PI * (1 + 5 ** 0.5) * i
    r = np.sqrt(1 - z * z)
    return np.stack([r * np.cos(phi), r * np.sin(phi), z], 1)


def dand_yellow(g, xf, rng, size=1.0):
    specs = [(30, 0.0185, 0.04, 0.0046, 0.0), (24, 0.0155, 0.4, 0.0042, 0.0012), (18, 0.012, 0.8, 0.0038, 0.0024)]
    for n, L, el, W, z in specs:
        petal_ring(g, 'petal_yellow', lc(n, 0.6), L * size, W * size, rng, r0=0.0015 * size, z0=z * size, elev=(el - 0.06, el + 0.1), elev_j=0.05, xf=xf,
                   a=0.45, b=0.45, nu=3, nv=2, bend=(-0.3, 0.1), notch=0.08, cup=0.2, cols=[(0, '#d09a00'), (0.4, '#f4c410'), (1, '#ffd820')], lj=0.12, roll=0.1)
    g.add('disc_yellow', dome(0.0048 * size, 0.0035 * size, nu=2, nseg=8, cols=lambda u, th: grad(u, [(0, '#b88a00'), (1, '#d8a800')])), xf @ T(0, 0, 0.0028 * size))
    petal_ring(g, 'sepal_green', lc(16, 0.5), 0.0095 * size, 0.0022 * size, rng, r0=0.002, z0=-0.003, elev=(-1.25, -0.85), xf=xf, a=0.4, b=0.7, nu=2, nv=2,
               cols=[(0, '#5a7a30'), (0.7, '#7a9a44'), (1, '#6a7a3a')], bend=0.3)
    petal_ring(g, 'sepal_green', lc(13, 0.5), 0.0085 * size, 0.0022 * size, rng, r0=0.0042, z0=-0.0045, elev=(1.3, 1.45), xf=xf, a=0.4, b=0.7, nu=2, nv=2,
               cols=[(0, '#5a7a30'), (1, '#7a9a44')], bend=-0.15)
    g.add('sepal_green', ellipsoid(0.0055, 0.0055, 0.0055, nu=3, nseg=8, cols=lambda u, th: grad(u, [(0, '#5a7a30'), (1, '#7a9a44')])), xf @ T(0, 0, -0.0055))


def dand_puff(g, xf, rng, n=80, R=0.022, hole=None):
    g.add('sepal_green', dome(0.0048, 0.004, nu=2, nseg=8, cols=lambda u, th: grad(u, [(0, '#6a7a3a'), (1, '#9aa868')])), xf @ T(0, 0, -0.001))
    dirs = fib_sphere(n, zmin=-0.25)
    if hole is not None:
        keep = rng.rand(n) > hole
        dirs = dirs[keep]
    ctr = np.array([0, 0, 0.0035])
    for d in dirs:
        d = unit(d + rng.normal(0, 0.05, 3))
        p0 = ctr + d * 0.003
        p1 = ctr + d * (R * 0.93)
        # shaft
        g.add('seed_white', ribbon(np.array([p0, (p0 + p1) / 2, p1]), [0.0003, 0.0002, 0.0002], cols=grad(np.array([0, 0.5, 1]), [(0, '#9a8a6a'), (0.4, '#d8d0c0'), (1, '#f4f4ee')]), side_ref=np.cross(d, [0.3, 0.5, 0.8])), xf)
        # pappus umbrella
        M = frame_z(p1 + d * 0.0005, d, rng.uniform(0, TAU))
        pr = 0.0098 * rng.uniform(0.9, 1.1)
        g.add('pappus', lobed_disc(pr, lobes=8, rings=1, segs=8 if LOD else 16, depth=0.4, cup=-0.45, sharp=1.2, rot=rng.uniform(0, 1),
                                   cols=lambda u, th: grad(u, [(0, '#a8a498'), (0.5, '#e4e2da'), (1, '#fdfdfb')])), xf @ M)


def dandelion(v, rng):
    g = Geo()
    cols = lambda n: grad(np.linspace(0, 1, n), [(0, '#8a7a4a'), (0.3, '#8aa060'), (1, '#9ab868')])
    h1 = {'a': 0.24, 'b': 0.30, 'c': 0.26, 'd': 0.22}[v] * rng.uniform(0.95, 1.06)
    pts = stem_path(h1, rng, lean=0.12, sway=0.05, n=7)
    g.add('stem_green', tube(pts, np.linspace(0.0024, 0.0016, len(pts)), sides=5, cols=cols(len(pts))))
    xf = head_frame(pts, nod=0.25, rng=rng)
    if v in ('a', 'd'):
        dand_yellow(g, xf, rng, size=1.0)
    elif v == 'b':
        dand_puff(g, xf, rng, n=lc(110, 0.55), R=0.024)
    else:
        dand_puff(g, xf, rng, n=lc(110, 0.55), R=0.023, hole=0.5)
    if v in ('c', 'd'):
        h2 = h1 * rng.uniform(0.55, 0.75)
        az = rng.uniform(0, TAU)
        pts2 = stem_path(h2, rng, lean=0.25, sway=0.04, n=6, dirang=az)
        g.add('stem_green', tube(pts2, np.linspace(0.0022, 0.0014, len(pts2)), sides=5, cols=cols(len(pts2))))
        x2 = head_frame(pts2, nod=0.2, rng=rng)
        if v == 'c':   # closed bud
            g.add('sepal_green', ellipsoid(0.0068, 0.0068, 0.011, nu=4, nseg=8, cols=lambda u, th: grad(u, [(0, '#587a30'), (0.7, '#7a9a44'), (1, '#c8b020')])), x2 @ T(0, 0, 0.007))
            petal_ring(g, 'sepal_green', lc(12, 0.5), 0.011, 0.0032, rng, r0=0.003, z0=0.0, elev=(-0.9, -0.5), xf=x2, a=0.4, b=0.6, nu=2, nv=2, cols=[(0, '#5a7a30'), (1, '#7a9a44')])
        else:
            dand_puff(g, x2, rng, n=lc(70, 0.6), R=0.02)
    # rosette of toothed leaves
    for i in range(lc(7, 0.6)):
        ang = i * 2.4 + rng.uniform(-0.3, 0.3); el = rng.uniform(0.12, 0.5)
        rad = np.array([math.cos(ang), math.sin(ang), 0.0])
        L = rng.uniform(0.11, 0.17)
        p = blade(L, L * 0.2, nu=14, nv=2, a=0.9, b=0.55, serr=0.5, bend=(-0.7, -0.25), fold=0.25, side=rng.uniform(-0.1, 0.1),
                  cols=[(0, '#7a6a3a'), (0.25, '#5a8a30'), (1, '#6aa03a')], mid=0.5, edge=0.1, baseW=0.12)
        g.add('dand_leaf', p, orient(rad * 0.003, rad * math.cos(el) + np.array([0, 0, math.sin(el)]), [0, 0, 1.0]))
    return g


# ------------------------------------------------------------------ CLOVER (red + white)
def trifoliate(g, xf, rng, size=1.0, m='clover_leaf', cols_base=None):
    for k in range(3):
        ang = k * TAU / 3 + rng.uniform(-0.15, 0.15) + PI / 2
        L = 0.03 * size * rng.uniform(0.9, 1.1); W = 0.022 * size
        def cfn(U, V, xn, L=L):
            c = grad(U, [(0, '#3d7228'), (0.5, '#5a9a38'), (1, '#6aac40')])
            chev = np.exp(-((U - (0.36 + 0.3 * np.abs(xn))) / 0.08) ** 2)
            return c * (1 - 0.55 * chev[..., None]) + np.array([0.15, 0.2, 0.12]) * chev[..., None] * 0.6
        p = blade(L, W, nu=4, nv=4, a=0.6, b=0.55, fold=0.3, bend=(-0.15, 0.1), cup=0.15, cfn=cfn, edge=0.05, serr=0.06, baseW=0.05)
        M = mm(xf, T(0, 0, 0.0), Rz(ang - PI / 2), Rx(rng.uniform(-0.2, 0.3)), T(0, 0.002 * size, 0))
        g.add(m, p, M)


def floret_cover(g, m, xf, rng, n, rx, ry, rz, zc, L, W, cols, zmin=-0.2, tilt=0.35, bend=0.25):
    for d in fib_sphere(n, zmin):
        d = unit(d + rng.normal(0, 0.06, 3))
        p = np.array([d[0] * rx, d[1] * ry, d[2] * rz + zc])
        nrm = unit(np.array([d[0] / rx, d[1] / ry, d[2] / rz]))
        yd = unit(nrm + tilt * np.array([0, 0, 1.0]))
        M = orient(p * 0.93 + np.array([0, 0, zc * 0.07]), yd, np.cross(yd, [-d[1], d[0], 0.01])) @ Ry(rng.uniform(0, TAU))
        g.add(m, blade(L * rng.uniform(0.8, 1.2), W, nu=1, nv=2, widthfn=lambda u: 1 - 0.45 * u, bend=bend, cup=0.3, cols=cols, lod=False), xf @ M)


def red_head(g, xf, rng, size=1.0):
    g.add('clover_pink', ellipsoid(0.0098 * size, 0.0098 * size, 0.0135 * size, nu=5, nseg=8,
                                   cols=lambda u, th: grad(u, [(0, '#8a2a62'), (0.5, '#b8408a'), (1, '#c8509a')])), xf @ T(0, 0, 0.0135 * size))
    floret_cover(g, 'clover_pink', xf, rng, lc(85, 0.4), 0.0098 * size, 0.0098 * size, 0.0135 * size, 0.0135 * size, 0.0058 * size, 0.0046 * size,
                 [(0, '#c04090'), (0.5, '#e860aa'), (1, '#f890c8')], zmin=-0.45, tilt=0.45)
    petal_ring(g, 'clover_leaf', 3, 0.012 * size, 0.005 * size, rng, r0=0.003, z0=-0.002, elev=(-0.2, 0.3), xf=xf, a=0.5, b=0.6, nu=2, nv=2, cols=[(0, '#4a7a30'), (1, '#7aa84a')], bend=0.3)


def clover_red(v, rng):
    g = Geo()
    nst = {'a': 3, 'b': 2, 'c': 4, 'd': 3}[v]
    hs = {'a': 0.3, 'b': 0.36, 'c': 0.26, 'd': 0.32}[v]
    cols = lambda n, a='#7a9a4a', b='#8aa858': grad(np.linspace(0, 1, n), [(0, a), (1, b)])
    for i in range(lc(nst, 0.6, 1)):
        h = hs * rng.uniform(0.75, 1.1)
        az = rng.uniform(0, TAU)
        pts = stem_path(h, rng, lean=0.12, sway=0.04, n=6, dirang=az)
        pts[:, :2] += np.array([math.cos(az), math.sin(az)]) * 0.012
        g.add('stem_grey', tube(pts, np.linspace(0.0016, 0.001, len(pts)), sides=4, cols=cols(len(pts), '#6a8a48', '#9ab06a')))
        red_head(g, head_frame(pts, nod=0.2, rng=rng), rng, size=rng.uniform(0.9, 1.1))
        # stem leaf just under head
        pos, tan = pathpt(pts, 0.78)
        trifoliate(g, frame_z(pos, unit(tan + np.array([0.3, 0.0, 0.2])), rng.uniform(0, TAU)) @ Rx(-0.8), rng, size=0.85)
    for i in range(lc(9, 0.6)):
        h = rng.uniform(0.07, hs * 0.75)
        az = rng.uniform(0, TAU)
        pts = stem_path(h, rng, lean=0.35, sway=0.05, n=5, dirang=az)
        pts[:, :2] += np.array([math.cos(az), math.sin(az)]) * 0.008
        g.add('stem_grey', tube(pts, np.linspace(0.0011, 0.0007, len(pts)), sides=3, cols=cols(len(pts), '#6a8a48', '#9ab06a')))
        pos, tan = pathpt(pts, 1.0)
        trifoliate(g, frame_z(pos, unit(tan + np.array([0.0, 0.0, 0.6])), rng.uniform(0, TAU)) @ Rx(-0.5), rng, size=rng.uniform(0.9, 1.25))
    return g


def white_head(g, xf, rng, size=1.0):
    g.add('clover_white', ellipsoid(0.0105 * size, 0.0105 * size, 0.0095 * size, nu=4, nseg=8,
                                    cols=lambda u, th: grad(u, [(0, '#b8a888'), (0.5, '#d8d0bc'), (1, '#e8e2d2')])), xf @ T(0, 0, 0.009 * size))
    floret_cover(g, 'clover_white', xf, rng, lc(64, 0.4), 0.0105 * size, 0.0105 * size, 0.0095 * size, 0.009 * size, 0.0062 * size, 0.0048 * size,
                 [(0, '#d0c4a8'), (0.4, '#f4f0e6'), (1, '#fffdf8')], zmin=-0.75, tilt=0.15, bend=0.0)


def clover_white(v, rng):
    g = Geo()
    nl = {'a': 14, 'b': 18, 'c': 11}[v]
    nh = {'a': 5, 'b': 7, 'c': 3}[v]
    R = {'a': 0.26, 'b': 0.32, 'c': 0.2}[v]
    cols = lambda n: grad(np.linspace(0, 1, n), [(0, '#6a8a48'), (1, '#9ab06a')])
    for i in range(lc(nl, 0.6)):
        az = rng.uniform(0, TAU)
        d = np.array([math.cos(az), math.sin(az), 0.0])
        rr = R * math.sqrt(rng.uniform(0.02, 1.0)) * 0.8
        h = rng.uniform(0.06, 0.13)
        p0 = d * rr * 0.4
        p3 = d * rr + np.array([0, 0, h])
        pts = bez(p0, p0 + np.array([0, 0, h * 0.7]), p3 - np.array([0, 0, h * 0.4]) - d * 0.01, p3, 4 if LOD else 5)
        g.add('stem_grey', tube(pts, np.linspace(0.0011, 0.0007, len(pts)), sides=3, cols=cols(len(pts))))
        trifoliate(g, frame_z(pts[-1], unit(np.array([0.0, 0, 1.0]) + d * 0.3), az) @ Rx(-0.35) @ Rx(0), rng, size=rng.uniform(1.0, 1.4))
    for i in range(lc(nh, 0.6)):
        az = rng.uniform(0, TAU)
        d = np.array([math.cos(az), math.sin(az), 0.0])
        rr = R * math.sqrt(rng.uniform(0.02, 1.0)) * 0.7
        h = rng.uniform(0.11, 0.2)
        p0 = d * rr * 0.3
        p3 = d * rr + np.array([0, 0, h])
        pts = bez(p0, p0 + np.array([0, 0, h * 0.7]), p3 - np.array([0, 0, h * 0.3]), p3, 5)
        g.add('stem_green', tube(pts, np.linspace(0.0012, 0.0008, len(pts)), sides=3, cols=cols(len(pts))))
        white_head(g, frame_z(pts[-1], [0, 0, 1.0], rng.uniform(0, TAU)), rng, size=rng.uniform(0.95, 1.15))
    return g


# ------------------------------------------------------------------ LAVENDER
def lav_spike(g, xf, rng, length=0.06, r=0.0075):
    nu_eff = lr(14)
    rot = rng.uniform(0, 1)

    def prof(u):
        rr = r * (0.45 + 0.75 * np.sin(np.minimum(u * 1.5, 1) * PI / 2)) * (1 - 0.55 * u ** 2.5) * np.clip(1.15 - 0.15 * u, 0, 1)
        rr = rr * np.clip((1 - u) * 6, 0, 1) ** 0.5 + 0.0001
        return rr, length * (0.12 + 0.88 * u) - 0.0 * u

    def ringidx(u):
        return np.round(u * nu_eff)

    def lobe(u, th):
        k = ringidx(u)
        bul = (k % 2)
        return (1 + 0.32 * bul) * (1 + 0.16 * np.cos(4 * (th + k * PI / 4 + rot)))

    def cols(u, th):
        k = ringidx(u)
        c = grad(u, [(0, '#5a40a0'), (0.5, '#8468cc'), (0.88, '#9a84d8'), (1, '#94a488')])
        return c * (0.72 + 0.28 * (k % 2))[..., None] * (0.92 + 0.08 * np.cos(4 * (th + k * PI / 4 + rot)))[..., None]
    g.add('petal_lavender', revolve(prof, nu_eff, 8, lobe=lobe, cols=cols, lod=False), xf @ T(0, 0, -length * 0.12))


def lavender(v, rng):
    g = Geo()
    n = {'a': 18, 'b': 15, 'c': 11, 'd': 19}[v]
    hmax = {'a': 0.42, 'b': 0.5, 'c': 0.4, 'd': 0.38}[v]
    arch = {'a': 0.25, 'b': 0.38, 'c': 0.5, 'd': 0.2}[v]
    # grey-green basal leaf mound
    for i in range(lc(30, 0.5)):
        ang = rng.uniform(0, TAU); el = rng.uniform(0.3, 1.1)
        rad = np.array([math.cos(ang), math.sin(ang), 0.0])
        L = rng.uniform(0.07, 0.12)
        p = blade(L, 0.0042, nu=4, nv=2, a=0.5, b=0.7, bend=(-0.7, -0.15), fold=0.45, cols=[(0, '#7a9678'), (1, '#9cb49a')], mid=0.1, baseW=0.3)
        g.add('leaf_grey', p, orient(rad * rng.uniform(0.004, 0.045), rad * math.cos(el) + np.array([0, 0, math.sin(el)]), [0, 0, 1.0]))
    for i in range(lc(n, 0.55)):
        ang = rng.uniform(0, TAU)
        d = np.array([math.cos(ang), math.sin(ang), 0.0])
        h = hmax * rng.uniform(0.72, 1.1)
        r0 = rng.uniform(0.0, 0.045)
        a2 = arch * rng.uniform(0.6, 1.3)
        p0 = d * r0 + np.array([0, 0, 0.03])
        p3 = d * (r0 + h * a2 * 0.55) + np.array([0, 0, h * (1 - 0.2 * a2)])
        pts = bez(p0, p0 + np.array([0, 0, h * 0.4]) + d * h * 0.05, p3 - np.array([0, 0, h * 0.3]) - d * h * a2 * 0.15, p3, 5 if LOD == 0 else 3)
        pts = np.vstack([np.array([d * r0 * 0.5 + np.array([0, 0, 0.0])]), pts])
        t = np.linspace(0, 1, len(pts))
        g.add('stem_grey', tube(pts, np.linspace(0.0014, 0.0009, len(pts)), sides=4, cols=grad(t, [(0, '#6a8a58'), (1, '#8aa678')]), cap=False))
        tan = unit(pts[-1] - pts[-2])
        lav_spike(g, frame_z(pts[-1] - tan * 0.002, tan, rng.uniform(0, TAU)), rng, length=rng.uniform(0.06, 0.08), r=rng.uniform(0.0052, 0.0064))
        # tiny leaf pair on stem
        if LOD == 0 and rng.rand() < 0.6:
            tt = rng.uniform(0.15, 0.4)
            for s in (0, PI):
                leaf_on_path(g, 'leaf_grey', pts, tt, s + rng.uniform(0, 1), 0.7, blade(0.03, 0.0025, nu=3, nv=2, a=0.5, b=0.7, bend=-0.2, fold=0.3, cols=[(0, '#7a9678'), (1, '#9cb49a')], baseW=0.3))
    return g


DEFS = [
    dict(sp='daisy', fn=daisy, variants=['a', 'b', 'c', 'd'], ko='불란서국화(옥스아이데이지)', weight=1.0, habitat='meadow', sway=0.6, lod=True),
    dict(sp='poppy', fn=poppy, variants=['a', 'b', 'c', 'd'], ko='개양귀비', weight=0.8, habitat='meadow', sway=0.7, lod=True),
    dict(sp='cornflower', fn=cornflower, variants=['a', 'b', 'c', 'd'], ko='수레국화', weight=0.8, habitat='meadow', sway=0.7, lod=True),
    dict(sp='buttercup', fn=buttercup, variants=['a', 'b', 'c', 'd'], ko='미나리아재비', weight=0.9, habitat='meadow', sway=0.6, lod=True),
    dict(sp='dandelion', fn=dandelion, variants=['a', 'b', 'c', 'd'], ko='서양민들레', weight=0.9, habitat='path', sway=0.5, lod=True),
    dict(sp='clover_red', fn=clover_red, variants=['a', 'b', 'c', 'd'], ko='붉은토끼풀(붉은클로버)', weight=0.8, habitat='meadow', sway=0.4, lod=True),
    dict(sp='clover_white', fn=clover_white, variants=['a', 'b', 'c'], ko='토끼풀(흰클로버)', weight=1.0, habitat='meadow', sway=0.1, lod=True),
    dict(sp='lavender', fn=lavender, variants=['a', 'b', 'c', 'd'], ko='라벤더', weight=0.4, habitat='garden', sway=0.4, lod=True),
]
